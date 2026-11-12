# SG-319 report — the SG-318 screenshots, proven from the DOM

First line: slice SG-319; model opencode-go/claude-haiku-5-5 (from my runtime; I did not read it from process arguments); effort not stated to me (UNCLEAR); working directory /home/andrei/StorageGenie; remote git@github.com:Andovol/StorageGenie.git; BASE ref origin/automation; resolved BASE commit e16fbaa10eb85d1828f6926c4015e23cd8fbfe98 (`git fetch origin automation` then `git rev-parse origin/automation`); WORK_HEAD at start e16fbaa10eb85d1828f6926c4015e23cd8fbfe98 (equal to BASE; the tree was clean).

Contract: I received no contract version line. I did not read the contract folder.

## Time

Elapsed: start 1794513171, end of teardown 1794513758 (587 s), report written after 1794513791.
- G0 preflight 1794513171–1794513176 (5 s). `docker version` showed a Server section (Engine 29.9.2). Health `curl http://127.0.0.1:8003/v1/health` = 200 at start; live health = 200 again at 1794513791 (end).
- Build 1794513361–1794513365 (3.4 s, `vite build --outDir` into scratch).
- Backend migrations 1794513229 onward; the first backend start held a tool call for about 120 s (my `&&` chain kept the tool's stdout open) and the backend was stopped when that call ended. Restarted as a standalone background command at 1794513401 (health 200 within 2 s).
- Seed: four runs, the last succeeded at 1794513463 (earlier runs failed on the expiry route path, the classification prerequisite, and a binary thumbnail response; each run reset the scratch DB and storage first).
- Shots: run 1 1794513575–1794513677; run 2 1794513697–1794513708 (the reported run).
- Teardown 1794513755–1794513758.

## How the scratch app and servers were started

- Preflight: exactly as the packet, with `DOCKER_CONFIG` and `DOCKER_HOST` set under scratch.
- Database: `DATABASE_URL=sqlite:////home/andrei/StorageGenie/output/SG-319-scratch/sg319.db`, `alembic upgrade head` from `backend/` (rc 0).
- Backend: `nohup venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 18319` from `backend/` in the background, with `STORAGE_ROOT` in scratch, `CORS_ORIGINS=http://127.0.0.1:14319`, `SG_CONSENT=false SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=`. No `.env` exists in `backend/`; the root `.env` is not read from this cwd. PID 762516 (`backend.pid`) returned 200.
- Frontend: `vite build --outDir output/SG-319-scratch/fe-dist` with `VITE_API_BASE=http://127.0.0.1:18319`. Then `nohup node node_modules/vite/bin/vite.js preview --port 14319 --strictPort` from `frontend/` in the background; PID 761207 returned 200. `npx` is not on PATH in this shell, so Vite was called through node.
- Bundle check (`output/SG-319-scratch/fe-dist/assets/index-BqY0gaoy.js`): `grep -o '127\.0\.0\.1:18319' | wc -l` = 7; `grep -o '8003' | wc -l` = 0.
- Test data (through the API only; `seed.py` in scratch): household "SG-319 Scratch"; 12 assets. Food: Juice 500 ml (expiry 2026-11-07, expired), Milk 1000 ml (2026-11-11, expired), Yogurt 4 piece (2026-11-12, today), Eggs 12 piece (2026-11-15), Apples 6 piece (2026-11-13), Bread 1 piece (2026-11-17), Oats 500 g (2027-03-01), Rice 1 kg (2027-06-01), Ketchup 300 ml (no photo, no date), Soup 400 g (no date). Non-food: Wrench (`non_perishable`, 1 piece). One nameless item (no `display_name`). Each photo is a generated PNG uploaded to `POST /v1/evidence` and attached at create time. Expiry via `POST /v1/plugins/expiry-tracker/assets/{id}/classification` then `.../expiry`.
- Photo-fail item: Yogurt. I deleted its stored original and its two derived files (`*_thumb256.jpg`, `*_thumb512.jpg`) under the scratch storage path. Afterwards `GET /v1/evidence/{id}/file` = 404 and `GET /v1/evidence/{id}/thumb/512` = 404 (both printed by the seed).
- Skipped-AI import: `POST /v1/evidence` (receipt image) → `POST /v1/imports` with `{"evidence_ids":[...],"config":{}}` → `POST /v1/imports/{id}/run`. The job reached `AWAITING_REVIEW`. The Inbox page reads "Reading the photo: Skipped (AI off)" and "Making items: Skipped (AI off)" (shot 06 `innerText`). A second import was created and not run, so the Inbox also shows a job whose state is *Not started*.
- Stop: by PID files (`kill $(cat ...)`), no `pkill`. Backend, frontend and Chrome were gone (`kill -0` fails) and both ports returned 000. Scratch removed by exact path (`rm -rf /home/andrei/StorageGenie/output/SG-319-scratch`), confirmed absent.

## Shots

Driver: `output/SG-319-scratch/shoot.mjs` (scratch, removed). Headless Chrome = Playwright `chrome-headless-shell` 1208 from `~/.cache/ms-playwright` (`/usr/bin/google-chrome` was not used), `--user-data-dir` in scratch, DevTools via built-in WebSocket. Theme set by `localStorage["sg-theme"]` before each load. Viewport 1280 x 900. The item panel opened by a real mouse click (`Input.dispatchMouseEvent`) at the centre of the deepest element whose text is "Yogurt" in the catalog (shot 04). Shot 06 opened the job by the same method on the element containing "Waiting for you".

| # | file | state | sha256 (12) | bytes | attempts | proving DOM text (innerText/leaves) |
|---|---|---|---|---|---|---|
| 01 | 01-catalog-light-1280.png | light 1280 | a881867fac95 | 90012 | 1 | "12 ITEMS", "Showing: 12 items", category chips "Food & beverages" (11), "Non-perishable" (1) |
| 02 | 02-asset-dated-food-light-1280.png | light 1280 | 4871b71badda | 61463 | 1 | h1 "Juice"; "Details" h3; "History" h3; Details row "Expiry date → 7 Nov 2026 → You → Kept"; history "Added — Today, 19:57" |
| 03 | 03-asset-no-photo-dark-1280.png | dark 1280 | e0ac25e328d4 | 66555 | 1 | h1 "Ketchup"; html.dark = true; "No evidence attached" (gallery empty text) |
| 04 | 04-item-panel-photo-fails-light-1280.png | light 1280 | e8b30e4dadb1 | 88640 | 1 | panel: "No photo yet." (p, 13 px); title "Yogurt"; "Unit" = piece; no displayed img with naturalWidth 0 |
| 05 | 05-expiry-light-1280.png | light 1280 | 8c79cd9ff07e | 90198 | 1 | h1 "Expiry"; "Use first" x2 (Yogurt, Apples); "Use soon" x2 (Eggs, Bread); "7 Nov 2026 · Expiry date"; "Expired (2)" |
| 06 | 06-inbox-skipped-import-light-1280.png | light 1280 | 6e1e22726f04 | 75331 | 1 | h1 "Inbox"; "Not started" (card 1); "Waiting for you · 6/8 complete · 0 failed · 1 pending"; "Checking your upload: Done"; "Reading the photo: Skipped (AI off)"; "Making items: Skipped (AI off)"; "Saving: Not started" |

Distinct-hash check: `sha256sum docs/worklogs/SG-318_shots/*.png` gives six different 12-character prefixes (a881867fac95, 4871b71badda, e0ac25e328d4, e8b30e4dadb1, 8c79cd9ff07e, 6e1e22726f04); `6 distinct of 6 shots`. The sha values match the INDEX table. The sha of shot 01 in the first run was 75d15f0fda30 (90616 bytes); the reported PNG is the second run's. I did not investigate why the two runs differ.

Per-shot DOM reads (all in `docs/worklogs/SG-318_shots/INDEX.md`, generated by the driver from the page): body and main-wrapper background, font-family of heading / body node / first button, every visible button's text, background and colour, smallest computed font-size, every text node under 13 px, contrast ratios, `mono` check, forbidden-string check on `document.body.innerText`, ISO regex, and the Menu button's computed display.

Checks common to all six shots (quoted from INDEX.md):
- Forbidden strings (`[object Object]`, `food_beverages`, `documents_other`, `non_perishable`, `Thumbnail unavailable`, `Untitled asset`, `noname`, `Analyzing with ai`, `AWAITING_REVIEW`, `consent_disabled`, `If-Match`): "in innerText false" for each, on all six shots.
- ISO regex `\d{4}-\d{2}-\d{2}` in innerText: "none" on all six.
- Menu button: `button.focus-ring.nav-menu-toggle display=none` on all six.
- Visible text with `mono` in font-family: "none" on all six.
- Text nodes under 13 px: "none" on all six. The page minimum is 13 px on all six.
- "Untitled item" probe: x0 on all six. The source literals named in SG-318 were not re-read in this slice.

Shot-specific reads:
- 01: category chips as rendered: "Food & beverages" x11, "Non-perishable" x1; no `_` in any chip (probe "_" x0). Body background `rgb(244, 240, 232)`; main wrapper (`main`) background `rgba(0, 0, 0, 0)`. Heading: no `h1` on this page (probe heading = null). Heading and body-node contrast: n/a (no qualifying node found by the script). Button contrast 15.47:1 (`button.focus-ring` on `rgb(244, 240, 232)`). Buttons: 12 "..." buttons (no label), "Save search", "Live", "Gone", "All (12)", etc.
- 02: Details rows as rendered: "Detail → Value → Source → State → Confidence → Evidence" (header); "Kind of item → Food & beverages → You → Kept"; "Name → Juice → You → Kept"; "Shelf life → Food & beverages → You → Kept"; "Expiry date → Unknown → Rule → Replaced"; "Expiry date → 7 Nov 2026 → You → Kept"; "Amount → 500 → You → Kept"; "Status → Live → You → Kept"; "Unit → ml → You → Kept". History as rendered: "Added — Today, 19:57", "Accepted — Today, 19:57", "Date entered by you — Today, 19:57". h1 "Juice" 24 px, contrast 15.39:1 against `rgb(244, 240, 232)`; body node 5.05:1; button "Edit" bg `rgb(255, 255, 255)`.
- 03: gallery empty text "No evidence attached" (leaf text on the page). Its computed font-size was NOT read by the driver (probe list did not include it); the page minimum of 13 px covers all visible text nodes, so the node is at least 13 px. The text "No photo yet" is absent (probe x0). Dark: body `rgb(32, 27, 23)`, heading contrast 15.64:1, body 11.46:1, button 15.01:1.
- 04: fallback text as rendered "No photo yet." (p, 13 px) inside the panel's photo box. Images on page: the catalog thumbnails (naturalWidth 256) and no displayed `<img>` with naturalWidth 0 ("Displayed images with naturalWidth 0: none"). Panel buttons include "Re-isolate Asset", "Generate Context Scene", "Cut-out", "In a scene", "Save changes", "−1", "+1", "Used up", "Thrown away", "Given away".
- 05: dates as rendered: "7 Nov 2026 · Expiry date" (Juice, Milk, Yogurt, Apples, Eggs, Bread, Oats "1 Mar 2027", Rice "1 Jun 2027"); pills: "Use first" (Yogurt, Apples), "Use soon" (Eggs, Bread); no pill for Oats or Rice ("109 days remaining", "201 days remaining"). Body node contrast 5.32:1 (`rgb(102, 98, 93)` on `rgb(244, 240, 232)`).
- 06: step labels as rendered: "Checking your upload: Done", "Tidying the details: Done", "Checking the file: Done", "Reading the photo: Skipped (AI off)", "Making items: Skipped (AI off)", "Looking for duplicates: Done", "Your review: Waiting for you", "Saving: Not started". Job date "Today, 19:57". Unrun job card: "Not started". Review status select "Open" (image).

## Design notes

Each note names the read or image that shows it.

01 catalog:
- Every one of the 12 rows reads "Photo only" in the Status column (leaf text list), including Juice (500 ml, dated, expired), so the status word does not describe those items. Image shows the same column.
- Dates here are relative ("4 min ago", leaf text) while the asset page shows "Today, 19:57" (shot 02 leaf list) and the Expiry page shows "7 Nov 2026" (shot 05). Three date styles across three screens.
- The page has no heading element (probe heading = null); "12 ITEMS" is the only heading-like text. The image shows no page title.
- 12 action buttons read "..." with no label (button list). Image shows the same column of "..." boxes.
- "DIMENSIONS/SPECS" is "—" on every row (leaf list and image).

02 asset Juice:
- "Shelf life → Food & beverages" repeats "Kind of item → Food & beverages" (Details rows). Both rows show the same category name.
- Two "Expiry date" rows: "Unknown → Rule → Replaced" and "7 Nov 2026 → You → Kept" (Details rows). The replaced row stays on screen.
- The native date input in "Manual expiry entry" shows "11/07/2026" (image) — US order, while the rest of the page uses "7 Nov 2026" (Details row). The input is a native control and is not in the button list.
- The "Edit" button has a white background `rgb(255, 255, 255)` on the cream page `rgb(244, 240, 232)` (button list). The image shows it as a white box.
- "Attach evidence" and "Choose Files" look like a different control family from the rest (image); the native file input's font is not in the DOM button list (UNCLEAR).

03 Ketchup (dark):
- The gallery's empty text reads "No evidence attached" (leaf text), not "No photo yet" (probe x0). The SG-318 wording "No photo yet" in the gallery did not appear for an item with no photo.
- Details row "Amount → 300" omits the unit; the unit is a separate row "Unit → ml" (Details rows, shot 03 leaf list).
- "Edit" bg `rgb(28, 26, 24)` sits on a page `rgb(32, 27, 23)` — a 4-unit difference (button list); the image shows the control only by its outline.
- "Attach evidence" bg `rgb(38, 35, 32)` with text `rgb(214, 211, 209)` (button list) reads as a secondary control; contrast fine (heading 15.64:1, body 11.46:1).

04 Yogurt panel:
- The fallback "No photo yet." renders at 13 px inside the photo box (probe sample: p, 13 px). The Yogurt photo files were removed from scratch (seed output: 404 for file and thumb512). Image shows the grey box.
- The bottom of the panel shows "Re-isolate Asset" and "Generate Context Scene" (button list) — developer-style wording on an owner page. Image crops them below the fold.
- The panel labels "Photo / Cut-out / In a scene" (image) and the "Metadata" block read cleanly.

05 Expiry:
- "Opened countdown" block reads "Days since each cosmetics item was opened, counted against its category's after-opening window." and "No cosmetics items to track." (leaf text) on a food-only page. The wording is developer-style.
- Tier pills appear on four rows only: "Use first" (Yogurt, Apples), "Use soon" (Eggs, Bread) (image and leaf text). Oats and Rice show no pill (leaf text). This matches the SG-318 intent.
- The heading "Expiry" and the line "Food and other dated things, soonest first." (leaf text) agree. No contradictions visible in this shot.

06 Inbox:
- "Waiting for you · 6/8 complete · 0 failed · 1 pending" (innerText) counts the two "Skipped (AI off)" steps as complete: 4 Done + 2 Skipped = 6. A skipped step is not completed work; the status says more than happened.
- "Skipped (AI off)" — "AI off" is developer-style wording (innerText).
- Both job cards read "Import job" (leaf text, image). Neither names its receipt; the file name "receipt-skipped" only appears inside the selected job's list (leaf text).
- "Not started" on the unrun job (leaf text) is consistent with the SG-318 change (PENDING → Not started). The top of the selected job reads "Waiting for you", which matches the step "Your review: Waiting for you".

## Contract, UNCLEAR and REMAINING

- Contract line: none received (see above).
- UNCLEAR: the model and effort I report on the first line come from my runtime, not from process arguments. Effort was not stated to me.
- UNCLEAR: the computed font-size of the shot 03 gallery text "No evidence attached" was not read.
- UNCLEAR: the shot 01 difference in sha between the two runs (75d15f0fda30 vs a881867fac95) is not explained.
- UNCLEAR: "Untitled item" literals in CatalogPage, PantryPage and OpenedCountdownSection are not on these six screens, so none is shown; I did not re-read the source.
- REMAINING (not shown in these screens, per SG-318 report): the `noname` stem in the backend. The seed printed `display_name = noname` for the nameless item via the API; the UI shows "Unnamed item" (probe x1 on shots 01, 04). So the API still returns `noname`; the UI hides it. Not changed (no product bytes in this slice).
- REMAINING: heading contrast n/a on shots 01 and 04 (no `h1` on those pages); body-node contrast n/a on shot 01 and shot 06 (no text node matched the script's length rule). These are gaps in my reads, not passes.
- REMAINING: no shot was retaken with the same click target. Run 1 failed shots 03 and 06 on two attempts each. Cause: 03 waited for "No photo yet" (not on that page); 06 clicked the unrun "Import job" card (image of the failed attempt shows *Not started*). I corrected both targets and reran all six; the reported PNGs are from the rerun.

## Criteria

- A1 — PASS. Preflight proven (Server section, socket listed, `docker version` rc 0); live health 200 at 1794513171 and at 1794513791; phase seconds above.
- A2 — PASS. Scratch app on 18319 and 14319 started in the background; PIDs 762516 and 761207 in `.pid` files; both returned 200; bundle check 7 / 0 (`grep -o ... | wc -l`); skipped-step import made by consent-off and provider `fake` (method above; page shows "Skipped (AI off)").
- A3 — FAIL. Six shots present with hash, size and proving text, and distinct-hash check quoted. Not complete: (1) shot 03's gallery empty text computed font-size not read; (2) heading contrast n/a on 01 and 04; (3) body-node contrast n/a on 01 and 06; (4) heading font-family null on 01 and 04.
- A4 — PASS. Design notes per shot, each naming its read or image.
- A5 — PASS for the bytes. Only `docs/worklogs/SG-319_report.md` and `docs/worklogs/SG-318_shots/` are written. No product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored file, host, provider, container or deploy bytes changed; `frontend/dist` untouched (build went to scratch via `--outDir`); no `/tmp` used. Scratch removed by exact path before this report. `git status` before the report: only `docs/worklogs/SG-318_shots/` untracked; no tracked file modified.
- A6 — Vacuity checked: non-paper body (body is `rgb(244, 240, 232)` / `rgb(32, 27, 23)`, paper, not white); system font on a button (no button in any shot uses a non-Instrument family; the native file input is not a button and is UNCLEAR); uppercase step name (the step names read in sentence case, leaf list shot 06); skipped step reading Done (reads "Skipped (AI off)"); ISO date (regex none); Menu displayed at 1280 (display none on all six); removed string in innerText (all eleven checked "in innerText false"); two shots with one hash (distinct check quoted: 6 of 6); bundle pointing at 8003 (0); server call that did not return (both servers started in background; the first backend start did hold a call for about 120 s — recorded above); scratch left behind (removed, absent).
- A7 — see last line.

Verification: FAIL — A3: shot 03 gallery empty-text computed font-size not read; heading contrast n/a on 01 and 04; body contrast n/a on 01 and 06; heading font null on 01 and 04
