# SG-029 — Food/Medicine eval corpus + first metered baseline (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 2 Slice 5 under D35 L3. SG-025/026/027/028 landed (028 rated 96 — full detail in `docs/ratings.md`). Plan: `docs/superpowers/plans/2026-09-11-phase-2-ai-extraction.md` Slice 5; blueprint §13 (private eval set BEFORE prompt optimization) + §5.3. Forks binding: GO on its own subscription (Q1) · spend uncapped-but-ledgered with re-evaluation owed (F2) · GPS-default-strip (F3) · Stage 0 (F4). **This is the FIRST slice that spends real money** (the metered corpus run) — hence G0's cap/ledger repair comes first, and the run is hard-ceilinged.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration this slice** (a `-1` that would unwind `sg025` is a STOP); **no prompt file edits** — v1 is frozen or a v2 is *recommended*, never cut here.
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-03` stop-is-BLOCKED-commit · `PG-EV-04` shape-of-what-is-sent · `PG-EV-05` property-not-command · `PG-EV-07` committed-fixtures-not-runtime-authored · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** For the METERED run, quote the provider-returned model id and per-call cost.

> **DO NOT HANG.** Bounds: 120s ordinary, 600s fixture legs, **900s the single metered run leg**, 1800s early-close, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none.** **NETWORK: ONLY the metered corpus run's calls** — at most 2 per fixture (strict parse + the single §5.3 repair), nothing else; any other network attempt is a STOP (`PG-PR-04`).
**Money facts:** vision model `deepseek-v4-flash-vision-exp`, $15/mo included; off-peak $0.15/1M input · $0.60/1M output (×2 at peak 01:00–04:00 + 06:00–10:00 UTC Mon–Fri); SG-027's calls cost ~$0.0003–0.001 each. **Run ceiling: ≤10 fixtures, ≤2 calls each; abort before any call that would take the projected total over $0.05; report every call's cost and the total.**

## Why this exists

SG-026 shipped a 5-fixture *provider-output* smoke corpus (no images, no network). The blueprint requires a private image corpus with ground truth and the first measured extraction numbers before any prompt tuning (§13). This slice adds the image corpus, runs it once against the ONE real adapter (metered), and records the baseline. It also repairs the two money-instrumentation gaps SG-028 left: caps that cannot bind from the pipeline and failed calls that leave no ledger row — both proven by tests before a cent is spent.

## G0 — money-instrumentation repair (FIRST, fully offline; SG-028 findings)

- **Caps must be ABLE to refuse before a call.** The pipeline call site supplies an estimate to the router/adapter (design yours: e.g. a bounded worst-case estimate from the adapter's own rate table). Proof: with a cap below the estimate, the step FAILS with the budget refusal, the provider is invoked **0** times and **0** rows are written; there is no network. With caps `None` (F2 default) behavior is unchanged.
- **Failed/errored calls are ledgered.** A provider error (retryable outage, or invalid output on both attempts) leaves a `provider_call` row with `error_state` populated and the cost/usage it actually incurred, and that row **survives step failure** (the existing `run_job` rollback must not erase it). Proof: a scripted failing provider leaves exactly the expected rows with `error_state` set and the job FAILED.
- Both proofs are new tests in `backend/tests/test_ai_pipeline.py` (extend it), FAIL-then-PASS with both raw runs committed.

## G1 — the image corpus (`backend/eval/corpus/`)

- Both categories represented (Food AND Medicine), cases: clean · glare · clutter · partial label · no-date-visible. ≤10 fixtures total. Each fixture carries: a stable id, `class`, `category`, an IMAGE reference, `ground_truth` (items/unknowns/needs_evidence/`expectation_class` consistent with the SG-026 schema), and at least one deliberately hard/expected-unknown case so the scorer can be shown to discriminate.
- **Synthetic only** — rendered labels (deterministic recipe, committed generator script allowed), ZERO personal images, zero `/data/storage` reads, no GPS. Images are committed (small) and versioned with their ground truth (`PG-EV-07`).
- Corpus integrity test (`backend/tests/test_eval_corpus.py`, new): every fixture has image + ground truth + expectation class + category; ids unique; the committed counts match the manifest; a fixture with a `provider_output` cache parses strictly. Replace `run.py`'s hardcoded `!= 5` check with the manifest count.

## G2 — the runner (`backend/eval/run.py`)

- Keep the existing offline scoring path working from the committed `provider_output` cache; the metered mode (`--live` or equivalent) runs per fixture: read image → SHARED `redact_image` → versioned prompt by fixture category → call the ONE adapter **through the SG-028 reader path** (no parallel call path; a category/`for` parameter is allowed if needed, reported) → strict parse with the single repair → cache the validated output into the fixture JSON (so later scoring/tests stay offline and reproducible) → score.
- Scoring: field accuracy + unknown-rate, correction-rate tracking extended per the plan; print per-call model/latency/usage/cost and the total; abort before any call that would exceed the $0.05 projected ceiling.
- Consent/provider for the run are set by environment for that one command (`SG_CONSENT=true`, `SG_PROVIDER_ID=opencode-go`), never committed; the key comes from the host env only (`CO-44`, never printed).

## G3 — proof

- Offline: corpus integrity green; scorer discrimination shown (a fixture it scores below 1.0 for a recorded reason); offline scoring reproducible from the cache; `PG-EV-04` the bytes handed to the provider are the redacted PNG (no EXIF) and the prompt is the exact versioned file.
- Metered: ONE run, transcript quoted — per-call model id, latency, usage, computed cost, validated-parse result, total spend vs ceiling; model id must be the provider-returned one.
- G0 tests green; suite from `backend/` (base-proved reds stay reds); `ruff` clean; `mypy` quoted; secret grep 0; no-migration proof; zero ignored files staged.

## G4 — baseline report (`backend/eval/baseline_sg029.md`)

- Numbers (accuracy, unknown-rate, correction rate) + spend (per call and total) + the corpus manifest; a one-line verdict: prompt v1 frozen, or a v2 is recommended with the observed reason (**recommended only — no prompt edit this slice**).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-029.log`, `SG-029_report.md`, `SG-029_verify.log` (both raw runs + the metered transcript). First token `SG-029`; per-leg elapsed-vs-budget with units; MODEL + effort from process arguments; spend lines; live-state ledger; three UNCLEAR lines.

## G6 — receipt note on the notes ref (proven shape)

Push the work to `automation`, worktree clean (`CO-55`). Note on the work HEAD LAST (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-029 | Report: docs/worklogs/SG-029_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP (never force-replace); final line `note=yes`; zero-exit with `note=no` is a FAIL. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.

## Constraints

- Scope ceiling: `backend/eval/run.py` · `backend/eval/corpus/**` (images + ground-truth JSON + optional generator) · `backend/eval/baseline_sg029.md` (new) · `backend/tests/test_eval_corpus.py` (new) · `backend/tests/test_ai_pipeline.py` (G0 tests) · `backend/app/services/providers/reader.py` (G0 estimate + error-ledger) · `backend/app/services/providers/opencode_go.py` (only if the estimate wants a helper there) · `docs/worklogs` (3). **Anything else is a STOP. No migration. No prompt edits. No tuning. No second provider. No UI.**
- Privacy: synthetic images only; GPS stripped by construction (shared helper); no personal data; key names/counts only.
- Money: ≤10 fixtures, ≤2 calls each, abort over $0.05 projected; every call ledgered with cost; the ceiling is printed and honored, never silent.
- Cross-product (`PG-IC-01`): G0 needs only the offline reader/router; G1/G2 only the corpus + runner; the metered leg is ONE command. Recorded once.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s fixture legs, 900s metered run, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse the reader path, the redactor, the schemas, the scorer; no new machinery where one exists.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); G0 proofs first, and they must FAIL before the fix (both raw runs).
- Corpus: both categories, the five case shapes, every fixture with image + ground truth + expectation class; integrity test green; scorer shown to discriminate; synthetic/no-personal-data proven.
- Runner: offline reproducible from the cache; metered mode reuses the reader path with the shared redactor and the versioned prompt; per-call cost printed; ceiling honored (abort proven or never approached with the number quoted).
- Metered: exactly one run; transcript quoted with provider-returned model id, latency, usage, cost; total ≤ $0.05; FAIL-then-PASS for the new offline tests; suite/ruff/mypy quoted; secret grep 0; no migration; no prompt file changed (diff proof).
- Baseline report committed; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78`; live-state ledger includes per-call spend and the total.

## Budget

120s probes, 600s fixture legs, 900s metered run, 1800s early-close, 2400s overall.
