# SG-341 report — deploy rider: serve redesign C (item page one row per pack, grouped catalog cards; SG-336, SG-337, SG-338, SG-339), prove the served bytes, keep the way back

Slice SG-341. Model and effort are not visible in my process arguments, so I state neither and infer nothing. Working directory `/home/andrei/StorageGenie`. Remote `origin` = `git@github.com:Andovol/StorageGenie`. BASE ref `origin/automation`, resolved BASE commit `9898b0d448a51461fb7589562c1b4e21fdfa2adf` (message `SG-340 rated 94; SG-341 rider packet (serve redesign C)`; verified equal to `origin/automation` before starting). WORK_HEAD = the report commit below (quoted with the push output).

Contract: the packet states the contract as recorded `0.63.0` (`AGENTS.md`, D42). This lane denies reading the contract folder, so I never tried; the denial is expected and is not a STOP. I received no contract version line for this run, so I echo no version line.

## Time

- Start stamp 1794995785. Publish bound (1200 s) = 1794996985 — publishing well before it. Elapsed at publish ≈ N s (start 1794995785 → push; quoted with the push output), inside RUN_BUDGET_S 2100, against the ≈220 s estimate (`UNVERIFIED — my estimate`: SG-335 ≈214 s, SG-332 233 s).
- G0 1794995785→1794995843 (≈58 s): socket block, health, pre-state, rollback override, read-only census, old-image hashes and string counts.
- G1 1794995843→1794995949 (≈106 s): one build rc 0, runtime diff, one recreate rc 0, healthy, tag `release-sg341`.
- G2 1794995949→1794996003 (≈54 s): served string counts, woff2 probe, local vite build of HEAD and equality check.
- G3 1794996003→1794996007 (≈4 s): health ×6, routes, two API endpoints, startup log, census after, served-vs-worktree check.
- Report + publish after.

## G0 — socket first, and the pre-state

The literal block ran first (stamp 1794995785): `mkdir -p output/SG-341-scratch/docker-config`, the three exports (`DOCKER_CONFIG`, `TMPDIR`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-341/docker.sock`), `echo $DOCKER_HOST` printing the socket path, `ls -l /run/dispatch-storagegenie-SG-341/` showing `docker.sock` (`srw-rw---T`), and `docker version` printing a **Server** section (29.9.2). No `/tmp` used by any command, including `curl -o`. Scratch stayed in `output/SG-341-scratch/`; `output/` itself and `output/dispatch` never touched.

- `/v1/health` at start: `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state, hypotheses from `docs/releases/2026-11-18-sg335.md` all confirmed (`docker inspect --format` with named fields only): container `76faf17879d3…` (expected `76faf178…`), image `a1e3fbf196ce…` (expected `a1e3fbf1…`), `Cmd=[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, `RestartCount=0` (expected 0), state running. Alembic head in the database: `20261102_sg279_candidate_state` (expected). No other running image to account for.
- `storagegenie-backend:release-sg335` resolves to the running image id `sha256:a1e3fbf196ce44adb189449f6e9f617be37d2f90ce6b3ca29aae8dcf5887ca47`, and `docker compose -f docker-compose.yml -f output/SG-341-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg335` for `backend`. The override writes only `services.backend.image: storagegenie-backend:release-sg335`.
- Read-only census of all 29 tables (sqlite `mode=ro`, counts only): see `SG-341_census.txt` (BEFORE section). No write, no migration, no data repair.
- No rights probe on any real object: nothing was tagged, untagged, stopped or restarted to test rights.

## G1 — ONE build, ONE recreate

- One `docker compose build backend`, rc 0 (stamp 1794995843). `storagegenie-backend:latest` pointed at `a1e3fbf196ce` before and `85728f2ea203` after. Not cache-satisfied (new image id); no assumption made.
- Derived backend set (`git diff --name-only a5b00728..HEAD -- backend/ ':!backend/alembic'`): empty — the packet's expectation, quoted: **empty**. Alembic diff (`... -- backend/alembic`): empty. The measured runtime diff over the whole served `/app` tree (new image's tree hashed via the authorised `docker run --rm --network none --entrypoint sh … find … sha256sum` command) is exactly: old JS removed (`index-DIkDaL1_.js` `8e7afeb6…`, 372821 B), new JS added (`index-lfQJ5nAV.js` `f70939f7…`, 387775 B), `index.html` changed (`7173830a…` → `32c59941…`, 944 B both). No backend file — no STOP in S0. Full changed paths with both hashes: `SG-341_runtime_diff.txt`. The CSS (`index-e_BzCe-6.css`, `d0a1bbde…`, 7307 B, unchanged) and both Instrument Sans `.woff2` files (same names, `c4fcfe…` 11144 B / `2ee175…` 30092 B) are byte-identical, measured not assumed. Served backend `.py` (217 files) equals worktree `backend/` `.py` (217 files, venv/__pycache__ excluded both sides): zero path mismatches, zero hash mismatches.
- Alembic head unchanged before and after (`20261102_sg279_candidate_state`); no migration command run.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0 (1794995925). **Now S1.** New container `c0f5faebd4e3…`, image `85728f2ea203`, `Cmd=[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, `RestartCount=0`, endpoint 200 on the first check after recreate (1794995929, ≈4 s recreate-to-healthy, within 120 s).
- Tagged what now serves: `storagegenie-backend:release-sg341` on `85728f2ea203` (absent before → created; resolves to the same id as `latest`; nothing else touched). No tag removed or moved: `release-sg335` still `a1e3fbf1…`, and `release-sg332/329/327/323/320/317/314/310/309/303/299/296/295`, `recovery-sg270` unchanged. No git tag created.

## G2 — the new behaviour is in the served artifact

From the served container's own files (`docker exec storagegenie-backend-1`): the served JS differs from the old one (`8e7afeb6…` → `f70939f7…`), and its name and hash equal a local `vite build` of `HEAD` into scratch (built with the image's own `VITE_API_BASE=https://storagegenie.dynv6.net` from the Dockerfile): `index-lfQJ5nAV.js` `f70939f7…`, CSS `d0a1bbde…`, both `.woff2` and `index.html` identical (see `SG-341_strings.txt`).

Counts in the served JS — before → after: *More about this item* 0 → **1** (at least 1 after); *Add another pack* 1 → **2** (at least 1); *Your things* 1 → **3** (at least 1); *Add item* 4 → **4** (at least 1); *Use by, soonest first* 1 → **1** (at least 1); the packs-line template (`{item.packCount} packs`, `frontend/src/components/catalog/ProductCard.tsx:235`, counted as ` packs`) 0 → **4** (at least 1); *Import Asset* **0** before and after (0 after; before count quoted). `GET /assets/<the woff2 the CSS names>` on `127.0.0.1:8003` returns **200**, content type `application/octet-stream` (W11, not a STOP), 30092 bytes, hash equals the image's file.

Honest limit: no screen is viewed in a browser here; the screens were photographed on a scratch app by SG-340; the change's tests are SG-336–SG-339's; no item on the live app is changed here.

## G3 — the app answers, and nothing moved

- `/v1/health` six times, each `{"status":"ok","db":"ok","storage":"ok"}` (see `SG-341_served.txt`).
- Shell routes `/`, `/pantry`, `/expiry`, `/inbox`, `/planning`, `/capture` all return 200.
- `GET /v1/assets?household_id=<redacted>&category=food_beverages&limit=5` → 200, `items` on the first page: 1 (response keys `items`, `next_cursor`; no `total`). `GET /v1/plugins/expiry-tracker/status?household_id=<redacted>&category=food_beverages` → 200. Household id taken from the database and never printed.
- Startup log, read by named lines only (`grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`): `Application startup complete.` present, no `Traceback`, and the Daily reminder pass line (`reminders_created=0`) accounts for the `reminder` count. No household id, query string, or owner value in my output.
- Census after compared with G0: IDENTICAL in every table (see `SG-341_census.txt`); `reminder` did not rise, as the line accounts for.

## Constraints (one line each)

- PB-1: every premise derived myself (`git diff` backend/alembic sets, image ids, counts) and quoted with evidence; the packet's own expectations are labelled as such.
- PB-2: no denial occurred; the contract-folder denial was expected per the packet and never attempted; a denial would have been a STOP, never a workaround.
- PB-3: vacuity checked — an extra file in the runtime diff, an unchanged JS hash, *More about this item* or the packs line missing, a moved count, a route not 200, a restart loop, or a traceback would each have failed this slice; I checked all seven (diff is 3 static changes only; JS hash changed; *More about this item* 1 and packs 4; census identical; all routes 200; restart count 0 with endpoint healthy; no traceback).
- PB-4: model/effort line above states only what my process arguments show (nothing); no name, id, or field value of the owner in any log or report.
- PB-5: no provider called, no key read or printed, no `.env` opened, no spend; database read-only; no browser.
- PB-6: scratch stayed in `output/SG-341-scratch/`, removed by exact path at the end (removal shown below); `output/` itself and `output/dispatch` untouched; staging only `docs/worklogs/SG-341*`.

## Changed files

`docs/worklogs/SG-341_report.md`, `SG-341_runtime_diff.txt`, `SG-341_census.txt`, `SG-341_strings.txt`, `SG-341_served.txt` (new). Scratch `output/SG-341-scratch/` removed by exact path (shown below). One docker image tag `storagegenie-backend:release-sg341`; the backend container recreated once (S1, no rollback needed).

## Criterion lines

- A1 — Socket-first proven with the literal block (stamp 1794995785, Server 29.9.2, socket `srw-rw---T`); pre-state quoted (container `76faf178…`, image `a1e3fbf1…`, head `20261102_sg279_candidate_state`, restart 0); rollback override names `release-sg335`; no rights probe.
- A2 — One build, one recreate, rc 0 both; no migration (head unchanged, alembic diff empty); container ids `76faf17879d3…` → `c0f5faebd4e3…`, image ids `a1e3fbf196ce` → `85728f2ea203` before and after.
- A3 — Runtime diff equals the derived set (derived list empty and packet expectation empty, both quoted); no backend file; JS changed and equals a local build of HEAD; CSS and `.woff2` with sizes and hashes; served tree equals worktree.
- A4 — G2's strings quoted from the served artifact (1/2/3/4/1/4/0); the honest-limit sentence stated.
- A5 — Health and routes 200; census compared (identical); startup log clean (no traceback).
- A6 — `release-sg341` tag created on the new image id (absent before); no tag removed or moved; state reached: **S1** (no S0 stop, no rollback).
- A7 — No owner name/id/field, no key/`.env`, no provider, no browser, no database write; scratch removed by exact path (shown below).
- A8 — PB-3 vacuity: the seven failure shapes named under Constraints and each checked.
- A9 — `HEAD` equals `origin/automation` after the push, both hashes quoted (with the push output); phase seconds from the stamps above.
- A10 — Last line below.

Verification: PASS
