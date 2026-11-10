Slice SG-299 · model opencode-go/claude-haiku-5-5 · effort high (process args: `--model opencode-go/claude-haiku-5-5 --variant high`) · cwd /home/andrei/StorageGenie · remote git@github.com:Andovol/StorageGenie.git · BASE ref origin/automation → resolved 6cb9de6b1dc7f1cb011f07838d0d2ac3b794e9cf · WORK_HEAD 6cb9de6b1dc7f1cb011f07838d0d2ac3b794e9cf (report commit is the next commit on origin/automation)

# SG-299 report — deploy rider: SG-272 + SG-297 + SG-298 served live

Contract: rule-set version recorded 0.58.0 (AGENTS.md, as received). Contract folder not read (lane denial, not attempted).

## Outcome

**S1, no rollback.** The new backend image `storagegenie-backend:release-sg299` (`sha256:62db28ab96e8`) is serving. The health probe passed in 15 s and held through six probes and all route checks. No migration ran, the database is unchanged, and no provider was called.

Served-artifact strings are present (G2). The first real use of put back, gone and quantity is the owner's (see "Honest limit").

## Phases (stamps from `date +%s`)

| Phase | Stamps | Seconds |
|---|---|---|
| G0 socket block, `docker version` (Server section present) | 1794342758 → 1794342758 | 0 |
| G0 pre-state (container, image, release-sg296 resolve, health) and read-only census | 1794342777 → 1794342777 | 0 |
| Rollback override written; `config --images` (rc 0); Dockerfile read | 1794342784 → 1794342785 | 1 |
| G1 pre-build snapshot of running image's `/app` tree | 1794342806 → 1794342808 | 2 |
| G1 one `docker compose build backend` (rc 0; layers cached) | 1794342808 → 1794342811 | 3 |
| G1 new-image snapshot, runtime diff, worktree compare | 1794342811 → 1794342813 | 2 |
| S1 `docker compose up -d --no-deps --force-recreate backend` (rc 0) | 1794342823 → 1794342824 | 1 |
| S1 health wait to healthy (recreate-to-healthy: 15 s from recreate start) | 1794342828 → 1794342838 | 10 |
| G2 served-artifact checks; G3 health x6, routes, API, log, census after | 1794342860 → 1794342867 | 7 |
| Evidence, scratch removal, git status | 1794342886 → 1794342886 | <1 |

Engine elapsed: 128 s (1794342758 → 1794342886). Expected ≈300 s (`UNVERIFIED — my estimate`); the actual run is under the estimate. Budget 2100 s; publish before 1200 s — met.

## State reached

**S1** — new container started and healthy within 120 s; no restart; no rollback needed or used.

## Ids and state, before and after

| Item | Before | After |
|---|---|---|
| backend container | `0c4462ee548260ab08a89f39a6df92c77fbca0177414a9158caa3c564dbba102` | `23975bec092cdce406731af09f9a96100d0c69dc239d42a485369dc94d409419` |
| running image | `sha256:dcc67781b9392fcc7914ce015abbda7454a6f498fe6ef9c2b3897b604eadc7d3` | `sha256:62db28ab96e8ff1450186be6526b86b08fccb20610ecbcfc4f62fcffeb7bdf76` |
| Cmd | `uvicorn app.server:app --host 0.0.0.0 --port 8000` | same |
| restart count / health | 0 / healthy | 0 / healthy |
| `storagegenie-backend:release-sg299` | absent | `62db28ab96e8` (created by this run) |
| `storagegenie-backend:latest` | `5867d89b579e` (run 1's build, moved by it) | `62db28ab96e8` (this run's build) |
| `storagegenie-backend:release-sg296` | `dcc67781b939` | unchanged |
| `storagegenie-backend:release-sg295` | `6b86f5e09a11` | unchanged |
| `storagegenie-backend:recovery-sg270` | `2acd0c2438f3` | unchanged |

Note on `latest`: run 1's build had moved `latest` to `5867d89b`. This run's build (cache-satisfied, the same content) moved it to `62db28ab`, which is now also `release-sg299`. No tag was removed or moved except `latest`, which the compose build moves by design. Run 1's open question about an unverified `latest` is closed: `latest` = `release-sg299` = the served image.

Compose recreate: the packet's literal command was used (no `--no-build`); compose recreated from the freshly built `latest`, and the container's image is `62db28ab`.

## Frontend (static, from the served image)

| File | Before | After |
|---|---|---|
| `index.html` | 944 B, `4b803f41…` | 944 B, `97437d95…` (changed) |
| JS | `index-aRzURpTy.js` 336969 B, `80e565d2…` | `index-CjbyAByJ.js` 347968 B, `665dcb11…` (changed) |
| CSS | `index-C07VbG0m.css` 4535 B, `c3b58cda…` | same, unchanged |

Full sha256 for each file in `docs/worklogs/SG-299_runtime_diff.txt`.

## Runtime diff (whole `/app` tree = `backend/` copy, excluding `/app/static` and `__pycache__`)

Derived with `git diff --name-only 58ce7fa..HEAD -- backend/ ':!backend/alembic'`: exactly the 10 files in the packet's G1 list. Image comparison (running `dcc67781` vs built `62db28ab`):

- **Changed (9):** `app/api/v1/assets.py`, `app/api/v1/reminders.py`, `app/api/v1/review_tasks.py`, `app/services/asset_service.py`, `app/services/expiry_engine.py`, `app/services/lifecycle.py`, `tests/fixtures/sg136_asset_dict_baseline.json`, `tests/test_plugin_expiry.py`, `tests/test_sg111_lifecycle.py`.
- **Added (1):** `tests/test_sg272_flow.py`.
- **Removed:** none.

Nothing outside the derived set. The full list with both hashes is in `docs/worklogs/SG-299_runtime_diff.txt`.

Served tree vs worktree: every tracked file under `backend/` matches the new image's hash exactly. The only differences are 37 untracked local cache entries in the worktree (`.mypy_cache`, `.pytest_cache`, `.ruff_cache`), which are not in the image.

## G2 — new behaviour is in the served artifact

Checked from the served container (`docker exec` on `23975bec…`):

- `app/api/v1/review_tasks.py` contains `def _visible_tasks`: 1
- `app/api/v1/assets.py` contains `def _gone_reason_from_assertions`: 1 and `/quantity/decrement`: 1
- `app/services/asset_service.py` contains `def put_back`: 1 and `def mark_gone`: 1
- Served JS (`index-CjbyAByJ.js`) contains `Put back`: 5, `Gone items`: 1, `Use it up`: 4, `Amount left`: 4, `Thrown away`: 1

**Honest limit:** no gone, put back, increment or decrement was exercised live, because each writes the owner's data. The first real use is the owner's.

## G3 — the app answers, and nothing moved

- `/v1/health` six times, each `200 {"status":"ok","db":"ok","storage":"ok"}`.
- Shell routes: `/` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/review-tasks?household_id=<id>&limit=5`: 200, `total` 9. The household id was read from the database inside the check and not printed.
- `GET /v1/assets?household_id=<id>&limit=5`: 200.
- Startup log: uvicorn startup complete, no traceback, no ERROR or configuration error (grep count 0). Daily pass line: `app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-10 households_visited=1 reminders_created=0 errors=0`.
- Census (read-only, counts only) after compared with G0: **identical**, every table (`docs/worklogs/SG-299_census_after.txt`; diff exit 0). `reminder` 4 before and after, consistent with `reminders_created=0`.

## Alembic

`git diff --name-only 58ce7fa..HEAD -- backend/alembic` is empty. Head `20261102_sg279_candidate_state` before and after. No migration command was run.

## Constraints

- **A1** — Socket-first literal block run; `docker version` printed a Server section. Pre-state matched the hypotheses (container `0c4462ee`, image `dcc67781`, head unchanged, restart count 0). `storagegenie-backend:release-sg296` → `dcc67781`; `compose … config --images` named `storagegenie-backend:release-sg296` for backend (rc 0). Rollback override written to scratch and not used. No rights probe.
- **A2** — One build (rc 0), one recreate (rc 0). No migration; alembic diff empty; head unchanged. Container and image ids before and after: see the table above.
- **A3** — Runtime diff = the derived set exactly (9 changed + 1 added). JS changed (hashes and sizes above). Served tree equals worktree for tracked files.
- **A4** — G2 strings quoted from the served container. Honest-limit sentence stated.
- **A5** — Health 6x 200, routes 200, review-tasks and assets 200, census identical, startup log clean.
- **A6** — Tag `release-sg299` created on `62db28ab` (branch of this run: `origin/automation` at 6cb9de6 as base). No tag removed or moved; `release-sg296`, `release-sg295`, `recovery-sg270` unchanged. State reached: **S1** (no rollback).
- **A7** — No owner name, id or field value in logs or report. No key or `.env` read or printed; the rollback override was used only as `config --images`. No provider call. No browser. No database write (sqlite opened `mode=ro`). Scratch removed by exact path: `rm -rf output/SG-299-scratch` (rc 0; `output/` otherwise untouched, `output/dispatch` untouched).
- **A8** — `PB-3` vacuity: failure would show as (a) an extra file in the runtime diff — checked, none (exactly 10); (b) unchanged JS hash — checked, changed; (c) missing string — checked, all present; (d) moved census count — checked, none moved; (e) route not 200 — checked, all 200; (f) restart loop — checked, restarts 0 at 10 s and at check; (g) traceback — checked, 0 matches in `docker logs`.
- **A9** — `HEAD` and `origin/automation` after the push are quoted in the publish step below.
- **A10** — Last line below.

## Owner / desk notes

- Run 1's two open questions: (1) the packet's runtime list was too narrow — fixed in this retry, and the derived list matches the run-1 finding; (2) `latest` pointed at an unverified build — now `latest` = `release-sg299` = served image.
- Run 1's full-tree hash dumps (`SG-299_runtime_before.sha256`, `SG-299_runtime_after.sha256`, `SG-299_worktree_py.sha256`) and its static files are kept as run 1 evidence and are not reused. This run's evidence is `SG-299_runtime_diff.txt` (small: changed paths with hashes) and `SG-299_census_after.txt`.

## Evidence (docs/worklogs/SG-299_*)

- `SG-299_runtime_diff.txt` (this run): changed and added paths with sha256 before and after, static files.
- `SG-299_census_after.txt` (this run): counts after; identical to G0.
- `SG-299_census_before.txt` (run 1 file): counts before; identical to the G0 output of this run.
- Run 1 files retained: `SG-299_runtime_before.sha256`, `SG-299_runtime_after.sha256`, `SG-299_worktree_py.sha256`, `SG-299_static_before.txt`, `SG-299_static_after.txt`.

Verification: PASS

---

## Run 1 (stopped in S0, expected set too narrow)

# SG-299 report — deploy rider: STOPPED in S0 (app not touched)

Slice SG-299 · model opencode-go/claude-haiku-5-5 · effort high (process args) · cwd /home/andrei/StorageGenie · remote git@github.com:Andovol/StorageGenie.git · BASE ref origin/automation → resolved 7903a0b252a0d9523c998256d90ca29a7bea62c2 · WORK_HEAD 7903a0b252a0d9523c998256d90ca29a7bea62c2

## Outcome

**STOPPED in S0.** The built image's runtime diff is not the expected set. The packet says any other file is a STOP in S0, before the recreate. No recreate was run, so the live backend (container `0c4462ee`, image `dcc67781`, release-sg296) was never touched. No `release-sg299` tag was created.

Runtime diff of the built image against the served container (Python tree, `docs/worklogs/SG-299_runtime_before.sha256` vs `_after`):
- Expected six app files, all changed: `app/api/v1/assets.py`, `reminders.py`, `review_tasks.py`, `app/services/asset_service.py`, `expiry_engine.py`, `lifecycle.py`.
- **Not expected, extra:** `backend/tests/test_plugin_expiry.py` (changed), `backend/tests/test_sg111_lifecycle.py` (changed), `backend/tests/test_sg272_flow.py` (new). The packet's derivation (`git diff --name-only 58ce7fa..HEAD -- backend/app`) does not include them, but the Dockerfile does `COPY backend/ ./`, so they are inside the served image tree.
- Also changed, not a `.py` file: `backend/tests/fixtures/sg136_asset_dict_baseline.json`.

I did not accept the extra files on my own authority. Decision for the owner/desk (see below).

## Phases (stamps from `date +%s`)

| Phase | Stamps | Seconds |
|---|---|---|
| G0 socket, pre-state, rollback override, compose `--images`, census, git | 1794342538 → 1794342569 | 31 |
| G1 pre-build snapshot + one `docker compose build backend` (rc 0, layers cached) | 1794342586 → 1794342589 | 3 |
| G1 runtime-diff check (throwaway `docker run --rm --network none`, no mounts) | 1794342615 → 1794342616 | 1 |
| Final state check | 1794342632 → 1794342632 | <1 |
| G1 recreate, G2, G3 | not run (S0 stop) | 0 |

Engine elapsed at the stop: about 110 s. Expected ≈300 s (`UNVERIFIED — my estimate`). Budget 2100 s; publish before 1200 s — met.

## State reached

**S0** — stop before the recreate. No S1, no rollback needed or used.

## Ids and state, before and after

| Item | Before | After |
|---|---|---|
| backend container | `0c4462ee548260ab08a89f39a6df92c77fbca0177414a9158caa3c564dbba102` | unchanged |
| running image | `sha256:dcc67781b9392fcc7914ce015abbda7454a6f498fe6ef9c2b3897b604eadc7d3` | unchanged |
| restart count / health | 0 / healthy | 0 / healthy |
| built image (not served) | — | `sha256:5867d89b579e995ca574be19a3d3b8f52b4d97b7c590d8808134e7bf58693ca8` |
| `storagegenie-backend:release-sg296` | `dcc67781b939` | unchanged |
| `storagegenie-backend:latest` | `dcc67781b939` | **`5867d89b579e`** (moved by the compose build; see below) |
| `release-sg299` tag | absent | absent (not created) |
| `release-sg295`, `recovery-sg270` | present | unchanged |

Alembic: `git diff --name-only 58ce7fa..HEAD -- backend/alembic` is empty; head `20261102_sg279_candidate_state` before and after. No migration command was run.

Census (read-only `sqlite3` `mode=ro` on the live file, counts only): before and after **identical**, every table (`docs/worklogs/SG-299_census_before.txt`, `_after.txt`).

## Frontend (static, from the served container and the built image)

- `index.html`: 944 B, `4b803f41…` → `97437d95…` (changed in the built image)
- JS: `index-aRzURpTy.js` 336969 B, `80e565d2…` → `index-CjbyAByJ.js` 347968 B, `665dcb11…` (changed in the built image)
- CSS: `index-C07VbG0m.css` 4535 B, `c3b58cda…` (unchanged)

Served-tree-equals-worktree: the built image's `.py` tree (2187 files) equals the worktree hashes exactly (`docs/worklogs/SG-299_worktree_py.sha256`). The served (running) container's tree differs from the worktree only in the six app files and the three test files above.

## Constraints

- **A1** — Socket-first literal block run; `docker version` printed a Server section; pre-state quoted and matched; `release-sg296` resolved to `dcc67781` and `compose … config --images` named it (rc 0; the `--images` form only). Rollback override written at `output/SG-299-scratch/rollback.override.yml` and not used. No rights probe.
- **A2** — One build, rc 0. No migration; alembic diff empty; head unchanged. Recreate **not** run, so no new container.
- **A3** — **FAIL.** Runtime diff is not the expected set (see Outcome). JS changed (hashes and sizes above). Served tree equals worktree for the built image.
- **A4** — Not reached (no recreate, so G2 strings not checked in a served container).
- **A5** — Health `{"status":"ok","db":"ok","storage":"ok"}` at G0 and at the final check. The six health probes, shell routes, `review-tasks`/`assets` probes and startup log were not run (no restart). Census identical.
- **A6** — `release-sg299` not created; no tag removed; `latest` moved by the compose build (not in the packet). State reached: **S0**.
- **A7** — No owner name, id or field value printed; census output is table names and counts only; no key or `.env` read or printed; no provider call; no browser; no database write (sqlite opened `mode=ro`); `docker compose config` only with `--images`; scratch removed by exact path (shown below).
- **A8** — `PB-3` vacuity check: failures were looked for as (a) extra file in the runtime diff — **found** (`backend/tests/*`), which caused the stop; (b) unchanged JS hash — checked, changed; (c) missing string — not reached; (d) moved census count — checked, none moved; (e) route not 200 — not run; (f) restart loop — checked, restarts 0; (g) traceback — not checked (no restart).
- **A9** — Final lines below quote `HEAD` and `origin/automation`.
- **A10** — Last line below.

## For the owner / desk

1. **Scope of the runtime diff.** Decide whether `backend/tests/*` changes are allowed in a deploy rider. The tests are not imported by `app.server:app`, but the packet's rule is explicit (`backend/app` only). If they are acceptable, amend the expected list and re-run SG-299; otherwise keep the rule.
2. **`storagegenie-backend:latest` now points at the unverified build `5867d89b`** (moved from `dcc67781` by `docker compose build`). A later `docker compose up` for backend without `--no-build` would pick it up. I did not move it back, because the packet forbids moving tags. Repoint `latest` to `dcc67781` or accept the new image.

## Evidence (docs/worklogs/SG-299_*)

`SG-299_census_before.txt`, `SG-299_census_after.txt`, `SG-299_runtime_before.sha256`, `SG-299_runtime_after.sha256`, `SG-299_worktree_py.sha256`, `SG-299_static_before.txt`, `SG-299_static_after.txt`.

Verification: STOPPED in S0 — built image's runtime diff contains files outside the expected set (`backend/tests/test_plugin_expiry.py`, `backend/tests/test_sg111_lifecycle.py` changed; `backend/tests/test_sg272_flow.py` new); app not touched.
