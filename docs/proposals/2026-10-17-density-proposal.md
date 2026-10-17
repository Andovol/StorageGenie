# 2026-10-17 — Density proposal: real options with renders (SG-204)

Proposal step only (owner D-6, 2026-10-17): **no density system is implemented before an option is
picked.** This document changes no product bytes; every option below is presented with what it gives
and what it costs, on the measured facts, with no recommendation.

- Sources of the factual base: `docs/worklogs/SG-203_report.md` and `docs/worklogs/SG-203_measure.json`
  (the executed grid/table toggle measurement), `docs/worklogs/SG-199_report.md` (touch/zoom/dark
  measurement), audited at `docs/worklogs/SG-203_audit.md` / `docs/worklogs/SG-199_audit.md`.
- Renders: produced from the **real Catalog on the lane harness** (served build of the tree at BASE
  `42f248a`, driver `docs/proposals/2026-10-17-density-driver.mjs` sha256 `7e3c7067…`, run log
  `docs/worklogs/SG-204_renders_run.log`, measure `docs/worklogs/SG-204_measure.json`), privacy-masked;
  every render was opened and dispositioned for UI + layout + data issues (per-render line below).
- The measured control (re-verified on target): `Density = "grid" | "table"` at
  `frontend/src/components/shell/CatalogToolbar.tsx:5`; labels `:13-15`; props `:44-45`; control
  `:168`; default `useState<Density>("grid")` at `frontend/src/routes/CatalogPage.tsx:40`; grid
  breakpoints `frontend/src/components/catalog/ProductGrid.tsx:15-18`; table branch `:331`.
- Path finding (PB-1): the packet cites `frontend/src/styles/tokens.css:173`; the tree path is
  `frontend/src/theme/tokens.css:173` (same line content `.focus-ring:focus-visible`). Numbers agree.

## Factual base — the measured facts this turns on

Each line cites the artifact and section it was read from.

1. **Table density.** Grid cards render 248×296 px (4 tracks, gap 20 px; 7 items = 2 rows = 612 px of
   column height); table rows render 61 px each (7 rows = 457 px; header row 29.5 px) and add
   Category/Status/Added/Actions columns. The table is **~4.9× denser per item vertically** (61 vs 296).
   Source: `SG-203_measure.json` → `phases.density.worlds[light1440].grid.measure.gridTarget`,
   `.table.measure.tableTarget`; `SG-203_report.md` §"facts for the SG-204 proposal".
2. **Horizontal fit.** The table's 7 columns need **838 px** of content. The content column is
   **1052 px** at 1440/1280 → the table fits with no scroll (`container clientWidth 1052 = scrollWidth
   1052`, `maxScrollLeft 0`, reached 0). At the 200 %-zoom emulated world (577 px) the table scrolls
   horizontally by **261 px** (reached 261); at touch 390 (342 px) by **496 px** (reached 496). The grid
   never scrolls horizontally (`docOverflowX` 0 in every world/state). Source: same records, worlds
   `light1440`, `light1280`, `zoom200`, `touch390`.
3. **Contrast.** Table cells: 49 samples per table state × 5 table states = **245 samples, 0 below AA**
   (min 5.2606 light / 10.4918 dark). Density control: active 9.4611 both themes; inactive 5.2606 light
   / 10.4918 dark. Source: `SG-203_measure.json` → `phases.density.worlds[*].table.measure.tableContrast`
   and `.densityControl`. (Ledger: the SG-203 report text says 490; the audit `SG-203_audit.md` corrected
   the count to 245 — 49 × 5; the conclusion is unaffected.)
4. **Control behaviour.** The control defaults to grid and resets to grid on every fresh navigation
   (`CatalogPage.tsx:40`; **no persistence measured or claimed**), is operable by mouse and by touch tap
   in both directions with `aria-pressed` signalling, is 25 px high (≥ 24, PASS-SIZE) with a 4 px gap at
   touch (group 221.16×25). Source: `SG-203_report.md` §(c) A1; `SG-203_measure.json` → density worlds.
5. **Dark focus-ring defect (found by SG-203, not fixed).** The keyboard focus ring is 2 px solid
   `rgb(110,48,46)` offset 2 px — **`ringVsSurroundingBgRatio` 9.8813 light / 1.7559 dark** against its
   surrounding toolbar (below the 3:1 non-text contrast used for focus indicators). Shared `.focus-ring`,
   `frontend/src/theme/tokens.css:173`; app-wide, not density-specific. Re-verified on target by SG-204:
   before-injection readings `rgb(110,48,46)`, own-face 1.0, surrounding 1.7559 (dark).
   Source: `SG-203_measure.json` → `phases.density.focusProbes[light1440|dark1440]`;
   `SG-204_measure.json` → `renders[option 2].ringBefore`.
6. **Native default-button faces off-token in dark (measured input).** `SG-199_report.md:14` records
   that native default button faces (`Choose files`, `Take a photo`, `Run planning`, `Generate summary`,
   `Choose Files`) "render light-on-dark in dark theme — consistent, legible, but visually off-token".
   SG-204 re-measured the Analytics instance on target: `Generate summary` has no class attribute,
   computed background `rgb(239,239,239)` vs text `rgb(0,0,0)` — a light face in the dark theme
   (`lightFaceInDark: true`). Source: `SG-199_report.md:14`; `SG-204_measure.json` →
   `renders[option 3].buttonsBefore`.
7. **UI observations carried for this proposal.** Active label weight 600 widens the active segment by
   ~5.75 px with the group total roughly constant (221.17 → 221.16 — internal jitter on every toggle);
   at 1280 the toolbar wraps "None yet" onto a second row; at narrow/zoom worlds the sticky header
   consumes ~150–390 CSS px of the viewport. Source: `SG-203_report.md` §(a)10.
8. **Narrow-width ranking.** The table is the less usable state at narrow widths by measurement
   (needs 261–496 px of horizontal scroll); the grid needs none (`docOverflowX` 0 everywhere).
   Source: `SG-203_report.md` §"facts for the SG-204 proposal".

Demographic of the measured world: one household, 7 assets, fresh temp browser profile per invocation,
read-only GETs fulfilled from the loopback API; the same content appears in every render below.

## Options

Each option states: name — what changes — what it GIVES — what it COSTS — the measured fact it rests
on — the render filename. Renders changed by an option are **driver-injected simulations on the real
page**, labelled as such; the exact injection is quoted. No recommendation is made anywhere in this
document.

### Option 1 — Leave it (baseline)

- **Name:** Leave it.
- **What changes:** nothing. The grid/table toggle stands exactly as measured.
- **What it GIVES:** grid is the default with no horizontal scroll in every measured world; the table
  is one control press away (4.9× denser per item); both states measured AA-clean; the 25 px target
  passes size at touch.
- **What it COSTS:** the measured items stay as they are: the dark focus ring stays at 1.7559:1
  (item 5), native default-button faces stay off-token in dark as recorded (item 6), and the density
  choice still resets to grid on every fresh navigation (item 4).
- **Measured fact it rests on:** items 1–4 (density, fit, AA, control behaviour).
- **Render:** `docs/proposals/2026-10-17-density-renders/option-1-leave-it-baseline-grid-1440.jpg`
  — the shipped default state (grid, 1440 light), nothing injected. The toggle's second state is the
  committed SG-203 shot `docs/worklogs/SG-203_shots/light1440_table.jpg` (reused by reference).
- **Owner checklist:** [ ] accept / [ ] decline.

### Option 2 — Dark focus-ring token fix

- **Name:** Dark focus-ring token fix (candidate from the SG-203 defect).
- **What changes:** the `.focus-ring:focus-visible` outline colour (`frontend/src/theme/tokens.css:173`)
  gains a dark-adapted tint — e.g. a dark-theme override or a dedicated ring token, following the
  existing token pattern (the simulation uses the existing `--link` dark tint `hsl(2 41% 72%)`).
  The implementation shape is open; the class is shared, so the change is app-wide.
- **What it GIVES:** a keyboard focus indicator that clears the 3:1 non-text contrast bar in dark —
  simulated readings on target: **7.4784** against the surrounding toolbar, 4.2589 worst case against
  the focused button's own face (light unchanged at 9.8813).
- **What it COSTS:** a shared-token change — every `.focus-ring` surface needs re-verification in both
  themes; the dark ring becomes a second `--primary`-family tint (visual divergence from the light
  ring colour).
- **Measured fact it rests on:** item 5 — SG-203 dark 1.7559 vs light 9.8813, re-verified on target
  1.7559 before injection.
- **Injection (exact, simulation):**
  `html.dark .focus-ring:focus-visible { outline-color: hsl(var(--link)); }`
- **Render:** `docs/proposals/2026-10-17-density-renders/option-2-dark-focus-ring-fix.jpg`
  — 2× close-up of the real focused "Standard Grid" control in dark with the injected ring; **a
  simulation of the option, not shipped behaviour.**

### Option 3 — Native default-button token alignment in dark

- **Name:** Native default-button token alignment (the SG-199:14 measured item, named not invented).
- **What changes:** the faces recorded at `SG-199_report.md:14` (unclassed native buttons, e.g. the
  Analytics "Generate summary" face) receive the themed control treatment — e.g. the
  `THEMED_CONTROL_CLASS` treatment in source, or a token rule for unclassed buttons in dark. The
  implementation choice is open.
- **What it GIVES:** no light native faces in the dark theme; visual consistency with the themed
  control surfaces (`THEMED_CONTROL_CLASS`); the simulated face reads `rgb(28,26,24)` on
  `rgb(245,245,244)` after the change instead of `rgb(239,239,239)` on `rgb(0,0,0)`.
- **What it COSTS:** touches surfaces beyond the density control (app-wide review of native buttons);
  geometry may shift slightly (simulated: button height 21 → 25 px, width 130.08 → 133.27 px because of
  the padding the treatment carries); light theme unclassed faces are not addressed by the simulated
  dark-scoped rule.
- **Measured fact it rests on:** item 6 — `SG-199_report.md:14` plus the SG-204 on-target re-measure
  (`lightFaceInDark: true`, face `rgb(239,239,239)`).
- **Injection (exact, simulation):**
  `html.dark button:not([class]) { background-color: hsl(var(--card)); color: hsl(var(--foreground)); border: 1px solid hsl(var(--border)); border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 13px; }`
- **Render:** `docs/proposals/2026-10-17-density-renders/option-3-native-button-token-dark.jpg`
  — the real dark Analytics page with the injected treatment on the measured face; **a simulation of
  the option, not shipped behaviour.** The "before" is the committed SG-199 shot
  `docs/worklogs/SG-199_shots/dark_analytics_1440x900.jpg` (light face), reused by reference.

### Option 4 — Width-adaptive default (fit-based)

- **Name:** Width-adaptive default (fit-based).
- **What changes:** the initial density state becomes width-dependent — table wherever the measured
  838 px of columns fits the content column without horizontal scroll, grid otherwise (today
  `CatalogPage.tsx:40` is unconditionally `"grid"`). The exact rule — threshold, persistence, scope —
  **owner must specify** before any implementation slice; the threshold between 640 and 1280 was not
  measured.
- **What it GIVES:** density (4.9× per item) by default at widths where the table fits with zero
  horizontal scroll (measured 1052 px content at 1440/1280, `maxScrollLeft 0`), and no horizontal
  scrolling at narrow widths (grid at 342/577 px, `docOverflowX` 0).
- **What it COSTS:** the default behaviour changes (a different initial state per width); the table
  drops the card imagery the grid shows; without persistence the state still resets on navigation
  exactly as today; the breakpoint must be chosen or measured before implementation.
- **Measured fact it rests on:** items 1, 2 and 8 — 4.9× density; 838 ≤ 1052 with no scroll at
  1440/1280; 261/496 px of scroll (table) vs 0 (grid) at zoom200/touch390.
- **Render:** `docs/proposals/2026-10-17-density-renders/option-4-width-adaptive-table-1440.jpg`
  — the real table state at 1440 light, entered through the real "Compact Table" control. The image is
  real rendering of the shipped table state; the simulative element is only that this option would
  make it the initial state at this width (the shipped default remains grid). The narrow side is the
  committed SG-203 shot `docs/worklogs/SG-203_shots/touch390_grid.jpg`, reused by reference.

## Requirements not on record

**No density requirement exists on record.** SG-190 kept the existing toggle; no compact/comfortable,
persistence or per-surface rule was ever requested (recorded in `docs/decisions/2026-10-16-density-scope-d4.md`
and SG-203's report). None of the options above invents one: options 2 and 3 rest on measured defects /
measured off-token faces; option 4's premise (a width rule) is marked **owner must specify** and is
presented, not assumed. An option whose premise needs a requirement not on record is stated as such —
never invented (owner D-6 refinement 2).

## Renders — provenance and dispositions

Produced by `docs/proposals/2026-10-17-density-driver.mjs` (sha256 `7e3c7067…`) in one run on the
frozen driver bytes (11 s; `SG-204_renders_run.log`, `SG-204_measure.json`). Transport guard: GET only,
0 blocked, 0 external, 0 unexplained fulfillment byte mismatches (1 clock-only classification on
`/v1/analytics/summary`); masking applied after measurement, before capture. Every render was opened
by the Coder and dispositioned in one read-through:

| Render | Option | Kind | UI | Layout | Data |
|---|---|---|---|---|---|
| `option-1-leave-it-baseline-grid-1440.jpg` | 1 | real, no injection | clean, no clipping/overlap | 4-up grid, 2 rows, toolbar single row | 7 items, facet counts and categories consistent |
| `option-2-dark-focus-ring-fix.jpg` | 2 | simulation (injected CSS), 2× close-up | ring clearly visible, no artifacts | group intact, ring meets the neighbour edge without overlap | control only, no product data |
| `option-3-native-button-token-dark.jpg` | 3 | simulation (injected CSS) | face now dark-on-light-text, no artifacts | page layout unchanged; button 21→25 px high | Analytics numbers unchanged (7 total, 0 signals) |
| `option-4-width-adaptive-table-1440.jpg` | 4 | real state via real control; selection rule simulated | clean, no clipping/overlap | 7 columns fit 1052 px, no horizontal scroll | 7 rows; categories match the grid render |

Injection strings are quoted verbatim in the options above; every changed render is labelled a
simulation of the option, never shipped behaviour. No product/config/test/schema/migration change
exists in this slice.
