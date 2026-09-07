from __future__ import annotations

import io
from datetime import timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import AuditEvent, Household


def jpeg_bytes() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (32, 32), "orange").save(output, format="JPEG")
    return output.getvalue()


@pytest.fixture
def phase0_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "phase0.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    test_engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(test_engine)
    session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session: Session = session_factory()
    household = Household(name="Phase 0 E2E Household")
    session.add(household)
    session.commit()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = session_factory()
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
        test_engine.dispose()


def test_phase0_exit_condition(phase0_fixture) -> None:  # type: ignore[no-untyped-def]
    session, household_id = phase0_fixture
    display_name = "Orange Workshop Drill"

    with TestClient(app) as client:
        created = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            json={
                "display_name": display_name,
                "asset_type": "tool",
                "status": "ACTIVE",
                "quantity": 1,
                "unit": "piece",
                "condition": "good",
            },
        )
        assert created.status_code == 201
        asset_id = created.json()["id"]
        assert asset_id

        uploaded = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("orange-drill.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert uploaded.status_code == 201
        evidence_id = uploaded.json()["id"]
        assert evidence_id

        attached = client.post(
            f"/v1/assets/{asset_id}/evidence",
            params={"household_id": household_id},
            json={"evidence_ids": [evidence_id]},
        )
        assert attached.status_code == 200
        assert [item["id"] for item in attached.json()["evidence"]] == [evidence_id]

        searched = client.get(
            "/v1/assets",
            params={"household_id": household_id, "q": display_name},
        )
        assert searched.status_code == 200
        assert [item["id"] for item in searched.json()["items"]] == [asset_id]

        exported = client.get("/v1/export", params={"household_id": household_id})
        assert exported.status_code == 200
        manifest = exported.json()
        assert {item["id"] for item in manifest["assets"]} == {asset_id}
        assert {item["id"] for item in manifest["evidence_manifest"]} == {evidence_id}

        detail = client.get(
            f"/v1/assets/{asset_id}", params={"household_id": household_id}
        )
        assert detail.status_code == 200
        detail_body = detail.json()
        assert [item["id"] for item in detail_body["evidence"]] == [evidence_id]
        display_assertion = next(
            assertion
            for assertion in detail_body["assertions"]
            if assertion["field_path"] == "display_name"
        )
        assert display_assertion["value"] == display_name
        assert display_assertion["source_type"] == "user"
        assert display_assertion["review_state"] == "accepted"

    audit_rows = (
        session.query(AuditEvent)
        .filter_by(entity_type="asset", entity_id=asset_id)
        .order_by(AuditEvent.timestamp, AuditEvent.id)
        .all()
    )
    created_events = [row for row in audit_rows if row.action == "asset.create"]
    accepted_events = [row for row in audit_rows if row.action == "asset.accepted"]
    assert len(created_events) == 1
    assert len(accepted_events) == 1
    created_at = created_events[0].timestamp
    accepted_at = accepted_events[0].timestamp
    assert created_at is not None
    assert accepted_at is not None
    audit_timestamps = [row.timestamp for row in audit_rows]
    assert all(timestamp is not None for timestamp in audit_timestamps)
    assert audit_timestamps == sorted(audit_timestamps)
    assert audit_rows.index(created_events[0]) < audit_rows.index(accepted_events[0])
    duration = accepted_at - created_at
    assert accepted_at >= created_at
    assert duration >= timedelta(0)
