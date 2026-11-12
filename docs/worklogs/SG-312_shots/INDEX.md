# SG-312 shots (SG-313) — paper ground, control font, Inbox names, Menu hidden, proven from the DOM

Scratch app on `127.0.0.1:18313` (backend) / `127.0.0.1:14313` (frontend), temporary SQLite under `output/SG-313-scratch/`, providers off, consent off. All DOM reads through the same DevTools session as the shot (01 retaken once with an improved step query; the retake PNG is byte-identical: sha `3a80f9fd7394`, 73363 bytes, so the proof below covers both takes).

Hash check: `sha256sum *.png | awk '{print substr($1,1,12)}' | sort -u | wc -l` → `4`; 4 files → `4 distinct 12-char prefixes`. No two shots share a hash.

- `01-inbox-light-1280.png`: sha12 `3a80f9fd7394`, 73363 bytes
- `02-expiry-light-1280.png`: sha12 `7acd840d4ce4`, 92382 bytes
- `03-asset-dark-1280.png`: sha12 `73eb8ef9c44f`, 62300 bytes
- `04-pantry-light-375.png`: sha12 `e5629725a63b`, 28399 bytes

## 01 — Inbox, skipped-step import open — light 1280

Proving text (DOM, same session): h1 `"Inbox"`; job card `"Import job Waiting for you"` + date `"Today, 17:59"` (button `aria-label="Import job, Waiting for you"`, date div `Today, 17:59` proves `formatJobDate` Today-branch, not ISO); detail header `"Waiting for you · 6/8 complete · 0 failed · 1 pending"`; candidate row `"sg313-import · Waiting for you · Review"`; review row `"Date needed · High · Open"` + `"Ketchup"`.

- `body` background-color: `rgb(244, 240, 232)` (light `--paper` `40 35.3% 93.3%`).
- Main wrapper `[data-testid="page-container"]` background-color: `rgba(0, 0, 0, 0)` (transparent; the paper shows from `body`).
- Heading `h1.page-header` (`"Inbox"`) font-family: `"Instrument Sans Variable", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`, 24px, color `rgb(28, 25, 23)` on `rgb(244, 240, 232)`, contrast `15.39`.
- Body node `div` (`text="StorageGenieMenuCatalogPantryCaptureInbo"`, the page root text) font-family: same Instrument Sans stack, 16px, color `rgb(28, 25, 23)` on `rgb(244, 240, 232)`, contrast `15.39`.
- Button `button[aria-label="Switch to dark theme"]` (`"Switch to dark theme"`) font-family: same Instrument Sans stack (proves the `button { font: inherit }` rule; SG-311 read Arial here), 16px, bg `rgb(255, 255, 255)`, color `rgb(28, 25, 23)`, effective bg `rgb(255, 255, 255)`, contrast `17.49`.
- Every visible `button` (text | bg | color | font-size):
  - `"Switch to dark theme"` | `rgb(255, 255, 255)` | `rgb(28, 25, 23)` | 16px — white `--card` on paper, measured not guessed.
  - `"Import job, Waiting for you"` (job card) | `rgb(244, 240, 232)` | `rgb(25, 25, 25)` | 16px — paper, ink text.
- Smallest computed font-size among visible text nodes: `13px` (element `a "Catalog"`); every text node under 13px: none (`under13: []`).
- Menu button `.nav-menu-toggle` computed `display`: `none` (expected `none` at 1280).
- Steps as rendered (Selected-job section, `strong` parent text):
  - `Validating input: Done`
  - `Tidying the details: Done` (NORMALIZING → plain name)
  - `Checking the file: Done` (EXTRACTING_DETERMINISTIC_SIGNALS → plain name)
  - `Analyzing with ai: Skipped (AI off)` (skipped, never Done)
  - `Building candidates: Skipped (AI off)` (skipped, never Done)
  - `Looking for duplicates: Done` (DEDUPLICATING → plain name)
  - `Your review: Waiting for you` (AWAITING_REVIEW → plain name)
  - `Saving: In progress` (COMMITTING PENDING → plain name + In progress)
  - Header `Waiting for you · 6/8 complete · 0 failed · 1 pending`.
- Job date as rendered: `Today, 17:59` (all job cards: `["Today, 17:59"]`).
- Absence in `document.body.innerText` (1280): `optimistic concurrency:absent`, `blueprint:absent`, `Phase 0:absent`, `AWAITING_REVIEW:absent`, `consent_disabled:absent`, `If-Match:absent`, `evidence state:absent`, `per-press:absent`, `Import <hex> (/Import [0-9a-f]{8}/):absent`.

## 02 — Expiry, every tier with an item — light 1280

Proving text: h1 `"Expiry"`; sub `"Food and other dated things, soonest first."`; buckets `Expired (1)`, `This week (2)`, `This month (2)`, `Safe (2)`, `Unresolved (2)`; rows Milk/Eggs/Cheese/Untitled item/Yogurt/Warranty Papers/Rice.

- `body`: `rgb(244, 240, 232)`; wrapper `[data-testid="page-container"]`: `rgba(0, 0, 0, 0)`.
- Heading `h1.page-header` (`"Expiry"`): Instrument Sans stack, 24px, `rgb(28, 25, 23)` on `rgb(244, 240, 232)`, contrast `15.39`.
- Body `p(first)` (`"Food and other dated things, soonest first."`): Instrument Sans stack, 13px, `rgb(102, 98, 93)` (`--ink-muted`) on `rgb(244, 240, 232)`, contrast `5.32`.
- Button `button[aria-label="Switch to dark theme"]`: Instrument Sans stack, 16px, bg `rgb(255, 255, 255)`, color `rgb(28, 25, 23)`, contrast `17.49`.
- Every visible `button`: only `"Switch to dark theme"` | `rgb(255, 255, 255)` | `rgb(28, 25, 23)` | 16px. No Read/Dismiss buttons (Unread reminders 0 → `None`); the Shelf-life filter is a `select`, not a button.
- Smallest font-size: `13px` (`a "Catalog"`); under 13px: none.
- Menu `.nav-menu-toggle` display: `none`.
- Tier pills `[data-testid="tier-pill"]` as rendered: `["Use first", "Use soon", "Upcoming", "Upcoming", "Long lead", "Safe"]` (critical→Use first, urgent→Use soon, upcoming×2, long_lead→Long lead, safe→Safe; expired Milk carries no pill, tier null by engine rule).
- Absence: all eight strings `absent`, `Import <hex>:absent` (same quote as 01).

## 03 — Asset page, food item with a date — dark 1280

Proving text: h1 `"Milk"`; `"Live · 1000 ml left"` (quantityLeftText, not `qty`); `"Enrich costs up to $0.05 a press"` (not per-press cap); `"Date confirmed"` (labelExpiryState, not evidence state); `"Manual expiry entry"`; evidence thumb (red generated PNG).

- `body`: `rgb(32, 27, 23)` (dark `--paper` `26.7 16.4% 10.8%`).
- Wrapper `[data-testid="page-container"]`: `rgba(0, 0, 0, 0)`.
- Heading `h1` (`"Milk"`): Instrument Sans stack, 24px, `rgb(245, 245, 244)` on `rgb(32, 27, 23)`, contrast `15.64`.
- Body `div` (page root text `StorageGenieMenu…MilkEditLive · 1000 ml left…`): Instrument Sans stack, 16px, `rgb(245, 245, 244)` on `rgb(32, 27, 23)`, contrast `15.64`.
- Button `button[aria-label="Switch to light theme"]`: Instrument Sans stack, 16px, bg `rgb(28, 26, 24)` (dark `--card`), color `rgb(245, 245, 244)`, contrast `15.90`.
- Every visible `button` (text | bg | color | size):
  - `Switch to light theme` | `rgb(28, 26, 24)` | `rgb(245, 245, 244)` | 16px
  - `Edit` | `rgb(28, 26, 24)` | `rgb(245, 245, 244)` | 16px — dark `--card`, measured (the white-`--card` REMAINING is a light-theme reading; dark proves the token follows the theme).
  - `Enrich` | `rgb(110, 48, 46)` | `rgb(250, 250, 249)` | 16px — primary.
  - `Save shelf life` | `rgb(110, 48, 46)` | `rgb(250, 250, 249)` | 16px
  - `Used up` | `rgb(15, 14, 13)` | `rgb(245, 245, 244)` | 13px
  - `Thrown away` | `rgb(15, 14, 13)` | `rgb(245, 245, 244)` | 13px
  - `Given away` | `rgb(15, 14, 13)` | `rgb(245, 245, 244)` | 13px
  - `Save date` | `rgb(110, 48, 46)` | `rgb(250, 250, 249)` | 16px
  - `Clear expiry date` | `rgb(28, 26, 24)` | `rgb(245, 245, 244)` | 16px — dark card.
  - `Attach evidence` | `rgb(38, 35, 32)` | `rgb(214, 211, 209)` | 16px
  - (Native `Choose Files` file input is not a `button` in the DOM read; seen in the PNG as a white control on dark — noted in design notes.)
- Smallest font-size: `13px` (`a "Catalog"`); under 13px: none.
- Menu display: `none`.
- Absence: all eight `absent`, `Import <hex>:absent`.

## 04 — Pantry with the header — light 375

Proving text: h1 `"Pantry"`; `"7 ITEMS"`; `"What you have, and what to use first."`; `USE SOON` Milk `EXPIRED Expired 5 days ago 1000 ml left`, Eggs `Use today 12 left`, Cheese `Use in 3 days`; `EVERYTHING` repeats.

- `body`: `rgb(244, 240, 232)`; wrapper `[data-testid="page-container"]`: `rgba(0, 0, 0, 0)`.
- Heading `h1.page-header` (`"Pantry"`): Instrument Sans stack, 24px, `rgb(28, 25, 23)` on paper, contrast `15.39`.
- Body `p(first)` (`"What you have, and what to use first."`): Instrument Sans stack, 13px, `rgb(102, 98, 93)` on paper, contrast `5.32`.
- Button `button text="Menu"` (`"Menu"`): Instrument Sans stack, 13px, bg `rgb(244, 240, 232)` (paper), color `rgb(25, 25, 25)`, contrast `15.47`.
- Every visible `button` (25 total; white `--card` controls measured):
  - `Menu` | paper `rgb(244, 240, 232)` | `rgb(25, 25, 25)` | 13px
  - `Switch to dark theme` | `rgb(255, 255, 255)` | `rgb(28, 25, 23)` | 16px
  - Tile image buttons `Open Milk/Eggs/Cheese/...` (7) | `rgba(0, 0, 0, 0)` | `rgb(0, 0, 0)` | 16px (transparent image buttons)
  - Tile controls (each tile): `Edit` (amount tiles) or `Take off 1`/`−1` (counted Eggs) + `Use it up` | all `rgb(255, 255, 255)` | `rgb(25, 25, 25)` | 13px — white `--card` on paper, measured on every tile (the SG-312 REMAINING, now proven).
- Smallest font-size: `13px` (`button "Menu"`); under 13px: none.
- Header: `nav` height `93px`; children `getBoundingClientRect().top`: logo `a` 16 (h 24), `Menu` button 13 (h 30), `.nav-menu` div 0 (h 0, collapsed `data-open=false`), theme button 12 (h 32), `Import Asset` link 52 (h 28). Tops `16, 13, 0, 12, 52` are not equal → children sit on **two rows** (Import drops under the logo+Menu row at 375). Menu `display` is `flex` (visible, expected below 768).
