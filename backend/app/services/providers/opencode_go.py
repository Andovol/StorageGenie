"""OpenCode GO vision adapter (SG-027) — raw httpx, no vendor SDK.

Facts below are the G1 re-spike (attempt-2) live-verified set only; nothing is
inherited from the packet. ONE stable session id is supplied per conversation;
header VALUES are never logged, and the API key is read from the backend
environment only and never placed in a log line, payload, or repr.

F2 (owner 2026-09-11: "no caps at first, we will re-evaluate later."): the
per-job and monthly cap mechanisms ship here, but their configured defaults
are None (uncapped). A cap that binds logs by name and number only;
re-evaluation is owed.
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
from app.services.providers.router import BudgetExceededError, ProviderError
from app.services.providers.schemas import parse_extraction_output

logger = logging.getLogger(__name__)

BASE_URL = "https://opencode.ai/zen/go/v1"
CHAT_PATH = "/chat/completions"
DEFAULT_MODEL_ID = "deepseek-v4-flash-vision-exp"
USER_AGENT = "StorageGenie/0.1 (opencode-go vision adapter)"
DEFAULT_MAX_TOKENS = 2000
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
    """Empty/blank 200 bodies are rejected before any parsing."""
    if content is None or not content.strip():
        raise ProviderError("invalid_json", "provider returned empty content (empty-200 reject)")
    return content


def guard_usage(usage: dict[str, Any]) -> dict[str, Any]:
    """A 200 without non-zero usage proves nothing and is rejected."""
    total = usage.get("total_tokens") or 0
    if not total:
        total = (usage.get("prompt_tokens") or 0) + (usage.get("completion_tokens") or 0)
    if not total:
        raise ProviderError("invalid_json", "provider returned zero or absent usage tokens")
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


def compute_cost(usage: dict[str, Any]) -> float:
    """Computed USD for one call from the vendor rate table (off-peak rates).

    The peak multiplier (x2 at 01:00-04:00 and 06:00-10:00 UTC Mon-Fri) is a
    vendor fact recorded in the report, not a clock here: a time-dependent
    calculation would make unit tests date-dependent (PG-IC-07).
    """
    tokens_in = usage.get("prompt_tokens") or 0
    tokens_out = usage.get("completion_tokens") or 0
    return (tokens_in * INPUT_USD_PER_1M + tokens_out * OUTPUT_USD_PER_1M) / 1_000_000


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


class OpenCodeGoProvider:
    """Raw-httpx implementation of the vision extraction operation.

    `extract_items(image_bytes, prompt, estimated_cost=...)` is the SG-027
    surface; the SG-028 pipeline reader wires it to the provider protocol.
    """

    provider_id = "opencode-go"

    def __init__(
        self,
        session_id: str,
        *,
        model_id: str = DEFAULT_MODEL_ID,
        api_key: str | None = None,
        per_job_cap: float | None = None,
        monthly_cap: float | None = None,
        base_url: str = BASE_URL,
        timeout_s: float = CALL_TIMEOUT_S,
    ) -> None:
        self._session_id = session_id
        self._model_id = model_id
        self._api_key = api_key
        self._per_job_cap = per_job_cap
        self._monthly_cap = monthly_cap
        self._monthly_spent = 0.0
        self._base_url = base_url
        self._timeout_s = timeout_s
        logger.info(
            "opencode-go bound: model=%s per_job_cap=%s monthly_cap=%s",
            self._model_id,
            "uncapped" if per_job_cap is None else per_job_cap,
            "uncapped" if monthly_cap is None else monthly_cap,
        )

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

    def extract_items(
        self,
        image_bytes: bytes,
        prompt: str,
        *,
        estimated_cost: float = 0.0,
    ) -> ProviderResult:
        if self._per_job_cap is not None and estimated_cost > self._per_job_cap:
            raise BudgetExceededError(
                f"estimated cost {estimated_cost} exceeds per-job cap {self._per_job_cap}"
            )
        if (
            self._monthly_cap is not None
            and self._monthly_spent + estimated_cost > self._monthly_cap
        ):
            raise BudgetExceededError(
                f"estimated cost {estimated_cost} exceeds remaining monthly budget "
                f"({self._monthly_spent} spent of {self._monthly_cap})"
            )
        redacted = redact_image(image_bytes)
        image_b64 = base64.b64encode(redacted).decode("ascii")
        payload = build_chat_payload(self._model_id, prompt, image_b64)
        started = time.monotonic()
        body = self._post(payload)
        latency_ms = (time.monotonic() - started) * 1000.0
        usage = guard_usage(body.get("usage") or {})
        choices = body.get("choices") or []
        if not isinstance(choices, list) or not choices:
            raise ProviderError("invalid_json", "provider 200 with no choices")
        message = choices[0].get("message") or {}
        content = strip_single_think(guard_content(message.get("content")))
        parsed = parse_extraction_output(content)
        cost = compute_cost(usage)
        self._monthly_spent += cost
        return ProviderResult(
            normalized_output=parsed.model_dump(),
            raw_payload=body,
            request_id=str(body.get("id") or ""),
            usage=usage,
            cost=cost,
            model_id=str(body.get("model") or self._model_id),
            latency_ms=latency_ms,
        )
