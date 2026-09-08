from __future__ import annotations

import io
import json
from datetime import timedelta
from pathlib import Path

import pytest
import qrcode
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, AuditEvent, Household, JobStep, ReviewTask
from app.services import job_service, signals
from app.services.observations import Observation


@pytest.fixture
def phase1_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "phase1.db"
    storage_root = tmp_path / "storage"
    input_root = tmp_path / "mixed-folder"
    storage_root.mkdir()
    input_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Phase 1 E2E Household")
    session.add(household)
    session.commit()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    monkeypatch.setattr(settings, "exif_timestamps_enabled", True)

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, input_root
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _jpeg_bytes(image: Image.Image, *, exif: Image.Exif | None = None, quality: int = 95) -> bytes:
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=quality, exif=exif.tobytes() if exif else b"")
    return output.getvalue()


def _png_bytes(image: Image.Image) -> bytes:
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _tiff_bytes(image: Image.Image) -> bytes:
    output = io.BytesIO()
    image.save(output, format="TIFF")
    return output.getvalue()


def _ean13_image(first_twelve: str) -> tuple[Image.Image, str]:
    check = (10 - ((sum(int(d) for d in first_twelve[::2]) + 3 * sum(int(d) for d in first_twelve[1::2])) % 10)) % 10
    value = first_twelve + str(check)
    left = {
        "0": "0001101", "1": "0011001", "2": "0010011", "3": "0111101", "4": "0100011",
        "5": "0110001", "6": "0101111", "7": "0111011", "8": "0110111", "9": "0001011",
    }
    right = {
        "0": "1110010", "1": "1100110", "2": "1101100", "3": "1000010", "4": "1011100",
        "5": "1001110", "6": "1010000", "7": "1000100", "8": "1001000", "9": "1110100",
    }
    middle = {
        "0": "LLLLLL", "1": "LLGLGG", "2": "LLGGLG", "3": "LLGGGL", "4": "LGLLGG",
        "5": "LGGLLG", "6": "LGGGLL", "7": "LGLGLG", "8": "LGLGGL", "9": "LGGLGL",
    }
    first = middle[value[0]]
    left_g = {
        "0": "0100111", "1": "0110011", "2": "0011011", "3": "0100001", "4": "0011101",
        "5": "0111001", "6": "0000101", "7": "0010001", "8": "0001001", "9": "0010111",
    }
    bits = "101"
    for digit, mode in zip(value[1:7], first):
        bits += left[digit] if mode == "L" else left_g[digit]
    bits += "01010" + "".join(right[digit] for digit in value[7:]) + "101"
    scale, quiet, height = 4, 10, 120
    image = Image.new("RGB", ((len(bits) + quiet * 2) * scale, height), "white")
    draw = ImageDraw.Draw(image)
    for index, bit in enumerate("0" * quiet + bits + "0" * quiet):
        if bit == "1":
            draw.rectangle((index * scale, 0, (index + 1) * scale - 1, height), fill="black")
    return image, value


def _base_image() -> Image.Image:
    image = Image.new("RGB", (160, 120), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 130, 90), fill="navy")
    draw.ellipse((60, 35, 110, 85), fill="gold")
    return image


def _upload(client: TestClient, household_id: str, filename: str, data: bytes, media_type: str) -> dict[str, object]:
    response = client.post(
        "/v1/evidence",
        params={"household_id": household_id},
        files={"file": (filename, data, media_type)},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_phase1_exit_condition(phase1_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: C901
    session, household_id, input_root = phase1_fixture
    base = _base_image()
    anchor_bytes = _jpeg_bytes(base, quality=75)
    exif = Image.Exif()
    exif[0x9003] = "2026:09:08 12:34:56"
    ean_image, ean_value = _ean13_image("590123412345")
    qr_value = "https://example.test/SG-020"
    files = {
        "exif": ("phase1-camera.jpg", _jpeg_bytes(base, exif=exif), "image/jpeg"),
        "qr": ("phase1-qr.png", _png_bytes(qrcode.make(qr_value).convert("RGB")), "image/png"),
        "ean": ("phase1-barcode.png", _png_bytes(ean_image), "image/png"),
        "plain": ("phase1-camera.png", _png_bytes(base), "image/png"),
        "tiff": ("phase1-document.tiff", _tiff_bytes(Image.new("RGB", (17, 11), "red")), "image/tiff"),
    }

    with TestClient(app) as client:
        anchor_evidence = _upload(client, household_id, "anchor.jpg", anchor_bytes, "image/jpeg")
        anchor_asset_response = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            json={
                "display_name": "Phase 1 Existing Camera",
                "asset_type": "camera",
                "evidence_ids": [anchor_evidence["id"]],
            },
        )
        assert anchor_asset_response.status_code == 201, anchor_asset_response.text
        anchor_asset_id = anchor_asset_response.json()["id"]

        # The anchor is pre-existing catalog state needed to make both dedup legs meaningful.
        session.add(
            Assertion(
                asset_id=anchor_asset_id,
                field_path="identifier",
                value_json=json.dumps(ean_value),
                source_type="user",
                review_state="accepted",
            )
        )
        session.commit()
        anchor_observations = signals.extract_observations(anchor_evidence["id"], session)
        assert any(row.kind == "phash" for row in anchor_observations)
        session.commit()

        input_ids: list[str] = []
        input_payloads: dict[str, dict[str, object]] = {}
        for key, (filename, data, media_type) in files.items():
            input_path = input_root / filename
            input_path.write_bytes(data)
            payload = _upload(client, household_id, filename, input_path.read_bytes(), media_type)
            input_payloads[key] = payload
            input_ids.append(str(payload["id"]))
        assert input_payloads["tiff"]["media_type"] == "image/tiff"

        created = client.post(
            "/v1/imports",
            params={"household_id": household_id},
            headers={"Idempotency-Key": "sg-020-phase1-import"},
            json={"evidence_ids": input_ids},
        )
        assert created.status_code == 201, created.text
        job_id = str(created.json()["id"])
        assert [step["step_name"] for step in created.json()["steps"]] == list(job_service.STEP_NAMES)
        assert len(session.query(JobStep).filter_by(job_id=job_id).all()) == 6

        asset_ids_before_failure = {
            row.id for row in session.query(Asset).filter_by(household_id=household_id).all()
        }
        original_execute = job_service.execute_step
        failed_once = False

        def fail_normalizing(db: Session, job: object, step: object) -> dict[str, object]:
            nonlocal failed_once
            if getattr(step, "step_name", None) == "NORMALIZING" and not failed_once:
                failed_once = True
                raise RuntimeError("SG-020 injected normalizing failure")
            return original_execute(db, job, step)  # type: ignore[arg-type]

        monkeypatch.setattr(job_service, "execute_step", fail_normalizing)
        first_run = client.post(f"/v1/imports/{job_id}/run", params={"household_id": household_id})
        assert first_run.status_code == 200
        assert first_run.json()["state"] == "FAILED"
        failed_detail = client.get(f"/v1/imports/{job_id}", params={"household_id": household_id})
        assert failed_detail.status_code == 200
        assert failed_detail.json()["state"] == "FAILED"
        failed_step = next(step for step in failed_detail.json()["steps"] if step["state"] == "FAILED")
        assert failed_step["step_name"] == "NORMALIZING"
        assert failed_step["error"] == "SG-020 injected normalizing failure"
        assert {
            row.id for row in session.query(Asset).filter_by(household_id=household_id).all()
        } == asset_ids_before_failure

        retried = client.post(f"/v1/imports/{job_id}/retry", params={"household_id": household_id})
        assert retried.status_code == 200
        assert retried.json()["state"] == "AWAITING_REVIEW"
        awaiting = client.get(f"/v1/imports/{job_id}", params={"household_id": household_id})
        assert awaiting.status_code == 200
        assert awaiting.json()["state"] == "AWAITING_REVIEW"
        assert awaiting.json()["progress"] == {"completed": 4, "total": 6, "failed": 0, "pending": 1}
        assert failed_once

        observation_rows = (
            session.query(Observation)
            .filter(Observation.evidence_id.in_(input_ids))
            .order_by(Observation.created_at, Observation.id)
            .all()
        )
        assert all(
            any(row.evidence_id == evidence_id and row.kind == "phash" for row in observation_rows)
            for evidence_id in input_ids
        )
        exif_rows = [
            row for row in observation_rows
            if row.evidence_id == input_payloads["exif"]["id"] and row.kind == "exif"
        ]
        assert len(exif_rows) == 1
        assert json.loads(exif_rows[0].value_json)["timestamp"] == "2026:09:08 12:34:56"

        decoder_status: dict[str, str] = {}
        for key, expected in (("qr", qr_value), ("ean", ean_value)):
            rows = [
                row for row in observation_rows
                if row.evidence_id == input_payloads[key]["id"] and row.kind == "barcode_qr"
            ]
            valid = [json.loads(row.value_json) for row in rows if json.loads(row.value_json).get("validated")]
            if valid:
                assert any(item.get("value") == expected for item in valid)
                decoder_status[key] = "present"
            else:
                decoder_status[key] = "degraded"

        dedup_step = next(
            step for step in awaiting.json()["steps"] if step["step_name"] == "DEDUPLICATING"
        )
        candidate_id = str(dedup_step["output"]["candidate_id"])
        candidate_response = client.get(
            f"/v1/candidates/{candidate_id}", params={"household_id": household_id}
        )
        assert candidate_response.status_code == 200
        candidate = candidate_response.json()
        assert candidate["id"] == candidate_id
        assert candidate["job_id"] == job_id
        assert candidate["evidence_ids"] == input_ids
        similar = [match for match in candidate["dedup_matches"] if match["type"] == "similar"]
        assert any(match["asset_id"] == anchor_asset_id for match in similar)
        collision_task_ids = candidate["review_task_ids"]
        assert collision_task_ids
        tasks = client.get("/v1/review-tasks", params={"household_id": household_id})
        assert tasks.status_code == 200
        collision_task = next(
            item for item in tasks.json()["items"] if item["id"] in collision_task_ids
        )
        assert collision_task["task_type"] == "identifier_collision"
        assert collision_task["status"] == "open"

        blocked = client.post(
            f"/v1/candidates/{candidate_id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        assert blocked.status_code == 409

        resolved = client.post(
            f"/v1/review-tasks/{collision_task["id"]}/resolve",
            params={"household_id": household_id},
            json={"resolution": "confirmed"},
        )
        assert resolved.status_code == 200
        assert resolved.json()["status"] == "resolved"
        accepted = client.post(
            f"/v1/candidates/{candidate_id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["job"]["state"] == "COMPLETED"
        asset_id = str(accepted.json()["asset_id"])
        assert asset_id not in asset_ids_before_failure

        asset_detail = client.get(f"/v1/assets/{asset_id}", params={"household_id": household_id})
        assert asset_detail.status_code == 200
        detail = asset_detail.json()
        assert detail["id"] == asset_id
        assert {item["id"] for item in detail["evidence"]} == set(input_ids)
        assert {item["action"] for item in detail["audit_events"]} >= {
            "asset.create", "asset.accepted", "asset.lifecycle.created"
        }
        assert {item["review_state"] for item in detail["assertions"]} >= {"accepted", "proposed"}

        classified = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
            params={"household_id": household_id},
            json={"category": "food"},
        )
        assert classified.status_code == 200, classified.text
        assert classified.json()["expiry_assertion"]["review_state"] == "needs_evidence"
        expiry_task = next(
            item for item in client.get(
                "/v1/review-tasks", params={"household_id": household_id}
            ).json()["items"]
            if item["task_type"] == "expiry.manual_entry" and item["status"] == "open"
        )
        entered = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
            params={"household_id": household_id},
            json={
                "expiry_date": "2030-05-06",
                "date_type": "best_before",
                "unit": "piece",
                "source_evidence_ids": [input_payloads["exif"]["id"]],
            },
        )
        assert entered.status_code == 200, entered.text
        assert entered.json()["assertion"]["source_type"] == "user"
        assert entered.json()["assertion"]["review_state"] == "accepted"
        assert entered.json()["assertion"]["source_evidence_ids"] == [input_payloads["exif"]["id"]]
        assert expiry_task["status"] == "open"
        resolved_expiry = session.query(ReviewTask).filter_by(id=expiry_task["id"]).one()
        assert resolved_expiry.status == "resolved"

        stem = str(candidate["fields"]["display_name"])
        searched = client.get(
            "/v1/assets", params={"household_id": household_id, "q": stem, "limit": 100}
        )
        assert searched.status_code == 200
        assert asset_id in {item["id"] for item in searched.json()["items"]}

        exported = client.get("/v1/export", params={"household_id": household_id})
        assert exported.status_code == 200
        manifest = exported.json()
        assert {anchor_asset_id, asset_id} <= {item["id"] for item in manifest["assets"]}
        assert set(input_ids) <= {item["id"] for item in manifest["evidence_manifest"]}

    audit_rows = (
        session.query(AuditEvent)
        .filter(AuditEvent.household_id == household_id)
        .order_by(AuditEvent.timestamp, AuditEvent.id)
        .all()
    )
    job_created = next(row for row in audit_rows if row.action == "job.create" and row.entity_id == job_id)
    asset_accepted = next(row for row in audit_rows if row.action == "asset.accepted" and row.entity_id == asset_id)
    assert job_created.timestamp is not None
    assert asset_accepted.timestamp is not None
    assert asset_accepted.timestamp >= job_created.timestamp
    uv5 = asset_accepted.timestamp - job_created.timestamp
    assert uv5 >= timedelta(0)
    print(
        "SG-020 E2E "
        f"job_id={job_id} candidate_id={candidate_id} asset_id={asset_id} "
        f"anchor_asset_id={anchor_asset_id} evidence_ids={input_ids} "
        f"similar_anchor={anchor_asset_id} collision_409=409 retry=AWAITING_REVIEW "
        f"decoder_status={decoder_status} uv5_seconds={uv5.total_seconds():.6f}"
    )
