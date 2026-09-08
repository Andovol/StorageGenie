from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, Evidence, Household, ReviewTask
from app.plugins.expiry_tracker import EXPIRY_FIELD
from app.plugins.registry import PluginError, get_plugin


@pytest.fixture
def plugin_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'plugin.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Expiry Plugin Household")
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


def make_asset(session: Session, household_id: str, name: str = "Test item", asset_type: str = "product") -> Asset:
    asset = Asset(household_id=household_id, display_name=name, asset_type=asset_type, status="ACTIVE")
    session.add(asset)
    session.commit()
    return asset


def classify(client: TestClient, asset_id: str, household_id: str, category: str) -> object:
    return client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": category},
    )


def test_registry_rejects_unknown_and_version_mismatch() -> None:
    assert get_plugin("expiry-tracker", "1.0.0").plugin_id == "expiry-tracker"
    with pytest.raises(PluginError, match="Unknown plugin id"):
        get_plugin("missing-plugin", "1.0.0")
    with pytest.raises(PluginError, match="version mismatch"):
        get_plugin("expiry-tracker", "2.0.0")


def test_classification_profiles_round_trip_and_inactive_phase(plugin_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = plugin_db
    food = make_asset(session, household_id, "Canned beans")
    medicine = make_asset(session, household_id, "Medicine")
    with TestClient(app) as client:
        food_response = classify(client, food.id, household_id, "Food & beverages")
        medicine_response = classify(client, medicine.id, household_id, "Medicine/pharma")
        readback = client.get(
            f"/v1/plugins/expiry-tracker/assets/{food.id}/classification",
            params={"household_id": household_id},
        )
        inactive = [
            classify(client, food.id, household_id, category)
            for category in ("Cosmetics/personal care", "Household chemicals", "Documents/other")
        ]
    assert food_response.status_code == 200
    assert food_response.json()["classification"]["profile"]["tier_defaults"] == {
        "critical": 1,
        "urgent": 7,
        "upcoming": 30,
    }
    assert medicine_response.status_code == 200
    assert medicine_response.json()["classification"]["profile"]["tier_defaults"] == {
        "critical": 1,
        "urgent": 3,
        "upcoming": 14,
    }
    assert readback.status_code == 200
    assert readback.json()["classification"]["category"] == "food_beverages"
    stored = session.query(Assertion).filter_by(asset_id=food.id, field_path="plugin:expiry-tracker/classification").one()
    assert json.loads(stored.value_json)["category"] == readback.json()["classification"]["category"]
    assert all(response.status_code == 422 and "Phase 3" in response.json()["detail"] for response in inactive)


def test_plugin_and_extension_validation_rejects_all_core_overrides(plugin_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = plugin_db
    asset = make_asset(session, household_id)
    with TestClient(app) as client:
        unknown = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/classification",
            params={"household_id": household_id},
            json={"plugin_id": "unknown", "version": "1.0.0", "category": "food"},
        )
        mismatch = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/classification",
            params={"household_id": household_id},
            json={"plugin_id": "expiry-tracker", "version": "9.0.0", "category": "food"},
        )
        bad_schema = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/extensions",
            params={"household_id": household_id},
            json={"attributes": {"notification_tier": "made-up"}},
        )
        valid = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/extensions",
            params={"household_id": household_id},
            json={"attributes": {"storage_location": "pantry", "unit": "piece", "quantity": 2}},
        )
        readback = client.get(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/extensions",
            params={"household_id": household_id},
        )
        core_responses = [
            client.post(
                f"/v1/plugins/expiry-tracker/assets/{asset.id}/extensions",
                params={"household_id": household_id},
                json={"attributes": {field: "attempt"}},
            )
            for field in ("identifier", "condition", "location", "status")
        ]
    assert unknown.status_code == 422 and "Unknown plugin id" in unknown.json()["detail"]
    assert mismatch.status_code == 422 and "version mismatch" in mismatch.json()["detail"]
    assert bad_schema.status_code == 422 and "notification_tier" in bad_schema.json()["detail"]
    assert valid.status_code == 200
    assert readback.status_code == 200
    assert readback.json()["attributes"] == {"quantity": 2, "storage_location": "pantry", "unit": "piece"}
    assert all(response.status_code == 422 for response in core_responses)
    assert all(field in response.json()["detail"] for field, response in zip(("identifier", "condition", "location", "status"), core_responses))


def test_dateless_import_requires_manual_entry_and_reads_back(plugin_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = plugin_db
    asset = make_asset(session, household_id, "Canned beans")
    evidence = Evidence(
        household_id=household_id,
        sha256="e" * 64,
        storage_key="plugin/source.png",
        media_type="image/png",
        original_filename="source.png",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(evidence)
    session.commit()
    with TestClient(app) as client:
        classified = classify(client, asset.id, household_id, "food")
        pre_entry = client.get(f"/v1/assets/{asset.id}", params={"household_id": household_id})
        tasks = client.get("/v1/review-tasks", params={"household_id": household_id})
        entered = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/expiry",
            params={"household_id": household_id},
            json={
                "expiry_date": "2030-05-06",
                "date_type": "best_before",
                "unit": "piece",
                "source_evidence_ids": [evidence.id],
            },
        )
        post_entry = client.get(f"/v1/assets/{asset.id}", params={"household_id": household_id})
    assert classified.status_code == 200
    assert classified.json()["expiry_assertion"]["review_state"] == "needs_evidence"
    expiry_before = [row for row in pre_entry.json()["assertions"] if row["field_path"] == EXPIRY_FIELD and row["review_state"] == "accepted"]
    assert expiry_before == []
    assert tasks.status_code == 200
    assert any(item["task_type"] == "expiry.manual_entry" and item["status"] == "open" for item in tasks.json()["items"])
    assert entered.status_code == 200
    assert entered.json()["assertion"]["source_type"] == "user"
    assert entered.json()["assertion"]["review_state"] == "accepted"
    assert entered.json()["assertion"]["value"]["expiry_date"] == "2030-05-06"
    assert entered.json()["assertion"]["source_evidence_ids"] == [evidence.id]
    resolved = [row for row in post_entry.json()["assertions"] if row["field_path"] == EXPIRY_FIELD and row["review_state"] == "accepted"]
    assert len(resolved) == 1 and resolved[0]["value"]["date_type"] == "best_before"
    assert session.query(ReviewTask).filter_by(task_type="expiry.manual_entry", status="resolved").count() == 1


def test_manual_expiry_enforces_date_type_and_unit_enums(plugin_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = plugin_db
    asset = make_asset(session, household_id, "Canned beans")
    with TestClient(app) as client:
        assert classify(client, asset.id, household_id, "food").status_code == 200
        bad_date_type = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/expiry",
            params={"household_id": household_id},
            json={"expiry_date": "2030-05-06", "date_type": "invented"},
        )
        bad_unit = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/expiry",
            params={"household_id": household_id},
            json={"expiry_date": "2030-05-06", "unit": "box"},
        )
    assert bad_date_type.status_code == 422 and "date_type" in bad_date_type.json()["detail"]
    assert bad_unit.status_code == 422 and "unit" in bad_unit.json()["detail"]


def test_non_perishable_has_no_expiry_and_manual_entry_is_rejected(plugin_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = plugin_db
    asset = make_asset(session, household_id, "Cordless drill", "tool")
    with TestClient(app) as client:
        classified = classify(client, asset.id, household_id, "non-perishable")
        entered = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/expiry",
            params={"household_id": household_id},
            json={"expiry_date": "2030-05-06"},
        )
        detail = client.get(f"/v1/assets/{asset.id}", params={"household_id": household_id})
    assert classified.status_code == 200
    assert classified.json()["expiry_assertion"] is None
    assert entered.status_code == 422 and "non-perishable" in entered.json()["detail"]
    assert not any(row["field_path"] == EXPIRY_FIELD for row in detail.json()["assertions"])
