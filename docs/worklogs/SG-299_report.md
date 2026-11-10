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
