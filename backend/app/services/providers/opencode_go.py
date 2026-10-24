"""OpenCode GO vision adapter (SG-027) — raw httpx, no vendor SDK.

Facts below are the G1 re-spike (attempt-2) live-verified set only; nothing is
inherited from the packet. ONE stable session id is supplied per conversation;
header VALUES are never logged, and the API key is read from the backend
environment only and never placed in a log line, payload, or repr.

SG-250 (owner 2026-10-24: "Stop carrying about predicting costs, just log the
costs and thats it."): the pre-call estimate and both cost caps are gone. Every
call records the ACTUAL cost computed after the response from its real `usage`,
and emits one INFO line carrying provider, model, operation, cost, token counts
and latency — on success and on failure.
"""

from __future__ import annotations

import base64
import logging
import os
import re
import time
from typing import Any

import httpx

from app.services.providers.protocols import ProviderResult
from app.services.providers.redaction import redact_image
from app.services.providers.router import ProviderError
from app.services.providers.schemas import parse_extraction_output

logger = logging.getLogger(__name__)

BASE_URL = "https://opencode.ai/zen/go/v1"
CHAT_PATH = "/chat/completions"
DEFAULT_MODEL_ID = "deepseek-v4-flash-vision-exp"
USER_AGENT = "StorageGenie/0.1 (opencode-go vision adapter)"
DEFAULT_MAX_TOKENS = 2000
# SG-101: the TEXT turn gets its own bound. The default model is a reasoning
# model, so `reasoning_content` consumes completion budget before any answer;
# SG-099's live leg burned the full 2000 on reasoning and returned empty
# `content`. 4x headroom for reasoning+content; uncalibrated (G-A9). The VISION
# path keeps `DEFAULT_MAX_TOKENS` byte-untouched.
TEXT_MAX_TOKENS = 8000
CALL_TIMEOUT_S = 300.0
INPUT_USD_PER_1M = 0.15
OUTPUT_USD_PER_1M = 0.60

_THINK_RE = re.compile(r"^\s*<think>.*?</think>\s*", re.DOTALL)


def build_identity_headers(session_id: str) -> dict[str, str]:
    """Our own UA + ONE stable session id per conversation.

    The caller adds `Authorization` at send time; the key never enters this
    builder so it can never be logged together with the header set.
    """
    return {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "x-opencode-session": session_id,
    }


def response_format_for(model: str) -> dict[str, str]:
    """DeepSeek kin accept `json_object`; other models get `json_schema`."""
    if "deepseek" in model.lower():
        return {"type": "json_object"}
    return {"type": "json_schema"}


def guard_content(content: str | None) -> str:
    """Empty/blank 200 bodies are rejected before any parsing.

    This helper never sees the response body, so it attaches no accounting
    itself. The TEXT caller (`extract_text`) catches this raise and attaches the
    received body's usage/cost/latency (SG-101), so a billed empty-200 (SG-099:
    reasoning tokens consumed the completion budget, `content` arrived empty)
    can land a ledger row. A leg that raised before any completed 200 body has
    no usage to attach and stays honest `0.0`.
    """
    if content is None or not content.strip():
        raise ProviderError("invalid_json", "provider returned empty content (empty-200 reject)")
    return content


def guard_usage(usage: dict[str, Any]) -> dict[str, Any]:
    """A 200 without non-zero usage proves nothing and is rejected.

    The raised error carries the body's usage exactly as received (`0` values
    included) so the ledger records what crossed the wire rather than inventing.
    """
    total = usage.get("total_tokens") or 0
    if not total:
        total = (usage.get("prompt_tokens") or 0) + (usage.get("completion_tokens") or 0)
    if not total:
        exc = ProviderError("invalid_json", "provider returned zero or absent usage tokens")
        attach_body_accounting(exc, usage, latency_ms=None)
        raise exc
    return usage


def strip_single_think(text: str) -> str:
    """Strip ONE leading `<think>` block; a second block fails loudly."""
    match = _THINK_RE.match(text)
    if match is None:
        if "<think>" in text:
            raise ProviderError("invalid_json", "unbalanced or stray <think> block in content")
        return text
    rest = text[match.end() :]
    if "<think" in rest:
        raise ProviderError("invalid_json", "multiple <think> blocks: strip once, then fail loudly")
    return rest


def attach_body_accounting(
    exc: ProviderError,
    usage: dict[str, Any] | None,
    *,
    latency_ms: float | None,
) -> None:
    """Attach a RECEIVED body's usage/cost/latency to a raised error (SG-062).

    The usage is carried EXACTLY as the body delivered it — never recomputed or
    rounded here; the cost is the file's own `compute_cost` arithmetic, the same
    line the success path uses. A leg with no received body attaches nothing, so
    the reader records honest `0.0`/absent (the SG-030 `_write_error_ledger`
    contract is unchanged: it persists whatever the exception carries).
    """
    if usage is None:
        return
    # `ProviderError` is defined in `router.py` (outside this slice's ceiling);
    # its optional accounting carriers are attached dynamically so no second
    # copy of the exception type exists and the reader's `getattr` contract holds.
    setattr(exc, "usage", usage)
    setattr(exc, "cost", compute_cost(usage))
    if latency_ms is not None:
        setattr(exc, "latency_ms", latency_ms)


def compute_cost(usage: dict[str, Any]) -> float:
    """Computed USD for one call from the vendor rate table (off-peak rates).

    This prices what actually happened: it reads the response's real token
    counts after the call. The peak multiplier (x2 at 01:00-04:00 and
    06:00-10:00 UTC Mon-Fri) is a vendor fact recorded in the report, not a
    clock here: a time-dependent calculation would make unit tests
    date-dependent (PG-IC-07).
    """
    tokens_in = usage.get("prompt_tokens") or 0
    tokens_out = usage.get("completion_tokens") or 0
    return (tokens_in * INPUT_USD_PER_1M + tokens_out * OUTPUT_USD_PER_1M) / 1_000_000


def _log_call(
    *,
    operation: str,
    model_id: str,
    usage: dict[str, Any] | None,
    cost: float | None,
    latency_ms: float | None,
    status: str,
) -> None:
    """One INFO line per provider call: never a prompt, body, image or key."""
    tokens = usage or {}
    logger.info(
        "provider call: provider=%s model=%s operation=%s status=%s cost=%.8f "
        "input_tokens=%d output_tokens=%d latency_ms=%s",
        "opencode-go",
        model_id,
        operation,
        status,
        float(cost or 0.0),
        int(tokens.get("prompt_tokens") or 0),
        int(tokens.get("completion_tokens") or 0),
        f"{latency_ms:.1f}" if latency_ms is not None else "unknown",
    )


def build_chat_payload(model: str, prompt: str, image_b64: str) -> dict[str, Any]:
    """The exact outgoing wire shape (PG-EV-04): no key material, ever."""
    return {
        "model": model,
        "stream": False,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "response_format": response_format_for(model),
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ],
    }


def build_text_payload(model: str, prompt: str, text: str) -> dict[str, Any]:
    """The exact outgoing wire shape for a text turn (PG-EV-04).

    `prompt` is the system instruction (the versioned chat prompt); `text` is
    the user turn (the delimited catalogue data plus the question). Plain text
    content: no image part, no `response_format` (the answer is free text), and
    never any key material. `max_tokens` is `TEXT_MAX_TOKENS`, the text-turn
    bound (SG-101), never the vision `DEFAULT_MAX_TOKENS`.
    """
    return {
        "model": model,
        "stream": False,
        "max_tokens": TEXT_MAX_TOKENS,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
    }


class OpenCodeGoProvider:
    """Raw-httpx implementation of the vision and text operations.

    The recorded cost is the post-call computation of the response's real
    `usage`; no call is refused for cost.
    """

    provider_id = "opencode-go"

    def __init__(
        self,
        session_id: str,
        *,
        model_id: str = DEFAULT_MODEL_ID,
        api_key: str | None = None,
        base_url: str = BASE_URL,
        timeout_s: float = CALL_TIMEOUT_S,
    ) -> None:
        self._session_id = session_id
        self._model_id = model_id
        self._api_key = api_key
        self._base_url = base_url
        self._timeout_s = timeout_s

    def _resolve_api_key(self) -> str:
        key = self._api_key or os.environ.get("OPENCODE_API_KEY", "")
        if not key:
            raise ProviderError("missing_key", "OPENCODE_API_KEY not present in backend env")
        return key

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = build_identity_headers(self._session_id)
        headers["Authorization"] = f"Bearer {self._resolve_api_key()}"
        try:
            with httpx.Client(timeout=httpx.Timeout(self._timeout_s)) as client:
                response = client.post(self._base_url + CHAT_PATH, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise ProviderError(
                "transport", f"provider transport failure: {type(exc).__name__}"
            ) from exc
        if response.status_code != 200:
            raise ProviderError(
                "http_status",
                f"provider returned HTTP {response.status_code}: {response.text[:300]!r}",
            )
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderError("invalid_json", "provider 200 with a non-JSON body") from exc
        if not isinstance(body, dict):
            raise ProviderError("invalid_json", "provider 200 with a non-object body")
        return body

    def extract_items(self, image_bytes: bytes, prompt: str) -> ProviderResult:
        """Vision turn on the real adapter: one call, one actual-cost result."""
        redacted = redact_image(image_bytes)
        image_b64 = base64.b64encode(redacted).decode("ascii")
        payload = build_chat_payload(self._model_id, prompt, image_b64)
        started = time.monotonic()
        usage: dict[str, Any] | None = None
        try:
            body = self._post(payload)
            latency_ms = (time.monotonic() - started) * 1000.0
            usage = guard_usage(body.get("usage") or {})
            choices = body.get("choices") or []
            if not isinstance(choices, list) or not choices:
                exc = ProviderError("invalid_json", "provider 200 with no choices")
                attach_body_accounting(exc, usage, latency_ms=latency_ms)
                raise exc
            message = choices[0].get("message") or {}
            content = strip_single_think(guard_content(message.get("content")))
            parsed = parse_extraction_output(content)
            cost = compute_cost(usage)
            result = ProviderResult(
                normalized_output=parsed.model_dump(),
                raw_payload=body,
                request_id=str(body.get("id") or ""),
                usage=usage,
                cost=cost,
                model_id=str(body.get("model") or self._model_id),
                latency_ms=latency_ms,
            )
        except Exception as exc:
            error_latency = getattr(exc, "latency_ms", None)
            if error_latency is None:
                error_latency = (time.monotonic() - started) * 1000.0
            _log_call(
                operation="extract_items",
                model_id=self._model_id,
                usage=getattr(exc, "usage", usage),
                cost=getattr(exc, "cost", None),
                latency_ms=error_latency,
                status="failed",
            )
            raise
        _log_call(
            operation="extract_items",
            model_id=result.model_id,
            usage=result.usage,
            cost=result.cost,
            latency_ms=result.latency_ms,
            status="ok",
        )
        return result

    def extract_text(self, text: str, prompt: str) -> ProviderResult:
        """Text turn on the real adapter: one call, one actual-cost result.

        No image, no base64, no `parse_extraction_output`: the normalized output
        is the answer text plus the response metadata (`model`, `finish_reason`).
        """
        payload = build_text_payload(self._model_id, prompt, text)
        started = time.monotonic()
        usage: dict[str, Any] | None = None
        try:
            body = self._post(payload)
            latency_ms = (time.monotonic() - started) * 1000.0
            usage = guard_usage(body.get("usage") or {})
            choices = body.get("choices") or []
            if not isinstance(choices, list) or not choices:
                exc = ProviderError("invalid_json", "provider 200 with no choices")
                attach_body_accounting(exc, usage, latency_ms=latency_ms)
                raise exc
            choice = choices[0]
            message = choice.get("message") or {}
            try:
                content = strip_single_think(guard_content(message.get("content")))
            except ProviderError as exc:
                # SG-101: a content-shape rejection AFTER a completed 200 body is
                # a billed leg (SG-099's empty-200 spent reasoning tokens,
                # `content` empty). Attach what crossed the wire, exactly like
                # the no-choices leg above, so `reader._write_error_ledger`
                # records it.
                attach_body_accounting(exc, usage, latency_ms=latency_ms)
                raise
            model_id = str(body.get("model") or self._model_id)
            cost = compute_cost(usage)
            result = ProviderResult(
                normalized_output={
                    "text": content,
                    "model": model_id,
                    "finish_reason": choice.get("finish_reason"),
                },
                raw_payload=body,
                request_id=str(body.get("id") or ""),
                usage=usage,
                cost=cost,
                model_id=model_id,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            error_latency = getattr(exc, "latency_ms", None)
            if error_latency is None:
                error_latency = (time.monotonic() - started) * 1000.0
            _log_call(
                operation="extract_text",
                model_id=self._model_id,
                usage=getattr(exc, "usage", usage),
                cost=getattr(exc, "cost", None),
                latency_ms=error_latency,
                status="failed",
            )
            raise
        _log_call(
            operation="extract_text",
            model_id=result.model_id,
            usage=result.usage,
            cost=result.cost,
            latency_ms=result.latency_ms,
            status="ok",
        )
        return result
