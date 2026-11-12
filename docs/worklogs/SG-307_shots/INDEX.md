# SG-307 shots INDEX — DOM proofs (SG-316, Muse xhigh)

Scratch household `01a1d127-e2ec-7a30-a242-d6821d8f16c4` (SG-316 Scratch, second household; first household `01a1d127-9efc-...` holds one orphan Milk from the first seed attempt and is never selected: `localStorage household_id` is set to the second on every shot). 11 assets in the shot household: Milk 1000 ml expired 2026-11-07 (amount, expired), Eggs 12 piece 2026-11-12 (counted, today), Apples 5 piece 2026-11-13, Cheese 200 g 2026-11-15, Yogurt 150 g 2026-11-20, noname 250 g 2026-11-20 (filename-stem name; truly nameless asset `01a1d128-...` display_name null, 1 piece, 2026-11-18), Rice 1000 g 2027-02-10 (safe), Ketchup 500 ml dateless (food, unresolved), Wrench 1 piece non_perishable (non-food), Warranty Papers documents_other 2026-12-27. Catalog status: all `raw` → `Photo only` x11 (the API without a provider keeps every asset raw; no `processed`/`rendered` was reachable — one status only, stated, not hidden). Counts: catalog `11 ITEMS` / `Showing: 11 items`; Pantry `9 ITEMS` (9 food_beverages). Skipped-step import `01a1d127-e4df-...` state `AWAITING_REVIEW`, `ANALYZING_WITH_AI {"status":"skipped","reason":"consent_disabled"}`, `BUILDING_CANDIDATES {"status":"skipped","reason":"consent_disabled"}` (run output quoted in SG-316 report).
Panel opened by a click on a card through the same DevTools session: `Array.from(document.querySelectorAll('[data-testid="product-card"]')).find(el=>text.includes('Milk')).click()` (grid forced first by clicking `Standard Grid`; table is the default at 1280, grid has the cards). 03 keeps the Photo tab; 04 then clicks the `Cut-out` role=tab. Inbox opened by `button[aria-label*="Import job"]` click. Asset 07 is `/assets/<milk>?household_id=<hid>`, file input scrolled into view.
Theme set the way SG-311 did: `localStorage sg-theme` light/dark + `household_id`, then reload. Chrome `chrome-headless-shell-1208`, `--user-data-dir` under scratch, DevTools WebSocket, `Page.captureScreenshot`. Viewports 1280x900 (01–04,06,07) and 375x900 mobile (05).

## Files (sha256-12, bytes; no two share a hash)

- 01-catalog-light-1280.png sha `4d6dda96041d` 50241
- 02-catalog-dark-1280.png sha `9eba1ee0876c` 50075
- 03-panel-photo-light-1280.png sha `3d383b27ee0b` 65754
- 04-panel-cutout-dark-1280.png sha `780e916576e5` 66034
- 05-pantry-light-375.png sha `829902446b3f` 31125
- 06-inbox-light-1280.png sha `07bc0208d93a` 72106
- 07-asset-dark-1280.png sha `4bc2e47cf66d` 66487
- Distinct-hash check: `7 files, 7 distinct 12-char prefixes (4d6dda96041d, 9eba1ee0876c, 3d383b27ee0b, 780e916576e5, 829902446b3f, 07bc0208d93a, 4bc2e47cf66d)` — quoted from the script output; no two shots share a hash.

## Per-shot proofs (all read through the same DevTools session)

### 01 catalog light 1280
- Proving text: `[data-testid="catalog-count"]` `11 ITEMS`; `[data-testid="catalog-showing"]` `Showing: 11 items`; category pills `All (11)`, `Documents/other (1)`, `Food & beverages (9)`, `Non-perishable (1)` (screenshot shows `Documents/other`, `Food & beverages` with counts — plain pill labels with counts).
- body `rgb(244, 240, 232)` (light `--paper` 40 35.3% 93.3%); wrapper `[data-testid="page-container"]` `rgba(0, 0, 0, 0)` (transparent; paper shows from body).
- Heading: catalog has no `h1`; heading is `[data-testid="catalog-count"]` `11 ITEMS`, font `"Instrument Sans Variable", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` (cntFam, DOM-read). Body node (page-container text: table head `11 ITEMS ASSET NAME CATEGORY…`) font same Instrument Sans stack (bodyNodeFam). Button (theme toggle `Switch to dark theme`) same Instrument Sans stack.
- Every visible button (10): `Switch to dark theme` paper `rgb(244,240,232)`/`rgb(25,25,25)`; `Live` ink `rgb(25,25,25)`/`rgb(244,240,232)` (active); `Gone` paper/paper-ink; `All (11)` ink/paper (active); `Documents/other (1)` paper; `Food & beverages (9)` paper; `Non-perishable (1)` paper; `Standard Grid` ink/paper (active); `Compact Table` paper; `Save search` paper (disabled). All paper or ink, none white `--card` `rgb(255,255,255)`, measured.
- Smallest font-size `13px`; under-13 nodes `[]`; mono nodes `[]` (no `font-family` contains `mono`).
- Contrast (WCAG from the two DOM-read colours, Python recompute): button `Switch to dark theme` `15.47` (25,25,25 on 244,240,232); heading/body use the same ink-on-paper pair `15.47` (heading fg is the DOM-read button ink on the same page, same `--ink`/`--paper` tokens — disclosed proxy: heading `color` was not separately collected in PROOF_JS; the pair is the page's own ink/paper tokens, comparison named here).
- Border-radius: card `0px`, well `0px`, button `0px` (all three DOM-read, expected `0px`).
- Count header `11 ITEMS`; showing `Showing: 11 items`; every card status `Photo only` x11 (badges list, all `Photo only`); timestamp: grid renders no timestamp (finding — table view on the same household renders `6 min ago`, `7 min ago` x4, quoted from the table-view run `proofs.json` agoTexts; the grid shot shows no `ago` node).
- Menu `.nav-menu-toggle` display `none` (1280, expected `none`).
- Absence (`document.body.innerText`): `optimistic concurrency:absent`, `blueprint:absent`, `Phase 0:absent`, `AWAITING_REVIEW:absent`, `consent_disabled:absent`, `If-Match:absent`, `Source Only:absent`, `Bounding-box:absent` (all quoted).

### 02 catalog dark 1280
Same as 01 on dark: body `rgb(32, 27, 23)` (dark `--paper` 26.7 16.4% 10.8%, comparison to `tokens.css:71`); wrapper transparent; heading `11 ITEMS` Instrument Sans; body Instrument Sans; button `Switch to light theme` Instrument Sans `rgb(32,27,23)`/`rgb(244,240,232)`; 10 buttons, all paper/ink swapped, none white; min `13px`, under `[]`, mono `[]`; button contrast `15.01`; card/well/button `0px`; count `11 ITEMS`, showing `Showing: 11 items`, badges `Photo only` x11; timestamp none in grid (same finding; table-view timestamp `7 min ago` quoted); Menu `none`; all eight absence strings absent.

### 03 panel Photo light 1280 (Milk, Photo tab)
- Proving text: drawer `[data-testid="drawer-title"]` Milk (screenshot shows `Milk` + `Food & beverages` pill); tabs `Photo:true`, `Cut-out:false`, `In a scene:false` (tab names as rendered, Photo selected — DOM `aria-selected`).
- body `rgb(244,240,232)`, wrapper transparent; heading fallback `11 ITEMS` Instrument Sans (catalog behind drawer; drawer title `Milk` inherits the same stack — drawer title element font was not separately collected, disclosed); body Instrument Sans; button Instrument Sans.
- Buttons (20 visible: 10 toolbar + 10 drawer): toolbar same 10 as 01 (paper/ink); drawer: `Close inspector` paper, `Photo` ink/paper active, `Cut-out` paper, `In a scene` paper, `Save changes` ink/paper, `−1` paper, `+1` paper, `Used up`/`Thrown away`/`Given away` paper, `Re-isolate Asset` paper, `Generate Context Scene` ink/paper. All paper/ink, none white, measured.
- Min `13px`, under `[]`, mono `[]`; button contrast `15.47`; card `0px`, well `0px`, button `0px`.
- Empty-state: Photo tab with a photo has no empty state (`sourceEmptyText:null`, correct — the viewer shows the Milk image alt; screenshot shows the image area with `Milk` alt text and a broken-image icon — finding below); Cut-out empty `No cut-out yet.` is on 04, not here.
- Kind of item `#drawer-category-input` value `Food & beverages`; pill `[data-testid="drawer-category"]` `Food & beverages` (taxonomy words, matches `labels.ts:106`).
- Panel `innerText` none of `Bounding-box` (false), `Version` (false), `If-Match` (false), `Isolated Cutout` (false), `AI stages` (false) — all quoted absent.
- Menu `none`; body absence all eight absent.

### 04 panel Cut-out dark 1280 (Milk, Cut-out tab)
- Tabs `Photo:false`, `Cut-out:true`, `In a scene:false` (Cut-out selected); empty-state `[data-testid="cutout-honest-state"]` `No cut-out yet.` (one line, quoted); Kind `Food & beverages`, pill same.
- body `rgb(32,27,23)`, wrapper transparent; fonts all Instrument Sans (same note as 03 for drawer title).
- Buttons (20): same as 03 on dark tokens (paper `rgb(32,27,23)`, ink `rgb(244,240,232)`); `Save changes` ink/paper; all measured, none white.
- Min `13px`, under `[]`, mono `[]`; button contrast `15.01`; card/well/button `0px`.
- Drawer absence five strings all false; Menu `none`; body eight absent.

### 05 Pantry light 375
- Proving text: `h1.page-header` `Pantry`; `[data-testid="pantry-count"]`? count `9 ITEMS` (screenshot shows `9 ITEMS`); `What you have, and what to use first.`; `USE SOON`; `Milk EXPIRED Expired 5 days ago 1000 ml left`; `Eggs Use today 12 left`; `Apples Use by tomorrow 5 left`; `Cheese Use in 3 days 200 g left`.
- body `rgb(244,240,232)`, wrapper transparent; h1 Instrument Sans; body `p` Instrument Sans; button `Menu` Instrument Sans.
- Header: `nav` height `57px`; children tops `A:16, BUTTON Menu:13, DIV nav-menu:0 (h 0, collapsed), BUTTON theme:12, A Import:14` — ignoring the collapsed menu (h 0), tops 12–16 span 4px (expected one row: tops within 4px — quoted, passes; screenshot shows one row: logo, Menu, toggle, import icon, no `Import Asset` text — the 480px media rule hides `.sg-import-label`, proven by the icon-only import link).
- Tile buttons bg paper, not white: `Edit`/`Use it up`/`−1` all `rgb(244,240,232)` (paper), e.g. `Edit rgb(244,240,232)`, `Use it up rgb(244,240,232)`, `−1 rgb(244,240,232)` — measured on all 44 visible buttons; image buttons (`No photo yet Milk`, `Eggs` etc.) transparent `rgba(0,0,0,0)`, not white.
- Min `13px`, under `[]`, mono `[]`; Menu display `flex` (visible at 375, expected); body eight absent.
- Button contrast e.g. `Menu` `15.47`.

### 06 Inbox light 1280 (skipped-step import open)
- Proving text: `h1` `Inbox`; `Import jobs`; job card `Import job, Waiting for you`, `Today, 19:06` (date div, plain `Today, 19:06`, not ISO); detail `Waiting for you · 6/8 complete · 0 failed · 1 pending`; steps `Validating input: Done`, `Tidying the details: Done`, `Checking the file: Done`, `Analyzing with ai: Skipped (AI off)`, `Building candidates: Skipped (AI off)`, `Looking for duplicates: Done`, `Your review: Waiting for you`, `Saving: In progress` (skipped steps read `Skipped (AI off)`, never `Done` — quoted); candidate `import · Waiting for you · Review`; review queue `Date needed · High · Open`, subject `Ketchup`, `Review` link.
- body paper, wrapper transparent; h1/body/button all Instrument Sans.
- Buttons (2 visible): theme toggle paper, job card paper `rgb(244,240,232)`/`rgb(25,25,25)`; review `Resolve` buttons (if any open tasks without data_required) paper — measured; none white.
- Review status select `rgb(244,240,232)` (expected paper — quoted).
- Min `13px`, under `[]`, mono `[]`; button contrast `15.47`; Menu `none`; body eight absent.

### 07 Asset dark 1280 (Milk, file input in view)
- Proving text: `h1` `Milk` (DOM `h1Text Milk`); `Manual expiry entry`; `Date confirmed`; `11/07/2026` date input; `Evidence`; `Choose Files No file chosen Attach evidence`; `Details` table; `History Asset Create — 2026-11-12T19:06:54…` (ISO timestamps in History — finding).
- body `rgb(32,27,23)`, wrapper transparent; h1/body/button Instrument Sans.
- Buttons (10): theme toggle dark paper, `Edit` dark card `rgb(28,26,24)`, `Enrich`/`Save shelf life`/`Save date` primary `rgb(110,48,46)` on `rgb(250,250,249)`, `Used up`/`Thrown away`/`Given away` dark `rgb(32,27,23)`, `Clear expiry date` dark, `Attach evidence` dark. Measured.
- File input `rgb(32,27,23)` bg, `rgb(244,240,232)` color (expected paper — quoted; screenshot shows `Choose Files` on dark paper).
- Min `11px`; under-13: `Thumbnail unavailable 11px` (one node, quoted — finding); mono `[]`; Menu `none`; body eight absent; button contrast e.g. theme toggle `15.01`.
- Details table shows `[object Object]` for Shelf life / Expiry date values and raw `food_beverages`, `ACTIVE`, `ml` (findings — leftover developer wording).

## Cross-shot
- No ISO date in catalog/inbox/pantry timestamps (all `X min ago`, `just now`, `Today, 19:06`, `Expired 5 days ago`, `Use today`, `Use by tomorrow`, `Use in 3 days`); ISO appears only in asset History (`2026-11-12T19:06:54…`) and the date input value `11/07/2026` (locale input, not ISO text) — quoted as findings on 07.
- Status words: all catalog cards `Photo only` (true — no cut-out exists without a provider); inbox `Skipped (AI off)` / `Waiting for you` / `In progress` (true — the job waits for review); `Saving: In progress` for a waiting job reads as in-progress while waiting (wording finding, also noted in SG-313).
- Category/heading: catalog pills show raw keys `food_beverages`, `documents_other`, `non-perishable` while the panel shows `Food & beverages` and pantry shows food only — the catalog card category chips contradict the panel taxonomy (finding on 01–02; screenshots prove both spellings).
