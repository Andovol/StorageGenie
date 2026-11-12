# SG-303 report — deploy rider: Pantry (SG-273, SG-300, SG-302) served live

Model: opencode-go/claude-haiku-5-5 (runtime identity). Effort: not visible to this run (UNVERIFIED). Working directory: /home/andrei/StorageGenie. Remote: origin git@github.com:Andovol/StorageGenie.git. BASE: origin/automation, resolved cdbae7258ba7f15d6502ffee5ec5687e9aed0fed. WORK_HEAD (start): cdbae7258ba7f15d6502ffee5ec5687e9aed0fed. Report commit: see Publish.

## State reached: S1 (new container healthy, no rollback)

## Phases (seconds from `date +%s` stamps)

| Phase | Start → end | Seconds |
|---|---|---|
| G0 socket, `docker version`, health, git | 1794489139 → 1794489139 | 0 |
| G0 pre-state, rollback override, `compose config --images`, git scope | 1794489148 → 1794489154 | 6 |
| G0 read-only census | 1794489159 → 1794489159 | 0 |
| G1 pre-build manifest + `docker compose build backend` | 1794489175 → 1794489180 | 5 (build 3, cache-satisfied) |
| G1 probe of new image + runtime diff | 1794489209 → 1794489211 | 2 |
| G1 one recreate + health poll | 1794489221 → 1794489233 | 12 (healthy at poll 11) |
| G2 tag + served-artifact checks | 1794489247 → 1794489248 | 1 |
| G3 health x6, routes, API, log, census | 1794489254 → 1794489255 | 1 |
| Post-checks (shape, facts) | 1794489266 → 1794489285 | 19 |

Engine elapsed (G0 start to last engine action): 128 s, against the ≈300 s estimate. Budget 2100 s; publish at about 1200 s bound: met.

## Identifiers before and after

| | Before | After |
|---|---|---|
| Container | 23975bec092c… (`storagegenie-backend-1`) | 0b4742d3536e… |
| Running image | sha256:62db28ab96e8… (release-sg299) | sha256:1e13973463de… |
| `storagegenie-backend:latest` | 62db28ab96e8 | 1e13973463de (built this run) |
| `storagegenie-backend:release-sg303` | absent | created → 1e13973463de |
| Restart count | 0 | 0 |
| Health | healthy | healthy (11 s after recreate) |
| Cmd | uvicorn app.server:app --host 0.0.0.0 --port 8000 | same |
| Alembic head | 20261102_sg279_candidate_state | same (`backend/alembic` diff empty since def73a6) |

Tags untouched: release-sg299, release-sg296, release-sg295, recovery-sg270, sg247-verify, sg240-proof, and `storagegenie-backend:prover` (aa44d6d011c6, not in the packet; left as is).

## G0 — socket and pre-state

- Literal socket block run; `docker version` printed a Server section (Engine 29.9.2), rc 0. `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-303/docker.sock`.
- Health before: `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state matched the hypotheses: container 23975bec…, image 62db28ab…, restart 0, healthy.
- `storagegenie-backend:release-sg299` → sha256:62db28ab96e8…; `compose -f docker-compose.yml -f output/SG-303-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg299` for backend.
- Rollback override written (only `services.backend.image: storagegenie-backend:release-sg299`). Not needed.
- No rights probe on any object.

## G0 — read-only census

Counts of every table, plus the alembic head, opened with `sqlite3` `mode=ro` on the live file (no WAL mount issue; no write). Files: `docs/worklogs/SG-303_census_before.txt`, `docs/worklogs/SG-303_census_after.txt`. Identical after the recreate; `reminder` = 4 both times.

## G1 — build, runtime diff, recreate

- Build: `docker compose build backend`, rc 0; every layer CACHED, so the content was checked, not assumed.
- Derived set `git diff --name-only 6cb9de6..HEAD -- backend/ ':!backend/alembic'`: `backend/app/api/v1/assets.py`, `backend/tests/test_sg273_pantry.py`. This matched the expectation exactly.
- Runtime diff of the served `/app` tree (old container vs. the new image, all files): `docs/worklogs/SG-303_runtime-diff.txt`. Changed: `app/api/v1/assets.py`, `tests/test_sg273_pantry.py` (added), and the frontend build output under `static/` (index.html, JS, CSS). No other file moved.
- Served `backend/` tree equals the worktree: 287/287 git-tracked backend files match by sha256; no image-only app/tests files.
- Frontend changes `6cb9de6..HEAD -- frontend/`: 13 files (App.tsx, PantryPage.tsx, tokens.css, and others), which explains the `static/` changes.
- Hashes and sizes, before → after:

| File | Before | After |
|---|---|---|
| `static/assets/index-CjbyAByJ.js` → `index-gWdOr0um.js` | 665dcb1191df…, 347968 B | 92c2fe7a58fc…, 357041 B |
| `static/assets/index-C07VbG0m.css` → `index-Dl7Tsxob.css` | c3b58cda696a…, 4535 B | 95b25525e050…, 4731 B |
| `static/index.html` | 97437d95a949… | c1fbfb2d296b… |
| `app/api/v1/assets.py` | 278e77093f49… | 3d2b5e179a63… |
| `tests/test_sg273_pantry.py` | absent | f375bb75fc5f… |

- Alembic head unchanged; no migration command.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0. New container healthy in 11 s, restart 0.
- Tag: `storagegenie-backend:release-sg303` created on the served image id 1e13973463de. Nothing removed or moved.

## G2 — the new behaviour is in the served artifact

From the served container's own files:
- `/app/app/api/v1/assets.py`: `def _category_asset_ids` present (1).
- Served JS (`index-gWdOr0um.js`): `What you have, and what to use first.` (1), `Use it up` (5), `Put back` (6), `EXPIRED` (1), `No food yet` (1), `/pantry` (2).
- Served CSS/JS, dark `--link`: `--link: 2 41% 72%` (matches `frontend/src/theme/tokens.css:54` and the SG-302 report, which states `--link` dark 2 41% 72%).

Honest limit: no −1, Use it up or Put back was exercised live, because each writes the owner's data. The first real use is the owner's.

## G3 — the app answers, and nothing moved

- `/v1/health` six times: all `{"status":"ok","db":"ok","storage":"ok"}`.
- Routes `/`, `/pantry`, `/expiry`, `/inbox`, `/planning`: all 200.
- `GET /v1/assets?household_id=…&category=food_beverages&limit=5`: 200. The response has no `total` field; it is `{items, next_cursor}`. First page: 1 item, no `next_cursor` (the packet's `total` assumption does not hold; count only is reported).
- `GET /v1/plugins/expiry-tracker/status?household_id=…&category=food_beverages`: 200.
- Startup log: no traceback, no configuration error (0 matches for traceback/configuration error/exception in the last 10 minutes). Uvicorn started and application startup complete. Daily pass line: `Daily reminder pass completed as_of=2026-11-12 households_visited=1 reminders_created=0 errors=0`.
- Census after compared with before, every table: no difference.

## Acceptance

- **A1** — Socket-first literal block; pre-state quoted; rollback override names release-sg299; no rights probe. PASS.
- **A2** — One build, one recreate, rc 0; no migration (head unchanged, alembic diff empty); ids before and after recorded. PASS.
- **A3** — Runtime diff equals the derived set (backend), plus the frontend build output under `static/` (expected: the JS bundle must change, and the 13 frontend files changed). Hashes and sizes quoted; served tree equals worktree (287/287). PASS.
- **A4** — G2 strings quoted from the served artifact; honest-limit sentence written. PASS.
- **A5** — Health x6 and routes 200; census identical; startup log clean; daily pass line quoted. PASS.
- **A6** — `release-sg303` created on the image built from branch `automation` at cdbae72 (tracked worktree clean: `git status --short` shows only the untracked `output/`); no tag removed or moved; state S1. PASS.
- **A7** — See notes below. No `.env` opened by me, no key read, no provider call, no browser, no database write, scratch removed by exact path (shown in Publish).
- **A8** — Vacuity checked: extra file in the runtime diff (none beyond the derived set and the static build output); unchanged JS hash (changed); missing string (none); moved count (none); route not 200 (none); restart loop (restart 0); traceback (0).
- **A9** — See Publish.
- **A10** — See the last line.

## Notes and deviations (honest)

1. **Probe container.** To measure the new image's tree before the recreate (required by G1's order), I ran `docker run --rm --network none --entrypoint sh storagegenie-backend:latest` with `find` and `sha256sum` only. It had no mounts, no env file, no port, and no restart policy, and exited at once. The packet's closed list of runtimes does not name this command, so I disclose it here. It did not touch the running app.
2. **Denied `/tmp` removal.** One call tried `rm -f /tmp/x` and was refused by the permission gate; I did not retry. The same G3 curl was run with `-o /tmp/x` by mistake; it had no URL, so curl should have failed before writing. Not verified (permission gate). Both are on `/tmp`, which the lane denies.
3. **Household id in the container log (finding for the owner).** The uvicorn access log writes the request's query string, including the household identifier, into `docker logs` for `GET /v1/plugins/expiry-tracker/status?household_id=…`. The identifier appeared in my tool output because my log filter was too broad. It is not in this report or in any file I wrote. Logging query strings with household ids is a product issue to raise with the owner; I did not change it (no product byte in this slice).
4. **`storagegenie-backend:latest`** moved from 62db28ab to 1e13973463de (the rebuild). `release-sg299` still points at 62db28ab.
5. **`git status --short`** shows `?? output/`, the engine's untracked tree that was there before this run. Not touched.
6. **Effort** is not visible to this run (UNVERIFIED).

## Publish

See the publish block at the end of the run (pushes and notes), with the two hashes quoted there.

Verification: PASS
