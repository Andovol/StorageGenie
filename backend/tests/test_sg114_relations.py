"""SG-114 asset relations: typed links (offline, $0, temp DBs only).

Scope: the new ``asset_relation`` table + ONE migration + the flag-gated
relation routes + the asset-detail ``relations[]`` reader. The production
migration is NOT run here (the flag stays OFF in production); every database is
a temp SQLite file. The relation vocabulary is pinned to exactly two types;
duplicate ownership stays with the SG-112 merge redirect, never a relation type.
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

# The relation model/API are imported lazily inside the tests that need them so
# the fail-run against BASE (where the modules do not exist) still collects and
# reaches the behavioural route fails instead of dying at collection.
HEAD_REVISION = "20260924_sg114_relation"
PREVIOUS_REVISION = "20260924_sg113_location"
RELATION_SURFACE = (
    "app/models/relation.py",
    "app/api/v1/relations.py",
    "alembic/versions/20260924_sg114_relation.py",
)


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[1] / "alembic")
    )
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_sg114_migration_upgrade_downgrade_upgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'sg114_migration.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)

    command.upgrade(config, "head")
    inspector = sa_inspect(create_engine(url))
    tables = set(inspector.get_table_names())
    assert "asset_relation" in tables
    assert {ix["name"] for ix in inspector.get_indexes("asset_relation")} >= {
        "ix_asset_relation_household_id",
        "ix_asset_relation_from_asset_id",
        "ix_asset_relation_to_asset_id",
    }
    unique = {
        u["name"]: set(u["column_names"])
        for u in inspector.get_unique_constraints("asset_relation")
    }
    assert unique.get("uq_asset_relation_from_to_type") == {
        "from_asset_id",
        "to_asset_id",
        "relation_type",
    }

    command.downgrade(config, PREVIOUS_REVISION)
    remaining = set(sa_inspect(create_engine(url)).get_table_names())
    assert "asset_relation" not in remaining

    command.upgrade(config, "head")
    assert "asset_relation" in set(sa_inspect(create_engine(url)).get_table_names())


def test_vocabulary_is_exactly_two_types() -> None:
    from app.api.v1.relations import RELATION_TYPES

    # A third type is a new decision, never a design call: the pin is the guard.
    assert RELATION_TYPES == frozenset({"related_to", "contains"})
    assert not any("duplicate" in name for name in RELATION_TYPES)


def test_relation_surface_has_no_duplicate_of_type() -> None:
    # Duplicate ownership is owned by the SG-112 merge redirect
    # (`merge.merged_into`), never a relation type. The pre-existing
    # `duplicate_of_asset` dedup PROPOSAL kind elsewhere is out of scope.
    root = Path(__file__).resolve().parents[1]
    for rel_path in RELATION_SURFACE:
        assert "duplicate_of" not in (root / rel_path).read_text()


def _set_flag(monkeypatch: pytest.MonkeyPatch, value: bool) -> None:
    # The flag does not exist on BASE; guard so the fail-run still collects and
    # reaches the behavioural route fails rather than erroring in setup.
    if hasattr(settings, "sg_relations_enabled"):
        monkeypatch.setattr(settings, "sg_relations_enabled", value)


@pytest.fixture(autouse=True)
def _relations_on(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_flag(monkeypatch, True)


@pytest.fixture
def rel_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg114.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG114 Household")
    other = Household(name="SG114 Other")
    session.add_all([household, other])
    session.commit()
    a = Asset(household_id=household.id, display_name="Toolbox", asset_type="product", status="ACTIVE")
    b = Asset(household_id=household.id, display_name="Screwdriver", asset_type="product", status="ACTIVE")
    foreign = Asset(household_id=other.id, display_name="Foreign", asset_type="product", status="ACTIVE")
    session.add_all([a, b, foreign])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, other.id, a.id, b.id, foreign.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _create(
    client: TestClient,
    household_id: str,
    from_asset_id: str,
    to_asset_id: str,
    relation_type: str = "related_to",
):
    return client.post(
        f"/v1/assets/{from_asset_id}/relations",
        params={"household_id": household_id},
        json={"to_asset_id": to_asset_id, "relation_type": relation_type},
    )


def _count(session: Session) -> int:
    from app.models.relation import AssetRelation

    session.expire_all()
    return session.query(AssetRelation).count()


def test_flag_off_every_new_route_is_404(rel_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, a, b, foreign = rel_db
    _set_flag(monkeypatch, False)
    with TestClient(app) as client:
        params = {"household_id": hh}
        assert client.get(f"/v1/assets/{a}/relations", params=params).status_code == 404
        assert _create(client, hh, a, b).status_code == 404
        assert (
            client.delete(f"/v1/assets/{a}/relations/missing", params=params).status_code == 404
        )
        detail = client.get(f"/v1/assets/{a}", params=params)
        assert detail.status_code == 200
        assert "relations" not in detail.json()


def test_empty_relations_when_on(rel_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, a, b, foreign = rel_db
    with TestClient(app) as client:
        listing = client.get(f"/v1/assets/{a}/relations", params={"household_id": hh})
        assert listing.status_code == 200
        assert listing.json()["items"] == []
        detail = client.get(f"/v1/assets/{a}", params={"household_id": hh})
        # ON means the key is PRESENT and empty, never absent (the reader half).
        assert detail.json()["relations"] == []


def test_create_read_both_directions_delete_idempotent(rel_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, a, b, foreign = rel_db
    with TestClient(app) as client:
        params = {"household_id": hh}
        created = _create(client, hh, a, b, "contains")
        assert created.status_code == 201
        row = created.json()
        assert row["from_asset_id"] == a
        assert row["to_asset_id"] == b
        assert row["relation_type"] == "contains"
        assert row["direction"] == "outgoing"
        assert _count(session) == 1

        # The SAME typed link twice is one row -> 409, nothing written.
        duplicate = _create(client, hh, a, b, "contains")
        assert duplicate.status_code == 409
        assert _count(session) == 1

        # A different type on the same pair is a DISTINCT link.
        related = _create(client, hh, a, b, "related_to")
        assert related.status_code == 201
        assert _count(session) == 2

        # Both directions: the `from` end sees outgoing, the `to` end incoming.
        outgoing = client.get(f"/v1/assets/{a}/relations", params=params).json()["items"]
        incoming = client.get(f"/v1/assets/{b}/relations", params=params).json()["items"]
        assert {item["direction"] for item in outgoing} == {"outgoing"}
        assert {item["direction"] for item in incoming} == {"incoming"}
        assert {item["id"] for item in outgoing} == {item["id"] for item in incoming}

        # Delete is idempotent: a repeat delete of a missing link is a 200 no-op.
        for _ in range(2):
            removed = client.delete(
                f"/v1/assets/{a}/relations/{row['id']}", params=params
            )
            assert removed.status_code == 200
            assert removed.json() == {"status": "deleted", "id": row["id"]}
        assert _count(session) == 1  # only the related_to row remains


def test_refusals_write_nothing(rel_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, a, b, foreign = rel_db
    with TestClient(app) as client:
        before = _count(session)
        results = {
            "self_link": _create(client, hh, a, a).status_code,
            "illegal_type": _create(client, hh, a, b, "duplicate_of").status_code,
            "foreign_to": _create(client, hh, a, foreign).status_code,
            "foreign_from": _create(client, hh, foreign, b).status_code,
            "missing_to": _create(client, hh, a, "no-such-asset").status_code,
            "cross_household_list": client.get(
                f"/v1/assets/{a}/relations", params={"household_id": other}
            ).status_code,
            "cross_household_detail": client.get(
                f"/v1/assets/{a}", params={"household_id": other}
            ).status_code,
        }
        assert results == {
            "self_link": 422,
            "illegal_type": 422,
            "foreign_to": 403,
            "foreign_from": 403,
            "missing_to": 404,
            "cross_household_list": 403,
            "cross_household_detail": 403,
        }
        # PG-EV-02: every refusal left the table byte-identical (zero rows).
        assert _count(session) == before == 0


def test_delete_refuses_foreign_and_unrelated_links(rel_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, a, b, foreign = rel_db
    from app.models.relation import AssetRelation

    with TestClient(app) as client:
        params = {"household_id": hh}
        created = _create(client, hh, a, b).json()

        # Same household, but the link does not touch this asset -> 404 under
        # the nested path (the route is scoped to the path asset).
        c = Asset(
            household_id=hh, display_name="Extra", asset_type="product", status="ACTIVE"
        )
        session.add(c)
        session.commit()
        unrelated = client.delete(
            f"/v1/assets/{c.id}/relations/{created['id']}", params=params
        )
        assert unrelated.status_code == 404

        # A link owned by ANOTHER household is 403, never silently deleted.
        foreign_row = AssetRelation(
            household_id=other,
            from_asset_id=foreign,
            to_asset_id=foreign,
            relation_type="related_to",
        )
        session.add(foreign_row)
        session.commit()
        denied = client.delete(
            f"/v1/assets/{a}/relations/{foreign_row.id}", params=params
        )
        assert denied.status_code == 403

        # Both links survive the refused deletes (PG-EV-02).
        assert _count(session) == 2


def test_asset_detail_relations_reader_when_on(rel_db) -> None:  # type: ignore[no-untyped-def]
    session, hh, other, a, b, foreign = rel_db
    with TestClient(app) as client:
        params = {"household_id": hh}
        _create(client, hh, a, b, "contains")
        detail_a = client.get(f"/v1/assets/{a}", params=params).json()
        assert len(detail_a["relations"]) == 1
        assert detail_a["relations"][0]["direction"] == "outgoing"
        assert detail_a["relations"][0]["relation_type"] == "contains"
        detail_b = client.get(f"/v1/assets/{b}", params=params).json()
        assert len(detail_b["relations"]) == 1
        assert detail_b["relations"][0]["direction"] == "incoming"
