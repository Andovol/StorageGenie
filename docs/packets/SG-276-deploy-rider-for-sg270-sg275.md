# SG-276 — Deploy rider: serve SG-270 and SG-275's flow fixes live, prove the served bytes, count the date tasks left behind

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It serves the delta and writes its own evidence files. Nothing outside `docs/worklogs` is committed.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: read-only only** — the table census, the schema head and the counts in G5, no write, no migration, no data repair.
**Restart: one recreate of the backend container**, as the standing rider does.
**Provider: none.** No provider is called, no key is read or printed, no `.env` file is opened, **no spend**.

**Contract chain:** recorded `0.56.0` == published payload `contract-v0.56.0` == the host's contract `0.56.0` (SG-275's echo) == the echo this report must carry from `/home/andrei/storagegenie-contract/CODER.md` line 3.

**Previous report's open items:** SG-270 and SG-275's `REMAINING` lines have destinations in their audits; only the count of older rejected candidates' tasks is this rider's work (G5). The root-owned `~/.docker` is still expected, so `DOCKER_CONFIG` and an explicit `DOCKER_HOST` are required (G0).

## Why this exists

The owner approved stage C (*"d14 ok"*) and its larger size (*"D15 - approved."*). SG-270 was audited 91 and its deploy held for one regression; SG-275 fixed it and was audited 97, which clears the hold. The standing rule deploys every app-changing slice as its own slice right after it is rated. This rider writes none of the owner's data.

## G0 — Socket first, and the pre-state

**Before any docker command:** set `DOCKER_CONFIG` to a writable temp directory under `output/SG-276-scratch/` and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-276/docker.sock`, then prove it answers: `docker version` must print a **Server** section. A denied default path is expected; no daemon restart, no alternate socket, no sudo (`PB-2`, `PG-PR-03`). Remove the scratch path exactly at the end; never touch `output/` itself or `output/dispatch`.

Record the pre-serve state: the running container's id and image id, its `Cmd`, restart count and health, the schema head, and a **read-only census of all tables**. Expected, as hypotheses from `docs/releases/2026-11-02-sg262.md` and `STATE.md`: container `c1beebf9`, image `3e0d49de`, head `20261023_sg233_reminder`. **A difference is a finding: report it, and STOP if the running image is not the one you can account for.** Quote the health body.

## G1 — ONE build, ONE recreate

- One `docker compose build backend` (rc=0). **If the build is cache-satisfied, do not assume the image is current: compare the image's runtime tree against the worktree** and report the result.
- One `docker compose up -d --no-deps --force-recreate backend` (rc=0): the new container's id, image id, `Cmd`, restart count and health.
- **No migration.** The alembic head must be unchanged; report it before and after.
- Health: `curl -s http://127.0.0.1:8003/v1/health` at the start, at least six times after the recreate, and at the end, each answer quoted.

## G2 — The served bytes are these two slices', and nothing else

- **The runtime diff** between the pre-serve image and the worktree, over the served Python tree, is expected to be **exactly** `app/api/v1/candidates.py`, `app/api/v1/review_tasks.py`, `app/plugins/expiry_tracker.py` and `app/services/candidates.py`. Any extra or missing file is a finding.
- **The frontend bundle** must change where the product changed: report `index.html`, the JS and the CSS hashes and sizes before and after. The **JS must change**; a byte-identical JS is a finding.
- The served tree must equal the worktree after the build (`diff` rc=0, naming any `__pycache__` exclusion).

## G3 — The new behaviour is in the served artifact

From the **served image's own files** (not the worktree's), quote:

1. `app/services/candidates.py` contains `CANDIDATE_DECISION_EXEMPT_TASK_TYPES` and `review_task.move`;
2. `app/api/v1/candidates.py` contains `_created_asset_from_commit_step` (the SG-275 repair);
3. `app/api/v1/review_tasks.py` contains `subject_kind`;
4. the served frontend JS contains `The date can be added after accepting.`, `retired split origin` and `Choose a category, then add a date if it has one.`

**Honest limit:** no accept, reject or split is exercised live, because each would write the owner's data. State plainly that the first real use awaits the owner.

## G4 — The live census is unchanged by this rider

The read-only census of all tables before and after the recreate, every count compared. **Expected delta: zero.** The daily reminder pass may legitimately add `reminder` rows during this window; if `reminder` moves, report the count and whether the pass's own log line accounts for it. Any other table moving: STOP and report it with the table named.

## G5 — What the fixes will meet on the live database

Read-only, against the served database, and **counts only: no names, no ids, no field values**:

- open `expiry.manual_entry` tasks, by whether the subject is a candidate or an asset, and for candidates by the candidate's state (`proposed`, `held`, `accepted`, `edited`, `rejected`, `split`, `merged`);
- open tasks of any other type on `rejected`, `split` or `merged` candidates, by type;
- candidates by state, and how many `accepted` or `edited` candidates have a commit step output naming a created asset, against how many do not.

Say what each count means for the owner in one plain line. **Repair nothing.** Any cleanup is the owner's decision.

## G6 — The app answers after the serve

`curl -s http://127.0.0.1:8003/v1/health` (six times, quoted) and the shell routes `/`, `/expiry`, `/inbox`, `/planning` must return 200. No browser, no write, no provider. Report the served container's log section for the startup: no traceback, no configuration error.

## Acceptance criteria

- **A1** — Socket-first proven before any docker command, `DOCKER_CONFIG`/`DOCKER_HOST` named, the Server section quoted; a denied default path is recorded, not routed around.
- **A2** — One build and one recreate, both rc=0, with the container id, image id, `Cmd`, restart count and health quoted; no migration (head unchanged); health green at the start, six times after and at the end; the shell routes 200.
- **A3** — The runtime diff is the four expected files, or the difference is stated; the JS bundle changed (hash and size quoted), the index/CSS status stated; the served tree equals the worktree.
- **A4** — G3's proofs, each quoted from the served image's own files or bundle, and the explicit honest-limit sentence.
- **A5** — The pre/post census with every table count compared, per G4.
- **A6** — G5's counts, with no personal or item data in the report or logs.
- **A7** — No provider call, no key or `.env` read, no browser, no production write, $0; the rider commits only `docs/worklogs/SG-276*`.
- **A8** — `PB-3` vacuity: say what each check would look like if it failed: a runtime diff with an extra file; a JS hash that did not move; a missing string in the served artifact; a table count that moved; a health or shell route not 200; a startup traceback. None may be the observed result.
- **A9** — The report's last line is `Verification: PASS` or the honest failure reason.

## Scope ceiling

- `docs/worklogs/SG-276*` only. **No product, config, schema, migration, dependency or test byte.**
- The backend container is recreated **once**; no other service is touched; no migration command; no browser; no provider call; no key value or `.env` read; no database write.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`): never route around the socket, sudo or a missing package.

## Hang bounds

`docker version` **120 s**; `docker build` **900 s**; recreate **300 s**; health and shell GETs **120 s**; census, counts and content comparison **300 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1200 s.** Expected ≈450 s, from this lane's rider actual SG-257 451 s; compare against the engine's elapsed.

## Report

Destination: `docs/worklogs/SG-276_report.md`, evidence logs beside it (`docs/worklogs/SG-276_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈450 s expectation, names every phase over 60 s, and states the container and image ids before and after, the census before and after, and the files changed. The report's evidence is what the release record will cite; **do not create the tag**.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-276 | Report: docs/worklogs/SG-276_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
