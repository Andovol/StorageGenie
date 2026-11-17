# SG-334 — *Import Asset* in the non-catalog nav becomes *Add item*, styled as the catalog header's

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; a rider follows.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-17: *"Then: small slice for "Import Asset" left in the non-catalog nav (App.tsx:156, :176) → "Add item", plus its rider."* Stage C (*"d14 ok"*, L3).

**Tier: MINOR** (`CODER.md` §11): one label, its accessible name and its colours; no storage, privacy, write, route or production surface. One targeted test FAIL → PASS plus the full gate; a short report.

## Why this exists

SG-330 R2 renamed the catalog header's button to *Add item* (`frontend/src/components/shell/AppHeader.tsx:81–104`), but every other page still shows the shared legacy nav's *Import Asset* (`frontend/src/App.tsx:156` `aria-label`, `:176` label; SG-332 audit I22). Hypotheses (`PB-1`): these two strings are the only product occurrences (`grep -rn "Import Asset" frontend/src`); the legacy link uses `--ink` / `--paper` (`App.tsx:~170`) while the catalog header's uses `--primary` / `--primary-foreground` (`AppHeader.tsx:~98`); `frontend/src/components/shell/shell.test.tsx:451–452` asserts the old name and is updated; `frontend/src/sg330-r2.sg330.test.tsx:91` asserts the old name is absent from the catalog and stays valid.

| ID | Change |
|---|---|
| **G1** | On every non-catalog route, the nav button's visible label and accessible name are *Add item*; its background and text colours are the catalog header's (`--primary` / `--primary-foreground`); it still opens the import dialog instead of routing to `/capture`. **No product occurrence of *Import Asset* remains** in `frontend/src` (tests that assert its absence excepted). |

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-334-scratch/docker-config output/SG-334-scratch/logs output/SG-334-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-334-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-334/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-334-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-334-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-334/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-334-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-334-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — The change

**Write the test first and run it (FAIL), then change `App.tsx` and run it again (PASS)**; log names and first assertion to `docs/worklogs/SG-334_fail.log` and `SG-334_pass.log`. Test file `frontend/src/sg334-add-item-nav.sg334.test.tsx`: render a non-catalog route (e.g. `/capture`, as `shell.test.tsx:448` does) and assert a link named *Add item*, no element named or reading *Import Asset*, the link's inline `background-color` / `color` naming `--primary` / `--primary-foreground`, and that clicking it opens the import dialog. One commit `SG-334 G1: …` holding the change, its test and `shell.test.tsx` updated (old → new named). Leave the `sg-import-label` class as it is.

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg334*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-334_<step>.log`, exact counts. Quote `grep -rn "Import Asset" frontend/src` after the change.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — G1 done with file and line; every wrong premise named.
- **A3** — The test FAIL before, PASS after; logs named.
- **A4** — Gate green with exact counts; the named files twice green; the final `grep` quoted.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like *Import Asset* still rendered on `/capture`, an *Add item* that routes instead of opening the dialog, the ink colours kept, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** `frontend/src/App.tsx`, `frontend/src/components/shell/shell.test.tsx`, new `*.sg334.test.tsx`. Any other file is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈450 s (`UNVERIFIED — my estimate`: SG-328, a slice of the same size and gate).

## Report

Destination: `docs/worklogs/SG-334_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; the change with file and line; each premise confirmed or falsified; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-334`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-334 | Report: docs/worklogs/SG-334_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
