# SG-302 report — Pantry warning text in dark, every pair measured, Capture link, dark shots

Slice SG-302 · model opencode-go/muse-spark-1.3-contributor · effort xhigh (from process args `opencode run --model opencode-go/muse-spark-1.3-contributor --variant xhigh`) · cwd /home/andrei/StorageGenie · remote git@github.com:Andovol/StorageGenie · BASE ref origin/automation → resolved cc1ec9270ea3fadf68210aa629325b53ead7de74 · WORK_HEAD: the report commit (HEAD at publish; see the git note).

Contract: `Rule-set version recorded here: 0.58.0` (`AGENTS.md:4`, echoed as received). The contract folder was not read (denial expected, not a STOP).

## Time

- Budget: ≈900 s expected; stop rule 1300 s (RUN_BUDGET_S 2100 s). Elapsed 1794487612 → 1794488585 ≈973 s.
- G0 preflight: 1794487612 → 1794487619 ≈7 s (`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-302/docker.sock`, `docker version` Server ok, `busybox` rc 0; `backend/venv/bin/python` 3.12.3; `curl 8003` 200 `{"status":"ok","db":"ok","storage":"ok"}`).
- G1 fix: 1794487629 → 1794487696 ≈67 s (grep, token calc, test authoring, two edits).
- G2 FAIL: 1794487673/1794487683 (3 failed, base); PASS: 1794487702/1794487730 (3 passed, candidate).
- G3 gate: 1794487751 → 1794488051 ≈300 s (eslint rc 0 1794487768, tsc rc 0 1794487772, build rc 0 1794487784/1794488051, backend 1794487904→1794487988 84 s, frontend 1794487991→1794488007, three-files twice 1794488012/1794488017).
- G4 scratch: 1794488068 → 1794488579 ≈511 s (migrate 1794488119/1794488123, scratch build 1794488128→1794488131 with `VITE_API_BASE`, backend 18302 PID 321913→326742→329769, frontend 14302 PID 322042, seed 14 items 1794488173, chrome PID 322595 port 37223, shots 1794488406→1794488418 + empty 1794488462, stop 1794488568, `rm -rf output/SG-302-scratch` 1794488579). Health end 1794488585 200. No `pkill -f` used; kills by PID only.

## Premises (PB-1, falsified first)

- `--link` equals `--primary` in light, differs in dark — **confirmed** from `frontend/src/theme/tokens.css:9` (`--primary: 2 41% 30.6%`), `:14` (`--link: 2 41% 30.6%`), `:51` (`--primary: 2 41% 30.6%` dark), `:54` (`--link: 2 41% 72%`, SG-118 comment `~7.5:1 on card, ~8.3:1 on background`). Computed (HSL→sRGB): light `rgb(110,48,46)` both, ratio 8.69 on paper light `rgb(244,240,232)`; dark link `rgb(213,156,154)` ratio 7.36 on paper dark `rgb(32,27,23)`, 8.31 on body `rgb(15,14,13)`; dark primary `rgb(110,48,46)` ratio 1.73 on paper, 1.95 on body. If `--link` had failed 4.5:1 I would have chosen another hue value and said why — it passes, so no new token.
- Surface the tile text sits on — **paper, not body**. Page sets `--paper` (`PantryPage.tsx:327` `backgroundColor: hsl(var(--paper))`); tile article has no background. DOM-read effective background of `[data-testid=pantry-expired]` in dark is `rgb(32, 27, 23)` (dark `--paper`), while `body` is `rgb(15, 14, 13)` (`proof_full.json: expiredBgDark1280`, `bodyBgDark`). Measured against `rgb(32,27,23)` throughout.
- `.text-link` exists (`tokens.css:142-144` `color: hsl(var(--link))`) — **reused the token** via inline `hsl(var(--link))` (same value, keeps the file's inline-style pattern; light computed colour identical by token equality, DOM light `rgb(110,48,46)` both).

## G1 how met

1. Warning text ≥4.5:1 dark: grep `var(--primary)` in `PantryPage.tsx` found exactly 2 uses — `:196` EXPIRED label, `:204` accent time-left line — both switched to `hsl(var(--link))` (`replaceAll`, verified `rg` shows only `--link` at 196/204/396). Light computed `rgb(110,48,46)` identical to base (token equality `2 41% 30.6%` both; DOM light proof `expiredColorLight375: rgb(110, 48, 46)`). Dark computed `rgb(213,156,154)` on `rgb(32,27,23)` = 7.36:1 (DOM-read, §contrast). No other `--primary` text on this page.
2. Empty Capture link: `No food yet. Add an item from Capture…` now contains `<Link to="/capture" className="focus-ring" style={{color:"hsl(var(--link))", textDecoration:"underline"}}>Capture</Link>` (`PantryPage.tsx:392-399`; `Link` already imported). DOM dark `href=/capture color=rgb(213,156,154) deco=underline bg=rgb(32,27,23)`; light `href=/capture color=rgb(110,48,46) deco=underline` (`read_empty_link.mjs`). Focus outline via existing `.focus-ring:focus-visible { outline: 2px solid hsl(var(--link)) }`. Sentence otherwise unchanged.
3. Every pair measured: `docs/worklogs/SG-302_contrast.md` lists heading, subtitle, count, unsorted line+link, section headings, tile name, time-muted/accent, EXPIRED, quantity, No-photo, action buttons, notice+Put back, empty+link, tile error — light+dark fg/bg from DOM, ratio, size, pass. All rendered pairs pass (lowest 5.32 light muted, 7.36 dark accent). Error text not rendered in normal DOM → REMAINING, not fixed (outside scope: no error triggered).

Scope kept: product only `PantryPage.tsx`; no `tokens.css` change (link sufficed); no backend/migration/Docker/compose/lockfile/dependency/`.env`/host/provider/deploy bytes; `frontend/dist` untouched (mtime check via build `outDir` in scratch).

## G2 FAIL-then-PASS

- New `frontend/src/routes/PantryPage.sg302.test.tsx` (3 tests: EXPIRED `var(--link)` not `var(--primary)`; accent time-left `var(--link)`; empty Capture link `href` ends `/capture`).
- FAIL on base `docs/worklogs/SG-302_fail.log`: 3 failed — `EXPIRED label… → expected '…hsl(var(--primary));' to contain 'var(--link)'`; `accent time-left… → expected '…hsl(var(--primary));' to contain 'var(--link)'`; `empty Capture… → Unable to find role="link" and name "Capture"`. First FAIL run also hit `Found multiple elements by [data-testid=pantry-expired]` (Use soon + Everything grids); test fixed to `findAllByTestId` before the clean FAIL quoted here. `SG-302_fail_full.log` is the superseded early run.
- PASS on candidate `docs/worklogs/SG-302_pass.log`: 3 passed (165 ms).
- No SG-300/SG-273 test asserted `--primary` on these elements (`rg primary|--link` in both files: no hits) — none updated, each named here as not requiring update.

## G3 full gate (candidate, before screenshots)

1. `ruff check` on backend changed: none — `docs/worklogs/SG-302_ruff.log` states `no backend file changed… not run (expected none)`.
2. `eslint` on changed frontend files: `frontend/node_modules/.bin/eslint src/routes/PantryPage.tsx src/routes/PantryPage.sg302.test.tsx` rc 0, empty log `SG-302_eslint.log`; `tsc --noEmit` rc 0 `SG-302_tsc.log`; `vite build --outDir ../output/SG-302-scratch/build` rc 0 `SG-302_build.log` (`1970 modules`, `index-MeuNWAvj.js 356.78 kB`); `frontend/dist` untouched.
3. `make backend-test`: `docs/worklogs/SG-302_backend-test.log` — host `805 passed, 2 deselected, 59 warnings in 75.65s`; image `2 passed, 6 deselected in 1.88s`; rc 0. Pre-existing mypy reds out of scope (not run as gate here beyond `ruff none`).
4. `make frontend-test`: `docs/worklogs/SG-302_frontend-test.log` — `44 passed (44), 396 passed (396) in 15.33s`; rc 0 (SG-300 was 43/393; +1 file +3 tests). Pre-existing `App.household-nav.test.tsx` eslint error untouched (not in changed files).
5. Three files twice: `SG-302_threefiles_run1.log` + `run2.log` — each `3 passed (3), 27 passed (27)` (sg302 3 + sg273 5 + sg300 19); rc 0 both. No red; no base-only rerun needed; no STOP.

## G4 shots + contrast (after gate)

Scratch only: `DATABASE_URL=sqlite:////…/output/SG-302-scratch/scratch.db` (+`scratch_empty.db`), `STORAGE_ROOT=…/storage` (`…_empty`), `SG_PROVIDER_ID=fake`, migrations via `backend/venv/bin/python -m alembic upgrade head` (head `20261102_sg279_candidate_state`), seed 14 items (Juice −5d, Cheese −3d, Milk −1d, Yogurt 0d, Apples 1d, Eggs 3d, Bread 5d, Oats/Rice/Pasta later, Ketchup/Soup dateless, Old Soup gone, Wrench unsorted), backend `127.0.0.1:18302`, frontend scratch build `VITE_API_BASE=http://127.0.0.1:18302` (`ui/index-g1_1qR9Z.js` contains `127.0.0.1:18302`, no `localhost:8003`) served on `127.0.0.1:14302`, headless Chrome via CDP (`WebSocket`, no install). Backend needed `CORS_ORIGINS=http://127.0.0.1:14302` for the direct bundle (without it: `Could not load households: Failed to fetch`); first three Use-soon shots retaken once after the fix (allowed once). Never 8003/live container/stored files. Clicks + DOM reads via Node in scratch. Servers stopped by PID (`kill 329769 322042 322595`; `ps -p` RC 1 each; `curl 18302/14302` 000). `rm -rf output/SG-302-scratch` RC 0 (`ls output/` → `dispatch` only).

| Shot | Theme/width | sha12 | bytes | proving DOM text + label colour |
|---|---|---|---|---|
| Pantry Use soon | dark 1280 | 7beb2d8005da | 302754 | `11 ITEMS`; Use soon `CheeseEXPIREDExpired 3 days ago…MilkEXPIREDExpired yesterday…` (Juice gone after notice); EXPIRED `rgb(213,156,154)` on `rgb(32,27,23)` |
| Pantry Use soon | dark 375 | 03d2456b7a36 | 114654 | same Use soon (Cheese…Bread); EXPIRED `rgb(213,156,154)` |
| Pantry Use soon | light 375 | e0dd18e15335 | 114070 | same Use soon; EXPIRED `rgb(110,48,46)` on `rgb(244,240,232)` (light unchanged) |
| Pantry notice | dark 375 | 3e506593d834 | 111434 | `Juice used up · Put back` (`pantry-notice`); EXPIRED at notice `rgb(213,156,154)` |
| Pantry empty | dark 375 | ea0b32585cc4 | 26575 | `0 ITEMS`; `No food yet. Add an item from Capture…`; Capture `href=/capture rgb(213,156,154) underline` |
| Pantry empty | light 375 | 718aecfea113 | 26288 | same empty; Capture `href=/capture rgb(110,48,46) underline` |
| Catalog Gone | dark 1280 | d9f337ee6b06 | 44278 | `Gone — used up` (2); `Old Soup listed` |

Distinct-hash: `sha256sum *.png | awk '{print substr($1,1,12)}' | sort -u | wc -l` → 7; 7 files → quoted equal, no two share a hash. `INDEX.md` holds the table. Contrast summary: 16 rendered pairs + 1 REMAINING (tile error, no error state rendered); all rendered pass (dark min 7.36 accent/EXPIRED/empty-link; light min 5.32 muted/No-photo; large headings ~15.6).

Changed files: `frontend/src/routes/PantryPage.tsx` (2 colour tokens + empty link, +11/−3); `frontend/src/routes/PantryPage.sg302.test.tsx` (new); evidence `docs/worklogs/SG-302_fail.log`, `SG-302_pass.log`, `SG-302_ruff.log`, `SG-302_eslint.log`, `SG-302_tsc.log`, `SG-302_build.log`, `SG-302_backend-test.log`, `SG-302_frontend-test.log`, `SG-302_threefiles_run1/2.log`, `SG-302_contrast.md`, `SG-302_shots/` (7 png + `INDEX.md` + `proof_full.json` + `proof_empty.json`); `SG-302_fail_full.log` (superseded early FAIL, kept for honesty).

UNCLEAR: tile error-text ratio (no error rendered in scratch; token-only, not claimed); the stray `/tmp/sg302_pass_raw.txt` from an early `tee` (lane denies `/tmp`; I did not remove it — `rm` outside workspace is denied to this runtime — quoted here instead of hidden). REMAINING: none in product; error-text measurement only.

Constraints: PB-1 premises established from file + DOM (above); PB-2 preflight proven (Server section, rc 0, health 200/200, venv python, no privileged op); PB-3 vacuity checked — dark ratio <4.5 would have failed (measured 7.36), light change would have failed (measured identical `110,48,46`), Capture as plain text would have failed (now link `href=/capture`), missing pair would have failed (table lists all +1 REMAINING), typed-from-token would have failed (all from `getComputedStyle`), shared hash would have failed (7/7 distinct), scratch bundle pointing at 8003 would have been STOP (contains 18302, no 8003), red suite would have stopped (all green), second-run flake would have failed (both runs 27/27); none observed. PB-4/5/6 bound (`PB-1–PB-6 bind`, `PB-7` full suites ran). No second-opinion trigger (no 🟠/🔴). No deploy/restart (rider SG-303 follows).

A1 enumerated 2 accent uses, dark 7.36:1 on measured `rgb(32,27,23)`, light identical `rgb(110,48,46)` quoted. A2 Capture link `/capture`, link colour, underline, focusable (`focus-ring`). A3 contrast table DOM-read, all pass or REMAINING with owner (none). A4 FAIL on base / PASS on candidate logged, no old test updated. A5 ruff none, eslint/tsc clean, build rc 0, backend 805+2/image 2+6, frontend 44/396, three files twice 27/27. A6 7 shots with hash/size/proving text/label colour, 7/7 distinct, servers by PID stopped, scratch removed by exact path. A7 scope as ceiling (only `PantryPage.tsx` + new tests; `tokens.css` untouched; zero backend/migration/Docker/compose/lockfile/dependency/`.env`/live/host/provider/container/deploy; `frontend/dist` untouched). A8 preflight proven, health 200/200, phase seconds from stamps. A9 vacuity checked, none observed. A10 below.

Verification: PASS
