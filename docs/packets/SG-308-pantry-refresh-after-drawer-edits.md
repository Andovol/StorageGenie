# SG-308 — Changes made in the item panel opened from the Pantry show on the Pantry at once

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases, plus a throwaway SQLite file under scratch for one runtime check. No live database read or write.
**Restart: none.** No deploy; a rider follows this slice.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo **your own contract's** version line as you received it — not the project file's `Rule-set version recorded here` line (SG-302 audit I2). A denial on that folder is expected and is not a STOP.

**Approval:** stage C (*"d14 ok"*, L3). Ordered by the plan review SG-305/SG-306 (`docs/reviews/review-ledger.md`, 2026-11-12), owner's request for that review: *"Can you review the plan using the 2nd decision model?"*. The review's words: *"isolate the refresh repair as the next small corrective slice with its own rider."*

## Why this exists

The Pantry is live since SG-303. It opens the item panel for a tile (`frontend/src/routes/PantryPage.tsx` ~`:423-428`; amount items offer **Edit** through it, ~`:223-225`). The panel's five success handlers (`frontend/src/components/shell/ItemInspectorDrawer.tsx` ~`:139-210`: `patchMut`, `goneMut`, `putBackMut`, `decMut`, `incMut`) invalidate only `["assets"]` and `["asset", asset.id]`. The Pantry reads `["pantry-assets", household]` and `["pantry-expiry", household]` (~`:255-268`). **Hypothesis (Architect's read and SG-306's, not observed at runtime):** after a save, −1, +1, gone or put back in the panel, the Pantry's tiles, count and Use soon membership stay stale until something else refetches. **Falsify it first:** reproduce it in a failing test; if you cannot, say so with evidence and stop after G1.

The Pantry's own tile buttons already invalidate its keys (~`:123-140`, `:286-294`) — they are not the defect.

## G1 — The fix, the smallest that is right

- **Criterion, not a list:** every query that displays an asset's quantity, status, expiry date or gone state must be refreshed after each of the panel's five actions. **Enumerate those query keys yourself** across `frontend/src` (the Pantry's two, the catalog's, the Expiry page's, the analytics summary if it counts items, any other) and report the table: key · screen · refreshed before · refreshed after. My expectation, labelled as such: `pantry-assets`, `pantry-expiry`, the Expiry page's keys and `analytics-summary` are missing today.
- Prefer one shared helper (for example `invalidateAssetViews(qc, assetId)`) used by all five handlers and by the Pantry's own handlers, over five copies. Say why if you choose otherwise.
- **Do not change** routes, API calls, payloads, the If-Match header, any screen's look or wording.

## G2 — Tests, FAIL-then-PASS, observable, not spies

In `frontend/src/routes/PantryPage.sg308.test.tsx`: render the Pantry with a real `QueryClient` and a mocked API whose responses change after each mutation; open the panel from a tile; for **each of the five actions** assert the **rendered tile** changes without remount or refocus (for example *"4 left"* → *"3 left"* after −1 in the panel; the tile leaves Use soon after gone; returns after put back; a new amount after save; *"5 left"* after +1). **An assertion only that `invalidateQueries` was called does not satisfy this** (SG-306). Logs `docs/worklogs/SG-308_fail.log`, `SG-308_pass.log` (`PG-EV-09`), FAIL logs holding names and first assertion only, **no other FAIL log**.

## G3 — The full gate, once, on the candidate

In order, exact counts (`PG-IC-08`), each into `docs/worklogs/SG-308_<step>.log`: `ruff` on any backend file (expected none); `eslint` on every changed frontend file; `tsc --noEmit`; the frontend build with `outDir` in scratch (`PG-SC-12`); `make backend-test` once; `make frontend-test` once; the SG-308, SG-302, SG-300 and SG-273 test files and any catalog or Expiry test touching the panel, twice consecutively (`PG-DP-04`). Pre-existing `eslint` error in `App.household-nav.test.tsx` and the mypy reds are out of scope. A red is fixed only within scope; an old test asserting behaviour this slice did not mean to change is a **STOP and report**.

## G4 — One runtime check, after the gate

Scratch app as SG-302 did (fresh SQLite under `output/SG-308-scratch/` by the project's migrations, a few food items through the API, providers off; backend `127.0.0.1:18308`; frontend scratch build **with `VITE_API_BASE=http://127.0.0.1:18308`** on `127.0.0.1:14308` — a bundle pointing at 8003 is a STOP). Through a Node DevTools script (built-in `WebSocket`, no install): open the Pantry, open a counted item's panel, press −1 in the panel, and **read the tile's text from the DOM before and after without reload** — quote both. One screenshot `docs/worklogs/SG-308_shots/pantry-after-panel-decrement-375.png` (light) with its sha256 (12) and size. Stop servers by PID, never `pkill -f`; remove `output/SG-308-scratch/` by that exact path. **No `/tmp`**: the lane denies it; any `tee` or temporary file goes under the scratch path.

## Acceptance criteria

- **A1** — The key table; the defect reproduced (or falsified with evidence); one shared helper or the reason for not.
- **A2** — Five rendered-tile assertions FAIL on base, PASS on candidate.
- **A3** — Gate green with counts; the named files twice green.
- **A4** — Runtime DOM text before and after the panel's −1, no reload; the shot with hash and size.
- **A5** — Scope as below; zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes; `frontend/dist` untouched; nothing written under `/tmp`.
- **A6** — Preflight proven; health 200 at start and end; phase seconds from `date +%s` stamps.
- **A7** — `PB-3` vacuity: a failure would look like a tile unchanged after a panel action, a test passing on base, a spy-only assertion, a key missing from the table, a red row, a flaky second run, a bundle pointing at 8003. Say which you checked.
- **A8** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## G0 — Preflight

Copy these lines exactly:

```
mkdir -p output/SG-308-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-308-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-308/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-308/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for make and `ruff`; a missing venv `python` is a STOP. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. **Run `date +%s` at the start of every goal and gate step.** `output/` itself and `output/dispatch` are never touched.

## Scope ceiling

- **Product:** `frontend/src/components/shell/ItemInspectorDrawer.tsx`; `frontend/src/routes/PantryPage.tsx` (only to use the shared helper); a new helper file under `frontend/src/lib/` or `frontend/src/api/`. Any other product file is a STOP and report (`PG-EV-03`).
- **Tests:** new `*.sg308*` files; older tests only where they assert the old invalidation calls, each named.
- **No backend file.** Reads of any file are allowed.
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the frontend build, scratch servers on `127.0.0.1:18308` and `:14308`, the project's migrations on a scratch file, headless Chrome, a Node DevTools script in scratch. No install, no other image or port.
- Evidence: `docs/worklogs/SG-308*` only. No deploy, restart or touch of the running container, its image tag, the live database or the stored files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **300 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; scratch server start **60 s** each; one screenshot **60 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **At 1300 s elapsed by your stamps, stop, commit, write the report, publish.** **There is no optional goal.** Order: G0, G1, G2, G3, G4. Expected ≈800 s (`UNVERIFIED — my estimate`: SG-302, a two-line fix with a 16-pair table and 7 shots, took ≈973 s; this has a five-path test and one shot).

## Report

Destination: `docs/worklogs/SG-308_report.md`, evidence beside it. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: elapsed against ≈800 s and every phase's seconds; the hypothesis confirmed or falsified; the key table; the helper; each gate step's counts; every red and what was done; the runtime DOM text and shot; changed files; your contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint and criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-308`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-308 | Report: docs/worklogs/SG-308_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
