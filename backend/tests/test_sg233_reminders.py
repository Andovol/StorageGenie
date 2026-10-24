"""SG-233: expiry reminder store, real-engine writer, routes and read-back.

Every database is a scratch SQLite file built by the committed migration; the
production SQLite and the storage folder are never opened. Fixture dates are
computed from the live clock at execution and passed explicitly (`PG-IC-07`).
The production modules are imported inside the tests so the same file collects
against the start-base tree, where they do not exist.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect as sa_inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import Assertion, Asset, Household
from app.plugins.expiry_tracker import EXPIRY_FIELD

PREVIOUS_REVISION = "20260924_sg114_relation"
ROOT = Path(__file__).resolve().parents[2]

REMINDER_COLUMNS = {
    "id",
    "household_id",
    "asset_id",
    "as_of_day",
    "tier",
    "bucket",
    "days_remaining",
    "status",
    "created_at",
    "updated_at",
}

SHIPPED_PATHS = (
    "backend/alembic/versions/20261023_sg233_reminder.py",
    "backend/app/models/reminder.py",
    "backend/app/services/reminders/service.py",
    "backend/app/api/v1/reminders.py",
    "frontend/src/routes/ExpiryPage.tsx",
)


def _missing_shipped_paths(paths: tuple[str, ...]) -> list[str]:
    return [
        path
        for path in paths
        if not (ROOT / path).is_file() or (ROOT / path).stat().st_size == 0
    ]


def _alembic_config(url: str) -> Config:
    config = Config(str(ROOT / "backend" / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "backend" / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


@pytest.fixture
def reminder_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    url = f"sqlite:///{tmp_path / 'sg233.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    command.upgrade(_alembic_config(url), "head")
    engine = create_engine(url, connect_args={"check_same_thread": False})
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG233 Household")
    other = Household(name="SG233 Other Household")
    session.add_all([household, other])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
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


def _asset(session: Session, household_id: str, name: str = "SG233 Milk") -> Asset:
    asset = Asset(
        household_id=household_id, display_name=name, asset_type="product", status="ACTIVE"
    )
    session.add(asset)
    session.commit()
    return asset


def _classify(client: TestClient, asset_id: str, household_id: str) -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": "food_beverages"},
    )
    assert response.status_code == 200, response.text


def _enter_expiry(client: TestClient, asset_id: str, household_id: str, day: date) -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
        params={"household_id": household_id},
        json={"expiry_date": day.isoformat(), "date_type": "expiry_date"},
    )
    assert response.status_code == 200, response.text


def _add_assertion(
    session: Session, asset: Asset, field_path: str, value: object, review_state: str
) -> None:
    session.add(
        Assertion(
            asset_id=asset.id,
            field_path=field_path,
            value_json=json.dumps(value),
            source_type="user",
            review_state=review_state,
        )
    )
    session.commit()


def _due_asset(
    client: TestClient, session: Session, household_id: str
) -> tuple[Asset, date, date]:
    today = datetime.now(timezone.utc).date()
    expiry = today + timedelta(days=3)
    asset = _asset(session, household_id)
    _classify(client, asset.id, household_id)
    _enter_expiry(client, asset.id, household_id, expiry)
    return asset, today, expiry


def test_sg233_migration_upgrade_downgrade_upgrade_and_unique(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'sg233_migration.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)
    command.upgrade(config, "head")

    inspector = sa_inspect(create_engine(url))
    assert "reminder" in set(inspector.get_table_names())
    columns = {column["name"]: column for column in inspector.get_columns("reminder")}
    assert set(columns) == REMINDER_COLUMNS
    assert columns["tier"]["nullable"] is True
    assert columns["household_id"]["nullable"] is False
    assert columns["asset_id"]["nullable"] is False
    assert columns["status"]["nullable"] is False
    indexes = {index["name"] for index in inspector.get_indexes("reminder")}
    assert {
        "ix_reminder_household_id",
        "ix_reminder_asset_id",
        "ix_reminder_status",
    } <= indexes
    uniques = {
        unique["name"]: set(unique["column_names"])
        for unique in inspector.get_unique_constraints("reminder")
    }
    assert uniques.get("uq_reminder_asset_as_of_day") == {"asset_id", "as_of_day"}
    foreign_keys = {
        (fk["constrained_columns"][0], fk["referred_table"]) for fk in inspector.get_foreign_keys("reminder")
    }
    assert foreign_keys == {("household_id", "household"), ("asset_id", "asset")}

    from app.models.reminder import Reminder

    assert {column.name for column in Reminder.__table__.columns} == REMINDER_COLUMNS
    assert Reminder.__table__.c.tier.nullable is True
    assert Reminder.__table__.c.days_remaining.nullable is False

    engine = create_engine(url)
    session = Session(engine)
    household = Household(name="SG233 Migration Household")
    session.add(household)
    session.commit()
    asset = Asset(
        household_id=household.id,
        display_name="SG233 Migration Item",
        asset_type="product",
        status="ACTIVE",
    )
    session.add(asset)
    session.commit()
    day_key = (datetime.now(timezone.utc).date() + timedelta(days=3)).isoformat()
    session.add(
        Reminder(
            household_id=household.id,
            asset_id=asset.id,
            as_of_day=day_key,
            tier="urgent",
            bucket="this-week",
            days_remaining=3,
            status="unread",
        )
    )
    session.commit()
    session.add(
        Reminder(
            household_id=household.id,
            asset_id=asset.id,
            as_of_day=day_key,
            tier="urgent",
            bucket="this-week",
            days_remaining=3,
            status="unread",
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
    session.close()
    engine.dispose()

    command.downgrade(config, PREVIOUS_REVISION)
    assert "reminder" not in set(sa_inspect(create_engine(url)).get_table_names())
    command.upgrade(config, "head")
    assert "reminder" in set(sa_inspect(create_engine(url)).get_table_names())


def test_sg233_due_fixture_creates_engine_shaped_unread_reminder(
    reminder_env,  # type: ignore[no-untyped-def]
) -> None:
    session, household_id, _other = reminder_env
    client = TestClient(app)
    asset, today, _expiry = _due_asset(client, session, household_id)

    before = client.get("/v1/reminders", params={"household_id": household_id})
    assert before.status_code == 200, before.text
    assert before.json()["items"] == []

    from app.services.reminders.service import record_due

    created = record_due(session, household_id, today)
    assert len(created) == 1, "a due fixture must create exactly one reminder"
    row = created[0]
    assert row.asset_id == asset.id
    assert row.as_of_day == today.isoformat()
    assert row.tier == "urgent"
    assert row.bucket == "this-week"
    assert row.days_remaining == 3
    assert row.status == "unread"

    engine_status = client.get(
        "/v1/plugins/expiry-tracker/status",
        params={"household_id": household_id, "as_of": today.isoformat()},
    ).json()
    engine_row = engine_status["rows"][0]
    assert (engine_row["tier"], engine_row["bucket"], engine_row["days_remaining"]) == (
        row.tier,
        row.bucket,
        row.days_remaining,
    )

    listed = client.get("/v1/reminders", params={"household_id": household_id})
    assert listed.status_code == 200
    body = listed.json()
    assert body["unread_count"] == 1
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["asset_id"] == asset.id
    assert item["display_name"] == "SG233 Milk"
    assert item["as_of_day"] == today.isoformat()
    assert item["tier"] == "urgent"
    assert item["window_days"] == 7
    assert item["bucket"] == "this-week"
    assert item["days_remaining"] == 3
    assert item["status"] == "unread"

    later = today + timedelta(days=4)
    _enter_expiry(client, asset.id, household_id, today + timedelta(days=20))
    changed = record_due(session, household_id, later)
    assert len(changed) == 1
    assert (changed[0].tier, changed[0].bucket, changed[0].days_remaining) == (
        "upcoming",
        "this-month",
        16,
    )


def test_sg233_record_due_defaults_to_the_live_utc_day(
    reminder_env,  # type: ignore[no-untyped-def]
) -> None:
    session, household_id, _other = reminder_env
    client = TestClient(app)
    _due_asset(client, session, household_id)
    before = datetime.now(timezone.utc).date()

    from app.services.reminders.service import record_due

    created = record_due(session, household_id)
    after = datetime.now(timezone.utc).date()
    assert len(created) == 1
    assert created[0].as_of_day in {before.isoformat(), after.isoformat()}


def test_sg233_unresolved_and_non_warning_rows_create_nothing(
    reminder_env,  # type: ignore[no-untyped-def]
) -> None:
    session, household_id, _other = reminder_env
    client = TestClient(app)
    today = datetime.now(timezone.utc).date()

    unresolved = _asset(session, household_id, "SG233 Proposed")
    _classify(client, unresolved.id, household_id)
    _add_assertion(
        session,
        unresolved,
        EXPIRY_FIELD,
        {"expiry_date": (today + timedelta(days=3)).isoformat(), "date_type": "expiry_date"},
        "proposed",
    )

    expired = _asset(session, household_id, "SG233 Expired")
    _classify(client, expired.id, household_id)
    _add_assertion(
        session,
        expired,
        EXPIRY_FIELD,
        {"expiry_date": (today - timedelta(days=1)).isoformat(), "date_type": "expiry_date"},
        "accepted",
    )

    safe = _asset(session, household_id, "SG233 Safe")
    _classify(client, safe.id, household_id)
    _add_assertion(
        session,
        safe,
        EXPIRY_FIELD,
        {"expiry_date": (today + timedelta(days=60)).isoformat(), "date_type": "expiry_date"},
        "accepted",
    )

    from app.models.reminder import Reminder
    from app.services.reminders.service import record_due

    assert record_due(session, household_id, today) == []
    assert session.query(Reminder).count() == 0
    listed = client.get("/v1/reminders", params={"household_id": household_id})
    assert listed.status_code == 200
    assert listed.json()["items"] == []
    assert listed.json()["unread_count"] == 0


def test_sg233_same_day_rerun_inserts_zero_rows(
    reminder_env,  # type: ignore[no-untyped-def]
) -> None:
    session, household_id, _other = reminder_env
    client = TestClient(app)
    _due_asset(client, session, household_id)
    today = datetime.now(timezone.utc).date()

    from app.models.reminder import Reminder
    from app.services.reminders.service import record_due

    first = record_due(session, household_id, today)
    second = record_due(session, household_id, today)
    assert len(first) == 1
    assert second == []
    assert session.query(Reminder).count() == 1


def test_sg233_read_and_dismiss_round_trip_with_illegal_transitions(
    reminder_env,  # type: ignore[no-untyped-def]
) -> None:
    session, household_id, other_household = reminder_env
    client = TestClient(app)
    _due_asset(client, session, household_id)
    today = datetime.now(timezone.utc).date()

    from app.services.reminders.service import record_due

    record_due(session, household_id, today)
    baseline = client.get("/v1/reminders", params={"household_id": household_id}).json()
    assert baseline["unread_count"] == 1
    reminder_id = baseline["items"][0]["id"]

    assert (
        client.post(
            f"/v1/reminders/{reminder_id}/read", params={"household_id": other_household}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/v1/reminders/missing/read", params={"household_id": household_id}
        ).status_code
        == 404
    )

    read = client.post(
        f"/v1/reminders/{reminder_id}/read", params={"household_id": household_id}
    )
    assert read.status_code == 200, read.text
    assert read.json()["status"] == "read"
    after_read = client.get("/v1/reminders", params={"household_id": household_id}).json()
    assert after_read["unread_count"] == baseline["unread_count"] - 1
    assert after_read["items"][0]["status"] == "read"
    assert (
        client.post(
            f"/v1/reminders/{reminder_id}/read", params={"household_id": household_id}
        ).status_code
        == 422
    )

    assert (
        client.post(
            f"/v1/reminders/{reminder_id}/dismiss", params={"household_id": other_household}
        ).status_code
        == 403
    )
    dismissed = client.post(
        f"/v1/reminders/{reminder_id}/dismiss", params={"household_id": household_id}
    )
    assert dismissed.status_code == 200, dismissed.text
    assert dismissed.json()["status"] == "dismissed"
    after_dismiss = client.get("/v1/reminders", params={"household_id": household_id}).json()
    assert after_dismiss["unread_count"] == baseline["unread_count"] - 1
    assert after_dismiss["items"][0]["status"] == "dismissed"
    assert (
        client.post(
            f"/v1/reminders/{reminder_id}/read", params={"household_id": household_id}
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/v1/reminders/{reminder_id}/dismiss", params={"household_id": household_id}
        ).status_code
        == 422
    )


def test_sg233_shipped_paths_still_exist() -> None:
    missing = _missing_shipped_paths(SHIPPED_PATHS)
    assert missing == [], f"SG-233 shipped paths missing or empty: {missing}"
