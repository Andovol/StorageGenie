# SG-326 proofs — six shots, read from the DOM in the same DevTools session

Seed: `output/SG-326-scratch/ids.json` (household `01a1e56f-1b34-…`, OO1 `…0c3d` dated
2030-05-06, OO2 `…61ff` dated 2031-02-03, soup `01a1e573-…` 300 ml, candidate
`01a1e56f-1d4b-…` duplicate of OO1 carrying 2032-06-18). Raw probe JSON per shot in
`output/SG-326-scratch/proofs/` (removed with scratch before the report; the values
below are copied from those files).

Theme: `localStorage["sg-theme"]` set to the shot's theme + reload (SG-321r1 method).
Fills: native value setter + `input`/`change` events. Catalog search narrowed
(02 proves 2 rows). Viewport via `Emulation.setDeviceMetricsOverride`.

## Distinct-hash check

Quoted check: the six sha12 values `42cd8c134017`, `08b05cd18d83`, `119ab7c17e55`,
`202afe6500b0`, `e6f40c3f420f`, `d591dd992d95` are pairwise distinct — 6 distinct of 6.
No two shots share a hash.

## Forbidden-text + ISO check (every shot)

Quoted check: `document.body.innerText` scanned for `[object Object]`,
`duplicate_of_asset`, `display_name`, `expiry_date`, `Candidate`, `Photo only`,
`Dimensions/Specs`, `Create asset`, `Untitled`, `Thumbnail unavailable`, `noname`,
`AWAITING_REVIEW` → hits `[]` on all six shots (probe field `hits`). ISO regex
`\d{4}-\d{2}-\d{2}` on `innerText` → `[]` on all six (probe field `iso`).
UUID pattern in `innerText` → false on all six. `ACTIVE` count in `innerText` → 0 on
all six. Note: input *values* are not `innerText` — 05/06 visibly render `ACTIVE`
and `unknown` inside inputs (image), which the scan does not see; reported under
05/06, not failed (SG-325 UNCLEAR I8).

Fonts everywhere: no visible text node's `font-family` contains `mono` (probe `mono: []`
all six). Every button on every shot carries a numeric contrast ratio (WCAG formula in
the script on the effective background); none is missing or "n/a".

---

## 01 — asset page, Tomato Soup 300 ml, light, 1280

File `01-asset-tomato-soup-light-1280.png`, sha12 `42cd8c134017`, 100466 bytes.
Proving text (DOM `innerHead`): `Tomato Soup`, `Live · 300 ml left`,
`Manual expiry entry`, `Date confirmed`, Details rows below. The shot shows the
expiry section and the Details table (image), matching the scrolled position the
script set (`section[aria-label="Manual expiry entry"]` scrolled to top at
1280×1200).

- `body` background: `rgb(244, 240, 232)` (light paper).
- Main wrapper `[data-testid="page-container"]` background: `rgba(0, 0, 0, 0)`
  (transparent over body — no mismatched surface; image shows one paper ground).
- Heading font (`h1.page-header`, text `Tomato Soup`): `"Instrument Sans Variable",
  system-ui, …`.
- Body text node font (nav sample): same Instrument Sans stack.
- Button font (first visible button): same Instrument Sans stack.
- Buttons (label | bg | color | ratio — all numeric):
  `Switch to dark theme` | paper | ink | 15.47;
  `Edit` | `rgb(244, 240, 232)` | `rgb(25, 25, 25)` | 15.47;
  `Enrich` | `rgb(110, 48, 46)` | `rgb(250, 250, 249)` | 9.46;
  `Save shelf life` | maroon | paper-light | 9.46;
  `Used up` / `Thrown away` / `Given away` | paper | ink | 15.47 each;
  `Save date` | maroon | paper-light | 9.46;
  `Clear expiry date` | `rgb(244, 240, 232)` | `rgb(25, 25, 25)` | 15.47;
  `Attach evidence` (disabled) | `rgb(245, 245, 244)` | `rgb(107, 101, 97)` | 5.26.
- Smallest computed `font-size` among visible text nodes: 13 px; nodes under 13 px: none.
- Mono: none.
- Details rows (DOM `table.detail-table tbody tr`, label → value):
  `Kind of item → Food & beverages`; `Name → Tomato Soup`;
  `Expiry date → 15 Sep 2030`; `Amount → 300 ml`; `Status → Live`.
  No `Shelf life` row among Details labels (probe `detailRows` has no such label).
  The string `Shelf life` in `innerText` is the category-picker section heading
  (`h3` above the select, image), not a Details row.
- `Edit` bg `rgb(244, 240, 232)` and `Clear expiry date` bg `rgb(244, 240, 232)`
  equal the page paper — the theme's control style (DOM `editBg`/`clearBg` vs body).
- Layout: no clipping or crowding claim — the image shows the expiry box, Details
  table and History stacked with whitespace; every listed button reports
  `wraps: false` with rects (e.g. `Clear expiry date` 122×26 at (547, 605)).

Design notes (image unless named): (1) clipping/crowding — none; sections breathe
(image). (2) surfaces — one paper ground; white card absent here (image). (3) text
under 13 px — none (DOM smallest 13). (4) weak contrast — `Attach evidence` 5.26:1
is disabled (DOM ratio; image shows it greyed) — acceptable for disabled; all live
controls ≥ 9.46 (DOM). (5) leftover wording — none in Details; History reads
`Added / Accepted / Date entered by you` plain words (image). (6) date format —
`15 Sep 2030` in Details (DOM) while the date input renders locale `09/15/2030`
(image; input, not `innerText`). (7) same-name telling-apart — n/a on this screen.

## 02 — catalog table, searched `Olive Oil`, light, 1280

File `02-catalog-olive-oil-light-1280.png`, sha12 `08b05cd18d83`, 45062 bytes.
Proving text (DOM `innerHead`): `Showing: 2 items`, `Search: Olive Oil`,
`2 ITEMS`, rows `Olive Oil Food 3 Feb 2031 …` and `Olive Oil Food 6 May 2030 …`.
The search narrowed: `document.querySelectorAll('[data-testid="product-row"]').length
=== 2` (wait condition met, no report-needed fallback). The shot shows exactly two
rows (image).

- `body` background: `rgb(244, 240, 232)`.
- Wrapper `[data-testid="page-container"]`: transparent (same as 01).
- Heading: no `h1` on the catalog (selector null — same as SG-321r1); substitute the
  count label `2 ITEMS`, 13 px, Instrument Sans stack, paper-on-ink ≈15.47.
- Body/button fonts: Instrument Sans stack (DOM).
- Buttons (all numeric): `Switch to dark theme` 15.47; `Live` (active, ink bg /
  paper text) 15.47; `Gone` 15.47; `All (2)` (active) 15.47; `Food (2)` 15.47;
  `Standard Grid` 15.47; `Compact Table` (active) 15.47; `Save search` 15.47;
  `Clear all` 8.69; two `More actions for Olive Oil` 15.47 each.
- Smallest: 13 px; under 13: none. Mono: none.
- Headers in order (DOM `thead th`): `ASSET | NAME | CATEGORY | USE BY | ADDED |
  ACTIONS` — a `Use by` column, no `Status`, no `Dimensions/Specs`.
- Every `Olive Oil` row's date (DOM `[data-testid="use-by-cell"]`): `3 Feb 2031`,
  `6 May 2030` (in row order; image shows the same two dates).
- Row buttons' accessible names (DOM): `More actions for Olive Oil` × 2.
- Layout: the probe flags `wraps: true` on the two `...` buttons (rect 25×26,
  lineHeight 16 — padding makes height > 1.6× line height), but the image shows
  `...` on one line in each row — no label wraps onto two lines; the flag is a
  probe-heuristic artifact, not a shown wrap. No crowding or clipping in the image.

Design notes: (1) no clipping/crowding (image). (2) no mismatched surfaces; thumbs
are the uploaded 48 px evidence squares (image: olive and green blocks). (3) no text
under 13 px (DOM). (4) weakest live control `Clear all` 8.69:1 (DOM) — link-styled,
readable in the image. (5) no leftover wording; `Photo only` nowhere (DOM `hits`
empty, image shows no such text). (6) dates plain words × 2 (DOM + image). (7) the
two same-name items tell apart at a glance by date + thumb tint (image), not by name
— the date column carries the distinction (image + DOM dates).

## 03 — catalog cards, unfiltered, dark, 390

File `03-catalog-cards-dark-390.png`, sha12 `119ab7c17e55`, 29207 bytes.
Proving text (DOM `innerHead`): `6 ITEMS`, cards `15 Sep 2030 Tomato Soup`,
`No date Pasta`, `15 Jan 2030 Milk`, `No date Rice`, `3 Feb 2031 Olive Oil`,
`6 May 2030 Olive Oil`. The shot shows the first cards (image: Tomato Soup
`15 Sep 2030`, yellow `No date` card below).

- `body` background: `rgb(32, 27, 23)` (dark ground).
- Wrapper `[data-testid="page-container"]`: transparent.
- Heading: none (catalog); substitute `6 ITEMS` 13 px Instrument Sans.
- Buttons (all numeric, all 15.01): `Menu`; `Switch to light theme`; `Live`
  (active); `Gone`; `All (7)` (active); `Food (6)`; `Food & beverages (1)`;
  `Standard Grid` (active); `Compact Table`; `Save search`. No wraps (all
  `wraps: false`, DOM rects e.g. `Food & beverages (1)` 146×26).
- Smallest: 13 px; under 13: none. Mono: none.
- Every card's date (DOM `[data-testid="use-by-date"]`, card order): `15 Sep 2030`,
  `No date`, `15 Jan 2030`, `No date`, `3 Feb 2031`, `6 May 2030` — each Olive Oil
  card carries its date (image shows dates on the visible cards).
- `scrollWidth` 390 vs `clientWidth` 390 (DOM) — no sideways scroll; image shows a
  single column fitting the phone width.
- Facet pills read `All (7)` / `Food (6)` while the list reads `6 ITEMS` (DOM):
  scratch artifact — the archived first soup still counts in facets while the live
  list hides it (explained in the report; not a product claim).

Design notes: (1) no clipping; cards stack full-width (image). (2) surfaces
consistent dark; date chips paper-on-dark (image). (3) no text under 13 px (DOM).
(4) no weak contrast — every button 15.01 (DOM). (5) no leftover wording (DOM hits
empty). (6) dates plain words + `No date` (DOM + image). (7) same-name items: both
Olive Oil cards show distinct dates (DOM list), telling apart at a glance once
scrolled (image shows the top cards only). Phone button sizes (DOM rects): density
and pill buttons 26 px tall (e.g. `Menu` 57×30) — small but tappable targets;
no label wraps (DOM + image).

## 04 — capture form, `olive oil` warning, dark, 1280

File `04-capture-warning-dark-1280.png`, sha12 `202afe6500b0`, 63353 bytes.
Proving text (DOM `warnText`): `You already have these: Olive Oil (use by
3 Feb 2031) Open it / Olive Oil (use by 6 May 2030) Open it`, buttons
`Add another pack | Cancel`. Saving only raised the warning (`samePacks` set,
`createItem` not reached); `Add another pack` was not clicked. The shot shows the
heading, the typed name and the warning (image).

- `body`: `rgb(32, 27, 23)`. Wrapper transparent.
- Heading (`h1.page-header` `Add an item`): Instrument Sans. Body/button: same stack.
- Buttons: `Switch to light theme` 15.01; `Add another pack` dark-paper bg 15.01;
  `Cancel` 15.01; `Add to catalog` maroon `rgb(110, 48, 46)` / paper-light 9.46.
  The warning's buttons ride the theme's control style (DOM bgs), not grey.
- Warning full text + dates + button labels quoted above (DOM).
- Smallest: 11 px; under-13 nodes (DOM): the formats note `PNG, JPG, WebP, TIFF,
  HEIC or PDF, up to 20 MiB per file.` at 11 px (3 text nodes) — the only
  sub-13 text; the hint `Leave it blank and we use the photo's file name` is 13 px
  (image + DOM).
- Mono: none.

Design notes: (1) no clipping; warning box sits above the submit (image). (2) no
white-on-paper leak in dark (image). (3) 11 px formats note persists (DOM + image)
— the one agreed leftover small print. (4) contrast fixed vs SG-321's 2.02:1 —
warning buttons now 15.01 (DOM). (5) wording plain (`not chosen yet`, filename hint)
(image). (6) dates plain words × 2 (DOM). Same-name telling-apart n/a here beyond
the two dated `Open it` links (image).

## 05 — review, duplicate card, light, 1280

File `05-review-duplicate-light-1280.png`, sha12 `e6f40c3f420f`, 75425 bytes.
Proving text (DOM `cardText` head): `Check this item / This may already be in your
catalog / This photo matches Olive Oil (use by 6 May 2030).` The shot shows the
card, the three choices and the fields (image).

- `body`: `rgb(244, 240, 232)`. Wrapper transparent.
- Heading (`h1` `Review workspace`): Instrument Sans. Body/button: same stack.
- Buttons: `Switch to dark theme` 15.47; `It's another pack` maroon 9.46;
  `It's the same pack` paper 15.47; `Decide later` paper 15.47; `Reject` paper 15.47.
- Card full text (DOM): heading + duplicate line + `What we read` + fields +
  `Photo` + `Reject` (quoted in the probe; `cardText` ≤ 900 chars).
- Visible button labels (DOM `cardBtns`): `It's another pack`, `It's the same
  pack`, `Decide later`, `Reject`. `Save edits` / `Accept` / `Hold` visibility
  (DOM): all absent — `saveEdits false`, `acceptBtn false`, `holdBtn false`
  (expected none; image shows none of them).
- Field labels (DOM): `Name`, `Kind of item`, `Status`, `Use by`, `Lot` — plain
  words, no raw key.
- Use-by input: `type: date`, `value: 2032-06-18` (DOM) — a date field carrying
  the new date; rendered locale `06/18/2032` in the image (input, not `innerText`,
  so the ISO scan stays clean).
- No UUID in `innerText` (DOM false); the existing item's id never renders (image
  shows no id; duplicate line names name + date only).
- Smallest 13 px; under-13 none; mono none.

Design notes: (1) no crowding; card breathes (image). (2) white card on paper reads
as an intentional card (image). (3) no text under 13 px (DOM). (4) weakest control
9.46 maroon (DOM) — passes. (5) leftover wording visible in the image: the `Kind of
item` input holds raw `unknown` and the `Status` input holds raw `ACTIVE` (image;
input values, invisible to the `innerText` scan — SG-325 UNCLEAR I8, reported not
failed). The image also shows `Confidence … Source: extraction/deterministic`
lines. (6) date plain words in the duplicate line (DOM), locale in the input
(image). Same-name telling-apart n/a (single card).

## 06 — review, duplicate card, dark, 390

File `06-review-duplicate-dark-390.png`, sha12 `d591dd992d95`, 58439 bytes.
Proving text: same card text as 05 (DOM `cardText` identical head). The shot shows
the card stacked on the phone width (image).

- `body`: `rgb(32, 27, 23)`. Wrapper transparent.
- Buttons (all numeric): `Menu` 15.01; `Switch to light theme` 15.01;
  `It's another pack` maroon 9.46; `It's the same pack` paper-on-dark 15.01;
  `Decide later` 15.01; `Reject` 15.01. No wraps (all `wraps: false`; e.g.
  `It's the same pack` rect 127×26 at (177, 281), lineHeight 0 — one line in the
  image).
- Same visibility/field/type/value/UUID results as 05 (DOM): no `Save edits` /
  `Accept` / `Hold`; labels plain; `type: date`, `value: 2032-06-18`; no UUID.
- `scrollWidth` 390 vs `clientWidth` 390 (DOM) — no sideways scroll (image fits).
- Smallest 13; under-13 none; mono none. The duplicate line wraps onto two text
  lines at 390 (`This photo matches Olive Oil (use by 6` / `May 2030).` in the
  image) — body text reflow, not a button-label wrap.

Design notes: (1) no clipping; page scrolls below `Lot` (image cuts mid-card —
normal scroll, not clipping). (2) dark surfaces consistent (image). (3) no text
under 13 px (DOM). (4) all buttons ≥ 9.46 (DOM). (5) same `unknown` / `ACTIVE`
input values as 05 once scrolled (DOM values; image top shows fields down to Lot).
(6) date line plain words (DOM). Phone button sizes (DOM rects): choices 117/127
×26 with `Decide later` 94×26 on its own row — usable, none wrapping its label
(DOM + image).
