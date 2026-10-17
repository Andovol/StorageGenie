# SG-203 — Density toggle measured on both states: every load-bearing number holds, but the report overstates the AA sample total 2× (490 vs 245), rated 96

Immutable audit: base `8bcbee2` -> work `7bbdc35` (evidence only: driver sha `757f05c8`, 5 worlds x 2 states, 23 shots, measure JSON) -> report/paste `2abe8a7`. Local `--ff-only` to the exact report HEAD (`2abe8a7` == origin/automation). Trigger exit 0; engine status `report_unreadable ... reason=report_missing`. Against that: the CODER's receipt note `Dispatch-ID: SG-203 | Report: docs/worklogs/SG-203_report.md | Work-HEAD: 7bbdc35...` IS on the remote (`SG-203_receipt.log`: push `0cecfae..5b6a0d5`, mapped-fetch read-back `show_exit=0`). Per `DISPATCH.md` §2 the failure condition is receipt-based: receipt present -> NOT failed. **Sixth ISS-4 instance** (SG-202 was the fifth). No re-trigger; no debug slice.

Scope: every changed path under `docs/worklogs/SG-203*` (12 files: driver, controls JSON, measure JSON, 4 logs, health, receipt, worklog, report, 23 JPEGs). No product/config/test/lockfile/schema/migration change. Read-only lane-CDP + driver-side loopback fulfillment; zero denials; no restart/deploy; DB/storage untouched (health `{"status":"ok","db":"ok","storage":"ok"}` start 12:11:17Z + end 12:20:57Z). Contract 0.50.0 == expectation (`/home/andrei/storagegenie-contract/CODER.md` line 3; RULES.md sha `49338e39…` == `RULES.sha256`).

Holistic rating: **96/100**, no flag. **One deduction (attribution `coder`):** the report states "49 text samples per world/state (**490 total**)" for table-cell AA (report §(c), fact line 3). The measure JSON holds **245** `passesAA` records — 49 per **TABLE** state × 5 table states; grid states carry no table cells (`tableContrast` appears 5×, once per table state, `gridContrast` 0). The **conclusion is unaffected** (0 below AA; mins verified below), but the total is an overstatement not supported by its own artifact (`G-A3`). `slowest_waste` = `none` (recon/contract/build/driver-authoring, controls+density runs and the two repairs, merge+analysis+23-image read+report — every phase's output used).

## Evidence accepted (independently parsed from `SG-203_measure.json`, not copied from the report)

- **Harness frozen:** `harness.sha256` = `757f05c8351f6a18bf189ccde1362685589aab6e896e5371d005a76e148e0faf` == the report's driver sha. Every run re-executed on this one sha after the repairs.
- **Controls 26/26**, exit 0, `controls_rc=0`; every must-fail arm observably failing (contrast wrong 5.0, tap wrong 99, zoom wrong 700, dark wrong `light`; `density_toggle_wrong_expectation_must_fail` computed false -> NOT held). One **failed prove execution** (`density_toggle_keyboard_returns_grid`, CDP `rawKeyDown` Enter did not fire the native button) repaired with a material change (`keyDown` + `\r`) and re-run green; failed transcript preserved verbatim in `SG-203_worklog.log` (CO-63, not reconstructed). Focus-probe refinement (`ringVsOwnBgRatio` 1.0 artifact -> `ringVsSurroundingBgRatio` against the parent chain) disclosed and re-run.
- **Grid geometry reproduced (G2 confirmed):** `columnsComputed` `248px 248px 248px 248px` / cards 248x296 / rowCount 2 (light1440, dark1440, light1280); `280.5px 280.5px` (zoom200); `163px 163px` (touch390). No tree finding.
- **Table:** rows 7, `firstRowHeight` 61, `headerRowHeight` 29.5 in all five worlds.
- **Overflow:** `docOverflowX` 0 in every world/state; table container light1440/dark1440/light1280 = client 1052 / scroll 1052, `maxScrollLeft` 0 (not scrollable); zoom200 = 577/838, max 261 reached; touch390 = 342/838, max 496 reached.
- **AA contrast:** `passesAA` true 245 / false **0**; mins 5.2606 (light chip) / 10.4918 (dark chip). Every sample opaque (`bgCompositeAlphaOverTransparent` 1, `partialAlphaLinks` []).
- **Control:** active 9.4611 (bg-primary rgb(110,48,46), weight 600), inactive 5.2606 light / 10.4918 dark; 25px-high target, 4px group gap. **DEFECT (finding, not fixed):** focus ring `ringVsSurroundingBgRatio` 9.8813 light / **1.7559 dark** (`.focus-ring`, `tokens.css:173`) — below 3:1 non-text in dark; named for SG-204.
- **Transport guard:** methods GET 95; `blocked` [] / `blockedExternal` []; `fulfilledFromLoopback` 62; `fulfillFailures` 0; `simulatedFailures` 0; `byteMismatchClock` 0; `byteMismatchUnexplained` 0; `bytesCompared` 112336. Density-harness stdout `loopbackDriverGets` 126 (report figure confirmed in `SG-203_density_run.log`); controls stdout 57.
- **Masking:** UUID-shaped-run grep over every committed SG-203 artifact = **0**; blur + U+25A0+U+200B post-measurement, layout-safe.
- **All 23 screenshots opened by this audit** (`D425`): light1280 + touch390 + zoom200 + the remaining light/dark 1440 states opened here in full (10 in the prior pass, 13 now). Dispositions: no clipping, no overlap, no broken layout, no data anomaly on any of the 23; 1440/1280 tables show all seven columns; zoom200/touch390 tables clip at the container edge and scroll (touch `table_scrolled` shows right-hand columns + container scrollbar); zoom shots show the collapsed Menu + 2-up reflow; dark shots legible; dark focus close-up visually confirms the low-contrast ring. Masked names render as U+25A0 runs; item images blurred; categories/dates visible (product metadata, masking scope respected).
- **A4 receipt:** bound lane notes-ref; push + mapped-fetch read-back verified; report commit follows evidence commit.

## Dispositions

| Item | Destination |
|---|---|
| Density facts (table 4.9× denser than grid per item; 838px column need vs 1052 fit / 261–496px scroll; both states AA-clean; control resets to grid on navigation) | **Feeds SG-204** (D-6 density proposal) |
| Dark-theme focus ring 1.7559:1 (`.focus-ring`, `tokens.css:173`) | **SG-204** (option/token fix; named, not fixed here) |
| Active-weight-600 width jitter (~5.75px), "None yet" toolbar wrap at 1280, sticky header+toolbar 150–390 CSS px at narrow/zoom | **SG-204** (UI observations) |
| AA sample total stated 490 vs actual 245 | **Deduction recorded** here (report inaccuracy; conclusion unaffected) |
| Auth-live + live-container rendering | Blocked, stated (no credentials/host grant) |
| Native zoom + physical-device touch | Emulated only, disclosed (SG-199 emulation carried) |
| Runner `report_unreadable` misfire, 6th instance | Desk #84 (no re-trigger) |
| Full backend suite untouched/unrun | No product in scope (stated); 2 env rows stand to Launcher provisioning |

Harness context-size reading unavailable; no conclusion made.
