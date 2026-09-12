# SG-028 — Pipeline wiring: `ANALYZING_WITH_AI` runs for real (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 2 Slice 4 under D35 L3. SG-025 (seam) / SG-026 (schemas+eval baseline) / SG-027 (GO adapter, work `0be0315`) landed 98. Plan: `docs/superpowers/plans/2026-09-11-phase-2-ai-extraction.md` Slice 4; blueprint §5.1 (8 states, `ANALYZING_WITH_AI` + `BUILDING_CANDIDATES` between signals and dedup), §5.2-5..7 (formation/dedup/gating), §5.3 (AI gate: repair once then fail step), §9.3 (never a guessed expiry), §11.3 (review shows confidence + source). Forks binding (dispute is a STOP): GO on its own subscription (Q1) · spend uncapped-but-ledgered (F2 — **zero spend this slice, fake only**) · GPS-default-strip (F3) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration in this slice** — `assertion.model_json` already exists (verify in G0); a `-1` that would unwind `sg025` is a STOP.
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-03` stop-is-BLOCKED-commit · `PG-EV-04` shape-of-what-is-sent · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, fixture legs 600s. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed. NETWORK: none — this slice is fake/offline by construction; any provider HTTP attempt is a STOP** (`PG-PR-04`: proof is in-process tests only; zero live calls; spend $0).

## Why this exists

The seam (SG-025), schemas (SG-026) and the one cloud adapter (SG-027) exist as code, but the pipeline never calls them: `STEP_NAMES` has six deterministic steps and no AI state exists anywhere in `backend/` (grep-verified). This slice wires extraction into the job pipeline: `ANALYZING_WITH_AI` (provider call → strict validation → ledger) and `BUILDING_CANDIDATES` (signals + AI → candidate with per-field provenance), then the gating/correction rules that make AI output auditable rather than trusted. Default posture is unchanged: with the shipped defaults (`sg_provider_id="fake"`, `sg_consent=False`) the steps skip and the Phase-1 deterministic behavior is byte-for-byte what it was.

## G0 — verify premises before building (read + quote; differences = findings)

- Tree clean (`git status --porcelain` quoted); suite BASELINE from `backend/` (bound 600s): known base-proved reds = 2 decoder env legs + the 2 config-reload pollution reds (base-proved in SG-027; cite the base run, not this packet).
- Read and quote: `job_service.py` (`STEP_NAMES`, `execute_step`, `run_job`, the AWAITING_REVIEW resume); `dedup.py` (candidate creation + the early-return reuse path around `:102-104`); `candidates.py` (commit gating sets + hardcoded `source_type="deterministic"` around `:76-91`); `api/v1/candidates.py` (decision path); providers (`protocols.py`, `router.py`, `fake.py` — its `extract_items` returns a shape that `parse_extraction_output` REJECTS: no `confidence`, extra `source`; `opencode_go.py` `extract_items(image_bytes, prompt, estimated_cost=...)`); `schemas.py` (`parse_extraction_output` + `extract_with_single_repair`); `config.py` (six named settings); prompts front-matter; `CandidateCard.tsx` `fieldInfo` (`:4-14`) + `ProvenanceBadge`; `provider_call` model; `signals.py` original-file resolution; review-task resolve API; `plugins.py` manual-entry path.
- Premise frame (correct me with evidence): the AI output reader must supply BYTES + prompt (the adapter surface), not the `image_ref` the Protocol suggests — the Protocol is the seam shape, the SG-028 reader is the bridge; `commit_job_candidate` commits the FIRST candidate only; `CandidateCard` already renders per-field `{value, confidence, source_type}`; the fake's raw output must never reach `parse_extraction_output`/candidates as-is.

## G1 — the two steps (job_service.py)

- Insert `ANALYZING_WITH_AI` + `BUILDING_CANDIDATES` in blueprint §5.1 order (between `EXTRACTING_DETERMINISTIC_SIGNALS` and `DEDUPLICATING`); `STEP_NAMES` updated; resume/retry semantics preserved (a FAILED AI step retries via existing `retry_job`; no partial state).
- **Default OFF:** provider id not configured for real OR consent false → step output `{"status": "skipped", "reason": ...}`, zero provider calls, zero ledger rows, zero AI fields — default pipeline equals Phase-1 behavior (prove it; goldens updated only for step list/counters).
- **Enabled path (tests):** per evidence — resolve the immutable original the way `signals.py` does; redact via the SHARED `redact_image` (GPS never leaves; same function, no copy); build the prompt from the versioned prompt file (food v1 default; medicine selectable behind ≤1 named setting); call through the SG-025 router (budget refusal BEFORE any call; fallback semantics untouched); validate via `parse_extraction_output` through `extract_with_single_repair` (exactly one repair, then the STEP FAILS — never a silent skip, §5.3); write ONE `provider_call` ledger row per call (provider, model, prompt_template_version, input hashes, output payload, cost, usage, latency, error state, `job_id`); keep the validated output for the next step.
- **Injectability:** tests run fully offline with a schema-valid scripted provider (a schema-valid mode/injection in `fake.py` is allowed if cleanest — report it). ONE named seam, documented.
- **BUILDING_CANDIDATES:** deterministic fields merged with AI output (first item → `display_name`, expiry fields, `lot`); per-field provenance carried in the SAME object shape `CandidateCard.fieldInfo` already renders — `{"value", "confidence", "source_type", "provider", "model", "prompt_template_version", "provider_call_id"}` — no parallel structure, no reshaping. ALL items + `unknowns` preserved in the proposal; >1 item → blocking review task (existing resolve API is the resolution path; no split UI, no auto-split) — a scope decision, report it.
- **Gating (§5.2-7):** `identifier`, `expiry`, `expiry_date`, `condition`, `lot` route to review ALWAYS (`proposed`, any confidence); other fields auto-accept only at/above ONE named threshold setting (env-overridable; conservative default; docstring marked uncalibrated per `G-A9`). No silent auto-accept of a gated field — negative tests.
- **Dedup reconciliation:** a candidate created by `BUILDING_CANDIDATES` must still receive dedup matches (reconcile the early-return reuse path; matches semantics unchanged; mechanism yours).
- **`needs_evidence`:** no expiry value derived; the manual-entry path stays §9.3-faithful (same task kinds the SG-026 bridge uses; never a guessed date).

## G2 — provenance and corrections (candidates.py, assertion_service.py)

- Commit derives each assertion's `source_type` from field provenance (`"extraction"` for AI, `"deterministic"` otherwise) and writes the `model_json` envelope {provider, model, prompt_template_version, provider_call_id, evidence/observation ids}. **No migration** — the column exists.
- User corrections supersede + write a new `accepted` assertion, never overwrite (extend existing upsert semantics where a path bypasses them); audit trail proven by test.

## G3 — review workspace: ZERO change expected

`fieldInfo` + `ProvenanceBadge` already exist (G-A10: the renderer was found before designing one). Verify by reading; only if a REAL gap forces it: minimal change + component test + quoted reason, reported. No redesign.

## G4 — tests + carried fixes

- NEW `backend/tests/test_ai_pipeline.py` (offline, fake only): (1) low-risk fields auto-accept at/above the threshold; (2) expiry always `proposed` — negative test: no accepted expiry without a user decision; (3) `needs_evidence` → no expiry value + open manual-entry task + unknowns honored; (4) correction chain: `superseded` + new `accepted` + audit rows; (5) default config = Phase-1 behavior (skip, no ledger rows); (6) multi-item: all preserved + blocking task; resolve → accept → commit works; (7) one `provider_call` row per AI call with the §3.3 fields + `job_id`; (8) no-network: zero HTTP attempts, and a real provider id without consent SKIPS rather than calls.
- Goldens (expected, named): `test_import_jobs.py:95`, `test_phase1_e2e.py:190,226` — update step list/counters, keep the assertions meaningful.
- Carried fixes: `schemas.py` docstring clause "(or the original non-retryable error)" is wrong (always `ExtractionFailedError`, chained) — fix the one line; `test_opencode_go.py` `test_config_readback_new_values` reload pollution — make it leak-free; proof = the two previously-polluted migration tests green in a plain full-suite run from `backend/` (residual = finding).
- FAIL-then-PASS (`PG-EV-01`/`PG-EV-09`): new tests PRE-FAIL raw + POST-green raw both committed in the verify log. Full suite from `backend/` (bound 600s); `ruff` clean; `mypy` quoted; read-back (`PG-SC-02`) of every new setting + the serialized step list.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-028.log`, `{{WORKLOG_DIR}}/SG-028_report.md`, `{{WORKLOG_DIR}}/SG-028_verify.log` (both-runs raw). First token `SG-028`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0 — no calls); live-state ledger; three UNCLEAR lines.

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-028 | Report: docs/worklogs/SG-028_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP (never force-replace); final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `job_service.py` · `candidates.py` · `assertion_service.py` · `config.py` (≤2 named settings) · `schemas.py` (docstring line only) · `fake.py` (only if the schema-valid test mode lands there — small, reported) · ONE optional new module under `services/providers/` (reader bridge; quoted reason if added) · frontend ONLY if G3 proves a real gap (minimal + component test) · tests (new file + named goldens + pollution fix) · `docs/worklogs` (3 files). **Anything else is a STOP. No migration. No prompt tuning. No second category beyond Food/Medicine. No Phase 3 agents.**
- Money/privacy: zero spend (fake only; any network = STOP). Secrets: names and counts only (`CO-44`); key never read, never logged.
- Cross-product (`PG-IC-01`): G0 only reads; G1 needs the G0-quoted adapter surface; G4 only fixtures + fakes. Recorded once.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s fixture legs, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): verify before asserting; no new checklists; reuse the renderer, the ledger, the bridge, the repair helper.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every G0 premise re-verified in-slice with quoted reads; differences reported as findings.
- Steps exist in blueprint order; default-off path proved (no call/no ledger row/no AI field); enabled path runs offline end-to-end on the scripted provider with exactly one repair max (§5.3 fail-loud on second failure).
- Gating proved by negative tests (no silent auto-accept of identifier/expiry/condition/lot); provenance envelope on committed assertions (`source_type` derived, `model_json` populated); correction chain auditable (superseded + new accepted + audit rows).
- ≤1 `provider_call` ledger row per AI call, `job_id` linked; multi-item preserved + blocking task; `needs_evidence` → manual-entry task, never a guessed date.
- Goldens updated meaningfully; carried fixes done (docstring line; pollution leak-free with full-suite proof); FAIL-then-PASS both runs quoted; suite/ruff/mypy quoted; MODEL + effort provenance quoted; no vacuous pass; zero network calls proven.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger includes the spend line ($0) and the network-attempt count (0, proven).

## Budget

120s probes, 600s fixture legs, 1800s early-close, 2400s overall.
