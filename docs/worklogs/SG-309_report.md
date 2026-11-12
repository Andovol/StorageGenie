# SG-309 report — deploy rider: serve SG-308

SG-309 | model: opencode-go/claude-haiku-5-5 | effort: not stated to me (not read from process arguments; not visible to me) | cwd: /home/andrei/StorageGenie | remote: origin git@github.com:Andovol/StorageGenie.git | BASE: origin/automation -> e4618b7dc4c6f5015e06a05cd3a3b5f1d0e80935 | WORK_HEAD: the report commit (see Publish below)

Contract version echoed from my own contract as received: `0.59.0 (D30, 2026-11-12)`. The contract folder was not read.

## State reached

S1 — new container started, healthy within about 10 s, no rollback. The rollback override was prepared but not used.

## Phases (stamps from `date +%s`)

| Phase | Start | End | s |
|---|---|---|---|
| G0 socket, health, git | 1794491120 | 1794491122 | 2 |
| G0 pre-state, read-only census, running-tree hash | 1794491129 | 1794491154 | 25 |
| Rollback override written, `config --images` | 1794491138 | 1794491138 | 0 |
| G1 build, tree compare (the first compare script had a bad assertion; re-parsed the saved output, no rebuild) | 1794491168 | 1794491208 | 40 |
| G1 recreate, healthy, tag | 1794491220 | 1794491232 | 12 |
| G3 health x6, routes, data endpoints | 1794491246 | 1794491246 | 0 |
| G2 served bytes, key counts | 1794491262 | 1794491273 | 11 |
| Startup log, census after | 1794491290 | 1794491290 | 0 |

Engine elapsed: 170 s (1794491120 to 1794491290), against the ≈300 s estimate and the packet's ≈150 s expectation. Budget 2100 s; publish point 1200 s — both met.

## Ids before and after

| Item | Before | After |
|---|---|---|
| Container | `0b4742d3536e…` (healthy, restart count 0) | `d01a24930670…` (healthy, restart count 0) |
| Image | `sha256:1e13973463de…` | `sha256:62e616895158…` |
| Cmd | `uvicorn app.server:app --host 0.0.0.0 --port 8000` | same |
| Alembic head | `20261102_sg279_candidate_state` | same, no migration |
| Tag `latest` | `1e13973463de` | `62e616895158` |
| Tag `release-sg303` | `1e13973463de` | unchanged |
| Tag `release-sg309` | absent | `62e616895158` (created) |
| Tags `release-sg299`, `release-sg296`, `release-sg295`, `recovery-sg270` | present | present, unmoved |

The `release-sg309` tag was created on the new image. Its code commit is e4618b7 on `automation`, the build context being the clean worktree at that commit (`git status --short` was empty before the build).

## Census

Read-only (`mode=ro`) on the live file, no WAL or SHM copy needed. `docs/worklogs/SG-309_census_before.txt` vs `SG-309_census_after.txt`: diff empty. Every table identical; `reminder` 4 before, 4 after. The startup reminder pass reported `reminders_created=0`.

## Runtime diff (G1)

- Derived backend set, `git diff --name-only cdbae72..HEAD -- backend/ ':!backend/alembic'`: **empty**. My expectation was empty: match.
- `git diff --name-only cdbae72..HEAD -- backend/alembic`: empty.
- Whole `/app` tree, 4067 files both sides, from a throwaway `docker run --network none` with no mounts or env:
  - changed: `static/index.html`, hash `c1fbfb2d296b` → `e5bfc84f5c9f`, 944 bytes both.
  - removed: `static/assets/index-gWdOr0um.js`, `92c2fe7a58fc`, 357041 bytes.
  - added: `static/assets/index-BL66eLr6.js`, `095f99df799a`, 356660 bytes.
  - CSS `static/assets/index-Dl7Tsxob.css` unchanged: `95b25525e050`, 4731 bytes.
  - No non-`static/` path changed.
- The backend `COPY` layer re-ran rather than hitting cache; the file hashes are nonetheless identical to the running image.

Served bytes: `GET /` returned `index.html` with hash `e5bfc84f5c9f` (944 bytes); the bundle it names, `/assets/index-BL66eLr6.js`, returned `095f99df799a` (356660 bytes). Both equal the new image's files.

## G2 — the new behaviour in the served artifact

Counts in the served JS (`output/SG-309-scratch/served.js`, deleted below) vs the old `release-sg303` bundle:

| String | Old bundle | Served bundle |
|---|---|---|
| `pantry-assets` | 4 | 2 |
| `pantry-expiry` | 4 | 2 |
| `household-assets` | 1 | 2 |
| `asset-facets` | 1 | 2 |
| `What you have, and what to use first.` | 1 | 1 |

The `pantry-assets` and `pantry-expiry` drop is expected, and the source explains it. At `cdbae72` the Pantry held three invalidations per key (tile -1, tile gone, put-back) plus its query key, so 4 each. SG-308 moved those three invalidations into the shared helper `invalidateAssetViews`. The helper plus the Pantry query key gives 2 each in source (`frontend/src/lib/invalidateAssetViews.ts`, `PantryPage.tsx`), and the bundle carries 2 each. The helper's own keys (`household-assets`, `asset-facets`) rose from 1 to 2. The helper's name is minified, so the body is what shows: `kn(e,t)` invalidates `["pantry-assets"]` and `["pantry-expiry"]`.

**Honest limit:** no item-panel action was exercised live, because each writes the owner's data. The first real use of the refresh is the owner's.

## G3 — the app answers, nothing moved

- `/v1/health` six times: `{"status":"ok","db":"ok","storage":"ok"}` each time.
- Shell routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/assets?household_id=…&category=food_beverages&limit=5`: 200, 1 item on the first page.
- `GET /v1/plugins/expiry-tracker/status?household_id=…&category=food_beverages`: 200.
- The household id was read from the database into a shell variable and never printed.
- Startup log, named lines only: `Traceback` 0; `Application startup complete` 1; `Daily reminder pass` 1 (`households_visited=1 reminders_created=0 errors=0`).

## SG-308 rating note

`docs/ratings.md` rates SG-308 84 with "hard stop breached (≈1450/1300 s) → flagged to owner and desk". That is a coder-side timing breach. SG-308 is rated, so the close-out rule applies and the deploy proceeds as the packet directs. The breach is recorded here and remains open with the owner and desk.

## Constraints

- **A1** — Socket-first literal block run; `docker version` shows a Server section; pre-state quoted; override names `release-sg303` and resolves `backend` to it; no rights probe.
- **A2** — One `docker compose build backend` (rc 0), one `docker compose up -d --no-deps --force-recreate backend` (rc 0); no migration; head unchanged; alembic diff empty; ids above.
- **A3** — Runtime diff equals the derived set (empty backend, `static/` only); JS changed; CSS and `index.html` hashes and sizes quoted; served bytes equal the image's.
- **A4** — G2 strings quoted from the served bundle; honest-limit sentence above.
- **A5** — Health and routes 200; census identical; startup log clean (0 Tracebacks).
- **A6** — `release-sg309` created on the new image, code commit e4618b7 on `automation`; no tag removed or moved; state S1, no rollback.
- **A7** — No owner name, id or field value appears in this report or any log output; no key or `.env` read or printed; no provider call; no browser; no database write (`mode=ro` only); scratch removed by exact path (shown below).
- **A8** — Vacuity: failure signatures checked — extra file in runtime diff (none outside `static/`), unchanged JS hash (changed), missing strings (present), moved count (census identical, reminder 4 unchanged), route not 200 (all 200), restart loop (restart count 0, healthy), traceback (0).
- **A9** — Phase seconds above from stamps. `HEAD` and `origin/automation` hashes are in the final publish output, not in this file (a commit cannot record its own hash).
- **A10** — See the last line.

## Scratch and evidence

Scratch `output/SG-309-scratch/` removed by exact path after the census and G2 checks. Evidence files kept: `docs/worklogs/SG-309_report.md`, `SG-309_runtime-diff.txt`, `SG-309_census_before.txt`, `SG-309_census_after.txt`.

Verification: PASS
