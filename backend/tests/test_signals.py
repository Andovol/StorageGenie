from __future__ import annotations

import io
import json
from pathlib import Path
from typing import cast

import pytest
import qrcode
from alembic import command
from alembic.config import Config
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base
from app.models import Evidence, Household, JobStep
from app.services import job_service, signals
from app.services.observations import Observation


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "signals.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    household = Household(name="Signals Household")
    session.add(household)
    session.commit()
    try:
        yield session, household.id, storage_root
    finally:
        session.close()
        engine.dispose()


def _evidence(session: Session, household_id: str, root: Path, data: bytes, name: str, media: str) -> Evidence:
    key = f"signals/{name}"
    path = root / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    import hashlib

    row = Evidence(
        household_id=household_id,
        sha256=hashlib.sha256(data).hexdigest(),
        storage_key=key,
        media_type=media,
        original_filename=name,
        size_bytes=len(data),
    )
    session.add(row)
    session.commit()
    return row


def _png(image: Image.Image) -> bytes:
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _jpeg(image: Image.Image, exif: Image.Exif | None = None) -> bytes:
    output = io.BytesIO()
    image.save(output, format="JPEG", exif=exif.tobytes() if exif else b"")
    return output.getvalue()


def _ean13_image(first_twelve: str, check_digit: str | None = None) -> tuple[Image.Image, str]:
    assert len(first_twelve) == 12 and first_twelve.isdigit()
    check = (10 - ((sum(int(d) for d in first_twelve[::2]) + 3 * sum(int(d) for d in first_twelve[1::2])) % 10)) % 10
    value = first_twelve + (check_digit if check_digit is not None else str(check))
    left_patterns = {
        "0": "0001101", "1": "0011001", "2": "0010011", "3": "0111101", "4": "0100011",
        "5": "0110001", "6": "0101111", "7": "0111011", "8": "0110111", "9": "0001011",
    }
    right_patterns = {
        "0": "1110010", "1": "1100110", "2": "1101100", "3": "1000010", "4": "1011100",
        "5": "1001110", "6": "1010000", "7": "1000100", "8": "1001000", "9": "1110100",
    }
    parity = {
        "0": "LLLLLL", "1": "LLGLGG", "2": "LLGGLG", "3": "LLGGGL", "4": "LGLLGG",
        "5": "LGGLLG", "6": "LGGGLL", "7": "LGLGLG", "8": "LGLGGL", "9": "LGGLGL",
    }[value[0]]
    bits = "101"
    for digit, mode in zip(value[1:7], parity):
        bits += left_patterns[digit] if mode == "L" else {
            "0": "0100111", "1": "0110011", "2": "0011011", "3": "0100001", "4": "0011101",
            "5": "0111001", "6": "0000101", "7": "0010001", "8": "0001001", "9": "0010111",
        }[digit]
    bits += "01010"
    bits += "".join(right_patterns[digit] for digit in value[7:])
    bits += "101"
    scale, quiet, height = 4, 10, 120
    image = Image.new("RGB", ((len(bits) + quiet * 2) * scale, height), "white")
    draw = ImageDraw.Draw(image)
    for index, bit in enumerate("0" * quiet + bits + "0" * quiet):
        if bit == "1":
            draw.rectangle((index * scale, 0, (index + 1) * scale - 1, height), fill="black")
    return image, value


def _text_image() -> Image.Image:
    image = Image.new("RGB", (900, 220), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
    draw.text((30, 60), "SG-013 OCR TEST", font=font, fill="black")
    return image


def test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, root = isolated_db
    qr_value = "https://example.test/SG-013"
    qr_image = qrcode.make(qr_value).convert("RGB")
    qr = _evidence(session, household_id, root, _png(qr_image), "qr.png", "image/png")
    ean_image, ean_value = _ean13_image("590123412345")
    ean = _evidence(session, household_id, root, _png(ean_image), "ean.png", "image/png")
    # Deliberately render a syntactically valid EAN with the wrong check digit.
    bad_value = ean_value[:-1] + ("0" if ean_value[-1] != "0" else "1")
    bad_image, _ = _ean13_image(ean_value[:-1], bad_value[-1])
    bad = _evidence(session, household_id, root, _png(bad_image), "bad.png", "image/png")

    qr_rows = signals.extract_observations(qr.id, session)
    ean_rows = signals.extract_observations(ean.id, session)
    bad_rows = signals.extract_observations(bad.id, session)

    qr_values = [json.loads(row.value_json) for row in qr_rows if row.kind == "barcode_qr"]
    ean_values = [json.loads(row.value_json) for row in ean_rows if row.kind == "barcode_qr"]
    bad_values = [json.loads(row.value_json) for row in bad_rows if row.kind == "barcode_qr"]
    assert any(item.get("value") == qr_value and item["validated"] for item in qr_values)
    assert any(item.get("value") == ean_value and item["validated"] for item in ean_values)
    assert bad_value not in json.dumps(bad_values)
    assert any(item.get("validated") is False for item in bad_values)
    assert any(row.confidence is not None and row.confidence < 0.5 for row in bad_rows)


def test_ocr_has_text_boxes_and_mean_confidence(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, root = isolated_db
    evidence = _evidence(session, household_id, root, _png(_text_image()), "text.png", "image/png")
    rows = signals.extract_observations(evidence.id, session)
    ocr = [json.loads(row.value_json) for row in rows if row.kind == "ocr"]
    assert ocr
    assert any("SG-013" in item["text"] and item["boxes"] and item["mean_confidence"] > 0 for item in ocr)


def test_exif_timestamp_gate_never_persists_gps(isolated_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, root = isolated_db
    exif = Image.Exif()
    exif[0x9003] = "2026:09:08 12:34:56"
    exif[0x8825] = {1: "N", 2: (40.0, 0.0, 0.0), 3: "W", 4: (74.0, 0.0, 0.0)}
    evidence = _evidence(session, household_id, root, _jpeg(Image.new("RGB", (80, 80), "red"), exif), "dated.jpg", "image/jpeg")

    monkeypatch.setattr(settings, "exif_timestamps_enabled", False)
    assert not [row for row in signals.extract_observations(evidence.id, session) if row.kind == "exif"]
    session.query(Observation).delete()
    session.commit()
    monkeypatch.setattr(settings, "exif_timestamps_enabled", True)
    rows = signals.extract_observations(evidence.id, session)
    exif_values = [json.loads(row.value_json) for row in rows if row.kind == "exif"]
    assert any(item["timestamp"] == "2026:09:08 12:34:56" for item in exif_values)
    assert all("gps" not in json.dumps(item).lower() for item in exif_values)


def test_dhash_identical_near_resized_and_far(isolated_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, root = isolated_db
    base = Image.new("RGB", (160, 120), "white")
    ImageDraw.Draw(base).rectangle((20, 20, 130, 90), fill="navy")
    same = _evidence(session, household_id, root, _png(base), "base.png", "image/png")
    resized = _evidence(session, household_id, root, _png(base.resize((320, 240))), "resized.png", "image/png")
    different_image = Image.new("RGB", (160, 120), "white")
    ImageDraw.Draw(different_image).ellipse((20, 20, 130, 90), fill="orange")
    different = _evidence(session, household_id, root, _png(different_image), "different.png", "image/png")
    first = signals.extract_observations(same.id, session)
    second = signals.extract_observations(resized.id, session)
    third = signals.extract_observations(different.id, session)
    def value(rows: list[Observation]) -> str:
        return cast(str, next(json.loads(row.value_json)["hash"] for row in rows if row.kind == "phash"))
    assert value(first) == value(first)
    assert signals.dhash_hex(base) == signals.dhash_hex(base.copy())
    assert signals.hamming_distance(value(first), value(second)) <= settings.dhash_near_threshold
    assert signals.hamming_distance(value(first), value(third)) > settings.dhash_near_threshold


def test_corrupt_input_quarantines_and_retry_can_resume(isolated_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, root = isolated_db
    evidence = _evidence(session, household_id, root, b"not-an-image", "broken.bin", "application/octet-stream")
    job = job_service.create_job(session, household_id, [evidence.id])
    failed = job_service.run_job(session, job)
    failed_step = session.query(JobStep).filter_by(
        job_id=job.id, step_name="EXTRACTING_DETERMINISTIC_SIGNALS"
    ).one()
    assert failed.state == "FAILED"
    assert "quarantined" in json.loads(failed_step.output_refs or "{}")["error"]
    monkeypatch.setattr(signals, "extract_observations", lambda evidence_id, db: [])
    retried = job_service.retry_job(session, failed)
    assert retried.state == "AWAITING_REVIEW"


def test_step_output_refs_and_observation_getter(isolated_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, root = isolated_db
    evidence = _evidence(session, household_id, root, _png(Image.new("RGB", (40, 40), "white")), "plain.png", "image/png")
    job = job_service.create_job(session, household_id, [evidence.id])
    step = session.query(JobStep).filter_by(job_id=job.id, step_name="EXTRACTING_DETERMINISTIC_SIGNALS").one()
    monkeypatch.setattr(signals, "extract_observations", lambda evidence_id, db: [
        Observation(evidence_id=evidence_id, kind="phash", value_json='{"hash":"0000000000000000"}', confidence=1.0)
    ])
    output = job_service.execute_step(session, job, step)
    session.commit()
    assert output["counts"] == {"phash": 1}
    observation_ids = cast(list[str], output["observation_ids"])
    rows = signals.get_observations(session, observation_ids)
    assert [row.id for row in rows] == observation_ids


def test_observation_migration_upgrade_downgrade_upgrade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "migration.db"
    url = f"sqlite:///{database_path}"
    monkeypatch.setattr(settings, "database_url", url)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    assert "observation" in inspect(create_engine(url)).get_table_names()
    command.downgrade(config, "-1")
    assert "observation" not in inspect(create_engine(url)).get_table_names()
    command.upgrade(config, "head")
    assert "observation" in inspect(create_engine(url)).get_table_names()
