# SG-034 — Manual entry on asset detail + on-screen corrections (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 Slice 3 under D46 L3. SG-033 landed (rated 98, work `5a744ad`). Plan: `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 3. **Authoring date (metadata, never a gate):** 2026-09-14. Previous slice left one folded destination: F-SG033-2 (manual_entry orphan on split origins) lands in G2 here; mypy advisory stands.
**Money posture:** **zero live calls in this slice** — all proofs offline; any network attempt is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (task resolution uses existing columns — a schema diff is a STOP); no prompt-file edits; no live calls. Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable (starting a service is deploying, out of scope per the privileged-denial path below).
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-07` no-data-bar · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite, 600s `npm run build`, 600s vitest. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed. NETWORK: none** (`PG-PR-04`: proof is in-process tests; zero live calls; spend $0).

## Why this exists

Two gaps, both screens over already-proven backends. (1) Corrections: the backend chain is safe — `PATCH /assets/{id}` runs `update_asset`, which upserts one assertion per field plus audit (`backend/app/services/asset_service.py:69-83`, verified 2026-09-14) — but the AssetDetail edit panel edits display_name ONLY (`frontend/src/routes/AssetDetailPage.tsx:77-92`); quantity/unit/condition corrections need the raw API. (2) Manual entry: typing a date by hand exists only inside Review-after-accept (`ExpiryEntryForm` rendered by `ReviewPage`); an asset sitting in `needs_evidence` has no entry screen on its own detail page — and SG-033 left F-SG033-2: a split origin's open `expiry.manual_entry` task stays orphaned on the retired candidate while its children carry the unknowns. `store_manual_expiry` resolves open manual-entry tasks by `subject_ref=asset.id` only (`backend/app/plugins/expiry_tracker.py:418-442`, verified 2026-09-14).

## G1 — on-screen corrections for accepted fields

- Extend the AssetDetail edit panel beyond display_name: quantity, unit, condition through the EXISTING `PATCH /v1/assets/{id}` (If-Match pattern already in the page). No backend change expected — verify the chain, do not rebuild it.
- Property (`PG-EV-05`): editing quantity supersedes the prior accepted quantity assertion (new `accepted`, old `superseded`) with an audit row; the history list on the page shows it. If any field bypasses the chain, STOP and say which — do not paper over it.
- Frontend test beside the page (edit quantity → PATCH → updated value + history entry visible). Backend test in `backend/tests/test_assets_crud.py` ONLY if uncovered — first grep for the supersede-chain coverage; a covered premise is cited with base proof per the standing line, never re-proven silently.

## G2 — manual entry on asset detail + orphan pickup (F-SG033-2)

- Render manual-expiry entry on AssetDetail when the asset's expiry assertion is `needs_evidence` (reuse the `ExpiryEntryForm` component/route pattern: `POST /v1/plugins/expiry-tracker/assets/{id}/expiry`). Never a guessed date: empty submit stays refused by validation; leaving it open is valid.
- Orphan pickup in `store_manual_expiry`: entering expiry for an asset ALSO resolves open `expiry.manual_entry` tasks on split origins sharing the evidence (children carry `split_from` + shared evidence per SG-033) — resolved with audit, never deleted. Tasks unrelated to the evidence stay open (`PG-SC-07`: elimination of every task is refused — name the smallest case, a task for other evidence, and prove it stays open).
- `PG-SC-02`: manual-entry value traced entry → assertion → resolved task list (own + orphan), all asserted in one test. Tests in `backend/tests/test_plugin_expiry.py`, FAIL-then-PASS raw (pre-change: orphan stays open — quoted, committed).
- The `plugins.py` route is read-only context — the pickup lives in the service. If the route itself needs a touch, STOP (M6) rather than widening silently.

## G3 — proof

- FAIL-then-PASS raw for every new test in the verify log (pre-change quoted, committed). Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted. `npm run build` green (quoted), `npx vitest run` (600s) green. Secret scan 0. No migration, no prompt diff, no ignored file staged, no network (prove it). Health probe per the standing line above.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-034.log`, `{{WORKLOG_DIR}}/SG-034_report.md`, `{{WORKLOG_DIR}}/SG-034_verify.log` (both-runs raw). First token `SG-034`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0); live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-034 | Report: docs/worklogs/SG-034_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `frontend/src/routes/AssetDetailPage.tsx` + beside test · `frontend/src/components/ExpiryEntryForm.tsx` (reuse; modify only if the detail page needs it) · `frontend/src/api/client.ts` · `frontend/src/api/types.ts` · `backend/app/plugins/expiry_tracker.py` (`store_manual_expiry` orphan pickup only) · `backend/tests/test_plugin_expiry.py` · `backend/tests/test_assets_crud.py` (G1 test ONLY if uncovered) · `docs/worklogs` (3 files). **Anything else is a STOP — including `api/v1/plugins.py`, `assertion_service.py`, `asset_service.py` (all read-only context here). No migration. No prompt edits. No live calls.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money/privacy: zero spend; no key read; no network. Secrets: names and counts only (`CO-44`).
- Cross-product (`PG-IC-01`): G1 needs the page + existing PATCH (no backend write expected); G2 the detail page + entry component + `store_manual_expiry`; G3 proves both. Timeouts are per-command-class (120/600/600/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse PATCH, the entry component, the resolve-by-subject pattern extended by evidence; no new machinery, no new task type.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- Editing quantity/unit/condition on screen supersedes auditably with history visible; any chain bypass is a STOP finding, not a silent pass.
- A `needs_evidence` asset offers hand entry on its detail page; entering resolves its own open tasks AND the split-origin orphans sharing the evidence (audited, not deleted); unrelated-evidence tasks stay open; empty entry stays refused — never a guessed date.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; `npm run build` green (quoted); secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: spend $0, network attempts 0 (proven).

## Budget

120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall.
