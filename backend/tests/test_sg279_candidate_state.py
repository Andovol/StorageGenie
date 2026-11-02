"""SG-279: candidate state constraint widening on a migrated schema.

Every database is a scratch SQLite file built by the committed Alembic chain to
head; the production SQLite and the storage folder are never opened. No key, no
network, zero spend.

Seams under test: `POST /v1/candidates/{id}/split` and
`POST /v1/candidates/merge` on a schema built by Alembic (not `create_all`),
with the app's own connection behaviour (foreign keys on), read back in fresh
sessions on that same file. Plus: all seven states stored and an invalid one
refused (each in its own transaction), and model-vs-migrated parity.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import Evidence, Household
from app.services import job_service
from app.services.candidates import Candidate


SEVEN_STATES = ["proposed", "accepted", "edited", "held", "rejected", "split", "merged"]


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _enable_app_connection_behaviour(engine):  # type: ignore[no-untyped-def]
    """Mirror `app/db.py:22-27`: FKs on, WAL, busy timeout."""

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


@pytest.fixture
def sg279_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    db_path = tmp_path / "sg279.db"
    url = f"sqlite:///{db_path}"
    monkeypatch.setattr(settings, "database_url", url)
    monkeypatch.setattr("app.config.settings.storage_root", str(tmp_path / "storage"))
    config = _alembic_config(url)
    command.upgrade(config, "head")
    head = ScriptDirectory(str(Path(__file__).resolve().parents[1] / "alembic")).get_current_head()
    print(f"\nSG279_DB_PATH={db_path} ALEMBIC_HEAD={head} URL={url}")
    engine = create_engine(url, connect_args={"check_same_thread": False})
    _enable_app_connection_behaviour(engine)
    # Prove FK enforcement is on for this engine (app behaviour).
    with engine.connect() as conn:
        fk_on = conn.execute(text("PRAGMA foreign_keys")).scalar()
        print(f"SG279_FK_PRAGMA={fk_on}")
        assert fk_on == 1
        rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
        print(f"SG279_ALEMBIC_VERSION={rev}")
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG279 Household")
    other = Household(name="SG279 Other Household")
    session.add_all([household, other])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, other.id, db_path, factory, head
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _evidence(session: Session, household_id: str, suffix: str) -> Evidence:
    row = Evidence(
        household_id=household_id,
        sha256=(suffix * 64)[:64],
        storage_key=f"sg279/{suffix}.jpg",
        media_type="image/jpeg",
        original_filename=f"{suffix}.jpg",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(row)
    session.commit()
    return row


def _provenance(value: object, confidence: float | None = 0.9) -> dict[str, object]:
    return {
        "value": value,
        "confidence": confidence,
        "source_type": "extraction",
        "provider": "scripted",
        "model": "scripted-model-1",
        "prompt_template_version": "extract-food-v1",
        "provider_call_id": "call-1",
    }


def _two_item_proposal() -> dict[str, object]:
    return {
        "kind": "new_asset",
        "asset_id": None,
        "fields": {
            "display_name": _provenance("Milk"),
            "asset_type": _provenance("food"),
            "status": {"value": "ACTIVE", "source_type": "deterministic", "confidence": None,
                       "provider": None, "model": None,
                       "prompt_template_version": None, "provider_call_id": None},
        },
        "dedup_matches": [],
        "review_task_ids": [],
        "ai_items": [
            {"name": "Milk", "expiry_date": "2030-01-15", "confidence": 0.9},
            {"name": "Yogurt", "expiry_date": None, "confidence": 0.8},
        ],
        "ai_unknowns": [],
        "needs_evidence": False,
        "ai_provider": "scripted",
        "ai_model": "scripted-model-1",
        "prompt_template_version": "extract-food-v1",
        "provider_call_ids": ["call-1"],
    }


def _seed_split_candidate(session: Session, household_id: str, evidence_id: str) -> Candidate:
    job = job_service.create_job(session, household_id, [evidence_id])
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json=json.dumps([evidence_id]),
        proposed_fields_json=json.dumps(_two_item_proposal(), ensure_ascii=False),
        state="proposed",
        household_id=household_id,
    )
    session.add(candidate)
    session.commit()
    return candidate


def _seed_merge_pair(session: Session, household_id: str, suffix_a: str, suffix_b: str) -> tuple[Candidate, Candidate]:
    job_w = job_service.create_job(session, household_id, [])
    winner = Candidate(
        job_id=job_w.id,
        evidence_ids_json=json.dumps([]),
        proposed_fields_json=json.dumps({"kind": "new_asset", "fields": {}}, ensure_ascii=False),
        state="proposed",
        household_id=household_id,
    )
    session.add(winner)
    session.flush()
    job_l = job_service.create_job(session, household_id, [])
    loser = Candidate(
        job_id=job_l.id,
        evidence_ids_json=json.dumps([]),
        proposed_fields_json=json.dumps({"kind": "new_asset", "fields": {}}, ensure_ascii=False),
        state="proposed",
        household_id=household_id,
    )
    session.add(loser)
    session.commit()
    # silence unused suffixes (evidence not needed for merge union of empties)
    _ = (suffix_a, suffix_b)
    return winner, loser


def _fresh(factory) -> Session:  # type: ignore[no-untyped-def]
    return factory()


def test_sg279_split_through_route_commits_on_migrated_schema(sg279_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _, db_path, factory, head = sg279_db
    incoming = _evidence(session, household_id, "s")
    candidate = _seed_split_candidate(session, household_id, incoming.id)
    candidate_id = candidate.id
    session.close()

    with TestClient(app) as client:
        response = client.post(
            f"/v1/candidates/{candidate_id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["state"] == "split"
        assert len(body["children"]) == 2
        child_ids = [child["id"] for child in body["children"]]

    fresh = _fresh(factory)
    try:
        origin = fresh.query(Candidate).filter_by(id=candidate_id).one()
        assert origin.state == "split"
        children = [fresh.query(Candidate).filter_by(id=cid).one() for cid in child_ids]
        assert [c.state for c in children] == ["proposed", "proposed"]
    finally:
        fresh.close()
    print(f"SG279_SPLIT_OK db={db_path} head={head} origin=split children=2")


def test_sg279_merge_through_route_commits_on_migrated_schema(sg279_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _, db_path, factory, head = sg279_db
    winner, loser = _seed_merge_pair(session, household_id, "m1", "m2")
    winner_id, loser_id = winner.id, loser.id
    session.close()

    with TestClient(app) as client:
        response = client.post(
            "/v1/candidates/merge",
            params={"household_id": household_id},
            json={"winner_id": winner_id, "loser_ids": [loser_id]},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["winner_id"] == winner_id
        assert body["state"] == "proposed"

    fresh = _fresh(factory)
    try:
        stored_winner = fresh.query(Candidate).filter_by(id=winner_id).one()
        stored_loser = fresh.query(Candidate).filter_by(id=loser_id).one()
        assert stored_winner.state == "proposed"
        assert stored_loser.state == "merged"
        assert json.loads(stored_loser.proposed_fields_json)["merged_into"] == winner_id
    finally:
        fresh.close()
    print(f"SG279_MERGE_OK db={db_path} head={head} loser=merged survivor=proposed")


def test_sg279_all_states_stored_and_invalid_refused(sg279_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _, db_path, factory, head = sg279_db
    job = job_service.create_job(session, household_id, [])
    job_id = job.id
    session.close()

    fresh = _fresh(factory)
    try:
        for state in SEVEN_STATES:
            row = Candidate(
                job_id=job_id,
                evidence_ids_json=json.dumps([]),
                proposed_fields_json=json.dumps({"kind": "new_asset", "fields": {}}),
                state=state,
                household_id=household_id,
            )
            fresh.add(row)
            fresh.commit()
            assert fresh.query(Candidate).filter_by(id=row.id).one().state == state
        # invalid state refused in its own transaction
        bad = Candidate(
            job_id=job_id,
            evidence_ids_json=json.dumps([]),
            proposed_fields_json=json.dumps({"kind": "new_asset", "fields": {}}),
            state="bogus",
            household_id=household_id,
        )
        fresh.add(bad)
        with pytest.raises(IntegrityError, match="ck_candidate_state"):
            fresh.commit()
        fresh.rollback()
    finally:
        fresh.close()
    print(f"SG279_STATES_OK db={db_path} head={head} states={','.join(SEVEN_STATES)}")


def test_sg279_model_and_migrated_schema_agree(sg279_db) -> None:  # type: ignore[no-untyped-def]
    _, _, _, db_path, _, head = sg279_db
    # model side
    checks = [c for c in Candidate.__table__.constraints if getattr(c, "name", None) == "ck_candidate_state"]
    assert len(checks) == 1, "model must declare exactly one ck_candidate_state"
    model_sql = str(checks[0].sqltext)
    model_states = set(re.findall(r"'([a-z_]+)'", model_sql))
    # migrated side
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            schema_sql = conn.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='candidate'")
            ).scalar()
    finally:
        engine.dispose()
    assert schema_sql is not None
    migrated_states = set(re.findall(r"'([a-z_]+)'", schema_sql))
    print(f"SG279_PARITY db={db_path} head={head} model={sorted(model_states)} migrated={sorted(migrated_states)}")
    assert model_states == set(SEVEN_STATES)
    assert migrated_states == set(SEVEN_STATES)
    assert model_states == migrated_states
