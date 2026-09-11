# Phase 2 — AI extraction, Food + Medicine (slice plan)

**Basis:** blueprint v3 §14 (Phase 2), §6 (provider abstraction), §13 (evaluation), §10 (guardrails);
accepted register (`docs/decisions/2026-09-03-accepted-optimizations.md` — UV-3/UV-6 rejected, all else carried);
ADRs 001/002/003/005/006/008/009. **Missing and owned by this stage:** ADR-004 (provider abstraction),
ADR-007 (privacy/external-AI handling), ADR-010 (guardrail rollout tracking) — SG-018 explicitly deferred
them to the Phase 2 door. **Zero provider/LLM code exists** (verified 2026-09-11: no gateway, adapter, prompt,
or key anywhere in `backend/`); `ANALYZING_WITH_AI` is a pipeline state awaiting its worker.
**Landscape note (§2):** adapters ride the provider's official SDK (thin call + schema validation); the
gateway, router, call ledger, prompt files, and eval runner are in-house — no dependency beats a ledger
table and a scoring script, and none was found that does.

**Exit condition (blueprint:522):** AI proposes candidates including expiry dates for Food/Medicine;
corrections are auditable; a working expiry tracker is usable end-to-end for the two initial users.

## Slice 1 — SG-025: provider seam (ADR-004/007/010 + gateway + ledger + fake)

**Outcome:** the provider surface exists as code with zero cloud dependency; privacy and guardrail rules
are written before any image leaves the LAN.
**Files:** create `backend/app/services/providers/` (`protocols.py` — §6.1 four Protocols verbatim-shaped,
`router.py` — config-driven routing: provider, fallback, JSON-strictness, per-job cost budget, retryable
errors; never quality-ranked), `backend/app/models/provider_call.py` + migration (every call stores
provider, model, prompt-template version, input hashes, output payload, cost/usage, latency, error state —
§3.3); `backend/app/services/providers/fake.py` (scripted test double: valid / invalid-JSON-once /
needs_evidence / outage shapes); `backend/tests/test_provider_gateway.py` (router picks config, fallback
fires on retryable error, ledger row written per call, budget exceeded refuses BEFORE the call).
**Out of scope:** any real SDK, key, network call, prompt content, pipeline wiring.
**Tests:** gateway contract tests green against the fake in all four shapes; ledger migration applies/rolls
back; no secret material anywhere in tree or logs (grep-gated).
**Deliverables:** ADR-004, ADR-007, ADR-010 (all three — no implementation without them).

## Slice 2 — SG-026: prompts, schemas, fallback, eval scaffolding (fake only)

**Outcome:** extraction is strict structured output on versioned files; `needs_evidence` reaches the
existing manual-entry flow; the eval runner exists before any prompt is tuned (§13: corpus before
optimization).
**Files:** create `backend/app/services/providers/prompts/` (`extract-food-v1.*`, `extract-medicine-v1.*`,
plugin fragment hooks per §8 — versioned, never edited in place); `backend/app/services/providers/schemas.py`
(Pydantic: items, unknowns array REQUIRED, per-assertion confidence + uncertainty reasons; free-form prose
never parsed); wire `needs_evidence` → existing manual-entry review task; create `backend/eval/`
(corpus dir + `run.py` scoring field accuracy vs ground truth JSON, incl. expected-unknown cases; correction
rate from `audit_event`); `backend/tests/test_extraction_contract.py` (schema rejects prose, unknowns
honored, repair-prompt retried exactly once per §5.3 then step fails).
**Out of scope:** real provider, pipeline wiring, UI changes, prompt tuning (scores are baselines, not targets).
**Tests:** contract tests green on the fake; eval runner scores a 5-fixture smoke corpus and prints the baseline.
**Deliverable:** eval baseline number recorded (single-run honesty, `G-A3`).

## Slice 3 — SG-027: the one cloud adapter (owner forks F1–F3 gate it)

**Outcome:** exactly one provider answers real calls with keys, budget, and privacy controls enforced in code.
**Files:** modify `backend/app/services/providers/` (new `<provider>.py` adapter: SDK call, JSON repair
attempt, usage/cost capture, timeouts named); `backend/app/config.py` (named settings: provider id, key
source = backend env ONLY, per-job cost cap, monthly cap, consent flag — all env-overridable, logged when
they bind, `413`/`422` on breach per cap policy); `.env.example` (key names, never values); redaction helper
(EXIF-GPS never leaves the box unless ADR-007 consent says so — default strips); `backend/tests/`
(adapter tests against recorded fixtures, NEVER live; one live smoke test marked to run only with an
explicit env flag, cost printed).
**Out of scope:** second provider/fallback (Phase 4), router auto-switching on quality, any UI.
**Tests:** fixture tests green offline; live smoke runs once with owner watching (cost quoted in the report).
**Deliverable:** live smoke receipt (model id, latency, cost) + budget/refusal proof.

## Slice 4 — SG-028: pipeline wiring (AI step → candidates → review)

**Outcome:** `ANALYZING_WITH_AI` runs for real: deterministic signals + AI output become candidates with
assertion provenance, confidence gates route per §5.2 steps 4–7, corrections supersede auditably.
**Files:** modify `backend/app/services/job_service.py` (AI step: signals in, extraction call, schema
validate, candidate formation per §5.2-5, dedup per §5.2-6, gating per §5.2-7 — identifiers/price/expiry/
condition to review BY DEFAULT); `backend/app/services/assertion_service.py` (AI assertions carry
provider/model/prompt-version/observation links; user correction writes `superseded` + new `accepted`,
never overwrites); review workspace shows AI fields with confidence + source (minimal template change);
`backend/tests/test_ai_pipeline.py` (fake provider: low-risk auto-accept under threshold, expiry always
routed to review, correction chain auditable).
**Out of scope:** prompt tuning, second category beyond Food/Medicine fragments, chat/planning agents (Phase 3).
**Tests:** pipeline tests green on the fake; no silent auto-accept of a gated field (negative tests).

## Slice 5 — SG-029: Food/Medicine eval corpus + baseline

**Outcome:** a curated corpus with ground truth; the first measured extraction numbers; prompt v1 frozen or
v2 cut with a recorded reason.
**Files:** create `backend/eval/corpus/` (Food + Medicine images: clean, glare, clutter, partial labels,
no-date-visible cases with ground-truth JSON incl. `needs_evidence` expectations); extend `backend/eval/run.py`
(correction-rate tracking); run against the ONE adapter (metered, budgeted); `backend/tests/` asserts
corpus integrity (every fixture has ground truth; every ground truth has an expectation class).
**Out of scope:** optimizing past the baseline (that is Phase-3-plus work with the corpus as guard);
non-Latin stress beyond 2 fixtures (recorded follow-up).
**Tests:** corpus integrity green; baseline run completes inside budget with numbers quoted (accuracy,
unknown-rate, correction rate) — no tuning in this slice.
**Deliverable:** baseline report committed under `backend/eval/`.

## Slice 6 — SG-030: Phase 2 exit E2E + runbook + close-out

**Outcome:** the blueprint:522 exit proved in one fixture; docs match the tree; stage closes cleanly.
**Files:** create `backend/tests/test_phase2_e2e.py` (Food + Medicine images → import → AI candidates with
expiry assertions → `needs_evidence` case → manual entry → accept commits asset+assertions+audit atomically →
correction supersedes auditably → provider_call rows exist per AI call with cost); extend `README.md`
(Phase 2 runbook: provider setup, key placement, budgets, eval commands, consent switches); ADR amendments
only as promised; no migration unless a slice left one explicitly open.
**Also:** full suite + ruff + mypy quoted; explicit non-goals ledger for the Phase 3 door.
**Close-out:** stage exit verdict against blueprint:522; L3 ends; Phase 3 proposal goes to owner as the next
decision — never auto-chained.

## Slice order and IDs

SG-025 → SG-026 → SG-027 → SG-028 → SG-029 → SG-030. Six slices, each one dispatch. Reordering past a hard
stop is forbidden. **F1–F3 must arrive before SG-027 fires** (no key, no spend, no cloud photo without them);
SG-025/026 run on the fake and need no fork answered.

## Owner forks (all answered before they bind — none auto-decided)

- **F1 — which cloud vision provider?** Money + privacy + lock-in in one choice. One adapter ships in SG-027.
- **F2 — spend caps?** Per-job and monthly numbers (a bare number is unauditable — caps live in config with units).
- **F3 — photo consent?** Both household users explicitly in; redaction posture per ADR-007 (default: GPS never leaves).
- **F4 — guardrail stage confirmed at Stage 0** (blueprint:410 — confirm, not re-decide; human confirmation mandatory regardless).
- **F5 — L3 grant for the next-session arc** under D34 bounds (opencode, one retry per slice, hard stops: BLOCKED/STOP, score <95, any new provider/privacy/money fork, any sensitive-surface touch).
