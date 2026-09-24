"""SG-107: the pure expiry urgency engine + its plugin read route.

Boundary table through the REAL `CATEGORIES` data, the stricter accepted-only
resolved rule (a proposed date can never tier), household isolation, `as_of`
determinism, a no-write proof on both the compute and the route legs, and the
route shape/reconciliation/empty-set contract. Fixture dates are sample data
computed relative to the live clock (no fixed dates, `PG-IC-07`).
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, Household
from app.plugins import expiry_tracker
from app.plugins.expiry_tracker import CLASSIFICATION_FIELD, EXPIRY_FIELD
from app.services import expiry_engine

ROW_KEYS = {
    "asset_id",
    "display_name",
    "category",
    "expiry_date",
    "date_type",
    "days_remaining",
    "tier",
    "bucket",
}


def _today() -> date:
    return datetime.now(timezone.utc).date()


@pytest.fixture
def engine_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg107.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household_a = Household(name="SG107 Household A")
    household_b = Household(name="SG107 Household B")
    session.add_all([household_a, household_b])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household_a.id, household_b.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def make_asset(
    session: Session, household_id: str, name: str = "Item", asset_type: str = "product"
) -> Asset:
    asset = Asset(
        household_id=household_id, display_name=name, asset_type=asset_type, status="ACTIVE"
    )
    session.add(asset)
    session.commit()
    return asset


def add_classification(session: Session, asset: Asset, category_slug: str) -> Assertion:
    assertion = Assertion(
        asset_id=asset.id,
        field_path=CLASSIFICATION_FIELD,
        value_json=json.dumps({"category": category_slug, "label": category_slug}),
        source_type="user",
        review_state="accepted",
    )
    session.add(assertion)
    session.commit()
    return assertion


def add_expiry(
    session: Session, asset: Asset, value: object, review_state: str = "accepted"
) -> Assertion:
    assertion = Assertion(
        asset_id=asset.id,
        field_path=EXPIRY_FIELD,
        value_json=json.dumps(value),
        source_type="user",
        review_state=review_state,
    )
    session.add(assertion)
    session.commit()
    return assertion


def table_counts(session: Session) -> dict[str, int]:
    return {
        name: int(session.execute(select(func.count()).select_from(table)).scalar_one())
        for name, table in Base.metadata.tables.items()
    }


def _classify(client: TestClient, asset_id: str, household_id: str, category: str):  # type: ignore[no-untyped-def]
    return client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": category},
    )


def _enter(client: TestClient, asset_id: str, household_id: str, expiry_date: str):  # type: ignore[no-untyped-def]
    return client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
        params={"household_id": household_id},
        json={"expiry_date": expiry_date, "date_type": "expiry_date"},
    )


def _status(client: TestClient, household_id: str, **params: str):  # type: ignore[no-untyped-def]
    return client.get(
        "/v1/plugins/expiry-tracker/status",
        params={"household_id": household_id, **params},
    )


# --- G2: generic tier rule through the REAL category data ---------------------

FOOD = {"critical": 1, "urgent": 7, "upcoming": 30}
MEDICINE = {"critical": 1, "urgent": 3, "upcoming": 14}
COSMETICS = {"critical": 7, "urgent": 30, "upcoming": 90}
HOUSEHOLD = {"upcoming": 30}
DOCUMENTS = {"upcoming": 30, "long_lead": 60}

BOUNDARY_TABLE: list[tuple[str, dict[int, str | None]]] = [
    (
        "food_beverages",
        {
            -1: None,
            0: "critical",
            1: "critical",
            3: "urgent",
            7: "urgent",
            14: "upcoming",
            30: "upcoming",
            60: "safe",
            90: "safe",
            91: "safe",
        },
    ),
    (
        "medicine_pharma",
        {
            -1: None,
            0: "critical",
            1: "critical",
            3: "urgent",
            7: "upcoming",
            14: "upcoming",
            30: "safe",
            60: "safe",
            90: "safe",
            91: "safe",
        },
    ),
    (
        "cosmetics_personal_care",
        {
            -1: None,
            0: "critical",
            1: "critical",
            3: "critical",
            7: "critical",
            14: "urgent",
            30: "urgent",
            60: "upcoming",
            90: "upcoming",
            91: "safe",
        },
    ),
    (
        "household_chemicals",
        {
            -1: None,
            0: "upcoming",
            1: "upcoming",
            3: "upcoming",
            7: "upcoming",
            14: "upcoming",
            30: "upcoming",
            60: "safe",
            90: "safe",
            91: "safe",
        },
    ),
    (
        "documents_other",
        {
            -1: None,
            0: "upcoming",
            1: "upcoming",
            3: "upcoming",
            7: "upcoming",
            14: "upcoming",
            30: "upcoming",
            60: "long_lead",
            90: "safe",
            91: "safe",
        },
    ),
]


def test_category_windows_are_the_declared_uncalibrated_data() -> None:
    assert expiry_tracker.CATEGORIES["food_beverages"].tier_defaults == FOOD
    assert expiry_tracker.CATEGORIES["medicine_pharma"].tier_defaults == MEDICINE
    assert expiry_tracker.CATEGORIES["cosmetics_personal_care"].tier_defaults == COSMETICS
    assert expiry_tracker.CATEGORIES["household_chemicals"].tier_defaults == HOUSEHOLD
    assert expiry_tracker.CATEGORIES["documents_other"].tier_defaults == DOCUMENTS
    assert expiry_tracker.CATEGORIES["non_perishable"].tier_defaults == {}


def test_boundary_table_reproduces_every_category_window() -> None:
    for slug, expected in BOUNDARY_TABLE:
        for d, tier in expected.items():
            assert expiry_engine.tier_for(slug, d) == tier, (slug, d)
        max_window = max(expiry_tracker.CATEGORIES[slug].tier_defaults.values())
        assert expiry_engine.tier_for(slug, max_window + 1) == "safe", slug


def test_non_perishable_tier_is_null_and_bucket_still_computed() -> None:
    for d in (-1, 0, 7, 8, 30, 31, 400):
        assert expiry_engine.tier_for("non_perishable", d) is None
    assert expiry_engine.bucket_for(31) == "safe"


def test_bucket_boundaries() -> None:
    assert [expiry_engine.bucket_for(d) for d in (-1, 0, 7, 8, 30, 31)] == [
        "expired",
        "this-week",
        "this-week",
        "this-month",
        "this-month",
        "safe",
    ]


def test_days_remaining_is_calendar_difference() -> None:
    base = _today()
    assert expiry_engine.days_remaining(base, base) == 0
    assert expiry_engine.days_remaining(base + timedelta(days=9), base) == 9
    assert expiry_engine.days_remaining(base - timedelta(days=1), base) == -1


# --- G2: resolved rule + discrimination ---------------------------------------


def test_discrimination_proposed_near_date_never_tiers(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    as_of = _today()
    accepted = make_asset(session, household_a, "Accepted")
    add_classification(session, accepted, "food_beverages")
    add_expiry(session, accepted, {"expiry_date": as_of.isoformat(), "date_type": "expiry_date"})
    proposed = make_asset(session, household_a, "Proposed")
    add_classification(session, proposed, "food_beverages")
    add_expiry(
        session,
        proposed,
        {"expiry_date": as_of.isoformat(), "date_type": "expiry_date"},
        review_state="proposed",
    )
    superseded = make_asset(session, household_a, "Superseded")
    add_classification(session, superseded, "food_beverages")
    add_expiry(
        session,
        superseded,
        {"expiry_date": as_of.isoformat(), "date_type": "expiry_date"},
        review_state="superseded",
    )

    result = expiry_engine.compute_status(session, household_a, as_of)
    row_ids = {row["asset_id"] for row in result["rows"]}
    assert row_ids == {accepted.id}
    reasons = {row["asset_id"]: row["reason"] for row in result["unresolved_rows"]}
    assert reasons[proposed.id] == "proposed"
    assert reasons[superseded.id] == "dateless"
    assert result["summary"]["unresolved"] == 2
    assert result["summary"]["total"] == 3


def test_unresolved_reasons_cover_all_four(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    as_of = _today()
    needs_evidence = make_asset(session, household_a, "Needs evidence")
    add_classification(session, needs_evidence, "food_beverages")
    add_expiry(
        session, needs_evidence, {"status": "unknown"}, review_state="needs_evidence"
    )
    unparseable = make_asset(session, household_a, "Unparseable")
    add_classification(session, unparseable, "food_beverages")
    add_expiry(session, unparseable, {"status": "unknown"})
    dateless = make_asset(session, household_a, "Dateless")
    add_classification(session, dateless, "documents_other")

    result = expiry_engine.compute_status(session, household_a, as_of)
    assert result["rows"] == []
    reasons = {row["asset_id"]: row["reason"] for row in result["unresolved_rows"]}
    assert reasons == {
        needs_evidence.id: "needs_evidence",
        unparseable.id: "unparseable",
        dateless.id: "dateless",
    }


def test_household_isolation(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, household_b = engine_db
    as_of = _today()
    mine = make_asset(session, household_a, "Mine")
    add_classification(session, mine, "food_beverages")
    add_expiry(session, mine, {"expiry_date": (as_of + timedelta(days=3)).isoformat()})
    theirs = make_asset(session, household_b, "Theirs")
    add_classification(session, theirs, "food_beverages")
    add_expiry(session, theirs, {"expiry_date": (as_of + timedelta(days=3)).isoformat()})

    result = expiry_engine.compute_status(session, household_a, as_of)
    assert {row["asset_id"] for row in result["rows"]} == {mine.id}
    assert theirs.id not in {row["asset_id"] for row in result["rows"]}


def test_as_of_shifts_days_exactly(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    base = _today()
    asset = make_asset(session, household_a, "Shifting")
    add_classification(session, asset, "food_beverages")
    add_expiry(session, asset, {"expiry_date": (base + timedelta(days=10)).isoformat()})

    first = expiry_engine.compute_status(session, household_a, base)["rows"][0]
    second = expiry_engine.compute_status(
        session, household_a, base + timedelta(days=4)
    )["rows"][0]
    assert first["days_remaining"] == 10
    assert second["days_remaining"] == 6
    assert first["bucket"] == "this-month" and first["tier"] == "upcoming"
    assert second["bucket"] == "this-week" and second["tier"] == "urgent"


def test_urgency_sort_is_expired_first_then_days_ascending(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    as_of = _today()
    for name, delta in (("far", 40), ("expired", -2), ("near", 1), ("soon", 5)):
        asset = make_asset(session, household_a, name)
        add_classification(session, asset, "food_beverages")
        add_expiry(session, asset, {"expiry_date": (as_of + timedelta(days=delta)).isoformat()})

    rows = expiry_engine.compute_status(session, household_a, as_of)["rows"]
    assert [row["display_name"] for row in rows] == ["expired", "near", "soon", "far"]
    assert rows[0]["tier"] is None and rows[0]["bucket"] == "expired"


# --- G2: no-write proof -------------------------------------------------------


def test_compute_status_writes_nothing(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    as_of = _today()
    asset = make_asset(session, household_a, "Read only")
    add_classification(session, asset, "food_beverages")
    add_expiry(session, asset, {"expiry_date": (as_of + timedelta(days=2)).isoformat()})

    before = table_counts(session)
    expiry_engine.compute_status(session, household_a, as_of)
    after = table_counts(session)
    assert before == after


# --- G2: the route through the REAL TestClient --------------------------------


def test_route_shape_summary_reconciles_and_writes_nothing(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    as_of = _today()
    with TestClient(app) as client:
        milk = make_asset(session, household_a, "Milk")
        assert _classify(client, milk.id, household_a, "Food & beverages").status_code == 200
        assert _enter(client, milk.id, household_a, (as_of + timedelta(days=2)).isoformat()).status_code == 200

        bread = make_asset(session, household_a, "Bread")
        assert _classify(client, bread.id, household_a, "food").status_code == 200
        assert _enter(client, bread.id, household_a, (as_of + timedelta(days=20)).isoformat()).status_code == 200

        old = make_asset(session, household_a, "Old yogurt")
        assert _classify(client, old.id, household_a, "food").status_code == 200
        assert _enter(client, old.id, household_a, (as_of - timedelta(days=1)).isoformat()).status_code == 200

        cream = make_asset(session, household_a, "Cream")
        assert _classify(client, cream.id, household_a, "cosmetics").status_code == 200

        passport = make_asset(session, household_a, "Passport")
        assert _classify(client, passport.id, household_a, "documents").status_code == 200

        proposed = make_asset(session, household_a, "Proposed date")
        add_classification(session, proposed, "food_beverages")
        add_expiry(
            session,
            proposed,
            {"expiry_date": (as_of + timedelta(days=1)).isoformat()},
            review_state="proposed",
        )
        unparseable = make_asset(session, household_a, "Unparseable")
        add_classification(session, unparseable, "food_beverages")
        add_expiry(session, unparseable, {"status": "unknown"})

        before = table_counts(session)
        response = _status(client, household_a, as_of=as_of.isoformat())
        after = table_counts(session)

    assert response.status_code == 200
    body = response.json()
    assert body["as_of"] == as_of.isoformat()
    assert set(body) == {"as_of", "household_id", "category", "rows", "summary", "unresolved_rows"}

    rows = body["rows"]
    assert [set(row) for row in rows] == [ROW_KEYS] * len(rows)
    by_id = {row["asset_id"]: row for row in rows}
    assert by_id[milk.id]["days_remaining"] == 2
    assert by_id[milk.id]["tier"] == "urgent" and by_id[milk.id]["bucket"] == "this-week"
    assert by_id[milk.id]["category"] == "food_beverages"
    assert by_id[milk.id]["date_type"] == "expiry_date"
    assert by_id[old.id]["tier"] is None and by_id[old.id]["bucket"] == "expired"
    assert [row["days_remaining"] for row in rows] == sorted(
        row["days_remaining"] for row in rows
    )
    assert rows[0]["asset_id"] == old.id

    summary = body["summary"]
    assert set(summary) == {"by_tier", "by_bucket", "unresolved", "total"}
    assert sum(summary["by_bucket"].values()) == len(rows)
    assert sum(summary["by_tier"].values()) == len(rows)
    assert summary["unresolved"] == len(body["unresolved_rows"])
    assert summary["total"] == len(rows) + len(body["unresolved_rows"])
    assert summary["total"] == 7

    unresolved = {row["asset_id"]: row["reason"] for row in body["unresolved_rows"]}
    assert unresolved[cream.id] == "needs_evidence"
    assert unresolved[passport.id] == "dateless"
    assert unresolved[proposed.id] == "proposed"
    assert unresolved[unparseable.id] == "unparseable"
    assert all(set(row) == {"asset_id", "reason"} for row in body["unresolved_rows"])
    assert before == after


def test_route_empty_sets_are_200_and_zeroed(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, household_b = engine_db
    as_of = _today()
    asset = make_asset(session, household_a, "Only food")
    add_classification(session, asset, "food_beverages")
    add_expiry(session, asset, {"expiry_date": (as_of + timedelta(days=1)).isoformat()})

    with TestClient(app) as client:
        empty_household = _status(client, household_b, as_of=as_of.isoformat())
        no_match = _status(client, household_a, category="documents_other", as_of=as_of.isoformat())
        unknown_slug = _status(client, household_a, category="made-up", as_of=as_of.isoformat())

    for response in (empty_household, no_match, unknown_slug):
        assert response.status_code == 200
        body = response.json()
        assert body["rows"] == []
        assert body["unresolved_rows"] == []
        assert body["summary"] == {
            "by_tier": {},
            "by_bucket": {},
            "unresolved": 0,
            "total": 0,
        }


def test_route_category_filter_narrows_without_fallback(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    as_of = _today()
    food = make_asset(session, household_a, "Food")
    add_classification(session, food, "food_beverages")
    add_expiry(session, food, {"expiry_date": (as_of + timedelta(days=1)).isoformat()})
    med = make_asset(session, household_a, "Medicine")
    add_classification(session, med, "medicine_pharma")
    add_expiry(session, med, {"expiry_date": (as_of + timedelta(days=1)).isoformat()})

    with TestClient(app) as client:
        filtered = _status(client, household_a, category="medicine", as_of=as_of.isoformat())

    assert filtered.status_code == 200
    body = filtered.json()
    assert [row["asset_id"] for row in body["rows"]] == [med.id]
    assert body["category"] == "medicine_pharma"
    assert body["summary"]["total"] == 1


def test_route_unknown_household_404(engine_db) -> None:  # type: ignore[no-untyped-def]
    _session, _household_a, _household_b = engine_db
    with TestClient(app) as client:
        response = _status(client, "00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["status"] == 404


def test_route_unparseable_as_of_422(engine_db) -> None:  # type: ignore[no-untyped-def]
    _session, household_a, _household_b = engine_db
    with TestClient(app) as client:
        response = _status(client, household_a, as_of="2026-13-40")
    assert response.status_code == 422
    assert "as_of" in response.json()["detail"]


def test_route_default_as_of_is_live_today(engine_db) -> None:  # type: ignore[no-untyped-def]
    session, household_a, _household_b = engine_db
    asset = make_asset(session, household_a, "Today boundary")
    add_classification(session, asset, "food_beverages")
    add_expiry(session, asset, {"expiry_date": _today().isoformat()})

    with TestClient(app) as client:
        response = _status(client, household_a)
    assert response.status_code == 200
    body = response.json()
    assert body["as_of"] == _today().isoformat()
    assert body["rows"][0]["days_remaining"] == 0
