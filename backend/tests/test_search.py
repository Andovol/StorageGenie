from __future__ import annotations

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Asset, Household
from app.services.asset_service import create_asset
from app.services.evidence_service import store_evidence


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
