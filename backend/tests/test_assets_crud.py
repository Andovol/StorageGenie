from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

import pytest

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-asset-tests-"))
TEST_STORAGE_ROOT = TEST_ROOT / "storage"
TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)

from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

@pytest.fixture
def db():  # type: ignore[no-untyped-def]
    from app.db import Base, SessionLocal, engine
    from app.models import Household

    Base.metadata.create_all(engine)
    session = SessionLocal()
    first = Household(name="Asset Test Household")
    second = Household(name="Other Asset Household")
    session.add_all([first, second])
    session.commit()
    try:
        yield session, first.id, second.id
    finally:
        session.close()


def jpeg_bytes(color: str) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(output, format="JPEG")
    return output.getvalue()


def evidence_for(session, household_id: str, color: str):  # type: ignore[no-untyped-def]
    from app.services.evidence_service import store_evidence

    return store_evidence(jpeg_bytes(color), f"{color}.jpg", "image/jpeg", household_id, session)


def post_asset(client: TestClient, household_id: str, **payload: object):
    return client.post("/v1/assets", params={"household_id": household_id}, json=payload)


def test_manual_create_idempotency_detail_scoping_and_archive(db) -> None:  # type: ignore[no-untyped-def]
    from app.main import app
    from app.models import Asset, AuditEvent

    session, household_id, other_household_id = db
    evidence = evidence_for(session, household_id, "red")
    other_evidence = evidence_for(session, other_household_id, "blue")
    payload = {
        "display_name": "Cordless Drill",
        "asset_type": "tool",
        "status": "ACTIVE",
        "quantity": 2,
        "unit": "pieces",
        "condition": "good",
        "evidence_ids": [evidence.id],
    }

    with TestClient(app) as client:
        first = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            headers={"Idempotency-Key": "asset-create-1"},
            json=payload,
        )
        assert first.status_code == 201
        asset_id = first.json()["id"]

        detail = client.get(
            f"/v1/assets/{asset_id}", params={"household_id": household_id}
        )
        assert detail.status_code == 200
        detail_body = detail.json()
        assert detail_body["evidence"] and detail_body["evidence"][0]["id"] == evidence.id
        accepted = {
            assertion["field_path"]: assertion
            for assertion in detail_body["assertions"]
            if assertion["review_state"] == "accepted"
        }
        expected_fields = {"display_name", "asset_type", "status", "quantity", "unit", "condition"}
        assert set(accepted) == expected_fields
        assert {field: accepted[field]["value"] for field in expected_fields} == {
            field: payload[field] for field in expected_fields
        }
        assert (
            session.query(AuditEvent)
            .filter_by(action="asset.create", entity_type="asset", entity_id=asset_id)
            .count()
            == 1
        )

        duplicate = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            headers={"Idempotency-Key": "asset-create-1"},
            json=payload,
        )
        assert duplicate.status_code == 201
        assert duplicate.json()["id"] == asset_id
        assert session.query(Asset).filter_by(household_id=household_id).count() == 1

        unknown = client.get(
            "/v1/assets/not-an-asset", params={"household_id": household_id}
        )
        assert unknown.status_code == 404

        cross_read = client.get(
            f"/v1/assets/{asset_id}", params={"household_id": other_household_id}
        )
        cross_patch = client.patch(
            f"/v1/assets/{asset_id}",
            params={"household_id": other_household_id},
            json={"display_name": "cross-household"},
        )
        cross_delete = client.delete(
            f"/v1/assets/{asset_id}", params={"household_id": other_household_id}
        )
        cross_attach = client.post(
            f"/v1/assets/{asset_id}/evidence",
            params={"household_id": other_household_id},
            json={"evidence_ids": [other_evidence.id]},
        )
        assert [response.status_code for response in (cross_read, cross_patch, cross_delete, cross_attach)] == [
            403,
            403,
            403,
            403,
        ]

        duplicate_attach = client.post(
            f"/v1/assets/{asset_id}/evidence",
            params={"household_id": household_id},
            json={"evidence_ids": [evidence.id]},
        )
        assert duplicate_attach.status_code == 200
        assert [item["id"] for item in duplicate_attach.json()["evidence"]].count(evidence.id) == 1

        archived = client.delete(
            f"/v1/assets/{asset_id}", params={"household_id": household_id}
        )
        assert archived.status_code == 200
        archived_detail = client.get(
            f"/v1/assets/{asset_id}", params={"household_id": household_id}
        )
        assert archived_detail.status_code == 200
        assert archived_detail.json()["status"] == "ARCHIVED"
        assert archived_detail.json()["version"] == 2
        assert (
            session.query(AuditEvent)
            .filter_by(action="asset.archive", entity_type="asset", entity_id=asset_id)
            .count()
            == 1
        )


def test_asset_cursor_pagination_and_mixed_filters(db) -> None:  # type: ignore[no-untyped-def]
    from app.main import app

    session, household_id, _ = db
    evidence = evidence_for(session, household_id, "green")
    fixtures = [
        ("Kitchen Blender", "appliance", "ACTIVE", True),
        ("Garden Chair", "furniture", "ACTIVE", False),
        ("Kitchen Table", "furniture", "ARCHIVED", True),
        ("Office Lamp", "appliance", "ARCHIVED", False),
        ("Garage Shelf", "storage", "ACTIVE", False),
    ]
    created: dict[str, dict[str, object]] = {}
    with TestClient(app) as client:
        for name, asset_type, status, has_evidence in fixtures:
            response = post_asset(
                client,
                household_id,
                display_name=name,
                asset_type=asset_type,
                status=status,
                **({"evidence_ids": [evidence.id]} if has_evidence else {}),
            )
            assert response.status_code == 201
            created[name] = response.json()

        assert len(created) > 2
        seen: list[str] = []
        cursor: str | None = None
        pages = 0
        while True:
            params: dict[str, object] = {"household_id": household_id, "limit": 2}
            if cursor is not None:
                params["cursor"] = cursor
            response = client.get("/v1/assets", params=params)
            assert response.status_code == 200
            body = response.json()
            page_ids = [item["id"] for item in body["items"]]
            assert page_ids
            assert len(page_ids) <= 2
            seen.extend(page_ids)
            pages += 1
            cursor = body["next_cursor"]
            if cursor is None:
                break
            assert pages < len(created)

        assert pages > 1
        assert len(seen) == len(set(seen))
        assert set(seen) == {item["id"] for item in created.values()}

        def filtered_ids(**params: object) -> set[str]:
            response = client.get(
                "/v1/assets", params={"household_id": household_id, "limit": 100, **params}
            )
            assert response.status_code == 200
            return {item["id"] for item in response.json()["items"]}

        expected_q = {created["Kitchen Blender"]["id"], created["Kitchen Table"]["id"]}
        expected_type = {created["Kitchen Blender"]["id"], created["Office Lamp"]["id"]}
        expected_status = {
            created["Kitchen Blender"]["id"],
            created["Garden Chair"]["id"],
            created["Garage Shelf"]["id"],
        }
        expected_evidence = {
            created["Kitchen Blender"]["id"],
            created["Kitchen Table"]["id"],
        }
        all_created_ids = {item["id"] for item in created.values()}
        assert expected_q and expected_q != all_created_ids
        assert expected_type and expected_type != all_created_ids
        assert expected_status and expected_status != all_created_ids
        assert expected_evidence and expected_evidence != all_created_ids
        assert filtered_ids(q="Kitchen") == expected_q
        assert filtered_ids(asset_type="appliance") == expected_type
        assert filtered_ids(status="ACTIVE") == expected_status
        assert filtered_ids(has_evidence=True) == expected_evidence
        assert filtered_ids(has_evidence=False) == all_created_ids - expected_evidence
