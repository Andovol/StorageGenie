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
from copy import deepcopy
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

    def extract_items(
        self,
        image_bytes: bytes,
        prompt: str,
        *,
        estimated_cost: float = 0.0,
    ) -> ProviderResult:
        if self.mode == "needs_evidence":
            return self._behave(operation="extract_items", normalized={"needs_evidence": True, "items": []})
        return self._behave(
            operation="extract_items",
            normalized={"needs_evidence": False, "items": [{"name": "fake-item", "source": image_bytes}]},
        )

    def extract_text(
        self, text: str, prompt: str = "", *, estimated_cost: float = 0.0
    ) -> ProviderResult:
        """Scripted text response (SG-038 G1): no network, no key, cost fixed."""
        return self._behave(operation="extract_text", normalized={"text": "fake-text", "source": text})

    def embed(self, text: str) -> ProviderResult:
        return self._behave(operation="embed", normalized={"vector": [0.1, 0.2, 0.3], "source": text})

    def search_and_summarize(self, query: str) -> ProviderResult:
        return self._behave(
            operation="search_and_summarize",
            normalized={"summary": "fake-summary", "sources": [], "query": query},
        )


class ScriptedProvider:
    """Schema-valid scripted vision provider for offline pipeline tests (SG-028).

    The SG-027 `FakeProvider` deliberately returns a non-schema shape (no
    `confidence`, extra `source`) so the strict reader REJECTS it; the pipeline
    tests need the opposite — a provider whose payload already validates — so
    this class returns a caller-supplied `ExtractionOutput`-shaped dict and
    records the exact bytes/prompts it was handed (PG-EV-04). `fail_times` makes
    the first N invocations raise a retryable `invalid_json`, exercising the
    single-repair policy. No network, no key, cost 0.0.
    """

    def __init__(
        self,
        *,
        provider_id: str,
        payload: dict[str, Any],
        model_id: str = "scripted-model-1",
        fail_times: int = 0,
    ) -> None:
        self.provider_id = provider_id
        self.model_id = model_id
        self.payload = payload
        self.fail_times = fail_times
        self.invocations = 0
        self.images: list[bytes] = []
        self.prompts: list[str] = []

    def extract_items(
        self,
        image_bytes: bytes,
        prompt: str,
        *,
        estimated_cost: float = 0.0,
    ) -> ProviderResult:
        self.invocations += 1
        self.images.append(image_bytes)
        self.prompts.append(prompt)
        if self.invocations <= self.fail_times:
            raise ProviderError("invalid_json", f"scripted invalid_json on attempt {self.invocations}")
        return ProviderResult(
            normalized_output=deepcopy(self.payload),
            raw_payload={"scripted": True, "provider_id": self.provider_id},
            request_id=str(uuid.uuid4()),
            usage={"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18},
            cost=0.0,
            model_id=self.model_id,
            latency_ms=1.25,
        )
