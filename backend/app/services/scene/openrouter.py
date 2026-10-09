"""OpenRouter scene-render client (SG-155, spec §§2–3).

Single integration: one owner-placed `OPENROUTER_API_KEY`, one frozen request
envelope against the OpenAI-compatible
`POST https://openrouter.ai/api/v1/chat/completions`. There is no per-vendor
client — the OpenRouter router is the adapter (spec §2).

Decisions recorded here (reported, not hidden):
- The `Authorization` header is added at SEND time from a key resolved through
  the settings/env seam (the enrich key-seam precedent, SG-097 in
  `services/enrich/`). The key VALUE is never returned by a builder, never
  stored in a request object and never logged.
- `resolve_openrouter_key` reads the declared `settings.openrouter_api_key`
  field first and otherwise the `OPENROUTER_API_KEY` process environment. The
  settings field is the declared carrier; the environment is the explicit
  fallback, never a silent one.
- The envelope is frozen: `tool_choice: "required"` (no model-decides vagueness),
  exactly one `openrouter:image_generation` tool, `max_tool_calls: 1`, and the
  `stop_server_tools_when` condition schema T0-PINNED from the live contract on
  2026-10-09 (`https://openrouter.ai/openapi.json`, openapi 3.1.0). The image
  model is CONFIG, never code (D7 swaps a name, not an architecture).
- The asset photo enters as message image content
  (`{"type": "image_url", "image_url": {"url": ...}}`), never as query text.

T0-PINNED (verbatim, re-stated for T1b, never re-derived):
- `stop_server_tools_when` is an array (`minItems: 1`) of conditions discriminated
  by `type`; any condition firing halts the loop (OR logic) and, when set, it
  OVERRIDES `max_tool_calls`. The five `type`s are `step_count_is`,
  `has_tool_call`, `max_tokens_used`, `max_cost`, `finish_reason_is`.
  - `max_cost`: `{"type": "max_cost", "max_cost_in_dollars": <number>}` required.
  - `step_count_is`: `{"type": "step_count_is", "step_count": <int>}` required.
- The `openrouter:image_generation` server tool "generates images from text
  prompts"; its parameters config is documented as accepting "all image_config
  params ... plus a model field" and does NOT declare a reference-image field.
  Reference images (`input_references`) are documented only on the standalone
  image-generation request, not on the server tool. T0b answer: on this
  chat-completions server-tool path the tool is text-prompt-only; the asset is
  carried by orchestrator vision into the text prompt.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from app.config import settings

SCENE_ENDPOINT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"

# T0-PINNED condition types (live OpenAPI contract, 2026-10-09).
STOP_CONDITION_TYPES = (
    "step_count_is",
    "has_tool_call",
    "max_tokens_used",
    "max_cost",
    "finish_reason_is",
)

# The orchestrator rewrites the photo + brief into a detailed render prompt
# (subject preserved, shape/label/material pinned; scene, lighting and framing
# variable), then the image tool renders it. The image model is config.
SCENE_SYSTEM_PROMPT = (
    "You are a product-scene director. You receive a photograph of a real "
    "household asset and a short scene brief. Rewrite the brief into one "
    "detailed image-generation prompt that preserves the asset's subject, "
    "shape, label and material exactly, while varying only the surrounding "
    "scene, lighting and framing. Then call the image generation tool once."
)


@dataclass(frozen=True)
class SceneRefusal:
    """A loud, named refusal: never an exception, never a silent empty run."""

    code: str
    reason: str


def resolve_openrouter_key(explicit: str | None = None) -> str | None:
    """Resolve the OpenRouter key through the settings/env seam.

    Explicit wins (test/DI seam), then the declared `openrouter_api_key`
    settings field, then the `OPENROUTER_API_KEY` process environment. Returns
    `None` when no key is present; the caller refuses loudly, never crashes.
    """
    if explicit:
        return explicit
    configured = getattr(settings, "openrouter_api_key", None)
    if isinstance(configured, str) and configured:
        return configured
    from_env = os.environ.get(OPENROUTER_API_KEY_ENV)
    return from_env or None


def _resolve_spend_cap(spend_cap_usd: float | None) -> float | None:
    if spend_cap_usd is not None:
        return spend_cap_usd
    configured = getattr(settings, "sg_scene_cap", None)
    if isinstance(configured, (int, float)):
        return float(configured)
    return None


def build_scene_request(
    photo_ref: str,
    brief: str,
    image_model: str,
    orchestrator: str,
    *,
    spend_cap_usd: float | None = None,
) -> dict[str, object]:
    """Build the exact sendable request; the key is added at SEND time only.

    `photo_ref` is the asset photo as a base64 data URL or HTTP(S) URL; it
    enters as message image content. `spend_cap_usd` overrides the configured
    `sg_scene_cap`. The returned dict carries `method`, `url`, `headers`
    (never `Authorization`) and the `json` body.
    """
    stop_conditions: list[dict[str, object]] = [
        # One render per request: stop the agent loop after a single tool step.
        {"type": "step_count_is", "step_count": 1}
    ]
    cap = _resolve_spend_cap(spend_cap_usd)
    if cap is not None:
        stop_conditions.append({"type": "max_cost", "max_cost_in_dollars": cap})

    body: dict[str, object] = {
        "model": orchestrator,
        "messages": [
            {"role": "system", "content": SCENE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": brief},
                    {"type": "image_url", "image_url": {"url": photo_ref}},
                ],
            },
        ],
        "tools": [
            {
                "type": "openrouter:image_generation",
                "parameters": {"model": image_model},
            }
        ],
        "tool_choice": "required",
        "max_tool_calls": 1,
        "stop_server_tools_when": stop_conditions,
    }
    return {
        "method": "POST",
        "url": SCENE_ENDPOINT_URL,
        "headers": {"Content-Type": "application/json"},
        "json": body,
    }


def missing_key() -> SceneRefusal:
    """Refuse a send when no key is present at any seam layer (`PG-SC-03`)."""
    return SceneRefusal(
        code="missing_key",
        reason=(
            f"missing_key: {OPENROUTER_API_KEY_ENV} is not present in the backend "
            "environment; refusing to send an unauthenticated scene render"
        ),
    )


def refused_consent() -> SceneRefusal:
    """Refuse a send when scene consent is not granted (privacy gate)."""
    return SceneRefusal(
        code="refused_consent",
        reason=(
            "refused_consent: scene rendering is consent-gated; sg_consent is "
            "not granted, so no photo is sent"
        ),
    )


def over_cap(*, cap_usd: float, spent_usd: float) -> SceneRefusal:
    """Refuse a send when the arc spend cap is already reached (never spend)."""
    return SceneRefusal(
        code="over_cap",
        reason=(
            f"over_cap: spent {spent_usd} USD has reached the {cap_usd} USD scene "
            "cap; refusing to spend further"
        ),
    )
