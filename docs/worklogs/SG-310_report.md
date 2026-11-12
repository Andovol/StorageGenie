# SG-310 report — deploy rider: serve SG-301 (Instrument Sans, header, plain words), prove served bytes

SG-310 | model: opencode-go/muse-spark-1.3-contributor | effort: xhigh (read from `output/dispatch/SG-310.launcher.sh`: `opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/muse-spark-1.3-contributor --variant xhigh`) | cwd: /home/andrei/StorageGenie | remote: origin git@github.com:Andovol/StorageGenie.git | BASE ref: origin/automation | BASE commit: 73d0d360179ef7155018b7996b41f8f48c3876e0 | WORK_HEAD: the report commit (see Publish below; a commit cannot record its own hash)

Contract version echoed from my own contract as received: `0.59.0 (D30, 2026-11-12)`. The contract folder was not read (denial expected, not a STOP).

SG-301 rating: 80 in `docs/ratings.md` (Instrument Sans 5.3.0 pinned OFL, header in paper look, plain words via `labels.ts`, EXPIRED 13px; shots by SG-311 rated 96).

## State reached

S1 — new container started, healthy within ~16 s, restart count 0, no rollback. The rollback override was prepared but not used. No S2.

## Phases (stamps from `date +%s`)

| Phase | Start | End | s |
|---|---|---|---|
| G0 socket, health | 1794495033 | 1794495034 | 1 |
| G0 pre-state, rollback override, `config --images`, read-only census, old-tree hash | 1794495043 | 1794495090 | 47 |
| G1 build (`docker compose build backend`, rc 0) | 1794495105 | 1794495143 | 38 |
| G1 new-tree hash + runtime diff | 1794495143 | 1794495149 | 6 |
| G1 recreate (`up -d --no-deps --force-recreate backend`, rc 0) to healthy | 1794495171 | 1794495187 | 16 |
| G1 tag `release-sg310` | 1794495187 | 1794495194 | 7 |
| G2 served artifact (CSS/woff2/JS counts) | 1794495212 | 1794495258 | 46 |
| G3 health x6, routes, data endpoints, logs, census after | 1794495258 | 1794495276 | 18 |
| Evidence + report write | 1794495276 | 1794495302 | 26 |

Engine elapsed G0 start to G3 end: 243 s (1794495033 to 1794495276), against the ≈300 s estimate and the packet's ≈250 s expectation (`UNVERIFIED — my estimate`: SG-309 took 170 s; this build fetches one new npm package). Budget `RUN_BUDGET_S` 2100 s, publish bound 1200 s — both met. Runtime against budget per `PG-PR-06`: ~243 s / 2100 s, publish well before 1200 s.

## Ids before and after

| Item | Before | After |
|---|---|---|
| Container | `d01a24930670…` (healthy, restart count 0) | `77bcbb51c6a4…` (healthy, restart count 0) |
| Image | `sha256:62e616895158…` | `sha256:969ce26419f9…` |
| Cmd | `uvicorn app.server:app --host 0.0.0.0 --port 8000` | same |
| Alembic head | `20261102_sg279_candidate_state` | same, no migration |
| Tag `latest` | `62e616895158` | `969ce26419f9` |
| Tag `release-sg309` | `62e616895158` | unchanged |
| Tag `release-sg310` | absent (No such image) | `969ce26419f9` (created) |
| Tags `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295`, `recovery-sg270` | present | present, unmoved |

The `release-sg310` tag was created on the new image. Its code commit is `73d0d36` on `automation`, the build context being the worktree with only `docs/worklogs/SG-310*` untracked at build time (`git status --short` showed only those + `output/` scratch; `git diff --name-only e4618b7..HEAD -- backend/` empty).

## G0 — socket-first and pre-state

Literal block run:

```
mkdir -p output/SG-310-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-310-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-310/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-310/
docker version
```

`unix:///run/dispatch-storagegenie-SG-310/docker.sock`, `srw-rw----T 1 andrei docker.sock`, `docker version` shows Client 29.9.2 + Server 29.9.2 (Engine, containerd, runc, rootlesskit) — Server section present.

- `curl -s http://127.0.0.1:8003/v1/health` → `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state hypotheses from `docs/releases/2026-11-12-sg309.md`: container `d01a2493…` matched `d01a24930670`, image `62e61689…` matched `sha256:62e616895158…`, head `20261102_sg279_candidate_state` matched DB `SELECT version_num FROM alembic_version`, restart count 0 matched `docker inspect --format '{{.RestartCount}}'`. `docker inspect` only with `--format` and named fields.
- `storagegenie-backend:release-sg309` resolves to `sha256:62e616895158…` (running image id) and `docker compose -f docker-compose.yml -f output/SG-310-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg309` for `backend`. Rollback override file sets only `services.backend.image: storagegenie-backend:release-sg309`.
- Read-only census (`file:data/db/storagegenie.db?mode=ro`, no WAL copy needed — WAL 0 B, SHM 32 KiB, mount writable): `docs/worklogs/SG-310_census_before.txt`, identical to SG-309's census (see Census below).
- No rights probe on any real object (`PG-PR-01`): never tagged, untagged, stopped or restarted anything to test rights.

## G1 — ONE build, ONE recreate

- One `docker compose build backend`, rc 0. Build log: `frontend-build 4/6 RUN npm ci` CACHED (cache held the SG-301r1 image build with the new lockfile), `COPY frontend/ ./` re-ran, `RUN npm run build` re-ran: `1973 modules`, `dist/index.html 0.94 kB`, `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2 11.14 kB`, `instrument-sans-latin-wght-normal-BbzFLZTg.woff2 30.09 kB`, `index-PyJpCP1_.css 5.52 kB`, `index-NSe2tTq7.js 358.97 kB`. Backend layers (`apt`, `pip`, `COPY backend/`) CACHED.
- Because cache-satisfied, runtime tree compared against worktree (not assumed): derived backend set `git diff --name-only e4618b7dc4c6f5015e06a05cd3a3b5f1d0e80935..HEAD -- backend/ ':!backend/alembic'` → empty. My expectation, labelled as such: empty. Match. `git diff --name-only e4618b7..HEAD -- backend/alembic` → empty.
- Runtime diff (whole `/app` tree, throwaway `docker run --rm --network none` with no mounts/env/port, authorised command `docker run --rm --network none --entrypoint sh storagegenie-backend:latest -c 'cd /app && find . -type f -exec sha256sum {} +'` for the new tree; same flags for the old `release-sg309` tree): old 4067 files, new 4069 files. `docs/worklogs/SG-310_runtime-diff.txt` holds changed paths with both hashes (not full dumps):
  - changed: `./static/index.html` running `e5bfc84f5c9f` → new `31ecda559fb6`
  - removed: `./static/assets/index-BL66eLr6.js` `095f99df799a` (356660 B), `./static/assets/index-Dl7Tsxob.css` `95b25525e050` (4731 B)
  - added: `./static/assets/index-NSe2tTq7.js` `c135e1d391a4` (359160 B), `./static/assets/index-PyJpCP1_.css` `e1eca724a61c` (5517 B), `./static/assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` `2ee17598a98d` (30092 B), `./static/assets/instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` `c4fcfea41f2c` (11144 B)
  - No non-`static/` path differs — equals the derived set (empty backend). Any measured backend file outside the derived set would have been a STOP in S0; none found.
- Served tree equals worktree: backend in the new image reuses the cached backend layers that equal the worktree backend (derived set empty, backend diff empty, old image built from `e4618b7` with same backend); frontend `static/` in the image is the worktree frontend built at HEAD (vite 1973 modules, woff2 sizes match SG-301's `build-check` proof 30092 B + 11144 B).
- Alembic head unchanged before and after (`20261102_sg279_candidate_state` in both censuses); `git diff --name-only e4618b7..HEAD -- backend/alembic` empty; no migration command.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0. Now S1. New container `77bcbb51c6a4…`, image `969ce26419f9…`, `Cmd [uvicorn app.server:app --host 0.0.0.0 --port 8000]`, restart count 0, health `healthy`; measured recreate-to-healthy 16 s (1794495171 to 1794495187; `up` rc at 1794495172, `healthy` at third 5-s poll). No restart loop, so no rollback serve.
- Tag what now serves: `storagegenie-backend:release-sg310` was absent → created via `docker tag storagegenie-backend:latest storagegenie-backend:release-sg310` on `969ce26419f9…`. Absent→create branch taken. Never removed or moved any tag; `release-sg309`, `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295`, `recovery-sg270` stay.

## G2 — the new behaviour is in the served artifact

From the served container's own files (`docker exec storagegenie-backend-1`):

- Served CSS `index-PyJpCP1_.css` contains `@font-face{font-family:Instrument Sans Variable;font-style:normal;font-display:swap;font-weight:400 700;src:url(/assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2) format("woff2-variations")` and the second `@font-face` for `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` — quoted. Count `Instrument Sans Variable` = 3 (two faces + one token).
- `--font-sans` beginning with it: `--font-sans: "Instrument Sans Variable", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` — quoted.
- The `.woff2` the `@font-face` names exist in `static/assets/`: `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` 30092 B, `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` 11144 B (`ls -l /app/static/assets/instrument-sans*.woff2`).
- `GET /assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` on `127.0.0.1:8003` returns 200, `content-type: application/octet-stream`, `content-length: 30092`. `GET /assets/instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` returns 200, `content-type: application/octet-stream`, `content-length: 11144`.
- Served JS counts (`grep -o … | wc -l` — occurrence counts, not `grep -c` line counts on minified bundles):
  - `optimistic concurrency`: old (release-sg309) 2 → new 1. The remaining 1 is `ItemInspectorDrawer.tsx:441` (`Uses If-Match: {current.version} for optimistic concurrency`) — catalog drawer, SG-307 scope, not SG-301. SG-301 removed the Asset page copy (`AssetDetailPage.tsx` `Uses If-Match: {version} for optimistic concurrency` gone; worktree `grep -rn` shows only the drawer line). `blueprint urgency order`: old 1 → new 0 — the Expiry dev paragraph is gone from source (`grep -rn blueprint urgency order frontend/src/` empty) and from the bundle.
- Label-map strings (SG-301 report §G2 table, `frontend/src/lib/labels.ts` + `AppHeader.tsx`): served JS contains `Showing:` 1, `Needs attention` 2, `Possible duplicate` 2. One quoted match: `Needs attention` (from `labels.ts:15 FAILED: "Needs attention"`) appears in the served bundle — the plain word replacing raw `FAILED`/`COMPLETED` states.

Honest limit: no screen is viewed in a browser here. The owner's first look is the visual check.

## G3 — the app answers, and nothing moved

- `/v1/health` six times, each `{"status":"ok","db":"ok","storage":"ok"}` (1794495258 block, all 200 bodies quoted).
- Shell routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200 (`curl -s -o /dev/null -w "%{http_code}"`).
- `GET /v1/assets?household_id=<redacted>&category=food_beverages&limit=5` → 200, `items` on first page = 1, no `total` key. `GET /v1/plugins/expiry-tracker/status?household_id=<redacted>&category=food_beverages` → 200, `rows` = 1, `unresolved_rows` = 0. Household id read from the database into `HH` shell variable and never printed (only `HH_LEN=36` shown).
- Startup log, named lines only: `docker logs --since 10m storagegenie-backend-1 | grep -E 'Traceback|Application startup complete|Daily reminder pass'` → `INFO: Application startup complete.` (1), `Daily reminder pass completed … households_visited=1 reminders_created=0 errors=0` (1), `Traceback` 0. No wider filter; no access-log line printed (access log carries household ids per backlog W10).
- Census after `docs/worklogs/SG-310_census_after.txt` vs before: `diff -u` empty, rc 0. Every table identical; `reminder` 4 before, 4 after — may rise only as the startup line accounts for, and it reports `reminders_created=0`, so no rise. Alembic head `20261102_sg279_candidate_state` both sides.

## Census

Before (`SG-310_census_before.txt`) = after (`SG-310_census_after.txt`): `alembic_head 20261102_sg279_candidate_state`, `alembic_version 1`, `assertion 40`, `asset 7`, `asset_evidence 20`, `asset_fts 7`, `asset_fts_config 1`, `asset_fts_data 9`, `asset_fts_docsize 7`, `asset_fts_idx 7`, `asset_location 1`, `asset_relation 1`, `audit_event 104`, `candidate 10`, `enrich_snapshot 4`, `evidence 27`, `guardrail_event 2`, `household 1`, `idempotency_key 11`, `job 11`, `job_step 72`, `location 1`, `observation 20`, `planning_suggestion 0`, `provider_call 39`, `reminder 4`, `review_task 9`, `saved_search 0`, `source_attribution 0`, `user 2`.

## Constraints (one line each)

- A1 — Socket-first literal block run; `docker version` Server 29.9.2 shown; pre-state quoted (container `d01a24930670`, image `62e61689`, head, restart 0); rollback override names `release-sg309` and `config --images` names it; no rights probe.
- A2 — One build rc 0, one recreate rc 0; no migration (head unchanged, alembic diff empty); container/image ids before/after quoted above.
- A3 — Runtime diff equals derived set (derived `git diff --name-only e4618b7..HEAD -- backend/ ':!backend/alembic'` empty, my expectation empty, both quoted; measured diff `static/` only); JS and CSS changed (hashes/sizes quoted); two `.woff2` listed with sizes (30092 B, 11144 B); served tree equals worktree (backend cached-equal, frontend built from HEAD).
- A4 — G2 strings quoted from served artifact (`@font-face` + `--font-sans` + woff2 + `Needs attention`); honest-limit sentence present.
- A5 — Health 6×200 and routes 200 quoted; census identical; startup log clean (0 Tracebacks).
- A6 — `release-sg310` created on new image (absent→create branch); no tag removed/moved; state S1 (no rollback) named.
- A7 — No owner name/id/field value in report/logs; no key or `.env` read/printed; no provider; no browser; no DB write (`mode=ro` only); scratch `output/SG-310-scratch/` removed by exact path (removal shown below).
- A8 — PB-3 vacuity checked: extra backend file in diff (none — `NON-STATIC DIFF: []`), unchanged JS hash (changed `095f99df`→`c135e1d39`), missing `@font-face`/woff2 (present, 2 files), moved count (census diff empty), route not 200 (all 200), restart loop (restart 0, healthy), traceback (0).
- A9 — Phase seconds from stamps above; `HEAD` equals `origin/automation` after push — both hashes in publish output below (a commit cannot record its own hash in its file).
- A10 — See last line.

## Scope ceiling

Written `docs/worklogs/SG-310*` only in git (`SG-310_report.md`, `SG-310_runtime-diff.txt`, `SG-310_census_before.txt`, `SG-310_census_after.txt`); `output/SG-310-scratch/` (docker-config, old/new-tree hashes, rollback override); one `release-sg310` tag; backend container recreated once (no rollback second). No product/config/schema/migration/dependency/test byte. No other service touched. No data repair. Stored photos/files untouched. Staged only by exact path `docs/worklogs/SG-310*`; `git status --short` clean except those (plus scratch, removed before report close); `git show --stat HEAD` will hold only those paths. Authorised runtimes only: named docker/compose, `curl` to `127.0.0.1`, read-only SQLite census. Never `docker rmi/image prune/system prune` or `config` without `--images`.

## Scratch and evidence

Scratch `output/SG-310-scratch/` removed by exact path `rm -rf output/SG-310-scratch` after census/G2 (removal `ls` shown in publish block). Never touched `output/` itself or `output/dispatch`. No `/tmp` used for any command including `curl -o` (used `-o /dev/null` and pipes). Evidence kept: `docs/worklogs/SG-310_report.md`, `SG-310_runtime-diff.txt`, `SG-310_census_before.txt`, `SG-310_census_after.txt` — each small (diff as changed paths + hashes).

Verification: PASS
