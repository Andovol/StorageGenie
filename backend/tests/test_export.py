from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from PIL import Image

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Asset, Evidence, Household, IdempotencyKey
from app.services.asset_service import create_asset
from app.services.evidence_service import store_evidence


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "source.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session: Session = session_factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = session_factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    household = Household(name="Export Test Household")
    session.add(household)
    session.commit()
    try:
        yield session, household.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def jpeg_bytes(color: str) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(output, format="JPEG")
    return output.getvalue()


def seed_export_data(session: Session, household_id: str) -> tuple[list[Asset], list[Evidence]]:
    evidence = [
        store_evidence(jpeg_bytes("red"), "red.jpg", "image/jpeg", household_id, session),
        store_evidence(jpeg_bytes("blue"), "blue.jpg", "image/jpeg", household_id, session),
    ]
    assets = [
        create_asset(
            session,
            household_id,
            {
                "display_name": "Red Tool",
                "asset_type": "tool",
                "evidence_ids": [evidence[0].id],
            },
        ),
        create_asset(
            session,
            household_id,
            {
                "display_name": "Blue Appliance",
                "asset_type": "appliance",
                "evidence_ids": [evidence[1].id],
            },
        ),
    ]
    return assets, evidence


def test_export_manifest_is_complete_and_downloadable(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = isolated_db
    assets, evidence = seed_export_data(session, household_id)

    with TestClient(app) as client:
        response = client.get("/v1/export", params={"household_id": household_id})

    assert response.status_code == 200
    body = response.json()
    assert {asset["id"] for asset in body["assets"]} == {asset.id for asset in assets}
    manifest = {item["id"]: item for item in body["evidence_manifest"]}
    assert set(manifest) == {item.id for item in evidence}
    for item in manifest.values():
        assert item["sha256"]
        assert item["storage_key"]
        assert item["size_bytes"] > 0
    assert body["assertions"]
    assert body["audit_events"]
    assert body["manifest_version"] == "1"
    assert body["db_revision"] == "0201cf10c56c"
    assert "attachment" in response.headers.get("content-disposition", "").lower()


def test_export_manifest_restores_into_a_fresh_database(isolated_db, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    source_session, household_id = isolated_db
    seed_export_data(source_session, household_id)
    with TestClient(app) as client:
        exported = client.get("/v1/export", params={"household_id": household_id})
    assert exported.status_code == 200
    manifest = exported.json()

    sink_path = tmp_path / "restored.db"
    assert sink_path != tmp_path / "source.db"
    sink_engine = create_engine(f"sqlite:///{sink_path}")
    Base.metadata.create_all(sink_engine)
    sink_factory = sessionmaker(bind=sink_engine, expire_on_commit=False)
    sink_session: Session = sink_factory()
    try:
        sink_session.add(Household(id=household_id, name="Restored Household"))
        for asset in manifest["assets"]:
            sink_session.add(
                Asset(
                    id=asset["id"],
                    household_id=household_id,
                    display_name=asset["display_name"],
                    asset_type=asset["asset_type"],
                    status=asset["status"],
                    version=asset["version"],
                )
            )
        for item in manifest["evidence_manifest"]:
            sink_session.add(
                Evidence(
                    id=item["id"],
                    household_id=household_id,
                    sha256=item["sha256"],
                    storage_key=item["storage_key"],
                    size_bytes=item["size_bytes"],
                    media_type="application/octet-stream",
                    original_filename=f"{item['id']}.bin",
                )
            )
        sink_session.commit()
        assert sink_session.query(Asset).count() == len(manifest["assets"])
        assert sink_session.query(Evidence).count() == len(manifest["evidence_manifest"])
        assert {row.id for row in sink_session.query(Asset).all()} == {
            row["id"] for row in manifest["assets"]
        }
        assert {row.id for row in sink_session.query(Evidence).all()} == {
            row["id"] for row in manifest["evidence_manifest"]
        }
    finally:
        sink_session.close()
        sink_engine.dispose()


@pytest.mark.parametrize("path", ["/v1/jobs", "/v1/review-tasks"])
def test_phase_zero_list_stubs_have_paginated_envelopes(isolated_db, path: str) -> None:  # type: ignore[no-untyped-def]
    _, household_id = isolated_db
    with TestClient(app) as client:
        response = client.get(path, params={"household_id": household_id})

    assert response.status_code == 200
    body = response.json()
    assert {"items", "next_cursor"}.issubset(body)
    assert body["items"] == []
    assert body["next_cursor"] is None


def test_asset_idempotency_is_persisted_and_reused(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = isolated_db
    payload = {"display_name": "Idempotent Asset", "asset_type": "tool"}
    key = "sg-008-idempotency-key"
    with TestClient(app) as client:
        first = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            headers={"Idempotency-Key": key},
            json=payload,
        )
        first_id = first.json()["id"]
        row = session.query(IdempotencyKey).filter_by(key=key).one()
        assert row.response_json is not None
        assert json.loads(row.response_json)["id"] == first_id
        second = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            headers={"Idempotency-Key": key},
            json=payload,
        )

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["id"] == first_id
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1
