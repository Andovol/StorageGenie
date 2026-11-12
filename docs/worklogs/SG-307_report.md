SG-307 | model opencode-go/muse-spark-1.3-contributor effort xhigh (both read from the process arguments: `opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/muse-spark-1.3-contributor --variant xhigh`) | cwd /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> resolved 0dd3fa74c27de4d64a1f85778a1417f4469ef105 | WORK_HEAD 76c5315de50c36900fa87aafa136882ceaca88be (this report's commit follows it)

# SG-307 report: catalog and item panel in the tandpfun look, plain words, no white controls on paper

**Result: G0, G1, G2, G3 done and committed. G4 partial: FAIL-then-PASS done (11 failed / 1 passed on base, 12 passed on candidate); older changed files green (55/55); tsc green; the full gate (eslint log, build, backend, image, frontend suite, twice runs) NOT run — stopped past the 1100 s line (see Elapsed). Verification: FAIL.**

## Elapsed and phase seconds (stamps from `date +%s`)

- Start 1794507405. G0 preflight 1794507405 to 1794507408 (3 s): `docker version` shows a Server section, `docker run --rm busybox true` rc 0; health 200 at start.
- Inventory + reads 1794507408 to 1794507605 (~197 s).
- G1 catalog build 1794507605 to 1794507856 (~251 s), committed 8c62201.
- G2 panel build 1794507856 to 1794508157 (~301 s), committed 21a0832.
- G3 controls + header 1794508157 to 1794508218 (~61 s), committed 56cf7d3.
- G4 tests 1794508218 to 1794508521 (~303 s): new files written, FAIL on base worktree, PASS on candidate, two older files updated and green, tsc fixed green. Committed 76c5315.
- Stop-line overrun: G4 commit at 1794508521 is 1116 s elapsed, 16 s past the 1100 s hard line; report + publish run past it (disclosed, not hidden). Scratch `output/SG-307-scratch` removed at 1794508512 (before the report); health 200 at end (1794508512).
- Base worktree `output/SG-307-scratch/base` added at 0dd3fa7 and removed with `git worktree remove --force` before scratch removal.

## Inventory (G1 premise; quoted in full)

**Components the catalog and the panel render:**
CatalogPage (route) → AppShell → AppHeader (+ ThemeToggle, AssetImportModal), CatalogToolbar, ProductGrid → ProductCard / ProductCardSkeleton / AssetImportModal (empty state); ItemInspectorDrawer on select (header, tablist, viewer well, Metadata, Amount left, Use it up, Observed, AI actions; reuses CONTROL_STYLE / THEMED_CONTROL_CLASS from CatalogToolbar).

**Test files that render them:** `catalog.test.tsx`, `CatalogPage.sg272.test.tsx`, `shell.test.tsx`, `drawer.test.tsx`, `ItemInspectorDrawer.sg272/sg300.test.tsx`, `theme-adoption.test.tsx`, `sg301-screens.sg301.test.tsx`, `sg312-design.sg312.test.tsx`, `sg312-screens.sg312.test.tsx`.

**Owner-facing strings that are developer wording, an enum, monospace or under 13 px (every one quoted):**
- ProductCard: `Source Only` / `Cutout Extracted` / `Scene Rendered` / `Failed`; category chip `font-mono` 11 px rounded; badge 11 px `borderRadius 999`; card `borderRadius 12`, well `borderRadius 8` on `bg-card-muted`; title 14 px (ok).
- ProductGrid: `formatRelativeDate` `30m ago` / `6h ago` / `6d ago` + `font-mono` date column; category chip `font-mono` 11 px rounded; badge 11 px `999`; headers 11 px; table dot `999`; empty help 12 px; CTA `borderRadius 6`; `...` actions button `borderRadius 4`; GRID_CSS `repeat(2/3/4/5` + `@media`.
- CatalogPage Gone: `bg-card` cards `borderRadius 8`; `Put back` / `Load more` `bg-card` `borderRadius 6`; `Fetching...` 12 px; no count header.
- CatalogToolbar: root `bg-card` (white); pills `bg-card-muted` / `bg-primary` with CONTROL_STYLE `borderRadius 6`; selects THEMED_CONTROL_CLASS `bg-background` (near-white); saved labels + active filters 11 px `999`; `None yet` 12 px; `Clear all` 12 px.
- AppShell: `bg-background` wrappers (near-white).
- AppHeader: search `minWidth 180`; `Import Asset` text (wraps at 375); no aria-label; no one-row classes.
- ThemeToggle: `bg-card` (white) `borderRadius 6`.
- AssetImportModal: panel `borderRadius 12`; queue `font-mono` file size + 12 px rows `borderRadius 6` on `bg-card-muted`; `queue-empty` 12 px; dropzone `borderRadius 8` on `bg-card-muted`; size note 11 px; `auto-detect-help` 11 px; `rejected-files` 12 px; `Cancel` `bg-card` `borderRadius 6`; `Remove` 12 px; native file input unstyled (white on dark per SG-313).
- ItemInspectorDrawer: tabs `Isolated Cutout` / `Scene / Context` / `Source Photo`; cut-out empty `No isolated cutout exists yet. Cutouts arrive with the AI stages — nothing is being processed.`; scene empty `No context scene exists yet. Scene rendering arrives with the AI stages — nothing is being rendered.`; source empty `No source photo is attached to this asset.`; `Bounding-box overlay omitted: no bounding-box data exists for this asset yet — a decorative box is never drawn.`; category chip `font-mono` 11 px; tabs 12 px `borderRadius 6` `gap 4`; well `bg-card-muted` `borderRadius 8`; inputs `bg-background` `borderRadius 6`; `Save changes` `bg-primary` `borderRadius 6`; `Uses If-Match: {version} for optimistic concurrency` 11 px; observed empties `No observed color data for this asset.` / `No functional description assertion for this asset.`; `Read-only rows: these fields have no schema home yet, so they are never editable here (D65).` 11 px; AI buttons `borderRadius 6` (`bg-card-muted` / `bg-primary`); `ai-notice` 12 px `borderRadius 6` `bg-card-muted`; `No model or cost text is shown: with no provider backend a model/cost string would be fabricated.` 11 px.

## Premises, confirmed or falsified (file:line as read before edits)

- **Catalog mono timestamps + `item` chips CONFIRMED:** `ProductCard.tsx:208` `font-mono` chip; `ProductGrid.tsx:188` `font-mono` chip; `:223` `font-mono` date column; `formatRelativeDate` (`ProductGrid.tsx:55-69`) returns `Xm/Xh/Xd ago`.
- **`Source Only` CONFIRMED:** `ProductCard.tsx:41` `raw: "Source Only"` (plus `:42-43` `Cutout Extracted` / `Scene Rendered`).
- **Rounded thumbnails + white toolbar CONFIRMED:** card `borderRadius 12` (`:115`), well `borderRadius 8` (`:127`); toolbar root `bg-card` (`CatalogToolbar.tsx:112`).
- **Panel tab `Isolated Cutout` CONFIRMED:** `ItemInspectorDrawer.tsx:16`.
- **Developer sentences CONFIRMED:** `:345` cut-out AI-stages sentence; `:376` bounding-box sentence.
- **`Kind of item: Uncategorized` for a food item — cause established:** the input at `:390-398` reads the `category` state, which is initialised from `asset.asset_type` (`:72`, `:111` `toProductCategory(asset.asset_type)`). A Pantry food item's food kind lives in the accepted expiry classification assertion (`plugin:expiry-tracker/classification`, category `food_beverages`), not in `asset_type` (Pantry tests use `asset_type: "product"` with food rows; real items with `asset_type unknown`/empty map to `Uncategorized`). So the field correctly reports what `asset_type` holds; showing the classification kind would need a backend sync (or a frontend read of the assertion into the `asset_type` editor, which would change PATCH payloads). Per the packet, **backend change reported, nothing changed there** — the field still reads `asset_type`, now in plain words via `labelAssetType`.
- **White controls CONFIRMED by code (SG-313 measured):** Pantry `ACTION_STYLE` `backgroundColor hsl(var(--card))` (`PantryPage.tsx:51`); `ThemeToggle.tsx:15` `bg-card`; Inbox Review status `THEMED_CONTROL_CLASS` = `bg-background` (`CatalogToolbar.tsx:64`, used `InboxPage.tsx:82`); asset native file input unstyled (`AssetDetailPage.tsx:806`).
- **375 header wraps CONFIRMED by code (no screenshot in this slice):** AppHeader content (count ~100 + search min 180 + toggle + Import text + gaps + 48 padding) exceeds 327 px; both Nav (`App.tsx:68-80`) and AppHeader use `flexWrap: wrap`.

## How each goal was met (file named for each)

- **G1 catalog:** `labels.ts` gains `PRODUCT_STATUS_LABELS` + `labelProductStatus` (raw `Photo only` — only the photo exists; processed `Cut-out ready`; rendered `Scene ready`; failed `Needs attention`, matching the shared failed wording; reason: owner sees what exists, not pipeline stages). `ProductCard.tsx` uses `labelProductStatus`, drops `font-mono`, square (`borderRadius 0`), paper ground + `--line` border, badge/chip/category 13 px, dots square. `ProductGrid.tsx` GRID_CSS is now `repeat(auto-fill, minmax(165px, 1fr))`; `formatRelativeDate` returns `1 min ago` / `6 hours ago` / `6 days ago` etc.; table headers 13 px uppercase spaced, chips/badges 13 px square paper, actions button paper square. `CatalogToolbar.tsx` root paper + `--line`, joined square tabs (`gap 0`), active `ink` bg / paper text (matches App nav active; distinct by fill, not colour alone), `CONTROL_STYLE` radius 0, `THEMED_CONTROL_CLASS` = `sg-paper-control` (so Inbox inherits paper without touching it), saved/filter pills 13 px square paper. `CatalogPage.tsx` category display + active filters via `labelAssetType` (unknown → `Uncategorized` unchanged; `food_beverages` → `Food Beverages`), Gone cards + `Put back` / `Load more` paper square via `sg-paper-control`, `Fetching...` 13 px, new `data-testid="catalog-count"` `N ITEMS` 13 px 700 `.12em` uppercase (Pantry parity). `AppShell.tsx` wrappers paper/ink (was `bg-background`). `ProductCardSkeleton.tsx` square paper/line. `AssetImportModal.tsx` (rendered by the catalog empty state) panel/queue/dropzone paper square, mono removed, all text ≥13 px, buttons `sg-paper-control`/ink. `tokens.css` gains `.sg-paper-control` (paper, `--line`, square, ink, 13 px) — the one named rule.
- **G2 panel:** `ItemInspectorDrawer.tsx` tabs renamed Photo / Cut-out / In a scene (source first; joined square, `gap 0`, active ink/paper, `marginLeft -1` shared edge); cut-out empty `No cut-out yet.`, scene `No scene yet.`, source `No photo yet.` (one short line each, never how the system works); bounding-box `<p>` removed from the screen, hook kept as `data-bbox-omitted="true"` on `viewer-well`; category display + inputs use `labelAssetType(asset_type)` (same field, plain words; `product` → `Product` instead of raw lowercase); fields square `sg-paper-control` 13 px; section rules `--line`; `Version {version}` replaces the If-Match sentence (header still sends If-Match; display only); observed empties `No colours yet.` / `No description yet.`, note `These stay read-only here.`; AI copy shortened only for the 11 px floor (`No model or cost shown.`), buttons square paper/ink. **Kind cause:** see Premises; no backend byte changed.
- **G3 controls + 375:** `ThemeToggle.tsx` is now `sg-paper-control` square with `data-testid="theme-toggle"` (was `bg-card`). `tokens.css` adds the native `input[type="file"]` paper rule (asset page fixed without touching it) and the `[data-testid="pantry-tile"] button, [data-testid="pantry-notice"] button` paper override (`!important` only to beat the untouched inline `var(--card)`; `PantryPage.tsx` NOT touched per the scope ceiling). Inbox Review status inherits paper via `THEMED_CONTROL_CLASS` (no `InboxPage.tsx` touch). `AppHeader.tsx` (`sg-header`, `sg-header-count`, `sg-header-search`, `Import Asset` gains `aria-label` + `<span class="sg-import-label">`, search `minWidth 0`) + `App.tsx` nav (`sg-nav`, same import span/aria) + `@media (max-width: 480px)` rule (hide import text + count, `nowrap`, tighter padding/gaps) fits one row; choice documented in CSS: icon-shortening keeps the toggle reachable everywhere (vs moving it into the menu).
- **Do-not-change:** no behaviour, routes, API calls, data, Inbox/Expiry/asset logic beyond the shared control rule; no backend/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/host/provider/container/deploy bytes; `frontend/dist` untouched; no `/tmp` (npm cache in scratch); `output/` + `output/dispatch` untouched; `output/SG-307-scratch` removed before this report; no server started.

## Test changes (all named)

- New `frontend/src/components/catalog/catalog.sg307.test.tsx` (6 tests): status map, no mono + plain status, all statuses, plain timestamps + no mono + no short forms, grid track rule, square/paper/13 px card.
- New `frontend/src/components/shell/panel.sg307.test.tsx` (6 tests): plain tabs + one-line cut-out, bbox off-screen + data hook, no mono, Kind reads `asset_type` plain, shared rule + toggle, 375 header classes.
- Older, updated because they asserted replaced wording/styling:
  - `frontend/src/components/catalog/catalog.test.tsx`: grid test now expects `repeat(auto-fill, minmax(165px, 1fr))` (was 2/3/4/5 + `@media`); `formatRelativeDate` now `30 min ago` / `6 hours ago` / `6 days ago` (was `30m/6h/6d ago`). Reason: G1 plain words + grid rule.
  - `frontend/src/components/shell/drawer.test.tsx`: title test tab `Photo` (was `Source Photo`); cut-out test tab `Cut-out` + `No cut-out yet.` (was `Isolated Cutout` + AI-stages sentence); scene test tab `In a scene` + `No scene yet.` + bbox hook attribute (was `Scene / Context` + AI-stages sentence + bbox text); observed test `No description yet.` (was `no functional description assertion`); source-empty test `No photo yet.` (was `no source photo is attached`). Reason: G2 plain words.
- No behaviour test was changed.

## FAIL-then-PASS (G4)

- FAIL on base worktree `output/SG-307-scratch/base` at `origin/automation` 0dd3fa7 (node_modules symlinked, the two new files copied in): **11 failed, 1 passed** (`docs/worklogs/SG-307_fail.log` holds names + first assertion only). First assertions: `labelProductStatus is not a function`; font-mono present; `Photo only` absent (base `Source Only`); `30m ago` vs `30 min ago`; grid lacks the 165 px rule; card radius `12px`; tab `Cut-out` absent; bbox sentence present; drawer font-mono present; `THEMED_CONTROL_CLASS` lacks `sg-paper-control`; `catalog-header` absent. The one pass is the Kind test (`Uncategorized` was already plain on base) — kept as a guard, like SG-312's `.nav-menu-toggle` guard.
- PASS on candidate: **12 passed, 2 files** (`docs/worklogs/SG-307_pass.log`).
- Older changed files on candidate: `catalog.test.tsx` + `drawer.test.tsx` **55 passed, 2 files**.

## Gate counts (G4) — INCOMPLETE, see REMAINING

- `tsc --noEmit`: rc 0 (after fixing the panel test's `afterEach`/`useAssets` mock types).
- `eslint`: our files 0 errors; repo shows the pre-existing out-of-scope error in `App.household-nav.test.tsx` (as in SG-301r1). No `SG-307_eslint.log` written (time).
- Frontend build into scratch, `make backend-test` (host + image proof), `make frontend-test`, SG-307 + changed-older-files twice: **REMAINING — not run** (hit the stop line; the twice-run of new files above is the only repetition evidence).
- No `docs/worklogs/SG-307_<step>.log` gate logs were written beyond fail/pass.

## Changed files

Product: `frontend/src/components/catalog/ProductCard.tsx`, `ProductCardSkeleton.tsx`, `ProductGrid.tsx`, `frontend/src/components/shell/AppShell.tsx`, `AssetImportModal.tsx`, `CatalogToolbar.tsx`, `ItemInspectorDrawer.tsx`, `AppHeader.tsx`, `frontend/src/theme/ThemeToggle.tsx`, `frontend/src/App.tsx`, `frontend/src/lib/labels.ts`, `frontend/src/routes/CatalogPage.tsx`, `frontend/src/theme/tokens.css`. Tests: the two new `*.sg307*` files + `catalog.test.tsx` + `drawer.test.tsx`. Evidence: `docs/worklogs/SG-307_fail.log`, `SG-307_pass.log`, `SG-307_report.md`. No backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, `frontend/dist` or deploy bytes (`git diff --name-only origin/automation..HEAD` shows only the above).

## Contract line

Contract line: I received none. (The packet states recorded `0.59.0` but gives no line of my own; this lane denies the contract folder, so I did not read it.)

## UNCLEAR / REMAINING

- **REMAINING: the full gate** (eslint log, frontend build into scratch, `make backend-test`, image proof, `make frontend-test`, new + changed-older files twice with `SG-307_<step>.log` logs and exact counts). Cause: G4 test updates + tsc fix consumed the budget; the 1100 s line hit at the older-files green (1096 s) and the run overran to 1116 s at commit.
- **REMAINING: screenshots** — this slice builds and gates only (a full build slice lost its shots twice); shots are their own slice + rider by design.
- **UNCLEAR: 375 one-row header** — proven by class/media rule + aria-label (no browser render in this slice); the rider's shots must prove the single 93 px → one-row change.
- **UNCLEAR: Pantry white-tile fix** — applied as a `tokens.css` `!important` override without touching `PantryPage.tsx` (scope ceiling); the rider's light Pantry shot must prove `rgb(244,240,232)` tiles.
- **UNCLEAR: Arial/Instrument on the new controls** — `font: inherit` was SG-312's rule and `sg-paper-control` sets `font: inherit`; not re-measured here.
- **Budget:** `RUN_BUDGET_S` 2100 s respected (stopped work at ~1116 s + report/publish); the 1100 s hard line overran by ~16 s at the G4 commit (disclosed).

## One line per criterion

- **A1** — Inventory quoted; G1–G3 each met with file named above; Kind cause stated (reads `asset_type`, food lives in classification → backend sync needed, unchanged).
- **A2** — G4 FAIL 11/1 on base, PASS 12/12 on candidate; updated older tests named (catalog 2, drawer 5). Met, with the one guard pass noted.
- **A3** — Gate green with counts, files twice green: NOT MET (REMAINING above).
- **A4** — Zero backend/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/stored-files/host/provider/container/deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before the report. Met.
- **A5** — Preflight proven; health 200 start and end; phase seconds from stamps above. Met.
- **A6** — Vacuity: a failure would look like a `font-mono` class still rendered, a developer string (`Source Only`, AI-stages sentence, bbox sentence) still rendered, a rounded corner, a white button on paper, a two-row header at 375, a test passing on base. Checked: FAIL log shows the mono/status/timestamp/grid/radius/tab/bbox/control/header failures on base; the Kind guard passes on both (named). No browser render checked (shots slice owns it).
- **A7** — Last line is FAIL because A3 is not met.

Verification: FAIL — A3 (full gate with counts, files twice green) not run; stopped past the 1100 s line.
