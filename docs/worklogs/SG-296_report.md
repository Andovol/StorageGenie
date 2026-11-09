SG-296 (run 2) · model `opencode-go/claude-haiku-5-5` (from the run setting; effort and process arguments not inspected) · working directory `/home/andrei/StorageGenie` · remote `origin` = `git@github.com:Andovol/StorageGenie.git` · BASE ref `origin/automation` resolved `d205f9a6ec7f9efe8a40cbebe7fdf7238a735536` · WORK_HEAD `d205f9a6ec7f9efe8a40cbebe7fdf7238a735536`

## State reached: S1 — new container healthy, no rollback needed

SG-271 is served live. The new image `storagegenie-backend:latest` (`sha256:dcc67781b938…`) runs as container `0c4462ee5482…`, restart count 0, healthy about 12 s after the recreate. Evidence is in `docs/worklogs/SG-296_evidence.txt`.

Contract: recorded `0.58.0` (`AGENTS.md`). The contract folder was not opened; this lane denies it and no attempt was made.

## G0 — socket and pre-state

- Socket: `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-296/docker.sock`, `docker version` rc 0 with a Server section (Engine 29.9.2).
- Health before: `{"status":"ok","db":"ok","storage":"ok"}`.
- Container `e2a10bded379…` (`storagegenie-backend-1`), image `sha256:6b86f5e09a11…`, restart count 0, health `healthy`, status `running`, Cmd `uvicorn app.server:app --host 0.0.0.0 --port 8000`. Matches the packet's hypothesis.
- Mounts: `./data/db` → `/data/db` (bind, rw); `storagegenie_storage_data` → `/data/storage` (volume, rw).
- `storagegenie-backend:release-sg295` resolves to `sha256:6b86f5e09a11…` (the running image). `docker compose -f docker-compose.yml -f output/SG-296-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg295` for `backend`. The override file sets only `services.backend.image`.
- Other backend tags, untouched: `latest` (6b86), `recovery-sg270` (`2acd0c2438f3`), `prover`, `sg247-verify`, `sg240-proof`. `release-sg296` did not exist (`No such image`).
- Schema head: `20261102_sg279_candidate_state`.
- SG-271 range `29df408..9f9963c`: 0 files changed under `backend/alembic/versions/`, so no migration.
- Census before (read-only; byte copy of the database with its WAL and shm; counts only): 29 tables, 418 rows. `assertion 40, asset 7, asset_evidence 20, asset_fts 7, asset_fts_config 1, asset_fts_data 9, asset_fts_docsize 7, asset_fts_idx 7, asset_location 1, asset_relation 1, audit_event 104, candidate 10, enrich_snapshot 4, evidence 27, guardrail_event 2, household 1, idempotency_key 11, job 11, job_step 72, location 1, observation 20, planning_suggestion 0, provider_call 39, reminder 4, review_task 9, saved_search 0, source_attribution 0, user 2, alembic_version 1`.

## G1 — one build, one recreate

- Build: `docker compose build backend` rc 0, 2 s, 13 cache hits, 10 steps. The new image is `sha256:dcc67781b938…`. Because the build was mostly cached, the tree was compared directly (below), not assumed.
- Side effect: the compose build moved the `latest` tag from `6b86…` to `dcc6…`. That is compose's default tag, not a manual move. `release-sg295` and `recovery-sg270` were not touched.
- Runtime diff, `/app/app` of the `release-sg295` image vs the new image (excluding `__pycache__`): exactly the five expected files, `api/v1/candidates.py`, `api/v1/jobs.py`, `plugins/expiry_tracker.py`, `services/candidates.py`, `services/expiry_engine.py`. No other file.
- `eval/` is in the image (the Dockerfile copies `backend/` whole). The one differing file is `eval/baseline_sg029_frozen.md`, as expected.
- New image `app/` and `eval/` equal the worktree `backend/app` and `backend/eval` (excluding `__pycache__`): rc 0.
- Served tree before the recreate equal the old image's tree: rc 0, so no runtime drift.
- Static (JS and CSS hashes and sizes, before → after):
  - `index.html`: `571ad339…` (944 bytes) → `4b803f41…` (944 bytes).
  - JS: `index-FB7x-XIy.js`, 333530 bytes, `8743733b…` → `index-aRzURpTy.js`, 336969 bytes, `80e565d2…`. **The JS changed.**
  - CSS: `index-C07VbG0m.css`, 4535 bytes, `c3b58cda…`, unchanged.
- Alembic head unchanged before and after (`20261102_sg279_candidate_state`). No migration command run.
- Recreate: `docker compose -f docker-compose.yml up -d --no-deps --force-recreate backend` rc 0.
  - Container `e2a10bded379…` → `0c4462ee5482…`.
  - Image `sha256:6b86…` → `sha256:dcc6…`.
  - Cmd unchanged. Restart count 0. Health `healthy` at the 6th poll (about 12 s from the recreate command, polls every 2 s). Under the 120 s bound, so no rollback.
- Startup log: `Application startup complete`, the daily pass line, and `GET /v1/health 200`. No traceback.
- Tag: `storagegenie-backend:release-sg296` created on `sha256:dcc67781b938…`. The image was built from the worktree at `d205f9a` on branch `automation`. No other tag was removed or moved by me.
- Note: the pre-tag inspect printed a blank line instead of the `No such image` error seen in G0. The tag was then created and resolves to `dcc6…`.

## G2 — the new behaviour is in the served artifact

Read from a copy of the served container's own `/app`, not from the worktree:

- `app/plugins/expiry_tracker.py:42`: `def requires_date_task(unknowns: object) -> bool:`
- `app/services/candidates.py:1015`: `def committed_asset_id(db: Session, candidate: Candidate) -> str | None:`
- `app/services/expiry_engine.py`: `dateless_count` at lines 252, 282 and 332.
- Served bundle `index-aRzURpTy.js`: `In your catalog` ×1, `Kind of item` ×3, `the AI is turned off` ×1, `Date proposed` ×1, `set to need no date` ×1.

**Honest limit:** no accept, classify, clear or confirm was exercised live, because each writes the owner's data. The first real use is the owner's.

## G3 — the app answers, and nothing moved

- `/v1/health` six times: `{"status":"ok","db":"ok","storage":"ok"}` each time.
- Shell routes: `/` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/plugins/expiry-tracker/status` for one household (id read inside the script, not printed): HTTP 200. The summary keys are `by_bucket, by_tier, dateless, total, unresolved`. `summary.dateless` is present with value **0**.
- Startup log: 0 traceback or configuration lines, 0 ERROR or WARNING lines. The daily pass line: `app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-09 households_visited=1 reminders_created=0 errors=0`.
- Census after (byte copy of the live database with its WAL and shm; read-only open): 29 tables, 418 rows. No table moved. `reminder` stayed at 4, as the daily-pass line accounts for. Alembic head unchanged.

## Acceptance criteria

- **A1** — Socket-first proven (`docker version` Server section, rc 0). Pre-state quoted. Rollback override names `release-sg295`. No rights probe on any object.
- **A2** — One build (rc 0), one recreate (rc 0). No migration (head unchanged). Container `e2a10bded379…` → `0c4462ee5482…`; image `6b86f5e09a11…` → `dcc67781b938…`.
- **A3** — Runtime diff is the expected set; `eval/baseline_sg029_frozen.md` stated. JS changed; hashes and sizes quoted. Served tree equals the worktree (rc 0).
- **A4** — G2 strings quoted from the served artifact; honest-limit sentence present.
- **A5** — Health ×6 and routes 200; `dateless` present in the status summary (value 0); census compared, no table moved; startup log clean.
- **A6** — `release-sg296` tag created on `sha256:dcc67781b938…`; its branch is `automation` at `d205f9a`. No tag removed or moved by me; the compose build moved `latest` (see G1). State reached: **S1, no rollback**.
- **A7** — No owner name, id or field value in any log or report. The household id was read in-process and not printed. No key or `.env` value read or printed. No provider call. No browser. No database write (byte copies and read-only opens only). Scratch removed by exact path (`output/SG-296-scratch`); `ls` shows the path gone and `output/` holds only `dispatch`.
- **A8** — Vacuity checks, each of which would have shown a failure: the runtime file set (an extra file would appear in the diff); the JS hash (unchanged would show as identical); the string counts (0 would show as missing); route codes (non-200 would show); restart count (non-zero would show); traceback count (non-zero would show); census (a moved count would show). All passed.
- **A9** — `HEAD` and `origin/automation` after the push: see the publish output below.
- **A10** — Last line below.

## Runtime against budget

Engine elapsed about 2.5 minutes (scratch created 20:44, cleanup 20:46), against the ≈450 s estimate. No phase over 60 s. Recreate-to-healthy measured at about 12 s.

## Process notes

- One bash call was refused by the permission layer, with no reason given. I did not retry the process probe; I re-ran only the cleanup step.
- The model and effort line is from the run setting; the process arguments were not inspected.

## Owner action

None for the deploy. The first real use of the Expiry and classification flows is the owner's, per the honest limit above.

Verification: PASS

---

## Run 1 (stopped in S0)

### SG-296 report — deploy rider for SG-271

Slice SG-296 · model `opencode-go/claude-haiku-5-5` (from the run's model setting; process arguments not inspected) · effort not stated in this run · working directory `/home/andrei/StorageGenie` · remote `origin` = `git@github.com:Andovol/StorageGenie.git` · BASE ref `origin/automation` resolved `611575bbd4e9dcda41f503be7bf4ed211719696b` · WORK_HEAD `611575bbd4e9dcda41f503be7bf4ed211719696b`

#### State reached: S0 — stopped before the recreate

Nothing on the app changed. No build, no recreate, no tag, no migration, no database write, no provider call. The app is still `e2a10bde…` on `6b86f5e0…` (`release-sg295`).

#### Why it stopped

The contract chain requires the echo from `/home/andrei/storagegenie-contract/CODER.md` line 3. Reading that file was refused by a permission rule (bash deny on `*/home/andrei/storagegenie-contract*` and `*../storagegenie-contract*`). Under `PB-2` / `PG-PR-03` a denial is a STOP. I did not read the file by another route.

- Verified: recorded rule-set version `0.58.0` (`AGENTS.md` header; `STATE.md` resume block).
- Not verified: the published `contract-v0.58.0`, the host echo from SG-271, and the `CODER.md` echo.

The owner or desk needs to decide whether that path may be read. After that, SG-296 can be re-dispatched from G0.

#### G0 — pre-state (read-only)

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

#### Constraints

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

#### Runtime against budget

Stopped at S0 early. The recreate-to-healthy time is not measured, because no recreate ran.

#### Owner / desk action

1. Decide whether `/home/andrei/storagegenie-contract/CODER.md` may be read for the echo, or record the echo another way.
2. Then re-dispatch SG-296 from G0.

`STATE.md` was not changed (outside this slice's scope).

Verification: STOPPED in S0 — contract chain unverified: the permission rule denies reading `/home/andrei/storagegenie-contract/CODER.md`, so the echo cannot be carried; the app was not touched.
