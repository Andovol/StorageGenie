from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Household
from app.models.review_task import ReviewTask
from app.services import job_service
from app.services.candidates import Candidate
from app.services.observations import Observation
from app.models.evidence import Evidence


@pytest.fixture
def candidate_read_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'candidate-read.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Read Household")
    other = Household(name="Other Read Household")
    session.add_all([household, other])
    session.commit()
    evidence = Evidence(
        household_id=household.id,
        sha256="r" * 64,
        storage_key="candidate-read/source.png",
        media_type="image/png",
        original_filename="source.png",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(evidence)
    session.commit()
    job = job_service.create_job(session, household.id, [evidence.id])
    session.add(Observation(evidence_id=evidence.id, kind="phash", value_json=json.dumps({"hash": "0" * 16}), confidence=1.0))
    session.commit()
    job_service.run_job(session, job)
    candidate = session.query(Candidate).filter_by(job_id=job.id).one()
    proposal = json.loads(candidate.proposed_fields_json)
    task = ReviewTask(
        task_type="identifier_collision",
        priority="high",
        subject_ref=candidate.id,
        proposed_change=json.dumps({"candidate_id": candidate.id}),
        status="open",
        household_id=household.id,
    )
    session.add(task)
    session.flush()
    proposal["review_task_ids"] = [task.id]
    candidate.proposed_fields_json = json.dumps(proposal)
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, other.id, candidate.id, evidence.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def test_candidate_read_returns_review_payload_and_checks_household(candidate_read_db) -> None:  # type: ignore[no-untyped-def]
    _, household_id, other_household_id, candidate_id, evidence_id = candidate_read_db
    with TestClient(app) as client:
        response = client.get(f"/v1/candidates/{candidate_id}", params={"household_id": household_id})
        cross_household = client.get(
            f"/v1/candidates/{candidate_id}", params={"household_id": other_household_id}
        )
        missing = client.get("/v1/candidates/missing-candidate", params={"household_id": household_id})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == candidate_id
    assert body["job_id"]
    assert body["state"] == "proposed"
    assert body["fields"]["display_name"] == "source"
    assert body["dedup_matches"] == []
    assert body["review_task_ids"]
    assert body["evidence_ids"] == [evidence_id]
    assert cross_household.status_code == 403
    assert missing.status_code == 404
