import hashlib
import io
import logging
import mimetypes
from pathlib import Path
import re
import struct
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.evidence import Evidence
from app.services import audit_service
from app.storage.local_store import storage_path_for, thumbnail_path

logger = logging.getLogger(__name__)

ALLOWED_MEDIA = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG",
    "image/webp": b"RIFF",
    "application/pdf": b"%PDF",
}


class EvidenceValidationError(ValueError):
    """The upload content cannot be accepted as evidence."""


class UploadTooLargeError(EvidenceValidationError):
    """The upload exceeds the configured byte limit."""


def _dimensions_from_bomb_message(message: str) -> str:
    match = re.search(r"Image size (\d+x\d+)", message)
    return match.group(1) if match else "unknown"


def _image_dimensions(file_bytes: bytes, message: str) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", Image.DecompressionBombWarning)
        try:
            image = Image.open(io.BytesIO(file_bytes))
            return f"{image.width}x{image.height}"
        except Exception:
            pass
    if file_bytes.startswith(b"\x89PNG") and len(file_bytes) >= 24:
        width, height = struct.unpack(">II", file_bytes[16:24])
        return f"{width}x{height}"
    return _dimensions_from_bomb_message(message)


def _detect_media_type(file_bytes: bytes, claimed: str) -> str:
    detected: str | None = None
    if file_bytes.startswith(b"\xff\xd8\xff"):
        detected = "image/jpeg"
    elif file_bytes.startswith(b"\x89PNG"):
        detected = "image/png"
    elif file_bytes.startswith(b"%PDF"):
        detected = "application/pdf"
    elif file_bytes.startswith(b"RIFF") and len(file_bytes) >= 12 and file_bytes[8:12] == b"WEBP":
        detected = "image/webp"

    if detected is None:
        raise EvidenceValidationError("media_type_mismatch: unsupported media signature")
    if claimed != detected:
        raise EvidenceValidationError(
            f"media_type_mismatch: claimed {claimed!r}, detected {detected!r}"
        )
    return detected


def _decode_image(file_bytes: bytes, sha: str) -> Image.Image:
    """Decode an image while converting Pillow bomb warnings into validation errors."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            image = Image.open(io.BytesIO(file_bytes))
            width, height = image.size
            configured_limit = settings.max_image_pixels
            if configured_limit is not None and width * height > configured_limit:
                dimensions = f"{width}x{height}"
                logger.warning(
                    "Rejected decompression bomb sha=%s dimensions=%s limit_kind=max_image_pixels limit=%s",
                    sha,
                    dimensions,
                    configured_limit,
                )
                raise EvidenceValidationError(
                    f"decompression_bomb limit exceeded: max_image_pixels ({dimensions})"
                )
            image = ImageOps.exif_transpose(image)
            image.load()
            return image
        except (Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
            dimensions = _image_dimensions(file_bytes, str(exc))
            logger.warning(
                "Rejected decompression bomb sha=%s dimensions=%s limit_kind=pillow_max_image_pixels",
                sha,
                dimensions,
            )
            raise EvidenceValidationError(
                f"decompression_bomb limit exceeded: Pillow max_image_pixels ({dimensions})"
            ) from exc
        except UnidentifiedImageError as exc:
            raise EvidenceValidationError("invalid image content") from exc


def _thumbnail_bytes(image: Image.Image, media_type: str, size: int) -> bytes:
    thumb = image.copy()
    thumb.thumbnail((size, size))
    output = io.BytesIO()
    if media_type == "image/jpeg":
        if thumb.mode in ("RGBA", "LA"):
            background = Image.new("RGB", thumb.size, (255, 255, 255))
            background.paste(thumb, mask=thumb.split()[-1] if thumb.mode == "RGBA" else None)
            thumb = background
        elif thumb.mode == "P":
            thumb = thumb.convert("RGB")
        elif thumb.mode not in ("RGB", "L"):
            thumb = thumb.convert("RGB")
        thumb.save(output, format="JPEG", exif=b"")
    else:
        format_name = {"image/png": "PNG", "image/webp": "WEBP"}[media_type]
        thumb.save(output, format=format_name, exif=b"")
    return output.getvalue()


def store_evidence(  # noqa: C901
    file_bytes: bytes,
    original_filename: str,
    media_type: str,
    household_id: str,
    db: Session,
    actor: str = "api",
) -> Evidence:
    if len(file_bytes) > settings.max_upload_bytes:
        raise UploadTooLargeError(
            f"max_upload_bytes limit exceeded: {len(file_bytes)} > {settings.max_upload_bytes} bytes"
        )
    sha = hashlib.sha256(file_bytes).hexdigest()
    existing = db.query(Evidence).filter_by(sha256=sha).first()
    if existing:
        return existing

    media_type = _detect_media_type(file_bytes, media_type)
    decoded_image: Image.Image | None = None
    if media_type.startswith("image/"):
        decoded_image = _decode_image(file_bytes, sha)
    ext = Path(original_filename).suffix.lower()
    if not ext:
        ext = mimetypes.guess_extension(media_type) or ".bin"
        if ext == ".jpe":
            ext = ".jpg"
    if not ext.startswith("."):
        ext = "." + ext
    full = storage_path_for(sha, ext, household_id)
    rel = full.relative_to(Path(settings.storage_root)).as_posix()
    full.parent.mkdir(parents=True, exist_ok=True)
    # Write original atomically
    tmp = full.with_suffix(full.suffix + ".tmp")
    try:
        tmp.write_bytes(file_bytes)
        tmp.replace(full)
    finally:
        if tmp.exists():
            tmp.unlink()

    # Thumbnails are best-effort, but every failure is observable and atomic.
    if decoded_image is not None:
        for size in settings.thumbnail_sizes:
            tp = thumbnail_path(rel, size)
            thumbnail_tmp = tp.with_suffix(tp.suffix + ".tmp")
            try:
                tp.parent.mkdir(parents=True, exist_ok=True)
                thumbnail_tmp.write_bytes(_thumbnail_bytes(decoded_image, media_type, size))
                thumbnail_tmp.replace(tp)
            except Exception:
                logger.warning("Thumbnail generation failed sha=%s size=%s", sha, size, exc_info=True)
            finally:
                if thumbnail_tmp.exists():
                    thumbnail_tmp.unlink()

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
