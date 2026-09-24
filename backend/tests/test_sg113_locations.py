"""SG-113 location tree + asset-location assignment (offline, $0, temp DBs only).

Scope: the new ``location`` / ``asset_location`` tables + ONE migration + the
flag-gated routes + the asset-detail ``locations[]`` reader. The production
migration is NOT run here (the flag stays OFF in production); every database is
a temp SQLite file. The §9.2 seed names are never pre-created and never trusted
as the set.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect as sa_inspect
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Asset, Household

# The association table is imported lazily inside the one test that needs it so
# the fail-run against BASE (where the module does not exist) still collects
# and reaches the behavioural route fails, instead of dying at collection.
HEAD_REVISION = "20260924_sg113_location"
PREVIOUS_REVISION = "20260923_sg100_enrich_snapshot"


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[1] / "alembic")
    )
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_sg113_migration_upgrade_downgrade_upgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'sg113_migration.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)

    command.upgrade(config, "head")
    inspector = sa_inspect(create_engine(url))
    tables = set(inspector.get_table_names())
    assert {"location", "asset_location"} <= tables
    assert {ix["name"] for ix in inspector.get_indexes("location")} >= {
        "ix_location_household_id",
        "ix_location_parent_id",
    }
    assert {ix["name"] for ix in inspector.get_indexes("asset_location")} >= {
        "ix_asset_location_location_id"
    }
    pk = inspector.get_pk_constraint("asset_location")
    assert set(pk["constrained_columns"]) == {"asset_id", "location_id"}

    command.downgrade(config, PREVIOUS_REVISION)
    remaining = set(sa_inspect(create_engine(url)).get_table_names())
    assert "location" not in remaining
    assert "asset_location" not in remaining

    command.upgrade(config, "head")
    assert {"location", "asset_location"} <= set(
        sa_inspect(create_engine(url)).get_table_names()
    )


def _set_flag(monkeypatch: pytest.MonkeyPatch, value: bool) -> None:
    # The flag does not exist on BASE; guard so the fail-run still collects and
    # reaches the behavioural route fails rather than erroring in setup.
    if hasattr(settings, "sg_locations_enabled"):
        monkeypatch.setattr(settings, "sg_locations_enabled", value)


@pytest.fixture(autouse=True)
def _locations_on(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_flag(monkeypatch, True)


@pytest.fixture
def loc_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg113.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG113 Household")
    other = Household(name="SG113 Other")
    session.add_all([household, other])
    session.commit()
    asset = Asset(
        household_id=household.id, display_name="Milk", asset_type="product", status="ACTIVE"
    )
    other_asset = Asset(
        household_id=other.id, display_name="Bread", asset_type="product", status="ACTIVE"
    )
    session.add_all([asset, other_asset])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, other.id, asset.id, other_asset.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _create(client: TestClient, household_id: str, name: str, parent_id: str | None = None):
    body: dict[str, object] = {"name": name}
    if parent_id is not None:
        body["parent_id"] = parent_id
    return client.post("/v1/locations", params={"household_id": household_id}, json=body)


def test_flag_off_every_new_route_is_404(loc_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, asset_id, _ = loc_db
    _set_flag(monkeypatch, False)
    with TestClient(app) as client:
        p = {"household_id": hh}
        assert client.get("/v1/locations", params=p).status_code == 404
        assert client.post("/v1/locations", params=p, json={"name": "Fridge"}).status_code == 404
        assert (
            client.patch("/v1/locations/missing", params=p, json={"name": "x"}).status_code
            == 404
        )
        assert client.delete("/v1/locations/missing", params=p).status_code == 404
        assert (
            client.post(
                f"/v1/assets/{asset_id}/locations",
                params=p,
                json={"location_id": "missing"},
            ).status_code
            == 404
        )
        assert (
            client.delete(f"/v1/assets/{asset_id}/locations/missing", params=p).status_code
            == 404
        )
        detail = client.get(f"/v1/assets/{asset_id}", params=p)
        assert detail.status_code == 200
        assert "locations" not in detail.json()


def test_seed_names_are_not_precreated(loc_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, *_ = loc_db
    with TestClient(app) as client:
        response = client.get("/v1/locations", params={"household_id": hh})
        assert response.status_code == 200
        assert response.json()["items"] == []


def test_tree_create_child_reparent_and_cycle_refusal(loc_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, *_ = loc_db
    with TestClient(app) as client:
        a = _create(client, hh, "Kitchen").json()
        b = _create(client, hh, "Fridge", a["id"]).json()
        c = _create(client, hh, "Freezer", b["id"]).json()
        assert b["parent_id"] == a["id"]

        reparented = client.patch(
            f"/v1/locations/{c['id']}", params={"household_id": hh}, json={"parent_id": a["id"]}
        )
        assert reparented.status_code == 200
        assert reparented.json()["parent_id"] == a["id"]

        renamed = client.patch(
            f"/v1/locations/{a['id']}",
            params={"household_id": hh},
            json={"name": "Kitchen Renamed"},
        )
        assert renamed.status_code == 200
        assert renamed.json()["name"] == "Kitchen Renamed"

        self_parent = client.patch(
            f"/v1/locations/{a['id']}", params={"household_id": hh}, json={"parent_id": a["id"]}
        )
        assert self_parent.status_code == 422

        # a -> c now (c reparented under a); reparenting a under its own
        # descendant c closes a loop.
        cycle = client.patch(
            f"/v1/locations/{a['id']}", params={"household_id": hh}, json={"parent_id": c["id"]}
        )
        assert cycle.status_code == 422

        assert _create(client, hh, "Orphan", "no-such-parent").status_code == 404
        foreign = _create(client, other, "Foreign").json()
        assert _create(client, hh, "BadParent", foreign["id"]).status_code == 403


def test_name_validation(loc_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, *_ = loc_db
    with TestClient(app) as client:
        assert _create(client, hh, "").status_code == 422
        assert _create(client, hh, "   ").status_code == 422
        assert _create(client, hh, "x" * 201).status_code == 422
        stripped = _create(client, hh, "  Pantry  ").json()
        assert stripped["name"] == "Pantry"
        missing_household = client.post(
            "/v1/locations", params={"household_id": "missing"}, json={"name": "x"}
        )
        assert missing_household.status_code == 404


def test_delete_with_assignments_409_and_empty_delete_200(loc_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, asset_id, _ = loc_db
    with TestClient(app) as client:
        loc = _create(client, hh, "Pantry").json()
        assigned = client.post(
            f"/v1/assets/{asset_id}/locations",
            params={"household_id": hh},
            json={"location_id": loc["id"]},
        )
        assert assigned.status_code == 200

        blocked = client.delete(f"/v1/locations/{loc['id']}", params={"household_id": hh})
        assert blocked.status_code == 409

        removed = client.delete(
            f"/v1/assets/{asset_id}/locations/{loc['id']}", params={"household_id": hh}
        )
        assert removed.status_code == 200
        deleted = client.delete(f"/v1/locations/{loc['id']}", params={"household_id": hh})
        assert deleted.status_code == 200


def test_delete_with_children_409(loc_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, *_ = loc_db
    with TestClient(app) as client:
        parent = _create(client, hh, "Garage").json()
        _create(client, hh, "Shelf", parent["id"])
        blocked = client.delete(f"/v1/locations/{parent['id']}", params={"household_id": hh})
        assert blocked.status_code == 409


def test_assign_unassign_idempotent_and_asset_detail_roundtrip(loc_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, asset_id, _ = loc_db
    with TestClient(app) as client:
        loc = _create(client, hh, "Bathroom Cabinet").json()
        for _ in range(2):
            assigned = client.post(
                f"/v1/assets/{asset_id}/locations",
                params={"household_id": hh},
                json={"location_id": loc["id"]},
            )
            assert assigned.status_code == 200

        from app.models.location import asset_location

        session.expire_all()
        rows = session.execute(asset_location.select()).fetchall()
        assert len(rows) == 1

        detail = client.get(f"/v1/assets/{asset_id}", params={"household_id": hh}).json()
        assert detail["locations"] == [
            {"id": loc["id"], "name": "Bathroom Cabinet", "parent_id": None}
        ]

        for _ in range(2):
            removed = client.delete(
                f"/v1/assets/{asset_id}/locations/{loc['id']}", params={"household_id": hh}
            )
            assert removed.status_code == 200

        detail = client.get(f"/v1/assets/{asset_id}", params={"household_id": hh}).json()
        assert detail["locations"] == []


def test_cross_household_refusals(loc_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, asset_id, other_asset_id = loc_db
    with TestClient(app) as client:
        loc = _create(client, hh, "Fridge").json()
        assert (
            client.patch(
                f"/v1/locations/{loc['id']}", params={"household_id": other}, json={"name": "x"}
            ).status_code
            == 403
        )
        assert (
            client.delete(f"/v1/locations/{loc['id']}", params={"household_id": other}).status_code
            == 403
        )
        foreign = _create(client, other, "Foreign Shelf").json()
        assert (
            client.post(
                f"/v1/assets/{asset_id}/locations",
                params={"household_id": hh},
                json={"location_id": foreign["id"]},
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/v1/assets/{other_asset_id}/locations",
                params={"household_id": hh},
                json={"location_id": loc["id"]},
            ).status_code
            == 403
        )
        assert (
            client.get(f"/v1/assets/{asset_id}", params={"household_id": other}).status_code == 403
        )
