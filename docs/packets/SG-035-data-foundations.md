# SG-035 — Data foundations migration: attribution + planning + guardrail tables (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 Slice 4 under D46 L3. SG-034 landed (rated 98, work `9e91363`). Plan: `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 4. **Authoring date (metadata, never a gate):** 2026-09-14. Previous slice left no open UNCLEAR (link-key confirmed; co-evidence advisory carried in STATE; mypy advisory stands).
**Money posture:** **zero live calls in this slice** — schema only; any network attempt is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **this slice's ONE stated migration is the only schema change** — any second migration, any edit to the five existing version files, any live-DB write is a STOP; no prompt-file edits; no live calls. Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable (starting a service is deploying, out of scope per the privileged-denial path below).
**Sensitive-surface scope (D46 requires it stated):** this packet authorizes exactly one alembic migration run against TEMP SQLite databases in tests, plus model files. The production database (`/data/db/storagegenie.db`) is never opened for writing — any live write is a STOP (`PG-PR-10`).
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-10` no-ignored-commit · `PG-SC-11` sequence-append · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: temp SQLite ONLY in tests — zero live rows, production DB never opened for writing. Restart: none — no service touched, nothing deployed. NETWORK: none** (`PG-PR-04`: proof is in-process tests; zero live calls; spend $0).

## Why this exists

The agents (SG-037/038) need tables that do not exist: where a future web lookup attaches (S2 attribution), what a planning run proposed (suggestion records with status), and the Stage-1 evidence base (guardrail log). Building them now — additive only, no routes, no agents — keeps the agent slices free of schema work.

## G1 — three additive tables + migration (the full schema change)

- New models following the `provider_call.py` pattern (verified 2026-09-14: `TimestampMixin` + `Base` from `app.models.base`, `new_id` string PKs, `__tablename__`, registered in `app/models/__init__.py`):
  1. `source_attribution`: id, household FK, asset FK, assertion FK (nullable), field_path, uri, retrieved_at, note (nullable) — where a later fetcher attaches; no fetcher here.
  2. `planning_suggestion`: id, household FK, kind, title, body JSON, backing_refs JSON (the label data behind it), status (`pending` default; `confirmed`/`dismissed` later), timestamps.
  3. `guardrail_event`: id, household FK, kind (`suggestion`|`correction`|`constraint`), ref_ids JSON, detail JSON, timestamps — append-only by convention (no update path; state it).
- One migration `20260914_sg035_foundations` with `down_revision = "20260912_sg025_provider_call"` (chain verified 2026-09-14: five versions, sg025 is the head). Upgrade creates all three tables + indexes on the FK/status columns; downgrade drops all three. Existing version files are read-only context — touching one is a STOP.
- `PG-SC-11`: grep for head-relative assertions (`downgrade`, `latest`, `HEAD`, `expected_head`) and list every hit in the slice; `test_export.py:114-116` derives the head live (verified 2026-09-14) so it flows — prove it, do not assume it. Any assertion true only while its subject is newest is a finding with a destination.

## G2 — model round-trip + migration integrity (no routes yet)

- `PG-SC-02` stated plainly: NO production writer exists in this slice — writers arrive in SG-037/038. This slice proves the columns accept values and the migration is sound; the read-back route (planning/chat screens) is SG-037/038 acceptance, not this slice's. Say so in the report; silence is not valid.
- Tests (new `backend/tests/test_foundations.py`): upgrade/downgrade/upgrade on a temp DB (the `test_candidates.py:154` / `test_signals.py:221` / `test_search.py:232` pattern); per-table write+read round-trip through the models; downgrade removes all three tables; re-upgrade restores. FAIL-then-PASS raw (pre-change: tables absent — quoted, committed).

## G3 — proof

- FAIL-then-PASS raw in the verify log. Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted (new model files must add ZERO new errors — check the file list in the output). Secret scan 0. No frontend change (no build needed — state why: zero frontend files touched). No prompt diff, no ignored file staged, no network (prove it). No live DB opened for writing (state the temp-DB evidence). Health probe per the standing line above.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-035.log`, `{{WORKLOG_DIR}}/SG-035_report.md`, `{{WORKLOG_DIR}}/SG-035_verify.log` (both-runs raw). First token `SG-035`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0); live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-035 | Report: docs/worklogs/SG-035_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/models/source_attribution.py` (new) · `backend/app/models/planning_suggestion.py` (new) · `backend/app/models/guardrail_event.py` (new) · `backend/app/models/__init__.py` (registration only) · `backend/alembic/versions/20260914_sg035_foundations.py` (new, the ONLY migration) · `backend/tests/test_foundations.py` (new) · `docs/worklogs` (3 files). **Anything else is a STOP — including the five existing version files, any route, any service, any UI. No second migration. No live calls.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money/privacy: zero spend; no key read; no network. Secrets: names and counts only (`CO-44`). No secret-shaped column carries a real value in tests (sentinel strings only if needed).
- Cross-product (`PG-IC-01`): G1 needs models + registration + the one migration; G2 the new test file + temp DBs; G3 proves both. Timeouts are per-command-class (120/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): follow the provider_call model pattern and the upgrade/downgrade/upgrade test pattern; no new machinery. No update path on guardrail_event (append-only stated).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- `alembic upgrade head` on a temp DB creates all three tables with the stated columns/indexes; downgrade removes them; re-upgrade restores; existing five versions untouched (diff proves it); head-relative assertions found by grep and all green.
- Each table round-trips a row through its model; no routes, no writers — stated with SG-037/038 as their destination, not implied.
- New model files add zero mypy errors; suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: spend $0, network attempts 0 (proven), live DB writes 0 (temp-DB evidence quoted).

## Budget

120s probes, 600s suite, 1800s early-close, 2400s overall.
