"""SG-273: the Pantry view — ACTIVE food only, Use soon from the engine window.

Every gate runs in-process on a temp SQLite database; no live database read or
write, no key, no network, no spend. Fixtures follow `test_sg272_flow.py`.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Household


@pytest.fixture
def pantry_db(tmp_path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg273.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-273 Household")
    session.add(household)
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
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


def _create(client: TestClient, household_id: str, **fields: object) -> dict:  # type: ignore[type-arg]
    payload = {"display_name": "Milk", "asset_type": "product", **fields}
    response = client.post("/v1/assets", params={"household_id": household_id}, json=payload)
    assert response.status_code == 201, response.text
    return response.json()  # type: ignore[no-any-return]


def _classify(client: TestClient, asset_id: str, household_id: str, category: str = "food_beverages") -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": category},
    )
    assert response.status_code == 200, response.text


def _enter_expiry(client: TestClient, asset_id: str, household_id: str, expiry: str) -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
        params={"household_id": household_id},
        json={"expiry_date": expiry, "date_type": "expiry_date"},
    )
    assert response.status_code == 200, response.text


def _pantry_ids(client: TestClient, household_id: str) -> list[str]:
    response = client.get(
        "/v1/assets",
        params={"household_id": household_id, "category": "food_beverages", "limit": 100},
    )
    assert response.status_code == 200, response.text
    return sorted(row["id"] for row in response.json()["items"] if row["status"] == "ACTIVE")


def _use_soon_ids(client: TestClient, household_id: str) -> list[str]:
    status = client.get(
        "/v1/plugins/expiry-tracker/status",
        params={"household_id": household_id, "category": "food_beverages"},
    )
    assert status.status_code == 200, status.text
    rows = status.json()["rows"]
    return sorted(
        row["asset_id"] for row in rows if row["bucket"] in ("expired", "this-week")
    )


def test_only_active_food_listed_gone_leaves_and_returns(pantry_db) -> None:  # type: ignore[no-untyped-def]
    _, household_id = pantry_db
    with TestClient(app) as client:
        food = _create(client, household_id, display_name="Milk", quantity=2, unit="pcs")
        food_id = str(food["id"])
        _classify(client, food_id, household_id, "food_beverages")
        _enter_expiry(client, food_id, household_id, (date.today() + timedelta(days=5)).isoformat())

        non_food = _create(client, household_id, display_name="Wrench")
        non_food_id = str(non_food["id"])
        _classify(client, non_food_id, household_id, "household_chemicals")

        unsorted = _create(client, household_id, display_name="Mystery")
        unsorted_id = str(unsorted["id"])

        assert food_id in _pantry_ids(client, household_id)
        assert non_food_id not in _pantry_ids(client, household_id)
        assert unsorted_id not in _pantry_ids(client, household_id)

        summary = client.get("/v1/analytics/summary", params={"household_id": household_id}).json()
        assert summary["categories"]["uncategorized"] >= 1

        gone = client.post(
            f"/v1/assets/{food_id}/gone",
            params={"household_id": household_id},
            json={"reason": "used_up"},
        )
        assert gone.status_code == 200, gone.text
        assert food_id not in _pantry_ids(client, household_id)
        gone_view = client.get(
            "/v1/assets", params={"household_id": household_id, "status": "ARCHIVED", "limit": 100}
        ).json()
        assert food_id in [row["id"] for row in gone_view["items"]]

        back = client.post(f"/v1/assets/{food_id}/put-back", params={"household_id": household_id})
        assert back.status_code == 200, back.text
        assert food_id in _pantry_ids(client, household_id)


def test_use_soon_matches_engine_window_both_sides_of_edge(pantry_db) -> None:  # type: ignore[no-untyped-def]
    _, household_id = pantry_db
    with TestClient(app) as client:
        expired = _create(client, household_id, display_name="Old Milk")
        expired_id = str(expired["id"])
        _classify(client, expired_id, household_id)
        _enter_expiry(client, expired_id, household_id, (date.today() - timedelta(days=1)).isoformat())

        edge_in = _create(client, household_id, display_name="Edge In")
        edge_in_id = str(edge_in["id"])
        _classify(client, edge_in_id, household_id)
        _enter_expiry(client, edge_in_id, household_id, (date.today() + timedelta(days=7)).isoformat())

        edge_out = _create(client, household_id, display_name="Edge Out")
        edge_out_id = str(edge_out["id"])
        _classify(client, edge_out_id, household_id)
        _enter_expiry(client, edge_out_id, household_id, (date.today() + timedelta(days=8)).isoformat())

        soon = _use_soon_ids(client, household_id)
        assert expired_id in soon
        assert edge_in_id in soon
        assert edge_out_id not in soon
        assert sorted(soon) == sorted([i for i in soon if i in (expired_id, edge_in_id)])


def test_tile_actions_hit_existing_routes(pantry_db) -> None:  # type: ignore[no-untyped-def]
    _, household_id = pantry_db
    with TestClient(app) as client:
        asset = _create(client, household_id, display_name="Beans", quantity=2, unit="pcs")
        asset_id = str(asset["id"])
        _classify(client, asset_id, household_id)
        _enter_expiry(client, asset_id, household_id, (date.today() + timedelta(days=5)).isoformat())

        dec = client.post(f"/v1/assets/{asset_id}/quantity/decrement", params={"household_id": household_id})
        assert dec.status_code == 200, dec.text
        assert dec.json()["quantity"] == 1.0

        gone = client.post(
            f"/v1/assets/{asset_id}/gone",
            params={"household_id": household_id},
            json={"reason": "used_up"},
        )
        assert gone.status_code == 200, gone.text
        assert gone.json()["gone_reason"] == "used_up"
        assert asset_id not in _pantry_ids(client, household_id)


def test_journey_hand_classify_pantry_minus_use_up_gone(pantry_db) -> None:  # type: ignore[no-untyped-def]
    _, household_id = pantry_db
    with TestClient(app) as client:
        asset = _create(client, household_id, display_name="Hand Rice", quantity=2, unit="pcs")
        asset_id = str(asset["id"])
        assert asset_id not in _pantry_ids(client, household_id)

        _classify(client, asset_id, household_id, "food_beverages")
        assert asset_id in _pantry_ids(client, household_id)

        dec = client.post(f"/v1/assets/{asset_id}/quantity/decrement", params={"household_id": household_id})
        assert dec.status_code == 200, dec.text
        assert dec.json()["quantity"] == 1.0

        gone = client.post(
            f"/v1/assets/{asset_id}/gone",
            params={"household_id": household_id},
            json={"reason": "used_up"},
        )
        assert gone.status_code == 200, gone.text
        assert asset_id not in _pantry_ids(client, household_id)
        gone_view = client.get(
            "/v1/assets", params={"household_id": household_id, "status": "ARCHIVED", "limit": 100}
        ).json()
        assert asset_id in [row["id"] for row in gone_view["items"]]
