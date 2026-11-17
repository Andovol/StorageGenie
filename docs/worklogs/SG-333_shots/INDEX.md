# SG-333 proofs — six catalog redesign shots, read from the DOM in the same DevTools session

Method: headless Chrome `/usr/bin/google-chrome` (headless=new, --no-sandbox), one browser, one page target, one DevTools WS session, driver `output/SG-333-scratch/shoot.mjs` (scratch, removed before the report). Frontend `http://127.0.0.1:14333` (scratch build, `VITE_API_BASE=http://127.0.0.1:18333`), API `http://127.0.0.1:18333` (scratch SQLite `output/SG-333-scratch/sg333.db`). Theme via `localStorage["sg-theme"]` set before reload (SG-326 method); `household_id` seeded the same way. Viewport via `Emulation.setDeviceMetricsOverride` (1280×900 or 390×844, DPR 1, mobile true under 640). Items-per-row through the page's own visible control (`.sg-per-row-button` click, `clicked:4` quoted where used); defaults by removing the key then reload. Full-page screenshot via `Page.captureScreenshot` with `captureBeyondViewport:true` and full-content clip. Every value below is read from the page through the same session that took the shot (probe `PROBE_JS` in the driver); raw probe JSON per shot was `output/SG-333-scratch/proof-*.json` (removed with scratch).

Seed: household `01a1eb6c-e60f-70a0-aae4-ad9a849dd2af` ("SG-333 Scratch"), run date 2026-11-17. 12 live + 1 gone through the HTTP API (`output/SG-333-scratch/seed.py`, log `logs/seed.log`): 4 photos as 48×48 solid PNGs made with the backend venv's Pillow (no install — red/green/blue/yellow, 126–129 bytes) uploaded via `POST /v1/evidence`, assets via `POST /v1/assets`, `classification {"category":"food"}`, `expiry {"expiry_date":…}`, gone via `POST /v1/assets/{id}/gone {"reason":"used_up"}`. Dates computed from the run date: past 2026-11-16 (−1d, Olive Oil #1), this-week 2026-11-19 (+2d, Milk) and 2026-11-22 (+5d, Olive Oil #2), later 2026-12-17 (Rice) / 2027-01-16 / 2027-02-15 / 2027-03-17 / 2027-05-16 / 2027-06-05 / 2027-07-25 / 2027-09-13, no-date Pasta, gone Old Jam 2026-12-27. Verify: `LIVE_COUNT 12`, `GONE_COUNT 1`, `STATUS rows=11 past=1 soon=2` (seed log). No provider network: the seed never calls `/v1/imports` (no import/run path); backend ran with `SG_PROVIDER_ID=fake` and empty keys; `app/services/providers/fake.py:1` docstring reads "no network, no key, no SDK" and `grep -rE "requests|httpx|urllib|urlopen|socket"` on that file returns 0 hits; `provider_call` table count is 0 after seeding (sqlite check quoted in the report).

Bundle: built `output/SG-333-scratch/build/assets/index-CVimjnED.js` — `grep -o 127.0.0.1:18333 | wc -l` = 7 (>0), `grep -o 8003 | wc -l` = 0 (else STOP, did not stop).

## Distinct-hash check

Quoted check: the six sha12 values `7e186ab1dfe4`, `6e1b097c1f34`, `48ca1f1bf413`, `0452ff2819a9`, `6835ae53cd28`, `698f4ec38faf` are pairwise distinct — 6 distinct of 6. No two shots share a hash.

## Forbidden-text + ISO check (every shot)

Quoted check: `document.body.innerText` scanned for `[object Object]`, `display_name`, `expiry_date`, `Candidate`, `Photo only`, `Dimensions/Specs`, `Create asset`, `Import Asset`, `Untitled`, `Thumbnail unavailable`, `noname`, `AWAITING_REVIEW`, `ACTIVE`, `ARCHIVED` → hits `[]` on all six shots (probe field `hits`). ISO regex `\d{4}-\d{2}-\d{2}` on `innerText` → `[]` on all six (probe field `isoHits`, capped at 10). Note: later dates render as `17 Dec 2026` etc. (no ISO), verified by the empty scan.

Fonts everywhere: no visible text node's computed `font-family` contains `mono` (probe `mono: []` all six). Every visible button/link on every shot carries a numeric WCAG contrast ratio computed in the script on its effective background; none missing or "n/a" (probe `ctrls[].ratio` all numbers, minima quoted per shot). Every card date line carries a numeric ratio on the card's effective background (probe `cardData[].ratio` all numbers).

---

## 01 — catalog, light, 1280, 5 per row (default)

File `01-catalog-light-1280-5.png`, sha12 `7e186ab1dfe4`, 86966 bytes.
Proving text (DOM): title `Your things` (`h1.sg-catalog-title`); `12 things`; `Gone (1)` link; attention `1 item is past its date and 2 run out this week. Show them` (`[data-testid="catalog-attention"]`); sort value `useby`, label `Use by, soonest first` (`select[aria-label="Sort"]`). The shot shows the title, the attention line, the toolbar with `Per row 4 5 6` (5 active) and a 5-across grid (image).

- `body` background: `rgb(243, 242, 239)` (light paper). Main wrapper `[data-testid="page-container"]` background: `rgba(0, 0, 0, 0)` (transparent over body — image shows one paper ground).
- Fonts: heading (`h1.sg-catalog-title`, text `Your things`) `"Instrument Sans Variable", system-ui, …`; one card name (`.sg-card-name`, text `Olive Oil`) same stack; one button (`button`, label `Menu`) same stack.
- Buttons/links: 33 visible, every one with numeric bg/color/ratio (min 5.44). Sample: `StorageGenie` paper/ink 15.36; `Catalog` (active) ink bg/paper text 15.36; `Add item` ink/paper 12.74 (dark-on-light button); `Gone (1)` ink 15.36; `Uncategorized` muted 5.44; per-row `5` (active, ink bg) vs `4`/`6` paper. Full list in the probe JSON (removed with scratch; minima quoted here).
- Date lines (12 cards, all numeric ratios): `Olive Oil — Past its date · 16 Nov` `rgb(122, 46, 34)` 8.37; `Milk — Use by 19 Nov · 2 days` `rgb(95, 69, 17)` 8.0; `Olive Oil — Use by 22 Nov · 5 days` same 8.0; later cards `Use by 17 Dec 2026` … `Use by 13 Sep 2027` ink `rgb(25, 27, 34)` 15.36 each; `Pasta — No date yet` muted `rgb(95, 98, 107)` 5.44. Past and this-week lines named (the two Olive Oils + Milk).
- Smallest computed `font-size` among visible text nodes: 13 px; nodes under 13 px: none (`under13: []`).
- Mono: none (`mono: []`).
- Grid (`[data-testid="catalog-grid"]`): computed `grid-template-columns` = `191.188px 191.203px 191.203px 191.203px 191.188px`, track count 5; cards sharing the first card's `top` = 5. Both equal the shot's 5. `localStorage sg-per-row-wide` = null (key removed → default 5), `sg-per-row-narrow` = `3` (untouched other mode); active per-row buttons `[{4,false},{5,true},{6,false}]` (DOM).
- Corners: card `0px`, photo tile `[data-testid="product-card-well"]` `0px`, one button `0px` (all quote `0px`).
- Tiles: 4 photo cards each `<img naturalWidth 48>` (loaded, not broken: Olive Oil red, Milk blue, Olive Oil green, Rice yellow); 8 no-photo cards each show the fallback `Package` icon (`fallback-icon(Package)`, well text empty) — no text tile.
- Two Olive Oils: `Past its date · 16 Nov` vs `Use by 22 Nov · 5 days` (DOM `olives`); told apart at a glance — image shows red vs green tiles plus different washes/text.
- Scroll (desktop, informational): `scrollWidth 1265` vs `clientWidth 1265` (equal).
- Truncation: `trunc: []` (no card name truncated or wrapping); toolbar control wrap: probe `toolbarWrap:true` is a minHeight artifact (per-row buttons `min-height:44px` vs 13 px text) — the image shows every toolbar control label on one line (`All`, `Uncategorized`, sort, `Per row 4 5 6`) on a single toolbar row, no control text wraps onto two lines.

Design notes (image unless named): (1) clipping/crowding — none; image shows an airy 5-across grid with wide gaps and no overlap; DOM `trunc []` proves no name clips. (2) mismatched surfaces — one paper ground (DOM body vs transparent wrapper); photo tiles are loud solid scratch colors (image) against quiet grey cube tiles — the placeholder reads fine, the solids are a scratch artifact, not the product. (3) text under 13 px — none (DOM smallest 13). (4) weak contrast — none weak: weakest DOM 5.44 (muted `No date yet`/`Uncategorized`) passes 4.5, every button ≥5.44, image text crisp. (5) leftover developer wording — none in the image; `Uncategorized` is the designed plain word for unknown (DOM category), `Show them` is the designed link, catalog shows `Add item` (not `Import Asset`). (6) date wording — past + two this-week lines in owner words with day-month, later dates with year, `No date yet` for Pasta (DOM + image). (7) no-photo tile beside photo tile — image shows grey cube tiles beside saturated photos; the cube reads as an intentional placeholder. (8) two Olive Oils — told apart at a glance by tile color and date wash/text (image + DOM olives). Phone sizes n/a (desktop shot).

## 02 — catalog, dark, 1280, 5 per row (default)

File `02-catalog-dark-1280-5.png`, sha12 `6e1b097c1f34`, 86507 bytes.
Proving text (DOM): same as 01 — title `Your things`, attention `1 item is past its date and 2 run out this week. Show them`, sort `useby` / `Use by, soonest first`. Image shows the same 5-across grid on dark.

- `body` background: `rgb(18, 20, 25)` (dark). Wrapper `[data-testid="page-container"]`: `rgba(0, 0, 0, 0)` (transparent — image shows one dark ground).
- Fonts: heading / card name / button all Instrument Sans Variable stack (same selectors as 01).
- Buttons/links: 33 visible, all numeric, min 7.57. Sample: `Catalog` active paper bg/dark text 15.32; `Add item` light bg/dark text 10.88; `Uncategorized` muted 7.57.
- Date lines: `Past its date · 16 Nov` `rgb(240, 196, 190)` 11.71; this-week `rgb(235, 215, 166)` 12.99 each; later ink `rgb(232, 234, 240)` 15.32 each; `No date yet` muted `rgb(162, 166, 177)` 7.57.
- Smallest: 13 px; under 13: none. Mono: none.
- Grid: `191.188px …` 5 tracks; firstRow 5; equals 5. `sg-per-row-wide` null (default), `sg-per-row-narrow` `3`; active `5:true`.
- Corners: `0px` / `0px` / `0px`.
- Tiles: same 4 `<img naturalWidth 48>` + 8 `fallback-icon(Package)`.
- Olives: same two date texts; told apart by tile color + wash (image).
- Scroll 1265 vs 1265. Trunc []. ToolbarWrap flag same artifact; image shows single-row toolbar, no control wraps.
- Forbidden/ISO: `hits []`, `isoHits []`.

Design notes: (1) clipping/crowding — none (image airy; DOM trunc []). (2) mismatched surfaces — one dark ground (DOM); photo solids pop on dark (image, scratch artifact), cube tiles dark-grey — coherent. (3) text under 13 px — none (DOM). (4) weak contrast — none: weakest DOM 7.57 on dark (better than light's 5.44), image text highly legible including muted lines. (5) leftover wording — none (image; same `Uncategorized`/`Show them` design notes as 01). (6) date wording — same owner words as 01, dark washes readable (image + DOM). (7) no-photo vs photo — image shows dark cube tiles beside bright photos; placeholder reads clearly. (8) two Olive Oils — told apart at a glance (image tile colors + DOM dates). Phone sizes n/a.

## 03 — catalog, light, 390, 3 per row (default)

File `03-catalog-light-390-3.png`, sha12 `48ca1f1bf413`, 49901 bytes.
Proving text (DOM): title `Your things`, attention same line, sort `useby` / `Use by, soonest first`. Image shows narrow 3-across grid, `Per row 3 4` with 3 active.

- `body` `rgb(243, 242, 239)`; wrapper transparent. Fonts: same Instrument Sans stack (h1 / card name / button).
- Buttons/links: 24 visible, min 5.44 (`Uncategorized` muted; `Add item` 12.74; rest ≥8).
- Date lines (narrow wording): `Olive Oil — Past · 16 Nov` 8.37; `Milk — 19 Nov` 8.0; `Olive Oil — 22 Nov` 8.0; later `17 Dec 2026` … ink 15.36; `Pasta — No date` muted 5.44. Past + this-week by name (first three cards).
- Smallest 13; under13 []; mono [].
- Grid: `108.656px 108.672px 108.656px`, 3 tracks; firstRow 3; equals 3. `sg-per-row-narrow` null (default), `sg-per-row-wide` `5`; active `[{3,true},{4,false}]`. No visible-control click (default).
- Corners `0px`×3. Tiles: 4× `naturalWidth 48` + 8× fallback icon.
- Olives: `Past · 16 Nov` vs `22 Nov` (DOM); image shows red vs green tiles, told apart.
- Phone: `scrollWidth 390` vs `clientWidth 390` (equal — no sideways scroll). `trunc []` (no card name truncated or wrapping). Toolbar: container wraps to two rows on narrow (image shows tabs+sort row and icons+Per-row row; DOM `toolbarTops [187,187,192,234,234,238,224,224]` proves two toolbar rows) — no control's own text wraps onto two lines in the image (each label single-line); probe `toolbarWrap:true` is the 44 px min-height artifact, not a shown wrap.
- Forbidden/ISO clean.

Design notes: (1) clipping/crowding — none; image shows breathing 3-across cards, DOM scroll equal + trunc [] prove no sideways clip or name clip. (2) mismatched surfaces — one paper ground; grey cubes vs solid photos as on 01 (image). (3) text under 13 px — none (DOM). (4) weak contrast — weakest 5.44 muted, passes; image crisp. (5) leftover wording — none (image). (6) date wording — narrow short forms (`Past · 16 Nov`, bare `19 Nov`) read well at 390 (image + DOM). (7) no-photo vs photo — cubes align with photos in 3-col rhythm (image). (8) two Olive Oils — told apart (image colors + DOM dates). (9) card/button sizes at 3 per row — comfortable: tiles ~108 px, names 13 px single-line, Per-row buttons 44 px targets (image + DOM `min-height:44px`); 3 is not tight.

## 04 — catalog, light, 390, 4 per row (via visible control)

File `04-catalog-light-390-4.png`, sha12 `0452ff2819a9`, 45795 bytes.
Proving text: same title/attention/sort as 03 (DOM). Image shows 4-across grid, `Per row 3 4` with 4 active.

- Body/wrapper/fonts: same light values as 03. Buttons/links 24, min 5.44. Date lines same narrow texts as 03 with same colors/ratios (past 8.37, soon 8.0, later 15.36, none 5.44).
- Smallest 13; under13 []; mono [].
- Grid: `79.5px 79.5px 79.5px 79.5px`, 4 tracks; firstRow 4; equals 4. `sg-per-row-narrow` read back `4`; control `clicked:4` (driver clicked the visible `4` button — quoted `controlResult`), active `[{3,false},{4,true}]`. Items-per-row was set through the page's own visible control, then read back — no fallback.
- Corners `0px`×3. Tiles 4×48 + 8×fallback. Olives same as 03, told apart (image).
- Phone: scroll 390 vs 390 equal; trunc []; toolbar two rows in image as on 03, no control wraps (same artifact note).
- Forbidden/ISO clean.

Design notes: (1) clipping/crowding — none in the image; 4-across tiles ~79.5 px (DOM grid) still separate with gaps; DOM trunc [] + scroll equal prove no clip. (2) surfaces — same as 03 (image). (3) text under 13 px — none (DOM). (4) weak contrast — same minima as 03, passes (DOM + image). (5) leftover wording — none. (6) date wording — same short forms, still legible at 4-col (image). (7) no-photo vs photo — same placeholder rhythm, tighter but aligned (image). (8) Olive Oils — told apart (image + DOM). (9) 3 vs 4 tightness — 4 is tighter than 03 (tiles 79.5 vs 108.7 px) but every name/date stays on one line in the image and DOM trunc [] proves none wraps or truncates; 4 is readable, 3 breathes more — owner call, not a defect.

## 05 — catalog, dark, 390, 3 per row (default)

File `05-catalog-dark-390-3.png`, sha12 `6835ae53cd28`, 49587 bytes.
Proving text: same title/attention/sort (DOM). Image shows dark 3-across grid, `Per row 3 4` with 3 active.

- Body `rgb(18, 20, 25)`; wrapper transparent; fonts Instrument Sans stack.
- Buttons/links 24, min 7.57. Date lines narrow dark colors: past 11.71, soon 12.99, later 15.32, none 7.57.
- Smallest 13; under13 []; mono [].
- Grid `108.656px …` 3 tracks; firstRow 3. `sg-per-row-narrow` null (default); active 3:true. No click.
- Corners `0px`×3. Tiles 4×48 + 8×fallback. Olives `Past · 16 Nov` / `22 Nov`, told apart (image).
- Phone: 390 vs 390; trunc []; toolbar two rows (image), no control wraps (artifact note as 03).
- Forbidden/ISO clean.

Design notes: (1) clipping/crowding — none (image + DOM scroll/trunc). (2) surfaces — one dark ground; dark cubes vs bright photos coherent (image). (3) text under 13 px — none. (4) weak contrast — weakest 7.57, strong on dark (DOM + image). (5) leftover wording — none. (6) date wording — short dark-wash forms legible (image + DOM). (7) no-photo vs photo — placeholder clear beside photos (image). (8) Olive Oils — told apart. (9) 3 per row — comfortable at 390 dark, same as 03 (image).

## 06 — catalog, dark, 390, 4 per row (via visible control)

File `06-catalog-dark-390-4.png`, sha12 `698f4ec38faf`, 45498 bytes.
Proving text: same title/attention/sort (DOM). Image shows dark 4-across grid with 4 active.

- Body/wrapper/fonts as 05. Buttons/links 24, min 7.57. Dates same as 05.
- Smallest 13; under13 []; mono [].
- Grid `79.5px ×4`, 4 tracks; firstRow 4. `sg-per-row-narrow` = `4`; control `clicked:4`, active 4:true — set through the visible control.
- Corners `0px`×3. Tiles 4×48 + 8×fallback. Olives told apart (image).
- Phone: 390 vs 390; trunc []; toolbar as 05.
- Forbidden/ISO clean.

Design notes: (1) clipping/crowding — none (image; DOM proves no trunc/scroll). (2) surfaces — as 05. (3) text under 13 px — none. (4) weak contrast — min 7.57, no weak control especially on dark (DOM + image). (5) leftover wording — none. (6) date wording — short forms hold at 4-col dark (image). (7) no-photo vs photo — aligned tighter grid, still clear (image). (8) Olive Oils — told apart. (9) 4 vs 3 — 4 tight but readable on dark too (image shows all names/dates one-line, DOM trunc []); 3 airier — owner call.
