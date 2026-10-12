"""SG-159 G0-fix — 2xx-body persistence + extractor hardening (offline, $0; `PG-EV-04`).

Fail-pre on the SG-158 base: the extractor misses the documented
`openrouter:image_generation` result shapes (`result`, `imageB64`, `b64_json`),
a failed tool status is not surfaced, and no response body is persisted for 2xx
responses (F-SG158-3). Pass-post: every live body is persisted at return with
its sha256, the extractor reads the documented shapes, and a billed tool
failure ledgers its reason. All HTTP legs are `httpx.MockTransport` — no
network, no key, no metered call; the live renders live in
`docs/worklogs/SG-159_*`.

A1 pins are exercised against a real SQLAlchemy SQLite session (same fixture
shape as `test_sg158_scene_render.py`), not a stand-in (`PG-SC-12`).
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  (registers every table for create_all)
from app.config import settings
from app.db import Base
from app.models.evidence import Evidence
from app.models.household import Household
from app.models.provider_call import ProviderCall
from app.services.scene import openrouter as scene

BRIEF = "restage this labeled packet on a clean kitchen counter in warm daylight"
IMAGE_MODEL = "google/gemini-3.1-flash-image"
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
PHOTO = "data:image/png;base64,QUJD"
KEY = "test-key-value-never-stored"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 248
PNG_B64 = base64.b64encode(PNG_BYTES).decode()
PNG_DATA_URL = "data:image/png;base64," + PNG_B64
AUTHORITY = scene.SceneSpendAuthority(grant_id="D-1009-4 + L3 (D-1009-7) + D-1009-10", cap_usd=1.0)
WORST_CASE = 0.05
HOUSEHOLD_ID = "hhhhhhhh-1590-4590-8590-hhhhhhhhhhhh"


@pytest.fixture()
def db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Session:
    monkeypatch.setattr(settings, "storage_root", str(tmp_path / "storage"))
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(Household(id=HOUSEHOLD_ID, name="Test Household"))
    session.commit()
    try:
        yield session
    finally:
        session.close()


def _tool_payload(
    *,
    image_url: str | None = None,
    image_b64: str | None = None,
    tool_error: str | None = None,
    cost: float | None = 0.0003,
) -> dict[str, Any]:
    item: dict[str, Any] = {"type": "openrouter:image_generation"}
    if tool_error is not None:
        item.update({"status": "failed", "error": tool_error})
    else:
        item.update({"status": "completed"})
        if image_url is not None:
            item["imageUrl"] = image_url
        if image_b64 is not None:
            item["imageB64"] = image_b64
    usage: dict[str, Any] = {"prompt_tokens": 10, "completion_tokens": 5}
    if cost is not None:
        usage["cost"] = cost
    return {
        "id": "gen-sg159-1",
        "choices": [{"message": {"role": "assistant", "content": [item]}}],
        "usage": usage,
    }


def _client(
    payload: dict[str, Any] | None = None,
    *,
    post_status: int = 200,
    get_bytes: bytes | None = None,
    get_status: int = 200,
) -> tuple[httpx.Client, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.method == "POST":
            return httpx.Response(post_status, json=payload, request=request)
        return httpx.Response(
            get_status,
            content=get_bytes or b"",
            headers={"Content-Type": "image/png"},
            request=request,
        )

    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def _call(db: Session, client: httpx.Client, **overrides: Any) -> scene.SceneRenderOutcome:
    kwargs: dict[str, Any] = {
        "db": db,
        "household_id": HOUSEHOLD_ID,
        "photo_ref": PHOTO,
        "brief": BRIEF,
        "image_model": IMAGE_MODEL,
        "orchestrator": ORCHESTRATOR,
        "worst_case_usd": WORST_CASE,
        "authority": AUTHORITY,
        "key": KEY,
        "http_client": client,
    }
    kwargs.update(overrides)
    return scene.render_scene(**kwargs)


# --------------------------------------------------------------------------- #
# extractor hardening — the documented server-tool output shapes
# --------------------------------------------------------------------------- #
def test_extract_image_url_reads_b64_json_shape() -> None:
    found = scene.extract_image_url({"data": [{"b64_json": PNG_B64, "media_type": "image/png"}]})
    assert found is not None and found.startswith("data:image/png;base64,")
    assert base64.b64decode(found.split(",", 1)[1]) == PNG_BYTES


def test_extract_image_url_reads_result_imageb64_and_imageurl() -> None:
    assert (
        scene.extract_image_url({"status": "completed", "result": "https://x/y.png"})
        == "https://x/y.png"
    )
    found = scene.extract_image_url({"status": "completed", "imageB64": PNG_B64})
    assert found is not None and base64.b64decode(found.split(",", 1)[1]) == PNG_BYTES
    assert (
        scene.extract_image_url(
            {"type": "openrouter:image_generation", "status": "completed", "imageUrl": PNG_DATA_URL}
        )
        == PNG_DATA_URL
    )


def test_extract_image_url_ignores_prose_and_short_strings() -> None:
    assert scene.extract_image_url({"choices": [{"message": {"content": "no image here"}}]}) is None
    assert scene.extract_image_url({"result": "short"}) is None
    assert scene.extract_image_url({"choices": []}) is None


def test_extract_image_tool_error_surfaces_a_failed_tool() -> None:
    payload = _tool_payload(tool_error="Generation failed due to content policy")
    message = scene.extract_image_tool_error(payload)
    assert message is not None and message.startswith("image_tool_failed:")
    assert "content policy" in message
    assert scene.extract_image_tool_error({"status": "error", "error": "boom"}) is not None
    assert scene.extract_image_tool_error(_tool_payload(image_url=PNG_DATA_URL)) is None


# --------------------------------------------------------------------------- #
# response-body persistence — real SQLite rows, 2xx and errors
# --------------------------------------------------------------------------- #
def test_successful_render_persists_2xx_body_with_sha(db: Session) -> None:
    client, _ = _client(_tool_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client)
    assert outcome.status == "rendered"

    entry = db.query(ProviderCall).one()
    payload = json.loads(entry.output_payload or "{}")
    body = payload["response_body"]
    assert isinstance(body, str) and "gen-sg159-1" in body and "usage" in body
    assert payload["response_body_sha256"] == hashlib.sha256(body.encode()).hexdigest()
    assert (Path(settings.storage_root) / db.query(Evidence).one().storage_key).read_bytes() == (
        PNG_BYTES
    )


def test_error_response_body_is_persisted_as_well(db: Session) -> None:
    client, _ = _client({"error": {"message": "rate limited"}}, post_status=429)
    outcome = _call(db, client)
    assert outcome.status == "failed"
    entry = db.query(ProviderCall).one()
    payload = json.loads(entry.output_payload or "{}")
    assert "rate limited" in payload["response_body"]
    assert "rate limited" in payload["error_body"]
    assert payload["response_body_sha256"] is not None


def test_billed_tool_failure_ledgers_reason_and_cost(db: Session) -> None:
    client, seen = _client(_tool_payload(tool_error="Generation failed due to content policy"))
    outcome = _call(db, client)
    assert outcome.status == "failed"
    assert outcome.error_state is not None
    assert outcome.error_state.startswith("image_tool_failed:")
    assert db.query(Evidence).count() == 0
    entry = db.query(ProviderCall).one()
    assert entry.cost == 0.0003  # billed, never dropped
    assert entry.error_state is not None and "content policy" in entry.error_state
    payload = json.loads(entry.output_payload or "{}")
    assert "content policy" in payload["response_body"]
    assert [r.method for r in seen] == ["POST"]


def test_long_inline_base64_is_redacted_structure_kept(db: Session) -> None:
    blob = "A" * 3000
    payload = _tool_payload(image_url=PNG_DATA_URL)
    payload["debug"] = {"blob": blob, "note": "kept"}
    client, _ = _client(payload)
    outcome = _call(db, client)
    assert outcome.status == "rendered"
    entry = db.query(ProviderCall).one()
    stored = json.loads(entry.output_payload or "{}")["response_body"]
    assert "<redacted len=3000" in stored
    assert "kept" in stored and "debug" in stored
    assert blob not in stored


# --------------------------------------------------------------------------- #
# dedicated Image API transport (SG-159 G0-fix decision)
# --------------------------------------------------------------------------- #
def test_image_api_request_shape() -> None:
    request = scene.build_image_request(PHOTO, BRIEF, IMAGE_MODEL)
    assert request["method"] == "POST"
    assert request["url"] == "https://openrouter.ai/api/v1/images"
    headers = request["headers"]
    assert isinstance(headers, dict) and "Authorization" not in headers
    body = request["json"]
    assert isinstance(body, dict)
    assert body["model"] == IMAGE_MODEL and body["prompt"] == BRIEF and body["n"] == 1
    assert body["input_references"] == [{"type": "image_url", "image_url": {"url": PHOTO}}]


def test_image_api_render_stores_b64_image(db: Session) -> None:
    payload = {
        "created": 1748372400,
        "data": [{"b64_json": PNG_B64, "media_type": "image/png"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 4175, "cost": 0.01},
    }
    client, seen = _client(payload)
    outcome = _call(db, client, transport="image_api")
    assert outcome.status == "rendered"
    assert outcome.cost_usd == 0.01
    assert outcome.error_state is None
    row = db.query(Evidence).one()
    assert (Path(settings.storage_root) / row.storage_key).read_bytes() == PNG_BYTES
    entry = db.query(ProviderCall).one()
    stored = json.loads(entry.output_payload or "{}")["response_body"]
    assert "b64_json" in stored and "usage" in stored
    assert [r.method for r in seen] == ["POST"]  # no download GET on this path


def test_image_api_200_without_image_ledgers_billed_miss(db: Session) -> None:
    client, _ = _client({"created": 1, "data": [], "usage": {"cost": 0.01}})
    outcome = _call(db, client, transport="image_api")
    assert outcome.status == "failed"
    assert outcome.error_state == "image_b64_missing"
    assert db.query(Evidence).count() == 0
    assert db.query(ProviderCall).one().cost == 0.01


# --------------------------------------------------------------------------- #
# frozen envelope re-asserted offline (PG-EV-04)
# --------------------------------------------------------------------------- #
def test_frozen_envelope_reasserted_offline() -> None:
    request = scene.build_scene_request(
        PHOTO, BRIEF, IMAGE_MODEL, ORCHESTRATOR, spend_cap_usd=WORST_CASE
    )
    assert request["url"] == "https://openrouter.ai/api/v1/chat/completions"
    headers = request["headers"]
    assert isinstance(headers, dict) and "Authorization" not in headers
    body = request["json"]
    assert isinstance(body, dict)
    assert body["tool_choice"] == "required" and body["max_tool_calls"] == 1
    tools = body["tools"]
    assert isinstance(tools, list) and len(tools) == 1
    assert tools[0]["type"] == "openrouter:image_generation"
    assert tools[0]["parameters"]["model"] == IMAGE_MODEL
    conditions = body["stop_server_tools_when"]
    assert {"type": "step_count_is", "step_count": 1} in conditions
    assert {"type": "max_cost", "max_cost_in_dollars": WORST_CASE} in conditions
    assert PHOTO in json.dumps(body)
