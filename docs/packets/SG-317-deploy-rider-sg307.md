# SG-317 — Deploy rider: serve SG-307 (the catalog and item panel in the new look, paper controls, the one-row phone header), prove the served bytes, keep the way back

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It serves the gated SG-307 work and writes only `docs/worklogs/SG-317*`, the scratch path and one image tag.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: read-only only** — the schema head and a table census, no write, no migration, no data repair.
**Restart: one recreate of the backend container**, as the standing rider does.
**Provider: none.** No provider is called, no key is read or printed, no `.env` is opened by you, **no spend**.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Authority:** owner D18, D33 (*"D33 approved."*); stage C (*"d14 ok"*, L3); the standing close-out rule (`AGENTS.md`). SG-307 is rated 78 (three runs, gate green at `14c1f1f`) and its screens were seen in SG-316 (`docs/worklogs/SG-316_audit.md`, `docs/worklogs/SG-307_shots/`); ratings in `docs/ratings.md`.

## Why this exists

SG-307, SG-307r1 and SG-315 (`614f61b..HEAD`) change **frontend files only** and **no dependency** (expected, `UNVERIFIED` — derive it: `git diff --name-only 614f61b..HEAD -- backend/ ':!backend/alembic'` empty, `-- frontend/package.json frontend/package-lock.json` empty). The live app serves `release-sg314` (`docs/releases/2026-11-12-sg314.md`), built from `614f61b`. So the expected runtime change is `static/` only: the JS and CSS bundles and `index.html`; the two Instrument Sans `.woff2` files unchanged.

## The way back — binds every goal, wins over any other instruction here (`PG-IC-03`)

| State | When | On failure |
|---|---|---|
| **S0** | Before the recreate | Stop. The app was never touched |
| **S1** | New container started | If it is not healthy within **120 s**, or restarts, serve the previous image **once** by the override below, prove health, report. No other retry |
| **S2** | A recovery step itself failed or was denied | Leave things as they are, report outcome `UNKNOWN`, no further attempt |

**Serving the previous image (S1):** write `output/SG-317-scratch/rollback.override.yml` setting only `services.backend.image: storagegenie-backend:release-sg314`, then `docker compose -f docker-compose.yml -f output/SG-317-scratch/rollback.override.yml up -d --no-build --no-deps --force-recreate backend`. With no migration, the old image reads the database unchanged. **Never run `docker compose config` without `--images`:** it prints the resolved `.env` values.

**A denial is a STOP (`PB-2`, `PG-PR-03`), never a reason to try another route.**

## G0 — Socket first, and the pre-state

Copy these lines exactly:

```
mkdir -p output/SG-317-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-317-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-317/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-317/
docker version
```

`docker version` prints a **Server** section; otherwise STOP as BLOCKED with the verbatim error. Scratch stays in `output/SG-317-scratch/`; **no `/tmp`, for any command, including `curl -o`** (the lane denies it), removed by exact path at the end; never touch `output/` itself or `output/dispatch`. **Run `date +%s` at the start of every goal and quote the stamps**; the report computes each phase's seconds from them.

- `curl -s http://127.0.0.1:8003/v1/health` quoted.
- **Pre-state, hypotheses from `docs/releases/2026-11-12-sg314.md`:** container `5cd10798…`, image `91b0969e…`, head `20261102_sg279_candidate_state`, restart count 0. `docker inspect` only with `--format` and named fields. A different running image you cannot account for is a STOP in S0.
- `storagegenie-backend:release-sg314` resolves to the running image id, and `docker compose -f docker-compose.yml -f output/SG-317-scratch/rollback.override.yml config --images` names it for `backend`; otherwise STOP in S0.
- A **read-only census** of every table: open the live database read-only, on a byte copy if WAL files sit in a read-only mount (SG-295 I1). Counts only.
- **No rights probe on any real object** (`PG-PR-01`): never tag, untag, stop or restart anything of the app's to test rights.

## G1 — ONE build, ONE recreate

- One `docker compose build backend`, rc 0. If cache-satisfied, compare the image's runtime tree against the worktree; do not assume. Report where `storagegenie-backend:latest` points before and after.
- **The runtime diff** between the running image and the new one, over the whole served `/app` tree. **Derive the expected backend set yourself:** `git diff --name-only 614f61b..HEAD -- backend/ ':!backend/alembic'` — my expectation, labelled as such: **empty**. Then only `static/` may differ: the JS and CSS bundles must change; **the Instrument Sans `.woff2` files must be byte-identical** (same names, same hashes) — list each with size. Any measured backend file outside the derived set is a STOP in S0. **To hash the new image's tree before the recreate, this command is authorised:** `docker run --rm --network none --entrypoint sh storagegenie-backend:latest -c 'cd /app && find . -type f -exec sha256sum {} +'` — no mounts, no env file, no port.
- Alembic head unchanged before and after; **no migration command**.
- One `docker compose up -d --no-deps --force-recreate backend`, rc 0. **Now S1.** New container id, image id, `Cmd`, restart count, health; the measured recreate-to-healthy seconds.
- **Tag what now serves:** `storagegenie-backend:release-sg317` on the new image id. Absent → create; resolves to the same id → nothing; resolves elsewhere → do not touch it, report it. Never remove or move any tag; `release-sg314`, `release-sg310`, `release-sg309`, `release-sg303`, `release-sg299`, `release-sg296`, `release-sg295` and `recovery-sg270` stay.

## G2 — The new behaviour is in the served artifact

From the **served container's own files**, before and after counts in the served JS and CSS: the CSS contains the `.sg-paper-control` rule and a `max-width: 480px` media rule hiding `.sg-import-label` (quote both as served); the JS contains *Photo only*, *Cut-out ready*, *No cut-out yet.*, *In a scene* and *Food & beverages*; it no longer contains `Source Only`, `Isolated Cutout` nor `Bounding-box overlay omitted` (count before and after). `GET /assets/<the woff2 the CSS names>` on `127.0.0.1:8003` returns 200 — quote the content type (backlog W11 expects `application/octet-stream`; report it, it is not a STOP).

**Honest limit:** no screen is viewed in a browser here; the screens were seen in SG-316 on a scratch build of the same commit. State that.

## G3 — The app answers, and nothing moved

`/v1/health` six times, each quoted; shell routes `/`, `/pantry`, `/expiry`, `/inbox`, `/planning` return 200; `GET /v1/assets?household_id=<id>&category=food_beverages&limit=5` and `GET /v1/plugins/expiry-tracker/status?household_id=<id>&category=food_beverages` each return 200 — quote the status codes and the number of `items` on the first page only (the response has no `total`); take the household id from the database and **never print it**. Startup log: **read only by named lines** — `grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`, never a wider filter; the access log carries household ids in query strings (backlog W10), and none may reach your output. Census after compared with G0, every table; **`reminder` may rise only as that line accounts for**; any other table moving is reported at once.

## Acceptance criteria

- **A1** — Socket-first proven with the literal block; pre-state quoted; the rollback override names `release-sg314`; no rights probe.
- **A2** — One build, one recreate, rc 0; no migration (head unchanged, alembic diff empty); container and image ids before and after.
- **A3** — Runtime diff equals the derived set (derived list and my expectation both quoted); JS and CSS changed, the `.woff2` files unchanged, with sizes and hashes; served tree equals worktree.
- **A4** — G2's strings quoted from the served artifact; the honest-limit sentence.
- **A5** — Health and routes 200; census compared; startup log clean.
- **A6** — `release-sg317` tag's branch stated; no tag removed or moved; the state reached (S0, S1, S1 with rollback, S2) named.
- **A7** — No name, id or field value of the owner's in any log or report; no key or `.env` read or printed; no provider; no browser; no database write; scratch removed by exact path, the removal shown.
- **A8** — `PB-3` vacuity: a failure would look like an extra file in the runtime diff, an unchanged JS hash, a missing string, a moved count, a route not 200, a restart loop, a traceback. Say which you checked.
- **A9** — `HEAD` equals `origin/automation` after your push, both hashes quoted; phase seconds from the stamps.
- **A10** — The last line is `Verification: PASS`, `Verification: STOPPED in S<n> — <reason>`, or `FAIL`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-317*` only in git; `output/SG-317-scratch/`; the one `release-sg317` tag; the backend container, recreated once (twice only through S1's rollback).
- **No product, config, schema, migration, dependency or test byte.** No other service touched. No data repair. Stored photos and files untouched.
- **Stage only by the exact path `docs/worklogs/SG-317*`**, never `git add -A` or `git add .`; `git status --short` clean and `git show --stat HEAD` holding only those paths.
- **Authorised runtimes:** the docker and compose commands named here, `curl` to `127.0.0.1`, and a read-only SQLite census. Never `docker rmi`, `image prune`, `system prune`, or `docker compose config` without `--images`.

## Hang bounds

`docker version` **120 s**; build **900 s**; recreate **300 s**; health wait **120 s**; health and routes **120 s**; census **300 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1200 s.** Expected ≈200 s (`UNVERIFIED — my estimate`: SG-314 took 159 s; no new package). Runtime against budget in the report (`PG-PR-06`).

## Report

Destination: `docs/worklogs/SG-317_report.md`, evidence beside it (`docs/worklogs/SG-317_*`), each evidence file small: the runtime diff as changed paths with both hashes, not full-tree dumps. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved commit, and WORK_HEAD. It compares engine elapsed with ≈200 s, gives every phase's seconds, the state reached, the ids before and after, the census before and after, and one line per constraint. The report feeds the release record; **do not create a git tag**.

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-317`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-317 | Report: docs/worklogs/SG-317_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or the honest stop or failure reason.
