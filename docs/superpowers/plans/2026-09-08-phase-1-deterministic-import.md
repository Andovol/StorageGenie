# Phase 1 — Deterministic import + Expiry Tracker skeleton (slice plan)

**Date:** 2026-09-08 · **Stage autonomy:** L3 (D8) — this plan is the single stage-scope approval; slices then sequence without per-slice check-ins · **Coder:** codex high (`m0106`, D8) · **Blueprint:** `inception/generic_asset_catalog_expiry_tracker_blueprint.md` v3 §5/§7/§8/§9/§11, Phase 1 exit blueprint:506-513.
**Carries:** BM-4 (Postgres-dialect CI check), UV-2 (FTS5 → Phase 1) per `docs/decisions/2026-09-03-accepted-optimizations.md:14,23,44`.
**Lifts:** D8 deterministic-import lift — OCR/barcode/EXIF/expiry-manual-entry allowed. **LLM banned until Phase 2** (blueprint:513); no provider keys, no AI endpoints, no Phase 2/3 agents/chat/planning.
**Standing slice discipline (every slice):** TDD fail-first; full `pytest` non-vacuous + `ruff` clean + `mypy` advisory count quoted; max one Alembic revision per slice (BM-5); temp-path fixtures only; zero prod writes/restarts/secrets/infra; `SG-<nnn>.log` + `docs/worklogs/SG-<nnn>_report.md` unconditional; audit + rate after each receipt.

**Execution model (fixed for the stage):** synchronous in-request step runner, no worker process — modular monolith per blueprint Risks ("split only under evidence"); durable `job`/`job_step` rows (`backend/app/models/job.py:8-32`) make resume/retry possible without infrastructure. If a slice proves this inadequate, that is a finding with ADR-003 amendment, not a silent redesign.

## Slice 1 — SG-012: Job engine core (durable state + run + retry)

**Outcome:** import jobs run deterministically through persisted steps and resume after failure.
**Files:** create `backend/app/services/job_service.py`, `backend/tests/test_import_jobs.py`; modify `backend/app/api/v1/jobs.py`, `backend/app/main.py` (mount imports router or extend jobs router — slice chooses, records why); at most one new migration (only if `job`/`job_step` need columns, e.g. error text — assess first, existing `JobStep.attempts/input_refs/output_refs` may suffice).
**Interfaces:**
- `POST /v1/imports` — create job (`job_type=import`, state `CREATED`) + link uploaded evidence ids + write step rows for the deterministic subset (`VALIDATING_INPUT → NORMALIZING → EXTRACTING_DETERMINISTIC_SIGNALS → DEDUPLICATING → AWAITING_REVIEW → COMMITTING`), idempotency-keyed.
- `POST /v1/imports/{job_id}/run` — execute pending steps inline, persisting per-step state/attempts/outputs; first failure parks the job in `FAILED` with the step error recorded, catalog untouched (commit step is atomic; §5.3 commit gate).
- `POST /v1/imports/{job_id}/retry` — reset `FAILED` steps to `RETRYING` → re-run; safe resume, no duplicate side effects.
- `GET /v1/imports/{job_id}` — job state + ordered steps + progress counts + errors.
- `GET /v1/jobs` repaired to return real items (closes review §6.1 wasted-read wart — query already computed in `jobs.py:19-36`).
**Out of scope:** signal extraction internals (stub step bodies returning `not_implemented` outputs — SG-013 fills them); candidates/decisions (SG-014); any AI step (no `ANALYZING_WITH_AI` state in Phase 1).
**Tests:** create→run green path reaches `AWAITING_REVIEW`; injected step failure → `FAILED` with catalog unchanged → retry → resumes to completion; double-`run`/`retry` idempotent; cross-household 403 on all four routes.
**Deliverable:** ADR-003 (durable DB job state, retry semantics, sync-runner choice, future queue path).

## Slice 2 — SG-013: Deterministic signal extraction (OCR, barcode/QR, EXIF, pHash)

**Outcome:** evidence files yield stored observations — text, codes, timestamps, perceptual hash — through quality-gated extractors.
**Files:** create `backend/app/services/signals.py` (+ `observations.py` if warranted), `backend/tests/test_signals.py`; modify `backend/app/api/v1/evidence.py` or job-runner wiring (fill SG-012 stub steps), `backend/pyproject.toml` + `backend/requirements.lock` + `backend/Dockerfile` (new deps only here); exactly one migration: `observation` table (`evidence_id` FK, `kind` in {ocr, barcode_qr, exif, phash}, `value_json`, `confidence`, created-at).
**Dependencies (fixed choice, simplicity per `G-A7`):** `pyzbar` (+ apt `libzbar0`) for barcode/QR with check-digit/syntax validation (EAN-13/UPC-A verified, QR syntax-checked; failures → low-confidence observation per §5.3, never an identifier); `pytesseract` (+ apt `tesseract-ocr`, eng only) for OCR text/boxes with mean-confidence; Pillow EXIF timestamps, privacy-gated behind a named setting (default off for GPS-derived fields per §12.2); hand-rolled dHash on Pillow (no new dep) for perceptual hash. TIFF input added to `allowed_mime_types`; HEIC explicitly deferred (needs `pillow-heif` + system lib — documented, not attempted).
**Out of scope:** AI vision (Phase 2); dedup policy use of these signals (SG-014 consumes them); evaluation corpus (Phase 2).
**Tests (fail-first, real files in temp paths):** generated QR + EAN-13 decode to exact values; OCR on rendered-text PNG finds the string with confidence recorded; EXIF-dated JPEG yields timestamp observation with gate off and none with gate on; dHash equal for identical bytes, near for resized copy, far for different image; corrupted/unsupported input quarantines per §5.3 (job step FAILED, quarantined state, never a crash).

## Slice 3 — SG-014: Deduplication, candidates, review decisions, lifecycle events

**Outcome:** duplicate policy enforced; candidates committed atomically through human decisions; review queue is real.
**Files:** create `backend/app/services/dedup.py`, `backend/app/services/candidates.py`, `backend/tests/test_dedup.py`, `backend/tests/test_candidates.py`; modify `backend/app/api/v1/review_tasks.py` (real items + `POST /v1/review-tasks/{task_id}/resolve`; keep `/review_tasks` alias working), job-runner `DEDUPLICATING`/`COMMITTING` steps; exactly one migration: `candidate` table (`job_id` FK, `evidence_ids_json`, `proposed_fields_json`, `state` in {proposed, accepted, edited, held, rejected}, household FK).
**Policy (ADR-006, written here):** exact SHA-256 collision → link existing evidence, never duplicate bytes; dHash distance under named threshold → `similar` candidate suggestion (advisory, never auto-merge); identifier exact match (barcode value already on another asset) → review task, never auto-merge serialized items. Commit path (§5 step 8): decision `accept`/`edit` creates asset + assertions (`source_type=deterministic`, `review_state=accepted` for machine-safe fields, `proposed` for identifiers/expiry per §5.2-7) + evidence links + initial lifecycle event **atomically**; `reject`/`hold` set state only. Minimal `POST /v1/assets/{asset_id}/events` appended here (lifecycle leg deferred since Phase 0 — blueprint §7) to record the creation event; full event history UI stays Phase 1-out.
**Out of scope:** split/merge of multi-object scenes (manual-split-required path returns a review task — blueprint §5.2-5); semantic similarity (advisory-only, Phase 2+).
**Tests:** byte-identical re-import links, no new evidence row; near-duplicate proposes suggestion; identifier collision opens review task and blocks commit; accept-commit atomicity (forced mid-commit failure rolls back, job retryable); resolve endpoint closes tasks with audit rows.

## Slice 4 — SG-015: Expiry Tracker plugin skeleton (taxonomy, profiles, manual entry)

**Outcome:** `expiry-tracker` 1.0.0 registered as a plugin; Food/Medicine categories classifiable with behavior profiles; expiry dates enter only via manual entry or not at all.
**Files:** create `backend/app/plugins/__init__.py`, `backend/app/plugins/registry.py`, `backend/app/plugins/expiry_tracker.py` (taxonomy + profiles + JSON Schemas + validators), `backend/app/api/v1/plugins.py` (namespaced `/v1/plugins/expiry-tracker/...` per blueprint:353), `backend/tests/test_plugin_expiry.py`; exactly one migration: `classification` (`asset_id` FK, `plugin_id`, `category`, `profile_json`) + extension-attribute storage (assess: reuse `assertion.value_json` with reserved `field_path` prefix vs new column — slice decides, records why).
**Content:** categories Food & beverages + Medicine/pharma first with tier defaults from blueprint §9.1 (30/7/1 + shorter windows); Cosmetics/Household/Documents structures present but inactive (no opened-date mechanic until Phase 3 — blueprint:529); date-type enum + unit enum from §9.2; `needs_evidence` fallback: no visible/legible date ⇒ `expiry_date` assertion in `needs_evidence` + review task prompting manual entry; categories without an expiry concept get **no** expiry assertion (blueprint:396, §15.2 constraint — test asserts the absence); extension attributes validated against the plugin JSON Schema on write; plugins cannot touch core fields (blueprint:370 — test attempts, fails).
**Out of scope:** expiry dashboard screen (SG-016); planning/chat/analytics agents (Phase 3); opened-date countdowns (Phase 3).
**Tests:** taxonomy resolution per category; profile tier application; schema rejection of bad extension attributes; `needs_evidence` + review-task creation on dateless import; non-perishable asset carries zero expiry assertions; core-field override attempt rejected.
**Deliverables:** ADR-005 (core/plugin contract, isolation) + ADR-009 (category/behavior-profile design, tiering).

## Slice 5 — SG-016: Inbox + review workspace UI

**Outcome:** users see imports, progress, failures, review tasks; decisions happen beside the source evidence, including manual expiry entry.
**Files:** create `frontend/src/routes/InboxPage.tsx`, `frontend/src/routes/ReviewPage.tsx`, `frontend/src/components/JobCard.tsx`, `frontend/src/components/CandidateCard.tsx`, `frontend/src/components/ExpiryEntryForm.tsx` (+ focused tests per component/route); modify `frontend/src/App.tsx` (routes), `frontend/src/api/client.ts` + `types.ts` (imports/candidates/review endpoints).
**Behaviors (§11.1-1, §11.3):** Inbox lists jobs with state/progress, failed jobs with errors + retry action, review-task queue; Review shows source evidence image beside candidate fields with confidence + extraction source per field; `Unknown` first-class (never forced, especially expiry); accept/edit/hold/reject + manual expiry-date entry with date-type selector; batch accept only for safe non-critical fields; keyboard accept/reject/prev/next.
**Out of scope:** expiry dashboard urgency view (deferred — plugin screen 7 lands when notifications exist; plan records the deferral, not a gap); capture-screen barcode-scan button wiring (CapturePage exists — wire only if zero-cost, else recorded follow-up).
**Tests:** jsdom/component — review renders evidence alongside fields; decision buttons call the right endpoints with ids from the loaded candidate (no fixed-id replay); expiry form posts manual entry and shows `needs_evidence` state before it; `tsc --noEmit` + `eslint` clean (SG-009 discipline).

## Slice 6 — SG-017: FTS5 search (UV-2) + Postgres-dialect CI check (BM-4)

**Outcome:** catalog search holds the §2.3 <300 ms target structurally; the ADR-001 migration path is CI-honest.
**Files:** modify `backend/app/api/v1/assets.py` (`q` via FTS5 with existing filters preserved), `Makefile` (new `check-postgres-dialect` target), `backend/tests/test_search.py` (extend) + new `backend/tests/test_postgres_dialect.py`; exactly one migration: FTS5 external-content table + sync triggers on `asset` (insert/update/delete), rebuildable via a named function.
**FTS5:** index `display_name` (+ category via classification join if cheap, else recorded follow-up); rank-ordered results; existing `asset_type`/`status`/`has_evidence` filters ANDed; ILIKE path retired only if FTS covers all polarities in tests — else both with a comment (honest, not clever). **BM-4:** offline `metadata.create_all` compile against the Postgres dialect, no server; SQLite-only FTS migration explicitly excluded with reason recorded in the test module docstring (FTS5 has no Postgres equivalent — ADR-008 records this); migration-path honesty for core DDL stays green in CI.
**Out of scope:** semantic/vector search (criterion only, ADR-008); pgvector; advanced filters/facets/saved searches (Phase 4 — blueprint:536).
**Tests:** 10k-asset fixture search p95 <300 ms local (names the machine, per `G-A3` single-run honesty); both-polarity filter tests stay green; FTS rebuild function verified; dialect test passes with zero server.
**Deliverable:** ADR-008 (deterministic FTS first; semantic-search criterion).

## Slice 7 — SG-018: Phase 1 exit E2E + runbook + close-out

**Outcome:** the Phase 1 exit condition proved in one fixture; docs match the tree; stage closes cleanly.
**Files:** create `backend/tests/test_phase1_e2e.py`, extend `README.md` (Phase 1 runbook section), extend `docs/adr/` only if a slice left a promised amendment; no migration; no frontend changes except test fallout repairs.
**E2E (`test_phase1_exit_condition`, single fixture, ids chained leg-to-leg — SG-010 discipline):** mixed temp folder (EXIF JPEG + QR image + EAN-13 image + plain PNG + TIFF) → `POST /v1/imports` → run → green-leg signals stored as observations → near-duplicate pair proposes suggestion → identifier collision opens review task → inject failure (e.g. quarantined file) → `FAILED` → `retry` → resumes to `AWAITING_REVIEW` → manual expiry entry resolves `needs_evidence` → accept commits asset + assertions + audit atomically → `GET /assets?q=` finds it via FTS → UV-5 duration (`job-created → asset-accepted` from `audit_event` timestamps, non-negative, ordered). Fail-first quoted, or "already passed, hardened".
**Also:** full suite + ruff + mypy counts quoted; README Phase 1 section (job run/retry commands, review flow, FTS rebuild, dialect check, data locations unchanged) verified line-by-line against the tree; explicit non-goals ledger for Phase 2 door (ADR-004/007/010 belong to Phase 2 — recorded, not written).
**Close-out:** stage exit verdict against blueprint:513 in the audit; L3 ends here; Phase 2 proposal (provider/budget/privacy choices) goes to owner as the next decision — never auto-chained (D8 rationale).

## Slice order andIDs

SG-012 → SG-013 → SG-014 → SG-015 → SG-016 → SG-017 → SG-018. Seven slices, each one dispatch. Reordering past a hard stop is forbidden; cosmetic reorder inside L3 sequencing is permitted only with nothing in flight and a recorded reason (SG-011 precedent, review §5).
