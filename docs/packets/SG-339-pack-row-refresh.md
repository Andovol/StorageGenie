# SG-339 — A pack row shows its new date (or *No date*) right after the date is saved or cleared

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.63.0` (`AGENTS.md`, D42). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-17: *"Then: redesign C — item page as in the mockup (one row per pack, Used up, Add another pack)"*. Stage C (*"d14 ok"*, L3). Found by SG-338 (`docs/worklogs/SG-338_report.md`, its one STOP item).

**Tier: MINOR** (`CODER.md` §11): which cached reads a write refreshes; no new write, route or storage.

## Why this exists

The new item page draws each pack row from the packs query (`["item-packs", householdId, <name>]`, `frontend/src/routes/AssetDetailPage.tsx:~776`), and a row's *Edit* uses `ExpiryEntryForm`. That form's two writes — set a date (`frontend/src/components/ExpiryEntryForm.tsx:83`) and clear it (`:99`) — refresh only `["asset", assetId, householdId]`. **So after saving or clearing a date in a pack row, the row keeps showing the old date until the page reloads** (SG-338: the *Clear* test stays red for exactly this). The amount controls in `PackEditor` already refresh `item-packs` (`AssetDetailPage.tsx:575`) — establish that (`PB-1`).

| ID | Change |
|---|---|
| **G1** | After `ExpiryEntryForm`'s set and clear writes succeed, the pack rows and the catalog list are refreshed too: also invalidate `["item-packs"]` and `["assets"]` (prefix keys) — in the form itself, so every page using it gets fresh lists. Nothing else in the form changes. |

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-339-scratch/docker-config output/SG-339-scratch/logs output/SG-339-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-339-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-339/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-339-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-339-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-339/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-339-scratch/`** — logs, captures, the build, any probe file. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-339-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — Tests first, then the change

Add to `frontend/src/sg336-item-page.sg336.test.tsx`, fed the shape the API really sends (copy the packs-list mock SG-338 added):

- **T9** a pack row with date 6 May 2030: open *Edit*, type 3 Feb 2031, save → after the write, the packs list is read again and the row's date line reads *Use by 3 Feb 2031* (assert the second packs read happened and the text).
- **T10** the same row, *Clear expiry date* → the row reads *No date*.

**Run them before the change (FAIL), log `docs/worklogs/SG-339_fail.log`.** Change `ExpiryEntryForm.tsx`. **Run again (PASS), `SG-339_pass.log`.** The SG-338 STOP test (`frontend/src/routes/AssetDetailPage.test.tsx`, *Clear writes the null active and empties the form*) must now pass **unchanged** — quote it before and after. One commit `SG-339 G1: …`.

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof), `make frontend-test` (**the whole suite, 0 failed** — expected 0 after this, SG-338 left 1), then `*sg336*`, `AssetDetailPage.test.tsx` and every other file using `ExpiryEntryForm` (grep and list them), **run twice**. Logs `docs/worklogs/SG-339_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — G1 with file and line; the premise about `PackEditor`'s amount refresh confirmed or falsified; every page using `ExpiryEntryForm` named.
- **A3** — T9, T10 FAIL before, PASS after; the SG-338 STOP test red before, green after, unchanged.
- **A4** — Gate green with exact counts (frontend 0 failed); the named files twice green.
- **A5** — Frontend files only (`ExpiryEntryForm.tsx`, the sg336 test file); no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a row still showing the old date, a test that never re-reads the list, the SG-338 test edited to pass, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** `frontend/src/components/ExpiryEntryForm.tsx` and `frontend/src/sg336-item-page.sg336.test.tsx`. Any other file is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit what is green, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈500 s (`UNVERIFIED — my estimate`: SG-334, a minor change with the same gate, ≈410 s).

## Report

Destination: `docs/worklogs/SG-339_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; the change with file and line; each premise confirmed or falsified; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-339`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-339 | Report: docs/worklogs/SG-339_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
