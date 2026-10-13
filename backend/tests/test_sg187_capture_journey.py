"""SG-187 G1: a CREATED job starts through the real /run route.

The Inbox Start control (frontend) posts the same `/v1/imports/{id}/run` the
modal uses when auto-detect is checked; these tests prove the route-side
journey on disposable state: CREATED -> run -> AWAITING_REVIEW, with the
foreign-household 403 control and the no-fake-success control (a second /run
on a FAILED job leaves it FAILED; retry recovers honestly).
"""
from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Evidence, Household, Job


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "sg187-journey.db"
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
    household = Household(name="SG-187 Journey Household")
    other_household = Household(name="SG-187 Foreign Household")
    session.add_all([household, other_household])
    session.commit()
    output = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(output, format="PNG")
    image_bytes = output.getvalue()
    evidence = Evidence(
        household_id=household.id,
        sha256="c" * 64,
        storage_key="sg187/evidence.png",
        media_type="image/png",
        original_filename="evidence.png",
        source_kind="upload",
        size_bytes=len(image_bytes),
    )
    session.add(evidence)
    session.commit()
    evidence_path = storage_root / evidence.storage_key
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_bytes(image_bytes)
    try:
        yield session, household.id, other_household.id, evidence.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def test_created_job_start_reaches_awaiting_review_with_foreign_403(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_household_id, evidence_id = isolated_db
    with TestClient(app) as client:
        created = client.post(
            "/v1/imports",
            params={"household_id": household_id},
            json={"evidence_ids": [evidence_id]},
        )
        job_id = created.json()["id"]
        foreign_run = client.post(
            f"/v1/imports/{job_id}/run", params={"household_id": other_household_id}
        )
        before = client.get(f"/v1/imports/{job_id}", params={"household_id": household_id})
        started = client.post(f"/v1/imports/{job_id}/run", params={"household_id": household_id})
        after = client.get(f"/v1/imports/{job_id}", params={"household_id": household_id})

    assert created.status_code == 201
    assert created.json()["state"] == "CREATED"
    assert foreign_run.status_code == 403
    assert before.json()["state"] == "CREATED"
    assert started.status_code == 200
    assert started.json()["state"] == "AWAITING_REVIEW"
    assert after.json()["state"] == "AWAITING_REVIEW"
    assert session.query(Job).filter_by(id=job_id).one().state == "AWAITING_REVIEW"


def test_run_on_failed_job_stays_failed_and_retry_recovers(isolated_db, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _, evidence_id = isolated_db
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
        first = client.post(f"/v1/imports/{job_id}/run", params={"household_id": household_id})
        second = client.post(f"/v1/imports/{job_id}/run", params={"household_id": household_id})
        retried = client.post(f"/v1/imports/{job_id}/retry", params={"household_id": household_id})

    assert first.status_code == 200
    assert first.json()["state"] == "FAILED"
    assert second.status_code == 200
    assert second.json()["state"] == "FAILED"
    assert retried.status_code == 200
    assert retried.json()["state"] == "AWAITING_REVIEW"
    assert session.query(Job).filter_by(id=job_id).one().state == "AWAITING_REVIEW"
