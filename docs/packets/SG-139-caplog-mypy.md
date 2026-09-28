# SG-139 — Green the suite: non-disabling fileConfig + dedup Row types, fail-then-pass

**Settings travel on the trigger** (`SG-139 coder=opencode effort=high`, D8) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** D8-authorized micro-slice (owner quote "D8 - approved"): SG-135 (98) left two known defects, both root-caused in its report. (1) F-SG135-1: `test_health.py::test_health_reports_database_failure` (`test_health.py:36-53`: `BrokenSession.execute` raises `RuntimeError("database probe failed")`, asserts 503 + body + `"Database health check probe failed" in caplog.text`) passes in isolation but fails under full-suite ordering (`caplog.text == ''`) because `backend/alembic/env.py:20` calls `fileConfig(config.config_file_name)` with the default `disable_existing_loggers=True`, globally disabling `app.api.v1.health` once any migration test runs earlier. (2) F-SG135-2: mypy +3, all in `backend/app/services/dedup.py` — `_similar_matches` (`dedup.py:43-65`) annotates `phash_rows: list[tuple[Observation, Asset]] | None` but assigns `db.query(Observation, Asset)...all()` (`list[Row[...]]`) and unpacks `for row, asset in phash_rows` (`arg-type` + `assignment` + `union-attr`). THIS slice fixes both + proves with fail-then-pass. **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-135's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** TWO-FIX slice. Writes: `backend/alembic/env.py` (one line), `backend/app/services/dedup.py` (annotation + import only), `docs/worklogs` (3 files) — and NOTHING else. No migration content change (env.py is config, not a version — prove by empty diff over `backend/alembic/versions/`), no behaviour change (logging enablement + annotations only — prove by full-suite green + byte-identical served routes), no rebuild/recreate (unserved until a rider word; `PG-PR-04` stated). Secrets: none touched (`CO-100` — no credential within ten lines of either hunk; assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-07` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (no version change — empty `backend/alembic/versions/` diff quoted). Restart: none. Deploy: none.**

## G0 — reproduce both defects on BASE (fail-pre, committed — `PG-EV-09`)

- Run the FULL backend suite on the unmodified tree and quote: the `test_health_reports_database_failure` red (`caplog.text == ''`) + current mypy `app` count (expectation: 44 errors / 10 files — differenced either way). Commit this capture to the verification log FIRST — a fix without a committed red proves nothing.
- `PG-IC-08` blast radius: expected failing set = exactly {`test_health_reports_database_failure` + 2 `test_signals` env reds}; a FOURTH red stops the run (report, don't fix around it).

## G1 — fix both (two hunks, decided shape stated, Coder owns the final form)

- `env.py:20`: pass `disable_existing_loggers=False` (expected one-line shape — if the call needs restructuring, decide and report). Constraint: migration runs must still configure logging (prove: an offline `alembic upgrade --sql` or `current` still emits; quote it).
- `dedup.py`: make the annotation true of the value (expected: `Row`-aware annotation + import — if a conversion at the boundary reads cleaner, decide and report). Constraint: runtime behaviour byte-identical (prove: `_similar_matches` callers + `test_dedup.py` green).
- Fail-post: FULL suite — `test_health_reports_database_failure` green in-suite (quoted), total reds == the 2 `test_signals` env reds only (both re-shown failing on bare BASE per `PG-SC-12` — derive BEFORE at the base commit); mypy `app` errors back to the pre-#20 count with zero new files carrying errors; ruff clean. Both runs (pre + post) committed to the verification log.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-139.log`, `SG-139_report.md`, `SG-139_verify.log` (fail-pre + fail-post captures, suite/mypy/ruff, empty-versions proof, `alembic current` proof). First token `SG-139`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — `alembic/env.py` (logging-config line only), `dedup.py` (annotation + import only), the 3 worklog files. **Any other write — versions/, served routes, tests, suite files — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs full-suite + mypy reads (600s class bound for suites); G1 needs the two hunks + proofs (modify-versus-call: tests CALL the fixed paths through the real suite, never a hand-rolled harness); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): one kwarg, one annotation. No logging overhaul, no dedup refactor, no test rewrite — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): logging — does the caplog test hold under full-suite ordering without touching the test? types — is the annotation true with no new mypy errors? safety — is the alembic-versions surface empty and migration output intact?
- Fail-pre red quoted from the commit + fail-post green quoted from the commit + suite reds == 2 base-proved env reds + mypy count back to pre-#20 with no new error files + `alembic current` output quoted + empty `versions/` diff + $0.000000 USD; no vacuous pass (an isolation-only green, a mypy count without the file list, or a missing pre-run evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-139 | Report: docs/worklogs/SG-139_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
