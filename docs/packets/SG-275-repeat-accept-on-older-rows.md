# SG-275 — Accepting an already committed candidate from before SG-270 must not create a second item

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** This slice does not deploy; its rider does.
**Provider: none.** No key, no `.env`, no spend. Scripted provider only.

**Contract chain:** recorded `0.56.0` (`AGENTS.md`) == published `contract-v0.56.0` == the host's contract, echoed by this report from `/home/andrei/storagegenie-contract/CODER.md` line 3. A different echo is a finding.

**Previous report's open items:** `docs/worklogs/SG-270_audit.md` I1 and I2 are this slice. The other `REMAINING` lines have destinations there and are not this slice's work.

## Why this exists

The SG-270 audit reproduced a regression on a temporary database, at `24e9d38`, the same flow with and without the `committed_assets` map (asset count, then `created`):

```
CONTROL (1, False)
OLD_ROW (2, True)
```

The map exists only on commits made since SG-270. `_prepare_commit_steps` (`backend/app/api/v1/candidates.py`) reopens the commit step for any accepted candidate, so a candidate committed earlier makes a second item. The live database holds such candidates (`docs/worklogs/SG-269_audit.md` I1: *"10 candidates against 7 assets"*), the new Inbox list reaches them, and Accept stays enabled on them. **The deploy is held on this.**

## G0 — Preflight

As in `docs/packets/SG-270-flow-fixes.md` G0, with this slice's socket: `DOCKER_CONFIG` to a writable temp directory, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-275/docker.sock`, `docker version` shows a **Server** section, `docker run --rm busybox true` rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch goes in `output/SG-275-scratch/`, removed by exact path; never touch `output/` itself or `output/dispatch`.

## G1 — One item, on older rows too

A repeat accept or edit of a candidate that already has an item returns that item with `created` false, and creates nothing, whenever it was committed.

Expected (each a hypothesis to falsify):

- `_prepare_commit_steps` reads the review step's output and resets the commit step's `output_refs` to None. The commit step's output, before that reset, holds the earlier `candidate_id` and `asset_id` (`backend/app/services/job_service.py:194-195`, `backend/app/services/candidates.py`, `commit_job_candidate`).
- The smallest fix: before the reset, when that output names this candidate and an asset id, add it to `committed_assets`. Then the existing branch in `commit_job_candidate` returns it. **If a smaller or sounder way exists, take it and say why.**
- A candidate whose commit failed has no asset id there, so its retry still commits. Prove it.
- A job's commit output names only the latest candidate. **Establish** whether any older row can have an item its commit output no longer names (expected none: before SG-270 a job committed once, and split children could not commit). Report the answer with the reasoning.
- The asset's household is checked before it is returned, as the existing branch does.

## G2 — Remove the fallbacks

Remove `candidate.blocking_review_task_ids ?? candidate.review_task_ids` (`frontend/src/components/CandidateCard.tsx`, `frontend/src/routes/ReviewPage.tsx`) and `task.subject_kind ?? "candidate"` (`frontend/src/routes/InboxPage.tsx`). The backend always sends both fields, and the types mark them required. Test fixtures that omit them gain them.

## G3 — Tests and the gate

- **The required case is a row as SG-270's base left it:** review step output with no `committed_assets`, commit step output as a real earlier commit wrote it. Build it by running a real commit, then removing only the map. Assert one item and `created` false. The test FAILS on the base and PASSES on the candidate; commit both runs as `docs/worklogs/SG-275_fail_*.log` and `SG-275_pass_*.log`. Fixture module: `backend/tests/test_sg270_flow.py`, in scope. Also cover: edit as the repeat action; a failed commit retried creates one item; a new row still works.
- First the targeted tests and `tsc`. Then `make backend-test` once (host suite green, the two marked tests **deselected**, image proof) and `make frontend-test` once. Quote exact counts (`PG-IC-08`).
- Run the affected test files **twice consecutively** (`PG-DP-04`). `ruff check` and `eslint` on **every changed file**; the repo-wide mypy reds and the one `eslint` error in `App.household-nav.test.tsx` are out of scope. Prove the deploy's frontend build step exits 0 (`PG-SC-12`).

## Acceptance criteria

- **A1** — A repeat accept and a repeat edit on an older row each return the existing item with `created` false; the item count stays 1.
- **A2** — A failed commit retried creates exactly one item. A new row behaves as before.
- **A3** — The older-row question in G1 is answered in the report.
- **A4** — The fallbacks are gone and the frontend suite is green.
- **A5** — FAIL-then-PASS with both logs committed; suites green; affected files run twice; build rc 0; counts quoted.
- **A6** — Scope is only the files below; zero schema, migration, Dockerfile, compose, lockfile, dependency, model, database, host, provider, running-container or deploy bytes.
- **A7** — Preflight proven before the gate; health 200 at start and end.
- **A8** — `PB-3` vacuity: a failure would look like an item count of 2, or `created` true on a repeat. Neither may be the observed result.
- **A9** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed product files:** `backend/app/api/v1/candidates.py`, `backend/app/services/candidates.py`, `backend/tests/test_sg270_flow.py`, `frontend/src/components/CandidateCard.tsx`, `frontend/src/routes/ReviewPage.tsx`, `frontend/src/routes/InboxPage.tsx`, and their existing test files.
- **Reads of any file are allowed.** The only runtimes authorised are the preflight, the `make` gate, the tests and the frontend build.
- Evidence: `docs/worklogs/SG-275*` only.
- **No changes** to schema, migration, `backend/app/models/**`, `backend/Dockerfile`, `docker-compose.yml`, `backend/requirements.lock`, dependency, `.env`, the **live** running container, its image tag, the host's packages, the database, or any provider. **No deploy.** No data repair.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`). No browser; no network in the tests.

## Hang bounds

Preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1500 s.** A partial slice with a receipt is a success. Expected ≈500 s (`UNVERIFIED — my estimate`, a far smaller slice than SG-262's 991 s).

## Report

Destination: `docs/worklogs/SG-275_report.md`, evidence logs beside it (`docs/worklogs/SG-275_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈500 s expectation and names every phase over 60 s. It lists the changed files, the test counts, the FAIL-then-PASS logs, the contract echo, and every `UNCLEAR` / `REMAINING` line. Each constraint gets a line.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-275 | Report: docs/worklogs/SG-275_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
