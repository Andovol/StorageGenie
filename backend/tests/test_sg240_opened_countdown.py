"""SG-240 G2/G3: the opened-date write path and the countdown read path."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, AuditEvent, Household
from app.plugins.expiry_tracker import OPENED_DATE_FIELD
from app.services.opened_countdown import add_months

COSMETICS = "cosmetics_personal_care"


@pytest.fixture
def sg240_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg240.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-240 Household")
    session.add(household)
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def make_asset(session: Session, household_id: str, name: str = "Cream") -> Asset:
    asset = Asset(household_id=household_id, display_name=name, asset_type="product", status="ACTIVE")
    session.add(asset)
    session.commit()
    return asset


def classify(client: TestClient, asset_id: str, household_id: str, category: str) -> object:
    return client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": category},
    )


def record_opened(
    client: TestClient, asset_id: str, household_id: str, opened_date: object
) -> object:
    return client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/opened",
        params={"household_id": household_id},
        json={"opened_date": opened_date},
    )


def read_countdown(client: TestClient, household_id: str, as_of: str) -> object:
    return client.get(
        "/v1/plugins/expiry-tracker/opened",
        params={"household_id": household_id, "as_of": as_of},
    )


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


# --- G2: the write path -----------------------------------------------------


def test_write_stores_an_accepted_bare_json_string(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    opened = (utc_today() - timedelta(days=10)).isoformat()
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        response = record_opened(client, asset.id, household_id, opened)

    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == asset.id
    assert body["assertion"]["field_path"] == OPENED_DATE_FIELD
    assert body["assertion"]["value"] == opened
    assert body["assertion"]["review_state"] == "accepted"
    assert body["assertion"]["source_type"] == "user"

    stored = (
        session.query(Assertion)
        .filter_by(asset_id=asset.id, field_path=OPENED_DATE_FIELD)
        .one()
    )
    assert stored.value_json == json.dumps(opened)
    assert json.loads(stored.value_json) == opened


def test_second_write_supersedes_the_first(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    today = utc_today()
    first = (today - timedelta(days=30)).isoformat()
    second = (today - timedelta(days=5)).isoformat()
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        assert record_opened(client, asset.id, household_id, first).status_code == 200
        response = record_opened(client, asset.id, household_id, second)

    assert response.status_code == 200
    session.expire_all()
    rows = (
        session.query(Assertion)
        .filter_by(asset_id=asset.id, field_path=OPENED_DATE_FIELD)
        .all()
    )
    assert len(rows) == 2
    by_value = {json.loads(row.value_json): row for row in rows}
    assert by_value[first].review_state == "superseded"
    assert by_value[second].review_state == "accepted"
    active = [row for row in rows if row.review_state not in ("superseded", "rejected")]
    assert len(active) == 1
    assert json.loads(active[0].value_json) == second


def test_non_tracking_category_is_refused(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id, "Milk")
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, "food_beverages").status_code == 200
        response = record_opened(
            client, asset.id, household_id, (utc_today() - timedelta(days=1)).isoformat()
        )

    assert response.status_code == 422
    assert "Opened-date tracking is not enabled" in response.json()["detail"]
    assert "food_beverages" in response.json()["detail"]
    assert (
        session.query(Assertion)
        .filter_by(asset_id=asset.id, field_path=OPENED_DATE_FIELD)
        .count()
        == 0
    )


def test_unclassified_asset_is_refused(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    with TestClient(app) as client:
        response = record_opened(
            client, asset.id, household_id, (utc_today() - timedelta(days=1)).isoformat()
        )
    assert response.status_code == 422
    assert "accepted classification" in response.json()["detail"]


def test_future_date_is_refused(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    future = (utc_today() + timedelta(days=2)).isoformat()
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        response = record_opened(client, asset.id, household_id, future)

    assert response.status_code == 422
    assert "must not be after today (UTC)" in response.json()["detail"]


def test_malformed_date_is_refused(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        unpadded = record_opened(client, asset.id, household_id, "2026-5-1")
        not_a_date = record_opened(client, asset.id, household_id, "not-a-date")
        missing = record_opened(client, asset.id, household_id, None)

    assert unpadded.status_code == 422
    assert not_a_date.status_code == 422
    assert missing.status_code == 422
    assert "opened_date" in missing.json()["detail"]


def test_unknown_asset_is_404_and_household_mismatch_is_403(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    opened = (utc_today() - timedelta(days=1)).isoformat()
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        unknown = record_opened(client, "does-not-exist", household_id, opened)
        mismatch = record_opened(client, asset.id, "another-household", opened)

    assert unknown.status_code == 404
    assert mismatch.status_code == 403


def test_the_write_leaves_an_audit_row(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    opened = (utc_today() - timedelta(days=3)).isoformat()
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        response = record_opened(client, asset.id, household_id, opened)

    assertion_id = response.json()["assertion"]["id"]
    audit = (
        session.query(AuditEvent)
        .filter_by(action="plugin.assertion.write", entity_id=assertion_id)
        .one()
    )
    assert audit.actor == "expiry-tracker"
    assert audit.household_id == household_id
    assert json.loads(audit.after_json)["value"] == opened
    assert json.loads(audit.after_json)["review_state"] == "accepted"


# --- G3: the read path ------------------------------------------------------


def test_known_opened_date_carries_the_real_counts(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id, "Serum")
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        assert record_opened(client, asset.id, household_id, "2026-01-31").status_code == 200
        response = read_countdown(client, household_id, "2026-02-15")

    assert response.status_code == 200
    body = response.json()
    assert body["household_id"] == household_id
    assert body["as_of"] == "2026-02-15"
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["asset_id"] == asset.id
    assert row["display_name"] == "Serum"
    assert row["category"] == COSMETICS
    assert row["opened_date"] == "2026-01-31"
    assert row["days_open"] == 15
    assert row["window_months"] == 12
    assert row["window_source"] == "category_default"
    assert row["window_end"] == "2027-01-31"
    assert row["days_remaining"] == 350


def test_no_opened_date_carries_nulls_not_zeros(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        response = read_countdown(client, household_id, "2026-02-15")

    row = response.json()["rows"][0]
    assert row["asset_id"] == asset.id
    assert row["opened_date"] is None
    assert row["days_open"] is None
    assert row["days_remaining"] is None
    assert row["window_end"] is None
    assert row["window_months"] == 12


def test_non_tracking_and_unclassified_assets_are_absent(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    food = make_asset(session, household_id, "Milk")
    unclassified = make_asset(session, household_id, "Mystery")
    with TestClient(app) as client:
        assert classify(client, food.id, household_id, "food_beverages").status_code == 200
        response = read_countdown(client, household_id, "2026-02-15")

    assert response.status_code == 200
    assert response.json()["rows"] == []
    assert unclassified.id  # the unclassified asset exists but is not a row


def test_month_end_opened_date_clamps(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        assert record_opened(client, asset.id, household_id, "2024-02-29").status_code == 200
        response = read_countdown(client, household_id, "2024-03-01")

    row = response.json()["rows"][0]
    assert row["window_end"] == "2025-02-28"
    assert row["days_remaining"] == (date(2025, 2, 28) - date(2024, 3, 1)).days


def test_add_months_clamps_the_day() -> None:
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)
    assert add_months(date(2024, 2, 29), 12) == date(2025, 2, 28)
    assert add_months(date(2026, 1, 31), 12) == date(2027, 1, 31)


def test_archived_assets_are_not_rows(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg240_db
    asset = make_asset(session, household_id)
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, COSMETICS).status_code == 200
        asset.status = "ARCHIVED"
        session.commit()
        response = read_countdown(client, household_id, "2026-02-15")
    assert response.status_code == 200
    assert response.json()["rows"] == []


def test_empty_household_returns_the_same_shape_with_an_empty_list(sg240_db) -> None:  # type: ignore[no-untyped-def]
    session, _household_id = sg240_db
    empty = Household(name="Empty household")
    session.add(empty)
    session.commit()
    with TestClient(app) as client:
        response = read_countdown(client, empty.id, "2026-02-15")

    assert response.status_code == 200
    assert response.json() == {
        "household_id": empty.id,
        "as_of": "2026-02-15",
        "rows": [],
    }


def test_unknown_household_is_404_and_bad_as_of_is_422(sg240_db) -> None:  # type: ignore[no-untyped-def]
    _session, household_id = sg240_db
    with TestClient(app) as client:
        unknown = read_countdown(client, "does-not-exist", "2026-02-15")
        malformed = read_countdown(client, household_id, "2026-2-15")
        not_a_date = read_countdown(client, household_id, "nope")

    assert unknown.status_code == 404
    assert malformed.status_code == 422
    assert not_a_date.status_code == 422
