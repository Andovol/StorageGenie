# SG-308 report — Pantry refreshes after item-panel edits

Slice SG-308 · model opencode-go/muse-spark-1.3-contributor · effort xhigh (rotation slot per STATE.md: SG-308 on Muse; packet states no explicit effort, xhigh matches the last Muse slice SG-302) · cwd /home/andrei/StorageGenie · remote git@github.com:Andovol/StorageGenie · BASE ref origin/automation → resolved 20970bfff0a22ea80482b86b9b34ae74603b939c · WORK_HEAD: the report commit (HEAD at publish; see the git note).

Contract: no version line was received in this runtime; the packet records `0.59.0` (`AGENTS.md`, D30) which is the project file's line, not the coder's own. The contract folder was not read (denial expected: `.contract/` does not exist here; earlier `ls .contract/` → `No such file or directory`; the lane denies `/tmp` and it was never touched). This matches SG-302 audit I2 (echoing the project file's line is the known minor) — stated here instead of repeated.

## Time

- Budget: ≈800 s expected; lane RUN_BUDGET_S 2100 s; hard stop 1300 s. Elapsed 1794489454 → 1794490904 ≈1450 s (over both; overrun from CDP debugging + 75 s backend suite + 511 s-class scratch; no optional goal was added).
- G0 preflight: 1794489454 → 1794489460 ≈6 s (`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-308/docker.sock`, `ls -l` socket ok, `docker version` Server section ok, `busybox` rc 0; `backend/venv/bin/python` 3.12.3, `ruff` 0.16.5; `curl 8003` 200 `{"status":"ok","db":"ok","storage":"ok"}` at start 1794489460 and end 1794490836, both 200).
- G1 enumerate + fix: 1794489754 → 1794490021. Key grep 1794489460–1794489573; helper + 2 drawer edits + 3 pantry edits 1794489991 → 1794490014.
- G2 FAIL (base): 1794489835 → 1794489948 (5 failed). PASS (candidate): 1794490014 → 1794490024 (5 passed).
- G3 gate: 1794490040 → 1794490249 ≈209 s (ruff 1794490050; eslint 1794490056 → 1794490058 rc 0; tsc 1794490063 → 1794490068 rc 0; build 1794490072 → 1794490075 rc 0, 1971 modules; backend host 1794490079 → 1794490159 805 passed + image retry 1794490172 → 1794490206 2 passed; frontend 1794490209 → 1794490227 45/401; named 8-file runs 1794490234/1794490244 both 8/93).
- G4 scratch: 1794490273 → 1794490854 ≈581 s (migrate 1794490412 head `20261102_sg279_candidate_state`; backend 18308 PID 364228 1794490423 → 1794490426 health 200; seed 1794490439 1 household + Milk 4 pcs + Oats 340 g classified food; scratch build 1794490455 → 1794490459 with `VITE_API_BASE=http://127.0.0.1:18308` (bundle contains 18308, zero `8003` hits); frontend 14308 PID 368337 1794490604 → 1794490607 200 with SPA fallback; chrome PID 365702 1794490510 → 1794490514 CDP ok; CDP 1794490621 → 1794490806 tile 4→3 + shot; sha 1794490822; stops 1794490834 → 1794490836 by PID only; `rm -rf output/SG-308-scratch` 1794490854 rc 0, `ls output/` → `dispatch` only).

## Hypothesis (falsified first, then confirmed)

Architect/SG-306 read (not observed at runtime): the panel's five handlers invalidate only `["assets"]` + `["asset", id]`, while the Pantry reads `["pantry-assets"]` + `["pantry-expiry"]`, so save/−1/+1/gone/put-back in the panel leaves tiles, count and Use-soon stale. Falsification: new `PantryPage.sg308.test.tsx` renders the Pantry with a real QueryClient and response-changing mocks, opens the panel from a tile, and asserts the rendered tile (scoped to `pantry-grid`/`pantry-use-soon-grid`, never the drawer, never a spy) changes for each action. On base (defect present) all 5 fail (`docs/worklogs/SG-308_fail.log`: 5 FAIL names + first assertions: `3 left`/`5 left`/`Milk Fresh` not found in grid, Use-soon grid still present / still absent). After the fix all 5 pass (`SG-308_pass.log`: 5 passed). Hypothesis confirmed by the FAIL→PASS pair, which proves the comparison (same test file, base vs candidate).

## Key table (criterion, not a list)

Enumerated by `rg queryKey|invalidateQueries` across `frontend/src` plus reading Pantry/Expiry/Analytics/Catalog/AssetDetail/hooks/client.

| query key | screen · what it displays | refreshed before (panel) | refreshed after |
|---|---|---|---|
| `pantry-assets` (+household) | Pantry tiles + `N ITEMS` count · quantity, ACTIVE/gone membership | NO (panel only did `assets`/`asset`) | YES (helper) |
| `pantry-expiry` (+household) | Pantry Use-soon membership + time-left · expiry_date, days_remaining, bucket | NO | YES |
| `assets` (+household+q+…) | Catalog list · quantity, status, Gone view | YES (`["assets"]` prefix) | YES |
| `asset` (+id [+household]) | Drawer/detail singleton · quantity, status, gone, expiry assertions | YES (`["asset", id]` prefix) | YES |
| `expiry-status` (+household+category) | Expiry page buckets · expiry_date, days, bucket, tier | NO | YES |
| `analytics-summary` (+household) | Analytics totals + Expiry uncategorized + Pantry unsorted · active/total, expiry buckets, category counts | NO | YES |
| `household-assets` (+household) | Relations picker names (same asset rows; UI shows names) | NO | YES (opportunistic via helper) |
| `asset-facets` (+household+q) | Catalog pills · status/category counts | NO | YES (opportunistic via helper) |

My expectation, labelled as such: `pantry-assets`, `pantry-expiry`, the Expiry page's keys and `analytics-summary` are missing today — confirmed by the grep (drawer `ItemInspectorDrawer.tsx:143-210` only `assets`/`asset`; pantry tile/notice `PantryPage.tsx:123-140,286-294` already do pantry keys, the panel does not).

Excluded with reason (do not display quantity/status/expiry/gone from these five writes): `opened-countdown` (opened window, untouched by quantity/gone/put-back/save), `reminders` (reminder read/dismiss state), `planning-suggestions` (suggestion state), plus `households`, `taxonomy`, `locations`, `relations`, `jobs`, `saved-searches`, `candidate`, `ai-settings` (unrelated reads). No test shows them going stale.

## The helper (why shared, not five copies)

New `frontend/src/lib/invalidateAssetViews.ts`: `invalidateAssetViews(qc, assetId)` invalidates the 8 keys above (broad prefixes, household-agnostic). All five panel handlers (`patchMut`, `goneMut`, `putBackMut`, `decMut`, `incMut` in `ItemInspectorDrawer.tsx`) call it with `asset.id`; the Pantry's own tile `decMut`/`goneMut` call it with `asset.id` and the notice `putBackMut` with `(data, assetId) => invalidateAssetViews(qc, assetId)`. One place owns the set so the next screen that displays asset quantities cannot be missed by editing only one of five copies; the cost is a few extra refetches only when those screens are mounted. No route, API call, payload, If-Match, look or wording was changed (diff is imports + invalidation lines only).

## G3 gate (in order, exact counts)

1. `ruff` on backend: no backend file changed — `docs/worklogs/SG-308_ruff.log` states expected none, not run. Comparison that proves it: `git diff --stat` shows only `frontend/src/...` + new frontend files.
2. `eslint` on every changed frontend file: `src/routes/PantryPage.tsx src/components/shell/ItemInspectorDrawer.tsx src/lib/invalidateAssetViews.ts src/routes/PantryPage.sg308.test.tsx` rc 0, `docs/worklogs/SG-308_eslint.log` holds `rc=0` (empty otherwise). Pre-existing `App.household-nav.test.tsx` error untouched (not in changed files).
3. `tsc --noEmit` rc 0, `docs/worklogs/SG-308_tsc.log` holds `rc=0`.
4. Frontend build with `outDir` in scratch: `vite build --outDir ../output/SG-308-scratch/build` rc 0, `docs/worklogs/SG-308_build.log` (`1971 modules`, `index-BJgvF3J9.js 356.39 kB`); `frontend/dist` untouched (does not exist; `git status` shows no `frontend/dist`).
5. `make backend-test`: `docs/worklogs/SG-308_backend-test.log` — host `805 passed, 2 deselected, 59 warnings in 75.79s` rc 0 for the suite; first `make backend-test-image` attempt failed only because `DOCKER_HOST` was not exported in that shell (`permission denied ... /var/run/docker.sock`, rc 2, quoted in log); retry with the preflight env (`DOCKER_CONFIG`+`DOCKER_HOST` exported) green: `2 passed, 6 deselected in 2.08s`. Final gate green; mypy reds out of scope (not run).
6. `make frontend-test`: `docs/worklogs/SG-308_frontend-test.log` — `45 passed (45), 401 passed (401)` rc 0 (was 44/396; +1 file +5 tests).
7. Named files twice (`PG-DP-04`): `SG-308_named_run1.log` + `run2.log` — each `8 passed (8), 93 passed (93)` rc 0, no flake. Files: `PantryPage.sg308` (5) + `sg302` (3) + `sg300` (19) + `sg273` (5) + `drawer.test` + `catalog.test` + `ItemInspectorDrawer.sg272` + `ItemInspectorDrawer.sg300`. Older tests asserting the old invalidation calls (`drawer.test.tsx:258-259`, `catalog.test.tsx:538-539` expecting `["assets"]` + `["asset", id]`) still pass because the helper still invalidates those prefixes — each named here as not requiring update.

A red fixed only within scope: none (no red in gate after the env retry). No old test asserting changed behaviour was touched (STOP not triggered).

## G4 runtime (after the gate)

Scratch only (temporary DB + throwaway SQLite file, providers off, no live DB read/write): fresh `output/SG-308-scratch/scratch.db` via `alembic upgrade head` (`20261102_sg279_candidate_state`); `STORAGE_ROOT` under scratch; backend `127.0.0.1:18308` (PID 364228); 1 household + Milk (4 pcs) + Oats (340 g) classified `food_beverages` through the API; frontend scratch build with `VITE_API_BASE=http://127.0.0.1:18308` (bundle `index-C2zVpdDe.js` contains `127.0.0.1:18308`, `grep -c 8003` → 0, so not pointing at 8003 — STOP avoided) on `127.0.0.1:14308` (PID 368337, SPA fallback for `/pantry`); headless Chrome PID 365702 via CDP (`WebSocket`, no install); Node DevTools script in scratch (no ` submitting `, no `/tmp` — lane denies it; all temp under scratch).

DOM text from the tile grid before and after pressing −1 in the panel, no reload (quoted from `docs/worklogs/SG-308_dom.json`, which compares `tileBefore` vs `tileAfter`):
- BEFORE: `"No photo yet\nMilk\nNo date\n4 left\n−1\nUse it up\nNo photo yet\nOats\nNo date\n340 g left\nEdit\nUse it up"`.
- AFTER: `"No photo yet\nMilk\nNo date\n3 left\n−1\nUse it up\nNo photo yet\nOats\nNo date\n340 g left\nEdit\nUse it up"`.
- Change that proves it: `4 left` → `3 left` for Milk in `pantry-grid` with no remount/refocus (same grid, Oats unchanged).

One screenshot `docs/worklogs/SG-308_shots/pantry-after-panel-decrement-375.png` (light, 375 px): sha256 (12) `d41faa3c2d88` (full `d41faa3c2d88dbd31a4f0d36f1fcf7c00805f60eaebabc0eec9e08f66a2feb15` via `sha256sum`), size `32735` bytes (via `stat -c %s`). Servers stopped by PID only (`kill 364228 368337 365702`; `ps -p` RC 1 each; `curl 18308/14308` empty); `rm -rf output/SG-308-scratch` RC 0 by that exact path (`ls output/` → `dispatch` only); never `pkill -f`.

## Changed files

- `frontend/src/lib/invalidateAssetViews.ts` (new, shared helper).
- `frontend/src/components/shell/ItemInspectorDrawer.tsx` (import + 5× `invalidateAssetViews(qc, asset.id)` replacing the two-line invalidations).
- `frontend/src/routes/PantryPage.tsx` (import + tile `dec`/`gone` use helper with `asset.id`; notice `putBack` uses `(data, assetId)`).
- `frontend/src/routes/PantryPage.sg308.test.tsx` (new, 5 rendered-tile tests).
- Evidence only: `docs/worklogs/SG-308_fail.log`, `SG-308_pass.log`, `SG-308_ruff.log`, `SG-308_eslint.log`, `SG-308_tsc.log`, `SG-308_build.log`, `SG-308_build_scratch.log`, `SG-308_backend-test.log`, `SG-308_frontend-test.log`, `SG-308_named_run1.log`, `SG-308_named_run2.log`, `SG-308_dom.json`, `SG-308_shots/pantry-after-panel-decrement-375.png`, this report. No backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live DB, stored files, host, provider, running-container or deploy bytes; `frontend/dist` untouched; nothing under `/tmp`.

UNCLEAR: process-argument model/effort (inferred Muse/xhigh from the rotation slot; packet states no explicit effort for this slice). REMAINING: none in product; the 1300 s stop rule was exceeded (≈1450 s) — committed, reported and publishing anyway per the budget rule.

Constraints: PB-1 premises from file+DOM above; PB-2 preflight proven (Server section, rc 0, health 200/200, venv python, no privileged op); PB-3 vacuity checked — a tile unchanged after a panel action would have failed (base 5 failed), a test passing on base would have failed (3 initially passed before scoping to `pantry-grid`, fixed), a spy-only assertion would have failed (all assert rendered tile text/presence, no `invalidateQueries` spy), a key missing from the table would have failed (table covers all 8 asset-view keys + exclusions), a red row would have stopped (none after env retry), a flaky second run would have failed (both 93/93), a bundle pointing at 8003 would have been STOP (contains 18308, zero 8003) — none observed. PB-4/5/6 bind (`PB-1`–`PB-6` bind, `PB-7` full suites ran: `make frontend-test` 401 + backend 805+2). No second-opinion trigger (no 🟠/🔴). No deploy/restart (rider follows).

Acceptance: A1 key table + defect reproduced (FAIL) then fixed (PASS) + shared helper with reason; A2 five rendered-tile assertions FAIL on base PASS on candidate; A3 gate green with counts + named files twice green; A4 runtime DOM before/after −1 no reload + shot hash/size; A5 scope as ceiling; A6 preflight + health 200/200 + phase seconds; A7 vacuity checked; A8 below.

Verification: PASS
