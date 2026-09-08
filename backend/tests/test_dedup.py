from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Asset, Assertion, AuditEvent, Evidence, Household, Job, ReviewTask
from app.services import job_service
from app.services.candidates import Candidate
from app.services.observations import Observation
from app.services.asset_service import create_asset


@pytest.fixture
def dedup_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'dedup.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Dedup Household")
    other = Household(name="Other Household")
    session.add_all([household, other])
    session.commit()
    monkeypatch.setattr("app.config.settings.storage_root", str(tmp_path / "storage"))

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, other.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def evidence(session: Session, household_id: str, suffix: str) -> Evidence:
    row = Evidence(
        household_id=household_id,
        sha256=(suffix * 64)[:64],
        storage_key=f"dedup/{suffix}.png",
        media_type="image/png",
        original_filename=f"{suffix}.png",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(row)
    session.commit()
    return row


def observation(session: Session, evidence_id: str, kind: str, value: dict[str, object]) -> Observation:
    row = Observation(evidence_id=evidence_id, kind=kind, value_json=json.dumps(value), confidence=1.0)
    session.add(row)
    session.commit()
    return row


def run_import(session: Session, household_id: str, evidence_ids: list[str]) -> Job:
    job = job_service.create_job(session, household_id, evidence_ids)
    return job_service.run_job(session, job)


def candidate_for(session: Session, job_id: str) -> Candidate:
    return session.query(Candidate).filter_by(job_id=job_id).one()


def test_exact_duplicate_proposes_existing_asset_without_new_asset(dedup_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = dedup_db
    source = evidence(session, household_id, "a")
    observation(session, source.id, "phash", {"hash": "0000000000000000"})
    existing = create_asset(session, household_id, {"display_name": "Existing camera", "evidence_ids": [source.id]})

    job = run_import(session, household_id, [source.id])
    candidate = candidate_for(session, job.id)
    proposal = json.loads(candidate.proposed_fields_json)

    assert proposal["kind"] == "duplicate_of_asset"
    assert proposal["asset_id"] == existing.id
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_near_duplicate_is_advisory_and_far_duplicate_has_no_similar_match(dedup_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = dedup_db
    source = evidence(session, household_id, "b")
    near = evidence(session, household_id, "c")
    far = evidence(session, household_id, "d")
    observation(session, source.id, "phash", {"hash": "0000000000000000"})
    observation(session, near.id, "phash", {"hash": "0000000000000001"})
    observation(session, far.id, "phash", {"hash": "ffffffffffffffff"})
    existing = create_asset(session, household_id, {"display_name": "Existing photo", "evidence_ids": [source.id]})

    near_job = run_import(session, household_id, [near.id])
    near_proposal = json.loads(candidate_for(session, near_job.id).proposed_fields_json)
    assert near_proposal["kind"] == "similar"
    assert near_proposal["dedup_matches"][0]["asset_id"] == existing.id
    assert near_proposal["dedup_matches"][0]["distance"] <= 10
    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate_for(session, near_job.id).id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200
    assert accepted.json()["job"]["state"] == "COMPLETED"
    assert session.query(Asset).filter_by(household_id=household_id).count() == 2

    far_job = run_import(session, household_id, [far.id])
    far_proposal = json.loads(candidate_for(session, far_job.id).proposed_fields_json)
    assert far_proposal["kind"] == "new_asset"
    assert not [match for match in far_proposal["dedup_matches"] if match["type"] == "similar"]


def test_identifier_collision_creates_task_and_blocks_commit_until_resolved(dedup_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_household_id = dedup_db
    existing_evidence = evidence(session, household_id, "e")
    incoming = evidence(session, household_id, "f")
    existing = create_asset(session, household_id, {"display_name": "Serialised item", "evidence_ids": [existing_evidence.id]})
    session.add(
        Assertion(
            asset_id=existing.id,
            field_path="identifier",
            value_json=json.dumps("ABC-123"),
            source_type="user",
            review_state="accepted",
        )
    )
    session.commit()
    observation(session, incoming.id, "barcode_qr", {"symbology": "QR", "value": "ABC-123", "validated": True})

    job = run_import(session, household_id, [incoming.id])
    task = session.query(ReviewTask).filter_by(household_id=household_id).one()
    candidate = candidate_for(session, job.id)
    assert task.task_type == "identifier_collision"
    assert task.subject_ref == candidate.id

    with TestClient(app) as client:
        blocked = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        listed = client.get("/v1/review-tasks", params={"household_id": household_id})
        alias = client.get("/v1/review_tasks", params={"household_id": household_id})
        resolved = client.post(
            f"/v1/review-tasks/{task.id}/resolve",
            params={"household_id": household_id},
            json={"resolution": "reviewed"},
        )
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        cross_resolve = client.post(
            f"/v1/review-tasks/{task.id}/resolve",
            params={"household_id": other_household_id},
            json={"resolution": "cross-household"},
        )
        cross = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": other_household_id},
            json={"action": "accept"},
        )

    assert blocked.status_code == 409
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == task.id
    assert listed.json()["next_cursor"] is None
    assert alias.json()["items"][0]["id"] == task.id
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"
    assert session.query(AuditEvent).filter_by(action="review_task.resolve", entity_id=task.id).count() == 1
    assert accepted.status_code == 200
    assert accepted.json()["job"]["state"] == "COMPLETED"
    assert cross_resolve.status_code == 403
    assert cross.status_code == 403


def test_no_merge_path_is_present_in_dedup_module() -> None:
    source = Path(__file__).parents[1] / "app" / "services" / "dedup.py"
    text = source.read_text()
    assert "UPDATE" not in text.upper()
    assert "merge" not in text.lower()
