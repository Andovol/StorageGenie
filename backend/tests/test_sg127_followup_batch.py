"""SG-127 follow-up batch: thumbnail bytes, extraction brand promotion, job->candidates.

$0, offline: real Pillow fixtures, real storage, real routes; no provider call,
no network, no metered path.

What this file proves (`PG-EV-09` fail-then-pass, `PG-SC-02` trace-to-read):
- G1: the served thumbnail BYTES match the served NAME/TYPE for jpeg/png/webp
  (plus heic through the SG-110 decode path): every artifact is `.jpg` + JPEG
  magic + `image/jpeg` (F-SG118-2).
- G2: the v3 extraction `brand` is promoted into candidate `fields`, is visible
  through the served candidate read, and commits as a `brand` assertion; a null
  extraction brand stays null (never invented or substituted).
- G3: `GET /v1/jobs/{job_id}/candidates` lists a job's candidates; unknown job ->
  404, foreign household -> 403 (the `_owned_job` gate shape).
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pillow_heif
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Household, Job
from app.services import candidates as candidates_service
from app.services.candidates import Candidate, build_candidate_from_extraction
from app.services.providers.schemas import ExtractionItem, ExtractionOutput
from app.storage.local_store import thumbnail_path

THUMB_SIZE = 256


@pytest.fixture
def sg127_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "sg127.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr("app.config.settings.storage_root", str(storage_root))
    household = Household(name="SG-127 Household")
    other_household = Household(name="SG-127 Other Household")
    session.add_all([household, other_household])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, other_household.id, storage_root
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


# --------------------------------------------------------------------------- #
# G1 — served thumbnail bytes match the served name/type
# --------------------------------------------------------------------------- #
def _image_bytes(fmt: str) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), "teal").save(buffer, format=fmt)
    return buffer.getvalue()


def _rgba_png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGBA", (40, 30), (0, 128, 128, 128)).save(buffer, format="PNG")
    return buffer.getvalue()


def _heic_bytes() -> bytes:
    buffer = io.BytesIO()
    pillow_heif.from_pillow(Image.new("RGB", (40, 30), "teal")).save(buffer, quality=50)
    return buffer.getvalue()


THUMB_CASES = [
    ("jpeg", "image/jpeg", "photo.jpg", _image_bytes, "JPEG"),
    ("png", "image/png", "scan.png", _rgba_png_bytes, "PNG"),
    ("webp", "image/webp", "clip.webp", _image_bytes, "WEBP"),
    ("heic", "image/heic", "IMG.heic", _heic_bytes, "HEIC"),
]


@pytest.mark.parametrize(
    ("kind", "media_type", "filename", "make", "source_format"),
    THUMB_CASES,
    ids=[case[0] for case in THUMB_CASES],
)
def test_served_thumbnail_bytes_match_served_name(  # type: ignore[no-untyped-def]
    sg127_env, kind, media_type, filename, make, source_format
) -> None:
    _session, household_id, _other, _storage = sg127_env
    data = make(source_format) if make is _image_bytes else make()
    with TestClient(app) as client:
        uploaded = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": (filename, data, media_type)},
        )
        assert uploaded.status_code == 201, uploaded.text
        evidence = uploaded.json()
        assert evidence["media_type"] == media_type
        served = client.get(
            f"/v1/evidence/{evidence['id']}/thumb/{THUMB_SIZE}",
            params={"household_id": household_id},
        )

    assert served.status_code == 200, served.text
    assert served.headers["content-type"].startswith("image/jpeg")
    body = served.content
    # The served bytes are a real JPEG, matching the served `image/jpeg` type...
    assert body[:3] == b"\xff\xd8\xff", (kind, body[:8])
    with Image.open(io.BytesIO(body)) as decoded:
        decoded.load()
        assert decoded.format == "JPEG"
    # ...and matching the artifact's `.jpg` name on disk (bytes vs suffix).
    artifact = thumbnail_path(evidence["storage_key"], THUMB_SIZE)
    assert artifact.suffix == ".jpg"
    assert artifact.read_bytes()[:3] == b"\xff\xd8\xff"


def test_jpeg_thumbnail_still_generated_and_bounded(sg127_env) -> None:  # type: ignore[no-untyped-def]
    _session, household_id, _other, _storage = sg127_env
    with TestClient(app) as client:
        uploaded = client.post(
            "/v1/evidence",
            params={"household_id": household_id},
            files={"file": ("photo.jpg", _image_bytes("JPEG"), "image/jpeg")},
        )
        evidence = uploaded.json()
        served = client.get(
            f"/v1/evidence/{evidence['id']}/thumb/{THUMB_SIZE}",
            params={"household_id": household_id},
        )

    assert served.status_code == 200
    with Image.open(io.BytesIO(served.content)) as decoded:
        assert max(decoded.size) <= THUMB_SIZE


# --------------------------------------------------------------------------- #
# G2 — extraction brand promotion -> served read -> committed label assertion
# --------------------------------------------------------------------------- #
def _extraction(brand: str | None) -> ExtractionOutput:
    return ExtractionOutput(
        items=[ExtractionItem(name="Milk", brand=brand, confidence=1.0)],
        unknowns=[],
        needs_evidence=False,
    )


def _job(session: Session, household_id: str) -> Job:
    job = Job(
        job_type="import",
        state="RUNNING",
        config_snapshot=json.dumps({"evidence_ids": []}),
        household_id=household_id,
    )
    session.add(job)
    session.commit()
    return job


def _analyzing() -> dict[str, object]:
    return {
        "provider": "scripted",
        "model": "scripted-model-1",
        "prompt_template_version": "extract-food-v3",
        "provider_call_ids": ["call-v3"],
    }


def test_extraction_brand_reaches_served_candidate_and_committed_assertion(  # type: ignore[no-untyped-def]
    sg127_env,
) -> None:
    session, household_id, _other, _storage = sg127_env
    job = _job(session, household_id)
    candidate = build_candidate_from_extraction(
        session, job, _extraction("DairyGold"), _analyzing()
    )
    session.commit()

    with TestClient(app) as client:
        read = client.get(
            f"/v1/candidates/{candidate.id}", params={"household_id": household_id}
        )

    assert read.status_code == 200, read.text
    brand = read.json()["fields"]["brand"]
    assert brand["value"] == "DairyGold"
    assert brand["source_type"] == "extraction"

    fetched = session.query(Candidate).filter_by(id=candidate.id).one()
    fetched.state = "accepted"
    session.flush()
    result = candidates_service.commit_candidate(session, fetched)
    session.flush()
    rows = (
        session.query(Assertion)
        .filter_by(asset_id=result["asset_id"], field_path="brand")
        .all()
    )
    assert len(rows) == 1
    assert json.loads(rows[0].value_json) == "DairyGold"
    assert rows[0].source_type == "extraction"


def test_extraction_null_brand_stays_null(sg127_env) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _other, _storage = sg127_env
    job = _job(session, household_id)
    candidate = build_candidate_from_extraction(
        session, job, _extraction(None), _analyzing()
    )
    session.commit()

    proposal = json.loads(candidate.proposed_fields_json)
    assert "brand" not in proposal["fields"]
    assert proposal["ai_items"][0]["brand"] is None


def test_split_child_keeps_its_own_brand_or_none(sg127_env) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _other, _storage = sg127_env
    job = _job(session, household_id)
    extraction = ExtractionOutput(
        items=[
            ExtractionItem(name="Milk", brand="DairyGold", confidence=1.0),
            ExtractionItem(name="Bread", brand=None, confidence=1.0),
        ],
        unknowns=[],
        needs_evidence=False,
    )
    candidate = build_candidate_from_extraction(session, job, extraction, _analyzing())
    session.commit()

    children, _resolved = candidates_service.split_candidate(session, candidate, [0, 1])
    session.commit()
    child_fields = [json.loads(child.proposed_fields_json)["fields"] for child in children]
    assert child_fields[0]["brand"]["value"] == "DairyGold"
    assert "brand" not in child_fields[1]


# --------------------------------------------------------------------------- #
# G3 — GET job -> candidates route (household-scoped, sibling gate)
# --------------------------------------------------------------------------- #
def _add_candidate(session: Session, job: Job, household_id: str) -> Candidate:
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json="[]",
        proposed_fields_json=json.dumps(
            {
                "kind": "new_asset",
                "asset_id": None,
                "fields": {},
                "dedup_matches": [],
                "review_task_ids": [],
            }
        ),
        state="proposed",
        household_id=household_id,
    )
    session.add(candidate)
    session.commit()
    return candidate


def test_job_candidates_route_lists_and_gates(sg127_env) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_household_id, _storage = sg127_env
    job = _job(session, household_id)
    first = _add_candidate(session, job, household_id)
    second = _add_candidate(session, job, household_id)
    empty_job = _job(session, household_id)

    with TestClient(app) as client:
        listed = client.get(
            f"/v1/jobs/{job.id}/candidates", params={"household_id": household_id}
        )
        empty = client.get(
            f"/v1/jobs/{empty_job.id}/candidates", params={"household_id": household_id}
        )
        missing = client.get(
            "/v1/jobs/missing-job/candidates", params={"household_id": household_id}
        )
        foreign = client.get(
            f"/v1/jobs/{job.id}/candidates", params={"household_id": other_household_id}
        )

    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert body["total"] == 2
    assert {item["id"] for item in body["items"]} == {first.id, second.id}
    assert all(item["job_id"] == job.id for item in body["items"])
    assert all(item["state"] == "proposed" for item in body["items"])
    assert empty.status_code == 200
    assert empty.json() == {"items": [], "total": 0}
    assert missing.status_code == 404
    assert foreign.status_code == 403
