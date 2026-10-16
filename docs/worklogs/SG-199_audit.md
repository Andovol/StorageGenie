# SG-199 — Touch/zoom/dark measured, rated 98 (runner misfired a fourth time, not a slice fault)

Immutable audit: base `714cd12` -> work `d9361ce` (evidence only, 28 shots + driver + measure JSON) -> paste `bcff9e5`. Trigger exit 0; engine status `report_unreadable ... inactive reason=report_missing`. Against that: the CODER's receipt note `Dispatch-ID: SG-199 | Report: docs/worklogs/SG-199_report.md | Work-HEAD: d9361ce...` IS on the remote (note `7075a3f`, pushed in-slice, read back in-slice AND by this audit via notes list). Dual paste note missing (same construction as SG-195/196/198). Fourth ISS-4 instance. Per DISPATCH section 2 the failure condition is receipt-based: receipt present -> NOT failed. No re-trigger; no debug slice.

Local `--ff-only` to the exact paste HEAD (`bcff9e5` == origin/automation). Scope: 38 files, ALL under `docs/worklogs/SG-199*` (zero product/config/test/lockfile change — verified by name-only diff). No restart/deploy; read-only GETs + driver-side loopback fulfillment; fresh temp profiles; no credentials. Contract 0.50.0 == expectation, sha match.

Holistic rating: **98/100**, no flag. No slice-side deduction (attribution empty). The clock-field classifier adaptation is accepted: narrowly allowlisted (JSON + every differing leaf ISO-parseable under `generated_at`), controlled 4/4 both directions, flagged not folded — killing the slice over a server wall-clock field would destroy the facts D-4 ordered. `slowest_waste` = `none` (recon/build, harness authoring incl. 3 material fix cycles, evidence assembly + full re-run — all used).

## Evidence accepted

- Numbers verified in `SG-199_measure.json` by independent parse (not copied from the report): touch overflow 0/6 (clientWidth==scrollWidth==390 all routes); zoom overflow 0/6 at BOTH 100% and emulated 200% (offender lists empty); dark `html.dark` true 6/6, 285 samples, 0 below AA, mins 9.46/9.46/9.18/9.46/9.46/8.31; driver sha `229cffbe` == frozen; guard aggregates GET 62/89/80, fulfilled 38/53/50, failures 0, clock-classified 1/2/1 with leaf evidence, unexplained 0/0/0.
- Controls read in JSON: 22 entries, every must-fail arm observably failing (contrast 5.0, tap 99, zoom 700, dark light); tap fixture event counters prove delivery; spacing fixtures discriminate PASS-SPACING vs FAIL; transport guard proves POST blocked server-side-unseen; byte-compare proves same/equal + diff/different.
- All 28 screenshots opened by this audit (D425): touch 8 (cards 2-up wrap, job list, expanded menu + badge 0, planning, analytics tables, detail stack, alert probes with nav+route alerts in viewport); zoom100 6 (full shell fits 1280, 4-up cards, two-pane inbox); zoom200 6 (collapsed-menu breakpoint as expected, toolbar wraps without overlap, single column, no cut content); dark 8 (legible throughout, badge/alerts readable, toggle sun state). No clipping, no overlap, no unreadable text on any shot. Data consistent single-household state (7 assets, honest badge 0, 0 suggestions); short job ids visible per the metadata disclosure; masking layout-safe (postMask overflow 0).
- Observations for the density proposal: grids already reflow 4->2->1; tables never overflow (row heights 39->78->117 px by world); native button faces render off-token in dark ((a)9, consistent + legible, design input not a failure). No product defect found on any axis — nothing to repair.
- A3: logs + report; 1132 s vs ~1200 s (under); constraints answered; FIRST READ (6-vs-10 route note: packet's enumerated 6 governs) / DURING EXECUTION (4 episodes, each materially repaired) / REMAINING dispositioned; first token SG-199. Density section present with per-route numbers.
- A4: WORK receipt present + read back twice; pushes complete; bound lane receipt, retired finalizer untouched.

## Dispositions

| Item | Destination |
|---|---|
| Touch/zoom/dark facts + density numbers | **DELIVERED** — density proposal with renders goes to the owner this turn (D-4) |
| Runner `report_unreadable` misfire, 4th instance | Recorded here; desk #84 follow-up owed at safe boundary (now 4 instances). No re-trigger |
| Auth-live / container identity / native-zoom / physical touch | Stand (blocked or excluded by design; stated) |

Harness context-size reading unavailable; no conclusion made.
