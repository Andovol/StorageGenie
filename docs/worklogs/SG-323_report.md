# SG-323 report — deploy rider: SG-304 + SG-322 served

Slice: SG-323 | Model: opencode-go/claude-haiku-5-5 (from the run environment; no effort argument was supplied, so effort is not stated) | Working directory: /home/andrei/StorageGenie | Remote: origin git@github.com:Andovol/StorageGenie.git | BASE ref: origin/automation, resolved fba17fb | WORK_HEAD (the commit the image was built from): fba17fb

Contract version line: none received. My context carries only the global and project AGENTS.md; I did not read the contract folder (denied, not attempted). The project file's line is not echoed here, per the packet.

## Outcome

Served: release-sg323 = image e2703987, container a92d27bba1cb, healthy, restart count 0. No rollback was needed.
State reached: **S1** (new container started, healthy within 10 s, served; no S1 rollback).

## Ids before and after

| | Before | After |
|---|---|---|
| Container | 07aa3de8b980 (healthy, restart 0) | a92d27bba1cb (healthy, restart 0) |
| Image | 10d6064f670e (`release-sg320`, `latest`) | e2703987421f (`latest`, `release-sg323`) |
| Cmd | uvicorn app.server:app --host 0.0.0.0 --port 8000 | same |
| Alembic head | 20261102_sg279_candidate_state | 20261102_sg279_candidate_state |

Tags: `release-sg323` created on e2703987 (it was absent). Every other tag is untouched, including `release-sg320`, `release-sg317`, `release-sg314`, `release-sg310`, `release-sg309`, `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295`, `recovery-sg270`. `storagegenie-backend:prover` (created 2026-11-14, image 6156e5f2) was not touched; it is not running.

## Census (read-only, counts only)

Before and after: all 29 tables identical; `reminder` stayed at 4, `audit_event` at 104, and `provider_call` at 39. Table: `docs/worklogs/SG-323_census.txt`. Opened with `mode=ro` from inside the running container; no write, no migration.

## Build and runtime diff

- `docker compose build backend`, rc 0. Every layer reported CACHED, so the tree was compared rather than assumed. `latest` moved from 10d6064f to e2703987.
- Runtime diff (full sha256 over /app, old vs new): `docs/worklogs/SG-323_runtime_diff.txt`.
- Derived set (`git diff --name-only 7a24601..HEAD -- backend/ ':!backend/alembic'`): backend/app/api/v1/candidates.py, backend/app/services/candidates.py. The image ships tests/, so the two new test files also count. Measured changes: exactly those two app files, both new test files (added), `static/index.html`, and the JS bundle (old index-_brNCbOJ.js replaced by index-CVSFCg0Q.js, 365842 -> 369594 B). Matches the expectation.
- CSS index-BGbwuPTO.css (6172 B) and both Instrument Sans .woff2 (11144 B, 30092 B) are byte-identical.
- Removed: 107 runtime `__pycache__` .pyc files from the old container (not source; .dockerignore excludes them). The packet's "removed" count of 108 is those plus the old JS bundle.
- Served app/ (117 files) matches the worktree backend/app hash for hash. Alembic and venv/ unchanged.
- Dependencies, lockfiles and migrations: no git diff (checked empty).

## G2 — the new behaviour in the served artifact

Served JS, before -> after: "You already have" 0 -> 2; "Add another pack" 0 -> 1; "This photo matches" 0 -> 2; "It's another pack" 0 -> 1; "It's the same pack" 0 -> 1; "Decide later" 0 -> 1; "Exact duplicate of asset" 1 -> 0. Served app/services/candidates.py: DECIDED_CANDIDATE_STATES 0 -> 3.
`GET /assets/instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` on 127.0.0.1:8003: 200, content type `application/octet-stream` (11144 B). This matches the W11 expectation; it is not a stop.

Honest limit: no screen was viewed in a browser here, and no candidate was decided on the live app. The screens were seen in SG-321r1 on a scratch build of the same code (docs/worklogs/SG-304_shots_r1/).

## G3 — the app answers

- `/v1/health` six times: `{"status":"ok","db":"ok","storage":"ok"}` each time.
- Shell routes: / 200, /pantry 200, /expiry 200, /inbox 200, /planning 200.
- `GET /v1/assets?household_id=…&category=food_beverages&limit=5`: 200, 1 item on the first page. `GET /v1/plugins/expiry-tracker/status?…`: 200. The household id was read from the database inside the container and never printed.
- Startup log, named lines only: `Application startup complete.` present; `Daily reminder pass completed as_of=2026-11-14 households_visited=1 reminders_created=0 errors=0`; no Traceback.

Mistake, recorded: my first G3 pass used the old container id 07aa3de8b980 for the household lookup, census and alembic reads, which no longer existed after the recreate. Those reads returned errors, and the assets probe in that pass returned an empty result, which I discarded. The redo against a92d27bba1cb produced the figures above. Health, routes and the log were read through the port and the container name and were not affected. No write happened in either pass.

## Constraints

- Socket first: the literal DOCKER_CONFIG/TMPDIR/DOCKER_HOST block; `docker version` printed a Server section (29.9.2).
- Pre-state: container, image and restart count as hypothesised; no unaccounted running image.
- Rollback override: wrote output/SG-323-scratch/rollback.override.yml naming storagegenie-backend:release-sg320; `docker compose ... config --images` resolved it to release-sg320. Not used.
- No rights probe on any real object. No tag removed or moved. No `docker rmi`, `image prune`, `system prune`. No `docker compose config` without `--images`.
- No provider call, no key or `.env` opened, no spend, no browser, no database write, no migration, no data repair, no stored photo or file touched.
- Logs and report carry no household id, name or field value of the owner's.
- Scratch removed by exact path: `rm -rf output/SG-323-scratch` (after the evidence was written). `output/dispatch` untouched.

## Phase times (from `date +%s` stamps)

| Phase | Stamps | Seconds |
|---|---|---|
| G0 socket, pre-state, rollback check, census | 1794687797 -> 1794687812 | 15 |
| G1 build (cached) | 1794687818 -> 1794687821 | 3 |
| G1 runtime hashing (old + new) | 1794687821 -> 1794687835 | 14 |
| G1 analysis and derivation | 1794687835 -> 1794687868 | 33 |
| Pre-recreate string counts | 1794687868 -> 1794687869 | 1 |
| Recreate -> healthy | 1794687873 -> 1794687886 | 13 (recreate rc 0 in 3 s; healthy in 10 s) |
| Tag and G2 after-counts, woff2 | 1794687898 -> 1794687899 | 1 |
| G3 first pass (discarded parts, see above) | 1794687905 -> 1794687911 | 6 |
| G3 redo, census, alembic | 1794687918 -> 1794687918 | under 1 |
| Evidence, census file, scratch removal | 1794687935 -> 1794687964 | 29 |

Engine elapsed at evidence removal: 167 s, against the ≈150 s estimate and the 2100 s run budget. Publish is well before the 1200 s bound. The gaps between stamps are my own write-up time and are not counted above.

## Acceptance

- A1: socket block run literally; pre-state quoted; override names release-sg320; no rights probe.
- A2: one build (rc 0), one recreate (rc 0); no migration; alembic head unchanged; ids above.
- A3: runtime diff equals the derived set; the two backend app files, both test files, the JS bundle and index.html changed; CSS and both .woff2 identical, with sizes and hashes in the evidence file; served app tree equals worktree.
- A4: G2 strings quoted from the served artifact; honest-limit sentence above.
- A5: health and routes 200; census identical; startup log clean.
- A6: release-sg323 tag on the image built from branch automation at fba17fb; no tag removed or moved; state S1 (no rollback).
- A7: no owner id, name or field value in any log or report; no key or .env read; no provider; no browser; no database write; scratch removed by exact path, shown above.
- A8: failure modes checked: an extra file in the runtime diff (none beyond the expected set); an unchanged JS hash (changed); a missing string (none missing); a moved census count (none); a route not 200 (none); a restart loop (restart count 0); a traceback (none in the named-line grep).
- A9: see the publish step below.
- A10: last line below.

Evidence: docs/worklogs/SG-323_runtime_diff.txt, docs/worklogs/SG-323_census.txt.
