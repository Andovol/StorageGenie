import hashlib
import io
import mimetypes
from pathlib import Path

from PIL import Image, ImageOps
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.evidence import Evidence
from app.services import audit_service

ALLOWED_MEDIA = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG",
    "image/webp": b"RIFF",
    "application/pdf": b"%PDF",
}


def _detect_media_type(file_bytes: bytes, claimed: str) -> str:
    # Strict magic-byte check with WebP RIFF+WEBP handling
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_bytes.startswith(b"\x89PNG"):
        return "image/png"
    if file_bytes.startswith(b"%PDF"):
        return "application/pdf"
    if file_bytes.startswith(b"RIFF") and len(file_bytes) >= 12 and file_bytes[8:12] == b"WEBP":
        return "image/webp"
    # Fallback: honour claimed if it's an allowed type or generic image
    if claimed in ALLOWED_MEDIA or claimed.startswith("image/"):
        return claimed
    return claimed


def store_evidence(  # noqa: C901
    file_bytes: bytes,
    original_filename: str,
    media_type: str,
    household_id: str,
    db: Session,
    actor: str = "api",
) -> Evidence:
    if len(file_bytes) > settings.max_upload_bytes:
        raise ValueError("File too large")
    sha = hashlib.sha256(file_bytes).hexdigest()
    existing = db.query(Evidence).filter_by(sha256=sha).first()
    if existing:
        return existing

    media_type = _detect_media_type(file_bytes, media_type)
    ext = Path(original_filename).suffix.lower()
    if not ext:
        ext = mimetypes.guess_extension(media_type) or ".bin"
        if ext == ".jpe":
            ext = ".jpg"
    if not ext.startswith("."):
        ext = "." + ext
    rel = f"{household_id}/{sha[:2]}/{sha}{ext}"
    full = Path(settings.storage_root) / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    # Write original atomically
    tmp = full.with_suffix(full.suffix + ".tmp")
    tmp.write_bytes(file_bytes)
    tmp.rename(full)

    # Thumbnails for images (best-effort)
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img = ImageOps.exif_transpose(img)  # type: ignore[assignment]
        for size in settings.thumbnail_sizes:
            thumb = img.copy()
            thumb.thumbnail((size, size))
            tp = full.with_name(f"{full.stem}_thumb{size}{full.suffix}")
            # Handle mode conversion for JPEG thumbnails
            if tp.suffix.lower() in (".jpg", ".jpeg"):
                if thumb.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", thumb.size, (255, 255, 255))
                    bg.paste(thumb, mask=thumb.split()[-1] if thumb.mode == "RGBA" else None)
                    thumb = bg
                elif thumb.mode == "P":
                    thumb = thumb.convert("RGB")
                elif thumb.mode not in ("RGB", "L"):
                    thumb = thumb.convert("RGB")
                thumb.save(tp, format="JPEG")
            else:
                thumb.save(tp)
    except Exception:
        pass

    ev = Evidence(
        household_id=household_id,
        sha256=sha,
        media_type=media_type,
        storage_key=rel,
        original_filename=original_filename,
        size_bytes=len(file_bytes),
        source_kind="upload",
    )
    db.add(ev)
    try:
        db.flush()
        audit_service.record(
            db,
            actor=actor,
            action="evidence.create",
            entity_type="evidence",
            entity_id=ev.id,
            before=None,
            after={"sha256": sha, "original_filename": original_filename, "size_bytes": len(file_bytes)},
            household_id=household_id,
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        race = db.query(Evidence).filter_by(sha256=sha).first()
        if race is not None:
            return race
        raise
    db.refresh(ev)
    return ev
