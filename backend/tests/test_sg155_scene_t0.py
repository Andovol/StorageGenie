"""SG-155 T0 — OpenRouter scene client seam + frozen request envelope (offline, $0).

Scope: this file makes NO network call and needs NO key (`PG-EV-04`). It asserts
the key-resolution seam and the request the client WOULD send
(`build_scene_request`), mirroring SG-082's Jina shape tests. The two live legs
of T0 (image-model catalogue and the server-tool contract) are recorded in the
worklog, never here.

What this file proves:
- G1: `resolve_openrouter_key` reads explicit > `settings.openrouter_api_key` >
  `OPENROUTER_API_KEY` env, else `None` (the caller then refuses loudly).
- G1: `build_scene_request` builds the frozen envelope — endpoint
  `https://openrouter.ai/api/v1/chat/completions`, `tool_choice: "required"`,
  exactly one `openrouter:image_generation` tool entry, `max_tool_calls: 1`, the
  T0-PINNED `stop_server_tools_when` condition schema, headers WITHOUT
  `Authorization` (added at send time), and the asset photo as message image
  content (never as query text).
- G1: the three loud refusals (`missing_key`, `refused_consent`, `over_cap`)
  return a `SceneRefusal` value and never raise.
"""

from __future__ import annotations

import json

import pytest

from app.config import settings
from app.services.scene import openrouter as scene

PHOTO = "data:image/jpeg;base64,QUJD"
BRIEF = "restage this asset on a marble kitchen counter"
IMAGE_MODEL = "openai/gpt-5-image"
ORCHESTRATOR = "google/gemini-3.1-flash-image"

# The five condition `type`s pinned by the live OpenAPI contract on 2026-10-09
# (`https://openrouter.ai/openapi.json`, components.schemas.StopServerToolsWhen).
T0_PINNED_STOP_TYPES = frozenset(
    {"step_count_is", "has_tool_call", "max_tokens_used", "max_cost", "finish_reason_is"}
)


def _request(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "photo_ref": PHOTO,
        "brief": BRIEF,
        "image_model": IMAGE_MODEL,
        "orchestrator": ORCHESTRATOR,
    }
    kwargs.update(overrides)
    return scene.build_scene_request(**kwargs)


# --------------------------------------------------------------------------- #
# G1 — the seam constants
# --------------------------------------------------------------------------- #
def test_env_name_and_endpoint_are_the_pinned_constants() -> None:
    assert scene.OPENROUTER_API_KEY_ENV == "OPENROUTER_API_KEY"
    assert scene.SCENE_ENDPOINT_URL == "https://openrouter.ai/api/v1/chat/completions"


# --------------------------------------------------------------------------- #
# G1 — key resolution: explicit > settings field > env > None (Jina shape)
# --------------------------------------------------------------------------- #
def test_settings_field_beats_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(scene.OPENROUTER_API_KEY_ENV, "test-env-key")
    monkeypatch.setattr(settings, "openrouter_api_key", "test-field-key")
    assert scene.resolve_openrouter_key() == "test-field-key"


def test_explicit_argument_beats_the_settings_field(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(scene.OPENROUTER_API_KEY_ENV, "test-env-key")
    monkeypatch.setattr(settings, "openrouter_api_key", "test-field-key")
    assert scene.resolve_openrouter_key("test-explicit-key") == "test-explicit-key"


def test_absent_field_falls_through_to_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "openrouter_api_key", None)
    monkeypatch.setenv(scene.OPENROUTER_API_KEY_ENV, "test-env-key")
    assert scene.resolve_openrouter_key() == "test-env-key"


def test_no_field_no_env_resolves_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "openrouter_api_key", None)
    monkeypatch.delenv(scene.OPENROUTER_API_KEY_ENV, raising=False)
    assert scene.resolve_openrouter_key() is None


# --------------------------------------------------------------------------- #
# G1 — the frozen request envelope (offline, `PG-EV-04`)
# --------------------------------------------------------------------------- #
def test_built_request_is_the_frozen_envelope() -> None:
    request = _request()
    assert request["method"] == "POST"
    assert request["url"] == "https://openrouter.ai/api/v1/chat/completions"

    headers = request["headers"]
    assert isinstance(headers, dict)
    assert "Authorization" not in headers  # the key is added at SEND time only
    assert headers.get("Content-Type") == "application/json"

    body = request["json"]
    assert isinstance(body, dict)
    assert body["model"] == ORCHESTRATOR
    assert body["tool_choice"] == "required"
    assert body["max_tool_calls"] == 1

    tools = body["tools"]
    assert isinstance(tools, list)
    assert len(tools) == 1  # exactly one image-generation tool entry
    assert tools[0]["type"] == "openrouter:image_generation"
    assert tools[0]["parameters"]["model"] == IMAGE_MODEL

    user = body["messages"][-1]
    assert user["role"] == "user"
    parts = user["content"]
    assert isinstance(parts, list)
    assert {"type": "text", "text": BRIEF} in parts
    assert {"type": "image_url", "image_url": {"url": PHOTO}} in parts


def test_photo_never_enters_the_text_part() -> None:
    request = _request()
    body = request["json"]
    text_parts = [p for p in body["messages"][-1]["content"] if p["type"] == "text"]
    assert text_parts == [{"type": "text", "text": BRIEF}]
    assert PHOTO not in text_parts[0]["text"]


def test_stop_condition_uses_the_t0_pinned_schema() -> None:
    request = _request(spend_cap_usd=1.0)
    conditions = request["json"]["stop_server_tools_when"]
    assert isinstance(conditions, list) and conditions
    assert {c["type"] for c in conditions} <= T0_PINNED_STOP_TYPES
    # exactly one tool step is allowed, from the verified schema
    assert {"type": "step_count_is", "step_count": 1} in conditions
    # the spend cap is expressed as the verified max_cost condition
    assert {"type": "max_cost", "max_cost_in_dollars": 1.0} in conditions


def test_no_spend_condition_when_no_cap_is_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "sg_scene_cap", None)
    request = _request(spend_cap_usd=None)
    conditions = request["json"]["stop_server_tools_when"]
    assert all(c["type"] != "max_cost" for c in conditions)


def test_configured_cap_is_used_when_no_explicit_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "sg_scene_cap", 0.75)
    request = _request()
    conditions = request["json"]["stop_server_tools_when"]
    assert {"type": "max_cost", "max_cost_in_dollars": 0.75} in conditions


def test_builder_carries_no_key_material(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(scene.OPENROUTER_API_KEY_ENV, "test-env-key")
    request = _request()
    rendered = json.dumps(request, sort_keys=True)
    assert "test-env-key" not in rendered
    assert "Authorization" not in request["headers"]


# --------------------------------------------------------------------------- #
# G1 — loud refusal constructors (`PG-SC-03`)
# --------------------------------------------------------------------------- #
def test_refusal_constructors_are_loud_values_and_never_raise() -> None:
    missing = scene.missing_key()
    refused = scene.refused_consent()
    over = scene.over_cap(cap_usd=1.0, spent_usd=1.25)
    for refusal in (missing, refused, over):
        assert isinstance(refusal, scene.SceneRefusal)
    assert missing.code == "missing_key"
    assert scene.OPENROUTER_API_KEY_ENV in missing.reason
    assert refused.code == "refused_consent"
    assert "consent" in refused.reason.lower()
    assert over.code == "over_cap"
    assert "1.0" in over.reason and "1.25" in over.reason
