"""SG-180 G1 probe — ingestion/evidence trace, byte integrity, disposable isolation.

Runs the REAL FastAPI routes against a disposable SQLite DB + storage root.
No production paths, no live providers, zero network. Prints one JSON object.

Run:
  cd /tmp/opencode && PYTHONPATH=<repo>/backend <repo>/backend/venv/bin/python \
      <repo>/docs/worklogs/SG-180_probe_g1.py
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg180-g1-"))
TEMP_DB = TEMP_ROOT / "storagegenie.db"
TEMP_STORAGE = TEMP_ROOT / "storage"
TEMP_STORAGE.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEMP_DB}"
os.environ["STORAGE_ROOT"] = str(TEMP_STORAGE)

from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image, ImageOps  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Evidence, Household  # noqa: E402
from app.services.evidence_service import ALLOWED_MEDIA  # noqa: E402

RESULTS: list[dict[str, object]] = []


def record(name: str, level: str, **detail: object) -> None:
    RESULTS.append({"check": name, "result": level, **detail})


def expect(name: str, condition: bool, **detail: object) -> None:
    record(name, "PASS" if condition else "FAIL", **detail)


def observe(name: str, **detail: object) -> None:
    record(name, "OBSERVE", **detail)


def jpeg_bytes(size=(64, 48), color="red", with_gps=False) -> bytes:
    image = Image.new("RGB", size, color)
    out = io.BytesIO()
    if with_gps:
        exif = Image.Exif()
        exif[0x0112] = 6
        exif[0x8825] = {1: "N", 2: (40.0, 1.0, 0.0), 3: "E", 4: (26.0, 2.0, 0.0)}
        image.save(out, format="JPEG", exif=exif.tobytes())
    else:
        image.save(out, format="JPEG")
    return out.getvalue()


def png_bytes(size=(20, 20), color="blue") -> bytes:
    out = io.BytesIO()
    Image.new("RGB", size, color).save(out, format="PNG")
    return out.getvalue()


def bomb_png(width: int, height: int) -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (1, 1), "red").save(out, format="PNG")
    data = bytearray(out.getvalue())
    struct.pack_into(">II", data, 16, width, height)
    struct.pack_into(">I", data, 29, zlib.crc32(data[12:29]) & 0xFFFFFFFF)
    return bytes(data)


def pdf_bytes() -> bytes:
    return b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF"


def upload(client: TestClient, household_id: str, data: bytes, filename: str, content_type: str, key: str | None = None):
    headers = {}
    if key is not None:
        headers["Idempotency-Key"] = key
    return client.post(
        "/v1/evidence",
        params={"household_id": household_id},
        files={"file": (filename, data, content_type)},
        headers=headers,
    )


def main() -> int:
    Base.metadata.create_all(engine)
    session = SessionLocal()
    house_a = Household(name="SG180 House A")
    house_b = Household(name="SG180 House B")
    session.add_all([house_a, house_b])
    session.commit()
    aid, bid = house_a.id, house_b.id

    isolation = {
        "temp_root": str(TEMP_ROOT),
        "settings_database_url": settings.database_url,
        "settings_storage_root": settings.storage_root,
        "engine_url": str(engine.url),
        "cwd": os.getcwd(),
    }
    print(json.dumps({"isolation": isolation}, indent=2))
    assert str(TEMP_ROOT) in settings.storage_root, "storage root not disposable"
    assert str(TEMP_ROOT) in settings.database_url, "database url not disposable"
    assert str(TEMP_ROOT) in str(engine.url), "engine not disposable"
    record("isolation", "PASS", **isolation)

    client = TestClient(app)
    img_a = jpeg_bytes(color="red")
    img_b = jpeg_bytes(color="green")
    img_c = jpeg_bytes(color="gray")
    img_gps = jpeg_bytes(with_gps=True)

    # --- G1.1 accepted/rejected inputs through the real route ---
    r = upload(client, aid, img_a, "a.jpg", "image/jpeg")
    expect("upload_jpeg_201", r.status_code == 201, status=r.status_code, body=r.json())
    ev_a = r.json() if r.status_code == 201 else None
    if ev_a:
        expect("upload_sha_matches_bytes", ev_a["sha256"] == hashlib.sha256(img_a).hexdigest(), sha=ev_a["sha256"])
        stored = TEMP_STORAGE / ev_a["storage_key"]
        expect("stored_file_under_temp_root", stored.is_file() and str(stored).startswith(str(TEMP_STORAGE)), path=str(stored))
        expect("stored_bytes_identical", stored.read_bytes() == img_a, size=stored.stat().st_size)

    r = upload(client, aid, pdf_bytes(), "doc.pdf", "application/pdf")
    expect("upload_pdf_201", r.status_code == 201, status=r.status_code, body=r.json())

    img_m = jpeg_bytes(color="orange")
    r = upload(client, aid, img_m, "mismatch.jpg", "image/png")
    expect("mismatch_declared_detected_422", r.status_code == 422 and "media_type_mismatch" in r.text, status=r.status_code, detail=r.json().get("detail"))
    r = upload(client, aid, img_a, "mismatch_replay.jpg", "image/png")
    record(
        "mismatch_claim_bypassed_on_known_bytes",
        "DEFECT_OBSERVED" if r.status_code == 201 else "PASS",
        status=r.status_code,
        returned_id=r.json().get("id"),
        note="sha short-circuit runs before _detect_media_type; a replayed sha returns 201 regardless of claimed media_type",
    )

    r = upload(client, aid, b"plain text, not media", "note.jpg", "image/jpeg")
    expect("unsupported_signature_422", r.status_code == 422 and "unsupported media signature" in r.text, status=r.status_code, detail=r.json().get("detail"))

    r = upload(client, aid, b"\x00" * (settings.max_upload_bytes + 1), "big.jpg", "image/jpeg")
    expect("oversize_413", r.status_code == 413, status=r.status_code, detail=r.json().get("detail"))

    truncated = jpeg_bytes()[: 60]
    r = upload(client, aid, truncated, "trunc.jpg", "image/jpeg")
    expect("truncated_jpeg_422", r.status_code == 422, status=r.status_code, detail=r.json().get("detail"))

    r = upload(client, aid, bomb_png(20000, 20000), "bomb.png", "image/png")
    expect("image_bomb_422", r.status_code == 422 and "decompression_bomb" in r.text, status=r.status_code, detail=r.json().get("detail"))

    record("allowed_media_table", "OBSERVE", allowed={k: v.decode("latin1") for k, v in ALLOWED_MEDIA.items()}, configured=settings.allowed_mime_types, max_upload_bytes=settings.max_upload_bytes, max_image_pixels=settings.max_image_pixels)

    # --- G1.2 EXIF/GPS handling: original retains, thumbnail strips ---
    r = upload(client, aid, img_gps, "gps.jpg", "image/jpeg")
    expect("upload_gps_jpeg_201", r.status_code == 201, status=r.status_code)
    ev_gps = r.json()
    served = client.get(f"/v1/evidence/{ev_gps['id']}/file", params={"household_id": aid})
    original_exif = Image.open(io.BytesIO(served.content)).getexif()
    gps_tag_present = 0x8825 in original_exif
    orient = original_exif.get(0x0112)
    thumb = client.get(f"/v1/evidence/{ev_gps['id']}/thumb/256", params={"household_id": aid})
    thumb_exif = dict(Image.open(io.BytesIO(thumb.content)).getexif()) if thumb.status_code == 200 else None
    observe("original_retains_gps_thumbnail_strips", gps_tag_present=gps_tag_present, orientation=orient, thumb_status=thumb.status_code, thumb_exif_keys=list(thumb_exif.keys()) if thumb_exif is not None else None, thumb_media=thumb.headers.get("content-type"))

    # --- G1.3 cross-household sha dedup (B uploads same bytes as A) ---
    r = upload(client, bid, img_a, "b_same.jpg", "image/jpeg")
    cross_id = r.json().get("id") if r.status_code == 201 else None
    foreign_read = client.get(f"/v1/evidence/{cross_id}", params={"household_id": bid}) if cross_id else None
    row = session.query(Evidence).filter_by(id=cross_id).first() if cross_id else None
    observe(
        "cross_household_sha_dedup",
        b_upload_status=r.status_code,
        returned_id=cross_id,
        a_evidence_id=ev_a["id"] if ev_a else None,
        returned_row_household=("A" if row and row.household_id == aid else "B" if row else None),
        b_get_status=foreign_read.status_code if foreign_read else None,
    )
    expect(
        "cross_household_sha_dedup_returned_a_row",
        row is not None and row.household_id == aid and cross_id == ev_a["id"],
        returned_id=cross_id,
        a_id=ev_a["id"],
    )
    # counter-control: different bytes for B yields B's own row
    r = upload(client, bid, img_b, "b_own.jpg", "image/jpeg")
    own_id = r.json().get("id") if r.status_code == 201 else None
    own_row = session.query(Evidence).filter_by(id=own_id).first() if own_id else None
    expect("counter_control_b_own_bytes_own_row", r.status_code == 201 and own_id != ev_a["id"] and own_row.household_id == bid, status=r.status_code, id=own_id)

    # --- G1.4 idempotency key replay across households ---
    r = upload(client, aid, img_c, "keyed_a.jpg", "image/jpeg", key="sg180-shared-key")
    keyed_a = r.json().get("id")
    r2 = upload(client, bid, img_gps, "keyed_b.jpg", "image/jpeg", key="sg180-shared-key")
    replay_id = r2.json().get("id") if r2.status_code == 201 else None
    observe(
        "cross_household_idempotency_replay",
        a_status=201 if keyed_a else None,
        a_id=keyed_a,
        b_status=r2.status_code,
        b_returned_id=replay_id,
        b_returned_a_row=bool(replay_id and replay_id == keyed_a),
        note="B sent DIFFERENT bytes under the same key",
    )
    expect("cross_household_key_replay_returns_a_row", replay_id == keyed_a, replay_id=replay_id, a_id=keyed_a)
    r3 = upload(client, bid, img_gps, "keyed_b2.jpg", "image/jpeg", key="sg180-fresh-key")
    expect("counter_control_fresh_key_own_row", r3.status_code == 201 and r3.json()["id"] != keyed_a, status=r3.status_code, id=r3.json().get("id"))

    # --- G1.5 immutability: re-upload same bytes returns same row, bytes untouched ---
    stored_c = TEMP_STORAGE / keyed_a
    # find row c
    row_c = session.query(Evidence).filter_by(id=keyed_a).one()
    path_c = TEMP_STORAGE / row_c.storage_key
    before_bytes = path_c.read_bytes()
    r = upload(client, aid, img_c, "renamed.jpg", "image/jpeg")
    same_id = r.json().get("id") if r.status_code == 201 else None
    expect("reupload_same_bytes_same_row", same_id == keyed_a, returned=same_id, first=keyed_a)
    expect("original_bytes_unchanged", path_c.read_bytes() == before_bytes, sha=hashlib.sha256(path_c.read_bytes()).hexdigest())

    # --- G1.6 same-size content corruption vs missing-file control ---
    img_d = jpeg_bytes(color="purple")
    r = upload(client, aid, img_d, "corrupt.jpg", "image/jpeg")
    ev_d = r.json()
    path_d = TEMP_STORAGE / ev_d["storage_key"]
    raw = bytearray(path_d.read_bytes())
    raw[len(raw) // 2] ^= 0xFF
    path_d.write_bytes(bytes(raw))
    served_corrupt = client.get(f"/v1/evidence/{ev_d['id']}/file", params={"household_id": aid})
    served_sha = hashlib.sha256(served_corrupt.content).hexdigest()
    record(
        "same_size_corruption_served",
        "DEFECT_OBSERVED" if served_corrupt.status_code == 200 and served_sha != ev_d["sha256"] else "PASS",
        status=served_corrupt.status_code,
        served_sha256=served_sha,
        db_sha256=ev_d["sha256"],
        note="read path does not verify content against sha256",
    )
    path_d.unlink()
    missing_file = client.get(f"/v1/evidence/{ev_d['id']}/file", params={"household_id": aid})
    thumb_still = client.get(f"/v1/evidence/{ev_d['id']}/thumb/256", params={"household_id": aid})
    record(
        "missing_original_controls",
        "PASS" if missing_file.status_code == 404 else "FAIL",
        file_status=missing_file.status_code,
        thumb_status_with_original_gone=thumb_still.status_code,
        note="thumbnail artifact is independent of the original at read time",
    )
    thumb_path = None
    stale = [p for p in TEMP_STORAGE.rglob("*.jpg") if ev_d["sha256"] in p.name]
    for p in stale:
        p.unlink()
    missing_thumb = client.get(f"/v1/evidence/{ev_d['id']}/thumb/256", params={"household_id": aid})
    expect("counter_control_missing_thumb_404", missing_thumb.status_code == 404, status=missing_thumb.status_code)

    # --- G1.7 foreign evidence read control ---
    foreign = client.get(f"/v1/evidence/{ev_a['id']}", params={"household_id": bid})
    expect("foreign_evidence_read_403", foreign.status_code == 403, status=foreign.status_code)

    # --- G1.7b upload against a non-existent household: file-before-row order ---
    bogus = "sg180-no-such-household"
    before_files = {p for p in TEMP_STORAGE.rglob("*") if p.is_file()}
    r = upload(client, bogus, jpeg_bytes(color="brown"), "orphan.jpg", "image/jpeg")
    after_files = {p for p in TEMP_STORAGE.rglob("*") if p.is_file()}
    new_files = sorted(str(p.relative_to(TEMP_STORAGE)) for p in after_files - before_files)
    record(
        "upload_unknown_household_orphan_file",
        "DEFECT_OBSERVED" if r.status_code == 422 and new_files else "PASS",
        status=r.status_code,
        detail=r.json().get("detail"),
        orphan_files=new_files,
        note="store_evidence writes the original before the Evidence row flush; FK rejection leaves the file",
    )

    # --- G1.8 factory trace: every written artifact under temp root ---
    all_paths_ok = all(str(p).startswith(str(TEMP_STORAGE)) for p in TEMP_STORAGE.rglob("*"))
    record("storage_tree", "PASS" if all_paths_ok else "FAIL", files=[str(p.relative_to(TEMP_STORAGE)) for p in sorted(TEMP_STORAGE.rglob("*")) if p.is_file()])

    session.close()
    print(json.dumps({"results": RESULTS}, indent=2))
    print(f"TEMP_ROOT={TEMP_ROOT}")
    failures = [r for r in RESULTS if r["result"] == "FAIL"]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
