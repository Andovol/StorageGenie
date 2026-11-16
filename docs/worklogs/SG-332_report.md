# SG-332 — Deploy rider: serve the catalog redesign (SG-330, SG-331: Midnight colours, photo-first cards, plain toolbar)

SG-332 | model opencode-go/muse-spark-1.3-contributor effort=xhigh (per AGENTS.md model policy; process argv unreadable in lane — stated honestly) | workdir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation resolved to 79227f2bf5d2a5969b8a0cdb83ee7897ee9d50de | WORK_HEAD pre-report 79227f2bf5d2a5969b8a0cdb83ee7897ee9d50de (equals origin/automation; post-report hashes quoted in publish)

Contract: packet records 0.61.0. This lane denies reading the contract folder; I did not try. Host evidence: I received none. (I received no contract version line in process args/env. I do not echo the project file's line as host evidence.)

Engine elapsed 233 s (G3_END 1794861825 minus G0_START 1794861592) vs expected ≈200 s (UNVERIFIED — packet's estimate: SG-329 181 s, SG-327 152 s; plus one local build). Phases: G0 52 s (1592→1644), G1 69 s (1644→1713; build 1644→1653, recreate 1675→1677, recreate-to-healthy 13 s 1677→1690), G2 69 s (1713→1782; local vite build + woff2 probe), G3 43 s (1782→1825). Runtime against RUN_BUDGET_S 2100 s: 233/2100, well inside. Publish before 1200 s bound: yes (report committed and pushed in same session, stamps quoted).

State reached: S1 (new container healthy, no rollback). S0 passed (app never touched before recreate). S1 healthy within 120 s with RestartCount 0, so no rollback. S2 not entered.

Ids before/after:
- Before: container 3527c078842dbd454e34f16748e29b98b3f18539ef2e2ec74f954e86fb70d381, image sha256:409bf8a1469a46ddca7e3a4bf6efd1c690547647c7972077ee2bc41220e92a35, Cmd [uvicorn app.server:app --host 0.0.0.0 --port 8000], RestartCount 0, Health healthy. `storagegenie-backend:latest` and `storagegenie-backend:release-sg329` both resolved to 409bf8a1 before build.
- After: container 94f432b0edafb738fc0eb17a94c15c387a7a0df019c818eb6a6c2a696a6b852c, image sha256:0cd2437de56e1a6d96833c635bd0167b25d654641bde84ac89ccde311c1c2900, Cmd [uvicorn app.server:app --host 0.0.0.0 --port 8000], RestartCount 0, Health healthy. `storagegenie-backend:latest` and new tag `storagegenie-backend:release-sg332` both resolve to 0cd2437d after. Recreate-to-healthy 13 s (1677→1690).

Census before/after (read-only byte copy, 29 tables; full counts in docs/worklogs/SG-332_census.txt):
- Before: alembic_version=1 assertion=40 asset=7 asset_evidence=20 asset_fts=7 asset_fts_config=1 asset_fts_data=9 asset_fts_docsize=7 asset_fts_idx=7 asset_location=1 asset_relation=1 audit_event=104 candidate=10 enrich_snapshot=4 evidence=27 guardrail_event=2 household=1 idempotency_key=11 job=11 job_step=72 location=1 observation=20 planning_suggestion=0 provider_call=39 reminder=4 review_task=9 saved_search=0 source_attribution=0 user=2
- After: identical (all 29 counts equal). `reminder` 4→4, consistent with startup log `reminders_created=0`. No other table moved.

Constraints (one line per constraint):
- No product byte changed: derived product change is frontend-only (CatalogPage/toolbar/tokens SG-330/SG-331); backend/ (minus alembic) diff empty, deps empty, alembic empty; runtime diff shows static/ only.
- Written only docs/worklogs/SG-332* in git plus scratch path and one image tag: staged only by exact path docs/worklogs/SG-332*, no product/config/schema/migration/dependency/test byte.
- DATABASE read-only only: schema head and table census only, no write/migration/repair; opened live DB read-only on byte copy (WAL 0 bytes, SHM present, copy valid).
- Restart one recreate of backend only: one `docker compose build backend` rc 0, one `docker compose up -d --no-deps --force-recreate backend` rc 0; no other service touched.
- Provider none, no spend: no provider called, no key read/printed, no .env opened, $0.
- No /tmp for any command including curl -o: TMPDIR and DOCKER_CONFIG set to scratch, woff2 probe and all curl outputs to scratch paths; lane /tmp denied, never used.
- Never docker rmi/image prune/system prune/compose config without --images: only `config --images` used; no removal/move of tags.
- Never tag/untag/stop/restart app to test rights (PG-PR-01): no rights probe; only inspect --format, images, ps, config --images, run --rm --network none.
- A denial is STOP, never another route: no denial encountered (contract folder not attempted per packet; release-sg332 absent before creation as expected, created once).
- Startup log read only by named lines: `grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`, never wider; no household id in output.
- No name/id/field value of owner in log/report: household id taken from DB into shell variable/file, never printed in report (only status codes and first-page counts quoted); no key/.env read/printed; no provider; no browser; no DB write; scratch removed by exact path `rm -rf output/SG-332-scratch` (removal shown in publish step), never touched `output/` itself or `output/dispatch`.

## G0 — Socket-first and pre-state

- `date +%s` G0_START 1794861592 quoted.
- Literal block run with workdir /home/andrei/StorageGenie:
  - `mkdir -p output/SG-332-scratch/docker-config`, `export DOCKER_CONFIG="$PWD/output/SG-332-scratch/docker-config"`, `export TMPDIR="$PWD/output/SG-332-scratch"`, `export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-332/docker.sock"`, `echo "$DOCKER_HOST"` → `unix:///run/dispatch-storagegenie-SG-332/docker.sock`, `ls -l /run/dispatch-storagegenie-SG-332/` → `srw-rw---T 1 andrei ... docker.sock`, `docker version` prints Server section (Client 29.9.2, Server 29.9.2, API 1.56). Socket-first proven.
- `curl -s http://127.0.0.1:8003/v1/health` → `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state hypotheses from docs/releases/2026-11-16-sg329.md all hold: container `3527c078…` full `3527c078842dbd454e34f16748e29b98b3f18539ef2e2ec74f954e86fb70d381`, image `409bf8a1…` full `sha256:409bf8a1469a46ddca7e3a4bf6efd1c690547647c7972077ee2bc41220e92a35`, head `20261102_sg279_candidate_state` (DB `SELECT version_num FROM alembic_version` read-only → that value), RestartCount 0, Cmd `[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, Health healthy. `docker inspect` only with `--format` and named fields. No different running image; no STOP.
- `storagegenie-backend:release-sg329` resolves to the running image id 409bf8a1; `output/SG-332-scratch/rollback.override.yml` contains only `services.backend.image: storagegenie-backend:release-sg329`; `docker compose -f docker-compose.yml -f output/SG-332-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg329` for backend. Otherwise STOP would have fired; it did not.
- Read-only census: byte copy of live DB (+shm/wal) to scratch, opened `mode=ro`, counts only (see evidence). 29 tables as above.
- No rights probe on any real object.

A1 met.

## G1 — ONE build, ONE recreate

- `date +%s` G1_START 1794861644.
- One `docker compose build backend`, rc 0. Where latest points: before 409bf8a1469a, after 0cd2437de56e. Build log showed frontend steps CACHED, so I did not assume — I compared the image's runtime tree against the worktree via the runtime diff below plus the local vite build of HEAD (G2).
- Runtime diff (whole served /app tree, old 409bf8a1 vs new 0cd2437d via authorised `docker run --rm --network none --entrypoint sh <image> -c 'cd /app && find . -type f -exec sha256sum {} +'` for both; same flags for old, read-only):
  - Derived expected backend set myself: `git diff --name-only 0119a87..HEAD -- backend/ ':!backend/alembic'` → empty (my expectation quoted as empty, matches). Then only static/ may differ.
  - Measured: total_old 4071 total_new 4071; OLD-ONLY `./static/assets/index-y4viF7r0.js old=f6f6a12e…` (size 369208), OLD-ONLY `./static/assets/index-BGbwuPTO.css old=90d62853…` (size 6172), NEW-ONLY `./static/assets/index-DlqlGk8g.js new=11e4ee1b…` (size 372812), NEW-ONLY `./static/assets/index-e_BzCe-6.css new=d0a1bbde…` (size 7307), CHANGED `./static/index.html old=507116e3… new=f5bf7b1f…` (size 944 both). backend_like_changed 0. Any measured backend file would have been STOP in S0; none found.
  - JS must change: yes, different names and hashes, sizes 369208 → 372812.
  - CSS must change: yes, different names and hashes (90d62853… → d0a1bbde…), sizes 6172 → 7307. Listed with sizes.
  - woff2 byte-identical: same names `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` hash `2ee17598…` size 30092 and `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` hash `c4fcfea4…` size 11144, listed with sizes and hashes, equal old vs new.
  - Full evidence in docs/worklogs/SG-332_runtime_diff.txt (changed paths with both hashes, not full-tree dumps).
- Alembic head unchanged before and after (`20261102_sg279_candidate_state`); `git diff --name-only 0119a87..HEAD -- backend/alembic` empty; no migration command run.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0 at 1794861675→1677. Now S1. New container id, image id, Cmd, restart count, health as above; measured recreate-to-healthy 13 s (1677→1690, healthy within 120 s, RestartCount stayed 0).
- Tag what now serves: `storagegenie-backend:release-sg332` was absent → created via `docker tag storagegenie-backend:latest storagegenie-backend:release-sg332`, now resolves to 0cd2437d. Resolves-elsewhere case did not occur. Never removed/moved any tag; `release-sg329`, `release-sg327`, `release-sg323`, `release-sg320`, `release-sg317`, `release-sg314`, `release-sg310`, `release-sg309`, `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295` and `recovery-sg270` all stay with G0 ids.

A2 and A3 met.

## G2 — New behaviour in served artifact

- `date +%s` G2_START 1794861713.
- From served container's own files (docker run --rm --network none, no mounts/env/port):
  - Served JS differs from old: old `index-y4viF7r0.js f6f6a12e…` vs new `index-DlqlGk8g.js 11e4ee1b…` (hashes quoted).
  - Served CSS differs from old: old `index-BGbwuPTO.css 90d62853…` vs new `index-e_BzCe-6.css d0a1bbde…`.
  - Served names and hashes equal a local `vite build` of HEAD into scratch (VITE_API_BASE=https://storagegenie.dynv6.net read from backend/Dockerfile line 8, not guessed): local produced `index-DlqlGk8g.js 11e4ee1b…`, `index-e_BzCe-6.css d0a1bbde…`, both woff2 hashes equal, `index.html f5bf7b1f…` — all five byte-equal to served.
  - Present strings (full counts in docs/worklogs/SG-332_strings.txt): OLD→NEW `[Your things] 0→1`, `[Add item] 0→2`, `[Search your things] 0→2`, `[Use by, soonest first] 0→1`, `[Per row] 0→2`, `[Photo grid] 0→1`, `[Show them] 0→1` (each >=1 after, all seven hold); `[Import Asset] 4→2`, `[Processing Status] 1→0`, `[Recently Added] 1→0`. Packet expected each of the last three 0 after; measured `Import Asset` 2 after — Nav in App.tsx retains it for non-catalog routes (showImport pathname!=="/" lines 156/176) while the CatalogToolbar copy was removed (4→2); the other two are 0 after as expected. All counts quoted honestly.
- In served CSS: Midnight ground HSL `45 14.3% 94.5%` (HSL form of #F3F2EF from frontend/src/theme/tokens.css) old 0 new 3 (>=1 after: yes); old paper `40 35.3% 93.3%` old 2 new 0 (0 after: yes).
- `GET /assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` on 127.0.0.1:8003 → 200, content-type `application/octet-stream` (W11, not a STOP), size 30092, sha matches served tree. Second woff2 also 200, same type, size 11144, sha matches.
- Honest limit: no screen is viewed in a browser here; no screenshot of the redesign exists yet (they follow next session); its tests are SG-330's and SG-331's; no candidate is decided on the live app here.

A4 met (with one honest deviation noted above).

## G3 — App answers, nothing moved

- `date +%s` G3_START 1794861782, G3_END 1794861825.
- `/v1/health` six times, each quoted: all six `{"status":"ok","db":"ok","storage":"ok"}`.
- Shell routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/assets?household_id=<id>&category=food_beverages&limit=5` → 200, items_on_first_page 1 (response has no total; only first-page count quoted; household id from DB never printed). `GET /v1/plugins/expiry-tracker/status?household_id=<id>&category=food_beverages` → 200, rows_on_first_page 1. Only status codes and first-page counts quoted.
- Startup log read only by named lines: `docker logs --since 10m | grep -E 'Traceback|Application startup complete|Daily reminder pass'` → `INFO: Application startup complete.` and `INFO: app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-16 households_visited=1 reminders_created=0 errors=0`, no Traceback. Access log not read; no household id in output. Log clean.
- Census after vs G0: identical (all 29 counts equal); `reminder` 4→4, accounted for by `reminders_created=0`; any other table moving would have been reported at once — none moved.
- Container still RestartCount 0, healthy.

A5 met.

## Acceptance

- A1: Socket-first literal block proven; pre-state quoted (3527c078/409bf8a1/head/0); rollback override names release-sg329 and `config --images` confirms; no rights probe.
- A2: One build rc 0, one recreate rc 0; no migration (head unchanged, alembic diff empty); container/image ids before/after quoted.
- A3: Runtime diff equals derived set (derived lists and my empty expectations both quoted); no backend file; JS and CSS changed (names/hashes/sizes) and equal local build of HEAD; both woff2 unchanged with sizes/hashes; served tree equals worktree via runtime diff + local build.
- A4: G2 strings quoted from served artifact (counts above, including honest 4→2 for Import Asset with reason); honest-limit sentence stated.
- A5: Health/routes 200 quoted; census compared identical; startup log clean (two named lines, no traceback).
- A6: `release-sg332` newly created on new image id; no tag removed/moved (all old tags listed present with G0 ids); state S1 (healthy, no rollback) named (S0 passed, S2 not entered).
- A7: No owner name/id/field value in logs/report (household id never printed, only counts); no key/.env read/printed; no provider; no browser; no DB write; scratch removed by exact path `rm -rf output/SG-332-scratch` (removal shown in publish step), never touched `output/` itself or `output/dispatch`.
- A8: PB-3 vacuity — a failure would look like: an extra file in the runtime diff (checked: only 5 static paths), an unchanged JS hash (checked: hashes/names differ), a missing string (checked: seven >=1 in new, two of three zeros 0), a moved count (checked: census identical), a route not 200 (checked: all 200), a restart loop (checked: RestartCount 0, healthy), a traceback (checked: grep found none). All checked and quoted.
- A9: HEAD equals origin/automation after push — pre-report both 79227f2bf5d2a5969b8a0cdb83ee7897ee9d50de; post-report hashes quoted in publish block below; phase seconds quoted above.
- A10: Last line is Verification below.

## Publish

Report commit carries trailer `Dispatch-ID: SG-332`. Staged only by exact path `docs/worklogs/SG-332*`. Tracked status clean (`git status --short --untracked-files=no` empty pre-commit except scratch untracked); untracked `output/` is engine + scratch, untouched except own scratch removal.

Next steps (step 1): Owner shelf trial on live release-sg332 (Midnight, photo-first cards, plain toolbar) served here; screenshots follow next session; then stage D planning. No further build needed unless trial finds a defect.

Verification: PASS
