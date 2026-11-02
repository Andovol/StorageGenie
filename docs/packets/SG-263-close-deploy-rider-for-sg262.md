# SG-263 — Close-deploy rider: serve SG-262's three fixes live, prove the served bytes, and record the release evidence

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It serves SG-262's delta and writes its own evidence files. Nothing outside `docs/worklogs` is committed.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: read-only only** — the table census and the schema head below, no write, no migration.
**Restart: one recreate of the backend container**, as the standing rider does.
**Provider: none.** No provider is called, no key is read or printed, no `.env` file is opened, **no spend**. Target: **$0**.

**Contract chain:** recorded `0.56.0` == published payload `contract-v0.56.0` == the host's contract `0.56.0` (the SG-262 report's echo) == the echo this report must carry from `/home/andrei/storagegenie-contract/CODER.md` line 3.

**Previous report's open items:** SG-262's `REMAINING` lines (a split-origin task; the classify type in `client.ts`) are in `docs/backlog.md` W8; **neither is this rider's work**. SG-259's cache-satisfied build needed a tree comparison; keep that comparison. The root-owned `~/.docker` is still expected, so `DOCKER_CONFIG` and an explicit `DOCKER_HOST` are required (G0).

## Why this exists

The owner approved this stage (D7; D10 and D11, 2026-11-02). SG-262 built the three fixes and was audited **96** (`docs/worklogs/SG-262_audit.md`). The standing rule deploys every app-changing slice as its own slice right after it is rated. This rider writes none of the owner's data: the fixes are proven by served code and bundle, not by a live classification.

## G0 — Socket first, and the pre-state

**Before any docker command:** set `DOCKER_CONFIG` to a writable temp directory and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-263/docker.sock`, then prove it answers: `docker version` must print a **Server** section. A denied default path is expected; no daemon restart, no alternate socket, no sudo (`PB-2`, `PG-PR-03`).

Record the pre-serve state: the running container's id and image id, its `Cmd`, restart count and health, the schema head, and a **read-only census of all tables**. Expected, as hypotheses from `STATE.md` and SG-259: container `10f7fc58`, image `d620e39d`, head `20261023_sg233_reminder`, 29 tables. **A difference is a finding: report it, and STOP if the running image is not the one you can account for.** Quote the health body.

## G1 — ONE build, ONE recreate

- One `docker compose build backend` (rc=0). **If the build is cache-satisfied, do not assume the image is current: compare the image's runtime tree against the worktree** and report the result.
- One `docker compose up -d --no-deps --force-recreate backend` (rc=0): the new container's id, image id, `Cmd`, restart count and health.
- **No migration.** The alembic head must be unchanged; report it before and after.
- Health: `curl -s http://127.0.0.1:8003/v1/health` at the start, at least six times after the recreate, and at the end, each answer quoted.

## G2 — The served bytes are SG-262's, and nothing else

- **The runtime diff** between the pre-serve image and the worktree, over the served Python tree, must be **exactly** `backend/app/api/v1/plugins.py` and `backend/app/plugins/expiry_tracker.py`. Any extra or missing file is a finding.
- **The frontend bundle** must change where the product changed: report `index.html`, the JS and the CSS hashes and sizes before and after. The **JS must change**; the index and CSS may be byte-identical, so say which. A byte-identical JS is a finding.
- The served tree must equal the worktree after the build (`diff` rc=0, naming any `__pycache__` exclusion).

## G3 — The new behaviour is in the served artifact

From the **served image's own files** (not the worktree's), quote:

1. the served `app/plugins/expiry_tracker.py` contains `resolved_review_task_ids` in `classify_asset`'s return;
2. the served `app/api/v1/plugins.py` contains `resolved_review_task_ids` in the classify route's response;
3. the served frontend JS contains the string `No date`;
4. the served frontend JS still contains `Manual expiry entry` (the asset page keeps the form).

The review page's removal cannot be shown by a string search on a shared component; **say so**, and point at SG-262's `ReviewPage.test.tsx` test as the proof.

**Honest limit:** the live classify move is **not** exercised, because it would write the owner's data. State plainly that the first real use awaits the owner.

## G4 — The live census is unchanged by this rider

The read-only census of all tables before and after the recreate, every count compared. **Expected delta: zero** (`after == before`). The daily reminder pass may legitimately add `reminder` rows if it fires during this window; if `reminder` moves, report the count and whether the pass's own log line accounts for it. Any other table moving: STOP and report it with the table named.

## G5 — The app answers after the serve

`curl -s http://127.0.0.1:8003/v1/health` (six times, quoted) and the shell routes `/`, `/expiry`, `/inbox`, `/planning` must return 200. No browser, no write, no provider. Report the served container's log section for the startup: no traceback, no configuration error.

## Acceptance criteria

- **A1** — Socket-first proven before any docker command, `DOCKER_CONFIG`/`DOCKER_HOST` named, the Server section quoted; a denied default path is recorded, not routed around.
- **A2** — One build and one recreate, both rc=0, with the container id, image id, `Cmd`, restart count and health quoted; no migration (head unchanged); health green at the start, six times after and at the end; the shell routes 200.
- **A3** — The runtime diff is exactly the two SG-262 backend files; the JS bundle changed (hash and size quoted), the index/CSS status stated; the served tree equals the worktree.
- **A4** — G3's four proofs, each quoted from the served image's own files or bundle, and the explicit honest-limit sentence.
- **A5** — The pre/post census with every table count compared, per G4.
- **A6** — No provider call, no key or `.env` read, no browser, no production write, $0; the rider commits only `docs/worklogs/SG-263*`.
- **A7** — `PB-3` vacuity: say what each check would look like if it failed: a runtime diff with an extra file; a JS hash that did not move; a missing `resolved_review_task_ids` or `No date` in the served artifact; a table count that moved; a health or shell route not 200; a startup traceback. None may be the observed result.
- **A8** — The report's last line is `Verification: PASS` or the honest failure reason.

## Scope ceiling

- `docs/worklogs/SG-263*` only. **No product, config, schema, migration, dependency or test byte.**
- The backend container is recreated **once**; no other service is touched; no migration command; no browser; no provider call; no key value or `.env` read.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`): never route around the socket, sudo or a missing package.

## Hang bounds

`docker version` **120 s**; `docker build` **900 s**; recreate **300 s**; health and shell GETs **120 s**; census and content comparison **300 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1200 s.** Expected ≈450 s, from this lane's rider actuals (SG-257 451 s). SG-259's actual is in its row in `docs/ratings.md`; compare against the engine's elapsed.

## Report

Destination: `docs/worklogs/SG-263_report.md`, evidence logs beside it (`docs/worklogs/SG-263_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈450 s expectation, names every phase over 60 s, and states the container and image ids before and after, the census before and after, and the files changed. The report's evidence is what the release record will cite; **do not create the tag**.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-263 | Report: docs/worklogs/SG-263_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
