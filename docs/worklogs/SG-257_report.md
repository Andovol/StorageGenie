# SG-257 — Close-deploy rider: served SG-256's row-11 polish live, proved the served bytes, recorded the release evidence

SG-257. model=opencode-go/deepseek-v4.1-flash effort=max, read from `/proc/2919458/cmdline` (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`). Served-model response metadata unavailable (no provider call made); no substitute claimed. dir=`/home/andrei/StorageGenie`; remote=`git@github.com:Andovol/StorageGenie.git`. BASE ref=`origin/automation`; resolved BASE COMMIT=`09d52891079697e7c6d6e989626c4f3d7d82bafb` (worktree HEAD at start, equal to `origin/automation`). WORK_HEAD=`d06e2300387e42f47532fc6b544d5d47272bd70b` (the docs-only evidence commit that precedes this report commit). Terminal class: **NO PRODUCT CHANGE** — one image build, one backend recreate, evidence files only. Target/actual spend: **$0 / $0.000000**; zero provider calls; no key value read, printed, hashed, stored or transmitted by these checks; no `.env` content inspected.

Contract chain: repo `AGENTS.md` records `0.53.0`; `/home/andrei/storagegenie-contract/VERSION` says `0.53.0`; host `CODER.md` line 3 verbatim: `**Contract version: 0.53.0** — **echo this line verbatim in your receipt.** It is the only proof that you`. The local contract clone is `fa76c7c` ("Contract payload 0.53.0") and still has no `contract-v0.53.0` tag (tags stop at `contract-v0.33.0`), the same local tag gap SG-252/SG-255/SG-256 reported; the payload version itself is `0.53.0`. Not a version mismatch.

## (a) Issues / deviations / surprises

I1. **G0 default docker path denied, as expected.** The first call (21:25:48Z) printed the Client block and no Server section, then `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`, rc=1. With `DOCKER_CONFIG=/tmp/opencode/sg257-docker` and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-257/docker.sock`, `docker version` printed the full **Server** block (29.9.2, API 1.56) and rc=0. `DOCKER_HOST` was unset in the dispatch shell, as SG-255/SG-256 found. CLI environment only; no daemon restart, no alternate socket, no sudo (`PB-2`, `PG-PR-03`).

I2. **The build was fully cache-satisfied because the image already existed.** All 23 build steps were `CACHED`; `storagegenie-backend:latest` is `sha256:b2c42abd942aa541034d3ef29b5b411919488af604f12fd6caa60788e3672c4b`, created `2026-10-28T21:13:11.68900601Z` — before this lane started at `21:23:58Z`, i.e. built during SG-256's session. Per G1 I did not assume currency: the built image's runtime tree equals the worktree (100/100 Python files, `diff` rc=0), and its static tree equals the post-serve bundle. The recreate served that proven image.

I3. **`index.html` changed, not byte-identical.** Vite content-hashes the JS filename and the index references it (`index-CWp6nYu6.js` -> `index-BRl7CaJb.js`). The packet allows the index to be identical but does not require it. The CSS is byte-identical. The JS changed as required.

I4. **The packet's "visible `Clear opened date` label" is the accessible label, not the visible text.** In the served bundle the string is `aria-label: "Clear opened date for ${x}"`; the visible button text is `children:"Clear"`. The component tests address the accessible name. Recorded as a `PB-1` phrase difference; the clear control is present and correctly named.

I5. **Live data has moved since SG-251, not during this slice.** `reminder=4` pre and post (SG-251 recorded 1 on 2026-10-24); `provider_call=39` pre and post. The startup daily pass logged `reminders_created=0 errors=0`, and the full 29-table census is identical before and after. Observation, not a finding; this rider wrote no row.

I6. **The error scan's only hit is the daily pass's `errors=0`.** Re-reading the startup log without that line leaves no `traceback`, `configuration error`, `exception`, `critical`, `failed` or `error` line. Same false positive SG-251 I8 recorded.

I7. **The build exported a manifest list** (`sha256:b2c42abd…`) with attestation; the container's `.Image` and the inspected image id are that same digest. No issue; recorded so the id fields are not read as a mismatch.

## (b) Actions

Changed paths: `docs/worklogs/SG-257_{g0,prestate,build,g1_build_verify,deploy,verify,g2,g3_served,g4_census,g5_live}.log`, `docs/worklogs/SG-257_report.md`, `docs/worklogs/SG-257_receipt.log`. **No product, config, schema, migration, dependency or test byte changed.** No migration command ran; no tag created.

The seven-file SG-256 delta is served as four runtime artifacts plus two test files that are not served: backend runtime `app/api/v1/plugins.py` and `app/plugins/expiry_tracker.py`; frontend sources `api/client.ts`, `api/types.ts`, `components/OpenedCountdownSection.tsx` compiled into the JS bundle; `backend/tests/test_sg240_opened_countdown.py` and `frontend/src/components/OpenedCountdownSection.test.tsx` are not runtime.

G0: lane socket `/run/dispatch-storagegenie-SG-257/docker.sock`; `DOCKER_CONFIG`/`DOCKER_HOST` named and proven (Server 29.9.2, API 1.56, rc=0). Pre-state: container `a831fbd0f8d2895d810efc4794f42166d194fa4e31c23403f02a8ff0cc19c2c1`, image `sha256:e8c7373577f9770bf486ae478e1a867b7ba41165aefa81d5f81d2b1d543d4ec3`, `Cmd ["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, RestartCount 0, running/healthy; head `20261023_sg233_reminder`; 29 tables; health start `http=200 {"status":"ok","db":"ok","storage":"ok"}`.

G1: one `docker compose build backend`, rc=0, 3 s, all steps CACHED; built image `sha256:b2c42abd942aa541034d3ef29b5b411919488af604f12fd6caa60788e3672c4b` (created `2026-10-28T21:13:11.68900601Z`), tree compared to worktree rc=0. One `docker compose up -d --no-deps --force-recreate backend`, rc=0, 1 s: new container `40bee778fa88dacb01236fff79d2ca0e5b3803b3cf0078cea76409c42e5049e2`, image `sha256:b2c42abd942aa541034d3ef29b5b411919488af604f12fd6caa60788e3672c4b`, same `Cmd`, Created `2026-10-28T21:26:44.631444958Z`, StartedAt `2026-10-28T21:26:45.567147289Z`, RestartCount 0, running/healthy by 21:27:06Z. No migration; alembic head `20261023_sg233_reminder` before and after. No other service touched (frontend container remained exited, unchanged).

G2: pre-serve-image-to-worktree runtime diff over `backend/app` is exactly two files, `api/v1/plugins.py` and `plugins/expiry_tracker.py`; set comparison against SG-256's `b3c18f3` backend files rc=0, extra=0, missing=0. Frontend: `index.html` `cec37cf5…` 944 B -> `14f82a64…` 944 B (changed); JS `index-CWp6nYu6.js` `fe7dff6e…` 326217 B -> `index-BRl7CaJb.js` `457010d8…` 327119 B (changed, cmp rc=1); CSS `index-C07VbG0m.css` `c3b58cda…` 4535 B (byte-identical, cmp rc=0). Served tree equals worktree: built image `/app/app` diff rc=0 and running container `/app/app` diff rc=0, 100/100 files.

G3: quoted from the served image's own files and served bundle in (c) A4. The served code and bundle are the proof.

G4: read-only census (`sqlite3` URI `file:/data/db/storagegenie.db?mode=ro`) of all 29 tables before and after: identical, `diff` rc=0; `provider_call=39` both; `reminder=4` both. Production sqlite main file unchanged: `424ac9d831daaae8c9d3e2a3684c7cad9724268f8688cff55c2e8e1f7673bc85`, 765952 B. No row written.

G5: six end health GETs and the final health GET all `http=200 {"status":"ok","db":"ok","storage":"ok"}`; shell routes `/`, `/expiry`, `/inbox`, `/planning` all http=200. Startup log: four uvicorn startup lines plus `Daily reminder pass completed as_of=2026-10-28 households_visited=1 reminders_created=0 errors=0`; no traceback, no configuration error.

External effects (CO-85): build completed (`storagegenie-backend:latest` -> `b2c42abd…`); recreate completed (`40bee778…` running/healthy); rows created **0**; counted row changes **0**; migration **0**; provider calls **0**; browser launches **0**; deployment count **1**; spend **$0.000000**.

Commits: evidence `d06e2300387e42f47532fc6b544d5d47272bd70b` ("SG-257: evidence (served SG-256 live; two-file runtime diff, bundle and census proof)"); the report commit follows and is pushed separately; receipt note added to the notes ref, which moves no product branch (CO-86).

Durations (box clock, UTC): lane start `2026-10-28T21:23:58Z` (epoch 1793222638); G0 socket proof `21:25:48Z`; pre-state `21:26:10–21:26:11Z`; build `21:26:20–21:26:23Z` (3 s); build-tree verification `21:26:37Z`; recreate `21:26:44–21:26:45Z` (1 s); post verify `21:27:06–21:27:12Z`; G3 `21:27:24–21:27:26Z`; census `21:27:52Z`; G5 `21:28:01–21:28:07Z`; G2 evidence `21:29:42–21:29:54Z`; report write end `21:31:29Z` (epoch 1793223089): **451 s** against the ≈400 s expectation (+51 s, +12.8%). Phases over 60 s: lane start -> G0 socket proof 110 s (session startup and packet/contract reading; no single command); report composition `21:29:54–21:31:29Z` 95 s. Fast remainder, each under 60 s: G0/pre-state 23 s, build 3 s, build-tree verification 14 s, recreate 1 s, post verify 27 s, G3 2 s, census 26 s, G5 6 s, G2 12 s. Retry count 0; test commands 0 (no product change); killed commands 0; no bound approached.

Highest-impact action: the single recreate to container `40bee778…` / image `b2c42abd…`, which made SG-256's edit/clear paths the served code and bundle.

## (c) Verification

A1 — **PASS.** The default endpoint was tried first and recorded, not routed around: Client 29.9.2 only, `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`, rc=1. Then `DOCKER_CONFIG=/tmp/opencode/sg257-docker` and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-257/docker.sock`; `docker version` printed `Server: Docker Engine - Community / Engine: Version 29.9.2 / API version: 1.56 (minimum version 1.40)`, rc=0 (`docs/worklogs/SG-257_g0.log`).

A2 — **PASS.** One build rc=0 (3 s, all steps CACHED; image `b2c42abd…` and tree check in I2/A3), one recreate rc=0 (1 s). Container `40bee778fa88dacb01236fff79d2ca0e5b3803b3cf0078cea76409c42e5049e2`, image `sha256:b2c42abd942aa541034d3ef29b5b411919488af604f12fd6caa60788e3672c4b`, `Cmd ["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, RestartCount 0, running/healthy. No migration; head `20261023_sg233_reminder` before and after. Health: start `http=200 {"status":"ok","db":"ok","storage":"ok"}` (21:26:10Z); six post-recreate: `health_1 {"status":"ok","db":"ok","storage":"ok"} http=200`, `health_2 {"status":"ok","db":"ok","storage":"ok"} http=200`, `health_3 {"status":"ok","db":"ok","storage":"ok"} http=200`, `health_4 {"status":"ok","db":"ok","storage":"ok"} http=200`, `health_5 {"status":"ok","db":"ok","storage":"ok"} http=200`, `health_6 {"status":"ok","db":"ok","storage":"ok"} http=200` (21:27:06–21:27:12Z); six end GETs `health_end_1..6 {"status":"ok","db":"ok","storage":"ok"} http=200` and final `http=200 {"status":"ok","db":"ok","storage":"ok"}` (21:28:01–21:28:07Z). Shell routes `/` 200, `/expiry` 200, `/inbox` 200, `/planning` 200. Logs: `docs/worklogs/SG-257_prestate.log`, `SG-257_deploy.log`, `SG-257_verify.log`, `SG-257_g5_live.log`.

A3 — **PASS.** The runtime diff between pre-serve image `e8c73735…` and the worktree over `backend/app` is exactly `api/v1/plugins.py` and `plugins/expiry_tracker.py`; set comparison to SG-256's backend files rc=0, extra=0, missing=0. JS bundle changed: `fe7dff6e58dd934ec14f693d40166aee5117453c13cb8caee45f371d4a944b99`, 326217 B -> `457010d8da9ba8863a7a6459817206f40f858f2bff756aff4da8ef83387c6356`, 327119 B, cmp rc=1. `index.html` changed (`cec37cf5…` 944 B -> `14f82a64…` 944 B, because it references the new content-hashed JS); CSS byte-identical (`c3b58cda…`, 4535 B, cmp rc=0). The served tree equals the worktree after the build: built image and running container `/app/app` both 100/100 Python files, `diff` rc=0. Logs: `docs/worklogs/SG-257_g2.log`, `SG-257_g1_build_verify.log`, `SG-257_verify.log`.

A4 — **PASS, from the served image's own files** (`docs/worklogs/SG-257_g3_served.log`; container `40bee778…`, image `b2c42abd…`, tree extracted by `docker cp`, bundle fetched from the served app over HTTP):

1. Served `app/api/v1/plugins.py`: `242:@router.post("/assets/{asset_id}/opened/clear")`, `243:def clear_opened_date(`, `253:        assertion = expiry_tracker.clear_opened_date(db, asset)`.
2. Served `app/plugins/expiry_tracker.py`: `531:def clear_opened_date(db: Session, asset: Asset) -> Assertion | None:` and the return block `552:    return _write_assertion(` / `553:        db, asset, OPENED_DATE_FIELD, None, "user", "accepted", None` / `554:    )`; the no-op path is `551:        return None`.
3. Served frontend JS (`index-BRl7CaJb.js`): `/opened/clear` hit count 1 — `function Dx(e,t){return ne(\`/v1/plugins/expiry-tracker/assets/${e}/opened/clear\`,{},{household_id:t})}`; `Clear opened date` hit count 1 — `"aria-label":\`Clear opened date for ${x}\`` with visible `children:"Clear"` (I4).

**Honest limit:** the live clear/edit write was **not** exercised — it would write the owner's data; the served code and bundle are the proof, and the first real clear awaits the owner's use.

A5 — **PASS.** Pre and post census both have 29 tables and 31 compared lines; `diff` rc=0. `provider_call=39` before and after; `assertion=40`, `asset=7`, `asset_evidence=20`, `audit_event=104`, `candidate=10`, `enrich_snapshot=4`, `evidence=27`, `household=1`, `idempotency_key=11`, `job=11`, `job_step=72`, `observation=20`, `reminder=4`, `review_task=9`, `user=2`; every other table unchanged. Log: `docs/worklogs/SG-257_g4_census.log`.

A6 — **PASS.** No provider call, no browser, no production write, no migration, no other service touched; spend $0.000000. No key value was read, printed, hashed, stored or transmitted by these checks; no `.env` content was inspected (`/app/.env` is absent from the image). The rider commits only `docs/worklogs/SG-257*`. No tag created.

A7 — **PB-3 vacuity: each check could have failed.** The runtime diff could have carried an extra file (e.g. `server.py`, a test, or a `.pyc`) or missed one of the two; it carried exactly the two, with extra=0 and missing=0. The JS hash could have stayed `fe7dff6e…` at 326217 B; it moved to `457010d8…` at 327119 B, cmp rc=1. The served code could have lacked the clear route or the call; the route is at line 242, the call at 253, and the bundle hits for `/opened/clear` and `Clear opened date` are each 1. The startup could have shown a traceback or a pydantic configuration error; it showed neither, only `errors=0`. `provider_call` could have moved 39 -> 40; it stayed 39 and all 29 tables are identical. A health or shell route could have been non-200; every health GET (start, six post, six end, final) and all four shell routes answered 200. None of these failure shapes is the observed result.

A8 — **PASS.** Last line.

INTENT: no behaviour-changing code item (this slice changes no product byte); the recreate serves SG-256's approved tree at `09d5289`; the check expects exactly the two SG-256 backend runtime files changed and the JS bundle changed; the approved D4 rider packet says exactly that.

TWINS: none; this is a release rider, not a defect fix (CO-17).

Skipped as unnecessary (CO-103): backend and frontend suites — no product byte changed and SG-256 was audited 96 on those gates; lint/type checks — same; browser screenshot — served bytes and live health are the proof; provider call — none in scope, $0; database backup — no schema change and no write; release tag — the packet forbids it; the tag and release record are the Architect's after audit.

UNCLEAR FIRST READ: the packet's "visible `Clear opened date` label" resolved to the served accessible label (`aria-label`), with visible text `Clear` (I4). DURING EXECUTION: why the cache-satisfied image predated this lane — it was built at 21:13:11Z during SG-256's session; content was proven equal to the worktree, so no action followed (I2). REMAINING: the root-owned `~/.docker` is still pending in the engine arc, so `DOCKER_CONFIG` and an explicit `DOCKER_HOST` remain required; no open product item.

Verification: PASS
