from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.evidence import Evidence
from app.services.observations import Observation
from app.storage.local_store import storage_path

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/tiff"}
OCR_KIND = "ocr"
BARCODE_KIND = "barcode_qr"
EXIF_KIND = "exif"
PHASH_KIND = "phash"
_EAN_L = {
    "0001101": "0", "0011001": "1", "0010011": "2", "0111101": "3", "0100011": "4",
    "0110001": "5", "0101111": "6", "0111011": "7", "0110111": "8", "0001011": "9",
}
_EAN_G = {
    "0100111": "0", "0110011": "1", "0011011": "2", "0100001": "3", "0011101": "4",
    "0111001": "5", "0000101": "6", "0010001": "7", "0001001": "8", "0010111": "9",
}
_EAN_R = {
    "1110010": "0", "1100110": "1", "1101100": "2", "1000010": "3", "1011100": "4",
    "1001110": "5", "1010000": "6", "1000100": "7", "1001000": "8", "1110100": "9",
}
_EAN_PARITY = {
    "LLLLLL": "0", "LLGLGG": "1", "LLGGLG": "2", "LLGGGL": "3", "LGLLGG": "4",
    "LGGLLG": "5", "LGGGLL": "6", "LGLGLG": "7", "LGLGGL": "8", "LGGLGL": "9",
}


class SignalQuarantineError(RuntimeError):
    """The original cannot be decoded safely for deterministic extraction."""


def get_observations(db: Session, observation_ids: list[str] | tuple[str, ...]) -> list[Observation]:
    if not observation_ids:
        return []
    rows = db.scalars(select(Observation).where(Observation.id.in_(observation_ids))).all()
    by_id = {row.id: row for row in rows}
    return [by_id[observation_id] for observation_id in observation_ids if observation_id in by_id]


def hamming_distance(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("dHash values must have equal length")
    return sum((int(a, 16) ^ int(b, 16)).bit_count() for a, b in zip(left, right))


def _pixel_value(image: Image.Image, x: int, y: int) -> int:
    pixel = image.getpixel((x, y))
    if isinstance(pixel, tuple):
        component = pixel[0]
        return int(component) if isinstance(component, (int, float)) else 0
    return int(pixel) if isinstance(pixel, (int, float)) else 0


def dhash_hex(image: Image.Image) -> str:
    grayscale = ImageOps.grayscale(image).resize((9, 8), Image.Resampling.LANCZOS)
    bits = [_pixel_value(grayscale, x, y) > _pixel_value(grayscale, x + 1, y) for y in range(8) for x in range(8)]
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def _quarantine(reason: str) -> SignalQuarantineError:
    return SignalQuarantineError(f"quarantined: {reason}")


def _stored_path(evidence: Evidence) -> Path:
    if evidence.media_type not in SUPPORTED_IMAGE_TYPES:
        raise _quarantine(f"unsupported media type {evidence.media_type}")
    path = storage_path(evidence.storage_key)
    if not path.is_file():
        raise _quarantine(f"original missing at storage key {evidence.storage_key}")
    return path


def _open_image(path: Path) -> Image.Image:
    try:
        image = Image.open(path)
        image.load()
        return image
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise _quarantine(f"image decode failed: {exc}") from exc


def _barcode_observations(image: Image.Image) -> list[tuple[dict[str, Any], float]]:  # noqa: C901
    try:
        from pyzbar.pyzbar import decode
    except ImportError:
        logger.warning("Barcode extraction unavailable: pyzbar/libzbar is not installed")
        decoded = []
    else:
        try:
            decoded = decode(image)
        except Exception as exc:  # pragma: no cover - depends on the system zbar ABI
            logger.warning("Barcode extraction unavailable: %s", exc)
            decoded = []

    payloads = [(bytes(item.data), str(item.type)) for item in decoded]
    if not any(item_type.upper().replace("_", "-") in {"EAN13", "EAN-13"} for _, item_type in payloads):
        fallback = _fallback_ean13(image)
        if fallback:
            payloads.append((fallback, "EAN13"))

    observations: list[tuple[dict[str, Any], float]] = []
    for raw, item_type in payloads:
        symbology = item_type.upper().replace("_", "-")
        try:
            value = raw.decode("utf-8")
        except UnicodeDecodeError:
            value = ""
        if symbology in {"QRCODE", "QR-CODE"}:
            valid = bool(value and "\x00" not in value)
            if valid:
                observations.append(({"symbology": "QR", "value": value, "validated": True}, 1.0))
            else:
                observations.append(({"symbology": "QR", "validated": False, "reason": "invalid_utf8_or_empty"}, 0.1))
            continue

        digits = value if value.isdigit() else ""
        if symbology in {"EAN13", "EAN-13"}:
            valid = len(digits) == 13 and _ean_check_digit(digits)
            label = "EAN-13"
        elif symbology in {"UPCA", "UPC-A"}:
            valid = len(digits) == 12 and _upc_check_digit(digits)
            label = "UPC-A"
        else:
            valid = False
            label = symbology
        if valid:
            observations.append(({"symbology": label, "value": digits, "validated": True}, 1.0))
        else:
            # Do not persist the unvalidated payload: this is a signal about a
            # failed candidate, never an identifier available to later slices.
            observations.append(({"symbology": label, "validated": False, "reason": "check_digit_or_syntax"}, 0.1))
    return observations


def _fallback_ean13(image: Image.Image) -> bytes | None:
    """Recover a full-frame EAN-13 candidate when zbar rejects a bad check digit."""
    mask = ImageOps.grayscale(image).point(lambda pixel: 0 if pixel < 128 else 255)
    bbox = ImageOps.invert(mask).getbbox()
    if bbox is None:
        return None
    cropped = mask.crop((bbox[0], 0, bbox[2], mask.height))
    width = cropped.width
    if width < 95:
        return None
    bits = "".join(
        "1"
        if _pixel_value(cropped, min(width - 1, int((index + 0.5) * width / 95)), cropped.height // 2) < 128
        else "0"
        for index in range(95)
    )
    if not (bits.startswith("101") and bits[45:50] == "01010" and bits.endswith("101")):
        return None
    left_digits: list[str] = []
    parity: list[str] = []
    for index in range(6):
        chunk = bits[3 + index * 7 : 10 + index * 7]
        if chunk in _EAN_L:
            left_digits.append(_EAN_L[chunk])
            parity.append("L")
        elif chunk in _EAN_G:
            left_digits.append(_EAN_G[chunk])
            parity.append("G")
        else:
            return None
    right_digits: list[str] = []
    for index in range(6):
        chunk = bits[50 + index * 7 : 57 + index * 7]
        if chunk not in _EAN_R:
            return None
        right_digits.append(_EAN_R[chunk])
    first_digit = _EAN_PARITY.get("".join(parity))
    if first_digit is None:
        return None
    return (first_digit + "".join(left_digits) + "".join(right_digits)).encode("ascii")


def _ean_check_digit(value: str) -> bool:
    expected = (10 - ((sum(int(d) for d in value[:12:2]) + 3 * sum(int(d) for d in value[1:12:2])) % 10)) % 10
    return int(value[-1]) == expected


def _upc_check_digit(value: str) -> bool:
    expected = (10 - ((3 * sum(int(d) for d in value[:11:2]) + sum(int(d) for d in value[1:11:2])) % 10)) % 10
    return int(value[-1]) == expected


def _ocr_observation(image: Image.Image) -> tuple[dict[str, Any], float] | None:
    try:
        import pytesseract
        from pytesseract import Output
    except ImportError:
        logger.warning("OCR extraction unavailable: pytesseract is not installed")
        return None
    try:
        data = pytesseract.image_to_data(image, lang="eng", config="--psm 6", output_type=Output.DICT)
    except Exception as exc:  # pragma: no cover - depends on the system tesseract binary
        logger.warning("OCR extraction unavailable: %s", exc)
        return None
    texts: list[str] = []
    boxes: list[dict[str, int | float | str]] = []
    confidences: list[float] = []
    for index, raw_text in enumerate(data.get("text", [])):
        text = str(raw_text).strip()
        if not text:
            continue
        try:
            confidence = float(data["conf"][index])
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if confidence < 0:
            continue
        texts.append(text)
        confidences.append(confidence)
        boxes.append(
            {
                "text": text,
                "left": int(data["left"][index]),
                "top": int(data["top"][index]),
                "width": int(data["width"][index]),
                "height": int(data["height"][index]),
                "confidence": confidence,
            }
        )
    if not texts or not confidences:
        return None
    mean_confidence = sum(confidences) / len(confidences)
    return ({"text": " ".join(texts), "boxes": boxes, "mean_confidence": mean_confidence}, mean_confidence / 100.0)


def _exif_observation(image: Image.Image) -> tuple[dict[str, str], float] | None:
    if not settings.exif_timestamps_enabled:
        return None
    exif = image.getexif()
    for tag, name in ((0x9003, "DateTimeOriginal"), (0x9004, "DateTimeDigitized"), (0x0132, "DateTime")):
        value = exif.get(tag)
        if value:
            return ({"tag": name, "timestamp": str(value)}, 1.0)
    return None


def _new_observation(evidence_id: str, kind: str, value: dict[str, Any], confidence: float | None) -> Observation:
    return Observation(
        evidence_id=evidence_id,
        kind=kind,
        value_json=json.dumps(value, ensure_ascii=False, sort_keys=True),
        confidence=confidence,
    )


def _extract_rows(evidence_id: str, evidence: Evidence, db: Session) -> list[Observation]:
    image = _open_image(_stored_path(evidence))
    rows: list[Observation] = []
    for value, confidence in _barcode_observations(image):
        rows.append(_new_observation(evidence_id, BARCODE_KIND, value, confidence))
    ocr = _ocr_observation(image)
    if ocr:
        rows.append(_new_observation(evidence_id, OCR_KIND, ocr[0], ocr[1]))
    exif = _exif_observation(image)
    if exif:
        rows.append(_new_observation(evidence_id, EXIF_KIND, exif[0], exif[1]))
    rows.append(_new_observation(evidence_id, PHASH_KIND, {"hash": dhash_hex(image)}, 1.0))
    return rows


def extract_observations(evidence_id: str, db: Session | None = None) -> list[Observation]:  # noqa: C901
    """Extract and stage deterministic observations for one immutable original."""
    owns_session = db is None
    if owns_session:
        from app.db import SessionLocal

        db = SessionLocal()
    assert db is not None
    try:
        existing = db.scalars(select(Observation).where(Observation.evidence_id == evidence_id)).all()
        if existing:
            return list(existing)
        evidence = db.get(Evidence, evidence_id)
        if evidence is None:
            raise _quarantine(f"evidence {evidence_id} not found")
        rows = _extract_rows(evidence_id, evidence, db)
        db.add_all(rows)
        db.flush()
        if owns_session:
            db.commit()
        return rows
    except Exception:
        if owns_session:
            db.rollback()
        raise
    finally:
        if owns_session:
            db.close()


def observation_counts(rows: list[Observation]) -> dict[str, int]:
    return dict(sorted(Counter(row.kind for row in rows).items()))
