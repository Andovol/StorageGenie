# SG-257 — Close-deploy rider: serve SG-256's row-11 polish live, prove the served bytes, and record the release evidence

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It serves SG-256's delta and writes its own evidence files. Nothing outside `docs/worklogs` is committed.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: read-only only** — the table census and the schema head below, no write, no migration.
**Restart: one recreate of the backend container**, as the standing rider does.
**Provider: none.** No provider is called, no key is read or printed, no `.env` file is opened, **no spend**. Target: **$0**.

**Contract chain:** recorded `0.53.0` (this packet's commit) == published payload `contract-v0.53.0` == the host's contract `0.53.0` (the SG-256 receipt echo) == the echo this report must carry from `/home/andrei/storagegenie-contract/CODER.md` line 3.

**Previous report's open items:** SG-256 left no product item; the root-owned `~/.docker` is still pending in the engine arc, so `DOCKER_CONFIG` stays required and `DOCKER_HOST` must be exported to the lane socket. The packet's base-checkout accounting gap is closed; nothing applies to this rider.

## Why this exists

The owner approved the row-11 polish plan on 2026-10-28 (`"D4 - approved"`, D4 in `STATE.md`); SG-256 built it and was audited **96**. The standing rule deploys every app-changing slice as its own slice right after it is rated, and the live app still runs SG-250's image (`a831fbd0` from `e8c73735`). This rider serves the seven-file delta and is where the edit/clear paths become live. It does not write the owner's data: the live controls are proven by the served code and bundle, not by a live clear.

## G0 — Socket first, and the pre-state

**Before any docker command:** set `DOCKER_CONFIG` to a writable temp directory and `DOCKER_HOST` to the lane socket (the shell does not export it), then prove it answers — `docker version` must print a **Server** section. A denied default path is expected (I1 of SG-256); no daemon restart, no alternate socket, no sudo (`PB-2`, `PG-PR-03`).

Record the pre-serve state: the running container's id and image id, its `Cmd`, restart count and health, the schema head (expect `20261023_sg233_reminder`), and a **read-only census of all 29 tables**. The `provider_call` count matters and must not move. Quote the health body.

## G1 — ONE build, ONE recreate

- One `docker compose build backend` (rc=0). **If the build is cache-satisfied, do not assume the image is current — compare the image's runtime tree against the worktree** and report the result.
- One `docker compose up -d --no-deps --force-recreate backend` (rc=0): the new container's id, image id, `Cmd`, restart count and health.
- **No migration.** The alembic head must stay `20261023_sg233_reminder`; report the head before and after.
- Health: `curl -s http://127.0.0.1:8003/v1/health` at the start, at least six times after the recreate, and at the end — each answer quoted.

## G2 — The served bytes are SG-256's, and nothing else

- **The runtime diff** between the pre-serve image (`e8c73735`) and the worktree, measured over the served Python tree: it must be **exactly** `backend/app/api/v1/plugins.py` and `backend/app/plugins/expiry_tracker.py` — the two SG-256 backend files — and **nothing else**. Any extra or missing file is a finding, not a detail.
- **The frontend bundle** must change where the product changed: report `index.html`, the JS and the CSS hashes and sizes before and after. The **JS must change** (the component, client and types are in it); the index and CSS may be byte-identical — say which. A byte-identical JS is a finding.
- The served tree must equal the worktree after the build (`diff` rc=0).

## G3 — The new behaviour is in the served artifact

From the **served image's own files** (not the worktree's), quote:
1. the served `app/api/v1/plugins.py` contains the `/opened/clear` route and calls `clear_opened_date`;
2. the served `app/plugins/expiry_tracker.py` contains `clear_opened_date` and passes `None` to `_write_assertion`;
3. the served frontend JS contains the clear path `/opened/clear` and the visible `Clear opened date` label (grep the bundle; quote the hits).

**Honest limit:** the live clear/edit write is **not** exercised — it would write the owner's data. The served code and bundle are the proof; state plainly that the first real clear awaits the owner's use.

## G4 — The live census is unchanged

The read-only census of all 29 tables before and after: every count identical, including `provider_call`. The rider writes no row. If a count moved, STOP and report it as a finding with the table named.

## G5 — The app answers after the serve

`curl -s http://127.0.0.1:8003/v1/health` (six times, quoted) and the shell routes `/`, `/expiry`, `/inbox`, `/planning` must return 200. No browser, no write, no provider. Report the served container's log section for the startup — no traceback, no configuration error.

## Acceptance criteria

- **A1** — socket-first proven before any docker command, `DOCKER_CONFIG`/`DOCKER_HOST` named, the `docker version` Server section quoted; a denied default path is recorded, not routed around.
- **A2** — one build and one recreate, both rc=0, with the container id, image id, `Cmd`, restart count and health quoted; **no migration** (head unchanged); health green at the start, six times after and at the end; the shell routes 200.
- **A3** — the runtime diff is **exactly** the two SG-256 backend files and nothing else; the JS bundle changed (hash and size quoted), the index/CSS status stated; the served tree equals the worktree (`diff` rc=0).
- **A4** — G3's three proofs, each quoted from the served image's own files/bundle, and the explicit honest-limit sentence.
- **A5** — the pre/post census: all 29 table counts identical, including `provider_call`.
- **A6** — no provider call, no key or `.env` read, no browser, no production write, $0; the rider commits only `docs/worklogs/SG-257*`.
- **A7** — `PB-3` vacuity: say what each check would have looked like if it failed — a runtime diff with an extra file; a JS hash that did not move; a missing clear route in the served code; a startup traceback; a `provider_call` count that moved; a health or shell route that was not 200. None of these may be the observed result.
- **A8** — the report's last line is `Verification: PASS` or the honest failure reason.

## Scope ceiling

- `docs/worklogs/SG-257*` only. **No product, config, schema, migration, dependency or test byte.**
- The backend container is recreated **once**; no other service is touched; no migration command; no browser; no provider call; no key value or `.env` read.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`): never route around the socket, sudo or a missing package.
- The dispatch key opens no shell and runs nothing but this slice.

## Hang bounds

`docker version` **120 s**; `docker build` **900 s**; recreate **300 s**; health/shell GETs **120 s**; census and content comparison **300 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1200 s.** Expected ≈400 s, derived from SG-251's actual 257 s for one build, one recreate and a full verify, plus SG-256's frontend-layer rebuild and the bundle/census comparison.

## Report

Destination: `docs/worklogs/SG-257_report.md`, evidence logs beside it (`docs/worklogs/SG-257_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈400 s expectation, names every phase over 60 s, and states the container and image ids before and after, the census before and after, and the files changed. The report's evidence is what the release record will cite; **do not create the tag**.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-257 | Report: docs/worklogs/SG-257_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
