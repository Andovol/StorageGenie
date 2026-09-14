# SG-033 — Multi-item split: one candidate → per-item candidates + review UI (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 Slice 2 under D46 L3. SG-031 landed (rated 98, work `edf3cdc`). Plan: `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 2. **Authoring date (metadata, never a gate):** 2026-09-14. Previous slice left no open UNCLEAR (SG-031 whitelist confirmed; mypy advisory stands).
**Money posture:** **zero live calls in this slice** — all proofs offline on scripted/deterministic paths; any network attempt is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (candidate rows only — a schema diff is a STOP); no prompt-file edits; no live calls. Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable (starting a service is deploying, out of scope per the privileged-denial path below).
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

A photo with several items produces ONE candidate holding an `ai_items` list plus a `candidate.multi_item` review task (`backend/app/services/candidates.py:257-270`, verified 2026-09-14) — and review has nowhere to go: the decision route accepts/edits/holds/rejects the whole candidate only (`backend/app/api/v1/candidates.py:21-22`), and no split route or button exists anywhere (verified: no split operation in `api/v1/`, no split UI in `frontend/src/`). The schema already supports the outcome (many-to-many asset↔evidence: "one photo can back multiple assets after split/merge", `backend/app/models/evidence.py:7`). This slice builds the missing operation and its screen.

## G1 — split operation (candidate → per-item candidates)

- New route `POST /v1/candidates/{candidate_id}/split` (in `backend/app/api/v1/candidates.py`, beside the decision route): request names item indexes (empty set → enforced `422`, nothing created — `PG-SC-07`).
- Load-bearing facts (verify in-slice, mechanism is yours): the origin proposal carries `ai_items`, `ai_unknowns`, `provider_call_ids`, `evidence_ids`, `ai_provider/ai_model/prompt_template_version` (`candidates.py:232-245`); `Candidate` holds `job_id`, `evidence_ids_json`, `proposed_fields_json`, `state`, `household_id` (`candidates.py:246-252`); task resolution already exists (`POST /v1/review-tasks/{task_id}/resolve`).
- Property (`PG-EV-05`): each child is `proposed` with ITS item's fields, the SHARED evidence ids, and the origin's provider provenance + call ids — no field invented, no evidence dropped, no provenance lost. The origin leaves the decidable set (a later decision on it is rejected — code is yours, 409 or 422, state which) and the `candidate.multi_item` task resolves.
- `PG-SC-02`: `ai_items` traced origin → children with the read-back route named; ceiling contains the service, the route, and the screen — or the packet's M6 line fires (STOP and say which requirement lacks its file).

## G2 — review UI split action

- `frontend/src/routes/ReviewPage.tsx` (decision mutation + keyboard pattern verified 2026-09-14) and `frontend/src/components/CandidateCard.tsx` (renders candidate + `onDecision`, dedup matches): split button visible exactly when a `candidate.multi_item` task is open on the candidate; after split, the UI presents the children (links/invalidation via the existing react-query pattern).
- Options render from data, never hardcoded lists. `frontend/src/api/client.ts` gains the split call beside `candidateDecision`; `types.ts` gains its types.
- Frontend tests beside the page/card (action visible iff multi-item open; split round-trips through the mocked call; rejection surfaces). Pre-change run fails (action absent) — quoted raw with the post-change pass.

## G3 — proof

- FAIL-then-PASS raw for every new test in the verify log (pre-change: route 404 / action absent — quoted, committed). New tests in `backend/tests/test_candidates.py` (or a new `test_review_split.py` if the seam deserves its own file — decide and report). Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted. `npm run build` green (quoted), `npx vitest run` (600s) green. Secret scan 0. No migration, no prompt diff, no ignored file staged, no network (prove it). Health probe per the standing line above.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-033.log`, `{{WORKLOG_DIR}}/SG-033_report.md`, `{{WORKLOG_DIR}}/SG-033_verify.log` (both-runs raw). First token `SG-033`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0); live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-033 | Report: docs/worklogs/SG-033_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/api/v1/candidates.py` (split route only) · `backend/app/services/candidates.py` (split operation only) · `backend/tests/test_candidates.py` + `backend/tests/test_review_split.py` (new, only if the seam deserves it) · `frontend/src/routes/ReviewPage.tsx` · `frontend/src/components/CandidateCard.tsx` · beside tests · `frontend/src/api/client.ts` · `frontend/src/api/types.ts` · `docs/worklogs` (3 files). **Anything else is a STOP. No migration. No prompt edits. No dedup-rule changes. No live calls.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money/privacy: zero spend; no key read; no network. Secrets: names and counts only (`CO-44`).
- Cross-product (`PG-IC-01`): G1 needs the route + service + task-resolve route (read-only use); G2 the page + card + client; G3 proves both. Timeouts are per-command-class (120/600/600/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse the decision-route shape, the task-resolve route, the proposal JSON shape, the react-query mutation pattern; no new machinery.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- Splitting a multi-item candidate yields one `proposed` child per named item with per-item fields, shared evidence, and origin provenance; origin no longer decidable; multi-item task resolved; empty selection → 422 with nothing created; single-item split → 422 with nothing created.
- The split action is visible exactly for multi-item-open candidates and presents the children afterwards; pre-change UI tests fail, post-change pass — both quoted raw.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; `npm run build` green (quoted); secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: spend $0, network attempts 0 (proven).

## Budget

120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall.
