# SG-280 — Deploy rider: rehearse recovery on a copy, then run the one candidate state migration on the live database

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It writes only `docs/worklogs/SG-280*`, the scratch path, and one retained backup.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: the live app database, one approved migration.** `sqlite:////data/db/storagegenie.db`, on the host at `data/db/storagegenie.db`. This is a declared sensitive surface; this packet is the written plan the owner approved. **Any result other than the expected one, or any step outside this packet, stops the work and returns it to the owner.**
**Restart: one stop and one start of the backend container.**
**Provider: none.** No key is read or printed, no `.env` is opened by you, **no spend**. Scratch containers get no `env_file`.

**Authority, verbatim:** owner, D16: *"D16 - ok."*; D20: *"D20 - ok."* (`docs/decisions/2026-10-30-session-approvals.md`). Design: SG-277, SG-278, SG-282, SG-283; audit `docs/worklogs/SG-279_audit.md` I2 and I3.

**Contract chain:** recorded `0.56.0` (`AGENTS.md`) == published `contract-v0.56.0` == the host's contract. Report it; a different version is a finding.

## Why this exists

The code writes candidate states `split` and `merged`, and the live table refuses them. SG-279 (rated 90) built the fix. **Alembic runs non-transactionally here** (`docs/worklogs/SG-279_rehearsal.log:2`), so an interrupted migration can leave a half-done table, and that recovery path has never been run. The migration also rebuilds from a hand-written copy of the table (`backend/alembic/versions/20261102_sg279_candidate_state.py:28-72`), so it applies only if the live table matches.

## Recovery states — these bind every goal, and they win over any other instruction here (`PG-IC-03`)

| State | When | On failure |
|---|---|---|
| **S0** | Before the backend is stopped | Stop. The app was never touched |
| **S1** | Backend stopped, migration command not started | Start the **old image by its immutable id**. Nothing changed |
| **S2** | Migration command started, new image not started; a leftover `_alembic_tmp_candidate` counts | Restore the G4 backup, verify it as in G3, start the old image |
| **S3** | New image started; writers may have run (`backend/app/server.py:27-34`) | **No restore, no retry, no restart.** Leave things as they are and report at once. A restore is the owner's decision |
| **S4** | A recovery step itself failed or was denied | Leave the app **stopped**, report outcome `UNKNOWN`, no further attempt |

**A denial is a STOP (`PB-2`, `PG-PR-03`), never a reason to try another route.** A denial in S0 changes nothing. A denied live stop leaves the app running, which is S0. A denial in S1 or S2 during a recovery step is S4.

**Time guard:** do not start G4 if more than **1200 s** have elapsed since your start; report and stop, as S0. A partial slice with a receipt is a success. This keeps a budget kill out of the downtime window.

## G0 — Socket, pre-state and rights, changing nothing live

- `DOCKER_CONFIG` to a writable directory under `output/SG-280-scratch/`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-280/docker.sock`, and `docker version` shows a **Server** section. Scratch stays in `output/SG-280-scratch/`, removed by exact path at the end; never touch `output/` itself or `output/dispatch`.
- `curl -s http://127.0.0.1:8003/v1/health` quoted.
- Expected, hypotheses from `docs/releases/2026-11-02-sg270.md`: container `d972bc75`, image `sha256:96a66241`, head `20261023_sg233_reminder`, 29 tables, `asset` 7, `candidate` 10. **Record the full old image id; it is the recovery image.** A running image you cannot account for is a STOP.
- `git check-ignore` proves `data/db/SG-280-backup-probe.db` and `output/SG-280-scratch/x` are ignored (`PG-SC-10`). The first must match `data/db/*.db`. Otherwise STOP.
- **Rights, proven only on your own throwaway objects (`PG-PR-01`):** run a scratch `busybox` container with a bind mount under the scratch path and a label `sg280-scratch`, stop it, remove it, and `docker tag` the old id to a scratch tag and remove that tag. Never probe by stopping or restarting anything of the app's. `docker compose stop` on the live service cannot be proven in advance; that is accepted.

## G1 — Build the new image, no recreate

One `docker compose build backend`, rc 0; the running container is untouched. Record the new image id. The runtime diff between the old image and the new, over the served Python tree, is expected to be **exactly** `alembic/versions/20261102_sg279_candidate_state.py` and `app/services/candidates.py`; JS and CSS byte-identical. Any other difference is a STOP. The new image's id differing from the old's is required.

## G2 — Live inventory, read-only

Open the live database read-only. Record: `journal_mode`; every row of `sqlite_master` (type, name, tbl_name, sql); every table's count; the Alembic revision; `-wal` and `-shm` presence.

Build a reference database in the scratch path by running the migrations to `20261023_sg233_reminder` with the **new image** and scratch `DATABASE_URL`. Compare whole `sqlite_master`, with whitespace normalised:

- The live `candidate` text must equal the reference, which is expected to be `SG279_CANDIDATE_SQL_BEFORE` in `docs/worklogs/SG-279_rehearsal.log:47-60`.
- **Any difference in any object is a STOP in S0.** Report the difference verbatim; object definitions hold no owner data. Stopping is a success. A benign-looking difference is still the owner's to judge.

## G3 — Rehearse on copies while the app keeps running

The app stays up and serving throughout. All copies live under `output/SG-280-scratch/`. **They hold the owner's real data: never print a name, id or field value; counts and hashes only. Removed by exact path at the end.** Script and output: `docs/worklogs/SG-280_rehearse.py` (it must contain no data) and `docs/worklogs/SG-280_rehearsal.log`.

Take a copy of the live database with **SQLite's backup API** (expected: `sqlite3.connect(...).backup(...)` in a one-shot container with the live folder mounted read-only). `UNKNOWN to me, establish first:` whether a read-only mount works with the `journal_mode` from G2. If it does not, say so and STOP rather than mount it read-write. Each rehearsal below starts from a fresh file copy of this one.

1. **Upgrade on real data:** the new image upgrades a copy to head. Compare with the copy before: every candidate column by row hash, every other object's definition, every table count; `integrity_check`, `foreign_key_check`. Then in a transaction that is rolled back, store `split`, `merged` and an invalid state on one candidate: the first two accepted, the third refused naming `ck_candidate_state`.
2. **Interrupted migration, the worst point:** run the real migration with a one-shot wrapper that makes the process die with `os._exit` **immediately after `DROP TABLE candidate` and before the rename**, keyed on the statement text through a SQLAlchemy `before_cursor_execute` listener. Assert the damage landed: the process exit code, `candidate` missing or `_alembic_tmp_candidate` present, revision still old. **If the damage did not land, the rehearsal proves nothing: STOP.**
3. **Restore by the exact S2 procedure:** replace the damaged file with the backup copy, removing any `-wal` and `-shm` beside it. Prove the result: hash equal to the backup, `integrity_check`, `foreign_key_check`, head, all table counts.
4. **The old image reads it:** start the **old image by id** on that restored file, on no published port, with scratch `STORAGE_ROOT`, no `env_file`, no real storage mount. From inside the container `GET /v1/health` returns 200 and one read route returns 200. Its startup may write reminders; that is only the scratch copy. Remove the container.
5. **The check can fail (`PG-EV-01`):** give step 3's verification a deliberately truncated copy and show it refuses. This stands in for the failed-recovery branch: a refused restore is S4.

Any step not as expected: **STOP in S0**, app untouched.

## G4 — The live migration, in this order

Before starting, confirm no dispatch-unrelated container uses the file. Then:

1. `docker compose stop backend`; confirm not running, and no restart over 15 s. **State S1.**
2. Backup with SQLite's backup API to `data/db/SG-280-backup-<UTC>.db`, retained, not removed by you. Restore it to a scratch path and prove `integrity_check`, `foreign_key_check`, head and all table counts equal to the stopped live file.
3. `sha256` of the live file. **Now state S2.** One `docker compose run --rm --no-deps backend alembic upgrade head`.
4. Compare: `alembic` revision `20261102_sg279_candidate_state`; the live `sqlite_master` differs from G2 only in `candidate`, by the same text diff as G3 step 1; all table counts equal; candidate row hash equal; `integrity_check`, `foreign_key_check`; no `_alembic_tmp_candidate`.
5. `docker compose up -d --no-deps --force-recreate backend`. **Now state S3.** New container id, image id, `Cmd`, restart count, health status.

## G5 — The app answers

`/v1/health` six times, each quoted; shell routes `/`, `/expiry`, `/inbox`, `/planning` return 200. Startup log: no traceback or configuration error, and the daily pass's own line quoted. Census after: every table count compared with G2; **`reminder` may rise only as that line accounts for**; any other table moving is reported at once under S3. No split or merge is exercised live: **state plainly that the first real use is the owner's.**

## Acceptance criteria

- **A1** — Socket and rights proven before any live step, on throwaway objects only.
- **A2** — G2's comparison shown, or a STOP with the difference verbatim.
- **A3** — G3's five steps in the log: the damage landed, the restore matched by hash, the old image answered on the restored file, the truncated copy was refused.
- **A4** — G4's order held, the state named at each step; one stop, one migration, one start; the backup's path and hash reported, its restore proof shown.
- **A5** — After the migration only `candidate` changed, by the accepted set plus any quoting or clause order the rehearsal showed; counts and row hash equal.
- **A6** — Health and routes 200; old and new container and image ids quoted; census compared.
- **A7** — No name, id or field value of the owner's in any log or report; no key or `.env` read; no provider; no browser; scratch removed by exact path, the removal shown.
- **A8** — `PB-3` vacuity: a failure would look like an object difference, damage that did not land, a hash mismatch, a truncated copy accepted, a count that moved, a restart loop, a traceback. Say which you checked.
- **A9** — `HEAD` equals `origin/automation` after your push, both hashes quoted.
- **A10** — The report's last line is `Verification: PASS`, or the honest state: `Verification: STOPPED in S<n> — <reason>`, or `FAIL`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-280*` only in git; `output/SG-280-scratch/`; `data/db/SG-280-backup-<UTC>.db`; the live `candidate` table through the one migration, and the live file through S2's restore if it fires.
- **No product, config, schema, migration, dependency or test byte.** No other service touched. No data repair. Stored photos and files are untouched: no real storage mount in scratch containers.
- **The authorised runtimes:** the docker commands named here and the rehearsal script.

## Hang bounds

`docker version` **120 s**; build **900 s**; each one-shot **300 s**; stop and start **300 s**; health and routes **120 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling; the unit is seconds, read from the lane. Expected ≈800 s (`UNVERIFIED — my estimate`, from SG-276's rider and SG-279's 818 s). Downtime is expected in tens of seconds; quote the measured stop-to-healthy time. Runtime against budget goes in the report (`PG-PR-06`).

## Report

Destination: `docs/worklogs/SG-280_report.md`, evidence beside it (`docs/worklogs/SG-280_*`). The first line states the slice ID, model and effort, working directory, remote, BASE ref and resolved commit, and WORK_HEAD. It compares engine elapsed with ≈800 s, names every phase over 60 s, the state reached, and each constraint. The report feeds the release record; **do not create a tag**.

**Publish, literally, in this order, after your report commit:**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-280 | Report: docs/worklogs/SG-280_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them in your final message. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure:** the Architect must be able to read the state you left.
