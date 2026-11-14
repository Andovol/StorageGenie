# SG-304 shots retake (SG-321r1) — DOM proofs

One browser (`HeadlessChrome 145.0.7632.6`, chrome-headless-shell 1208), one page
target, one DevTools WS session for every step. Theme set via
`localStorage["sg-theme"]` then reload (SG-311); viewport via
`Emulation.setDeviceMetricsOverride` (1280x900, phone 390x844); inputs filled with
the native value setter plus `input` and `change` events; clicks via
`button.click()` in-page; screenshots via `Page.captureScreenshot`; counts via
in-page `fetch(/v1/assets)`. Driver returns quoted inline:
`fill01 set:Rice`, `submit01 clicked`, `fill02 set:olive oil `, `submit02 clicked`,
`click05 clicked`, `search05 set:Olive Oil`, `countBefore 6`, `countAfter 7`.

Font stack everywhere (computed): `"Instrument Sans Variable", system-ui,
-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.

## Distinct-hash check

```
2bcc7ac2bc88934d51c5c2c9e1db44640ae3eb7d5f3e098941f157a46b403e90  01-same-name-warning-one-light-1280.png
a479faff30278a491de46878b5e6876aee4711bfd88efa3c489b7bdcbe95798f  02-same-name-warning-two-dark-1280.png
0fda626a414bc55203e745b09bf806cac1f960dcdf5eb23f59eed8fcad24a3da  03-duplicate-card-light-1280.png
6ad6ac22473d193a5c51c9096c2b830de8c29fae90a48a7784fe7b4d484e503a  04-duplicate-card-dark-390.png
931d20cae24ebc415840a13ed02f5fec27cec37be2a85e4e0151e87a25b60a30  05-three-olive-oils-light-1280.png
```

5 distinct of 5 shots. No two shots share a hash.

## 01 — Add form, `Rice`, one match (light, 1280)

- File `01-same-name-warning-one-light-1280.png`, sha12 `2bcc7ac2bc88`, 52183 bytes.
- Proving text (warning `innerText`): `You already have Rice (use by 12 Aug
  2030). / Add another pack / Open it / Cancel`. The form stayed on the capture
  page (submit showed the warning instead of creating — no navigation happened).
- `body` background `rgb(244, 240, 232)`; main wrapper `#root` (no `main` on this
  page) background `rgba(0, 0, 0, 0)`.
- Heading: `h1` `Capture — Manual Create`, 24px, Instrument Sans stack,
  `rgb(28, 25, 23)`, contrast 15.39:1.
- Body node: `StorageGenie` header wordmark, 20px, Instrument Sans stack,
  `rgb(25, 25, 25)` on paper, 15.47:1 (measured on the catalog page in the same
  light theme; the header is the shared AppShell).
- Button font: first visible button is the icon-only theme toggle (`label ""`,
  32x32) in the Instrument Sans stack; e.g. `Add another pack` uses the same stack.
- Every visible `button` (label | bg | color | ratio): `""` | paper |
  `rgb(25, 25, 25)` | 15.47; `Add another pack` | `rgb(239, 239, 239)` |
  `rgb(110, 48, 46)` | **8.59**; `Cancel` | same | same | **8.59**;
  `Create asset` | `rgb(110, 48, 46)` | `rgb(250, 250, 249)` | **9.46**. The
  header `Import Asset` control is an anchor (`A`), not a button (tag read from
  the DOM); `Open it` in the warning is a `Link`, labels read via `warnLinks`.
- Smallest computed `font-size` among visible text nodes: 11px. Nodes under
  13px: `Left blank, we use the photo's filename` 11px; `PNG, JPG, WebP, TIFF,
  HEIC or PDF, up to` 11px; `20 MiB` 11px; `per file.` 11px.
- Contrasts: heading 15.39, body wordmark 15.47, warning buttons 8.59 / 8.59,
  warning text (`rgb(28, 25, 23)` on `rgb(236, 235, 233)`) 14.68.
- `mono` in any visible text node's font: none.
- Warning dates: `12 Aug 2030`. Warning buttons: `Add another pack`, `Cancel`;
  warning links: `Open it`.
- Forbidden strings (`[object Object]`, `duplicate_of_asset`, `duplicate_linked`,
  `as_new_pack`, `Exact duplicate of asset`, `Untitled asset`, `noname`,
  `AWAITING_REVIEW`, `If-Match`): none in `document.body.innerText`. ISO regex
  `\d{4}-\d{2}-\d{2}`: no hit. `Thumbnail unavailable`: 0 hits.
- `scrollWidth` 1280 vs `clientWidth` 1280.

## 02 — Add form, `olive oil `, two matches (dark, 1280)

- File `02-same-name-warning-two-dark-1280.png`, sha12 `a479faff3027`, 57378 bytes.
- Proving text (warning `innerText`): `You already have these: / Olive Oil (use by
  3 Feb 2031) Open it / Olive Oil (use by 6 May 2030) Open it / Add another pack /
  Cancel`. Lower-case input with a trailing space still matched both packs
  (trimmed, case-insensitive compare in `findSameNamePacks`).
- `body` background `rgb(32, 27, 23)`; wrapper `#root` transparent.
- Heading: `h1` `Capture — Manual Create`, 24px, Instrument Sans stack,
  `rgb(245, 245, 244)`, contrast 15.64:1.
- Body node: `StorageGenie` wordmark, 20px, same stack, `rgb(244, 240, 232)` on
  `rgb(32, 27, 23)`, 15.01:1 (same-theme catalog read, shared header).
- Button font: icon-only theme toggle first, Instrument Sans stack throughout.
- Every visible `button`: `""` | `rgb(32, 27, 23)` | `rgb(244, 240, 232)` | 15.01;
  `Add another pack` | `rgb(239, 239, 239)` | `rgb(213, 156, 154)` | **2.02**;
  `Cancel` | same | same | **2.02**; `Create asset` | `rgb(110, 48, 46)` |
  `rgb(250, 250, 249)` | **9.46**.
- Smallest: 11px; under 13px: the same four helper/format-note nodes as 01.
- Contrasts: heading 15.64, body 15.01, warning buttons 2.02 / 2.02, warning text
  (`rgb(245, 245, 244)` on `rgb(46, 42, 38)`) 13.05.
- `mono`: none. Warning dates: `3 Feb 2031`, `6 May 2030`. Buttons:
  `Add another pack`, `Cancel`; links: `Open it`, `Open it`.
- Forbidden: none. ISO: none. `Thumbnail unavailable`: 0.
- `scrollWidth` 1280 vs `clientWidth` 1280.

## 03 — Duplicate review card (light, 1280)

- File `03-duplicate-card-light-1280.png`, sha12 `0fda626a414b`, 82627 bytes.
- Card `innerText` (first `div[role="alert"]`): `Possible duplicates or
  collisions / This photo matches Olive Oil (use by 6 May 2030). / It's another
  pack / It's the same pack / Decide later / This match is advisory; review it
  before accepting.` The card renders (SG-322 fix: open duplicate reads with no
  `asset_id`, so `ReviewPage` takes the `CandidateCard` branch, not
  `In your catalog`).
- Every visible button's label: `""`, `It's another pack`, `It's the same pack`,
  `Decide later`, `Save edits`, `Reject`.
- `Accept` visible: no. `Hold` visible: no (the only hold-like control is
  `Decide later`). `Save edits` visible: yes — known gap G-1, photographed as is.
- Existing item's id (`01a1dbaf-ba79-…`) in `innerText`: no. (The candidate id
  `01a1d…af28` does appear in the `Candidate …` heading; that is the candidate,
  not the existing item.)
- `body` background `rgb(244, 240, 232)`; wrapper `#root` transparent.
- Heading: `h1` `Review workspace`, 24px, Instrument Sans stack,
  `rgb(28, 25, 23)`, 15.39:1.
- Body node: `StorageGenie` wordmark 20px, 15.47:1 (same-theme read).
- Button font: Instrument Sans stack on all six (first button is the 32x32
  header icon button).
- Every visible `button` (label | bg | color | ratio | rect): `""` | paper |
  `rgb(25, 25, 25)` | 15.47 | 32x32; `It's another pack` | `rgb(110, 48, 46)` |
  `rgb(250, 250, 249)` | **9.46** | 119x26; `It's the same pack` | paper |
  `rgb(25, 25, 25)` | **15.47** | 128x26; `Decide later` | paper | same |
  **15.47** | 94x26; `Save edits` | paper | same | **15.47** | 83x26; `Reject` |
  paper | same | **15.47** | 60x26.
- Smallest: 11px (`Confidence:` / `0.97` / `Source:` / `extraction` / `Unknown` /
  `deterministic` lines). Under 13px also: `State:`, `proposed`, `· Job:`,
  job-id text at 12px.
- Contrasts: heading 15.39, body 15.47, card buttons 9.46 / 15.47 / 15.47.
- `mono`: none. Forbidden: none. ISO in `innerText`: none (the candidate field
  input visibly holds `2032-06-18`, but input values are not part of
  `innerText`, so the check reads clean — see design notes). Thumb: 0.
- `scrollWidth` 1265 vs `clientWidth` 1265 (viewport 1280 minus scrollbar).

## 04 — Duplicate review card (dark, 390)

- File `04-duplicate-card-dark-390.png`, sha12 `6ad6ac22473d`, 135869 bytes.
- Card `innerText`: identical to 03 (`This photo matches Olive Oil (use by
  6 May 2030).` plus the three choices and the advisory line).
- Button labels: `Menu`, `""`, `It's another pack`, `It's the same pack`,
  `Decide later`, `Save edits`, `Reject`. `Accept`: no. `Hold`: no.
  `Save edits`: yes (G-1). Existing item id in `innerText`: no.
- `body` background `rgb(32, 27, 23)`; wrapper `#root` transparent.
- Heading: `h1` `Review workspace`, 24px, Instrument Sans stack,
  `rgb(245, 245, 244)`, 15.64:1.
- Body node: `StorageGenie` wordmark 20px, 15.01:1 (same-theme read).
- Every visible `button` (label | bg | color | ratio | rect): `Menu` |
  `rgb(32, 27, 23)` | `rgb(244, 240, 232)` | 15.01 | 57x30; `""` | same | same |
  15.01 | 32x32; `It's another pack` | `rgb(110, 48, 46)` | `rgb(250, 250, 249)` |
  **9.46** | 119x26; `It's the same pack` | `rgb(32, 27, 23)` | paper-light |
  **15.01** | 128x26; `Decide later` | same | same | **15.01** | 94x26;
  `Save edits` | same | same | **15.01** | 83x26; `Reject` | same | same |
  **15.01** | 60x26.
- Smallest: 11px (same confidence lines as 03, dark colors).
- No visible button wraps its label: every button's `getClientRects().length`
  is 1, and the image shows each label on one line (`It's the same pack` fits at
  128x26). The phone header bar itself occupies two rows in the image (wordmark
  row, then `Menu` / theme / import row) — that is the header wrapping, not a
  button label wrapping.
- `document.documentElement.scrollWidth` 390 vs `clientWidth` 390: no sideways
  scroll.
- `mono`: none. Forbidden: none. ISO: none (same input-value caveat as 03).
  Thumb: 0.

## 05 — Catalog narrowed to `Olive Oil` after `It's another pack` (light, 1280)

- File `05-three-olive-oils-light-1280.png`, sha12 `931d20cae24e`, 47260 bytes.
- The only write in the run: one click on `It's another pack` on the shot-03/04
  card. `GET /v1/assets` item count before the click: 6; after: 7 (both via
  in-page fetch). The decision committed a new pack.
- Catalog proves the narrowed state: search box value `Olive Oil` (DOM),
  `Showing: 3 items` (DOM), three table rows each containing `Olive Oil` (DOM,
  `oliveCount` 4 = 3 rows + the `Search: Olive Oil` filter chip).
- Per-row date text (row `innerText`, `|`-joined): `Olive Oil | Uncategorized |
  Photo only | — | just now | ...`, `Olive Oil | Uncategorized | Photo only | —
  | 4 min ago | ...`, `Olive Oil | Uncategorized | Photo only | — | 4 min ago |
  ...`. Neither the table rows nor the Standard Grid cards (probed read-only
  afterwards: three cards reading `Photo only / Olive Oil / Uncategorized`) print
  an expiry date, so the three pack dates come from in-page detail fetches of
  the three `Olive Oil` assets: `2032-06-18` (the pack the click just created),
  `2031-02-03`, `2030-05-06`.
- No `h1` or `h2` exists on the catalog page (selector query returns null).
  Nearest heading-like text: `Showing:` / `3 ITEMS` lines at 13px, Instrument
  Sans stack, `rgb(25, 25, 25)` on paper (≈15.47:1 by the same colour pair the
  logo read measures at 15.47).
- `body` background `rgb(244, 240, 232)`; main wrapper `main` (this page has a
  `main` element) background `rgba(0, 0, 0, 0)`.
- Body node: `StorageGenie` wordmark 20px, 15.47:1.
- Every visible `button`: `""` (theme toggle) 15.47; `Live` 15.47 (47x26);
  `Gone` 15.47; `All (3)` 15.47; `Uncategorized (3)` 15.47; `Standard Grid`
  15.47; `Compact Table` 15.47; `Save search` 15.47; `Clear all`
  (`rgba(0, 0, 0, 0)` bg, maroon text) **8.69**; three row `...` menus 15.47
  each (24x26, 16px `...`). Header `Import Asset` is an anchor, not a button.
- Smallest: 13px; no text node under 13px.
- `mono`: none. Forbidden: none. ISO: none. Thumb: 0.
- `scrollWidth` 1265 vs `clientWidth` 1265.
