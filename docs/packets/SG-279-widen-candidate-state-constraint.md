# SG-279 — One migration widens the candidate state constraint, so split and merge can work on a migrated database

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** This slice does not deploy; rider SG-280 does. Until then the live app stays as it is (`PG-PR-05`): the code already writes these states and the live database already refuses them.
**Provider: none.** No key, no `.env`, no spend.

**Contract chain:** recorded `0.56.0` (`AGENTS.md`) == published `contract-v0.56.0` == the host's contract, echoed by this report from `/home/andrei/storagegenie-contract/CODER.md` line 3. A different echo is a finding.

**Approval:** owner, stage C, D16: *"D16 - ok."* Design reviewed in SG-277 and SG-278 (`docs/worklogs/SG-278_report.md`; row in `docs/reviews/review-ledger.md`).

**Previous report's open items:** `docs/worklogs/SG-276_audit.md` I1 is this slice.

## Why this exists

The live `candidate` table refuses two states the code writes. SG-276's read of the live schema quotes `CHECK (state IN ('proposed', 'accepted', 'edited', 'held', 'rejected'))`; the code writes `split` and `merged`. The constraint comes from `backend/alembic/versions/20260908_sg014_candidate.py:31`. `Candidate` (`backend/app/services/candidates.py:496`) declares no constraint, and `test_review_split.py`, `test_sg270_flow.py` and `test_sg112_merge.py` build tables with `create_all`, so 781 green tests never met the migrated schema. `UNVERIFIED — inference, not driven live:` a split on the live app fails at the database.

## G0 — Preflight

`DOCKER_CONFIG` to a writable temp directory, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-279/docker.sock`, `docker version` shows a **Server** section, `docker run --rm busybox true` rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch goes in `output/SG-279-scratch/`, removed by exact path; never touch `output/` itself or `output/dispatch`.

## G1 — The migration and the model

One new migration, `down_revision = "20261023_sg233_reminder"`, widens `ck_candidate_state` to the states the code writes, keeping the constraint's name. The model declares the same constraint, so `create_all` schemas match. No other schema change.

**The set is a criterion, not a list:** enumerate every state the code assigns to a candidate and report it. Expected seven: `proposed`, `accepted`, `edited`, `held`, `rejected`, `split`, `merged` (`candidates.py` `SPLIT_ORIGIN_STATE`; `api/v1/candidates.py:134`). A different set, or any existing test that stores a state outside it once the model declares the constraint, is a STOP and report. Stopping there is a success.

Facts the design turns on, each a hypothesis to falsify:

- SQLite cannot alter a CHECK in place, so this is a table rebuild. The repo's precedent is `op.batch_alter_table` in `20260916_sg048_name_optional.py:117,138`. That file also removes the FTS view when rebuilding `asset`; `fts.py:46-82` hangs the view and three triggers on `asset`, not `candidate`, so **do not import that workaround** unless you find it needed.
- `UNKNOWN to me, establish before choosing:` whether batch mode on this Alembic and SQLAlchemy keeps the named CHECK on reflection or needs it dropped and recreated explicitly. Read the installed versions rather than remembering them.
- No foreign key targets `candidate` (the SG-278 search of migrations; `ReviewTask.subject_ref` is a plain string, `models/review_task.py:14-18`). This matters because dropping a table with foreign key enforcement on deletes its rows first, and that would cascade to any child. Enumerate from a migrated schema's `sqlite_master` and `PRAGMA foreign_key_list` of every table.
- `backend/alembic/env.py:22-23` overwrites Alembic's URL from `settings.database_url`, and `:35-44` makes its own engine, while `backend/app/db.py:22-27` enables foreign keys only on the app's engine. So establish how a test points Alembic at its temporary file, and whether the migration connection enforces foreign keys. State both in the report.
- The two `sa.DateTime` columns have `server_default` `(CURRENT_TIMESTAMP)` and the two indexes are `ix_candidate_job_id` and `ix_candidate_household_id` (`20260908_sg014_candidate.py:29-37`). They must survive the rebuild.

The downgrade restores the five-state constraint. **With any `split` or `merged` row present it refuses before changing anything**: same revision, data and schema afterwards.

**`PG-SC-11`:** grep for every assertion relative to the migration head (the literal `20261023_sg233_reminder`, "head", `[-1]`, "latest" in `backend/`), list the hits in the report, and update any this append makes false.

## G2 — Tests on a migrated schema

New file `backend/tests/test_sg279_candidate_state.py`, on one temporary database file built by **Alembic to head**, its path and revision recorded in the test output. Other tests keep `create_all`.

- **A real split and a real merge through their routes**, with the app's own connection behaviour (foreign keys on), read back **in fresh sessions on that same file**: origin state, children, loser state, survivor. Routes commit at `api/v1/candidates.py:207,229`; a seed session's cached objects prove nothing.
- **All seven states stored and an invalid one refused** on that schema, each attempt in its own transaction, so one refusal cannot spoil the next assertion.
- **Parity:** the model's `ck_candidate_state` and the migrated schema's accept the same set, read from `Candidate.__table__` and from `sqlite_master`.

Write the tests first. Run the route tests with **no migration and no model change**: they must FAIL and the failure text must name `ck_candidate_state`. A failure for another reason means the test is wrong. Commit that run as `docs/worklogs/SG-279_fail_routes.log` and the passing run as `docs/worklogs/SG-279_pass_routes.log` (`PG-EV-09`).

## G3 — Rehearse the upgrade and the downgrade

On a temporary database **populated at the old head by running the migrations to `20261023_sg233_reminder`**, not by `create_all`. Candidates in all five existing states; a real asset that the FTS index finds. Commit it as a test or a script under `backend/tests/` and say which; its output goes to `docs/worklogs/SG-279_rehearsal.log`.

Compare before and after, from raw `sqlite_master` and raw column values:

- every candidate column of every row, timestamps as stored; indexes; foreign keys; server defaults;
- every other object's definition, FTS view and triggers included, and every table's row count;
- an FTS search for the seeded asset returning it on both sides;
- `integrity_check` and `foreign_key_check` after the upgrade.

The expected difference in the schema text is the `candidate` table's own, with the accepted set changed. **Report the actual text diff.** Any semantic difference beyond the accepted set is a STOP and report; a difference only in whitespace or quoting is reported and passes, and you say why it is only that.

Then the downgrade both ways: **success** with no new-state rows, the five-state constraint back and data intact; **refusal** with a `split` row and again with a `merged` row, revision, data and schema unchanged, each compared rather than assumed.

Report in one line each, for the rider: the new revision id; whether Alembic on this database wraps the rebuild in a transaction, as established rather than remembered; and the Alembic invocation that reached the temporary file.

## G4 — The gate

First the targeted tests. Then `make backend-test` once (host suite green, the two marked tests **deselected**, image proof) and `make frontend-test` once only if a frontend file changed, which none should. Quote exact counts (`PG-IC-08`). The image proof shows the new migration is in the image.

Run the new test file **twice consecutively** (`PG-DP-04`). `ruff check` on **every changed file** (`PG-EV-15`); the repo-wide mypy reds are out of scope.

## Acceptance criteria

- **A1** — A split and a merge through the routes commit on a schema built by Alembic, read back in fresh sessions.
- **A2** — FAIL before the change names `ck_candidate_state`; PASS after; both logs committed.
- **A3** — The enumerated states equal the set the constraint accepts; an invalid state is refused; model and migrated schema agree.
- **A4** — The rehearsal log shows row values, other objects and counts unchanged, FTS search working, and integrity and foreign key checks clean. A criterion passes only if the same comparison **fails on a deliberately altered row or object**, shown once in the log (`PG-EV-01`).
- **A5** — Downgrade succeeds with no new-state rows, and refuses with either new state leaving everything unchanged.
- **A6** — `PG-SC-11` hits listed; host suite green; new test file run twice; counts quoted; `ruff` clean on changed files.
- **A7** — Scope is only the files below; zero live-database, host, running-container, deploy, Dockerfile, compose, lockfile, dependency or provider bytes.
- **A8** — Preflight proven before the gate; health 200 at start and end.
- **A9** — `PB-3` vacuity: a failure here would look like a route error naming the constraint, a missing index, a changed value or a lost row. Say which of these you checked for and that none was observed.
- **A10** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed product files:** one new file in `backend/alembic/versions/`, `backend/app/services/candidates.py` (the `Candidate` model only), `backend/tests/test_sg279_candidate_state.py`, a rehearsal script under `backend/tests/` if it is not in that test file, and any test `PG-SC-11` shows is made false.
- **Reads of any file are allowed.** The only runtimes authorised are the preflight, the `make` gate, the tests, Alembic on temporary files, and the docker commands those use.
- Evidence: `docs/worklogs/SG-279*` only.
- **No changes** to `backend/Dockerfile`, `docker-compose.yml`, `backend/requirements.lock`, any dependency, `.env`, the **live** running container, its image tag, the host's packages, the live database, the stored files, or any provider. **No deploy and no migration against anything but a temporary file.** Test rows live only in temporary files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`). No browser; no network in the tests.

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **300 s**; one test file **300 s**; one Alembic run **120 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1500 s.** A partial slice with a receipt is a success. Order: G0, G2's failing run, G1, G2's passing run, G3, G4. Expected ≈700 s (`UNVERIFIED — my estimate`, from SG-262's 991 s for a larger slice).

## Report

Destination: `docs/worklogs/SG-279_report.md`, evidence logs beside it (`docs/worklogs/SG-279_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈700 s expectation and names every phase over 60 s. It lists the changed files, the test counts, the logs, the contract echo, the G3 report lines, and every `UNCLEAR` / `REMAINING` line. Each constraint gets a line.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-279 | Report: docs/worklogs/SG-279_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
