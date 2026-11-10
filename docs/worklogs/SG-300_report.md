# SG-300 report — Pantry design fixes (SG-273 audit I1–I4)

Slice SG-300 · model opencode-go/claude-haiku-5-5 · effort UNCLEAR (not in this runtime; not read from process args) · cwd /home/andrei/StorageGenie · remote git@github.com:Andovol/StorageGenie.git · BASE ref origin/automation → resolved 36be113bc6e28262dbe690147b045a73b84ea8af · WORK_HEAD: the report commit (HEAD at publish; see the git note).

Contract: `Rule-set version recorded here: 0.58.0` (AGENTS.md, echoed as received). The contract folder was not read.

## Time
- Budget: ≈1000 s expected; stop rule 1300 s. Elapsed ≈ 900 s by the stamps (start 1794345949).
- G0 preflight: 1794345949 → 1794345970 ≈ 20 s (I2 removal at 1794345959).
- G1 implementation and tests written: ≈ 1794345970 → 1794346185 ≈ 215 s.
- G2 FAIL run 1794346084 → 1794346094 (10 s); PASS run 1794346191 → 1794346194 (3 s), after three test-authoring fixes (see G2).
- G3 static (eslint+tsc+build) 19 s; `make backend-test` 118 s (1794346207 → 1794346325); frontend suite 25 s; the three-file set twice 4 s each.
- G4 scratch build+migrate+backend+seed ≈ 1794346420 → 1794346440; shots 1794346509 → 1794346521 (12 s); catalog DOM proof 3 s; empty state shot ≈ 1794346565. A shell call hung for ≈200 s on a teardown command (`pkill -f` matched its own command line); the servers and Chrome were stopped afterwards (verified: ports 18300/14300 closed, no scratch processes).

## I2 (A1)
`ls -la output/SG-273-scratch` listed it (chrome profiles, `.cache`, `.config`, `hold`, `docker-config`, `dispatch` untouched). `rm -rf output/SG-273-scratch` by exact path. `ls output/` afterwards: `SG-300-scratch`, `dispatch`.

## Preflight (G0, A8)
Preflight copied as given: `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-300/docker.sock`; socket present; `docker version` showed the Server section (29.9.2); `docker run --rm busybox true` rc 0. Venv `python` is a symlink to /usr/bin/python3 (Python 3.12.3) and was used; nothing installed. Health `curl -s http://127.0.0.1:8003/v1/health` → 200 at start, and 200 at end (`{"status":"ok","db":"ok","storage":"ok"}`).

## G1 — how each line was met
1. **Order.** `sortPantryItems` in PantryPage.tsx: smallest `days_remaining` first (most overdue first), then soonest, dateless last, ties by name. Used for Use soon and Everything. DOM order at 1280 and 375: Juice (−3), Cheese (−1), Milk (1), Yogurt (2), Apples (3), Eggs (5), Bread (7).
2. **Time left.** `pantryTimeLeftText(days, expiry_date, todayYear)` reads `days_remaining` from the engine rows (`ExpiryStatusRow`, the same figure the Expiry page shows). No new date calculation. Phrases: 0 → "Use today"; 1 → "Use by tomorrow"; 2..14 → "Use in N days"; 15+ → "Use by 25 Nov" (year only when not the `as_of` year); −1 → "Expired yesterday"; −N → "Expired N days ago"; none → "No date". Accent (`--primary`) when days ≤ 2 (`data-accent="true"`). The EXPIRED label is literal DOM text in the spaced-label class. **Note:** "Expired today" is never produced, because the packet's edge set puts 0 at "Use today"; flagged as an interpretation.
3. **Quantity.** One formatter, `quantityLeftText(quantity, unit, counted)` in `frontend/src/lib/quantityText.ts`. `counted` is SG-272's `isCountedUnit` (AMOUNT_UNITS ml, l, g, kg and their names; empty, pcs and any other unit are counted). Counted → "4 left" (no unit); amount → "340 g left"; empty → "No count yet" / "No amount yet". Used in PantryPage's tile, ItemInspectorDrawer (2 places) and AssetDetailPage (2 places). Old "pcs left" text removed from those files.
4. **Subtitle.** "What you have, and what to use first."
5. **Phone.** Track `repeat(auto-fill, minmax(min(150px, calc(50% - 8px)), 1fr))`. DOM: 2 columns at 375 px, 6 at 1280 px (distinct `offsetLeft` count); no horizontal overflow (scrollWidth − innerWidth = 0 at 375; −15 at 1280).
6. **No card.** The tile wrapper has no border, no background, no radius (inline style). Photo is a square with `object-fit: contain` on the paper colour. Name, time left, quantity sit below in the 13 px label scale; separation by the 16 px grid gap. Checked: `borderedWrappers: 0` at both widths.
7. **Even actions.** One flex row at the tile bottom (`margin-top: auto`): counted → "−1" + "Use it up"; amount → "Edit" + "Use it up". Buttons `flex: 1`, `min-height: 40px`, 1 px `--line` border, square corners. **Note:** the 40 px height is set in style; it was not measured in the DOM. The 375 px screenshot shows the rows aligned.
8. **Use it up + notice.** "Use it up" calls `markGone(..., "used_up")` (the `/gone` route). Then a fixed bottom bar `data-testid=pantry-notice` (role=status) reads "Juice used up · Put back" for 6 s; one at a time. "Put back" calls `putBack` (the `/put-back` route); the tile returns (DOM proof `putBackRestoredJuice: true`). Change: the old "Now N left." tile message after −1 was removed because the quantity line now shows it and it broke the even tile rows.
9. **Not sorted yet** keeps its line and link (unchanged).

Label changes: tile "Used up" → "Use it up"; "Edit amount" → "Edit". The item page and drawer keep their own "Use it up" section unchanged.

## G2 — tests (A3)
New: `frontend/src/routes/PantryPage.sg300.test.tsx` (order, time-left edges, accent and EXPIRED, quantity wording, tile border, grid track, subtitle, one-row actions, notice with Put back, notice clears after 6 s), `frontend/src/lib/quantityText.sg300.test.ts` (formatter), `frontend/src/components/shell/ItemInspectorDrawer.sg300.test.tsx` (panel shows "1 left" and "340 g left").
- FAIL on base: `docs/worklogs/SG-300_fail.log` (21 failed; the formatter file failed at import because the module did not exist yet; names and first assertion only).
- Between FAIL and PASS, three test-authoring fixes in the new SG-300 files only: `findAllByTestId` (the tile renders in both Use soon and Everything), `pantry-notice` matched by testid instead of a role name, and a regex for the drawer's "340 g left — change the amount…" line. No product code was changed for these.
- PASS: `docs/worklogs/SG-300_pass.log`: 3 files, 29 tests passed.
- Old tests updated (each named): `frontend/src/routes/AssetDetailPage.sg272.test.tsx:118` "3 pcs left" → "3 left" (the shared wording drops the count unit). `frontend/src/routes/PantryPage.sg273.test.tsx`: test title line 137 and button name line 153 "Used up" → "Use it up"; title line 157 likewise (the tile label changed by line 8).

## G3 — the full gate (A4)
- ruff: no backend file changed; not run (expected none).
- eslint on the 9 changed frontend files: rc 0 (the pre-existing `App.household-nav.test.tsx` error and repo-wide mypy are out of scope; not run).
- `tsc --noEmit`: rc 0.
- Frontend build with outDir in scratch: rc 0. `frontend/dist` untouched (mtime 2026-11-09 20:35:22). **Note:** `frontend/src/api/client.ts` defaults the API base to `http://localhost:8003` (the live port) when `VITE_API_BASE` is unset. The gate build was not served. The scratch bundle was rebuilt with `VITE_API_BASE=http://127.0.0.1:14300` (rc 0; contains 127.0.0.1:14300, no localhost:8003).
- `make backend-test`: rc 0. Host suite: 805 passed, 2 deselected. Image proof: 2 passed, 6 deselected.
- `npm test -- --run` (frontend full): 43 files, 393 tests passed, rc 0.
- The SG-272, SG-273 and SG-300 test files (8 files) run twice in a row: 8 files, 48 tests each run, rc 0 both (`SG-300_sg27x_run1.log`, `_run2.log`).

## G4 — screenshots (A6)
Table with hashes, sizes and DOM proof text: `docs/worklogs/SG-300_shots/INDEX.md`. 12 shots, 12 distinct sha256 prefixes (`sort -u` count 12). Required states: Pantry full 1280/375; Use soon 1280/375; tile after −1 (375); notice after Use it up (375); empty state (375); item panel "1 left" (1280); catalog Gone (1280). Extra dark shots: full 1280, full 375, Use soon 375. Each proof text read from the DOM (quoted in INDEX.md). The catalog Gone view was confirmed by DOM text `Gone — used up` and visually.
Scratch servers stopped (ports 18300 and 14300 closed). Chrome stopped. `output/SG-300-scratch` removed by exact path. The Chrome DevTools port was opened on loopback by Chrome itself (chosen by Chrome, not fixed by us); Chrome needed `--disable-crash-reporter` and XDG dirs inside scratch to start.

## Changed files
Product: `frontend/src/lib/quantityText.ts` (new), `frontend/src/routes/PantryPage.tsx`, `frontend/src/components/shell/ItemInspectorDrawer.tsx` (import + 2 wording expressions), `frontend/src/routes/AssetDetailPage.tsx` (import + 2 wording expressions).
Tests: `frontend/src/routes/PantryPage.sg300.test.tsx` (new), `frontend/src/lib/quantityText.sg300.test.ts` (new), `frontend/src/components/shell/ItemInspectorDrawer.sg300.test.tsx` (new), `frontend/src/routes/PantryPage.sg273.test.tsx` (3 wording edits), `frontend/src/routes/AssetDetailPage.sg272.test.tsx` (1 wording edit).
Evidence: `docs/worklogs/SG-300_*` (fail, pass, eslint, tsc, build logs, backend and frontend logs, stamps, shots folder with PNGs, `INDEX.md`, `proof.json`, and the capture scripts `shoot.mjs`, `shoot2.mjs`, `seed.mjs`).
Not changed: backend, migrations, Dockerfile, compose, lockfile, dependencies, `.env` (none), live database, stored files, host, provider, running containers, deploy, `frontend/dist`, tokens.css.

## UNCLEAR / REMAINING
- UNCLEAR: effort value (not visible in this runtime).
- UNCLEAR: "Expired today" phrase (not produced; see G1 item 2).
- REMAINING: dark Use soon at 1280, dark notice, dark catalog Gone view (not captured separately).
- REMAINING: the 40 px button height was not measured in the DOM.

## Constraints and criteria
- A1 I2: done (exact-path removal; `ls output/` after).
- A2 G1 1–9: done (above); formatter used in the three places.
- A3 G2: FAIL (21 failed) and PASS (29 passed) logged; old tests updated and named.
- A4 gates: ruff none; eslint, tsc, build rc 0; backend 805 passed + image proof 2 passed; frontend 393 passed.
- A5 SG-272/273/300 twice: 48 tests both runs, rc 0.
- A6 shots: 12 with hash, size and DOM text; distinct check 12/12; servers stopped; scratch removed by exact path.
- A7 scope: no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live DB, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched. Scratch API base changed only at build time.
- A8 preflight proven; health 200 at start and end; phase seconds above.
- A9 vacuity: checked for out-of-order Use soon (DOM order), ISO date on a tile (none in DOM text), "pcs left" (none in DOM proof text; tests), one column at 375 (2 columns measured), a bordered tile (0), uneven action rows (visual, plus style), no notice (present), two states with one hash (none, 12/12), proof text not in DOM (all proofs read from DOM), red suite row (none), a test passing once and failing the second time (none: the 3-file set and the 8-file set each ran twice). None observed.
- A10 last line below.

Verification: PASS
