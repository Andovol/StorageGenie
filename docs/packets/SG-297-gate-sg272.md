# SG-297 — Run the full gate on SG-272's work, fix what it finds, and fix the task-list paging slip

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** No deploy; the rider follows this slice.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.58.0` (`AGENTS.md`). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line as you received it. A denial on that folder is expected and is not a STOP.

**Approval:** owner, stage C (*"d14 ok"*, L3), and *"Start SG-272"* (2026-11-09). This finishes SG-272.

## Why this exists

SG-272 (`391e6c8..3dcfd82`) built gone, put back and quantities, with 6 backend and 14 frontend new tests green, then stopped at its 1300 s stop rule **before the full gate** (`docs/worklogs/SG-272_report.md`: *"Verification: FAIL — full gate not run"*). Nothing deploys ungated. The audit (`docs/worklogs/SG-272_audit.md`) also found:

- **I2** — `GET /v1/review-tasks` (`backend/app/api/v1/review_tasks.py`, SG-272 hunk "SG-272 G1/G2: a gone item's asset-subject tasks hide…") drops gone items' tasks **from an already-paginated page**, so a page can come back short, and `total` still counts them.
- **I3** — that filter uses the literal `"ACTIVE"` instead of the shared rule in `backend/app/services/lifecycle.py` (`ACTIVE`, `active_clause()` at ~`:92`).

## G0 — Preflight

`DOCKER_CONFIG` to a writable temp directory, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-297/docker.sock`, `docker version` shows a **Server** section, `docker run --rm busybox true` rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make and `ruff` invocation (SG-272 found the venv `python` missing once: if it is missing, report the exact error and STOP — do not install anything). `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch in `output/SG-297-scratch/`, removed by exact path; never touch `output/` itself or `output/dispatch`.

## G1 — Fix I2 and I3 first

- Apply the gone filter **in the query, before pagination**, so a page holds up to its limit of visible tasks and the cursor stays correct. `total` counts what the list shows. Expected: tasks whose subject is an asset that is not ACTIVE are excluded; tasks whose subject is a candidate are unaffected. **Establish** how the query distinguishes the two (`subject_kind`, `subject_ref`) before writing it.
- Use `lifecycle.ACTIVE` / `lifecycle.active_clause()`; no status literal.
- Test (in `backend/tests/test_sg272_flow.py`, in scope): with a page limit of N and one gone item's task among the first N, a page returns N visible tasks and `total` excludes the hidden one. FAIL on the base, PASS after; logs `docs/worklogs/SG-297_fail_tasks.log`, `SG-297_pass_tasks.log` (`PG-EV-09`). **Keep FAIL logs short:** the failing test names and the first assertion only.

## G2 — The full gate, once, on the candidate

In this order, quoting exact counts (`PG-IC-08`), each into its own log `docs/worklogs/SG-297_<step>.log`:

1. `ruff check` on **every backend file SG-272 or this slice changed** (`git diff --name-only 391e6c8..HEAD -- backend/`) (`PG-EV-15`).
2. `eslint` on every changed frontend file; `tsc --noEmit`; the deploy's frontend build step rc 0 (`PG-SC-12`). The one pre-existing `eslint` error in `App.household-nav.test.tsx` and the repo-wide mypy reds are out of scope.
3. `make backend-test` once (host suite green, the two marked tests **deselected**, image proof).
4. `make frontend-test` once.
5. Every SG-272 and SG-297 test file **twice consecutively** (`PG-DP-04`).

**A red is fixed here if, and only if, the fix stays inside SG-272's own files and does not change what SG-272 does on screen or in the API.** Then re-run that step and say what you changed and why. A red that needs anything else — another file's behaviour, a design change, a test that asserts old behaviour SG-272 deliberately changed and whose new expectation you are unsure of — is a **STOP and report** with the failing test names and first assertion; stopping there is a success. An old test that fails on the candidate is also run alone on the base (`D443`) and the report says whether it failed there too.

## Acceptance criteria

- **A1** — I2: a page returns its full count of visible tasks and `total` excludes hidden ones; FAIL-then-PASS logged. I3: no status literal in the filter.
- **A2** — `ruff`, `eslint`, `tsc` clean on the named files; build rc 0.
- **A3** — Backend suite green with the two marked tests deselected, image proof passing; frontend suite green; counts quoted.
- **A4** — SG-272 and SG-297 test files green twice consecutively.
- **A5** — Every fix to a red named with its reason, or a STOP with the failing names.
- **A6** — Scope is only the files below; zero schema, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes.
- **A7** — Preflight proven; health 200 at start and end.
- **A8** — `PB-3` vacuity: a failure would look like a short page, a `total` counting hidden tasks, a lint or type error, a red suite row, or a test that passes once and fails the second time. Say which you checked and that none was observed.
- **A9** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Product files:** `backend/app/api/v1/review_tasks.py`, and the files SG-272 changed (`git diff --name-only 391e6c8..3dcfd82`, excluding `docs/`), only to fix a gate red as G2 allows. Tests: `backend/tests/test_sg272_flow.py` and SG-272's frontend `*.sg272.test.tsx` files. **Any other product file is a STOP and report — do not change it and disclose** (`PG-EV-03`).
- **Reads of any file are allowed.** Authorised runtimes: the preflight, the `make` gates, the tests, `ruff`, `eslint`, `tsc` and the frontend build. **No browser, no local app server, no other container image, no package install.**
- Evidence: `docs/worklogs/SG-297*` only.
- **No deploy, no restart, no touch of the running container or its image tag, the live database or the stored files.** Test rows live only in temporary files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **At 1300 s elapsed, stop whatever step you are in, commit, report, publish** — a stop rule, not a target. Order: G0, G1, G2 steps 1–5. Expected ≈500 s (`UNVERIFIED — my estimate`; SG-271's full gate took ≈200 s of its run).

## Report

Destination: `docs/worklogs/SG-297_report.md`, evidence beside it. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: elapsed against ≈500 s with every phase over 60 s named; each gate step's count; every red found and what was done; changed files; the contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint.

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-297`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-297 | Report: docs/worklogs/SG-297_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
