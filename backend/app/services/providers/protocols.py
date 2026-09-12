"""Provider capability interfaces (ADR-004).

Sync by design: the existing service layer (`app/services/`) is fully
synchronous and the Fake double plus the Phase 2 callers run in-process.
Async would add machinery with no caller. Revisit if a real adapter needs it.

Every result carries the §3.3 ledger envelope: normalized output plus the
raw provider payload, request id, usage/cost, model id, and latency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ProviderResult:
    normalized_output: dict[str, Any]
    raw_payload: dict[str, Any]
    request_id: str
    usage: dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    model_id: str = ""
    latency_ms: float = 0.0


class VisionExtractionProvider(Protocol):
    def extract_items(self, image_ref: str) -> ProviderResult:
        """Extract structured catalog items from an image reference."""
        ...


class OcrProvider(Protocol):
    def extract_text(self, image_ref: str) -> ProviderResult:
        """Extract text (plus layout metadata) from an image reference."""
        ...


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> ProviderResult:
        """Embed text; normalized output carries the vector."""
        ...


class WebEnrichmentProvider(Protocol):
    def search_and_summarize(self, query: str) -> ProviderResult:
        """Search the web and return a summary plus sources."""
        ...
