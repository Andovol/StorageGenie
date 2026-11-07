# SG-295 — Deploy rider: rehearse recovery on copies, then run the one candidate state migration on the live database

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It writes only `docs/worklogs/SG-295*`, the scratch path, one retained backup, and one image tag.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: the live app database, one approved migration.** `sqlite:////data/db/storagegenie.db`, on the host at `data/db/storagegenie.db`. A declared sensitive surface; this packet is the written plan the owner approved. **Any result other than the expected one, or any step outside this packet, stops the work and returns it to the owner.**
**Restart: one stop and one start of the backend container.**
**Provider: none.** No key is read or printed, no `.env` is opened by you, **no spend**. Scratch containers get no `env_file` and run `--network none`.

**Authority, verbatim:** owner, D16: *"D16 - ok."*; D20: *"D20 - ok."*; D23 and D26 (the recovery image): *"D23 and D24 ok. Lets run in L3 mode."*, *"D26 - approved"* (`docs/decisions/2026-10-30-session-approvals.md`). This reruns SG-280 (`docs/worklogs/SG-280_audit.md`) now that a recovery image exists (`docs/worklogs/SG-294_report.md`, `SG-294_audit.md`).

**Contract:** recorded `0.58.0` (`AGENTS.md`). This lane denies reading the contract folder; your echo line is the host evidence.

## Why this exists

The code writes candidate states `split` and `merged`, and the live table refuses them. SG-279 (rated 90) built the fix. **Alembic runs non-transactionally here** (`docs/worklogs/SG-279_rehearsal.log:2`), so an interrupted migration can leave a half-done table. The migration rebuilds from a hand-written copy of the table (`backend/alembic/versions/20261102_sg279_candidate_state.py:28-72`), so it applies only if the live table matches. SG-280 proved on a copy: the live schema matches, the upgrade works, the restore works, a truncated copy is refused; it stopped because the old image was gone. **SG-294 made and proved the recovery image:** `storagegenie-backend:recovery-sg270` = `sha256:2acd0c2438f34b5070b13bd04fa898b42cde126241dab43b0d124aa3a7a99ea2`, the same files and launch settings as the live container.

## Recovery states — these bind every goal, and they win over any other instruction here (`PG-IC-03`)

| State | When | On failure |
|---|---|---|
| **S0** | Before the backend is stopped | Stop. The app was never touched |
| **S1** | Backend stopped, migration command not started | **Start the recovery image** by the override below. Nothing changed |
| **S2** | Migration command started, new image not started; a leftover `_alembic_tmp_candidate` counts | Restore the G4 backup, verify it as in G3, start the recovery image |
| **S3** | New image started; writers may have run (`backend/app/server.py:27-34`) | **No restore, no retry, no restart.** Leave things as they are and report at once. A restore is the owner's decision |
| **S4** | A recovery step itself failed or was denied | Leave the app **stopped**, report outcome `UNKNOWN`, no further attempt |

**Starting the recovery image (S1, S2):** write `output/SG-295-scratch/recovery.override.yml` setting only `services.backend.image: storagegenie-backend:recovery-sg270`, then `docker compose -f docker-compose.yml -f output/SG-295-scratch/recovery.override.yml up -d --no-build --no-deps --force-recreate backend`. It keeps the compose file's mounts, ports, `env_file` and healthcheck. **Never run `docker compose config` without `--images`:** it prints the resolved `.env` values.

**A denial is a STOP (`PB-2`, `PG-PR-03`), never a reason to try another route.** A denial in S0 changes nothing. A denied live stop leaves the app running, which is S0. A denial in S1 or S2 during a recovery step is S4.

**Time guard:** do not start G4 if more than **1200 s** have elapsed since your start; report and stop, as S0. A partial slice with a receipt is a success.

## G0 — Socket, pre-state and the recovery image, changing nothing live

- `DOCKER_CONFIG` to a writable directory under `output/SG-295-scratch/`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-295/docker.sock`, and `docker version` shows a **Server** section. Scratch stays in `output/SG-295-scratch/`, removed by exact path at the end; never touch `output/` itself or `output/dispatch`.
- `curl -s http://127.0.0.1:8003/v1/health` quoted.
- **Pre-state, hypotheses from `docs/worklogs/SG-294_report.md`:** container `d972bc752fa038be…`, `.Image` `sha256:96a66241…`, started `2026-11-02T15:52:53.194514305Z`, restart count 0, mounts `/data/db` and `/data/storage` only; head `20261023_sg233_reminder`. `docker inspect` only with `--format` and named fields. A different container or a restart is a STOP.
- **The recovery image:** `storagegenie-backend:recovery-sg270` resolves to `sha256:2acd0c24…` (full id above); otherwise STOP. `docker compose -f docker-compose.yml -f output/SG-295-scratch/recovery.override.yml config --images` names it for `backend`; otherwise STOP.
- `git check-ignore` proves `data/db/SG-295-backup-probe.db` is ignored, by `data/db/*.db` (`PG-SC-10`); otherwise STOP.
- **`output/` is not in `.gitignore`, and your scratch will hold copies of the owner's data.** Stage only by the exact path `docs/worklogs/SG-295*`, never `git add -A` or `git add .`; remove the scratch before your report commit; show `git status --short` clean and `git show --stat HEAD` holding only those paths. Do not pass `--user` to scratch containers; files they write are removable, or go through a throwaway `busybox` container (`--network none`) by exact path.
- **No rights probe on any real object** (`PG-PR-01`): never tag, untag, stop or restart anything of the app's to test rights. `docker compose stop` on the live service cannot be proven in advance; that is accepted.

## G1 — Build the new image, no recreate

One `docker compose build backend`, rc 0; the running container is untouched. Record the new image id (it moves `:latest`; the recovery tag is unaffected — re-check it resolves to `2acd0c24…` after the build). Runtime diff between the **recovery image** and the new one, over the served Python tree, is expected to be **exactly** `alembic/versions/20261102_sg279_candidate_state.py` and `app/services/candidates.py`; JS and CSS byte-identical. Any other difference is a STOP.

## G2 — Live inventory, read-only

Open the live database read-only. Record: `journal_mode`; every row of `sqlite_master` (type, name, tbl_name, sql); every table's count; the Alembic revision; `-wal` and `-shm` presence.

Build a reference database in the scratch path by running the migrations to `20261023_sg233_reminder` with the **new image** and scratch `DATABASE_URL`. Compare whole `sqlite_master`, whitespace normalised. The live `candidate` text must equal the reference, expected to be `SG279_CANDIDATE_SQL_BEFORE` in `docs/worklogs/SG-279_rehearsal.log:47-60`. **Any difference in any object is a STOP in S0**, reported verbatim; object definitions hold no owner data.

## G3 — Rehearse on copies while the app keeps running

All copies live under `output/SG-295-scratch/`. **They hold the owner's real data: never print a name, id or field value; counts and hashes only.** Script and output: `docs/worklogs/SG-295_rehearse.py` (no data; start from `docs/worklogs/SG-280_rehearse.py`) and `docs/worklogs/SG-295_rehearsal.log`.

Take a copy of the live database with **SQLite's backup API** in a one-shot container with `data/db` mounted read-only (SG-280 and SG-294 proved this). Each rehearsal starts from a fresh file copy of it.

1. **Upgrade on real data:** the new image upgrades a copy to head. Compare with the copy before: every candidate column by row hash, every other object's definition, every table count; `integrity_check`, `foreign_key_check`. Then in a transaction that is rolled back, store `split`, `merged` and an invalid state on one candidate: the first two accepted, the third refused naming `ck_candidate_state`.
2. **Interrupted migration:** run the real migration with a one-shot wrapper that kills the process with `os._exit` at the drop/rename point, as SG-280 did. **Report exactly which damaged state landed:** `candidate` missing, or `_alembic_tmp_candidate` present beside `candidate`, with the revision still old and the exit code non-zero. Either is the S2 state the live rules key on. **If neither landed, the rehearsal proves nothing: STOP.**
3. **Restore by the exact S2 procedure:** replace the damaged file with the backup copy, removing any `-wal` and `-shm` beside it. Prove: hash equal to the backup, `integrity_check`, `foreign_key_check`, head, all table counts.
4. **The recovery image runs on it:** start `storagegenie-backend:recovery-sg270` on that restored file, `--network none`, no published port, scratch `STORAGE_ROOT`, no `env_file`, no real storage mount, the image's own user. **From inside it** `GET /v1/health` returns 200 and `GET /v1/households` returns 200 (status codes only). It must actually serve: a create-only check does not satisfy this step. Stop and remove it by name.
5. **The check can fail (`PG-EV-01`):** give step 3's verification a deliberately truncated copy and show it refuses.

Any step not as expected: **STOP in S0**, app untouched.

## G4 — The live migration, in this order

Before starting, confirm no dispatch-unrelated container uses the file. Then:

1. `docker compose stop backend`; confirm not running, and no restart over 15 s. **State S1.**
2. Backup with SQLite's backup API to `data/db/SG-295-backup-<UTC>.db`, retained, not removed by you. Restore it to a scratch path and prove `integrity_check`, `foreign_key_check`, head and all table counts equal to the stopped live file.
3. `sha256` of the live file. **Now state S2.** One `docker compose run --rm --no-deps backend alembic upgrade head`.
4. Compare: revision `20261102_sg279_candidate_state`; the live `sqlite_master` differs from G2 only in `candidate`, by the same text diff as G3 step 1; all table counts equal; candidate row hash equal; `integrity_check`, `foreign_key_check`; no `_alembic_tmp_candidate`.
5. `docker compose up -d --no-deps --force-recreate backend`. **Now state S3.** New container id, image id, `Cmd`, restart count, health status.
6. **Tag what now serves:** `storagegenie-backend:release-sg295` on the new image id. Absent → create; resolves to the same id → nothing; resolves elsewhere → do not touch it, report it. Never remove or move any tag.

## G5 — The app answers

`/v1/health` six times, each quoted; shell routes `/`, `/expiry`, `/inbox`, `/planning` return 200. Startup log: no traceback or configuration error, and the daily pass's own line quoted. Census after: every table count compared with G2; **`reminder` may rise only as that line accounts for**; any other table moving is reported at once under S3. No split or merge is exercised live: **state plainly that the first real use is the owner's.**

## Scope ceiling

- **Written:** `docs/worklogs/SG-295*` only in git; `output/SG-295-scratch/`; `data/db/SG-295-backup-<UTC>.db`; the live `candidate` table through the one migration, and the live file through S2's restore if it fires; the one `release-sg295` tag.
- **No product, config, schema, migration, dependency or test byte.** No other service touched. No data repair. Stored photos and files untouched: no real storage mount in scratch containers.
- **The authorised runtimes:** the docker and compose commands named here and the rehearsal script. Never `docker rmi`, `image prune`, `system prune`, or `docker compose config` without `--images`.

## Hang bounds

`docker version` **120 s**; build **900 s**; each one-shot **300 s**; stop and start **300 s**; health and routes **120 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. Expected ≈800 s (`UNVERIFIED — my estimate`, SG-280 reached G3 step 4 at ≈461 s). Downtime is expected in tens of seconds; quote the measured stop-to-healthy time. Runtime against budget in the report (`PG-PR-06`).

## Acceptance criteria

- **A1** — G0's pre-state quoted; the recovery tag resolves to `2acd0c24…` before and after the build; the override names it; no rights probe on a real object.
- **A2** — G2's comparison shown, or a STOP with the difference verbatim.
- **A3** — G3's five steps in the log: the damaged state named, the restore matched by hash, the recovery image served health and a read route on the restored file, the truncated copy refused.
- **A4** — G4's order held, the state named at each step; one stop, one migration, one start; the backup's path and hash reported, its restore proof shown; the release tag's branch stated.
- **A5** — After the migration only `candidate` changed, by the accepted set plus any quoting or clause order the rehearsal showed; counts and row hash equal.
- **A6** — Health and routes 200; old and new container and image ids quoted; census compared.
- **A7** — No name, id or field value of the owner's in any log or report; no key or `.env` read or printed; no provider; no browser; scratch removed by exact path, the removal shown.
- **A8** — `PB-3` vacuity: a failure would look like an object difference, damage that did not land, a hash mismatch, a truncated copy accepted, a count that moved, a restart loop, a traceback. Say which you checked.
- **A9** — `HEAD` equals `origin/automation` after your push, both hashes quoted.
- **A10** — The last line is `Verification: PASS`, or `Verification: STOPPED in S<n> — <reason>`, or `FAIL`.

## Report

Destination: `docs/worklogs/SG-295_report.md`, evidence beside it (`docs/worklogs/SG-295_*`). The first line states the slice ID, model and effort, working directory, remote, BASE ref and resolved commit, and WORK_HEAD. It compares engine elapsed with ≈800 s, names every phase over 60 s, the state reached, and each constraint. The report feeds the release record; **do not create a git tag**.

**Publish, literally, in this order, after your report commit:**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-295 | Report: docs/worklogs/SG-295_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them in your final message. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure:** the Architect must be able to read the state you left.
