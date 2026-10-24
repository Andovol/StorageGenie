# SG-238 — D-1024-6 + the two queued audit fixes: durable scope gates, a daily-pass success log line, and the two always-red signal tests proved environmental

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.** Scratch temp SQLite only; the production SQLite is not read and not written by this slice. **Restart: none.** No service, container, image, nginx or host operation of any kind — the image run in G3 is a **new, throwaway container** from the already-built local image, with no bind mount and no write to any existing container.
**Autonomy: L2.** Settings ride the trigger, never this packet. No production write of any kind.

**Context and standing lines.** Three items, all queued by this session's audits, all owner-approved where the owner was asked. Expected premises, all re-verified in-slice per `PB-1` (a difference is a finding, not an obstacle): (a) `backend/tests/test_sg233_reminders.py::test_sg233_diff_touches_only_the_approved_ceiling` asserts that the branch range `origin/automation...HEAD` equals **its own historical set** (one migration path) — it is therefore **red on every slice after SG-233**, including on the base, because the range empties once the branch is published; (b) `backend/tests/test_sg235_daily_caller.py::test_sg235_diff_touches_only_the_approved_ceiling` asserts that the same range contains the seven SG-235 product paths — equally **red once the branch is published** (SG-235 audit, and SG-236's report I10); (c) `backend/app/services/reminders/daily.py` logs **failures only** (`logger.exception` at two places) — it emits no line saying a pass ran, how many households it visited or how many reminders it created (SG-236 audit, SG-237 finding F2); (d) `backend/tests/test_signals.py` has two reds on this host — `test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `test_ocr_has_text_boxes_and_mean_confidence` — because the host's Python environment lacks the `libzbar0` and `tesseract` **system** libraries; the project's own image installs both (`backend/Dockerfile`: `apt-get install tesseract-ocr libzbar0`) and `backend/requirements.lock` carries `pytest==9.1.1`, `pytest-asyncio`, `pillow-heif`, `pytesseract` — so the same tests can run **inside the image**; (e) the image tag `storagegenie-backend:latest` exists locally (built by SG-236, image `2bd3599f`); (f) contract recorded `0.52.0` == published payload `0.52.0` == host copy `0.52.0` (SG-235, SG-236, SG-237 echoes).

**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback plus container-runtime only, nothing else.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked:** `PG-EV-01` seen-to-fail · `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-05` property-not-command · `PG-EV-07` real-source · `PG-EV-11` advisory-first · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-06` runtime-versus-budget.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

## Why this exists

Three debts this session's audits recorded, all of which make every later slice harder to trust:

1. **Two scope gates are red on every later slice.** Each asserted a *branch range* (`origin/automation...HEAD`) against its own historical file set — a property that cannot survive publication, so the gate is red on the base and on every candidate after it. They are noise, not signal (`G-A7`), and they cost two audits (SG-235, SG-236) a base-proved red each.
2. **The daily pass is unobservable.** It logs failures only, so no rider can see a pass run — which is exactly why SG-236 could only *infer* the pass and why SG-237's row had to be proven from the table instead of the log.
3. **Two suite tests are red for an environment reason** (`libzbar0`, `tesseract` missing on the host) and have masked real signal in every run since they appeared (SG-233, SG-235, SG-236, SG-237 each had to base-prove them).

## G1 — two durable gates instead of two branch-range gates

Replace both `*_diff_touches_only_the_approved_ceiling` tests with checks that **survive publication** and still fail when they should. The property each replacement must have:

- it does **not** depend on the branch's tip, the branch range, or the commit under test;
- it still **fails** when the thing it guards is wrong — and you show that failing (below);
- it guards something durable, not a moment.

The durable thing each slice's gate can guard: **the paths that slice shipped still exist in the tree** (a deletion tripwire) — SG-233's migration, model, service, API and page; SG-235's daily module, served entrypoint, `main.py`, Dockerfile, test module and the two frontend files. The mechanism is yours (report what you chose and why); the three properties above are not. **Do not write a gate that can only fail while a slice is in flight** — a check that reads the branch tip has this slice's problem again.

`PG-EV-01`: show each new gate **failing** in the same run — point it at a path that does not exist (or plant the absence it guards) and quote the failure — then restore and quote the green. A gate that was never seen to fail is decoration.

## G2 — the daily pass says what it did

`backend/app/services/reminders/daily.py` gains **one success log line per pass** — the pass's day, the households visited, the reminders created, and the errors — at a level the line is readable by an operator and by a test. Keep the existing failure logging as it is.

- The line is emitted **once per pass**, at INFO, with the counts (not the row objects).
- A test in the existing daily-caller module (`backend/tests/test_sg235_daily_caller.py`) captures it (`caplog` is available in this project — see `backend/tests/test_sg139_caplog_mypy.py`) and asserts the line exists with the right counts after a pass that created a known number of reminders, and that the numbers are the pass's real numbers, not a constant.
- The line must not leak household names or asset ids beyond what the counts need — the day's date and the counts are enough.

## G3 — the two red signal tests: prove the cause inside the project's own image

Run the two red tests **inside the already-built image** (`storagegenie-backend:latest`, image `2bd3599f`), which installs `tesseract-ocr` and `libzbar0` and carries pytest: a throwaway container, **no bind mount**, no write to any running container, no build. Report the result as observed.

- **If both pass inside the image:** the reds are environmental — state that, and record the runnable command as a **Makefile target** (e.g. `make backend-test-image`) so any later session can repeat it in one command. **Then, only if** the lane's identity can install the two system packages **without a password prompt** (probe once with `sudo -n true`), use the owner's authorisation (D-1024-6) to install `libzbar0` and `tesseract` on the host and re-run the two tests on the host to green. **If `sudo -n` is unavailable or denied, attempt no workaround and change nothing on the host** — report it (`PG-PR-03`); the host install then needs a path the owner must authorise separately.
- **If they still fail inside the image:** that is a **code** finding, not an environment one — say so, name the failing assertion, and give it a destination; do not touch the host either way.
- Either way: the **host** suite result before and after is quoted with the same counts, and the report states plainly which reds remain and why.

## Constraints

- Scope ceiling: `backend/tests/test_sg233_reminders.py` · `backend/tests/test_sg235_daily_caller.py` · `backend/app/services/reminders/daily.py` · `Makefile` (one target) · `docs/worklogs/SG-238*`. **Anything else is a STOP** — including `backend/app/api/v1/*`, `backend/app/models/*`, `backend/app/services/reminders/service.py`, `backend/app/server.py`, `backend/Dockerfile`, `frontend/**`, `README.md`, `docker-compose.yml`, `.env`, and any migration.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued; every acceptance criterion below names a ceiling file above. G-hunks share no condition with any remediation step — stops win.
- How code becomes live (`PG-PR-04`): the G2 log line becomes live at the **next** close-deploy rider, not in this slice; the report states that the served app still has the old module.
- No full-suite sweep on a container: the backend suite runs on the **host** environment (as it does today); the image run is scoped to the two signal tests.
- Runtime-versus-budget (`PG-PR-06`): elapsed per leg against the lane budget, in seconds; the image run's duration reported with its unit.
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`). No prompt or polling loop. No secret in any artifact.

## Acceptance criteria

- **Q1 (gates):** neither gate depends on the branch tip; both are green on a later slice's tree; **both were seen to fail** in this run (quoted failure, then quoted green); the durable thing each guards is named.
- **Q2 (log line):** one pass emits exactly one success line carrying the day, the households visited, the reminders created and the error count; a committed test captures it and asserts the real counts (not a constant); the existing failure logging still works.
- **Q3 (signal tests):** the two tests' result inside the image is quoted as observed; the host suite's before/after counts are quoted with the reason each remaining red remains; the repeatable command is recorded in the Makefile; **no host change** unless `sudo -n` succeeded, and then the install and the re-run are quoted.
- **Worlds named (`PG-SC-09`):** passes-but-wrong = a gate that was rewritten to assert nothing (ruled out by the seen-to-fail demonstration) or a log line with hardcoded numbers (ruled out by the test asserting the pass's real counts after a pass that created a known number); working-but-fails = the daily pass running with zero households (the line still appears, with zeros — that is a pass, not a failure).
- Full backend suite run **once** on the candidate with its counts quoted; `ruff` and `mypy` on the touched files clean; the diff touches ceiling paths only; no production data read or written; no dependency change; no ignored file staged; **no vacuous pass** (`PB-3`).

## Report

- Work dir `/home/andrei/StorageGenie`, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref:** push the work to `automation`, worktree clean (`CO-55`). Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-238 | Report: docs/worklogs/SG-238_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name, LIST the note contents and grep for this ID, `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- The report's LAST line is exactly one of: `Verification: PASS` — or `Verification: FAIL — <check>` naming the check that failed (`CO-104`).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s per command · 600s suite · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
