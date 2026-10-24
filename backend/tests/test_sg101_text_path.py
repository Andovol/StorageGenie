"""SG-101 text-path gates: separate text bound + empty-content accounting ($0).

Scope: the metered TEXT turn only (the vision path is deliberately untouched).
What this file proves (`PG-EV-04`/`PG-EV-01`):
- `build_text_payload` carries the new `TEXT_MAX_TOKENS` bound while the vision
  path's `DEFAULT_MAX_TOKENS` stays byte-untouched and its `:135` pin stays green;
- `extract_text`'s post-body empty-content raise carries the received body's
  usage/cost/latency (the SG-062 mechanism) exactly like the no-choices leg, so
  a billed empty-200 (SG-099: reasoning tokens, `content` empty) can be ledgered;
- the vision path's empty-content leg stays usage-free (text path ONLY).

No network, no key: every provider here is a `_post` stub over recorded body
shapes. The single live leg is the bounded worklog call, never this suite.
"""

from __future__ import annotations

import io
from typing import Any

import pytest
from PIL import Image

from app.services.providers import opencode_go as go
from app.services.providers.router import ProviderError

VISION_MAX_TOKENS = 2000
TEXT_BOUND = 8000


def _png_bytes() -> bytes:
    """A tiny real PNG: the vision path redacts (decodes) bytes before sending."""
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buf, format="PNG")
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# G1 — separate text bound; vision constant byte-untouched
# --------------------------------------------------------------------------- #
def test_text_payload_carries_new_bound_and_vision_constant_untouched() -> None:
    """The text builder moves to `TEXT_MAX_TOKENS`; the vision constant does not."""
    assert go.DEFAULT_MAX_TOKENS == VISION_MAX_TOKENS, "vision constant byte-untouched"
    assert go.TEXT_MAX_TOKENS == TEXT_BOUND
    assert go.TEXT_MAX_TOKENS != go.DEFAULT_MAX_TOKENS

    text_payload = go.build_text_payload("some-model", "SYSTEM", "USER")
    assert text_payload["max_tokens"] == go.TEXT_MAX_TOKENS
    assert text_payload["max_tokens"] == TEXT_BOUND

    # The vision builder (`extract_items`) keeps the old bound, unchanged.
    vision_payload = go.build_chat_payload("some-model", "SYSTEM", "Zm9v")
    assert vision_payload["max_tokens"] == go.DEFAULT_MAX_TOKENS


# --------------------------------------------------------------------------- #
# G2 — empty-content raise carries the received body's accounting
# --------------------------------------------------------------------------- #
def test_text_extract_empty_content_carries_received_body_accounting() -> None:
    """SG-101: the SG-099 empty-200 leg (reasoning burn) is billed, so account it.

    Shape is the `:333` raise-legs test extended to the content leg: a 200 body
    with non-zero usage and empty `content` must raise carrying `usage`/`cost`/
    `latency_ms` so `reader._write_error_ledger` records what crossed the wire.
    """
    usage = {"prompt_tokens": 1039, "completion_tokens": 2000, "total_tokens": 3039}
    expected_cost = go.compute_cost(usage)

    class _BodyProvider(go.OpenCodeGoProvider):
        def __init__(self, body: dict[str, Any]) -> None:
            super().__init__(session_id="sg101-content-leg")
            self._body = body

        def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
            return self._body

    body = {
        "id": "x",
        "model": "deepseek-v4-flash-vision-exp",
        "choices": [
            {
                "finish_reason": "length",
                "message": {"content": "", "reasoning_content": "We need output JSON only. ..."},
            }
        ],
        "usage": usage,
    }
    provider = _BodyProvider(body)
    with pytest.raises(ProviderError) as caught:
        provider.extract_text("USER", "SYSTEM")
    exc = caught.value
    assert exc.kind == "invalid_json"
    assert exc.usage == usage, "body usage must cross the boundary"
    assert exc.cost == expected_cost, "cost is the file's own compute_cost"
    assert exc.latency_ms is not None and exc.latency_ms >= 0.0


def test_vision_empty_content_leg_stays_usage_free_text_path_only() -> None:
    """The vision path is NOT changed: its empty-content leg stays accounting-free."""
    usage = {"prompt_tokens": 754, "completion_tokens": 341, "total_tokens": 1095}

    class _BodyProvider(go.OpenCodeGoProvider):
        def __init__(self, body: dict[str, Any]) -> None:
            super().__init__(session_id="sg101-vision-content-leg")
            self._body = body

        def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
            return self._body

    provider = _BodyProvider(
        {
            "id": "x",
            "model": "m",
            "usage": usage,
            "choices": [{"message": {"content": "   "}}],
        }
    )
    with pytest.raises(ProviderError) as caught:
        provider.extract_items(_png_bytes(), "prompt")
    exc = caught.value
    assert exc.kind == "invalid_json"
    assert getattr(exc, "usage", None) is None
    assert getattr(exc, "cost", None) is None
    assert getattr(exc, "latency_ms", None) is None
