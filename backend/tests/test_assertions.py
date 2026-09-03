from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

import pytest

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-assertion-tests-"))
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
    first = Household(name="Assertion Test Household")
    second = Household(name="Other Assertion Household")
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


def test_patch_supersedes_assertion_stale_match_and_attaches_evidence(db) -> None:  # type: ignore[no-untyped-def]
    from app.main import app
    from app.models import Assertion, AuditEvent

    session, household_id, other_household_id = db
    additional = evidence_for(session, household_id, "yellow")
    cross_household = evidence_for(session, other_household_id, "purple")
    with TestClient(app) as client:
        created = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            json={"display_name": "Original Name", "asset_type": "tool"},
        )
        assert created.status_code == 201
        asset_id = created.json()["id"]
        before = client.get(
            f"/v1/assets/{asset_id}", params={"household_id": household_id}
        ).json()
        original = next(item for item in before["assertions"] if item["field_path"] == "display_name")
        assert original["review_state"] == "accepted"
        assert before["version"] == 1

        updated = client.patch(
            f"/v1/assets/{asset_id}",
            params={"household_id": household_id},
            headers={"If-Match": "1"},
            json={"display_name": "Renamed Asset"},
        )
        assert updated.status_code == 200
        assert updated.json()["version"] == 2

        detail = client.get(
            f"/v1/assets/{asset_id}", params={"household_id": household_id}
        ).json()
        display_assertions = [
            item for item in detail["assertions"] if item["field_path"] == "display_name"
        ]
        updated_display = next(
            item
            for item in updated.json()["assertions"]
            if item["field_path"] == "display_name" and item["review_state"] == "accepted"
        )
        assert {item["id"] for item in display_assertions} == {original["id"], updated_display["id"]}
        assert {(item["value"], item["review_state"]) for item in display_assertions} == {
            ("Original Name", "superseded"),
            ("Renamed Asset", "accepted"),
        }
        assert (
            session.query(AuditEvent)
            .filter_by(action="assertion.upsert", entity_type="assertion")
            .filter(AuditEvent.entity_id.in_([item["id"] for item in display_assertions]))
            .count()
            == 1
        )

        snapshot = {
            "version": detail["version"],
            "display_name": detail["display_name"],
            "assertions": detail["assertions"],
        }
        stale = client.patch(
            f"/v1/assets/{asset_id}",
            params={"household_id": household_id},
            headers={"If-Match": "1"},
            json={"display_name": "Must Not Apply"},
        )
        assert stale.status_code == 409
        after_stale = client.get(
            f"/v1/assets/{asset_id}", params={"household_id": household_id}
        ).json()
        assert {
            "version": after_stale["version"],
            "display_name": after_stale["display_name"],
            "assertions": after_stale["assertions"],
        } == snapshot

        attached = client.post(
            f"/v1/assets/{asset_id}/evidence",
            params={"household_id": household_id},
            json={"evidence_ids": [additional.id]},
        )
        assert attached.status_code == 200
        assert {item["id"] for item in attached.json()["evidence"]} == {additional.id}

        unknown_evidence = client.post(
            f"/v1/assets/{asset_id}/evidence",
            params={"household_id": household_id},
            json={"evidence_ids": ["not-an-evidence-id"]},
        )
        assert unknown_evidence.status_code == 404
        cross_evidence = client.post(
            f"/v1/assets/{asset_id}/evidence",
            params={"household_id": household_id},
            json={"evidence_ids": [cross_household.id]},
        )
        assert cross_evidence.status_code == 403
        assert session.query(Assertion).filter_by(asset_id=asset_id).count() == 4
