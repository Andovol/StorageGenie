# SG-308 audit — the Pantry now refreshes after item-panel edits; Muse ran ≈150 s past its 1300 s hard stop

**Score 84/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` from the trigger (the report **inferred** both from the rotation instead of reading process arguments — `PB-4`). Diff `20970bf..71ef059`: `frontend/src/lib/invalidateAssetViews.ts` (new), `ItemInspectorDrawer.tsx`, `PantryPage.tsx`, a new test file. **Elapsed ≈1450 s by its stamps**, against ≈800 s expected and **the 1300 s hard stop**. Read: the whole report, the helper, the drawer diff, FAIL log, gate tails, engine status (`result=done published_head=yes`). **Opened the one shot.**

## Checked independently

- **Helper:** one function, eight prefix invalidations (`pantry-assets`, `pantry-expiry`, `assets`, `asset`+id, `expiry-status`, `analytics-summary`, `household-assets`, `asset-facets`); all five panel handlers now call it (diff: five two-line blocks replaced by one call each).
- **FAIL on base:** `SG-308_fail.log` — 5 failed, each a rendered-tile assertion (*"Unable to find … 3 left"*, *"… 5 left"*, *"Milk Fresh"*, the grid not null after gone); no spy.
- **Gate:** frontend `45 passed (45)`, `401 passed (401)`; named files twice `8 passed`, `93 passed`; host 805 + 2 deselected; image 2.
- **Runtime:** `SG-308_dom.json` before `4 left`, after `3 left`, same grid, no reload.

## What holds

The hypothesis reproduced, then fixed with the smallest right change: one shared helper instead of five copies, with the excluded keys named and reasoned. The key table found two more stale views than I expected (`household-assets`, `asset-facets`). Old tests asserting the old calls still pass because the helper keeps those prefixes. `VITE_API_BASE` set, bundle checked for no `8003`, PIDs stopped, scratch removed, no `/tmp`.

## Findings

I1. **Hard stop breached: ≈1450 s against 1300 s.** The packet: *"At 1300 s elapsed by your stamps, stop, commit, write the report, publish."* It disclosed the overrun but did not stop at the line; publishing before the 2100 s budget saved the run. **Muse's second stop-rule breach** (SG-271 run 1). **Attribution: mixed** — Coder (did not stop); packet (my ≈800 s estimate was low: one runtime DOM check cost ≈581 s of scratch app, CDP debugging included). **Flag to the owner and the desk.**

I2. **Model and effort inferred, not read** (`PB-4`). The engine's trigger is the authority (`effort=xhigh`). Coder.

I3. **The screenshot proves little by eye:** the open item panel covers the tile; only *"3 le…"* shows behind it. The DOM read is the proof and it holds. Packet (asked for one shot without saying the panel must be closed).

I4. **Image proof first failed** because `DOCKER_HOST` was not exported in that shell; retried green. Coder, ≈35 s.

Seen in the shot, for SG-307: the item panel says *Kind of item: Uncategorized* for a food item, *"Bounding-box overlay omitted…"*, cut-out tabs and rounded fields — all already in SG-307's scope.

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** stop-rule breach (Coder) on an under-estimated packet.
- **Root cause:** a full scratch app for one runtime check is ≈500–600 s on this lane (SG-302 ≈511 s, SG-308 ≈581 s); the estimate counted it as small.
- **Correction:** none needed in the product; the work is correct and published.
- **Recurrence guard:** Muse packets set the hard stop at **1100 s** (≈1000 s of margin to the 2100 s budget), and estimates count ≈550 s for any scratch-app phase.
- **Owner impact:** ≈1450 s; no product harm.

## Model note

Muse's seventh rotated slice: correct, well-reasoned work (the shared helper, a fuller key table than asked, a test that failed for the right reason) — and its second hard-stop breach. Pattern so far (`docs/coder-profiles.md`): Muse keeps stop rules when finishing with margin (SG-302 973 s) and breaks them when a phase runs long (SG-271 run 1, SG-308).

`slowest_waste`: ≈581 s G4 scratch app for one DOM check, CDP debugging included.
