# SG-320 report — deploy rider: serve SG-318, prove the served bytes, keep the way back

First line: slice SG-320; model opencode-go/muse-spark-1.3-contributor and effort xhigh read from process arguments (`opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/muse-spark-1.3-contributor --variant xhigh`); working directory /home/andrei/StorageGenie; remote origin git@github.com:Andovol/StorageGenie.git; BASE ref origin/automation; resolved BASE commit 7a24601dc5dafb1cf187c293122a7b4d5d303225; WORK_HEAD at start 7a24601dc5dafb1cf187c293122a7b4d5d303225 (HEAD equals origin/automation, worktree clean for tracked files).

Own contract version line (as received): none received. I did not read the contract folder.

## Outcome

State reached: **S1, no rollback.** The new container became healthy in 14 s with restart count 0. No product byte changed. The runtime change is `static/` only: the JS bundle and `index.html` changed; the CSS bundle kept the same name and hash (no style change in SG-318); the two `.woff2` files are byte-identical. The `release-sg320` tag was created on the new image. No other tag moved.

## Phase timing (from `date +%s` stamps)

| Phase | Start | End | Seconds |
|---|---|---|---|
| G0 socket, pre-state, census | 1794513964 | 1794514038 | 74 |
| G1 build start to built | 1794514047 | 1794514068 | 21 |
| G1 recreate to healthy | 1794514098 | 1794514112 | 14 (recreate rc 0 at 1794514099) |
| G1 tag | 1794514115 | 1794514115 | 0 (absent before, created) |
| G2 served strings + font | 1794514123 | 1794514135 | ~12 |
| G3 health/routes/API/logs/census | 1794514141 | 1794514164 | 23 |

Engine elapsed, first to last stamp: 200 s (1794513964 to 1794514164). Expected ≈150 s (`UNVERIFIED — my estimate`: SG-314 159 s, SG-317 123 s; no new package). Budget ceiling 2100 s; publish bound 1200 s; no hang bound was reached. Runtime against budget (`PG-PR-06`): 200 s of 2100 s, well under; publish started under 1200 s.

## G0 — socket and pre-state

- Literal socket block run: `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-320/docker.sock`; `ls -l /run/dispatch-storagegenie-SG-320/` listed the socket; `docker version` printed a Server section (Engine 29.9.2), rc 0.
- Health before: `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state matched hypotheses from `docs/releases/2026-11-12-sg317.md`: container `e61b3784941f1088bc508e4aa2a027b4702e40a4ea01d14cbf5b930205ef923d` (`e61b3784…`), image `sha256:1bdf6799b90cd6797bf01333b4e75c0179cc48a4cb7b750fe84547878faadc5f` (`1bdf6799…`), restart count 0, healthy, StartedAt `2026-11-12T19:29:56.96304178Z`, Cmd `[uvicorn app.server:app --host 0.0.0.0 --port 8000]`. `docker inspect` only with `--format` and named fields.
- `storagegenie-backend:release-sg317` resolves to `sha256:1bdf6799b90cd6797bf01333b4e75c0179cc48a4cb7b750fe84547878faadc5f`, equal to the running image. `docker compose -f docker-compose.yml -f output/SG-320-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg317` for backend.
- Rollback override written at `output/SG-320-scratch/rollback.override.yml` setting only `services.backend.image: storagegenie-backend:release-sg317`.
- No rights probe on any real object.
- Alembic head before: `20261102_sg279_candidate_state` (file list head and `SELECT version_num FROM alembic_version` read-only). No migration command run.
- Census before (read-only `mode=ro` on `data/db/storagegenie.db`; WAL 0 bytes so live file read directly; counts only; evidence `docs/worklogs/SG-320_census-before.txt`): 29 tables identical to SG-317 (assertion 40, asset 7, asset_evidence 20, asset_fts 7, audit_event 104, candidate 10, evidence 27, job 11, job_step 72, observation 20, provider_call 39, reminder 4, review_task 9, plus zeros for planning_suggestion/saved_search/source_attribution).
- Derived sets from `b9b5f3e..HEAD`: backend excluding alembic EMPTY; alembic EMPTY; `frontend/package.json frontend/package-lock.json` EMPTY. Expectation (packet, labelled as such): empty. Matched. Changed paths in the range are frontend sources, docs/packets, docs/ratings, STATE and worklogs only (no backend file).

## G1 — one build, one recreate

- `docker compose build backend`: rc 0. Frontend layers `COPY frontend/ ./` and `RUN npm run build` rebuilt (14.1 s, 1973 modules, `dist/index.html 0.94 kB`, `index-_brNCbOJ.js 365.64 kB`, `index-BGbwuPTO.css 6.17 kB`, woff2 11.14 kB and 30.09 kB); backend layers CACHED. The rebuild proves the frontend context came from the current worktree; the worktree equals HEAD (clean for tracked files).
- `storagegenie-backend:latest` before: `sha256:1bdf6799b90cd6797bf01333b4e75c0179cc48a4cb7b750fe84547878faadc5f`. After build: `sha256:10d6064f670eb066437c47e0d7e06ed19df1483564edebca056c4a46874bf191`.
- Runtime diff (evidence `docs/worklogs/SG-320_runtime-diff.txt`; authorised `docker run --rm --network none --entrypoint sh <image> -c 'cd /app && find . -type f -exec sha256sum {} +'` on both images; 4069 files each): only `static/` differs. Changed: old JS `index-C3KByf5V.js` removed, new JS `index-_brNCbOJ.js` added; `static/index.html` hash changed. Unchanged: `index-BGbwuPTO.css` same name and hash `90d6285326accc47e61b3073b951bb4e04234b582e495d2d8ec83c9144d6b6c0` (6172 bytes) before and after — SG-318 carries no style change, so the CSS bundle did not change; the packet expectation that CSS must change is not met, honestly reported. `.woff2` byte-identical: `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` `c4fcfea41f2c1cfeea9211fa43679845454a1d0e0d7e95e069c7e73c4ae302d2` (11144 bytes), `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` `2ee17598a98d8a59e4df8152d015bec9ab8e4d5672cc0ab42bef806b568e3971` (30092 bytes). No path outside `static/` differs, so the measured set equals the derived backend-empty set.
- Alembic head unchanged; no migration command.
- `docker compose up -d --no-deps --force-recreate backend`: rc 0. Now S1.

## Identities before and after

| | Before | After |
|---|---|---|
| Container | `e61b3784941f1088bc508e4aa2a027b4702e40a4ea01d14cbf5b930205ef923d` | `07aa3de8b980325d88313aad052a82a9b58ba90a2d916906f76c828db0b30c08` |
| Image | `sha256:1bdf6799b90cd6797bf01333b4e75c0179cc48a4cb7b750fe84547878faadc5f` | `sha256:10d6064f670eb066437c47e0d7e06ed19df1483564edebca056c4a46874bf191` |
| Restart count | 0 | 0 |
| Health | healthy | healthy (14 s from recreate start) |
| Cmd | `uvicorn app.server:app --host 0.0.0.0 --port 8000` | same |
| `:latest` | 1bdf6799 | 10d6064f (moved by the build) |
| `:release-sg317` | 1bdf6799 | 1bdf6799 (unchanged) |
| `:release-sg320` | absent | created on 10d6064f |

No tag removed or moved; `release-sg314`, `release-sg310`, `release-sg309`, `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295` and `recovery-sg270` stay. `prover` not touched. No `docker rmi`, prune, or `docker compose config` without `--images`.

## G2 — the new behaviour is in the served artifact

Counts from each image's own `/app/static/assets` JS (`grep -o -F`):

| String | release-sg317 (before) | release-sg320 (after) |
|---|---|---|
| `Not started` | 0 | 5 |
| `Checking your upload` | 0 | 1 |
| `Reading the photo` | 0 | 1 |
| `Making items` | 0 | 1 |
| `Date entered by you` | 0 | 1 |
| `No photo yet` | 2 | 4 |
| `Unnamed item` | 5 | 5 |
| `Untitled asset` | 1 | 0 |
| `Thumbnail unavailable` | 2 | 1 |

The served JS after contains all seven new wordings and no longer contains `Untitled asset`. `Thumbnail unavailable` falls 2→1 (the EvidenceGallery instance fixed by SG-318 W4 is gone); one instance remains from `CandidateCard.tsx:93` (out of SG-318 scope, honest). `Unnamed item` is 5→5 (SG-317 already carried it; SG-318 replaced the one `Untitled asset` with it and left the total at 5).

Font: the CSS names `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` and `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` under `/assets/`. `GET /assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` on `127.0.0.1:8003` returns 200, `content-type: application/octet-stream`, 30092 bytes. `GET /assets/instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` returns 200, `application/octet-stream`, 11144 bytes (backlog W11 expects `application/octet-stream`; reported, not a STOP).

Honest limit: no screen is viewed in a browser here; the screens were seen in SG-319 on a scratch build of the same commit.

## G3 — the app answers, and nothing moved

- `/v1/health` six times: each `{"status":"ok","db":"ok","storage":"ok"}`, http 200.
- Shell routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/assets?household_id=<id>&category=food_beverages&limit=5`: http 200, first page 1 item (id taken from the database into a shell variable and never printed; response has no `total`).
- `GET /v1/plugins/expiry-tracker/status?household_id=<id>&category=food_beverages`: http 200.
- Startup log, named lines only (`grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`): `INFO: Application startup complete.`, `INFO: app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-12 households_visited=1 reminders_created=0 errors=0`, no `Traceback` line.
- Census after compared with G0 (evidence `docs/worklogs/SG-320_census-after.txt`; `diff` empty): every table identical; `reminder` stays at 4, consistent with the reminder pass creating 0. Head still `20261102_sg279_candidate_state`.

## Acceptance criteria

- A1 — Socket-first proven with the literal block; pre-state quoted; the rollback override names `release-sg317`; no rights probe.
- A2 — One build, one recreate, rc 0; no migration (head unchanged, alembic diff empty); container and image ids before and after quoted.
- A3 — Runtime diff equals the derived set (derived backend empty and my expectation empty both quoted; matched). JS changed and `index.html` changed; CSS unchanged (same hash, honestly reported against the must-change expectation); `.woff2` unchanged with sizes and hashes; no backend file outside the derived set; served tree from the rebuilt frontend context equals the worktree (HEAD clean).
- A4 — G2 strings quoted from the served artifact with before/after counts; `Untitled asset` 1→0, `Thumbnail unavailable` 2→1 with out-of-scope cause named; the honest-limit sentence stated.
- A5 — Health 200 x6 and routes 200; census compared identical; startup log clean (no Traceback).
- A6 — `release-sg320` created on the new image (absent before); no tag removed or moved; state reached S1, no rollback (healthy in 14 s, restarts 0).
- A7 — No owner name, id or field value in any log or report; no key or `.env` read or printed; no provider; no browser; no database write (read-only census only); scratch `output/SG-320-scratch/` removed by exact path (shown in the commit step).
- A8 — `PB-3` vacuity: checked for an extra file in the runtime diff (none outside `static/`), an unchanged JS hash (changed: different name and hash), a missing new string (all seven present after), a moved count (census identical), a route not 200 (all 200), a restart loop (restarts 0), a traceback (none).
- A9 — `HEAD` equals `origin/automation` after push, both hashes quoted in the publish step; phase seconds from the stamps above.
- A10 — Last line is `Verification: PASS`.

## Constraints

- Written only `docs/worklogs/SG-320*` in git; `output/SG-320-scratch/` scratch only; the one `release-sg320` image tag; the backend container recreated once (no rollback second recreate).
- No product, config, schema, migration, dependency or test byte. No other service touched. No data repair. Stored photos and files untouched.
- Staged only by the exact path `docs/worklogs/SG-320*`; `git status --short` clean for tracked files and `git show --stat HEAD` holds only those paths (shown in publish).
- Authorised runtimes only: docker/compose as named, `curl` to `127.0.0.1`, read-only SQLite census. No `docker rmi`/prune, no `config` without `--images`.
- Contract: own version line none received; project file line never used as evidence; contract folder never read (denial expected, not a STOP).

Verification: PASS
