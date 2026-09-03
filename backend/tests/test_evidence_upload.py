import hashlib
import io
import os
import struct
import tempfile
import zlib
from pathlib import Path

import pytest

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-evidence-tests-"))
TEST_STORAGE_ROOT = TEST_ROOT / "storage"
TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)

from fastapi.testclient import TestClient  # noqa: E402
from PIL import ExifTags, Image  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import AuditEvent, Evidence, Household  # noqa: E402
import app.services.evidence_service as evidence_service  # noqa: E402
from app.services.evidence_service import store_evidence  # noqa: E402
from app.storage.local_store import thumbnail_path  # noqa: E402

Base.metadata.create_all(engine)


@pytest.fixture
def db():  # type: ignore[no-untyped-def]
    session = SessionLocal()
    household = Household(name="Evidence Test Household")
    session.add(household)
    session.commit()
    try:
        yield session, household.id
    finally:
        session.close()


def jpeg_bytes(color: str = "red", with_gps: bool = False) -> bytes:
    image = Image.new("RGB", (640, 480), color)
    output = io.BytesIO()
    if with_gps:
        exif = Image.Exif()
        exif[0x0112] = 6
        exif[0x010E] = "test metadata"
        exif[0x8825] = {1: "N", 2: (40.0, 0.0, 0.0), 3: "W", 4: (74.0, 0.0, 0.0)}
        image.save(output, format="JPEG", exif=exif.tobytes())
    else:
        image.save(output, format="JPEG")
    return output.getvalue()


def small_png_with_dimensions(width: int, height: int) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (1, 1), "red").save(output, format="PNG")
    data = bytearray(output.getvalue())
    struct.pack_into(">II", data, 16, width, height)
    struct.pack_into(">I", data, 29, zlib.crc32(data[12:29]) & 0xFFFFFFFF)
    return bytes(data)


def test_store_is_idempotent_audited_and_writes_thumbnail(db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = db
    first_bytes = jpeg_bytes()
    first = store_evidence(first_bytes, "first.jpg", "image/jpeg", household_id, session)
    duplicate = store_evidence(first_bytes, "different-name.jpg", "image/jpeg", household_id, session)
    different = store_evidence(jpeg_bytes("blue"), "different.jpg", "image/jpeg", household_id, session)

    assert duplicate.id == first.id
    assert duplicate.sha256 == first.sha256 == hashlib.sha256(first_bytes).hexdigest()
    assert duplicate.storage_key == first.storage_key
    assert different.id != first.id
    assert different.sha256 != first.sha256
    assert different.storage_key != first.storage_key

    audit_rows = session.query(AuditEvent).filter_by(action="evidence.create", household_id=household_id).all()
    assert len(audit_rows) == 2
    assert {row.entity_id for row in audit_rows} == {first.id, different.id}

    original = TEST_STORAGE_ROOT / first.storage_key
    original_hash_before = hashlib.sha256(original.read_bytes()).hexdigest()
    thumbnail = thumbnail_path(first.storage_key, settings.thumbnail_sizes[0])
    assert original.exists()
    assert thumbnail.exists()
    assert original_hash_before == first.sha256
    assert hashlib.sha256(original.read_bytes()).hexdigest() == original_hash_before


def test_thumbnail_has_no_exif_or_gps_and_original_is_immutable(db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = db
    original_bytes = jpeg_bytes(with_gps=True)
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    evidence = store_evidence(original_bytes, "gps.jpg", "image/jpeg", household_id, session)

    original = TEST_STORAGE_ROOT / evidence.storage_key
    thumbnail = thumbnail_path(evidence.storage_key, settings.thumbnail_sizes[0])
    with Image.open(thumbnail) as derived:
        exif = derived.getexif()
        gps_tag = ExifTags.Base.GPSInfo
        assert len(exif) == 0
        assert gps_tag not in exif
        assert not exif.get_ifd(gps_tag)
    assert hashlib.sha256(original.read_bytes()).hexdigest() == original_hash


def test_thumbnail_failure_is_logged_with_sha_and_size(db, monkeypatch, caplog) -> None:  # type: ignore[no-untyped-def]
    session, household_id = db

    def fail_thumbnail(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("thumbnail encoder failed")

    monkeypatch.setattr(evidence_service, "_thumbnail_bytes", fail_thumbnail)
    original_bytes = jpeg_bytes("orange")
    sha = hashlib.sha256(original_bytes).hexdigest()
    evidence = store_evidence(original_bytes, "failed-thumb.jpg", "image/jpeg", household_id, session)

    assert evidence.sha256 == sha
    assert f"Thumbnail generation failed sha={sha} size={settings.thumbnail_sizes[0]}" in caplog.text


@pytest.mark.parametrize(
    ("configured_limit", "width", "height"),
    [(1000, 5000, 5000), (None, 10000, 10000)],
)
def test_bomb_is_rejected_before_any_storage_or_row(  # type: ignore[no-untyped-def]
    db, monkeypatch, caplog, configured_limit, width, height
) -> None:
    session, household_id = db
    image_bytes = small_png_with_dimensions(width, height)
    sha = hashlib.sha256(image_bytes).hexdigest()
    monkeypatch.setattr(settings, "max_image_pixels", configured_limit)

    with TestClient(app) as client:
        response = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("bomb.png", image_bytes, "image/png")},
        )

    assert response.status_code == 422
    assert "decompression_bomb" in response.json()["detail"]
    assert "max_image_pixels" in response.json()["detail"]
    assert sha in caplog.text
    assert f"{width}x{height}" in caplog.text
    assert session.query(Evidence).filter_by(sha256=sha).count() == 0
    assert not (TEST_STORAGE_ROOT / household_id / sha[:2]).exists()
    assert not list(TEST_STORAGE_ROOT.rglob("*.tmp"))


def test_endpoint_duplicate_returns_same_id(db) -> None:  # type: ignore[no-untyped-def]
    _, household_id = db
    image_bytes = jpeg_bytes("green")
    with TestClient(app) as client:
        first = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("upload.jpg", image_bytes, "image/jpeg")},
        )
        duplicate = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("renamed.jpg", image_bytes, "image/jpeg")},
        )

    assert first.status_code == 201
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == first.json()["id"]


def test_endpoint_oversize_reject_names_configured_limit(db, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _, household_id = db
    monkeypatch.setattr(settings, "max_upload_bytes", 32)
    with TestClient(app) as client:
        response = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("large.bin", b"x" * 33, "application/octet-stream")},
        )

    assert response.status_code == 413
    assert "max_upload_bytes" in response.json()["detail"]
    assert "32" in response.json()["detail"]


def test_endpoint_rejects_claimed_signature_mismatch(db) -> None:  # type: ignore[no-untyped-def]
    _, household_id = db
    image_bytes = jpeg_bytes("purple")
    with TestClient(app) as client:
        response = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("mismatch.jpg", image_bytes, "image/png")},
        )

    assert response.status_code == 422
    assert "media_type_mismatch" in response.json()["detail"]
