"""Saved searches (SG-068): named per-household filter sets.

The saved `query` is EXACTLY the catalog filter surface (`q` / `asset_type` /
`status` / `has_evidence`), so the round-trip test reads a stored search back
and issues the SAME request the manual state would have sent. Everything runs
on the real HTTP path (`TestClient`) against a scratch temp SQLite database;
the migration test runs the real Alembic chain on its own scratch database.
No test row ever touches the production database.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Household, SavedSearch
from app.schemas.saved_search import SAVED_SEARCH_QUERY_MAX_BYTES
from app.services.asset_service import create_asset
from app.services.evidence_service import store_evidence


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[1] / "alembic")
    )
    config.set_main_option("sqlalchemy.url", url)
    return config


def _png_bytes() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (8, 8), "green").save(output, format="PNG")
    return output.getvalue()


@pytest.fixture
def saved_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    engine = create_engine(
        f"sqlite:///{tmp_path / 'saved.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    first = Household(name="First Household")
    second = Household(name="Second Household")
    session.add_all([first, second])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, first.id, second.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _create(client: TestClient, household_id: str, name: str, query: dict) -> dict:
    response = client.post(
        "/v1/saved-searches",
        params={"household_id": household_id},
        json={"name": name, "query": query},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _list(client: TestClient, household_id: str) -> dict:
    response = client.get("/v1/saved-searches", params={"household_id": household_id})
    assert response.status_code == 200, response.text
    return response.json()


def test_saved_search_crud_round_trips_name_and_query(saved_db) -> None:  # type: ignore[no-untyped-def]
    _, first, _ = saved_db
    with TestClient(app) as client:
        created = _create(
            client, first, "Toothpaste restock", {"q": "toothpaste", "asset_type": "hygiene"}
        )
        listed = _list(client, first)
        deleted = client.delete(
            f"/v1/saved-searches/{created['id']}", params={"household_id": first}
        )
        after_delete = _list(client, first)

    assert created["name"] == "Toothpaste restock"
    assert created["query"] == {"q": "toothpaste", "asset_type": "hygiene"}
    assert created["id"]
    assert listed["items"] == [created]
    assert deleted.status_code == 200
    assert deleted.json() == {"status": "deleted", "id": created["id"]}
    assert after_delete["items"] == []


def test_saved_filter_reads_back_to_the_same_query_the_manual_state_sends(
    saved_db,
) -> None:  # type: ignore[no-untyped-def]
    """PG-SC-02: the recorded filter reaches read-back as a WORKING query.

    A manual catalog request and a request built from the stored search must
    hit `GET /v1/assets` with the same query string and return the same body.
    """
    session, first, _ = saved_db
    evidence = store_evidence(_png_bytes(), "blender.png", "image/png", first, session)
    create_asset(
        session,
        first,
        {
            "display_name": "Kitchen Blender",
            "asset_type": "appliance",
            "status": "ACTIVE",
            "evidence_ids": [evidence.id],
        },
    )
    create_asset(
        session,
        first,
        {"display_name": "Kitchen Table", "asset_type": "appliance", "status": "ARCHIVED"},
    )
    create_asset(
        session,
        first,
        {"display_name": "Garden Chair", "asset_type": "furniture", "status": "ACTIVE"},
    )
    query = {"q": "Kitchen", "asset_type": "appliance", "status": "ACTIVE", "has_evidence": True}

    manual_params = {"household_id": first, **query}
    with TestClient(app) as client:
        manual = client.get("/v1/assets", params=manual_params)
        created = _create(client, first, "My unreviewed appliance", query)
        stored = _list(client, first)["items"][0]
        applied = client.get("/v1/assets", params={"household_id": first, **stored["query"]})

    assert manual.status_code == 200, manual.text
    assert stored["query"] == query
    assert applied.status_code == 200, applied.text
    assert applied.json() == manual.json()
    assert dict(applied.request.url.params) == dict(manual.request.url.params)
    assert {item["display_name"] for item in applied.json()["items"]} == {"Kitchen Blender"}
    assert created["id"] == stored["id"]


def test_second_household_cannot_see_or_delete_the_firsts_search(saved_db) -> None:  # type: ignore[no-untyped-def]
    _, first, second = saved_db
    with TestClient(app) as client:
        created = _create(client, first, "Private search", {"q": "secret"})
        second_list = _list(client, second)
        refused = client.delete(
            f"/v1/saved-searches/{created['id']}", params={"household_id": second}
        )
        still_there = _list(client, first)

    assert second_list["items"] == []
    assert refused.status_code == 403
    assert [item["id"] for item in still_there["items"]] == [created["id"]]


def test_unknown_filter_key_is_rejected_and_named(saved_db) -> None:  # type: ignore[no-untyped-def]
    _, first, _ = saved_db
    with TestClient(app) as client:
        response = client.post(
            "/v1/saved-searches",
            params={"household_id": first},
            json={"name": "bad", "query": {"q": "x", "not_a_filter": "1"}},
        )
        invalid_bool = client.post(
            "/v1/saved-searches",
            params={"household_id": first},
            json={"name": "bad bool", "query": {"has_evidence": "banana"}},
        )

    assert response.status_code == 422
    assert "not_a_filter" in response.text
    assert invalid_bool.status_code == 422


def test_name_and_query_caps_reject_visibly(saved_db) -> None:  # type: ignore[no-untyped-def]
    _, first, _ = saved_db
    with TestClient(app) as client:
        long_name = client.post(
            "/v1/saved-searches",
            params={"household_id": first},
            json={"name": "n" * 81, "query": {"q": "x"}},
        )
        long_query = client.post(
            "/v1/saved-searches",
            params={"household_id": first},
            json={"name": "ok", "query": {"q": "q" * 3000}},
        )

    assert long_name.status_code == 422
    assert long_query.status_code == 422
    assert str(SAVED_SEARCH_QUERY_MAX_BYTES) in long_query.text


def test_duplicate_name_is_case_insensitive_within_a_household(saved_db) -> None:  # type: ignore[no-untyped-def]
    _, first, second = saved_db
    with TestClient(app) as client:
        _create(client, first, "Toothpaste", {"q": "toothpaste"})
        duplicate = client.post(
            "/v1/saved-searches",
            params={"household_id": first},
            json={"name": "toothpaste", "query": {"q": "other"}},
        )
        other_household = client.post(
            "/v1/saved-searches",
            params={"household_id": second},
            json={"name": "toothpaste", "query": {"q": "other"}},
        )

    assert duplicate.status_code == 409
    assert other_household.status_code == 201


def test_empty_household_renders_empty_items_not_an_error(saved_db) -> None:  # type: ignore[no-untyped-def]
    _, first, _ = saved_db
    with TestClient(app) as client:
        body = _list(client, first)

    assert body == {"items": []}


def test_delete_missing_saved_search_is_404(saved_db) -> None:  # type: ignore[no-untyped-def]
    _, first, _ = saved_db
    with TestClient(app) as client:
        response = client.delete(
            "/v1/saved-searches/does-not-exist", params={"household_id": first}
        )

    assert response.status_code == 404


def test_saved_search_migration_upgrade_downgrade_upgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)

    command.upgrade(config, "head")
    inspector = inspect(create_engine(url))
    assert "saved_search" in inspector.get_table_names()
    assert {ix["name"] for ix in inspector.get_indexes("saved_search")} >= {
        "ix_saved_search_household_id",
    }
    columns = {column["name"] for column in inspector.get_columns("saved_search")}
    assert {"id", "household_id", "name", "query_json", "created_at"}.issubset(columns)

    command.downgrade(config, "20260916_sg048_name_optional")
    assert "saved_search" not in inspect(create_engine(url)).get_table_names()

    command.upgrade(config, "head")
    assert "saved_search" in inspect(create_engine(url)).get_table_names()


def test_saved_search_row_carries_the_parsed_query_json(saved_db) -> None:  # type: ignore[no-untyped-def]
    """The stored column is real JSON text, and the API reads it back parsed."""
    session, first, _ = saved_db
    with TestClient(app) as client:
        created = _create(client, first, "Json check", {"asset_type": "appliance"})

    row = session.query(SavedSearch).filter_by(id=created["id"]).one()
    assert json.loads(row.query_json) == {"asset_type": "appliance"}
    assert created["query"] == {"asset_type": "appliance"}
