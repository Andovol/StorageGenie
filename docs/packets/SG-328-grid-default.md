# SG-328 — The catalog always opens in Standard Grid (owner directive); the width rule is retired

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner, 2026-11-16: *"The standard grid should be the default view."* Stage C (*"d14 ok"*, L3).

**Tier: MINOR** (`CODER.md` §11): one default value and the code that computes it; no storage, privacy, write, route or production surface. One targeted test FAIL → PASS plus the full gate; a short report.

## Why this exists

The catalog opens in *Compact Table* when its content column is 860 px or wider (`frontend/src/routes/CatalogPage.tsx:38-52` `CATALOG_TABLE_FIT_MIN_PX` / `resolveInitialDensity`, applied in the mount `useLayoutEffect` at `:69-75`; SG-212, D-21). The owner wants *Standard Grid* every time. Hypotheses (`PB-1`): the state already starts as `"grid"` (`:65`), so removing the width rule and its effect is the change; `measureContentColumnWidth` and `contentColumnRef` may have no other use — establish it, and remove only what nothing else reads. The toggle (`components/shell/CatalogToolbar.tsx`, `DENSITY_LABELS`) is unchanged: *Compact Table* stays one click away. Older tests asserting the width rule (`components/catalog/catalog.test.tsx`, grep `860` / `resolveInitialDensity` / table-at-wide) are updated, each named, old → new.

| ID | Change |
|---|---|
| **G1** | The catalog opens in *Standard Grid* at every width (test at a wide content column, e.g. 1280 px, and a narrow one); *Compact Table* still switches to the table and back. |

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-328-scratch/docker-config output/SG-328-scratch/logs output/SG-328-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-328-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-328/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-328-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-328-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-328/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-328-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-328-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — The change

**Write the test first and run it (FAIL), then change `CatalogPage.tsx` and run it again (PASS)**; log names and first assertion to `docs/worklogs/SG-328_fail.log` and `SG-328_pass.log`. Test file `frontend/src/sg328-grid-default.sg328.test.tsx`, fed **the shape the API sends** (copy from an existing catalog test that uses the API client). One commit `SG-328 G1: …` holding the change, its test and the older tests updated. Before committing, run every older test file that renders the catalog.

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg328*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-328_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — G1 done with file and line; every wrong premise named; what was removed and why nothing else reads it.
- **A3** — The test FAIL before, PASS after; logs named.
- **A4** — Gate green with exact counts; the named files twice green.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like the table on a wide first render, a toggle that no longer switches, a test that never sets a width, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** the files named above, the ones you establish instead (named, with why), new `*.sg328.test.tsx`, older tests only where they assert the width rule.
- **Any backend file, any other product file, any style rule outside the controls named** is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈450 s (`UNVERIFIED — my estimate`: one small change plus SG-328's gate ≈300 s).

## Report

Destination: `docs/worklogs/SG-328_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; the change with file and line; each premise confirmed or falsified; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-328`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-328 | Report: docs/worklogs/SG-328_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
