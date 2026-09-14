# SG-036 — Cosmetics category + opened-date tracking (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 Slice 5 under D46 L3. SG-035 landed (rated 98, work `f0071ba`). Plan: `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 5. **Authoring date (metadata, never a gate):** 2026-09-14. Previous slice left no open UNCLEAR (registry touch confirmed; CHECK choice folds below; mypy advisory stands).
**Money posture:** **zero live calls in this slice** — corpus integrity + offline scoring only; any network attempt is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (pydantic-only schema change — an alembic diff is a STOP); frozen prompt files (`extract-food-v1.md`, `extract-medicine-v1.md`) are read-only context, never edited; no live calls. Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable (starting a service is deploying, out of scope per the privileged-denial path below).
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-07` no-data-bar · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed. NETWORK: none** (`PG-PR-04`: proof is in-process tests + offline eval; zero live calls; spend $0).

## Why this exists

Cosmetics exists in the taxonomy as an INACTIVE Phase-3 stub (`cosmetics_personal_care`: active False, no tiers, `profile()` hardcodes `opened_date_tracking: False` in both branches — `backend/app/plugins/expiry_tracker.py:64-122`, verified 2026-09-14). No cosmetics prompt file exists (`PROMPT_FILES` maps food/medicine only — `reader.py:51-53`); the extraction schema has NO opened-date field (`ExtractionItem`: name/expiry_date/date_type/lot/confidence/uncertainty_reasons — `schemas.py:30-39`). The eval corpus covers Food/Medicine only (7 fixtures, `manifest.json` count 7). This slice activates the category end-to-end on the proven rails, offline.

## G1 — schema + prompt + activation

- `schemas.py`: add `opened_date: str | None = None` to `ExtractionItem` under the SAME ISO discipline as `expiry_date` (valid `YYYY-MM-DD`, else rejected — extend the validator pattern, do not duplicate loosely). Optional: old payloads keep parsing. Unknowns entries may name it (the validator reads `model_fields`, so it flows — prove it).
- New `extract-cosmetics-v1.md` following the food prompt shape exactly (front matter `template_version`/`category`/`output_schema`/`repair_policy`, no-inference rules, unknowns discipline, single-retry section): transcribe printed PAO/open-jar dates into `opened_date` ONLY when fully legible; partial/illegible → null + unknowns + `needs_evidence` when the category requires a date decision.
- `reader.py`: register `"cosmetics"` in `PROMPT_FILES` (that line only). `sg_prompt_category` is an unvalidated plain string (`config.py:38`) — no config change.
- `expiry_tracker.py`: activate `cosmetics_personal_care` (active True, tiers, default tier) and make `opened_date_tracking` True for cosmetics in `profile()` (both branches currently hardcode False — the flag must become per-category). Tier values are DECLARED UNCALIBRATED (`G-A9`): premise `CRITICAL 7 / URGENT 30 / UPCOMING 90` days — implement, mark uncalibrated in the report, do not tune.
- Classify path (`classify_asset`, `has_expiry` already True for cosmetics) must accept the category without a new task type — prove with a test, do not invent one.

## G2 — eval corpus + contract (offline only)

- Extend the corpus the SG-029 way (committed deterministic recipe + ground-truth JSON + manifest update): cosmetics clean (legible PAO), cosmetics no-date-visible (unknown-valid, `needs_evidence` expected), cosmetics partial-label. Ground truth authored from the recipe, never from a model.
- `PG-SC-02`: prompt file traced recipe → fixtures → offline score; corpus integrity tests extended (every fixture has ground truth with an expectation class, cosmetics included).
- Contract tests: opened-date ISO accept/reject, unknowns-may-name-opened_date, `load_prompt("cosmetics")` returns versioned text, unknown category still raises. FAIL-then-PASS raw (pre-change: no field/file — quoted, committed).
- `eval/run.py`: read-only context — touch it ONLY if cosmetics scoring needs it, else STOP (M6) rather than widening silently. No `--live` in this slice: integrity + offline scoring from committed fixtures only.

## G3 — proof

- FAIL-then-PASS raw in the verify log. Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted (touched files add zero new errors — check the file list). Secret scan 0. No frontend change (no build needed — state why: zero frontend files touched). No migration (prove `git diff --name-only -- backend/alembic` empty), no frozen-prompt diff, no ignored file staged, no network (prove it). The `test_postgres_dialect.py` registry needs NO change (no tables added — state the negative). Health probe per the standing line above.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-036.log`, `{{WORKLOG_DIR}}/SG-036_report.md`, `{{WORKLOG_DIR}}/SG-036_verify.log` (both-runs raw). First token `SG-036`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0); live-state ledger; three UNCLEAR lines. The report marks tier values and any threshold as UNCALIBRATED with the reason.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-036 | Report: docs/worklogs/SG-036_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/providers/schemas.py` (opened_date field + validator only) · `backend/app/services/providers/prompts/extract-cosmetics-v1.md` (new) · `backend/app/services/providers/reader.py` (PROMPT_FILES line only) · `backend/app/plugins/expiry_tracker.py` (activation + profile flag only) · `backend/eval/corpus/` (fixtures + manifest + recipe) · `backend/tests/test_extraction_contract.py` · `backend/tests/test_plugin_expiry.py` · `backend/tests/test_eval_corpus.py` · `docs/worklogs` (3 files). **Anything else is a STOP — including `eval/run.py` (conditional above), frozen prompts, migrations, routes, UI. No live calls.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money/privacy: zero spend; no key read; no network. Secrets: names and counts only (`CO-44`).
- Cross-product (`PG-IC-01`): G1 needs schemas + prompt + registry line + taxonomy; G2 the corpus + contract tests; G3 proves both. Timeouts are per-command-class (120/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): follow the food-prompt shape, the provider_call-adjacent field pattern, the SG-029 corpus recipe; no new machinery. CHECK-constraint question from SG-035: decide for the new tables' convention fields in SG-037 if it binds there — NOT here (no tables touched).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- `load_prompt("cosmetics")` returns versioned text; cosmetics extraction validates with opened_date honored-or-unknown (never guessed); unknown category still raises; frozen prompts byte-identical.
- Cosmetics classifies with opened-date tracking True in profile and tiers marked uncalibrated; no new task type.
- Corpus covers cosmetics (clean/no-date/partial) with recipe-authored ground truth; integrity green; offline scoring runs from committed fixtures.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; touched files add zero mypy errors; no alembic diff; secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: spend $0, network attempts 0 (proven).

## Budget

120s probes, 600s suite, 1800s early-close, 2400s overall.
