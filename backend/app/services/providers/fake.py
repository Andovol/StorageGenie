"""Scripted provider double for contract tests (no network, no key, no SDK).

Four shapes:
- "valid": every operation returns a well-formed ProviderResult.
- "invalid_json_once": the first call raises non-retryable `invalid_json`,
  every later call returns valid (invalid-JSON-once-then-valid).
- "needs_evidence": `extract_items` reports `needs_evidence=True`.
- "outage_retryable": every call raises retryable `outage`.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.services.providers.protocols import ProviderResult
from app.services.providers.router import ProviderError

VALID_MODES = ("valid", "invalid_json_once", "needs_evidence", "outage_retryable")


class FakeProvider:
    """In-process double implementing all four provider protocols."""

    def __init__(self, mode: str, provider_id: str, model_id: str = "fake-model-1") -> None:
        if mode not in VALID_MODES:
            raise ValueError(f"unknown fake mode: {mode}")
        self.mode = mode
        self.provider_id = provider_id
        self.model_id = model_id
        self.invocations = 0
        self._flaky_fired = False

    def _behave(self, operation: str, normalized: dict[str, Any]) -> ProviderResult:
        self.invocations += 1
        if self.mode == "outage_retryable":
            raise ProviderError("outage", f"fake outage on {operation}")
        if self.mode == "invalid_json_once" and not self._flaky_fired:
            self._flaky_fired = True
            raise ProviderError("invalid_json", f"fake invalid JSON on {operation}")
        return ProviderResult(
            normalized_output=normalized,
            raw_payload={"fake": True, "operation": operation, "mode": self.mode},
            request_id=str(uuid.uuid4()),
            usage={"prompt_tokens": 10, "completion_tokens": 5},
            cost=0.01,
            model_id=self.model_id,
            latency_ms=1.5,
        )

    def extract_items(self, image_ref: str) -> ProviderResult:
        if self.mode == "needs_evidence":
            return self._behave(operation="extract_items", normalized={"needs_evidence": True, "items": []})
        return self._behave(
            operation="extract_items",
            normalized={"needs_evidence": False, "items": [{"name": "fake-item", "source": image_ref}]},
        )

    def extract_text(self, image_ref: str) -> ProviderResult:
        return self._behave(operation="extract_text", normalized={"text": "fake-text", "source": image_ref})

    def embed(self, text: str) -> ProviderResult:
        return self._behave(operation="embed", normalized={"vector": [0.1, 0.2, 0.3], "source": text})

    def search_and_summarize(self, query: str) -> ProviderResult:
        return self._behave(
            operation="search_and_summarize",
            normalized={"summary": "fake-summary", "sources": [], "query": query},
        )
