# SG-329 — Deploy rider: serve SG-328 (the catalog opens in Standard Grid)

SG-329 | model opencode-go/muse-spark-1.3-contributor effort=xhigh (per AGENTS.md model policy; process argv unreadable in lane — stated honestly) | workdir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation resolved to 4f2fbc29214c14d82dc82002c8660f3892c113df | WORK_HEAD pre-report 4f2fbc29214c14d82dc82002c8660f3892c113df (equals origin/automation; post-report hash quoted in publish)

Contract: packet records 0.61.0. This lane denies reading the contract folder; I did not try. Host evidence: I received none. (I received no contract version line in process args/env. I do not echo the project file's line as host evidence.)

Engine elapsed 181 s (G3_END 1794853895 minus G0_START 1794853714) vs expected ≈200 s (UNVERIFIED — packet's estimate: SG-327 152 s, SG-323 167 s; plus one local build). Phases: G0 41 s (3714→3755), G1 84 s (3755→3839; build 3755→3804 incl. tree hashes, recreate 3804→3806, recreate-to-healthy 13 s 3806→3819), G2 37 s (3839→3876), G3 19 s (3876→3895). Runtime against RUN_BUDGET_S 2100 s: 181/2100, well inside. Publish before 1200 s bound: yes (report committed and pushed in same session, stamps quoted).

State reached: S1 (new container healthy, no rollback). S0 passed (app never touched before recreate). S1 healthy within 120 s with RestartCount 0, so no rollback. S2 not entered.

Ids before/after:
- Before: container 9c7f8b81facea8c7dbe3250b5b9fa494e1a83316ee81ffa06b1d0ffb09588b32, image sha256:0cf8bdc1825a2b7dbf121bc99931d057459ec6b5e498ef7c3e2190a3198beaa3, Cmd [uvicorn app.server:app --host 0.0.0.0 --port 8000], RestartCount 0, Health healthy. `storagegenie-backend:latest` and `storagegenie-backend:release-sg327` both resolved to 0cf8bdc1 before build.
- After: container 3527c078842dbd454e34f16748e29b98b3f18539ef2e2ec74f954e86fb70d381, image sha256:409bf8a1469a46ddca7e3a4bf6efd1c690547647c7972077ee2bc41220e92a35, Cmd [uvicorn app.server:app --host 0.0.0.0 --port 8000], RestartCount 0, Health healthy. `storagegenie-backend:latest` and new tag `storagegenie-backend:release-sg329` both resolve to 409bf8a1 after. Recreate-to-healthy 13 s (3806→3819).

Census before/after (read-only byte copy, 29 tables; full counts in docs/worklogs/SG-329_census.txt):
- Before: alembic_version=1 assertion=40 asset=7 asset_evidence=20 asset_fts=7 asset_fts_config=1 asset_fts_data=9 asset_fts_docsize=7 asset_fts_idx=7 asset_location=1 asset_relation=1 audit_event=104 candidate=10 enrich_snapshot=4 evidence=27 guardrail_event=2 household=1 idempotency_key=11 job=11 job_step=72 location=1 observation=20 planning_suggestion=0 provider_call=39 reminder=4 review_task=9 saved_search=0 source_attribution=0 user=2
- After: identical (all 29 counts equal). `reminder` stayed 4, consistent with startup log `Daily reminder pass completed ... reminders_created=0`. No other table moved.

Constraints (one line each):
- No product byte changed: derived product change is frontend-only (CatalogPage.tsx SG-328 52283be); backend/ (minus alembic) diff empty, deps empty, alembic empty; runtime diff shows static/ only.
- Written only docs/worklogs/SG-329* in git plus scratch path and one image tag: staged only by exact path docs/worklogs/SG-329*, no product/config/schema/migration/dependency/test byte.
- DATABASE read-only only: schema head and table census only, no write/migration/repair; opened live DB read-only on byte copy (WAL 0 bytes, SHM present, copy valid).
- Restart one recreate of backend only: one `docker compose build backend` rc 0, one `docker compose up -d --no-deps --force-recreate backend` rc 0; no other service touched.
- Provider none, no spend: no provider called, no key read/printed, no .env opened, $0.
- No /tmp for any command including curl -o: TMPDIR and DOCKER_CONFIG set to scratch, woff2 probe and all curl outputs to scratch paths; lane /tmp denied, never used.
- Never docker rmi/image prune/system prune/compose config without --images: only `config --images` used; no removal/move of tags.
- Never tag/untag/stop/restart app to test rights (PG-PR-01): no rights probe; only inspect --format, images, ps, config --images, run --rm --network none.
- A denial is STOP, never another route: no denial encountered (contract folder not attempted per packet; /proc argv unreadable, stated not routed around; release-sg329 tag absent before creation as expected, created once).
- Startup log read only by named lines: `grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`, never wider; no household id in output.
- No name/id/field value of owner in log/report: household id taken from DB into shell variable, never printed (only status codes and first-page item counts quoted); no key/.env read/printed; no provider; no browser; no DB write; scratch removed by exact path `rm -rf output/SG-329-scratch` (removal shown in publish step), never touched `output/` itself or `output/dispatch`.

## G0 — Socket-first and pre-state

- `date +%s` G0_START 1794853714 quoted.
- Literal block run with workdir /home/andrei/StorageGenie:
  - `mkdir -p output/SG-329-scratch/docker-config`, `export DOCKER_CONFIG="$PWD/output/SG-329-scratch/docker-config"`, `export TMPDIR="$PWD/output/SG-329-scratch"`, `export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-329/docker.sock"`, `echo "$DOCKER_HOST"` → `unix:///run/dispatch-storagegenie-SG-329/docker.sock`, `ls -l /run/dispatch-storagegenie-SG-329/` → `srw-rw---T 1 andrei ... docker.sock`, `docker version` prints Server section (Client 29.9.2, Server 29.9.2, API 1.56). Socket-first proven.
- `curl -s http://127.0.0.1:8003/v1/health` → `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state hypotheses from docs/releases/2026-11-16-sg327.md all hold: container `9c7f8b81…` full `9c7f8b81facea8c7dbe3250b5b9fa494e1a83316ee81ffa06b1d0ffb09588b32`, image `0cf8bdc1…` full `sha256:0cf8bdc1825a2b7dbf121bc99931d057459ec6b5e498ef7c3e2190a3198beaa3`, head `20261102_sg279_candidate_state` (DB `SELECT version_num FROM alembic_version` read-only → that value), RestartCount 0, Cmd `[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, Health healthy. `docker inspect` only with `--format` and named fields. No different running image; no STOP.
- `storagegenie-backend:release-sg327` resolves to the running image id 0cf8bdc1; `output/SG-329-scratch/rollback.override.yml` contains only `services.backend.image: storagegenie-backend:release-sg327`; `docker compose -f docker-compose.yml -f output/SG-329-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg327` for backend. Otherwise STOP would have fired; it did not.
- Read-only census: byte copy of live DB (+shm/wal) to scratch, opened `mode=ro`, counts only (see evidence). 29 tables as above.
- No rights probe on any real object.

A1 met.

## G1 — ONE build, ONE recreate

- `date +%s` G1_START 1794853755.
- One `docker compose build backend`, rc 0. Where latest points: before 0cf8bdc1825a, after 409bf8a1469a.
- Cache note, not assumed: build log showed frontend `COPY frontend/` and `RUN npm run build` as CACHED, yet the produced tree differs (new JS name/hash below) — so I compared the image's runtime tree against the worktree instead of assuming: the runtime diff (below) plus the local vite build of HEAD (G2) prove the new image carries HEAD's frontend.
- Runtime diff (whole served /app tree, old 0cf8bdc1 vs new 409bf8a1 via authorised `docker run --rm --network none --entrypoint sh <image> -c 'cd /app && find . -type f -exec sha256sum {} +'` for both; same flags for old, read-only):
  - Derived expected backend set myself: `git diff --name-only 1d7cb04..HEAD -- backend/ ':!backend/alembic'` → empty (my expectation quoted as empty, matches). Then only static/ may differ.
  - Measured: old_files 4071 new_files 4071; OLD-ONLY `./static/assets/index-MC93YmcZ.js 328d7367…`, NEW-ONLY `./static/assets/index-y4viF7r0.js f6f6a12e…`, CHANGED `./static/index.html old=e5df1970… new=507116e3…`. backend_like_changed 0. Any measured backend file would have been STOP in S0; none found.
  - JS must change: yes, different names and hashes, sizes 369451 → 369208.
  - CSS byte-identical: same name `index-BGbwuPTO.css`, same hash `90d62853…`, same size 6172. Listed with size.
  - woff2 byte-identical: same names `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` hash `2ee17598…` size 30092 and `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` hash `c4fcfea4…` size 11144, listed with sizes and hashes.
  - Full evidence in docs/worklogs/SG-329_runtime_diff.txt (changed paths with both hashes, not full-tree dumps).
- Alembic head unchanged before and after (`20261102_sg279_candidate_state`); `git diff --name-only 1d7cb04..HEAD -- backend/alembic` empty; no migration command run.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0 at 1794853804→3806. Now S1. New container id, image id, Cmd, restart count, health as above; measured recreate-to-healthy 13 s (3806→3819, healthy within 120 s, RestartCount stayed 0).
- Tag what now serves: `storagegenie-backend:release-sg329` was absent → created via `docker tag storagegenie-backend:latest storagegenie-backend:release-sg329`, now resolves to 409bf8a1. Resolves-elsewhere case did not occur. Never removed/moved any tag; `release-sg327`, `release-sg323`, `release-sg320`, `release-sg317`, `release-sg314`, `release-sg310`, `release-sg309`, `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295` and `recovery-sg270` all stay with G0 ids.

A2 and A3 met.

## G2 — New behaviour in served artifact

- `date +%s` G2_START 1794853839.
- From served container's own files (docker run --rm --network none, no mounts/env/port):
  - Served JS differs from old: old `index-MC93YmcZ.js 328d7367…` vs new `index-y4viF7r0.js f6f6a12e…` (hashes quoted).
  - Served name and hash equal a local `vite build` of HEAD into scratch (VITE_API_BASE=https://storagegenie.dynv6.net read from backend/Dockerfile line 8, not guessed): local build produced `index-y4viF7r0.js f6f6a12e…`, `index-BGbwuPTO.css 90d62853…`, both woff2 hashes equal, `index.html 507116e3…` — all five byte-equal to served.
  - Present strings (full counts in docs/worklogs/SG-329_strings.txt): OLD→NEW `[Use by] 6→6`, `[Check this item] 1→1`, `[Add to catalog] 1→1`, `[Cut out the item again] 1→1`, `[More actions for] 2→2`, `[Standard Grid] 1→1`. All six present before and after (>=1); none missing.
- `GET /assets/<woff2 the CSS names>` on 127.0.0.1:8003: CSS names both woff2; `GET /assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` → 200, content-type `application/octet-stream` (backlog W11, not a STOP), size 30092, sha matches served tree.
- Honest limit: No screen is viewed in a browser here; the default is proven by SG-328's test (`frontend/src/sg328-grid-default.sg328.test.tsx`) and the owner sees it live; no candidate is decided on the live app here.

A4 met.

## G3 — App answers, nothing moved

- `date +%s` G3_START 1794853876, G3_END 1794853895.
- `/v1/health` six times, each quoted: all six `{"status":"ok","db":"ok","storage":"ok"}`.
- Shell routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/assets?household_id=<id>&category=food_beverages&limit=5` → 200, items_on_first_page 1 (response has no total; only first-page count quoted; household id from DB never printed). `GET /v1/plugins/expiry-tracker/status?household_id=<id>&category=food_beverages` → 200, items_on_first_page 1 (rows). Only status codes and first-page counts quoted.
- Startup log read only by named lines: `docker logs --since 10m | grep -E 'Traceback|Application startup complete|Daily reminder pass'` → `INFO: Application startup complete.` and `INFO: app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-16 households_visited=1 reminders_created=0 errors=0`, no Traceback. Access log not read; no household id in output. Log clean.
- Census after vs G0: identical (all 29 counts equal); `reminder` 4→4, accounted for by `reminders_created=0`; any other table moving would have been reported at once — none moved.
- Container still RestartCount 0, healthy.

A5 met.

## Acceptance

- A1: Socket-first literal block proven; pre-state quoted (9c7f8b81/0cf8bdc1/head/0); rollback override names release-sg327 and `config --images` confirms; no rights probe.
- A2: One build rc 0, one recreate rc 0; no migration (head unchanged, alembic diff empty); container/image ids before/after quoted.
- A3: Runtime diff equals derived set (derived lists and my empty expectations quoted); no backend file; JS changed (names/hashes/sizes) and equals local build of HEAD; CSS and woff2 unchanged with sizes/hashes; served tree equals worktree via runtime diff + local build.
- A4: G2 strings quoted from served artifact (counts above); honest-limit sentence stated.
- A5: Health/routes 200 quoted; census compared identical; startup log clean (two named lines, no traceback).
- A6: `release-sg329` newly created on new image id; no tag removed/moved (all old tags listed present with G0 ids); state S1 (healthy, no rollback) named (S0 passed, S2 not entered).
- A7: No owner name/id/field value in logs/report (household id never printed, only counts); no key/.env read/printed; no provider; no browser; no DB write; scratch removed by exact path `rm -rf output/SG-329-scratch` (removal shown in publish step), never touched `output/` itself or `output/dispatch`.
- A8: PB-3 vacuity — a failure would look like: an extra file in the runtime diff (checked: only 3 static paths), an unchanged JS hash (checked: hashes/names differ), a missing string (checked: all six >=1 in new), a moved count (checked: census identical), a route not 200 (checked: all 200), a restart loop (checked: RestartCount 0, healthy), a traceback (checked: grep found none). All checked and quoted.
- A9: HEAD equals origin/automation after push — pre-report both 4f2fbc29214c14d82dc82002c8660f3892c113df; post-report hashes quoted in publish block below; phase seconds quoted above.
- A10: Last line is Verification below.

## Publish

Report commit carries trailer `Dispatch-ID: SG-329`. Staged only by exact path `docs/worklogs/SG-329*`. Tracked status clean (`git status --short --untracked-files=no` empty); untracked `output/` is engine + scratch, untouched except own scratch removal.

Next steps (step 1): Owner shelf trial on live release-sg329 (Standard Grid default served); report any trial findings; then stage D planning. No further build needed unless the trial finds a defect.

Verification: PASS
