SG-295 | model opencode-go/claude-haiku-5-5 | effort: not stated in this agent's context | wdir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> f9bfb30d2ae19b49ed682b35a253fb835e1586cd | WORK_HEAD f9bfb30d2ae19b49ed682b35a253fb835e1586cd

Contract chain: recorded `0.58.0` (`AGENTS.md`). The contract folder was not read (this lane denies it). Host evidence: `docker version` Server section present (Engine 29.9.2, containerd v2.4.2, runc 1.5.2, rootless). Socket `unix:///run/dispatch-storagegenie-SG-295/docker.sock`; scratch in `output/SG-295-scratch/`, removed by exact path.

# SG-295 report — deploy rider: candidate-state migration on the live database: PASS

Outcome: the one approved migration `20261023_sg233_reminder -> 20261102_sg279_candidate_state` ran on the live database after the rehearsal on copies passed. Only `candidate` changed. Counts, candidate rows and integrity are unchanged. One stop, one migration, one start. The new image serves health and four shell routes with 200. State reached: S3 (new image serving). No restore and no retry. No split or merge was exercised live: the first real use is the owner's.

## G0 — pre-state and recovery image (A1)
- `docker version`: Server section present (see line above).
- Health at start: `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state matches SG-294: container `d972bc752fa038be2552322120af1e0d56a35321cc47d61fc4677b476a91332f`, `.Image` `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22`, started `2026-11-02T15:52:53.194514305Z`, running, restart count 0, healthy, mounts `/data/db` (bind) and `/data/storage` (volume) only.
- Recovery tag `storagegenie-backend:recovery-sg270` resolves to `sha256:2acd0c2438f34b5070b13bd04fa898b42cde126241dab43b0d124aa3a7a99ea2` before the build and after it (G1).
- Override written: `output/SG-295-scratch/recovery.override.yml` (one key, `services.backend.image`). `docker compose -f docker-compose.yml -f output/SG-295-scratch/recovery.override.yml config --images` names `storagegenie-backend:recovery-sg270` for `backend`. `docker compose config` without `--images` was never run.
- `git check-ignore -v data/db/SG-295-backup-probe.db` -> `.gitignore:19:data/db/*.db`.
- No rights probe on any real object. Only `output/` subpath `SG-295-scratch` was created and removed.

## G1 — build, no recreate (A1)
- `docker compose build backend`: rc 0. `storagegenie-backend:latest` -> `sha256:6b86f5e09a116a2e3bcbf324408200bdeb14c5f15b738e155171dff02e8e657f`. The running container was untouched. Recovery tag re-checked after the build: same id.
- Served-tree diff, recovery image against new image (create + export of both, extract `app/app`, `app/alembic`, `app/static`, `app/tests`):
  - `app/alembic/versions/20261102_sg279_candidate_state.py`: added (expected).
  - `app/app/services/candidates.py`: differs (expected).
  - `app/static/assets/index-C07VbG0m.css` and `index-FB7x-XIy.js`: byte-identical (prefixes `c3b58cda…`, `8743733b…` on both sides).
  - Disclosed, not product bytes: `__pycache__` directories exist only in the recovery image (bytecode written by the running container); the new image has none. The new image also carries `app/tests/test_sg279_candidate_state.py` and `app/tests/test_sg279_rehearsal.py`, outside the served tree (same disclosure as SG-280).

## G2 — live inventory, read-only (A2)
Full output: `docs/worklogs/SG-295_inventory.log`.
- Live opened read-only (one-shot container, `data/db` mounted `:ro`): `journal_mode=wal`; `-wal` 0 bytes; `-shm` 32768 bytes; revision `20261023_sg233_reminder`.
- `sqlite_master`: 95 rows live, 95 rows in a reference built with the new image to `20261023_sg233_reminder`. Object differences: 0. Live `candidate` text equals `SG279_CANDIDATE_SQL_BEFORE` (whitespace-normalised). PASS.
- Table counts recorded: 29 tables, 418 rows in total, `candidate` 10, `reminder` 4, `asset` 7.

## G3 — rehearsal on copies (A3)
Script `docs/worklogs/SG-295_rehearse.py` (no data). Output `docs/worklogs/SG-295_rehearsal.log`. Copies came from SQLite's backup API (`sha256 3aa4e1f5…`), one-shot container, `data/db` mounted read-only, app running.
1. Upgrade on the copy: PASS. Verify ok (integrity ok, fk 0, rev new). Counts equal. Candidate rows 10, row hash equal. Changed objects: `[('table','candidate')]` only. States after: the seven-state set. FK set and columns equal. In a transaction rolled back afterwards: `split` accepted, `merged` accepted, invalid state refused naming `ck_candidate_state`; the row hash after rollback equals the pre-transaction hash.
2. Interrupted migration: the one-shot wrapper exited with `os._exit(99)` right after the `DROP TABLE candidate` statement. Damage observed: rc 99; `_alembic_tmp_candidate` present beside `candidate` (the table still listed present at kill time); revision still `20261023_sg233_reminder`. This is the S2 state the live rules key on (tmp present, revision old, exit code non-zero). Damage landed; the rehearsal is not vacuous. The reason `candidate` still appeared at kill time was not investigated.
3. Restore by the S2 procedure (backup copy over the damaged file, `-wal`/`-shm` removed): PASS. SHA-256 equal to backup; integrity ok; fk 0; revision old; all 29 counts equal.
4. Recovery image `storagegenie-backend:recovery-sg270` (`2acd0c24…`) on the restored file. `--network none`, no published port, scratch `STORAGE_ROOT`, no `env_file`, no real storage mount, image's own user (no `--user`). From inside: `GET /v1/health` -> 200; `GET /v1/households` -> 200. Startup log traceback count 0. Container stopped and removed by name; removal confirmed. PASS.
5. Refusal check (PG-EV-01): truncated copy (382976 bytes, half the file). The same verify function refused it (unreadable: `DatabaseError`); its hash differs from the backup. PASS (refused).

## G4 — live migration in order (A4)
- Precondition: the only container mounting `data/db` is `storagegenie-backend-1`. Frontend is exited and mounts only its own folders.
- S1 — `docker compose stop backend`: rc 0. Status `exited false 0`, finished `2026-11-07T21:46:53.717766574Z`. Same status and restart count 0 after 15 s: no restart. GATE_S1_OK.
- Backup: SQLite backup API from the stopped live file (source `mode=ro`) to `data/db/SG-295-backup-20261107T214652Z.db`, 765952 bytes, `sha256 3aa4e1f5237f6e0a3ec15ce75a999c259e371917e5522a9debda2cb4b32eb4d2`. Retained; not removed.
- Restore proof: the backup copied to scratch and checked with `output/SG-295-scratch/g4_check.py`: integrity ok, fk 0, revision `20261023_sg233_reminder`, 29 tables, counts equal to the stopped live file (418 rows), candidate row hash `81af8de283e9fa34` equal, `sqlite_master` equal. PASS.
  - First attempt: running the same check on the backup file inside a read-only mount failed (`unable to open database file`: a WAL-mode file with no `-shm` in a read-only directory). Nothing was written. The check was repeated on the scratch copy (same bytes). The stopped live file had passed read-only before that (integrity ok).
- S2 — live file SHA-256 before migration: `424ac9d831daaae8c9d3e2a3684c7cad9724268f8688cff55c2e8e1f7673bc85`. `docker compose run --rm --no-deps backend alembic upgrade head`: rc 0; one step `20261023_sg233_reminder -> 20261102_sg279_candidate_state`; non-transactional DDL; about 2 s.
- Comparison after migration (copy of the migrated main file, taken after a clean exit with no `-wal`/`-shm`, SHA-256 `f08241130da7dc5aeca4111c2445a9d0c0c66b8109cb82bb3afe3c5c93e73567`):
  - revision `20261102_sg279_candidate_state`; integrity ok; fk 0;
  - changed objects: `[('table','candidate')]` only;
  - `candidate` text equals the SG-279 AFTER text, exact after whitespace normalisation;
  - all 29 table counts equal G2; candidate rows 10, row hash `81af8de283e9fa34` equal;
  - no `_alembic_tmp_candidate`. PASS.
  - First attempt: the migrated live file read through a read-only mount failed (`unable to open database file`; the clean exit had removed the sidecars). Checked as a copy instead (no sidecars present before the copy; same SHA-256).
- S3 — `docker compose up -d --no-deps --force-recreate backend`: rc 0 at 21:47:59 UTC. Healthy at 21:48:10 UTC (6 polls). New container `e2a10bded379d4c0b1698d4c3b085abac18e787b19c24a84547b8b4f488864bb`, image `sha256:6b86f5e0…`, `Cmd` `["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, restart count 0, health healthy. Old container `d972bc752fa0…` removed by the recreate.
- Release tag: `storagegenie-backend:release-sg295` was absent and was created on `sha256:6b86f5e0…` (the new image). Branch: the image was built from the working tree at `origin/automation` = `f9bfb30d2ae19b49ed682b35a253fb835e1586cd`. `storagegenie-backend:latest` also resolves to the same id. No tag was removed or moved. The previous `latest` (`e3e74a61…`, SG-294 donor) is no longer tagged `latest`; it was not removed.
- Old live image `sha256:96a662414c23…` is not addressable: `docker image inspect` reports no such image, and it is absent from `docker image ls -a`. SG-280's report already recorded "No such image" for this id before this slice. This slice ran no `rmi` or prune; the cause is not established. A rollback to that image by id is therefore not available. `storagegenie-backend:recovery-sg270` is present.
- Stop-to-healthy: 77.9 s (stop command at 21:46:52.0 UTC, healthy at 21:48:10.0 UTC). Breakdown: stop 2 s; confirmation wait 15 s; backup and verification; migration about 2 s; start-to-healthy about 11 s. Container not running for about 76 s.

## G5 — the app answers (A6)
- `/v1/health` six times (21:48:24 to 21:48:34 UTC): each `{"status":"ok","db":"ok","storage":"ok"}`.
- Routes `/`, `/expiry`, `/inbox`, `/planning`: 200 each.
- Startup log of the new container (6 lines): `Started server process`, `Uvicorn running on http://0.0.0.0:8000`, `app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-07 households_visited=1 reminders_created=0 errors=0`. No traceback, no configuration error.
- Census on the running app (read-only mount, copy-free): integrity ok, fk 0, revision new, every table count equal to G2 (none moved), `reminder` 4 (unchanged, as the daily line's `reminders_created=0` accounts for), candidate row hash equal.
- Old container `d972bc752fa0…`, image `sha256:96a662414c23…` (not addressable now, see G4); new container `e2a10bde…`, image `sha256:6b86f5e0…`.

## Acceptance criteria
- A1 — G0 pre-state quoted; recovery tag resolves to `2acd0c24…` before and after the build; override names it; no rights probe on a real object. Yes.
- A2 — G2 comparison shown in `SG-295_inventory.log`: 0 object differences; candidate text equal to the SG-279 BEFORE text. Yes.
- A3 — G3 five steps in the log. Damage named (tmp present beside candidate, revision old, rc 99). Restore matched by hash. Recovery image served health and a read route (200, 200) on the restored file. Truncated copy refused. Yes.
- A4 — Order held: S1 at stop (no restart over 15 s), backup named with path and hash and restore proof, S2 with live hash before the single migration, S3 after the start. One stop, one migration, one start. Release tag branch stated (`origin/automation` at `f9bfb30d…`). Yes.
- A5 — Only `candidate` changed, by the accepted set (two new states) and the SG-279 text (quoting and FK clause order as the rehearsal showed); counts and row hash equal. Yes.
- A6 — Health 200 six times; routes 200; old and new container and image ids quoted; census equal to G2. Yes.
- A7 — No name, id or field value of the owner's appears in logs or this report (counts, hashes and schema text only). No key read or printed; `.env` not opened by this agent (Compose reads it for interpolation as usual; nothing printed). No provider call, no browser, no spend. Scratch removed by exact path: `SCRATCH_REMOVED output/SG-295-scratch`; `output/` holds only `dispatch`, untouched. Yes.
- A8 — Vacuity checked: object difference (G2 and post-migration compare, 0 unexpected objects); damage that did not land (landed, see G3 step 2); hash mismatch (restore equal, truncated unequal); truncated copy accepted (refused); count moved (none); restart loop (restart count 0, no restart in 15 s); traceback (0 in both startup logs). Two verification attempts failed on read-only WAL reads and were repeated on copies; both failures are recorded above.
- A9 — `HEAD` and `origin/automation` after push: quoted in the final message.
- A10 — Last line of this report.

## Runtime and budget (PG-PR-06)
- Slice start 21:42:15 UTC. Engine clock at G5 end: 382 s, under the expected ≈800 s. Against `RUN_BUDGET_S` 2100 s: about 18%. The 1200 s start guard for G4 was not reached (G4 began at about 277 s).
- Phases over 60 s: stop-to-healthy window (78 s). No single command reached its hang bound. Build ran from cache (about 20 s). Rehearsal about 6 s.

## Open items for the owner
1. Old live image `96a66241…` is not addressable (see G4). `storagegenie-backend:recovery-sg270` is the rollback image present in the daemon; it is the pre-SG-279 code. Whether to roll back, and to what, is the owner's decision (S3 rule: no restore by this slice).
2. First real split/merge use is the owner's.
3. Backup retained at `data/db/SG-295-backup-20261107T214652Z.db` (gitignored, sensitive).

## Files
- `docs/worklogs/SG-295_report.md` (this file)
- `docs/worklogs/SG-295_inventory.log` (G2: schema text, counts, revisions; no owner values)
- `docs/worklogs/SG-295_rehearse.py` (G3 script; no data)
- `docs/worklogs/SG-295_rehearsal.log` (G3 output; counts and hashes only)

Verification: PASS
