# SG-335 report — deploy rider: serve *Add item* in the non-catalog nav (SG-334), prove the served bytes, keep the way back

Slice SG-335. Model and effort are not visible in my process arguments, so I state neither and infer nothing. Working directory `/home/andrei/StorageGenie`. Remote `origin` = `git@github.com:Andovol/StorageGenie`. BASE ref `origin/automation`, resolved BASE commit `e7468dc626ffb7b6980e4eb7c633c92ba11ea5c3` (message `D42 adopted: contract 0.63.0 (Muse-only kept, second opinion Sol 6.2); SG-334 rated 96; SG-335 rider packet`; verified equal to `origin/automation` before starting). WORK_HEAD = the report commit below (quoted with the push output).

Contract: the packet states the contract as recorded `0.63.0` (`AGENTS.md`, D42). This lane denies reading the contract folder, so I never tried; the denial is expected and is not a STOP. I received no contract version line for this run, so I echo no version line.

## Time

- Start stamp 1794952801. Publish bound (1200 s) = 1794954001 — publishing well before it. Elapsed at publish ≈ N s (start 1794952801 → push; quoted with the push output), inside RUN_BUDGET_S 2100, against the ≈220 s estimate (`UNVERIFIED — my estimate`: SG-332 233 s, SG-329 181 s).
- G0 1794952801→1794952853 (≈52 s): socket block, health, pre-state, rollback override, read-only census, old-image hashes and string counts.
- G1 1794952853→1794952956 (≈103 s): one build rc 0, runtime diff, one recreate rc 0, healthy, tag `release-sg335`.
- G2 1794952966→1794953006 (≈40 s): served string counts, woff2 probe, local vite build of HEAD and equality check.
- G3 1794953006→1794953015 (≈9 s): health ×6, routes, two API endpoints, startup log, census after, served-vs-worktree check.
- Report + publish after.

## G0 — socket first, and the pre-state

The literal block ran first (stamp 1794952801): `mkdir -p output/SG-335-scratch/docker-config`, the three exports (`DOCKER_CONFIG`, `TMPDIR`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-335/docker.sock`), `echo $DOCKER_HOST` printing the socket path, `ls -l /run/dispatch-storagegenie-SG-335/` showing `docker.sock` (`srw-rw---T`), and `docker version` printing a **Server** section (29.9.2). No `/tmp` used by any command, including `curl -o`.

- `/v1/health` at start: `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state, hypotheses from `docs/releases/2026-11-16-sg332.md` all confirmed (`docker inspect --format` with named fields only): container `94f432b0edaf…` (expected `94f432b0…`), image `0cd2437de56e…` (expected `0cd2437d…`), `Cmd=[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, `RestartCount=0` (expected 0), state running. Alembic head in the database: `20261102_sg279_candidate_state` (expected). No other running image to account for.
- `storagegenie-backend:release-sg332` resolves to the running image id `0cd2437de56e`, and `docker compose -f docker-compose.yml -f output/SG-335-scratch/rollback.override.yml config --images` names `storagegenie-backend:release-sg332` for `backend`. The override writes only `services.backend.image: storagegenie-backend:release-sg332`.
- Read-only census of all 29 tables (sqlite `mode=ro`, counts only): see `SG-335_census.txt` (BEFORE section). No write, no migration, no data repair.
- No rights probe on any real object: nothing was tagged, untagged, stopped or restarted to test rights.

## G1 — ONE build, ONE recreate

- One `docker compose build backend`, rc 0 (stamp 1794952853). `storagegenie-backend:latest` pointed at `0cd2437de56e` before and `a1e3fbf196ce` after. Not cache-satisfied (new image id); no assumption made.
- Derived backend set (`git diff --name-only e5467749..HEAD -- backend/ ':!backend/alembic'`): empty — the packet's expectation, quoted: **empty**. Alembic diff (`... -- backend/alembic`): empty. The measured runtime diff over the whole served `/app` tree (new image's tree hashed via the authorised `docker run --rm --network none --entrypoint sh … find … sha256sum` command) is exactly: old JS removed (`index-DlqlGk8g.js` `11e4ee1b…`, 372812 B), new JS added (`index-DIkDaL1_.js` `8e7afeb6…`, 372821 B), `index.html` changed (`f5bf7b1f…` → `7173830a…`). No backend file — no STOP in S0. Full changed paths with both hashes: `SG-335_runtime_diff.txt`. The CSS (`index-e_BzCe-6.css`, `d0a1bbde…`, 7307 B) and both Instrument Sans `.woff2` files (same names, `c4fcfe…` 11144 B / `2ee175…` 30092 B) are byte-identical, measured not assumed. Served backend `.py` (217 files) equals worktree `backend/` `.py` (217 files): sorted hash sequences identical, zero mismatches.
- Alembic head unchanged before and after (`20261102_sg279_candidate_state`); no migration command run.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0 (1794952929→1794952931). **Now S1.** New container `76faf17879d3…`, image `a1e3fbf196ce`, `Cmd=[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, `RestartCount=0`, docker status `healthy`, endpoint 200 on the first check (1794952935, ≈4 s recreate-to-healthy).
- Tagged what now serves: `storagegenie-backend:release-sg335` on `a1e3fbf196ce` (absent before → created; resolves to the same id; nothing else touched). No tag removed or moved: `release-sg332` still `0cd2437d…`, and `release-sg329/327/323/320/317/314/310/309/303/299/296/295`, `recovery-sg270` unchanged. No git tag created.

## G2 — the new behaviour is in the served artifact

From the served container's own files: the served JS differs from the old one (`11e4ee1b…` → `8e7afeb6…`), and its name and hash equal a local `vite build` of `HEAD` into scratch (built with the image's own `VITE_API_BASE=https://storagegenie.dynv6.net` from the Dockerfile): `index-DIkDaL1_.js` `8e7afeb6…`, CSS `d0a1bbde…`, both `.woff2` and `index.html` identical (see `SG-335_strings.txt`).

Counts in the served JS — before → after: *Add item* 2 → **4** (at least 2 after: the catalog header and the shared nav); *Your things* 1 → **1** (at least 1); *Use by, soonest first* 1 → **1** (at least 1); *Import Asset* 2 → **0** (0 after; before count quoted). `GET /assets/<the woff2 the CSS names>` on `127.0.0.1:8003` returns **200**, content type `application/octet-stream` (W11, not a STOP), 30092 bytes, hash equals the image's file.

Honest limit: no screen is viewed in a browser here; the change's tests are SG-334's; no candidate is decided on the live app here.

## G3 — the app answers, and nothing moved

- `/v1/health` six times, each `{"status":"ok","db":"ok","storage":"ok"}` (see `SG-335_served.txt`).
- Shell routes `/`, `/pantry`, `/expiry`, `/inbox`, `/planning`, `/capture` all return 200.
- `GET /v1/assets?household_id=<redacted>&category=food_beverages&limit=5` → 200, `items` on the first page: 1 (response keys `items`, `next_cursor`; no `total`). `GET /v1/plugins/expiry-tracker/status?household_id=<redacted>&category=food_beverages` → 200. Household id taken from the database and never printed.
- Startup log, read by named lines only (`grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`): `Application startup complete.` present, no `Traceback`, and the Daily reminder pass line (`reminders_created=0`) accounts for the `reminder` count. No household id, query string, or owner value in my output.
- Census after compared with G0: IDENTICAL in every table (see `SG-335_census.txt`); `reminder` did not rise, as the line accounts for.

## Constraints (one line each)

- PB-1: every premise derived myself (`git diff` backend/alembic sets, image ids, counts) and quoted with evidence; the packet's own expectations are labelled as such.
- PB-2: no denial occurred; the contract-folder denial was expected per the packet and never attempted; a denial would have been a STOP, never a workaround.
- PB-3: vacuity checked — an extra file in the runtime diff, an unchanged JS hash, *Import Asset* still counted, a moved census count, a non-200 route, a restart loop, or a traceback would each have failed this slice; I checked all seven (diff is 3 static changes only; JS hash changed; *Import Asset* 0; census identical; all routes 200; restart count 0 with healthy; no traceback).
- PB-4: model/effort line above states only what my process arguments show (nothing); no name, id, or field value of the owner in any log or report.
- PB-5: no provider called, no key read or printed, no `.env` opened, no spend; database read-only; no browser.
- PB-6: scratch stayed in `output/SG-335-scratch/`, removed by exact path at the end (removal shown below); `output/` itself and `output/dispatch` untouched; staging only `docs/worklogs/SG-335*`.

## Changed files

`docs/worklogs/SG-335_report.md`, `SG-335_runtime_diff.txt`, `SG-335_census.txt`, `SG-335_strings.txt`, `SG-335_served.txt` (new). Scratch `output/SG-335-scratch/` removed by exact path (shown below). One docker image tag `storagegenie-backend:release-sg335`; the backend container recreated once (S1, no rollback needed).

## Criterion lines

- A1 — Socket-first proven with the literal block (stamp 1794952801, Server 29.9.2, socket `srw-rw---T`); pre-state quoted (container `94f432b0…`, image `0cd2437d…`, head `20261102_sg279_candidate_state`, restart 0); rollback override names `release-sg332`; no rights probe.
- A2 — One build, one recreate, rc 0 both; no migration (head unchanged, alembic diff empty); container ids `94f432b0edaf…` → `76faf17879d3…`, image ids `0cd2437de56e` → `a1e3fbf196ce` before and after.
- A3 — Runtime diff equals the derived set (derived list empty and packet expectation empty, both quoted); no backend file; JS changed and equals a local build of HEAD; CSS and `.woff2` with sizes and hashes; served backend `.py` equals worktree.
- A4 — G2's strings quoted from the served artifact (4/1/1/0); the honest-limit sentence stated.
- A5 — Health and routes 200; census compared (identical); startup log clean (no traceback).
- A6 — `release-sg335` tag created on the new image id (absent before); no tag removed or moved; state reached: **S1** (no S0 stop, no rollback).
- A7 — No owner name/id/field, no key/`.env`, no provider, no browser, no database write; scratch removed by exact path (shown below).
- A8 — PB-3 vacuity: the seven failure shapes named under Constraints and each checked.
- A9 — `HEAD` equals `origin/automation` after the push, both hashes quoted (with the push output); phase seconds from the stamps above.
- A10 — Last line below.

Verification: PASS
