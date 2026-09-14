# SG-037 — Daily Planning Agent on a button, Stage 0 (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 Slice 6 under D46 L3. SG-036 landed (rated 98, work `b3f73e5`). Plan: `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 6. **Authoring date (metadata, never a gate):** 2026-09-14. Folded destinations landing here: SG-035 status/kind CHECK choice (decided below: service-level, no migration); mypy advisory stands.
**Money posture:** **ONE metered live run under a $0.05 ceiling** (SG-029 precedent: ceiling printed and checked before the run, per-call model/latency/usage/cost quoted, key from the host environment only, never logged). All behavior proofs offline on the scripted provider first; any SECOND live run or any spend past the ceiling is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · GPS-default-strip (F3) · Stage 0, human confirmation mandatory regardless (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (status validation is service-level — an alembic diff is a STOP); frozen extraction prompts are read-only context, never edited; only the ONE stated live run. Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable (starting a service is deploying, out of scope per the privileged-denial path below).
**CHECK-constraint decision (Architect, closing the SG-035 fold):** NO database CHECK on `planning_suggestion.status` / `guardrail_event.kind` — values are enforced at the confirm/dismiss boundary in service code (illegal transition → enforced `422`), matching the codebase's Python-default pattern. A future slice may add CHECKs with its own migration; nothing here assumes them.
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-07` no-data-bar · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite, 600s `npm run build`, 600s vitest. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: temp SQLite ONLY — zero live rows; the production DB is never opened for writing. Restart: none — no service touched, nothing deployed. NETWORK: exactly ONE metered live run** under the ceiling below (`PG-PR-04`: the running service is not touched; the live leg is a metered test leg against a temp DB, and `PG-PR-06` bounds it).

## Why this exists

Planning suggestions do not exist: no service, no route, no screen, no suggestion rows. The tables landed in SG-035 with no writers. This slice adds the manual-trigger agent on the proven provider seam under Stage 0 (no hardcoded dosage guardrails; human confirmation mandatory on every health-adjacent proposal — blueprint §10, F4).

## G1 — planning service, manual trigger, Stage 0

- New `backend/app/services/planning/` + `backend/app/api/v1/planning.py` (register beside the v1 routers in `main.py`): `POST /v1/planning/run` (manual trigger), `GET /v1/planning/suggestions`, `POST /v1/planning/suggestions/{id}/confirm`, `POST .../dismiss`.
- Load-bearing facts (verify in-slice): provider calls go through the reader seam with `ai_status()` consent gating (`reader.py:97-101` — no consent means NO provider object is even built); the fake provider is the scripted offline double; `PlanningSuggestion` (status default `pending`) and `GuardrailEvent` (append-only) models exist with no writers yet.
- Behavior: run reads the catalog (assets + expiry assertions via existing services), builds the planning prompt (new versioned file `planning-v1.md` in `prompts/` — same front-matter discipline as extraction prompts, never edited in place afterwards), calls through the seam, writes one `pending` `PlanningSuggestion` per proposal with `backing_refs_json` naming its label data, and writes a `guardrail_event` (kind `suggestion`) per run. Confirm/dismiss transitions validate status in service code (illegal → enforced `422`); dismiss with a reason writes a `correction` guardrail event. NO execution path exists anywhere — suggestions change no asset, job, or setting; prove the negative with a test asserting catalog state is identical before/after a run.
- Consent: no consent → run refuses BEFORE any call (0 invocations, 0 rows), same shape as the reader's own gate. Empty catalog → empty suggestion list (a valid outcome, not an error) with a guardrail note (`PG-SC-07`).
- Suggestions must never carry secrets: the prompt builder sees label data only; grep-gate key names in the service + a test asserting no key material in any written row (`PG-SC-05`).

## G2 — planning screen

- New planning route + component (react-query pattern): lists pending/confirmed/dismissed with status filter, shows backing evidence per suggestion, confirm/dismiss buttons with the run button that triggers `POST /v1/planning/run`. No auto-refresh, no schedule UI (deferred by owner decision — do not build it).
- Frontend tests beside the new files (run → pending appears; confirm/dismiss round-trip; refusal surfaces). Pre-change run fails (route/screen absent) — quoted raw with the post-change pass.
- `PG-SC-02`: backing refs traced suggestion → screen display; suggestion → guardrail rows asserted in the backend test.

## G3 — proof: offline behavior + ONE metered live run

- Offline (scripted provider, zero network): run writes pending suggestions with backing refs + guardrail rows; confirm/dismiss transition correctly with 422 on illegal moves; no-consent refuses with 0 calls/rows; empty catalog yields an empty list; catalog bytes identical before/after. FAIL-then-PASS raw, committed.
- Live leg (exactly ONE, last): print the `$0.05` ceiling and check it before the run (SG-029 shape); `SG_CONSENT=true` for the leg; key from the host environment, never logged; per-call model/latency/usage/cost quoted; ledger row exists for the call; total quoted against the ceiling. Any second live run, any ceiling breach, any key material in output is a STOP.
- Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted. `npm run build` green (quoted), `npx vitest run` (600s) green. Secret scan 0. No migration (prove the alembic diff empty), no frozen-prompt diff, no ignored file staged. Health probe per the standing line above.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-037.log`, `{{WORKLOG_DIR}}/SG-037_report.md`, `{{WORKLOG_DIR}}/SG-037_verify.log` (both-runs raw + live-leg receipt). First token `SG-037`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (live total + $0 offline); live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-037 | Report: docs/worklogs/SG-037_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/planning/` (new) · `backend/app/api/v1/planning.py` (new) · `backend/app/main.py` (registration only) · `backend/app/services/providers/prompts/planning-v1.md` (new) · `backend/tests/test_planning.py` (new) · `frontend/src/routes/` planning screen (new) + beside test · `frontend/src/components/` planning component (new, only if the screen needs it) + beside test · `frontend/src/api/client.ts` · `frontend/src/api/types.ts` · `docs/worklogs` (3 files). **Anything else is a STOP — including the SG-035 models (read/write as-is, no changes), the reader, migrations, frozen prompts, scheduling. ONE live run only.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money: exactly one live run under the printed $0.05 ceiling; per-call cost quoted; nothing else metered. Privacy: key from host env only, never logged/printed; suggestions carry label data only.
- Cross-product (`PG-IC-01`): G1 needs the service + routes + prompt file + existing seam/models (read-write as-is); G2 the screen + client; G3 proves both offline, then the single live leg. Timeouts are per-command-class (120/600/600/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 600s build, 600s vitest, $0.05 single live run, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse the reader seam, the review-task-style status pattern, the react-query screen pattern; no scheduler, no new machinery.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- Manual run writes pending suggestions with backing refs + suggestion guardrail rows; confirm/dismiss transition with 422 on illegal moves; dismissal with reason writes a correction event; catalog bytes identical before/after every run; no-consent run makes 0 calls and 0 rows; empty catalog yields an empty list.
- Screen lists all three states with backing evidence, runs on demand, confirms/dismisses; no schedule UI exists.
- Live leg: exactly one run under the printed ceiling with per-call figures quoted and a ledger row; total stated; zero key material anywhere.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; `npm run build` green (quoted); secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: live spend total (quoted), offline $0, network attempts exactly the live leg's calls (proven count), live DB writes 0 (temp-DB evidence quoted).

## Budget

120s probes, 600s suite, 600s build, 600s vitest, $0.05 single live run, 1800s early-close, 2400s overall.
