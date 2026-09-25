"""SG-130: legacy PNG thumbnail backfill, proven on fixtures through the real writer.

$0, offline: real Pillow PNG fixtures, real storage, real routes; no provider
call, no network, no metered path.

What this file proves (`PG-EV-09` fail-then-pass, `PG-SC-12` no re-implemented
resizer):
- the backfill helper loads from `backend/scripts/backfill_legacy_png_thumbs.py`
  and writes one `.jpg` artifact per configured `settings.thumbnail_sizes` using
  the production writer (`_decode_image` + `_thumbnail_bytes`), with `ffd8ff`
  JPEG magic at every size;
- a second run is idempotent (skips; no artifact changed) and `--overwrite`
  reuses the same atomic path to replace a stale artifact;
- the artifact the helper writes on disk is the one the real thumb route serves:
  200 `image/jpeg` with `ffd8ff` magic (writer path == reader path).
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
from pathlib import Path
from types import ModuleType

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Evidence, Household

BACKEND_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = BACKEND_DIR / "scripts" / "backfill_legacy_png_thumbs.py"


def _load_backfill() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sg130_backfill_png_thumbs", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BACKFILL = _load_backfill()


def _png_bytes(mode: str = "RGB", size: tuple[int, int] = (800, 600)) -> bytes:
    color = "teal" if mode == "RGB" else (0, 128, 128, 128)
    buffer = io.BytesIO()
    Image.new(mode, size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def _write_png(root: Path, payload: bytes, household: str = "household") -> str:
    sha = hashlib.sha256(payload).hexdigest()
    rel = f"{household}/{sha[:2]}/{sha}.png"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return rel


@pytest.fixture
def storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "storage"
    root.mkdir()
    monkeypatch.setattr(settings, "storage_root", str(root))
    return root


@pytest.mark.parametrize("mode", ["RGB", "RGBA"])
def test_backfill_writes_jpeg_artifacts_at_every_configured_size(
    storage: Path, mode: str
) -> None:
    key = _write_png(storage, _png_bytes(mode))
    written = BACKFILL.backfill_evidence(key)

    assert len(written) == len(settings.thumbnail_sizes) == 2
    for size in settings.thumbnail_sizes:
        artifact = BACKFILL.thumbnail_path(key, size)
        assert artifact in written
        assert artifact.suffix == ".jpg"
        body = artifact.read_bytes()
        assert body[:3] == b"\xff\xd8\xff", (mode, size, body[:8])
        with Image.open(io.BytesIO(body)) as decoded:
            decoded.load()
            assert decoded.format == "JPEG"
            assert max(decoded.size) <= size
    assert not list(storage.rglob("*.tmp"))


def test_backfill_skips_existing_artifacts_by_default(storage: Path) -> None:
    key = _write_png(storage, _png_bytes())
    first = BACKFILL.backfill_evidence(key)
    before = {path: path.read_bytes() for path in first}

    second = BACKFILL.backfill_evidence(key)

    assert second == []
    assert {path: path.read_bytes() for path in first} == before


def test_backfill_overwrite_replaces_a_stale_artifact(storage: Path) -> None:
    key = _write_png(storage, _png_bytes())
    first = BACKFILL.backfill_evidence(key)
    artifact = first[0]
    artifact.write_bytes(b"stale-not-jpeg")

    again = BACKFILL.backfill_evidence(key, overwrite=True)

    assert artifact in again
    assert artifact.read_bytes()[:3] == b"\xff\xd8\xff"


@pytest.fixture
def sg130_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "sg130.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    household = Household(name="SG-130 Household")
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
        yield session, household.id, storage_root
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def test_backfilled_artifact_is_served_200_jpeg(sg130_env) -> None:  # type: ignore[no-untyped-def]
    session, household_id, storage_root = sg130_env
    payload = _png_bytes("RGBA")
    key = _write_png(storage_root, payload, household=household_id)
    evidence = Evidence(
        household_id=household_id,
        sha256=hashlib.sha256(payload).hexdigest(),
        media_type="image/png",
        storage_key=key,
        original_filename="scan.png",
        size_bytes=len(payload),
    )
    session.add(evidence)
    session.commit()

    BACKFILL.backfill_evidence(key)

    with TestClient(app) as client:
        for size in settings.thumbnail_sizes:
            served = client.get(
                f"/v1/evidence/{evidence.id}/thumb/{size}",
                params={"household_id": household_id},
            )
            assert served.status_code == 200, served.text
            assert served.headers["content-type"].startswith("image/jpeg")
            assert served.content[:3] == b"\xff\xd8\xff", (size, served.content[:8])
