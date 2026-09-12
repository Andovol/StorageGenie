from __future__ import annotations

import io
import platform
import statistics
import time
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Asset, Evidence, Household, asset_evidence
from app.models.base import new_id
from app.services.asset_service import create_asset
from app.services.evidence_service import store_evidence
from app.services.fts import rebuild_asset_fts


@pytest.fixture
def search_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{tmp_path / 'search.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = session_factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = session_factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    household = Household(name="Search Test Household")
    session.add(household)
    session.commit()
    evidence = store_evidence(jpeg_bytes(), "search.jpg", "image/jpeg", household.id, session)
    specs = [
        ("Kitchen Blender", "appliance", "ACTIVE", True),
        ("Garden Chair", "furniture", "ACTIVE", False),
        ("Kitchen Table", "furniture", "ARCHIVED", True),
        ("Office Lamp", "appliance", "ARCHIVED", False),
        ("Garage Shelf", "storage", "ACTIVE", False),
    ]
    assets: dict[str, Asset] = {}
    for name, asset_type, status, has_evidence in specs:
        assets[name] = create_asset(
            session,
            household.id,
            {
                "display_name": name,
                "asset_type": asset_type,
                "status": status,
                "evidence_ids": [evidence.id] if has_evidence else [],
            },
        )
    try:
        yield session, household.id, assets
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def jpeg_bytes() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (32, 32), "green").save(output, format="JPEG")
    return output.getvalue()


def filtered_ids(client: TestClient, household_id: str, **filters: object) -> set[str]:
    response = client.get(
        "/v1/assets",
        params={"household_id": household_id, "limit": 100, **filters},
    )
    assert response.status_code == 200
    return {item["id"] for item in response.json()["items"]}


def test_search_q_returns_exact_mixed_fixture_ids(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    _, household_id, assets = search_fixtures
    with TestClient(app) as client:
        actual = filtered_ids(client, household_id, q="Kitchen")

    expected = {assets["Kitchen Blender"].id, assets["Kitchen Table"].id}
    all_ids = {asset.id for asset in assets.values()}
    assert expected and expected < all_ids
    assert actual == expected


def test_search_q_matches_multiple_literal_tokens(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    _, household_id, assets = search_fixtures
    with TestClient(app) as client:
        actual = filtered_ids(client, household_id, q="Kitchen Blender")

    assert actual == {assets["Kitchen Blender"].id}


def test_search_q_quotes_hostile_match_syntax(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = search_fixtures
    operator_named = create_asset(
        session,
        household_id,
        {"display_name": "OR 1 1", "asset_type": "test", "status": "ACTIVE"},
    )
    unterminated_named = create_asset(
        session,
        household_id,
        {"display_name": "unterminated quote", "asset_type": "test", "status": "ACTIVE"},
    )
    with TestClient(app) as client:
        hostile = filtered_ids(client, household_id, q='" OR "1"="1')
        unterminated = filtered_ids(client, household_id, q='unterminated "')

    assert hostile == {operator_named.id}
    assert unterminated == {unterminated_named.id}


def test_search_q_keeps_same_named_asset_in_other_household_isolated(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    session, household_id, assets = search_fixtures
    other_household = Household(name="Other Search Household")
    session.add(other_household)
    session.commit()
    other_asset = create_asset(
        session,
        other_household.id,
        {
            "display_name": "Kitchen Blender",
            "asset_type": "appliance",
            "status": "ACTIVE",
        },
    )
    with TestClient(app) as client:
        actual = filtered_ids(client, household_id, q="Kitchen Blender")

    assert actual == {assets["Kitchen Blender"].id}
    assert other_asset.id not in actual


def test_search_q_rebuild_restores_matches(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    session, household_id, assets = search_fixtures
    with TestClient(app) as client:
        before = filtered_ids(client, household_id, q="Kitchen")
        session.execute(text("INSERT INTO asset_fts(asset_fts) VALUES ('delete-all')"))
        session.commit()
        assert filtered_ids(client, household_id, q="Kitchen") == set()
        rebuild_asset_fts(session.connection())
        session.commit()
        after = filtered_ids(client, household_id, q="Kitchen")

    expected = {assets["Kitchen Blender"].id, assets["Kitchen Table"].id}
    assert before == expected
    assert after == expected


def test_fts_triggers_follow_asset_insert_update_delete(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = search_fixtures
    asset = create_asset(
        session,
        household_id,
        {"display_name": "Trigger Original", "asset_type": "test", "status": "ACTIVE"},
    )
    with TestClient(app) as client:
        assert filtered_ids(client, household_id, q="Trigger Original") == {asset.id}
        asset.display_name = "Trigger Updated"
        session.commit()
        assert filtered_ids(client, household_id, q="Trigger Original") == set()
        assert filtered_ids(client, household_id, q="Trigger Updated") == {asset.id}
        session.delete(asset)
        session.commit()
        assert filtered_ids(client, household_id, q="Trigger Updated") == set()


def test_search_asset_type_returns_exact_mixed_fixture_ids(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    _, household_id, assets = search_fixtures
    with TestClient(app) as client:
        actual = filtered_ids(client, household_id, asset_type="appliance")

    expected = {assets["Kitchen Blender"].id, assets["Office Lamp"].id}
    all_ids = {asset.id for asset in assets.values()}
    assert expected and expected < all_ids
    assert actual == expected


def test_search_status_returns_exact_mixed_fixture_ids(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    _, household_id, assets = search_fixtures
    with TestClient(app) as client:
        actual = filtered_ids(client, household_id, status="ACTIVE")

    expected = {
        assets["Kitchen Blender"].id,
        assets["Garden Chair"].id,
        assets["Garage Shelf"].id,
    }
    all_ids = {asset.id for asset in assets.values()}
    assert expected and expected < all_ids
    assert actual == expected


def test_search_has_evidence_returns_exact_ids_for_both_polarities(search_fixtures) -> None:  # type: ignore[no-untyped-def]
    _, household_id, assets = search_fixtures
    with TestClient(app) as client:
        with_evidence = filtered_ids(client, household_id, has_evidence=True)
        without_evidence = filtered_ids(client, household_id, has_evidence=False)

    expected_with = {assets["Kitchen Blender"].id, assets["Kitchen Table"].id}
    expected_without = {
        assets["Garden Chair"].id,
        assets["Office Lamp"].id,
        assets["Garage Shelf"].id,
    }
    assert with_evidence == expected_with
    assert without_evidence == expected_without
    assert with_evidence and without_evidence
    assert with_evidence.isdisjoint(without_evidence)


def test_fts_migration_upgrade_downgrade_upgrade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "fts-migration.db"
    url = f"sqlite:///{database_path}"
    monkeypatch.setattr(settings, "database_url", url)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    engine = create_engine(url)
    try:
        assert "asset" in inspect(engine).get_table_names()
        with engine.connect() as connection:
            assert connection.execute(
                text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'asset_fts'")
            ).first()
        command.downgrade(config, "20260908_sg014_candidate")
        with engine.connect() as connection:
            assert connection.execute(
                text("SELECT 1 FROM sqlite_master WHERE name = 'asset_fts'")
            ).first() is None
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert connection.execute(
                text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'asset_fts'")
            ).first()
    finally:
        engine.dispose()


def test_search_10k_fixture_latency_is_observed_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "latency.db"
    engine = create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        from app.services.fts import install_asset_fts

        install_asset_fts(connection, rebuild=True)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="10k Latency Household")
    session.add(household)
    session.commit()
    evidence = Evidence(
        household_id=household.id,
        sha256="f" * 64,
        storage_key="latency/evidence.jpg",
        media_type="image/jpeg",
        original_filename="evidence.jpg",
        size_bytes=1,
    )
    session.add(evidence)
    session.commit()
    asset_rows = [
        {
            "id": new_id(),
            "household_id": household.id,
            "display_name": f"Fixture asset {index:05d}",
            "asset_type": "test",
            "status": "ACTIVE",
            "version": 1,
        }
        for index in range(10_000)
    ]
    session.execute(Asset.__table__.insert(), asset_rows)
    session.execute(
        asset_evidence.insert(),
        [{"asset_id": row["id"], "evidence_id": evidence.id} for row in asset_rows[::1000]],
    )
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            durations = []
            for _ in range(20):
                started = time.perf_counter()
                response = client.get(
                    "/v1/assets",
                    params={"household_id": household.id, "q": "Fixture", "limit": 20},
                )
                durations.append(time.perf_counter() - started)
                assert response.status_code == 200
                assert response.json()["items"]
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()

    ordered = sorted(durations)
    p50 = statistics.median(ordered)
    p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
    print(
        f"10k FTS latency machine={platform.node()} platform={platform.platform()} "
        f"p50={p50 * 1000:.2f}ms p95={p95 * 1000:.2f}ms samples={len(ordered)}"
    )
