"""SG-187 G2: failing uploads leave no orphan bytes and speak plainly.

The failing baseline is the SG-180 G1.7b probe: an upload against a
non-existent household wrote the original before the Evidence row's FK
rejection and returned the raw SQL constraint text. These tests drive the real
route on disposable SQLite + storage with foreign keys enforced (the
application's own pragma), assert the rejection is readable, and assert the
storage tree is unchanged. The oversize 413 and media-mismatch 422 controls
prove the cap semantics are preserved.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import Base, _set_sqlite_pragma, get_db
from app.main import app
from app.models import Evidence, Household


@pytest.fixture
def db(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    database_url = f"sqlite:///{tmp_path / 'sg187-rejections.db'}"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    # Reuse the application's own SQLite pragma setup (FK enforcement included).
    event.listen(engine, "connect", _set_sqlite_pragma)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(settings, "storage_root", str(storage_root))

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    session = factory()
    household = Household(name="SG-187 Rejection Household")
    session.add(household)
    session.commit()
    try:
        yield session, household.id, storage_root
    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def jpeg_bytes(color: str = "brown") -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (64, 48), color).save(output, format="JPEG")
    return output.getvalue()


def stored_files(storage_root: Path) -> set[Path]:
    return {path for path in storage_root.rglob("*") if path.is_file()}


def test_unknown_household_upload_leaves_no_orphan_and_speaks_plainly(db) -> None:  # type: ignore[no-untyped-def]
    session, _, storage_root = db
    image_bytes = jpeg_bytes()
    sha = hashlib.sha256(image_bytes).hexdigest()
    before = stored_files(storage_root)

    with TestClient(app) as client:
        response = client.post(
            "/v1/evidence",
            params={"household_id": "sg187-no-such-household"},
            files={"file": ("orphan.jpg", image_bytes, "image/jpeg")},
        )

    after = stored_files(storage_root)
    detail = response.json()["detail"]
    assert response.status_code == 422
    assert "FOREIGN KEY" not in detail
    assert "sqlalchemy" not in detail.lower()
    assert "INSERT" not in detail
    assert after == before
    assert not (storage_root / "sg187-no-such-household" / sha[:2] / f"{sha}.jpg").exists()
    assert session.query(Evidence).filter_by(sha256=sha).count() == 0


def test_oversize_413_and_mismatch_422_leave_no_files(db, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, storage_root = db
    before = stored_files(storage_root)
    monkeypatch.setattr(settings, "max_upload_bytes", 32)
    with TestClient(app) as client:
        oversize = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("large.bin", b"x" * 33, "application/octet-stream")},
        )
    assert oversize.status_code == 413
    assert "max_upload_bytes" in oversize.json()["detail"]

    monkeypatch.setattr(settings, "max_upload_bytes", 20 * 1024 * 1024)
    mismatch_bytes = jpeg_bytes("purple")
    with TestClient(app) as client:
        mismatch = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("mismatch.jpg", mismatch_bytes, "image/png")},
        )
    assert mismatch.status_code == 422
    assert "media_type_mismatch" in mismatch.json()["detail"]
    assert stored_files(storage_root) == before
    assert session.query(Evidence).count() == 0
