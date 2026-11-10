# SG-299 — Deploy rider: serve SG-272 (with SG-297 and SG-298) live, prove the served bytes, keep the way back

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It serves the gated SG-272 work and writes only `docs/worklogs/SG-299*`, the scratch path and one image tag.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: read-only only** — the schema head and a table census, no write, no migration, no data repair.
**Restart: one recreate of the backend container**, as the standing rider does.
**Provider: none.** No provider is called, no key is read or printed, no `.env` is opened by you, **no spend**.

**Contract:** recorded `0.58.0` (`AGENTS.md`). **This lane denies reading the contract folder; do not try.** Your own contract's version line, as you received it, is the host evidence: echo it. A denial on that folder is expected and is not a STOP.

**Authority:** owner, stage C (*"d14 ok"*, L3); the standing rule deploys every app-changing slice as its own slice right after it is rated (`AGENTS.md`, Close-out). SG-272 rated 85, SG-297 90, SG-298 92, no flags; SG-298's full gate is green (`docs/worklogs/SG-298_audit.md`).

## Why this exists

SG-272 (`391e6c8..3dcfd82`) adds gone with a reason, put back, one-tap quantities and a Gone view; SG-297 (`e845baf..dd9b1b6`) and SG-298 (`468a17b..8be5bb8`) fixed its task paging and its two gate reds. **None has a migration** (no file under `backend/alembic/versions/` changed — verify with `git diff --name-only 58ce7fa..HEAD -- backend/alembic`). The live app serves `release-sg296`.

## The way back — binds every goal, wins over any other instruction here (`PG-IC-03`)

| State | When | On failure |
|---|---|---|
| **S0** | Before the recreate | Stop. The app was never touched |
| **S1** | New container started | If it is not healthy within **120 s**, or restarts, serve the previous image **once** by the override below, prove health, report. No other retry |
| **S2** | A recovery step itself failed or was denied | Leave things as they are, report outcome `UNKNOWN`, no further attempt |

**Serving the previous image (S1):** write `output/SG-299-scratch/rollback.override.yml` setting only `services.backend.image: storagegenie-backend:release-sg296`, then `docker compose -f docker-compose.yml -f output/SG-299-scratch/rollback.override.yml up -d --no-build --no-deps --force-recreate backend`. With no migration, the old image reads the database unchanged. **Never run `docker compose config` without `--images`:** it prints the resolved `.env` values.

**A denial is a STOP (`PB-2`, `PG-PR-03`), never a reason to try another route.**

## G0 — Socket first, and the pre-state

Copy these lines exactly (a past run mistyped this path by hand):

```
mkdir -p output/SG-299-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-299-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-299/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-299/
docker version
```

`docker version` prints a **Server** section; otherwise STOP as BLOCKED with the verbatim error. Scratch stays in `output/SG-299-scratch/`, removed by exact path at the end; never touch `output/` itself or `output/dispatch`. **Run `date +%s` at the start of every goal and quote the stamps**; the report computes each phase's seconds from them.

- `curl -s http://127.0.0.1:8003/v1/health` quoted.
- **Pre-state, hypotheses from `docs/releases/2026-11-09-sg296.md` and `STATE.md`:** container `0c4462ee…`, image `dcc67781…`, head `20261102_sg279_candidate_state`, restart count 0. `docker inspect` only with `--format` and named fields. A different running image you cannot account for is a STOP in S0.
- `storagegenie-backend:release-sg296` resolves to the running image id, and `docker compose -f docker-compose.yml -f output/SG-299-scratch/rollback.override.yml config --images` names it for `backend`; otherwise STOP in S0.
- A **read-only census** of every table: open the live database read-only, on a byte copy if WAL files sit in a read-only mount (SG-295 I1). Counts only.
- **No rights probe on any real object** (`PG-PR-01`): never tag, untag, stop or restart anything of the app's to test rights.

## G1 — ONE build, ONE recreate

- One `docker compose build backend`, rc 0. If cache-satisfied, compare the image's runtime tree against the worktree; do not assume.
- **The runtime diff** between the running image and the new one, over the served Python tree, is expected to be **exactly** `app/api/v1/assets.py`, `app/api/v1/reminders.py`, `app/api/v1/review_tasks.py`, `app/services/asset_service.py`, `app/services/expiry_engine.py`, `app/services/lifecycle.py` (derive it yourself: `git diff --name-only 58ce7fa..HEAD -- backend/app`, and report any difference from this list). Any other file is a STOP in S0. The **JS bundle must change**; report `index.html`, JS and CSS hashes and sizes before and after.
- Alembic head unchanged before and after; **no migration command**.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0. **Now S1.** New container id, image id, `Cmd`, restart count, health; the measured recreate-to-healthy seconds.
- **Tag what now serves:** `storagegenie-backend:release-sg299` on the new image id. Absent → create; resolves to the same id → nothing; resolves elsewhere → do not touch it, report it. Never remove or move any tag; `release-sg296`, `release-sg295` and `recovery-sg270` stay.

## G2 — The new behaviour is in the served artifact

From the **served container's own files**, not the worktree: `app/api/v1/review_tasks.py` contains `def _visible_tasks`; `app/api/v1/assets.py` contains `def _gone_reason_from_assertions` and `/quantity/decrement`; `app/services/asset_service.py` contains `def put_back` and `def mark_gone`. The served JS contains `Put back`, `Gone items`, `Use it up`, `Amount left` and `Thrown away`.

**Honest limit:** no gone, put back, increment or decrement is exercised live, because each writes the owner's data. State plainly that the first real use is the owner's.

## G3 — The app answers, and nothing moved

`/v1/health` six times, each quoted; shell routes `/`, `/expiry`, `/inbox`, `/planning` return 200; `GET /v1/review-tasks?household_id=<id>&limit=5` and `GET /v1/assets?household_id=<id>&limit=5` each return 200 — quote the status codes and the review-tasks `total` only; take the household id from the database and **never print it**. Startup log: no traceback or configuration error; the daily pass's own line quoted. Census after compared with G0, every table; **`reminder` may rise only as that line accounts for**; any other table moving is reported at once.

## Acceptance criteria

- **A1** — Socket-first proven with the literal block; pre-state quoted; the rollback override names `release-sg296`; no rights probe.
- **A2** — One build, one recreate, rc 0; no migration (head unchanged, alembic diff empty); container and image ids before and after.
- **A3** — Runtime diff is the expected set (derived list quoted); JS changed, hashes and sizes quoted; served tree equals worktree.
- **A4** — G2's strings quoted from the served artifact; the honest-limit sentence.
- **A5** — Health and routes 200; census compared; startup log clean.
- **A6** — `release-sg299` tag's branch stated; no tag removed or moved; the state reached (S0, S1, S1 with rollback, S2) named.
- **A7** — No name, id or field value of the owner's in any log or report; no key or `.env` read or printed; no provider; no browser; no database write; scratch removed by exact path, the removal shown.
- **A8** — `PB-3` vacuity: a failure would look like an extra file in the runtime diff, an unchanged JS hash, a missing string, a moved count, a route not 200, a restart loop, a traceback. Say which you checked.
- **A9** — `HEAD` equals `origin/automation` after your push, both hashes quoted; phase seconds from the stamps.
- **A10** — The last line is `Verification: PASS`, `Verification: STOPPED in S<n> — <reason>`, or `FAIL`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-299*` only in git; `output/SG-299-scratch/`; the one `release-sg299` tag; the backend container, recreated once (twice only through S1's rollback).
- **No product, config, schema, migration, dependency or test byte.** No other service touched. No data repair. Stored photos and files untouched.
- **Stage only by the exact path `docs/worklogs/SG-299*`**, never `git add -A` or `git add .`; `git status --short` clean and `git show --stat HEAD` holding only those paths.
- **Authorised runtimes:** the docker and compose commands named here, `curl` to `127.0.0.1`, and a read-only SQLite census. Never `docker rmi`, `image prune`, `system prune`, or `docker compose config` without `--images`.

## Hang bounds

`docker version` **120 s**; build **900 s**; recreate **300 s**; health wait **120 s**; health and routes **120 s**; census **300 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1200 s.** Expected ≈300 s (`UNVERIFIED — my estimate`, from this lane's last code-only rider, SG-296 run 2, ~150 s, plus a larger runtime diff). Runtime against budget in the report (`PG-PR-06`).

## Report

Destination: `docs/worklogs/SG-299_report.md`, evidence beside it (`docs/worklogs/SG-299_*`). The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved commit, and WORK_HEAD. It compares engine elapsed with ≈300 s, gives every phase's seconds, the state reached, the ids before and after, the census before and after, and one line per constraint. The report feeds the release record; **do not create a git tag**.

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-299`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-299 | Report: docs/worklogs/SG-299_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or the honest stop or failure reason.
