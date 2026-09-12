# ADR-004: Provider abstraction (capability interfaces, raw retention, config routing)

- Status: accepted for Phase 2
- Date: 2026-09-12
- Slice: SG-025

## Decision

All AI capability calls go through capability interfaces, never through a
concrete SDK at the call site. The four interfaces are `VisionExtractionProvider`
(`extract_items`), `OcrProvider` (`extract_text`), `EmbeddingProvider` (`embed`),
and `WebEnrichmentProvider` (`search_and_summarize`), defined in
`backend/app/services/providers/protocols.py`. Every result carries the §3.3
envelope: normalized output plus raw provider payload, request id,
usage/cost, model id, and latency — the raw response is always retained in
the ledger, never discarded.

Routing and fallback are configuration, not code: `RouterConfig` carries the
provider id, fallback id, JSON-strictness flag, per-job cost budget, and the
retryable-error set. The router never quality-ranks providers. The fallback
fires on retryable errors ONLY; non-retryable errors surface with no
fallback. A per-job cost budget refuses BEFORE any provider call, with zero
invocations on refusal.

## Existing pins

- `backend/app/services/providers/protocols.py` — four Protocols plus the
  `ProviderResult` envelope (sync by design: the service layer is fully
  synchronous; revisit if a real adapter needs async).
- `backend/app/services/providers/router.py` — `ProviderRouter.execute`
  (budget-first, retryable-only fallback), `RouterConfig`, `ProviderError`
  (machine-readable `kind`), `BudgetExceededError`, `ProviderNotFoundError`.
- `backend/app/services/providers/fake.py` — scripted double with four
  shapes: valid / invalid-JSON-once-then-valid / needs_evidence /
  outage-raises-retryable. No real SDK, no key read, no network anywhere
  under `providers/` (grep-gated per `PG-SC-05`).
- `backend/tests/test_provider_gateway.py` — contract tests proving
  configured-provider selection, retryable-only fallback, pre-call budget
  refusal, and all four fake shapes.

## Consequences

SG-027 (vision spike) and later slices add real adapters behind these same
interfaces. No call site may import a provider SDK directly; violations are
defects with a destination, not style notes.
