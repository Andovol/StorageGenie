from __future__ import annotations

import datetime
import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base
from app.models import (
    Asset,
    Assertion,
    GuardrailEvent,
    Household,
    PlanningSuggestion,
    SourceAttribution,
)

FOUNDATION_TABLES = ("source_attribution", "planning_suggestion", "guardrail_event")


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


@pytest.fixture
def foundation_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'foundations.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Foundations Household")
    session.add(household)
    session.commit()
    asset = Asset(household_id=household.id, display_name="Foundation Drill")
    session.add(asset)
    session.commit()
    assertion = Assertion(asset_id=asset.id, field_path="expiry", value_json='"2030-01-01"')
    session.add(assertion)
    session.commit()
    try:
        yield session, household, asset, assertion
    finally:
        session.close()
        engine.dispose()


def test_foundations_migration_upgrade_downgrade_upgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)

    command.upgrade(config, "head")
    inspector = inspect(create_engine(url))
    assert set(FOUNDATION_TABLES).issubset(set(inspector.get_table_names()))
    assert {ix["name"] for ix in inspector.get_indexes("source_attribution")} >= {
        "ix_source_attribution_household_id",
        "ix_source_attribution_asset_id",
        "ix_source_attribution_assertion_id",
    }
    assert {ix["name"] for ix in inspector.get_indexes("planning_suggestion")} >= {
        "ix_planning_suggestion_household_id",
        "ix_planning_suggestion_status",
    }
    assert {ix["name"] for ix in inspector.get_indexes("guardrail_event")} >= {
        "ix_guardrail_event_household_id",
    }

    command.downgrade(config, "20260912_sg025_provider_call")
    remaining = set(inspect(create_engine(url)).get_table_names())
    assert remaining.isdisjoint(FOUNDATION_TABLES)

    command.upgrade(config, "head")
    assert set(FOUNDATION_TABLES).issubset(set(inspect(create_engine(url)).get_table_names()))


def test_source_attribution_round_trips(foundation_db) -> None:  # type: ignore[no-untyped-def]
    session, household, asset, assertion = foundation_db
    retrieved_at = datetime.datetime(2026, 9, 14, 12, 0, tzinfo=datetime.timezone.utc)
    row = SourceAttribution(
        household_id=household.id,
        asset_id=asset.id,
        assertion_id=assertion.id,
        field_path="expiry",
        uri="https://example.invalid/expiry",
        retrieved_at=retrieved_at,
        note="sentinel attribution",
    )
    session.add(row)
    session.commit()
    session.expunge_all()

    loaded = session.get(SourceAttribution, row.id)
    assert loaded is not None
    assert loaded.household_id == household.id
    assert loaded.asset_id == asset.id
    assert loaded.assertion_id == assertion.id
    assert loaded.field_path == "expiry"
    assert loaded.uri == "https://example.invalid/expiry"
    assert loaded.note == "sentinel attribution"


def test_source_attribution_assertion_fk_is_nullable(foundation_db) -> None:  # type: ignore[no-untyped-def]
    session, household, asset, _ = foundation_db
    row = SourceAttribution(
        household_id=household.id,
        asset_id=asset.id,
        assertion_id=None,
        field_path="display_name",
        uri="https://example.invalid/name",
        retrieved_at=datetime.datetime(2026, 9, 14, 12, 0, tzinfo=datetime.timezone.utc),
        note=None,
    )
    session.add(row)
    session.commit()
    session.expunge_all()

    loaded = session.get(SourceAttribution, row.id)
    assert loaded is not None
    assert loaded.assertion_id is None
    assert loaded.note is None


def test_planning_suggestion_round_trips(foundation_db) -> None:  # type: ignore[no-untyped-def]
    session, household, asset, assertion = foundation_db
    suggestion = PlanningSuggestion(
        household_id=household.id,
        kind="use_first",
        title="Use the open milk first",
        body_json=json.dumps({"asset_id": asset.id}),
        backing_refs_json=json.dumps([assertion.id]),
    )
    session.add(suggestion)
    session.commit()
    session.expunge_all()

    loaded = session.get(PlanningSuggestion, suggestion.id)
    assert loaded is not None
    assert loaded.status == "pending"
    assert loaded.kind == "use_first"
    assert loaded.title == "Use the open milk first"
    assert json.loads(loaded.body_json) == {"asset_id": asset.id}
    assert json.loads(loaded.backing_refs_json) == [assertion.id]


def test_sqlite_busy_timeout_pragma(tmp_path: Path) -> None:
    from app.db import _set_sqlite_pragma
    import sqlite3

    db_path = tmp_path / "test_pragma.db"
    conn = sqlite3.connect(str(db_path))
    _set_sqlite_pragma(conn, None)

    cursor = conn.cursor()
    cursor.execute("PRAGMA busy_timeout;")
    timeout = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    assert timeout == 5000


def test_guardrail_event_round_trips(foundation_db) -> None:  # type: ignore[no-untyped-def]
    session, household, _, assertion = foundation_db
    event = GuardrailEvent(
        household_id=household.id,
        kind="correction",
        ref_ids_json=json.dumps([assertion.id]),
        detail_json=json.dumps({"from": "open", "to": "opened"}),
    )
    session.add(event)
    session.commit()
    session.expunge_all()

    loaded = session.get(GuardrailEvent, event.id)
    assert loaded is not None
    assert loaded.kind == "correction"
    assert json.loads(loaded.ref_ids_json) == [assertion.id]
    assert json.loads(loaded.detail_json) == {"from": "open", "to": "opened"}
