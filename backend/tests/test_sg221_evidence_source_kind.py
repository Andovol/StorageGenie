"""SG-221 G1 — the asset detail serializer says what kind each evidence row is.

The drawer can only tell a context-scene render from a source photo when the
asset route carries `Evidence.source_kind`. This test reads the real route
(`GET /v1/assets/{id}`) against an isolated SQLite database: the linked scene
render must serialize `source_kind="scene_render"` and the linked upload must
serialize `source_kind="upload"`. On the pre-slice serializer both keys are
absent, so this file fails before the additive key and passes after it.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  (registers every table for create_all)
from app.api.v1.assets import router as assets_router
from app.db import Base, get_db
from app.models import Asset, Evidence, Household, asset_evidence

HOUSEHOLD_ID = "hhhhhhhh-2211-4221-8221-hhhhhhhhhhhh"
ASSET_ID = "asset-sg221"
PHOTO_EVIDENCE_ID = "ev-photo-sg221"
SCENE_EVIDENCE_ID = "ev-scene-sg221"


def test_asset_detail_serializes_evidence_source_kind(tmp_path: Path) -> None:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg221.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    session: Session = sessionmaker(bind=engine)()
    session.add(Household(id=HOUSEHOLD_ID, name="SG-221 Household"))
    session.add(
        Asset(
            id=ASSET_ID,
            household_id=HOUSEHOLD_ID,
            display_name="Linked asset",
            asset_type="food",
        )
    )
    session.add_all(
        [
            Evidence(
                id=PHOTO_EVIDENCE_ID,
                household_id=HOUSEHOLD_ID,
                sha256="a" * 64,
                media_type="image/png",
                storage_key=f"{HOUSEHOLD_ID}/source.png",
                original_filename="source.png",
                source_kind="upload",
                size_bytes=10,
            ),
            Evidence(
                id=SCENE_EVIDENCE_ID,
                household_id=HOUSEHOLD_ID,
                sha256="b" * 64,
                media_type="image/jpeg",
                storage_key=f"{HOUSEHOLD_ID}/scene.jpg",
                original_filename="scene-render.jpg",
                source_kind="scene_render",
                size_bytes=20,
            ),
        ]
    )
    session.execute(
        asset_evidence.insert(),
        [
            {"asset_id": ASSET_ID, "evidence_id": PHOTO_EVIDENCE_ID},
            {"asset_id": ASSET_ID, "evidence_id": SCENE_EVIDENCE_ID},
        ],
    )
    session.commit()

    app = FastAPI()
    app.include_router(assets_router, prefix="/v1")
    app.dependency_overrides[get_db] = lambda: session
    try:
        response = TestClient(app).get(
            f"/v1/assets/{ASSET_ID}", params={"household_id": HOUSEHOLD_ID}
        )
    finally:
        session.close()

    assert response.status_code == 200
    evidence = {row["id"]: row for row in response.json()["evidence"]}
    assert set(evidence) == {PHOTO_EVIDENCE_ID, SCENE_EVIDENCE_ID}
    assert evidence[SCENE_EVIDENCE_ID]["source_kind"] == "scene_render"
    assert evidence[PHOTO_EVIDENCE_ID]["source_kind"] == "upload"
