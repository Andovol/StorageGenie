# SG-212 — D-21: width-adaptive density default (content-fit rule, recompute, Catalog only)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none** (frontend-only; lane-local serve for smoke only).
**Autonomy: L3** (approved queue — runs after SG-211; checkpoints only on `G-K2`/assumption-change/stage end). Authority: owner D-21 ("use your recommended values" — values stated in `docs/decisions/2026-10-17-d19-d22-answers.md`, proved here).

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

D-8 left width-adaptive default unapproved for want of a requirement; D-21 supplies it (Architect values, owner-adopted). The shipped default is unconditionally `"grid"` (`CatalogPage.tsx:40`) though SG-203 measured the table fits 1052 px content with zero scroll at 1440/1280 — density (4.9×/item) left on the table at wide widths, forced scroll inflicted at narrow ones when the user picks table.

## Handed-over facts (expected — re-verify on target, `PB-1`)

- Rule (the D-21 values): initial density = table iff the Catalog content column measures **≥860 px** at mount (838 px measured table need + 22 px uncalibrated margin, `G-A9`); else grid. Recompute on every fresh navigation (no persistence, no stored preference, no migration). Scope: Catalog only.
- Current code (expected): `useState<Density>("grid")` at `frontend/src/routes/CatalogPage.tsx:40`; breakpoints `ProductGrid.tsx:15-18`; table branch `:331`; control group `CatalogToolbar.tsx:168`. SG-203 numbers: 838 px columns; content 1052 at 1440/1280 (`maxScrollLeft` 0); 261 px scroll at zoom200-577, 496 px at touch390-342; grid `docOverflowX` 0 everywhere.
- What the choice turns on (stated so the Coder decides, not guesses): the rule reads CONTENT width (the measured quantity), never a viewport breakpoint (unmeasured in the 577–1280 band); the read point must exist before first paint decisions cause visible flip; narrow widths must NEVER initially scroll horizontally (grid fallback is the safe side — err toward grid on any unreadable measure).

## G1 — implement the rule

- Replace the unconditional `"grid"` initial with the content-fit evaluation at Catalog mount; recompute per fresh navigation; the toggle keeps working both directions afterwards (user choice always wins post-mount). No persisted preference anywhere (localStorage, URL, server — none).
- Tests (FAIL-then-PASS, new rows): wide-mount (≥860 mocked) initialises table; narrow-mount (<860) initialises grid; unreadable-measure initialises grid; toggle still flips both ways after mount. Base run = the new rows FAILING pre-change; candidate run = full frontend suite green once.

## G2 — prove it on the served page

- Lane smoke: served Catalog at 1440-equivalent width opens in table state with zero horizontal scroll; at touch390-equivalent opens in grid with zero `docOverflowX`; toggle exercised both directions at one width. Screenshots committed (2+), opened, dispositioned (the `/` route — no `/catalog` route exists, SG-207 finding #3).
- Enumeration: every other density-default or persistence site found on target (expected: none — report either way, `PG-IC-08`).

## Constraints

- **Scope ceiling (rule, grep-gated):** product bytes ONLY Catalog density-init + its tests; evidence ONLY `docs/worklogs/SG-212_*`. No backend/config/persistence/migration bytes; no other route touched.
- Reads: lane CDP + loopback GETs only; no production/evidence writes; no restart; health start+end identical expected. No prompt/polling/sudo/host change/secrets. `PB-2` denial STOPS; `PB-3` vacuity as in G1 (a test green without exercising the rule is a FAIL).
- Hang bounds: reads 120 s; suite per its bound; smokes 600 s; idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-208's 363 s removal + proof legs for the new-rule tests/smoke).
- Simplicity: one rule + tests + smoke; no preference infrastructure. Excluded (stated): persistence of any kind; other surfaces; Option C; AI stages.

## Acceptance criteria

- **A1:** new-rule tests FAIL pre-change / PASS post-change, both runs committed; full suite green once on candidate with counts.
- **A2:** served smoke shows table-at-wide (no scroll) + grid-at-narrow (no overflow) + working toggle; screenshots committed + opened; enumeration (criterion + set + delta) in the report.
- **A3:** report `docs/worklogs/SG-212_report.md`; elapsed vs ≈600 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-212`.
- **A4:** notes-ref receipt, first line `Dispatch-ID: SG-212 | Report: docs/worklogs/SG-212_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/05/08/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-01/03/04. Stop follows `PB-6`.
