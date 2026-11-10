# SG-300 — Pantry design fixes from SG-273's audit, honest screenshots, and the server scratch removed

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases, plus throwaway SQLite files under scratch for the screenshot app. No live database read or write.
**Restart: none.** No deploy; a rider follows this slice.
**Provider: none.** No key, no `.env`, no spend; the screenshot app runs with every provider off.

**Contract:** recorded `0.58.0` (`AGENTS.md`). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line as you received it. A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-10, D27 (*"Both approved."*): SG-300 fixes SG-273's audit findings I1–I4. Stage C (*"d14 ok"*, L3); D18 (the tandpfun look on the Pantry view). The owner: *"design, look and feel are very important, so hold every screen to that."*

## Why this exists

SG-273 (`def73a6..e68b14c`) built `/pantry` and passed the full gate, but its audit (`docs/worklogs/SG-273_audit.md`, rated 78 with a trust flag) found, from its own screenshots:

- **I1** — three "state" shots were byte-identical to the full page (sha256 `108328073e84…`, `114a41403581…`), yet were reported as showing the −1 state.
- **I2** — `output/SG-273-scratch/` was left on the host.
- **I3** — design faults listed in G1.
- **I4** — shots missing: empty state, Use soon dark and 375 px, a tile at 375 px, the catalog's Gone view.

**The Pantry code** is `frontend/src/routes/PantryPage.tsx` (expected; verify): `pantryUseSoonBucket` (~`:39`), `pantryQuantityText` (~`:43`, returns `${quantity}${unit} left`), `pantryDateText` (~`:50`), `PantryTile` (~`:54`, bordered at ~`:110`), the grid `minmax(165px, 1fr)` (~`:34`), the subtitle (~`:299`), the *Used up* label (~`:219`). The expiry rows come from `fetchExpiryStatus` and carry `asset_id`, `expiry_date` and `bucket` (~`:264–270`); **establish** whether they also carry days remaining or overdue (the Expiry page shows *"1 day overdue"*, *"2 days remaining"* — `frontend/src/routes/ExpiryPage.tsx`), and reuse that, never a second date calculation if one exists. The same *"pcs left"* wording comes from `ItemInspectorDrawer.tsx` and `AssetDetailPage.tsx` (SG-272).

## G0 — Preflight

Copy these lines exactly:

```
mkdir -p output/SG-300-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-300-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-300/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-300/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make and `ruff` call; a missing venv `python` is a STOP — install nothing. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch only in `output/SG-300-scratch/`. **Run `date +%s` at the start of every goal and gate step and quote the stamps**; the report gives each phase's seconds from them.

**I2 first:** `ls -la output/SG-273-scratch` (quote it), then `rm -rf output/SG-273-scratch` — that exact path, nothing else — and show `ls output/` afterwards. `output/` itself and `output/dispatch` are never touched.

## G1 — The Pantry, to the owner's bar

Each line is a requirement; the report says how each was met.

1. **Use soon in urgency order:** expired first (most overdue first), then soonest. **Everything** sorts the same way, with dateless items last, then by name.
2. **Dates as time left**, from the engine's figures: *"Expired today"*, *"Expired yesterday"*, *"Expired 3 days ago"*; *"Use today"*, *"Use by tomorrow"*, *"Use in 5 days"* up to 14 days; beyond that *"Use by 18 Nov"* (short month, no year unless it is not this year). No date → *"No date"*. **Expired and ≤ 2 days** take the accent colour (`--primary`); the rest stay muted ink. An expired tile also carries a small uppercase **EXPIRED** label in the same spaced-label style.
3. **Quantity wording:** a counted item (unit empty, `pcs`, or a count unit — **establish** which units SG-272 treats as counted) reads *"4 left"*, *"1 left"*; an amount reads *"340 g left"*. Empty: SG-272's *"No count yet"* / *"No amount yet"*. **Use one shared formatter** and use it on the Pantry tile, in `ItemInspectorDrawer.tsx` and in `AssetDetailPage.tsx`, so *"1 pcs left"* is gone everywhere.
4. **Copy:** the subtitle reads *"What you have, and what to use first."* No sentence about tiles or packs.
5. **Phone:** **two columns at 375 px**, five or more at 1280 px, no horizontal scroll. The grid track is `repeat(auto-fill, minmax(min(150px, calc(50% - 8px)), 1fr))` or your equivalent — prove the column count at both widths in a test or from the shots.
6. **Photos straight on the paper:** no card box, no border, no white tile background. The photo is a square (`object-fit: contain` on the paper colour); the name, time left and quantity sit below it in the label scale. Separation comes from spacing (the grid gap), not lines.
7. **Even tiles:** the actions sit in **one row** at the tile's bottom edge on every tile: counted → **−1** and **Use it up**; amount → **Edit** and **Use it up**. Square buttons with a 1 px `--line` border are fine (tandpfun's joined square tabs); at least 40 px tall for a thumb.
8. **Use it up** is the label (an action); it sets gone with reason *used up* through SG-272's `/gone` route, as now. **After it, a notice** at the bottom of the screen: *"Milk used up · Put back"*, for about 6 seconds; **Put back** calls SG-272's `/put-back` route and the tile returns. One notice at a time.
9. **Not sorted yet** keeps its line and link.

**Do not change** the Pantry's data rules (what enters, the engine's window), SG-272's routes, or any other screen beyond the formatter swap in line 3.

## G2 — Tests, FAIL-then-PASS

In `frontend/src/routes/PantryPage.sg300.test.tsx` (and beside the formatter): order (expired before soonest, dateless last); each date phrase at its edges (0, 1, 2, 14, 15 days, −1, −3); the accent at ≤ 2 days and the EXPIRED label; *"1 left"* / *"4 left"* / *"340 g left"* through the shared formatter, and the item panel rendering *"1 left"*; no element with a border on the tile wrapper; the notice appears after Use it up and Put back calls the route; the subtitle text. Logs `docs/worklogs/SG-300_fail.log`, `SG-300_pass.log` (`PG-EV-09`); **FAIL logs hold the failing names and first assertion only.** An SG-273 or SG-272 test asserting the old wording (*"Used up"* on the tile, *"pcs left"*) is updated here, each named.

## G3 — The full gate, once, on the candidate (before any screenshot)

In order, exact counts (`PG-IC-08`), each into `docs/worklogs/SG-300_<step>.log`:

1. `ruff check` on any backend file changed (expected: none).
2. `eslint` on every frontend file changed; `tsc --noEmit`; the frontend build with `outDir` in scratch so `frontend/dist` is untouched (`PG-SC-12`). The pre-existing `eslint` error in `App.household-nav.test.tsx` and the repo-wide mypy reds are out of scope.
3. `make backend-test` once — host suite green, the two marked tests deselected, the image proof passing.
4. `make frontend-test` once.
5. Every SG-300, SG-273 and SG-272 frontend test file twice consecutively (`PG-DP-04`).

**A red is fixed here only if** the fix stays in this slice's scope and changes nothing another slice built beyond line 3's wording. An old test that fails is run alone on the base (`D443`); one asserting behaviour this slice did not mean to change is a **STOP and report** with names and the first assertion.

## G4 — Screenshots, after the gate — required

Run the app **only on scratch**, exactly as SG-273 did (`docs/worklogs/SG-273_shots/INDEX.md`): a fresh SQLite file under `output/SG-300-scratch/` made by the project's migrations, test data through the API (about a dozen food items with generated test images, counted and amount items, one expired, several due within 2 and 7 days, some later, one dateless, one unsorted, one gone), every provider off; backend `127.0.0.1:18300`, frontend from the scratch build on `127.0.0.1:14300`. For the **empty state**, a second scratch database with a household and no food. Never port 8003, never the live container, never the stored files.

**A state that needs a click** (the catalog's Gone view, the notice after Use it up) is driven by a small Node script in scratch speaking the Chrome DevTools Protocol to the headless browser (Node's built-in `WebSocket`; no package install). A state made through the API (−1) is made before the shot.

Capture into `docs/worklogs/SG-300_shots/`, light and dark:

| Shot | Widths |
|---|---|
| Pantry, full page | 1280, 375 |
| Pantry, Use soon in view | 1280, 375 |
| Pantry, a tile after −1 | 375 |
| Pantry, the notice after Use it up | 375 |
| Pantry, empty state | 375 |
| Item panel showing *"1 left"* | 1280 |
| Catalog, Gone view | 1280 |

**Proof per shot, all three required:** its sha256 (first 12 characters) and size; **no two shots of different states share a hash** — check it and quote the check; and in `docs/worklogs/SG-300_shots/INDEX.md`, the **on-screen text that proves the state** (for example *"Milk · 1 left"* after −1, *"Milk used up · Put back"* for the notice, *"EXPIRED"* on the cheese). **Confirm that text by reading the page's DOM through the same DevTools session, not from memory**, and quote it. A shot that fails its proof is retaken once, then reported as failed — never described as showing what it does not. Stop the scratch servers and show they are gone; **remove `output/SG-300-scratch/` by that exact path at the end** (the shots are already in `docs/`).

## Acceptance criteria

- **A1** — I2: `output/SG-273-scratch` listed, removed by exact path, `ls output/` after.
- **A2** — G1 lines 1–9 each met, the report saying how; the shared formatter used in the three places.
- **A3** — G2 tests FAIL on base, PASS on candidate, logged; any old test updated is named with its reason.
- **A4** — ruff (none expected), eslint, tsc clean; build rc 0; backend suite green with image proof; frontend suite green; counts quoted.
- **A5** — SG-300, SG-273, SG-272 frontend test files green twice consecutively.
- **A6** — Every shot in the table with hash, size and DOM-confirmed proving text; the distinct-hash check quoted; servers stopped; scratch removed by exact path.
- **A7** — Scope as below; zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes; `frontend/dist` untouched.
- **A8** — Preflight proven; health 200 at start and end; phase seconds from the stamps.
- **A9** — `PB-3` vacuity: a failure would look like Use soon out of date order, an ISO date on a tile, *"pcs left"* anywhere, one column at 375 px, a bordered tile, uneven action rows, no notice, two states with one hash, proving text not in the DOM, a red suite row, a test passing once and failing the second time. Say which you checked; none observed.
- **A10** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/src/routes/PantryPage.tsx`; a new shared quantity formatter (for example `frontend/src/lib/quantityText.ts`); `frontend/src/components/shell/ItemInspectorDrawer.tsx` and `frontend/src/routes/AssetDetailPage.tsx` **for the formatter swap only**; `frontend/src/theme/tokens.css` only if a token is needed.
- **Tests:** new `*.sg300*` files; SG-272 and SG-273 frontend tests only where they assert the old wording, each named.
- **No backend file.** **Any other product file is a STOP and report** (`PG-EV-03`). Reads of any file are allowed.
- **Authorised runtimes:** the preflight, the `make` gates, the tests, `eslint`, `tsc`, the frontend build, **the scratch servers on `127.0.0.1:18300` and `:14300`, the project's migrations on scratch files, headless Chrome, and a Node DevTools script in scratch.** No package install, no other image, no other port.
- Evidence: `docs/worklogs/SG-300*` only. No deploy, no restart, no touch of the running container, its image tag, the live database or the stored files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **300 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; scratch server start **60 s** each; one screenshot **60 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **At 1300 s elapsed by your `date +%s` stamps, stop whatever you are doing, commit, write the report, publish.** A stop rule, not a target. **There is no optional goal.** Order: G0 (with I2), G1, G2, G3, G4 in the table's order. A stop inside G4 leaves the rest `REMAINING`, never described as done. Expected ≈1000 s (`UNVERIFIED — my estimate`: SG-273 took 1277 s for a new screen, its gate and 17 shots; this is a smaller change with 13 shots and a DevTools script).

## Report

Destination: `docs/worklogs/SG-300_report.md`, evidence beside it. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: elapsed against ≈1000 s and every phase's seconds from the stamps; how each G1 line was met; each gate step's counts; every red and what was done; the shot table with hashes and proving text; changed files; the contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint and criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-300`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-300 | Report: docs/worklogs/SG-300_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
