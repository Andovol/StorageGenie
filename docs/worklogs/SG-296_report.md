# SG-296 report — deploy rider for SG-271

Slice SG-296 · model `opencode-go/claude-haiku-5-5` (from the run's model setting; process arguments not inspected) · effort not stated in this run · working directory `/home/andrei/StorageGenie` · remote `origin` = `git@github.com:Andovol/StorageGenie.git` · BASE ref `origin/automation` resolved `611575bbd4e9dcda41f503be7bf4ed211719696b` · WORK_HEAD `611575bbd4e9dcda41f503be7bf4ed211719696b`

## State reached: S0 — stopped before the recreate

Nothing on the app changed. No build, no recreate, no tag, no migration, no database write, no provider call. The app is still `e2a10bde…` on `6b86f5e0…` (`release-sg295`).

## Why it stopped

The contract chain requires the echo from `/home/andrei/storagegenie-contract/CODER.md` line 3. Reading that file was refused by a permission rule (bash deny on `*/home/andrei/storagegenie-contract*` and `*../storagegenie-contract*`). Under `PB-2` / `PG-PR-03` a denial is a STOP. I did not read the file by another route.

- Verified: recorded rule-set version `0.58.0` (`AGENTS.md` header; `STATE.md` resume block).
- Not verified: the published `contract-v0.58.0`, the host echo from SG-271, and the `CODER.md` echo.

The owner or desk needs to decide whether that path may be read. After that, SG-296 can be re-dispatched from G0.

## G0 — pre-state (read-only)

- Socket: `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-296/docker.sock`; `docker version` rc 0 with a Server section (Engine 29.9.2).
- Health before: `{"status":"ok","db":"ok","storage":"ok"}`.
- Container: `e2a10bded379` (`storagegenie-backend-1`), image `sha256:6b86f5e09a11…`, restart count 0, health `healthy`, up 47 hours. Matches the packet's hypothesis.
- `storagegenie-backend:release-sg295` resolves to `6b86f5e09a11`, the running image. `docker compose -f docker-compose.yml -f <override> config --images` names `storagegenie-backend:release-sg295` for `backend`.
- Other backend tags, untouched: `latest` (6b86f5e09a11), `recovery-sg270` (2acd0c2438f3), `prover` (5a7f53b464a8), `sg247-verify` (0cb60586c19d), `sg240-proof` (ae1d292d7d3e).
- Schema head: `20261102_sg279_candidate_state`, matching the pre-state.
- SG-271 range `29df408..9f9963c`: an ancestor of `origin/automation`. No file under `backend/alembic/versions/` changed (0 files), so no migration. The range includes `backend/eval/baseline_sg029_frozen.md`. Whether the image carries `eval/` is unverified because no build ran.
- Census (read-only, on a byte copy of the database, its empty WAL and its shm; counts only):

```
29 tables, 418 rows total
assertion 40, asset 7, asset_evidence 20, asset_fts 7, asset_fts_config 1,
asset_fts_data 9, asset_fts_docsize 7, asset_fts_idx 7, asset_location 1,
asset_relation 1, audit_event 104, candidate 10, enrich_snapshot 4, evidence 27,
guardrail_event 2, household 1, idempotency_key 11, job 11, job_step 72,
location 1, observation 20, planning_suggestion 0, provider_call 39, reminder 4,
review_task 9, saved_search 0, source_attribution 0, user 2, alembic_version 1
```

## Constraints

- A1 — socket-first proven; pre-state quoted; rollback override written and names `release-sg295`; no rights probe on any object.
- A2 — not reached: no build, no recreate, no migration.
- A3 — not reached: no runtime diff was taken, and the served tree was not compared.
- A4 — not reached: no served-artifact strings were checked.
- A5 — health before only; health after and routes not reached.
- A6 — no tag created, moved or removed. `release-sg296` was not created. State: S0.
- A7 — no owner name, id or field value printed; no key or `.env` read or printed; no provider; no browser; no database write. Scratch removed by exact path (`output/SG-296-scratch`); `ls` afterwards shows it is gone and `output/` is otherwise untouched.
- A8 — vacuity check: not applicable, because no runtime diff or hash was taken. The SG-271 changed-file list was checked against the migration rule instead.
- A9 — `HEAD` equals `origin/automation` after publish; the two hashes are shown in the publish output.
- A10 — see the last line.

## Runtime against budget

Stopped at S0 early. The recreate-to-healthy time is not measured, because no recreate ran.

## Owner / desk action

1. Decide whether `/home/andrei/storagegenie-contract/CODER.md` may be read for the echo, or record the echo another way.
2. Then re-dispatch SG-296 from G0.

`STATE.md` was not changed (outside this slice's scope).

Verification: STOPPED in S0 — contract chain unverified: the permission rule denies reading `/home/andrei/storagegenie-contract/CODER.md`, so the echo cannot be carried; the app was not touched.
