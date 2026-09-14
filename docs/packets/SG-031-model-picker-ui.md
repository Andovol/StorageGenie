# SG-031 — Model-picker UI backed by a safe settings endpoint (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 Slice 1 under D46 L3. Phase 2 CLOSED (SG-030 rated 98). Plan: `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 1. **Authoring date (metadata, never a gate):** 2026-09-14. Previous slice left no open UNCLEAR.
**Money posture:** **zero live calls in this slice** — the override proof runs offline on the fake provider; any network attempt is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration**; no prompt-file edits; no provider switching (model only); no live calls.
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-03` stop-is-BLOCKED-commit · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-07` no-data-bar · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite, 600s `npm run build`, 600s vitest. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed. NETWORK: none** (`PG-PR-04`: proof is in-process tests; zero live calls; spend $0).

## Why this exists

Switching AI models today means editing the host `.env` and restarting the backend — no screen, no validation, no visibility into what is effective. The Settings page is a 21-line stub (household-clear button only). The `sg_model_id` setting exists (`backend/app/config.py:28`, default `deepseek-v4-flash-vision-exp`) and the reader builds the provider from settings (`backend/app/services/providers/reader.py:61-72`), but no API exposes it and no UI touches it (verified 2026-09-14: `backend/app/api/v1/` has no settings module; `frontend/src/api/` has no settings types). D42 queued exactly this slice: settings-backed, tested-models-only.

## G1 — safe settings endpoint (new `backend/app/api/v1/settings.py`)

- GET exposes the effective AI settings subset ONLY: provider id, model id, consent flag, cap values, prompt category. **The key (`opencode_api_key`) is never serialized, never logged — exclusion by RULE (`PG-SC-05`), proven by a test that configures a sentinel key and asserts its absence from every byte of the response, plus a grep gate over the response path.**
- PUT sets the runtime model selection. **Server-side whitelist, tested-models-only: premise list is `deepseek-v4-flash-vision-exp` (SG-027 spike + shipped default) and `deepseek-v4-flash` (SG-027run2…SG-030 metered runs) — verify against the tree/ratings in-slice and correct me.** Unknown model → enforced `422` with selection unchanged (`PG-SC-07`, `PG-EV-03`: rejection is enforced, never satisfied by disclosure). No silent fallback, ever.
- Load-bearing facts for the persistence choice: settings are env-loaded pydantic (no runtime write path exists), the backend is one process — so the override lives process-side and **a backend restart resets to the env default; the report and README line state this plainly** (`PG-SC-09`: the world where the test passes and the outcome still surprises is named, not hidden).
- Register the router beside the existing v1 routers (see `backend/app/main.py` — verify, do not assume the pattern).

## G2 — reader honors the runtime selection

- The read path that builds the effective provider for a call must resolve the G1 override (verify the build site in-slice starting from `reader.py:61-72` — premise, not direction). Mechanism is yours; the property (`PG-EV-05`) is: **the model recorded for a call made after PUT equals the selected model.**
- Proof offline on the fake provider: run the extraction path after selecting, assert the recorded model equals the selection. No network, no key.

## G3 — Settings UI picker

- `frontend/src/routes/SettingsPage.tsx` gains the picker beside the existing household control: options rendered from the endpoint's allowed list (**never a hardcoded list in the UI** — `PG-SC-02`: allowed list traced endpoint → screen; ceiling contains both ends), current effective model shown, selection PUTs and refetches (page reload re-reads the backend — no local mirror).
- Types in `frontend/src/api/types.ts`, calls in `frontend/src/api/client.ts` (extends the existing `apiGet`/`apiPost` pattern).
- Frontend tests beside the page (render from mocked endpoint list; selection round-trips; unknown-model rejection surfaces the 422). Pre-change run fails (component absent) — quoted raw with the post-change pass (`PG-EV-01`/`PG-EV-09`).

## G4 — proof

- FAIL-then-PASS raw for every new test in the verify log (pre-change: routes 404 / component absent — quoted, committed). Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted. `npm run build` (`tsc && vite build`, 600s) green with output quoted — this discharges the long-queued build proof for the frontend. `npx vitest run` (600s) green. Secret scan 0 (incl. sentinel-key absence). Health probe start+end with delta (`CO-92`; premise: live mapped port is 8003 per D20 — verify against the host compose file, correct me). No migration, no prompt diff, no ignored file staged, no network (prove it).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-031.log`, `{{WORKLOG_DIR}}/SG-031_report.md`, `{{WORKLOG_DIR}}/SG-031_verify.log` (both-runs raw). First token `SG-031`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0); live-state ledger; three UNCLEAR lines.

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-031 | Report: docs/worklogs/SG-031_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/api/v1/settings.py` (new) · `backend/app/main.py` (router registration only) · `backend/app/services/providers/reader.py` (override resolution only) · `backend/tests/test_settings.py` (new) · `frontend/src/routes/SettingsPage.tsx` · `frontend/src/routes/SettingsPage.test.tsx` (new) · `frontend/src/api/client.ts` · `frontend/src/api/types.ts` · `README.md` (restart-resets line only) · `docs/worklogs` (3 files). **Anything else is a STOP. No migration. No prompt edits. No provider switching. No live calls.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money/privacy: zero spend; no key read (sentinel only in tests); no network. Secrets: names and counts only (`CO-44`).
- Cross-product (`PG-IC-01`): G1 needs the new route + config read; G2 the reader build site; G3 the page + client; G4 proves all three. Timeouts are per-command-class (120/600/600/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Derived set per §3 conditional block: this project runs the FULL backend suite, so the conditional block is NOT pasted and the full suite runs.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse the v1 router pattern, the reader build site, the client helpers, the E2E-less unit-test pattern for settings; no new machinery.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- GET returns the safe subset with effective values; sentinel-key test proves no key byte leaks; PUT unknown → 422 with selection unchanged; PUT listed → GET reflects it; restart resets to env default (stated in report + README line).
- A fake-provider extraction after PUT records the selected model on the call; property holds, not just the command.
- Picker renders the endpoint's list, selects, and re-reads after reload; pre-change UI tests fail, post-change pass — both quoted raw.
- `npm run build` green (output quoted); backend suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: spend $0, network attempts 0 (proven).

## Budget

120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall.
