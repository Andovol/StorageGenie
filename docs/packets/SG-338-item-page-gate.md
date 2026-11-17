# SG-338 — Finish SG-336: update the 37 older tests to the new item page, copy the shelf-life category onto a new pack, run the full gate to green

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.63.0` (`AGENTS.md`, D42). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-17: *"Then: redesign C — item page as in the mockup (one row per pack, Used up, Add another pack)"*. Stage C (*"d14 ok"*, L3). This slice finishes SG-336, which stopped at its budget (`docs/worklogs/SG-336_report.md`, `Verification: FAIL — budget stop`).

**Tier: STANDARD** (`CODER.md` §11).

## Why this exists

SG-336 rebuilt `frontend/src/routes/AssetDetailPage.tsx` and its own tests pass (7/7), but **37 older tests in 8 files still assert the old layout** and the full gate never ran. Its report lists each file, its count and the direction of the update (`SG-336_report.md` §Tests, lines 61–67) — **use that list as your map; establish each failure yourself (`PB-1`)**. Every old behaviour still exists on the new page (in *More about this item*, behind *History (…)*, or in a pack row's *Edit*), so **an update opens the right section first and then asserts the same behaviour — never deletes an assertion to make it green.** A behaviour an old test protects that the new page truly lost is a STOP for that item: report it, do the rest.

Second, `addPackMut` (`AssetDetailPage.tsx:~963`) creates the new pack with `display_name` and `asset_type` but **not the opened item's shelf-life category** (`plugin:expiry-tracker/classification`), so the new pack would show *Uncategorized* beside its siblings. Hypothesis (`UNVERIFIED`): the page already has a classification write it uses for one item (find it; the scratch seed in SG-333 used `POST /v1/assets/<id>/classification {"category": …}`).

| ID | Change |
|---|---|
| **G1** | Each of the 37 failing assertions updated to the new layout, **file by file, smallest first**, each named old → new in the report. After each file: run that file alone and log it. |
| **G2** | *Add another pack* also sets the new pack's shelf-life category to the opened item's, through the existing classification write, when the opened item has one. Add **T8** to `frontend/src/sg336-item-page.sg336.test.tsx`: the create is followed by one classification write for the new id with the opened item's category, and none for any other id. |

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-338-scratch/docker-config output/SG-338-scratch/logs output/SG-338-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-338-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-338/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-338-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-338-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-338/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-338-scratch/`** — logs, captures, the build, **any probe or bisect file**. **Never `/tmp`, for anything** (SG-336 left `/tmp/opencode/probe.tsx`; do not touch it, it is the Architect's to remove). Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-338-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1, G2 — the order

1. First, one full `make frontend-test` run to take the list of failures (log `docs/worklogs/SG-338_before.log`, exact counts; expected 37 failed — a different number is stated, not a STOP).
2. G2 first (it is small): write T8, run it (FAIL, `SG-338_fail.log`), change, run it (PASS, `SG-338_pass.log`). Commit `SG-338 G2: …`.
3. G1, file by file. Commit after every file that turns green: `SG-338 G1: <file> …`. **A file you cannot finish is left as it was and listed `REMAINING`** — never half-edited.

## G3 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then `*sg336*` and every older file changed here, **run twice**. Logs `docs/worklogs/SG-338_<step>.log`, exact counts. **Start G3 no later than 800 s by your stamps**, whatever G1 has left: the gate's result is worth more than one more file.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — Every updated assertion named old → new with file and line; no assertion deleted without a replacement asserting the same behaviour; any lost behaviour named as a STOP item.
- **A3** — T8 FAIL before, PASS after; logs named.
- **A4** — Gate green with exact counts (frontend 0 failed); the named files twice green.
- **A5** — Frontend files only (test files, `AssetDetailPage.tsx` for G2); no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like an assertion removed with nothing in its place, a test that never opens *More* but passes, a new pack with no category, a classification write on another id, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** the 8 test files SG-336's report names, `frontend/src/sg336-item-page.sg336.test.tsx`, and `frontend/src/routes/AssetDetailPage.tsx` **for G2 only**. Changing the page's layout or behaviour to make an old test pass is a STOP for that item.
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **G3 starts by 800 s. At 1100 s by your stamps, stop, remove scratch, commit what is green, write the report, publish — whatever is left.** SG-336 ran to ≈1700 s past this line; **that is a breach, not an option.** **No optional goal.** Expected ≈900 s (`UNVERIFIED — my estimate`: SG-324r1, a gate-and-test-alignment slice, 709 s). A stop leaves the rest `REMAINING`, named per file.

## Report

Destination: `docs/worklogs/SG-338_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; per file the assertions updated old → new; G2 with file and line; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-338`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-338 | Report: docs/worklogs/SG-338_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
