from __future__ import annotations

import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Asset, Assertion, AuditEvent, Evidence, Household, Job
from app.models.evidence import asset_evidence
from app.services import candidates, job_service
from app.services.candidates import Candidate
from app.services.observations import Observation


@pytest.fixture
def candidate_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'candidate.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Candidate Household")
    other = Household(name="Other Candidate Household")
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
        yield session, household.id, other.id, tmp_path
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def evidence(session: Session, household_id: str, suffix: str) -> Evidence:
    row = Evidence(
        household_id=household_id,
        sha256=(suffix * 64)[:64],
        storage_key=f"candidate/{suffix}.png",
        media_type="image/png",
        original_filename=f"{suffix}.png",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(row)
    session.commit()
    return row


def create_pending_candidate(session: Session, household_id: str, evidence_id: str) -> tuple[Job, Candidate]:
    job = job_service.create_job(session, household_id, [evidence_id])
    session.add(
        Observation(
            evidence_id=evidence_id,
            kind="phash",
            value_json=json.dumps({"hash": "0000000000000000"}),
            confidence=1.0,
        )
    )
    session.commit()
    job = job_service.run_job(session, job)
    return job, session.query(Candidate).filter_by(job_id=job.id).one()


def test_accept_commit_is_four_way_atomic_and_visible_in_detail(candidate_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_household_id, _ = candidate_db
    incoming = evidence(session, household_id, "h")
    job, candidate = create_pending_candidate(session, household_id, incoming.id)

    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "edit", "corrected_fields": {"display_name": "Committed camera", "identifier": "NEW-1"}},
        )
        event = client.post(
            f"/v1/assets/{accepted.json()['asset_id']}/events",
            params={"household_id": household_id},
            json={"type": "inspected", "note": "serial checked"},
        )
        detail = client.get(
            f"/v1/assets/{accepted.json()['asset_id']}", params={"household_id": household_id}
        )
        cross_event = client.post(
            f"/v1/assets/{accepted.json()['asset_id']}/events",
            params={"household_id": other_household_id},
            json={"type": "stolen"},
        )

    assert accepted.status_code == 200
    asset_id = accepted.json()["asset_id"]
    assert accepted.json()["job"]["state"] == "COMPLETED"
    assert session.query(Asset).filter_by(id=asset_id, household_id=household_id).count() == 1
    assert session.query(Assertion).filter_by(asset_id=asset_id).count() >= 2
    assert session.execute(asset_evidence.select().where(asset_evidence.c.asset_id == asset_id)).fetchall()
    actions = [row.action for row in session.query(AuditEvent).filter_by(entity_id=asset_id).all()]
    assert "asset.lifecycle.created" in actions
    assert event.status_code == 201
    assert detail.status_code == 200
    assert any(row["action"] == "asset.lifecycle.inspected" for row in detail.json()["audit_events"])
    assert cross_event.status_code == 403


def test_forced_mid_commit_failure_rolls_back_and_retry_completes(candidate_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _, _ = candidate_db
    incoming = evidence(session, household_id, "i")
    job, candidate = create_pending_candidate(session, household_id, incoming.id)
    original = candidates._create_asset_for_candidate

    def fail_after_asset(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        original(*args, **kwargs)
        raise RuntimeError("forced mid-commit failure")

    monkeypatch.setattr(candidates, "_create_asset_for_candidate", fail_after_asset)
    with TestClient(app) as client:
        failed = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )

    assert failed.status_code == 200
    assert failed.json()["job"]["state"] == "FAILED"
    assert session.query(Asset).filter_by(household_id=household_id).count() == 0
    assert session.query(Assertion).count() == 0
    assert session.execute(asset_evidence.select()).fetchall() == []
    assert session.query(AuditEvent).filter(AuditEvent.entity_type == "asset").count() == 0

    monkeypatch.setattr(candidates, "_create_asset_for_candidate", original)
    with TestClient(app) as client:
        retried = client.post(f"/v1/imports/{job.id}/retry", params={"household_id": household_id})

    assert retried.status_code == 200
    assert retried.json()["state"] == "COMPLETED"
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_candidate_migration_upgrade_downgrade_upgrade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "migration.db"
    url = f"sqlite:///{database_path}"
    monkeypatch.setattr(settings, "database_url", url)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    assert "candidate" in inspect(create_engine(url)).get_table_names()
    command.downgrade(config, "20260908_sg013_observation")
    assert "candidate" not in inspect(create_engine(url)).get_table_names()
    command.upgrade(config, "head")
    assert "candidate" in inspect(create_engine(url)).get_table_names()
