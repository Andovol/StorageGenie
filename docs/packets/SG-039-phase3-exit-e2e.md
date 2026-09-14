# SG-039 — Phase 3 exit E2E + runbook + close-out (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3, FINAL slice under D46 L3 (plan `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 8; SG-040 landed rated 98, work `649cedf`). All seven prior slices rated 98: SG-031/033/034/035/036/037/038/040. **Authoring date (metadata, never a gate):** 2026-09-14. mypy advisory stands. The transport is the standard `job_spawn` lane (owner-fixed 2026-09-14).
**Money posture:** **ONE metered live run under a $0.05 printed ceiling** — the cosmetics eval leg deferred from SG-036 (`eval/run.py --live`, consent on, key from the host environment only, never logged; per-call model/latency/usage/cost quoted; accuracy figures reported). Plus the stage spend tally read from the durable `provider_call` ledger (sum of committed cost, quoted). Any SECOND live run, ceiling breach, or key material in output is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · GPS-default-strip (F3) · Stage 0, human confirmation mandatory regardless (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (an alembic diff is a STOP); frozen prompts (`extract-food-v1.md`, `extract-medicine-v1.md`, `extract-cosmetics-v1.md`, `planning-v1.md`, `chat-v1.md`) are read-only context; only the ONE stated live run. This is a PROOF + DOCS slice: bookkeeping and evidence, not features. **A source defect found while proving gets reported with a destination — do not silently fix beyond the ceiling; a defect inside the ceiling's own files follows the stop-path rules.** Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable.
**Sensitivity-proof posture (SG-030 precedent, proposal P1 `docs/proposals/2026-09-12-proof-scope-and-role-line.md`):** the new E2E file proves ALREADY-LANDED flows, so it passes on the unmodified base by construction. Do NOT fabricate a pre-fix failure: prove non-vacuity with **source-mutation proofs** — break each exit behaviour under test (one mutation at a time), show the test catches it, revert clean, record all three states (mutated / caught / reverted-clean) verbatim in the verify log. Aim for the same technique SG-030 used (three mutations: gating, rollback, supersession equate here to split-coverage, correction-chain, guardrail-write).
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-07` no-data-bar · `PG-SC-09` money-tally · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite, 600s `npm run build`, 600s vitest. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: temp SQLite ONLY — zero live rows; the production DB is never opened for writing (the live leg's eval run uses its own temp DB, quoted). Restart: none — nothing deployed. NETWORK: exactly ONE metered live run** (the cosmetics eval leg), everything else offline with `_post` patched to raise (`PG-PR-04`, `PG-PR-06`).

## Why this exists

The stage's exit bar (blueprint §14 Phase 3, `blueprint:524-531`): "daily planning suggestions and category chat are functional; guardrail rollout tracking (§10) is active" — plus the approved design's own bar: the usability block shippable on screen (model picker, multi-item split, manual entry per field, on-screen corrections), and Cosmetics tracked with opened-date. Every mechanism now exists; this slice proves the whole loop on the real HTTP path with zero network, runs the deferring cosmetics accuracy leg once, writes the Phase 3 runbook, tallies the stage spend, and hands the Architect the material for the exit verdict.

## G1 — the exit E2E (`backend/tests/test_phase3_e2e.py`, new)

One fixture, real HTTP routes through `TestClient`, temp SQLite/storage, scripted provider through the ONE seam (`provider_registry`), zero network (`_post` patched to raise; `network_attempts == []` asserted). Prove, with assertions on VALUES (not mere presence):

1. **Usability block:** settings picker round-trip (GET lists the allowed model; PUT selects it; an out-of-set id → enforced 422; the provider key never appears in any response); multi-item split (full-coverage indexes; partial-coverage → 422 with nothing created; children carry their per-item fields); manual expiry entry on a `needs_evidence` asset resolves the task (never a guessed date); the correction chain supersedes + audits.
2. **Planning:** run on the button → `pending` suggestions with backing refs + a `suggestion` guardrail row; confirm and dismiss transitions (illegal move → 422); dismiss-with-reason → `correction` guardrail row; catalogue state identical before/after a run (no execution path).
3. **Chat:** grounded answer through the seam for the requested category; unsupported category 422; a cross-category asset never appears in the wrong request's data; the user-initiated correction writes one `correction` guardrail row; model output alone writes none.
4. **Cosmetics + opened-date:** a cosmetics extraction carrying `opened_date` reaches a persisted `opened_date` assertion after candidate accept (gated: `review_state="proposed"`), and the chat/planning catalogue carries it; an item without an opened date stays null.
5. **Guardrail log:** `suggestion` and `correction` rows exist with their refs/detail shapes readable.
6. **Default-off unchanged:** with `SG_CONSENT=false` (and `fake` provider), planning run and chat both refuse with 0 calls/0 rows, and the import pipeline skips AI steps exactly as Phase 1 — assert the skip shape you find (name it in the report).

**Sensitivity:** source-mutation proofs as stated in the standing lines (three mutations, each caught, reverted clean, raw in the verify log) in lieu of a fabricated pre-fix failure — call the premise difference out explicitly, as SG-030 did.

## G2 — the cosmetics accuracy leg (ONE metered run, LAST)

- `SG_CONSENT=true SG_PROVIDER_ID=opencode-go venv/bin/python eval/run.py --live`, the SG-029/036 shape: print and check the `$0.05` ceiling BEFORE the run; consent on only for this leg; key from the host environment, never logged/printed; per-call model/latency/usage/cost quoted; accuracy / unknown_rate / correction figures for the cosmetics fixtures quoted against the committed ground truth; the ledger row(s) counted. State plainly that the offline caches are integrity-only (their 1.000s are not accuracy) and this leg is the accuracy evidence.
- **Stage spend tally:** sum the committed `provider_call` cost across the durable ledger (don't hand-add my per-slice figures — read the table; quote the query/statement and the total). Expected reference values to CHECK, not to trust: SG-037 $0.000722 + SG-038 $0.0001833 = $0.0009053 before this leg; a difference is a finding, report it.

## G3 — runbook + non-goals (README.md)

- New `## Phase 3 runbook` section: what the stage added (picker, split, manual entry, corrections, planning button, chat, cosmetics), the settings/consent switches in play (names only — never values), how to run planning and chat, what stays OFF by default, and the caps posture (F2: uncapped, re-evaluation owed).
- A `Phase 3 non-goals` ledger for the next door (name them; do not build): live web enrichment/search (owner: nice-to-have, deferred), auto-scheduling, second provider/multi-provider routing, streaming/persisted chat history, per-field accept UI for gated values beyond what exists, provider analytics.
- Keep the existing Phase 0/1/2 sections intact (append, never rewrite).

## G4 — proof + hygiene

- Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted (touched files add zero new errors). `npm run build` green and `npx vitest run` (600s) green ONLY if any frontend file changes; if the frontend diff is empty, state that instead (SG-035/036/040 precedent). Secret scan 0. No migration (prove the alembic diff empty), no frozen-prompt diff, no ignored file staged. Eval guard: confirm `eval/run.py`'s category set includes cosmetics and the frozen prompt names are intact — verify, don't change (a needed change is a finding first). Health probe per the standing line.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-039.log`, `{{WORKLOG_DIR}}/SG-039_report.md`, `{{WORKLOG_DIR}}/SG-039_verify.log` (mutation proofs + both-runs raw + the live leg's receipt and tally). First token `SG-039`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (live total for this leg + the stage tally); live-state ledger; three UNCLEAR lines. The report ends with the **stage exit material**: each exit-bar item → the test/evidence that proves it, and any limit that should appear in the verdict.

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-039 | Report: docs/worklogs/SG-039_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/tests/test_phase3_e2e.py` (new) · `README.md` (append the Phase 3 runbook + non-goals) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every source file (a needed source change is a finding, reported with a destination: STOP if it blocks the exit proof, otherwise report and ship the rest). ONE live run only. No migration. No frozen-prompt edits.
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money: exactly one live run under the printed $0.05 ceiling; per-call cost quoted; the stage tally read from the ledger. Privacy: key from host env only, never logged/printed.
- Cross-product (`PG-IC-01`): G1 needs the shipped endpoints (settings/split/expiry/planning/chat) read-through only; G2 the eval runner; G3 README; G4 the gates. Timeouts are per-command-class (120/600/600/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 600s build, 600s vitest, $0.05 single live run, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): this slice adds ONE test file and README prose; no new machinery anywhere.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- The E2E proves each exit-bar item on the real HTTP path with zero network, by VALUE; the default-off path is unchanged; non-vacuity is proven by three source mutations caught and reverted clean (all raw).
- The cosmetics live leg ran exactly once under the printed ceiling with per-call figures and accuracy quoted; the stage tally comes from the ledger and is quoted.
- README carries the Phase 3 runbook + non-goals, append-only.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; touched files add zero mypy errors; secret scan 0; no migration; no frozen-prompt diff; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: live spend this leg + stage tally from the ledger (quoted), network attempts exactly the live leg's calls (proven count), live DB writes 0 (temp-DB evidence quoted). End with the stage exit material per G5.

## Budget

120s probes, 600s suite, 600s build, 600s vitest, $0.05 single live run, 1800s early-close, 2400s overall.
