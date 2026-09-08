from __future__ import annotations

import json
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, AuditEvent, Evidence, Household, Job, JobStep


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "imports.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr("app.config.settings.storage_root", str(storage_root))

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    household = Household(name="Import Household")
    other_household = Household(name="Other Household")
    session.add_all([household, other_household])
    session.commit()
    evidence = Evidence(
        household_id=household.id,
        sha256="a" * 64,
        storage_key="import/evidence.png",
        media_type="image/png",
        original_filename="evidence.png",
        source_kind="upload",
        size_bytes=80,
    )
    other_evidence = Evidence(
        household_id=other_household.id,
        sha256="b" * 64,
        storage_key="other/evidence.bin",
        media_type="application/octet-stream",
        original_filename="other.bin",
        source_kind="upload",
        size_bytes=1,
    )
    session.add_all([evidence, other_evidence])
    session.commit()
    output = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(output, format="PNG")
    evidence_path = storage_root / evidence.storage_key
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_bytes(output.getvalue())
    try:
        yield session, household.id, other_household.id, evidence.id, other_evidence.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def test_import_create_run_and_jobs_list(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _, evidence_id, _ = isolated_db
    with TestClient(app) as client:
        created = client.post(
            "/v1/imports",
            params={"household_id": household_id},
            json={"evidence_ids": [evidence_id]},
        )
        assert created.status_code == 201
        job_id = created.json()["id"]
        assert session.query(JobStep).filter_by(job_id=job_id).count() == 6

        ran = client.post(f"/v1/imports/{job_id}/run", params={"household_id": household_id})
        detail = client.get(f"/v1/imports/{job_id}", params={"household_id": household_id})
        listed = client.get("/v1/jobs", params={"household_id": household_id})

    assert ran.status_code == 200
    assert detail.status_code == 200
    body = detail.json()
    assert body["state"] == "AWAITING_REVIEW"
    assert body["progress"] == {"completed": 4, "total": 6, "failed": 0, "pending": 1}
    assert [step["state"] for step in body["steps"]] == [
        "COMPLETED",
        "COMPLETED",
        "COMPLETED",
        "COMPLETED",
        "AWAITING_REVIEW",
        "PENDING",
    ]
    assert all(step["attempts"] == 1 for step in body["steps"][:5])
    assert body["steps"][2]["output"]["status"] == "ok"
    assert body["steps"][2]["output"]["counts"]["phash"] == 1
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == job_id
    assert listed.json()["items"][0]["state"] == "AWAITING_REVIEW"

    persisted = session.query(Job).filter_by(id=job_id).one()
    persisted_steps = session.query(JobStep).filter_by(job_id=job_id).order_by(JobStep.id).all()
    assert persisted.state == "AWAITING_REVIEW"
    assert len(persisted_steps) == 6
    persisted_output = json.loads(persisted_steps[2].output_refs or "{}")
    assert persisted_output["status"] == "ok"
    assert persisted_output["step"] == "EXTRACTING_DETERMINISTIC_SIGNALS"
    assert persisted_output["observation_ids"]
    assert persisted_output["completed_at"]


def test_failure_retry_is_durable_and_idempotent(isolated_db, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _, evidence_id, _ = isolated_db
    from app.services import job_service

    original_execute = job_service.execute_step
    failed_once = False

    def fail_normalizing(db, job, step):  # type: ignore[no-untyped-def]
        nonlocal failed_once
        if step.step_name == "NORMALIZING" and not failed_once:
            failed_once = True
            raise RuntimeError("forced step failure")
        return original_execute(db, job, step)

    monkeypatch.setattr(job_service, "execute_step", fail_normalizing)
    with TestClient(app) as client:
        created = client.post(
            "/v1/imports",
            params={"household_id": household_id},
            json={"evidence_ids": [evidence_id]},
        )
        job_id = created.json()["id"]
        first_run = client.post(f"/v1/imports/{job_id}/run", params={"household_id": household_id})
        failed_detail = client.get(
            f"/v1/imports/{job_id}", params={"household_id": household_id}
        )
        retry = client.post(f"/v1/imports/{job_id}/retry", params={"household_id": household_id})
        retry_again = client.post(
            f"/v1/imports/{job_id}/retry", params={"household_id": household_id}
        )
        run_again = client.post(
            f"/v1/imports/{job_id}/run", params={"household_id": household_id}
        )

    assert created.status_code == 201
    assert first_run.status_code == 200
    assert failed_detail.json()["state"] == "FAILED"
    failed_step = next(step for step in failed_detail.json()["steps"] if step["state"] == "FAILED")
    assert failed_step["error"] == "forced step failure"
    assert retry.status_code == 200
    assert retry.json()["state"] == "AWAITING_REVIEW"
    assert retry_again.status_code == 200
    assert retry_again.json()["id"] == job_id
    assert run_again.status_code == 200
    assert run_again.json()["state"] == "AWAITING_REVIEW"
    assert session.query(JobStep).filter_by(job_id=job_id).count() == 6
    assert session.query(Asset).filter_by(household_id=household_id).count() == 0
    assert session.query(Assertion).count() == 0
    assert session.query(AuditEvent).filter_by(entity_type="job", entity_id=job_id).count() >= 3


def test_import_idempotency_and_cross_household_protection(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_household_id, evidence_id, other_evidence_id = isolated_db
    with TestClient(app) as client:
        first = client.post(
            "/v1/imports",
            params={"household_id": household_id},
            headers={"Idempotency-Key": "import-same-key"},
            json={"evidence_ids": [evidence_id]},
        )
        replay = client.post(
            "/v1/imports",
            params={"household_id": household_id},
            headers={"Idempotency-Key": "import-same-key"},
            json={"evidence_ids": [evidence_id]},
        )
        job_id = first.json()["id"]
        cross_get = client.get(
            f"/v1/imports/{job_id}", params={"household_id": other_household_id}
        )
        cross_run = client.post(
            f"/v1/imports/{job_id}/run", params={"household_id": other_household_id}
        )
        cross_retry = client.post(
            f"/v1/imports/{job_id}/retry", params={"household_id": other_household_id}
        )
        cross_create = client.post(
            "/v1/imports",
            params={"household_id": household_id},
            json={"evidence_ids": [other_evidence_id]},
        )

    assert first.status_code == 201
    assert replay.status_code == 201
    assert replay.json()["id"] == first.json()["id"]
    assert session.query(Job).filter_by(idempotency_key="import-same-key").count() == 1
    assert [response.status_code for response in (cross_get, cross_run, cross_retry, cross_create)] == [
        403,
        403,
        403,
        403,
    ]
