"""SG-111: Asset lifecycle vocabulary, transition enforcement, readers, backfill.

The transition expectations below are an INDEPENDENT oracle typed from the
blueprint (``DRAFT -> PENDING_REVIEW -> ACTIVE -> ARCHIVED -> DISPOSED`` plus the
reserved ``ACTIVE -> MERGED``), never imported from the module under test. The
API matrix drives every ordered pair through the REAL ``PATCH /v1/assets/{id}``
route, so the fail half of the fail-then-pass is a genuine behaviour difference
(base has no validation and answers 200), not a missing-module import error.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, Household
from app.plugins.expiry_tracker import CLASSIFICATION_FIELD, EXPIRY_FIELD
from app.services import expiry_engine

# Independent oracle (NOT imported from app.services.lifecycle).
LEGAL: dict[str, set[str]] = {
    "DRAFT": {"PENDING_REVIEW"},
    "PENDING_REVIEW": {"ACTIVE"},
    "ACTIVE": {"ARCHIVED", "MERGED"},
    "ARCHIVED": {"DISPOSED"},
    "DISPOSED": set(),
    "MERGED": set(),
}
VOCABULARY: tuple[str, ...] = tuple(LEGAL)
CHAIN: tuple[str, ...] = ("DRAFT", "PENDING_REVIEW", "ACTIVE", "ARCHIVED", "DISPOSED")

BACKFILL_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "backfill_asset_lifecycle.py"


def _today() -> date:
    return datetime.now(timezone.utc).date()


@pytest.fixture
def lifecycle_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg111.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG111 Household")
    other = Household(name="SG111 Other")
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


def make_asset(session: Session, household_id: str, status: str, name: str = "Item") -> Asset:
    asset = Asset(
        household_id=household_id, display_name=name, asset_type="product", status=status
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


def _patch_status(client: TestClient, asset_id: str, household_id: str, status: str):  # type: ignore[no-untyped-def]
    return client.patch(
        f"/v1/assets/{asset_id}", params={"household_id": household_id}, json={"status": status}
    )


def _load_backfill():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("sg111_backfill", BACKFILL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- vocabulary + transition table (unit; the module is the thing introduced) --


def test_vocabulary_literals_are_exact() -> None:
    from app.services import lifecycle

    assert set(lifecycle.LIFECYCLE_STATUSES) == set(VOCABULARY)
    assert len(lifecycle.LIFECYCLE_STATUSES) == 6


def test_transition_table_matches_the_blueprint_oracle() -> None:
    from app.services import lifecycle

    assert {key: set(value) for key, value in lifecycle.TRANSITIONS.items()} == LEGAL


def test_every_ordered_pair_legal_or_rejected() -> None:
    from app.services import lifecycle

    for current in VOCABULARY:
        for requested in VOCABULARY:
            legal = requested == current or requested in LEGAL[current]
            if legal:
                lifecycle.validate_transition(current, requested)
            else:
                with pytest.raises(lifecycle.LifecycleTransitionError):
                    lifecycle.validate_transition(current, requested)


def test_legal_chain_walks_end_to_end_and_terminals_are_closed() -> None:
    from app.services import lifecycle

    current = CHAIN[0]
    for nxt in CHAIN[1:]:
        lifecycle.validate_transition(current, nxt)
        current = nxt
    assert current == "DISPOSED"
    with pytest.raises(lifecycle.LifecycleTransitionError):
        lifecycle.validate_transition("DISPOSED", "ACTIVE")
    with pytest.raises(lifecycle.LifecycleTransitionError):
        lifecycle.validate_transition("MERGED", "ACTIVE")


# --- API: the transition matrix through the REAL route -------------------------


def test_patch_transition_matrix_through_real_route(lifecycle_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = lifecycle_db
    with TestClient(app) as client:
        for current in VOCABULARY:
            for requested in VOCABULARY:
                asset = make_asset(session, household_id, current, f"{current}->{requested}")
                response = _patch_status(client, asset.id, household_id, requested)
                legal = requested == current or requested in LEGAL[current]
                assert response.status_code == (200 if legal else 422), (
                    current,
                    requested,
                    response.status_code,
                )
                if not legal:
                    detail = response.json()["detail"]
                    assert "illegal status transition" in detail
                    assert f"legal from {current!r}" in detail
                    assert str(sorted(LEGAL[current])) in detail


def test_patch_unknown_status_is_422(lifecycle_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = lifecycle_db
    asset = make_asset(session, household_id, "ACTIVE")
    with TestClient(app) as client:
        response = _patch_status(client, asset.id, household_id, "BOGUS")
    assert response.status_code == 422
    assert "legal from 'ACTIVE'" in response.json()["detail"]


def test_patch_legal_chain_through_real_route(lifecycle_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = lifecycle_db
    asset = make_asset(session, household_id, "DRAFT")
    with TestClient(app) as client:
        for nxt in CHAIN[1:]:
            assert _patch_status(client, asset.id, household_id, nxt).status_code == 200
        detail = client.get(
            f"/v1/assets/{asset.id}", params={"household_id": household_id}
        ).json()
    assert detail["status"] == "DISPOSED"
    with TestClient(app) as client:
        backward = _patch_status(client, asset.id, household_id, "ARCHIVED")
    assert backward.status_code == 422
    assert "legal from 'DISPOSED': []" in backward.json()["detail"]


def test_delete_archives_through_the_map(lifecycle_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = lifecycle_db
    active = make_asset(session, household_id, "ACTIVE", "Deletable")
    draft = make_asset(session, household_id, "DRAFT", "Draft")
    with TestClient(app) as client:
        first = client.delete(f"/v1/assets/{active.id}", params={"household_id": household_id})
        assert first.status_code == 200
        read_back = client.get(
            f"/v1/assets/{active.id}", params={"household_id": household_id}
        ).json()
        assert read_back["status"] == "ARCHIVED"
        # Re-archiving an already ARCHIVED asset is a same-status no-op.
        second = client.delete(f"/v1/assets/{active.id}", params={"household_id": household_id})
        assert second.status_code == 200
        blocked = client.delete(f"/v1/assets/{draft.id}", params={"household_id": household_id})
    assert blocked.status_code == 422
    assert "legal from 'DRAFT': ['PENDING_REVIEW']" in blocked.json()["detail"]


# --- readers -------------------------------------------------------------------


def test_engine_excludes_non_active_from_rows_and_unresolved(lifecycle_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = lifecycle_db
    as_of = _today()
    active = make_asset(session, household_id, "ACTIVE", "Active")
    add_classification(session, active, "food_beverages")
    add_expiry(session, active, {"expiry_date": (as_of + timedelta(days=2)).isoformat()})
    archived = make_asset(session, household_id, "ARCHIVED", "Archived")
    add_classification(session, archived, "food_beverages")
    add_expiry(session, archived, {"expiry_date": (as_of + timedelta(days=2)).isoformat()})
    archived_proposed = make_asset(session, household_id, "ARCHIVED", "Archived proposed")
    add_classification(session, archived_proposed, "food_beverages")
    add_expiry(
        session,
        archived_proposed,
        {"expiry_date": (as_of + timedelta(days=1)).isoformat()},
        review_state="proposed",
    )

    result = expiry_engine.compute_status(session, household_id, as_of)
    row_ids = {row["asset_id"] for row in result["rows"]}
    unresolved_ids = {row["asset_id"] for row in result["unresolved_rows"]}
    assert row_ids == {active.id}
    assert archived.id not in row_ids and archived.id not in unresolved_ids
    assert archived_proposed.id not in row_ids and archived_proposed.id not in unresolved_ids
    assert result["summary"]["total"] == 1


def test_assets_list_status_filter(lifecycle_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = lifecycle_db
    active = make_asset(session, household_id, "ACTIVE", "Live")
    archived = make_asset(session, household_id, "ARCHIVED", "Old")
    with TestClient(app) as client:
        active_only = client.get(
            "/v1/assets", params={"household_id": household_id, "status": "ACTIVE", "limit": 100}
        ).json()
        archived_only = client.get(
            "/v1/assets", params={"household_id": household_id, "status": "ARCHIVED", "limit": 100}
        ).json()
    assert {row["id"] for row in active_only["items"]} == {active.id}
    assert {row["id"] for row in archived_only["items"]} == {archived.id}


def test_analytics_chat_planning_active_semantics_unchanged(lifecycle_db) -> None:  # type: ignore[no-untyped-def]
    from app.services.analytics.service import compute_stats
    from app.services.chat.service import build_catalog as chat_catalog
    from app.services.planning.service import build_catalog as planning_catalog

    session, household_id, _ = lifecycle_db
    active = make_asset(session, household_id, "ACTIVE", "Live")
    add_classification(session, active, "food_beverages")
    archived = make_asset(session, household_id, "ARCHIVED", "Old")
    add_classification(session, archived, "food_beverages")

    stats = compute_stats(session, household_id)
    assert stats["assets"]["total"] == 2
    assert stats["assets"]["active"] == 1
    assert stats["assets"]["by_status"] == {"ACTIVE": 1, "ARCHIVED": 1}

    planning_ids = {row["id"] for row in planning_catalog(session, household_id)}
    chat_ids = {row["id"] for row in chat_catalog(session, household_id, "food")}
    assert planning_ids == {active.id}
    assert chat_ids == {active.id}


# --- backfill (real script bytes, temp DB) -------------------------------------


def test_backfill_dry_run_then_apply_on_temp(tmp_path: Path) -> None:
    backfill = _load_backfill()
    db_path = tmp_path / "temp.db"
    connection = sqlite3.connect(db_path)
    connection.execute("CREATE TABLE asset (id TEXT PRIMARY KEY, status TEXT NOT NULL)")
    connection.executemany(
        "INSERT INTO asset (id, status) VALUES (?, ?)",
        [
            ("a1", "ACTIVE"),
            ("a2", "ACTIVE"),
            ("a3", "ARCHIVED"),
            ("a4", "active"),
            ("a5", "DELETED"),
            ("a6", " MERGED "),
        ],
    )
    connection.commit()
    try:
        before = backfill.census(connection)
        planned = backfill.plan(connection)
        projected = backfill.projected_census(connection)
        assert backfill.census(connection) == before  # dry-run wrote nothing
        assert ("active", "ACTIVE", 1) in planned
        assert ("DELETED", "ARCHIVED", 1) in planned
        assert (" MERGED ", "MERGED", 1) in planned
        assert before == {"ACTIVE": 2, "ARCHIVED": 1, "active": 1, "DELETED": 1, " MERGED ": 1}
        changed = backfill.apply_changes(connection)
        assert changed == 3
        assert backfill.census(connection) == {"ACTIVE": 3, "ARCHIVED": 2, "MERGED": 1}
        assert projected == backfill.census(connection)
    finally:
        connection.close()


def test_backfill_is_idempotent_on_a_clean_vocabulary(tmp_path: Path) -> None:
    backfill = _load_backfill()
    db_path = tmp_path / "clean.db"
    connection = sqlite3.connect(db_path)
    connection.execute("CREATE TABLE asset (id TEXT PRIMARY KEY, status TEXT NOT NULL)")
    connection.executemany(
        "INSERT INTO asset (id, status) VALUES (?, ?)", [("a1", "ACTIVE"), ("a2", "ARCHIVED")]
    )
    connection.commit()
    try:
        assert backfill.plan(connection) == []
        assert backfill.apply_changes(connection) == 0
        assert backfill.census(connection) == {"ACTIVE": 1, "ARCHIVED": 1}
    finally:
        connection.close()
