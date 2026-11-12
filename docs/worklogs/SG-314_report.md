# SG-314 report — deploy rider: serve SG-312 static bundle as release-sg314

SLICE SG-314 | model: opencode-go/claude-haiku-5-5 (own identity; effort not visible in process arguments, no `opencode run` process listed by `ps`) | cwd: /home/andrei/StorageGenie | remote: origin git@github.com:Andovol/StorageGenie.git | BASE ref: origin/automation, resolved 614f61b09955a58c11830439ed3b382fd7eba995 | WORK_HEAD: 614f61b09955a58c11830439ed3b382fd7eba995

Contract version line (own copy as received): `Rule-set version recorded here: 0.59.0 (D30, 2026-11-12)`. The contract folder was not read; the contract version command was not run (its name is not in my instructions, and the lane denies that folder).

## Outcome

State reached: **S1** — new container started, healthy in 11 s, restart count 0. No rollback was needed; the previous image was not served. Verification: PASS.

## Phases (stamps from `date +%s`)

| Phase | Start | End | Seconds |
|---|---|---|---|
| G0 socket, pre-state, census, rollback resolution, old-tree hash | 1794507062 | 1794507098 | 36 |
| G1 build (rc 0) | 1794507113 | 1794507116 | 3 |
| G1 tree hash, sizes, comparison | 1794507116 | 1794507119 | 3 |
| G1 recreate (rc 0) to healthy | 1794507128 | 1794507139 | 11 |
| Tag release-sg314 + served-artifact check | 1794507172 | 1794507173 | 1 |
| G2 extra + G3 (health x6, routes, API, log, census) | 1794507190 | 1794507221 | 31 |
| Engine elapsed, G0 to G3 | 1794507062 | 1794507221 | 159 |

Engine elapsed 159 s against the ≈250 s estimate: under. Budget ceiling 2100 s; publish point 1200 s — both respected. Gaps between calls (planning time) are not counted.

## G0 — socket and pre-state

- Literal socket block: `docker version` printed a Server section (Engine 29.9.2). Socket `/run/dispatch-storagegenie-SG-314/docker.sock` present.
- `curl -s http://127.0.0.1:8003/v1/health` before the change: `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state matched the hypotheses: container `77bcbb51c6a4f7b87d9c01e316a112b3fdbb254ac1e262a6220d24182202927f`, image `sha256:969ce26419f906a1cf8cd0c3078c654ca734825122dfb2c0010de3ec471394e5`, restart count 0, healthy, alembic head `20261102_sg279_candidate_state`.
- Rollback override `output/SG-314-scratch/rollback.override.yml` sets only `services.backend.image: storagegenie-backend:release-sg310`. `docker compose -f docker-compose.yml -f <override> config --images` resolved backend to `storagegenie-backend:release-sg310`. The base `config --images` resolved to `storagegenie-backend`. Always with `--images`.
- `storagegenie-backend:release-sg310` resolves to `sha256:969ce264…`, the running image.
- No rights probe on any object.
- Census (read-only, byte copy of `data/db/storagegenie.db` plus its zero-byte WAL, opened with `PRAGMA query_only`): 29 tables; counts in `SG-314_census-before.txt`.

## G1 — one build, one recreate

- `docker compose build backend`: rc 0, 3 s. `storagegenie-backend:latest`: `969ce264…` before, `91b0969e9e0bf42dd0f10b666109ddbfb5706e3fc9b7bd82945446c6e1999655` after. Build log: `SG-314_build.log`.
- Derived backend set, `git diff --name-only 80011d0..HEAD -- backend/ ':!backend/alembic'`: **empty**. My expectation (empty) matched. Dependency files `frontend/package.json` and `frontend/package-lock.json` diff: empty.
- Runtime diff over `/app` (4069 files before and after, sha256 of each file, both images run with `--network none`): see `SG-314_runtime-diff.txt`.
  - Changed: `static/index.html` (31ecda559fb6… → 2f624e68167f…).
  - Added: `static/assets/index-D9KTmi-1.css`, `static/assets/index-DmXb2Y62.js`.
  - Removed: `static/assets/index-NSe2tTq7.js`, `static/assets/index-PyJpCP1_.css`.
  - No backend file changed.
  - The two Instrument Sans `.woff2` files are byte-identical: `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` 11144 bytes, `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` 30092 bytes, same sha256 before and after.
- Alembic head before and after: `20261102_sg279_candidate_state`. No migration command run.
- `docker compose up -d --no-deps --force-recreate backend`: rc 0 (no `--build`).
- Container before: `77bcbb51c6a4…` on `969ce264…`, restart 0. Container after: `5cd1079878a8353356c434636f24ea769fc390b6e65bb09be28afc6f45614945` on `91b0969e…`, restart 0, healthy, `Cmd=[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, started 2026-11-12T18:12:08Z.
- Tag: `storagegenie-backend:release-sg314` was absent; created on `sha256:91b0969e9e0bf42dd0f10b666109ddbfb5706e3fc9b7bd82945446c6e1999655`. `release-sg310` still on `969ce264…`. No tag removed or moved. The `storagegenie-backend:prover` tag (`665caf31…`, created today 15:07 UTC) exists and was not touched by this slice.

## G2 — the new behaviour in the served artifact

Read from the served container's own files (`docker exec` on `5cd10798…`) and from the previous image (`release-sg310`), same script `SG-314_served-check.sh`:

- CSS `body` rule (served): `body{background-color:hsl(var(--paper));color:hsl(var(--foreground));font-family:var(--font-sans)}`. `--paper` count in CSS: 2 before, 3 after.
- Control-font rule (served): `button,input,select,textarea{font:inherit}`.
- Menu: `.nav-menu-toggle{display:none}` and `.nav-menu-toggle{display:inline-flex}` both present in the served CSS. The media context of the second rule was not checked in this slice.
- JS counts, before → after: `Checking the file` 0 → 1; `Tidying the details` 0 → 1; `Looking for duplicates` 0 → 1; `Your review` 0 → 1; `Saving` 4 → 5; `nav-menu-toggle` 0 → 1; `evidence state` 1 → 0; `per-press` 1 → 0.
- Fonts: `GET /assets/instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` → 200, `application/octet-stream`, 11144 bytes. `GET /assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` → 200, `application/octet-stream`, 30092 bytes. Matches backlog W11's expectation; not a stop.

**Honest limit:** no screen was viewed in a browser in this slice. The screens were seen in SG-313 on a scratch build of the same commit.

## G3 — the app answers, nothing moved

- `/v1/health` six times: each `{"status":"ok","db":"ok","storage":"ok"}`, rc 0.
- Routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/assets?household_id=…&category=food_beverages&limit=5`: 200, first page 1 item. The household id was read from the database copy into a shell variable and not printed.
- `GET /v1/plugins/expiry-tracker/status?household_id=…&category=food_beverages`: 200.
- Startup log, named lines only (`grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `--since 10m`): `Application startup complete.`; `Daily reminder pass completed as_of=2026-11-12 households_visited=1 reminders_created=0 errors=0`. No traceback.
- Census after: `SG-314_census-after.txt`. `diff` against before: no difference (rc 0). All 29 tables identical, `alembic_version` unchanged, `reminder` unchanged (`reminders_created=0`).

## Constraints

- **A1** — socket-first literal block; pre-state quoted and matched; override names `release-sg310`; no rights probe. Pass.
- **A2** — one build (rc 0), one recreate (rc 0); no migration (head unchanged, census identical); container and image ids before and after given above. Pass.
- **A3** — runtime diff equals the derived set (empty backend diff; `static/` only); JS and CSS changed; `.woff2` unchanged with sizes and hashes; served tree is the image built from a clean worktree at HEAD `614f61b` (`git status` showed only the untracked `output/`). Pass.
- **A4** — G2 strings quoted from the served artifact; honest-limit sentence stated. Pass.
- **A5** — health and routes 200; census compared; startup log clean. Pass.
- **A6** — `release-sg314` created on `91b0969e…` (an image tag, not a git tag); no tag removed or moved; state **S1** (no rollback). Pass.
- **A7** — no owner name, id or field value in any output or report; no key or `.env` read or printed by this lane (`docker compose` reads `.env` as its `env_file` directive); no provider call; no browser; no database write (census on a byte copy, `query_only`); no `docker compose config` without `--images`; scratch removed by exact path (`rm -rf output/SG-314-scratch`, then `ls` returned "No such file or directory"); `output/dispatch` still present. Pass.
- **A8** — vacuity check, failure modes covered: extra files in the runtime diff (none beyond the bundle names and `index.html`, which are the expected changes); unchanged JS hash (JS changed); missing strings (all new ones present, old ones gone); moved counts (census identical); route not 200 (none); restart loop (restart count 0 at inspect, 11 s after start, plus six successful health probes about a minute later — the restart count was not re-read after the probes); traceback (none in the named grep).
- **A9** — HEAD equals origin/automation after push: quoted in the publish output (see final message).
- **A10** — last line below.

Verification: PASS
