# SG-026 — Prompts, schemas, fallback, eval scaffolding (fake only) (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 2 Slice 2 under D35 L3 (SG-026 cleared to fire; needs no key, no fork). Approvals: D35 (stage). SG-025 landed 98 (protocols sync, router, 4-shape fake, ledger + migration `20260912_sg025_provider_call`); SG-027 alone waits on Q2 (count 0 at SG-025 — re-probe information-only here).
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; new migration heads update head-relative downgrade assertions (grep `downgrade`, list hits) — no migration expected this slice; a `-1` that would unwind `sg025` is a STOP.
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-04` shape-of-unsent-repair · `PG-EV-07` architect-pushed input · `PG-EV-09` both-runs-committed · `PG-SC-02` schema-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (Owner standing requirement: the report quotes model provenance after EVERY slice.)

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, suite/eval legs name
> their own bound below. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed** (`PG-PR-04`: proof scoped to in-process tests + the eval runner).

## Why this exists

SG-025 built the seam (sync `ProviderResult` + four Protocols in `backend/app/services/providers/protocols.py`, `ProviderRouter` + `RouterConfig` in `router.py`, 4-shape `FakeProvider` in `fake.py`, `provider_call` ledger). Extraction still has no prompts, no output schema, no `needs_evidence` bridge, no eval runner — prompt tuning without a corpus-backed baseline is unmeasurable (§13: corpus before optimization). Starting premises (verify live — `PG-IC-09`): `backend/eval/` absent; `providers/prompts/` absent; `providers/schemas.py` absent; manual-entry flow at `backend/app/plugins/expiry_tracker.py:351-357` (writes `needs_evidence` assertion + open task) resolved at `:382-410`; review tasks in `backend/app/models/review_task.py`; correction signal in `audit_event` via `backend/app/services/audit_service.py`.

## G1 — gates (report only)

- `git status --porcelain` quoted (clean expected — dirt is a STOP; prior quarantine refs are history, never adopt). Full backend suite BASELINE (`venv/bin/python -m pytest -q`, bound 600s): green quoted, or red cited with base-run proof (the 2 decoder env-reds are known — cite, don't relitigate). `.env` presence only (`CO-44`). Q2 re-probe `grep -c '^OPENCODE_API_KEY=' .env` — INFORMATION ONLY, never a gate, value never printed/logged/committed.

## G2 — versioned prompts + strict schemas (only if G1 passes)

- Create `backend/app/services/providers/prompts/` with `extract-food-v1.*` + `extract-medicine-v1.*` (versioned files, never edited in place; plugin fragment hooks per blueprint §8; system instruction carries the provider-neutral rule: never infer beyond visible evidence). Prompt FORMAT (md + front-matter, json, or yaml) is your design call — decide and report.
- Create `providers/schemas.py` (Pydantic, sync to match SG-025): items array, `unknowns` array REQUIRED, per-assertion confidence + uncertainty reasons; free-form prose is never parsed (a prose input must fail validation — prove it in G4).
- ONE repair retry exactly once per §5.3 then the step fails (invalid-JSON-once shape exists in the fake — use it). Repair helper lives in `schemas.py`; a new `extraction.py` ONLY if you quote why schemas.py cannot hold it.

## G3 — `needs_evidence` bridge + eval scaffolding (only if G1 passes)

- Wire extraction `needs_evidence` output into the EXISTING manual-entry review-task path (`expiry_tracker.py:351-357` shape): same assertion kind, same open task, no new task type, no pipeline changes (pipeline wiring is SG-028 — this bridge is a callable mapping + tests, never a job-step edit).
- Create `backend/eval/` with `corpus/` (5 smoke fixtures: clean, glare, clutter, partial-label, no-date-visible — fabricated JSON observations + ground-truth JSON incl. `needs_evidence` expectations; NO real photos, nothing leaves the box) + `run.py` (scores field accuracy vs ground truth incl. expected-unknown cases; correction rate read from `audit_event`; prints the baseline; exits non-zero on corpus-integrity failure). `PG-EV-07`: the smoke input is pushed from the committed corpus, never authored by the test at runtime.
- Scores are BASELINES, not targets (`G-A3` single-run honesty) — tuning in this slice is a STOP-worthy scope breach; record the number in `backend/eval/baseline_sg026.md` (ID-suffixed, never dated).

## G4 — contract tests (only if G2+G3 exist)

- `backend/tests/test_extraction_contract.py`: schema rejects prose; `unknowns` honored (absent/empty where evidence missing passes, fabricated values fail); repair retried exactly once then step fails (prove with the fake's invalid-once shape: invocations == 2, second valid); `needs_evidence` output produces the manual-entry task (assert the open task row, not a mock); corpus integrity (every fixture has ground truth; every ground truth has an expectation class).
- FAIL-then-PASS (`PG-EV-01`/`PG-EV-09`): PRE-change FAIL + POST-change green, BOTH raw runs committed to `docs/worklogs/SG-026_verify.log` and quoted from it. Full suite green-except-base-proved-reds (bound 600s); eval smoke run completes inside 600s with numbers quoted; `ruff` clean; `mypy` quoted (untouched-file advisories are findings with destinations, never silent).
- Read-back statement (`PG-SC-02`): schema fields are read back by these tests + the eval scorer; the PRODUCTION reader arrives SG-028 — state that explicitly.

## G5 — worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-026.log`, `{{WORKLOG_DIR}}/SG-026_report.md`, `{{WORKLOG_DIR}}/SG-026_verify.log` (both raw runs). First token `SG-026`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments (owner rule); live-state ledger; no secret literal anywhere (grep-gated, `PG-SC-05`).

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
- Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-026 | Report: docs/worklogs/SG-026_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Verify with `show <WORK_HEAD>` and QUOTE executed output. Existing-note refusal is a STOP (never force-replace). Final line reads `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `prompts/` new + `schemas.py` [+ `extraction.py` iff quoted-necessary] + `needs_evidence` bridge touch inside `expiry_tracker.py` ONLY (capped diff, no step/job/api changes) + `backend/eval/*` + 1 test file + `docs/worklogs` (3 files). Prior quarantine refs never adopted. Anything else is a STOP with evidence. One L3 retry covers transients only, root cause or nothing.
- Cross-product (`PG-IC-01`): G2 needs only SG-025's protocols/router/fake shapes; G3 only the listed manual-entry sites + `audit_event`; G4 only the fake; G1 only host gates + count probe. Recorded once.
- Secrets: names and counts only (`CO-44`). No real SDK/key/network: any such import is a STOP with the grep quoted (`PG-SC-05`: excluded by rule). Privileged-denial: exact text, never route around (`PG-PR-03`).
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suites, 600s eval smoke, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): verify before asserting; no new checklists.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first). Live SG-025 surface confirmed (protocols/router/fake/ledger present or finding explained).
- G2: two versioned prompt files + strict schemas; prose input fails validation (quoted); repair fires exactly once then step fails (invocation counts quoted).
- G3: `needs_evidence` yields the existing manual-entry task (open-task row quoted, no new task type, no job-step edit); eval scores the 5-fixture corpus with baseline numbers quoted AND committed to `backend/eval/baseline_sg026.md`; no tuning performed.
- G4: PRE FAIL + POST green BOTH quoted from the committed verify log; corpus-integrity green; full suite green-except-base-proved-reds; ruff clean; mypy quoted. MODEL + effort provenance quoted (owner rule). No vacuous pass.
- Q2 count quoted (never a gate; no secret literal — grep-gated). Worklog + report + verify log committed; notes ref carries `Dispatch-ID: SG-026` + `Report:`, quoted executed output, result `note=yes`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments.

## Budget

120s probes, 600s suites, 600s eval smoke, 1800s early-close, 2400s overall.
