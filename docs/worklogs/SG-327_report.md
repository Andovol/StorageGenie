# SG-327 — Deploy rider: serve polish A and B (SG-324, SG-324r1, SG-325)

SG-327 | model opencode-go/muse-spark-1.3-contributor effort=xhigh (per AGENTS.md model policy; process argv unreadable in lane — /proc denied, stated honestly) | workdir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation resolved to 19469ad48b0f0c10218c089f4690d8fec44595ba | WORK_HEAD pre-report 19469ad48b0f0c10218c089f4690d8fec44595ba (equals origin/automation; post-report hash quoted in publish)

Contract: packet records 0.61.0 (AGENTS.md, D36). Lane denies reading the contract folder; I did not try. Host evidence: I received no contract version line in process args/env. I do not echo the project file's line as host evidence.

Engine elapsed 152 s (G3_END 1794851504 minus G0_START 1794851352) vs expected ≈200 s (UNVERIFIED — my estimate, per packet: SG-323 167 s, SG-320 200 s; no new package). Phases: G0 38 s (1352→1390), G1 78 s (1390→1468; build 53 s 1390→1443, recreate-to-healthy 15 s 1443→1458), G2 21 s (1468→1489), G3 15 s (1489→1504). Runtime against RUN_BUDGET_S 2100 s: 152/2100, well inside. Publish before 1200 s bound: yes (report committed and pushed in same session, stamps quoted).

State reached: S1 (new container healthy, no rollback). S0 passed (app never touched before recreate). S1 healthy within 120 s with RestartCount 0, so no rollback. S2 not entered.

Ids before/after:
- Before: container a92d27bba1cb0429b26e7489bc5bd59fd1e5230e7b128975aed78a756a712a3d, image e2703987421ffb9c2dfb38f137efe4aa3ea8acde04e170dcf22410e205a33374, Cmd [uvicorn app.server:app --host 0.0.0.0 --port 8000], RestartCount 0, Status running, Health healthy. `storagegenie-backend:latest` and `storagegenie-backend:release-sg323` both resolved to e2703987 before build.
- After: container 9c7f8b81facea8c7dbe3250b5b9fa494e1a83316ee81ffa06b1d0ffb09588b32, image 0cf8bdc1825a2b7dbf121bc99931d057459ec6b5e498ef7c3e2190a3198beaa3, Cmd [uvicorn app.server:app --host 0.0.0.0 --port 8000], RestartCount 0, Status running, Health healthy. `storagegenie-backend:latest` and new tag `storagegenie-backend:release-sg327` both resolve to 0cf8bdc8 after. Recreate-to-healthy 15 s (1443→1458).

Census before/after (read-only byte copy, 29 tables; full counts in docs/worklogs/SG-327_census.txt):
- Before: alembic_version=1 assertion=40 asset=7 asset_evidence=20 asset_fts=7 asset_fts_config=1 asset_fts_data=9 asset_fts_docsize=7 asset_fts_idx=7 asset_location=1 asset_relation=1 audit_event=104 candidate=10 enrich_snapshot=4 evidence=27 guardrail_event=2 household=1 idempotency_key=11 job=11 job_step=72 location=1 observation=20 planning_suggestion=0 provider_call=39 reminder=4 review_task=9 saved_search=0 source_attribution=0 user=2
- After: identical (diff -u empty). `reminder` stayed 4, consistent with startup log `Daily reminder pass completed ... reminders_created=0`. No other table moved.

Constraints (one line each):
- No product byte changed: git diff for product is frontend-only as derived; backend/ (minus alembic) empty, deps empty, alembic empty; runtime diff shows static/ only.
- Written only docs/worklogs/SG-327* in git plus scratch path and one image tag: staged only by exact path docs/worklogs/SG-327*, no product/config/schema/migration/dependency/test byte.
- DATABASE read-only only: schema head and table census only, no write/migration/repair; opened live DB read-only on byte copy; WAL 0 bytes, SHM present, copy valid.
- Restart one recreate of backend only: one `docker compose build backend` rc 0, one `docker compose up -d --no-deps --force-recreate backend` rc 0; no other service touched.
- Provider none, no spend: no provider called, no key read/printed, no .env opened, $0.
- No /tmp for any command including curl -o: TMPDIR set to scratch, DOCKER_CONFIG to scratch, woff2 probe to scratch path; lane /tmp denied, never used.
- Never docker rmi/image prune/system prune/compose config without --images: only `config --images` used; no removal/move of tags.
- Never tag/untag/stop/restart app to test rights (PG-PR-01): no rights probe; only inspect --format, images, ps, config --images, run --rm --network none.
- A denial is STOP, never another route: no denial encountered except expected /proc argv denial (stated, not routed around) and absent release-sg327 tag before creation (expected, created once).
- Startup log read only by named lines: `grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`, never wider; no household id in output.
- No name/id/field value of owner in log/report: household id taken from DB into variable, never printed; only counts quoted.

## G0 — Socket-first and pre-state

- `date +%s` G0_START 1794851352 quoted.
- Literal block run with workdir /home/andrei/StorageGenie:
  - `mkdir -p output/SG-327-scratch/docker-config`, `export DOCKER_CONFIG="$PWD/output/SG-327-scratch/docker-config"`, `export TMPDIR="$PWD/output/SG-327-scratch"`, `export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-327/docker.sock"`, `echo "$DOCKER_HOST"` → `unix:///run/dispatch-storagegenie-SG-327/docker.sock`, `ls -l /run/dispatch-storagegenie-SG-327/` → `srw-rw---T 1 andrei ... docker.sock`, `docker version` prints Server section (Client 29.9.2, Server 29.9.2, API 1.56). Socket-first proven.
- `curl -s http://127.0.0.1:8003/v1/health` → `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state hypotheses from docs/releases/2026-11-14-sg323.md all hold: container `a92d27bb…` full `a92d27bba1cb0429b26e7489bc5bd59fd1e5230e7b128975aed78a756a712a3d`, image `e2703987…` full `sha256:e2703987421ffb9c2dfb38f137efe4aa3ea8acde04e170dcf22410e205a33374`, head `20261102_sg279_candidate_state` (DB `SELECT version_num FROM alembic_version` → that value; file `backend/alembic/versions/20261102_sg279_candidate_state.py` revision matches), RestartCount 0, Cmd `[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, Health healthy. `docker inspect` only with `--format` and named fields. No different running image; no STOP.
- `storagegenie-backend:release-sg323` resolves to running image id e2703987; `output/SG-327-scratch/rollback.override.yml` contains only `services.backend.image: storagegenie-backend:release-sg323`; `docker compose -f docker-compose.yml -f output/SG-327-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg323` for backend. Otherwise STOP would have fired; it did not.
- Read-only census: `cp data/db/storagegenie.db output/SG-327-scratch/census-g0.db` (live WAL 0 bytes, SHM 32768 bytes, DB 798720 bytes), `python3 output/SG-327-scratch/census.py` read-only `mode=ro`, counts only (see evidence). 29 tables as above.
- No rights probe on any real object.

A1 met.

## G1 — ONE build, ONE recreate

- `date +%s` G1_START 1794851390.
- One `docker compose build backend`, rc 0 (Built). Build log: frontend `COPY frontend/` fresh (not cached), `npm run build` → `dist/index.html 0.94 kB`, `dist/assets/index-MC93YmcZ.js 369.25 kB`, `dist/assets/index-BGbwuPTO.css 6.17 kB`, two woff2; backend `COPY backend/` fresh, hatchling/editables, `pip install -e .`, `COPY --from=frontend-build /ui/dist ./static`. Where latest points: before e2703987, after 0cf8bdc1825a2b7dbf121bc99931d057459ec6b5e498ef7c3e2190a3198beaa3.
- Served tree vs worktree: build used current worktree (frontend COPY not cached, backend COPY fresh); backend derived set empty so served backend equals worktree backend; frontend built from worktree sources. No cache-satisfied staleness.
- Runtime diff (whole served /app tree, old e2703987 vs new 0cf8bdc8 via authorised `docker run --rm --network none --entrypoint sh <image> -c 'cd /app && find . -type f -exec sha256sum {} +'` for both; old via same flags, read-only):
  - Derived expected backend set myself: `git diff --name-only 4bf0e09..HEAD -- backend/ ':!backend/alembic'` → empty (my expectation quoted as empty, matches). Then only static/ may differ.
  - Measured: old_files 4071 new_files 4071; OLD-ONLY `./static/assets/index-CVSFCg0Q.js 4238560f71403876961c5e116bbb3a515021148f186d130740b72cb29701bb2c`, NEW-ONLY `./static/assets/index-MC93YmcZ.js 328d7367a1c35ba603d04e5928ee4f2cafef531d959abdd101f12185d9bd0ba1`, CHANGED `./static/index.html old=0fc1308548ede60eebc69aaec8b48a17a1df4e3fa5a0bd9a4659dd8de75f7094 new=e5df1970cc80968fb67ff1044dd840e7b9f79573a644c7c6e1ffb841c8a4fe05`. backend_like_changed 0. Any measured backend file would have been STOP in S0; none found.
  - JS must change: yes, different names and hashes, sizes 369594 → 369451.
  - CSS may change: measured unchanged — same name `index-BGbwuPTO.css`, same hash `90d6285326accc47e61b3073b951bb4e04234b582e495d2d8ec83c9144d6b6c0`, same size 6172. Stated as unchanged.
  - woff2 must be byte-identical: yes, same names `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` hash `2ee17598a98d8a59e4df8152d015bec9ab8e4d5672cc0ab42bef806b568e3971` size 30092 and `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` hash `c4fcfea41f2c1cfeea9211fa43679845454a1d0e0d7e95e069c7e73c4ae302d2` size 11144, listed with sizes and hashes.
  - Full evidence in docs/worklogs/SG-327_runtime_diff.txt (changed paths with both hashes, not full-tree dumps).
- Alembic head unchanged before and after (`20261102_sg279_candidate_state` in DB and files); `git diff --name-only 4bf0e09..HEAD -- backend/alembic` empty; no migration command run.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0 at 1794851443→1445. Now S1. New container id, image id, Cmd, restart count, health as above; measured recreate-to-healthy 15 s (1443→1458, healthy within 120 s, RestartCount stayed 0).
- Tag what now serves: `storagegenie-backend:release-sg327` was absent → created via `docker tag storagegenie-backend:latest storagegenie-backend:release-sg327`, now resolves to 0cf8bdc8. Resolves-elsewhere case did not occur. Never removed/moved any tag; `release-sg323`, `release-sg320`, `release-sg317`, `release-sg314`, `release-sg310`, `release-sg309`, `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295` and `recovery-sg270` plus `prover` all stay.

A2 and A3 met.

## G2 — New behaviour in served artifact

- `date +%s` G2_START 1794851468.
- From served container's own files (docker run --rm --network none, no mounts/env/port):
  - Present strings (full counts in docs/worklogs/SG-327_strings.txt): OLD→NEW: `[Use by] 3→6`, `[Check this item] 0→1`, `[This may already be in your catalog] 0→1`, `[Add to catalog] 0→1`, `[Add an item] 1→2`, `[Cut out the item again] 0→1`, `[Make a styled photo] 0→1`, `[More actions for] 0→2`, `[No photo yet] 4→5`. Packet states each 0 before; measured 6 of 9 are 0→>=1, 3 were already present (`Use by`, `Add an item`, `No photo yet`) and rose. All 9 are present after (>=1). Quoted honestly; no string missing.
  - Absent strings: `[Capture — Manual Create] 1→0`, `[Candidate review] 1→0`, `[Possible duplicates or collisions] 1→0`, `[Re-isolate Asset] 1→0`, `[Generate Context Scene] 1→0`, `[Thumbnail unavailable] 1→0`, `[Dimensions/Specs] 1→0`. None remains; where-in-bundle question moot.
- `GET /assets/<woff2 the CSS names>` on 127.0.0.1:8003: CSS `index-BGbwuPTO.css` names both woff2; `GET /assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` → 200, content-type `application/octet-stream` (backlog W11 expects octet-stream; reported, not STOP), size 30092, sha matches served tree. Second woff2 also 200 octet-stream.
- Honest limit: No screen was viewed in a browser here; the screens were seen in SG-326 on a scratch build of the same code (docs/worklogs/SG-326_shots/); no candidate was decided on the live app here.

A4 met (with noted 0-before variance for three strings).

## G3 — App answers, nothing moved

- `date +%s` G3_START 1794851489, G3_END 1794851504.
- `/v1/health` six times, each quoted: all six `{"status":"ok","db":"ok","storage":"ok"}`.
- Shell routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/assets?household_id=<id>&category=food_beverages&limit=5` → 200, items_on_page 1 (response has no total; only first-page count quoted; household id from DB never printed). `GET /v1/plugins/expiry-tracker/status?household_id=<id>&category=food_beverages` → 200, keys `as_of,category,household_id,rows,summary,unresolved_rows`, rows_len 1, unresolved_len 0, summary total 1.
- Startup log read only by named lines: `docker logs --since 10m | grep -E 'Traceback|Application startup complete|Daily reminder pass'` → `INFO: Application startup complete.` and `INFO: app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-16 households_visited=1 reminders_created=0 errors=0`, no Traceback. Access log not read; no household id in output. Log clean.
- Census after vs G0: identical (diff empty); `reminder` 4→4, accounted for by `reminders_created=0`; any other table moving would have been reported at once — none moved.
- Container still RestartCount 0, healthy.

A5 met.

## Acceptance

- A1: Socket-first literal block proven; pre-state quoted (a92d27bb/e2703987/head/0); rollback override names release-sg323 and `config --images` confirms; no rights probe.
- A2: One build rc 0, one recreate rc 0; no migration (head unchanged, alembic diff empty); container/image ids before/after quoted.
- A3: Runtime diff equals derived set (derived lists and my empty expectations quoted); no backend file; JS changed (names/hashes/sizes); CSS stated unchanged (same name/hash/size 6172); woff2 unchanged with sizes/hashes; served tree equals worktree via fresh COPY + empty backend diff.
- A4: G2 strings quoted from served artifact (counts above); honest-limit sentence stated.
- A5: Health/routes 200 quoted; census compared identical; startup log clean (two named lines, no traceback).
- A6: `release-sg327` newly created on new image id; no tag removed/moved (all old tags listed present); state S1 (healthy, no rollback) named (S0 passed, S2 not entered).
- A7: No owner name/id/field value in logs/report (household id never printed, only counts); no key/.env read/printed; no provider; no browser; no DB write; scratch removed by exact path `rm -rf output/SG-327-scratch` (removal shown in publish step), never touched `output/` itself or `output/dispatch`.
- A8: PB-3 vacuity — a failure would look like: an extra file in runtime diff (checked: only 3 static paths), an unchanged JS hash (checked: hashes differ, names differ), a missing present-string (checked: all 9 >=1 in new), a remaining absent-string (checked: all 7 are 0 in new), a moved count (checked: census diff empty), a route not 200 (checked: all 200), a restart loop (checked: RestartCount 0, healthy), a traceback (checked: grep found none). All checked and quoted.
- A9: HEAD equals origin/automation after push — pre-report both 19469ad48b0f0c10218c089f4690d8fec44595ba; post-report hashes quoted in publish block below; phase seconds quoted above.
- A10: Last line is Verification below.

## Publish

Report commit carries trailer `Dispatch-ID: SG-327`. Staged only by exact path `docs/worklogs/SG-327*`. Tracked status clean (`git status --short --untracked-files=no` empty); untracked `output/` is engine + prior scratch, untouched except own scratch removal.

Next steps (step 1): Owner shelf trial on live release-sg327 (polish A+B served); report any I8/I11–I13 leftovers from SG-326 audit; then stage D planning. No further build needed unless trial finds a defect.

Verification: PASS
