# SG-315 — Make SG-307's gate green: restore the drop-zone highlight, and bring 8 old styling tests to the new look

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write.
**Restart: none.** No deploy; a screenshot slice and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D18, D33 (*"D33 approved."*), D34; stage C (*"d14 ok"*, L3).

## Why this exists

SG-307 (`0dd3fa7..991c4d5`) put the catalog and item panel in the new look; SG-307r1 (`21d5761..ea01628`) fixed three things and ran the full gate (`docs/worklogs/SG-307r1_report.md` § Gate counts). Two reds remain, both **introduced by SG-307** (expected, `UNVERIFIED` — establish each):

1. **A lost feature:** `frontend/src/components/shell/AssetImportModal.tsx:76` — `dragOver` is set but never read (eslint `no-unused-vars`). Before SG-307 (`git show 0dd3fa7:frontend/src/components/shell/AssetImportModal.tsx`, line 206) the drop zone used it: `${dragOver ? "border-primary" : "border-border"}`. So **the drop zone no longer shows that a file is over it.** Restore the highlight in the new look (paper ground, square; the border in `--primary` while dragging, `--line` otherwise).
2. **Eight frontend tests** fail on class names (`docs/worklogs/SG-307r1_frontend-test.log`): `AssetForm.test.tsx` (the asset-type select's themed control; the file pickers behind themed labels), `InboxPage.test.tsx` (failed job detail and retry; a review task resolved), `theme-adoption.test.tsx` (capture screen container), `shell.test.tsx` (an active category pill *"carries the primary style"*; *Clear all*; an empty saved-search list *"renders a muted None yet"*).

**For each failing test, decide from the code, and say which:** (a) **the old class guarded something an owner sees** (an active pill must look different from an inactive one; *None yet* must look muted; a control must look like a control) → assert **the new equivalent** (e.g. the active pill's ink fill, `sg-paper-control`, the muted colour token), never delete the check; or (b) the product lost that thing → fix the product, like item 1. **A test is never weakened to pass** — every changed assertion is quoted old → new in the report.

## G0 — Preflight

```
mkdir -p output/SG-315-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-315-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-315/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-315/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-315-scratch/` (npm's cache there too). **No `/tmp` for anything — not even a redirect of a tail** (SG-307r1 left a file there). Run every command from the repository root and give the build an absolute `--outDir "$PWD/output/SG-315-scratch/build"` (SG-307r1's relative path landed under `frontend/`). `git status --short` clean except `output/` before the report; `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — The fixes, with tests

Item 1, then item 2 file by file. In `*.sg315.test.tsx`: the drop zone's border changes on drag-over and back on drag-leave (fire the events). FAIL on base, PASS on candidate; logs `docs/worklogs/SG-315_fail.log`, `SG-315_pass.log` (names and first assertion only). Commit.

## G2 — The full gate

As SG-307r1's R2: `eslint` (only the known `App.household-nav.test.tsx` error may remain — name it), `tsc`, the frontend build into scratch, `make backend-test` (host and image proof), `make frontend-test` (**0 failed**), then every `*.sg307*`, `*.sg307r1*`, `*.sg315*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-315_<step>.log`, exact counts. Commit.

**Time rule: if G1 is not committed by 500 s by your stamps, commit what is done, mark the rest `REMAINING`, and run G2. G2 is never skipped.**

## Acceptance criteria

- **A1** — The drop-zone highlight restored, file named; each of the 8 tests resolved as (a) or (b), the old and new assertion quoted.
- **A2** — G1 FAIL on base, PASS on candidate.
- **A3** — Gate green: eslint only the known error, frontend suite 0 failed, host and image green; files twice green; exact counts.
- **A4** — Zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before the report.
- **A5** — Preflight; health 200 start and end; phase seconds from stamps.
- **A6** — `PB-3` vacuity: a failure would look like a drop zone whose border does not change, a deleted assertion, a test passing on base, an eslint error beyond the known one, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/src/components/shell/AssetImportModal.tsx`; and, only under (b) for one of the 8 tests, the one product file that test renders, named with the reason. Any other product file is a STOP and report (`PG-EV-03`).
- **Tests:** the four named older test files; new `*.sg315*` files.
- **No backend file.**
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the frontend build into scratch. No install, no server, no browser.
- Evidence: `docs/worklogs/SG-315*` only. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2; commit after each. Expected ≈650 s (`UNVERIFIED — my estimate`: SG-307r1's gate took ≈350 s; one small product fix and 8 assertions ≈250 s).

## Report

Destination: `docs/worklogs/SG-315_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each premise confirmed or falsified with file and line; the 8 tests one line each, (a) or (b), old → new; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-315`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-315 | Report: docs/worklogs/SG-315_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
