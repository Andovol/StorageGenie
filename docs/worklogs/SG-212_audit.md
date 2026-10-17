# SG-212 audit — D-21: width-adaptive density default (content-fit ≥860 px), rated 98

Immutable audit: base `c27beab` → work `f54449a` (2 product files, +247/−50) → evidence `c371b34` (19 files) → report `a0e1d58` → receipt `e6ba4a3`. Local `--ff-only` to the exact tip (`e6ba4a3` == origin/automation at pull); tree clean. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-212 | Report: docs/worklogs/SG-212_report.md | Work-HEAD: c371b34...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Fifteenth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Product diff** (`c27beab..f54449a -- frontend/`, 2 files ONLY): `CatalogPage.tsx` gains the `CATALOG_TABLE_FIT_MIN_PX = 860` rule, `measureContentColumnWidth` + `resolveInitialDensity` helpers, a `contentColumnRef` (`data-testid="catalog-content-column"`) wrapping the grid/table region, and a mount-only `useLayoutEffect` (pre-paint by React guarantee); default `useState` stays `"grid"` (safe side). `catalog.test.tsx` gains the 4-row width-adaptive describe. No persistence anywhere (no storage/API/URL writes — enumeration confirms); toggle untouched post-mount.
- **FAIL-then-PASS (both committed raw):** failpre = new describe vs base → 4 failed / 33 skipped, rc=1 (failures are the rows: missing read point ×3, grid-default ×1); focused pass → 4 passed / 33 skipped, rc=0; full suite ONCE on candidate → `29 passed (29) / 297 passed (297)` (base 29/293 + exactly the 4 new rows — reconciled here). `tsc` rc=0. Boundary rows pin 860→table / 859→grid; unreadable (NaN, 0) → grid; getter-called assertions prove the rule read the column; remount row + no-density-key assertion prove recompute-no-persist.
- **Served smoke (both worlds, frozen driver `b46781eb`, rc=0 both):** wide1440 opens TABLE (content 1052 ≥ 860, 7 rows, maxScrollLeft 0, docOverflowX 0); touch390 opens GRID (content 342, 7 cards, docOverflowX 0 — the 3 "hScrollOffenders" are ellipsis-clipped name spans, clip not scroll, finding 5, accepted analysis); CDP toggle both directions through the real control with state assertions. Served bytes == build hashes (JS `04c9e2e2`, CSS `c3b58cda` unchanged — no CSS delta). 12 API GETs per world, 0 non-GET.
- **Screenshots — all 4 opened by this audit (D425):** initial-table (7 columns, Compact pressed, no h-scrollbar), after-grid (Standard pressed, 4-up, no overflow), after-table (back in table, identical), touch390 grid (2-up, Menu collapsed, wrapped toolbar, no h-scroll). Masking holds on all (names U+25A0, images blurred); no clipping, overlap, broken layout, or data anomaly. Finding 4's mask-coverage harness defect: found by the Coder opening superseded shots, repaired (re-mask per capture), all runs re-executed on the frozen sha, unmasked shots deleted never committed — lane-local only, nothing exfiltrated (zero external calls), disclosed. Process note, not a product finding.
- **Enumeration:** single density-default site (the changed `useState`); 6 files / 31 density references accounted; persistence sites `sg-theme` + `household_id` only (no density key anywhere — asserted in tests and greps); URL persistence `household_id`-only. Delta: none beyond the changed site.
- **Pre-existing eslint red** (`App.household-nav.test.tsx:2` unused `fireEvent` — proven at base via HEAD-pipe, finding 3): NOT this slice (file untouched here; vitest unaffected). Disposition: OPEN, parked — bundles with the next slice that touches test files. (Root note: SG-208 rewrote that file without lint in its gates; the gap is packet-scoping, not a defect to chase alone.)
- **Scope:** 19 evidence + 2 product files, all under the two allowed roots; grep-gated file list. **Contract:** 0.50.0 echoed with live proof. **Elapsed:** 489 s vs ≈600 s (under). No command over 60 s. Health identical.

## Rating

**Holistic: 98/100, no flag.** Rule implemented exactly as decided (threshold/edge/unreadable/remount rows), served proof on both widths with opened screenshots, harness defect self-found and repaired on a frozen driver, pre-existing lint proven-not-mine and parked honestly. `deduction_attribution`: empty (nothing deducted; finding 2's `:168` drift was no-consequence). `slowest_waste`: `none` (every phase's output used, incl. the diagnostic revisions). Guards: PG-EV-02/03/05/08/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-01/03.

## Dispositions

| Item | Destination |
|---|---|
| D-21 values PROVED on the served page (1052→table/no-scroll, 342→grid/no-overflow, toggle both ways) | Serve rider after SG-213 (product unserved; standing directives own it) |
| Pre-existing eslint unused-import (test file) | OPEN, parked — rides the next test-touching product slice |
| Runner `report_unreadable`, **15th instance** | Desk #84 (no re-trigger) |
| SG-213 (D-18(b) Google retry, $2 cap) | **Dispatched this turn after push** (packet already committed; L3 flow) |

Harness context-size reading unavailable; no conclusion made.
