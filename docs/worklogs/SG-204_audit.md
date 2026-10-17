# SG-204 — D-6 density proposal delivered: 4 grounded options + 4 real-page renders, rated 98 (packet premise errors caught by the Coder)

Immutable audit: base `42f248a` -> work `3724232` (evidence only: proposal doc + driver copy + 4 option JPEGs + measure JSON + logs) -> report/receipt `c34fee4`. Local `--ff-only` to the exact report HEAD (`c34fee4` == origin/automation). Trigger exit 0; engine status `report_unreadable ... reason=report_missing`. **Seventh ISS-4 instance.** Against that: the CODER's receipt note `Dispatch-ID: SG-204 | Report: docs/worklogs/SG-204_report.md | Work-HEAD: 3724232...` IS on the remote (`git notes --ref=refs/notes/storagegenie-coder-reports`, read back by this audit). Per `DISPATCH.md` §2 the failure condition is receipt-based: receipt present -> NOT failed. No re-trigger; no debug slice.

Scope: 15 files, ALL under `docs/proposals/2026-10-17-density-*` (the document, the driver copy, the 4-option renders dir) + `docs/worklogs/SG-204*` (report, receipt, logs, controls JSON, measure JSON). **Zero product/config/test/lockfile/schema/migration change** — verified by name-only diff `42f248a..c34fee4` (the only non-`docs/...` paths are none; the two families above are the entire delta). Read-only lane-CDP + driver-side loopback fulfillment; zero denials; no restart/deploy; health `{"status":"ok","db":"ok","storage":"ok"}` start 12:39:47Z + end 12:43:32Z. Contract 0.50.0 == expectation (live `/home/andrei/storagegenie-contract/CODER.md` line 3; RULES.md sha `49338e39…` == `RULES.sha256`).

Holistic rating: **98/100**, no flag. **No slice-side deduction.** The one failed exercise execution (`priv.scrub is not a function` in the driver copy's new `--renders` path) was self-caught by its own run, repaired with a material change, and **all four renders + the controls re-run on one frozen driver sha `7e3c7067`** — the proof discipline working (`CO-35`), not a deduction. `slowest_waste` = `none` (recon/premises/driver authoring, build, controls+renders, evidence+document+report — every phase's output used).

**Packet premise errors, caught and recorded by the Coder (`PG-IC-09`; packet-side, `F-SG204-1`):** the packet cited `frontend/src/styles/tokens.css:173`; the actual path is **`frontend/src/theme/tokens.css:173`** (`.focus-ring:focus-visible`, same line — verified independently here). Also `CatalogToolbar.tsx` labels at `:13` (packet `:14`), density control `role="group"` at `:168` (packet `:170`); `ProductGrid.tsx` table branch `:331` (packet `:330`). Numbers agree; the document records the actual paths. Recorded, not bent.

## Evidence accepted (independently parsed, not copied from the report)

- **Driver identity:** the proposal's driver copy `docs/proposals/2026-10-17-density-driver.mjs` hashes to `7e3c70675fa77b675fd9d97cf7e28f410977a5af5d4f3985d087b8ca0b69f089` == the report's claim. `docs/worklogs/SG-203_driver.mjs` is **untouched** (not in the delta; LF-normalized sha `757f05c8…` intact) — the copy-not-edit ceiling was honoured.
- **Factual base is grounded:** every one of the 8 factual-base lines cites its source artifact + section (`SG-203_measure.json` / `SG-203_report.md` / `SG-199_report.md`). The SG-203 AA-total error was **corrected** in the document (item 3 states 245, 49×5, citing `SG-203_audit.md`) — the Coder read the audit dispatched at the same base.
- **Options:** leave-it + 3 real options, each with name / what changes / GIVES / COSTS / measured fact / render. Leave-it, the dark focus-ring defect (`tokens.css:173`) and the native default-button off-token item (`SG-199_report.md:14`) are present as options 1-3; option 4's missing requirement is marked **"owner must specify"**, not invented. **No recommendation, no owner voice** — grep confirms only the two negation sentences.
- **Renders opened by this audit (`D425`), all 4:** option-1 real grid baseline (4-up, 2 rows, single toolbar row); option-2 dark 2× close-up with the injected ring clearly visible and meeting the neighbour edge without overlap; option-3 dark Analytics with the injected themed face (dark-on-light-text, page otherwise unchanged, numbers consistent 7 total/0 signals); option-4 real table state, 7 columns fit 1052 px, no horizontal scroll. No clipping, no overlap, no broken layout, no data anomaly on any. Changed-option renders are labelled simulations with the exact injection quoted.
- **Simulation effects measured, not asserted:** option-2 `ringVsSurroundingBgRatio` 1.7559 -> 7.4784 (own-face 1.0 -> 4.2589); option-3 face `rgb(239,239,239)`/`rgb(0,0,0)` -> `rgb(28,26,24)`/`rgb(245,245,244)`, height 21 -> 25 px (geometry shift disclosed). Verified in `SG-204_measure.json`.
- **Controls 26/26**, exit 0, same frozen sha, every must-fail arm observably failing (contrast 5.0, tap 99, zoom 700, dark `light`, toggle wrong-expectation NOT held).
- **Transport guard:** methods GET 37; `blockedExternal` []; `requestCount` 37; `fulfilledFromLoopback` 25; `byteMismatchClock` 1; `byteMismatchUnexplained` **0**.
- **Failed run preserved verbatim** in `SG-204_renders_run.log` (`render 4 ERROR TypeError: priv.scrub is not a function`, then the green re-run), not reconstructed.
- **A4 receipt:** bound lane notes-ref; note present + read back; report commit follows evidence commit.

## Dispositions

| Item | Destination |
|---|---|
| Density proposal (4 options + renders + factual base, no recommendation) | **DELIVERED to the owner this turn** with the Architect's recommendation (D-6) |
| Dark focus-ring defect (`theme/tokens.css:173`, 1.7559:1 dark) | Option 2 in the proposal (decision to owner); still OPEN as a defect |
| Native default-button off-token in dark | Option 3 in the proposal (decision to owner) |
| Packet premise errors (wrong tokens.css path, `:14/:170/:330` drifts) | Recorded here (`F-SG204-1`, packet-side); no score deduction |
| Runner `report_unreadable` misfire, **7th instance** | Desk #84 (no re-trigger) |
| Auth-live + live-container; native zoom / physical touch | Blocked / emulated-only, stated |
| Option 4 threshold/persistence/scope | UNSPECIFIED by design — "owner must specify" before any implementation slice |
| No option implemented | By design (proposal step only) |

Harness context-size reading unavailable; no conclusion made.
