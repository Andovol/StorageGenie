# SG-030 — Phase 2 exit E2E + runbook + close-out, money leftovers closed (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 2 Slice 6 — the FINAL slice under D35 L3. SG-025…SG-029 landed (029 rated 97, work `6a07c62`). Plan: `docs/superpowers/plans/2026-09-11-phase-2-ai-extraction.md` Slice 6. **Exit condition (blueprint:522, quoted):** "AI proposes candidates including expiry dates for Food/Medicine; corrections are auditable; a working expiry tracker is usable end-to-end for the two initial users."
**Money posture:** **zero live calls in this slice** — the E2E runs offline on a scripted provider through the existing injection seam; any network attempt is a STOP. The runbook documents live use; the SG-029 numbers are carried, not re-run. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · GPS-default-strip (F3) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (a `-1` that would unwind `sg025` is a STOP); no prompt-file edits (prompt v1 is FROZEN per SG-029).
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-03` stop-is-BLOCKED-commit · `PG-EV-04` shape-of-what-is-sent · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed. NETWORK: none** (`PG-PR-04`: proof is in-process tests; zero live calls; spend $0).

## Why this exists

The stage must close on its own exit condition, not on the sum of its slices. This slice proves blueprint:522 end-to-end in one fixture set, documents the runbook the owner needs to actually use it, and closes the two latent money findings the stage would otherwise exit with (ISS-10 monthly cap cannot bind across jobs; ISS-11 a call that returned a body can leave no cost record). Plan Slice 6 also carries the explicit Phase 3 non-goals ledger.

## G0 — close the two latent money findings (offline, FIRST; `PG-EV-01`)

- **ISS-10 — the monthly cap must bind ACROSS jobs.** Today `_monthly_spent` lives on a provider instance rebuilt each step, so it resets. Requirement: with a monthly cap configured, spend already recorded against the household/job stream must count toward the next call, and a job whose estimate would exceed the cap **refuses BEFORE any call** (0 invocations; 0 new ledger rows for that job) with the refusal visible in the step error. Mechanism is yours — prefer a durable, ledger-derived figure over an in-process singleton (say why in the report). Proof: two sequential offline jobs against a tiny cap; the first succeeds, the second refuses pre-call; FAIL-then-PASS raw.
- **ISS-11 — a call that reached the provider and returned a body must leave a durable cost/usage record**, even when the content later fails schema validation on both attempts or the step fails. Today such rows carry `cost=0.0`/no usage or are erased by the step rollback. Requirement: after a FAILED job whose scripted provider returned usage-bearing bodies that failed validation, committed rows exist carrying the real cost/usage **and** `error_state`; FAIL-then-PASS raw.
- Both live as new tests in `backend/tests/test_ai_pipeline.py`. With caps `None` (F2 default) and no failures, behavior is unchanged — say so and prove the default path still passes.

## G1 — Phase 2 exit E2E (`backend/tests/test_phase2_e2e.py`, NEW, offline/scripted)

Follow the `test_phase1_e2e.py` shape (TestClient over the real HTTP routes, temp SQLite + temp storage). Scripted provider only — assert zero network attempts. One fixture set proves:

1. **AI proposes candidates with expiry for Food AND Medicine.** Upload a food image and a medicine image; create + run an import job; `ANALYZING_WITH_AI` + `BUILDING_CANDIDATES` run on the scripted output; the candidate carries per-field provenance and the gated fields (`expiry*`, `identifier`, `condition`, `lot`) are `proposed`, not accepted.
2. **Accept commits atomically.** Decide `accept` on the candidate → asset + assertions + audit rows appear together; a forced failure inside the commit path leaves NO partial asset/assertion (prove rollback, not prose).
3. **`needs_evidence` path works for real.** A third image whose scripted output is `needs_evidence` → no expiry value anywhere → the manual-entry task exists → entering the date through the existing plugin route (the README-cited `POST /v1/plugins/expiry-tracker/assets/<id>/expiry`) resolves the task and writes an accepted user assertion, with the prior state superseded — **never a guessed date**.
4. **Corrections are auditable.** Correct an AI-sourced field after commit through the existing route → the prior assertion is `superseded`, a new `accepted` assertion exists, audit rows record both — never an overwrite.
5. **`provider_call` rows exist per AI call** with `job_id` linked, `error_state is None`, and the scripted cost/usage recorded (cost is the scripted value, not real money).
6. **Default-off unchanged.** With the shipped defaults the same flow yields Phase-1-equivalent behavior (skip, no ledger rows) — reference the existing coverage if it already proves this and say so.

## G2 — Phase 2 runbook + Phase 3 non-goals (`README.md`, `.env.example`)

- Add a **Phase 2 runbook** section: provider setup (OpenCode GO subscription, key into the host `.env`, value never printed/logged), the settings incl. `SG_PROVIDER_ID`, `SG_MODEL_ID`, `SG_CONFIDENCE_THRESHOLD`, `SG_PROMPT_CATEGORY`, the caps, and the consent switch with **cloud OFF by default**; the eval commands (offline default and the `--live` metered mode with its printed ceiling); and the budget posture (F2: uncapped now, re-evaluation owed; caps exist and can refuse).
- Add the missing key NAMES to `.env.example` (`SG_CONFIDENCE_THRESHOLD`, `SG_PROMPT_CATEGORY`) — names only, never values.
- Record the **explicit Phase 3 non-goals ledger** (what Phase 3 owns: web enrichment, planning/chat agents, remaining categories, prompt tuning, multi-provider). Keep it terse and factual.

## G3 — proof

- FAIL-then-PASS raw for every new test (G0 + G1) in the verify log (`PG-EV-01`/`PG-EV-09`). Full suite from `backend/` (bound 600s), `ruff` clean, `mypy` quoted. No network (prove it), no migration, no prompt-file diff, no ignored file staged, secret scan 0. Read-back (`PG-SC-02`) of any setting you touch.

## G4 — exit verdict (in the report)

- Map **blueprint:522 clause by clause** to evidence: (a) AI proposes candidates including expiry dates for Food/Medicine; (b) corrections are auditable; (c) a working expiry tracker is usable end-to-end. State plainly that this slice made **zero live calls** and that the measured numbers remain SG-029's (`field_accuracy=0.762`, annotated for the known glare-truth artifact; `$0.002328`). Say explicitly what is NOT yet true for the two initial users (e.g., no UI for split/manual-entry-by-component; single-household, LAN-only) — the verdict is a claim the owner can audit, not a victory lap.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-030.log`, `{{WORKLOG_DIR}}/SG-030_report.md`, `{{WORKLOG_DIR}}/SG-030_verify.log` (both-runs raw). First token `SG-030`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0); live-state ledger; three UNCLEAR lines.

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-030 | Report: docs/worklogs/SG-030_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/tests/test_phase2_e2e.py` (new) · `backend/tests/test_ai_pipeline.py` (G0 tests) · `README.md` · `.env.example` (names only) · `backend/app/services/providers/reader.py` · `backend/app/services/providers/opencode_go.py` · `backend/app/services/providers/router.py` (only if the monthly binding needs it) · `docs/worklogs` (3 files). **Anything else is a STOP. No migration. No prompt edits. No corpus edits. No UI. No live calls.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money/privacy: zero spend; no key read; no network. Secrets: names and counts only (`CO-44`).
- Cross-product (`PG-IC-01`): G0 needs only the reader/adapter + scripted provider; G1 the HTTP routes + the same script; G2 files only. Recorded once.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse the existing E2E pattern, the injection seam, the ledger, the task kinds; no new machinery.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- ISS-10 and ISS-11 each closed with a FAIL-then-PASS test quoted both raw; default (uncapped, no failure) behavior unchanged and proven.
- The E2E proves all six numbered behaviors on the HTTP path, offline, with zero network attempts; commit atomicity proved by a forced-failure rollback assertion; `needs_evidence` never yields a guessed date; corrections supersede auditably.
- README Phase 2 runbook + Phase 3 non-goals present; `.env.example` names added; no prompt/corpus/migration/UI change.
- Exit verdict maps blueprint:522 clause by clause with evidence and states its limits; zero live calls stated; SG-029 numbers carried unmodified.
- Suite/ruff/mypy quoted; secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: spend $0, network attempts 0 (proven).

## Budget

120s probes, 600s suite, 1800s early-close, 2400s overall.
