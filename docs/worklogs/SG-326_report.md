# SG-326 report — screenshots of polish A and B on a scratch app, proven from the DOM

SG-326 | model/effort: not visible in the process arguments available to this session (not inferred) | cwd /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref `origin/automation`, resolved BASE commit 87ae14e51e55f3bb92b3095247d799bf5c77521e | WORK_HEAD 87ae14e5 (pre-report HEAD; HEAD == origin/automation; the report commit hash is in the publish output)

Contract: I received no contract version line for this run.

## Time

- Start 1794850528. Stop-rule point (1100 s) = 1794851628. Cleanup end 1794851133 = 605 s. Report written after.
- G0 preflight 1794850528 (verbatim block + `date +%s`; `docker version` shows a Server section 29.9.2; socket `/run/dispatch-storagegenie-SG-326/docker.sock` listed; health `curl http://127.0.0.1:8003/v1/health` = 200).
- G1 migrate 1794850568–69 (rc 0, `sg326.db` 396K, head `20261102_sg279_candidate_state`); seed 1794850625–27 (rc 0, 6 assets, candidate `proposed` with `duplicate_of_asset`, `PROVIDER_INVOCATIONS 1`); build 1794850632–36 (rc 0, 3.18 s); bundle check (7 / 0); backend start 1794850646–48 (PID 230161, 200); frontend start 1794850651–53 (PID 230358, 200); verify 1794850656 (6 assets via live scratch API) + expiry join 1794850660 (OO1 2030-05-06, OO2 2031-02-03).
- Soup correction 1794850942–63 (new Tomato Soup via API with `asset_type food_beverages`, old photo-soup archived; live count 6).
- G2 shots run 1: 1794850835–89 (rc 0, six captured); re-shot after the soup correction 1794850966–1794851018 (rc 0, ALL_DONE 6). Teardown: health 200 at end 1794851126, ports closed 1794851129, scratch removed by exact path 1794851133 (absent).
- The 1100 s rule never triggered (cleanup done at 605 s). REMAINING: none.

## How servers were started and the duplicate made

- Preflight exactly as the packet with `DOCKER_CONFIG`/`DOCKER_HOST` under scratch, `PATH` with the backend venv, `TMPDIR` pointed at scratch, `echo`, `ls -l` of the socket dir, `docker version`, `curl` health, then `date +%s`.
- DB: `DATABASE_URL=sqlite:////home/andrei/StorageGenie/output/SG-326-scratch/sg326.db`, `STORAGE_ROOT` under scratch, `alembic upgrade head` from `backend/` (rc 0).
- Seed `output/SG-326-scratch/seed.py` (scratch, removed): method (b) — the same steps as `backend/tests/test_sg304_duplicate_pack.py::_setup` (`ScriptedPhase2Provider` from `tests/test_phase2_e2e.py` with the olive output carrying `2032-06-18`) against the scratch file, plus OO1 (`2030-05-06`), OO2 (`2031-02-03`), Rice (no date), Milk (`2030-01-15`), Pasta (no date). Household `SG-326 Scratch`. Log `logs/seed.log` proves: `PROVIDER_INVOCATIONS 1`, `CANDIDATE_STATE proposed`, `CANDIDATE_ASSET_ID None`, `matches=[duplicate_of_asset asset_id=OO1]`. Correction: the first 300 ml soup carried `asset_type food` so its Details kept a `Shelf life` row (`Food & beverages` vs `Food` — the drop rule compares equal labels); a second soup was made through the API with `asset_type food_beverages` (classified `food` → same label, row dropped) and the first was archived (`status ARCHIVED`, live count back to 6). Nothing in `backend/` was changed.
- No provider network: `backend/app/services/providers/fake.py:1` docstring reads `no network, no key, no SDK`, and `grep` for `requests|httpx|urllib|urlopen|socket` in that file returns 0 hits; the seed script patched `OpenCodeGoProvider._post` to raise `AssertionError("network must never be attempted")`, and the run completed with 1 invocation and no raise — so no network call happened.
- Backend: `DATABASE_URL`, `STORAGE_ROOT`, `CORS_ORIGINS=http://127.0.0.1:14326`, `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY= SG_CONSENT=false`, `cwd=backend`, `nohup backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 18326 > scratch/logs/backend.log 2>&1 &`, PID file, wait loop for 200 on `/v1/health` (PID 230161, 200 quoted).
- Frontend: `VITE_API_BASE=http://127.0.0.1:18326`, `NPM_CONFIG_CACHE` under scratch, `node node_modules/vite/bin/vite.js build --outDir scratch/build` from `frontend/` (rc 0), then `nohup node vite preview --host 127.0.0.1 --port 14326 --strictPort --outDir scratch/build > scratch/logs/frontend.log 2>&1 &`, PID file, wait loop for 200 on `/` (PID 230358, 200 quoted).
- Bundle check on `build/assets/index-sVkVBAYl.js`: `grep -o 127.0.0.1:18326 | wc -l` = 7 (> 0); `grep -o 8003 | wc -l` = 0 (else STOP, did not stop).
- Driver: one headless Chrome (156.0.8078.47, `--no-sandbox` after the root-owned `~/.local` blocked the profile — `HOME` pointed at scratch; first attempt without it died `Failed to create headless user data directory container`), one page target, one DevTools WS session. Theme via `localStorage["sg-theme"]` + reload; fills via native setter + `input`/`change` (driver returns `set:Olive Oil`, `set:olive oil`); search narrowed to 2 rows (wait met, no fallback); table view forced via the `Compact Table` button when auto-density was not table.

## Shots (full proofs in `docs/worklogs/SG-326_shots/INDEX.md`)

| # | file | theme / width | sha12 | bytes | proving DOM text |
|---|---|---|---|---|---|
| 01 | 01-asset-tomato-soup-light-1280.png | light 1280 | 42cd8c134017 | 100466 | `Tomato Soup`, `Live · 300 ml left`, Details rows Kind of item→Food & beverages, Name, Expiry date→15 Sep 2030, Amount→300 ml, Status→Live; no Shelf life Details row |
| 02 | 02-catalog-olive-oil-light-1280.png | light 1280 | 08b05cd18d83 | 45062 | `Showing: 2 items`, `Search: Olive Oil`, use-by cells `3 Feb 2031`, `6 May 2030`; headers ASSET/NAME/CATEGORY/USE BY/ADDED/ACTIONS; row buttons `More actions for Olive Oil` × 2 |
| 03 | 03-catalog-cards-dark-390.png | dark 390 | 119ab7c17e55 | 29207 | cards `15 Sep 2030 Tomato Soup`, `No date Pasta`, `15 Jan 2030 Milk`, `No date Rice`, `3 Feb 2031 Olive Oil`, `6 May 2030 Olive Oil`; scroll 390 vs 390 |
| 04 | 04-capture-warning-dark-1280.png | dark 1280 | 202afe6500b0 | 63353 | `Add an item`; warning `You already have these:` + two dated `Open it` lines (`3 Feb 2031`, `6 May 2030`); buttons `Add another pack`, `Cancel` |
| 05 | 05-review-duplicate-light-1280.png | light 1280 | e6f40c3f420f | 75425 | `Check this item`, `This may already be in your catalog`, `This photo matches Olive Oil (use by 6 May 2030).`; buttons It's another pack / It's the same pack / Decide later / Reject; labels Name, Kind of item, Status, Use by, Lot; use-by `type: date`, `value: 2032-06-18` |
| 06 | 06-review-duplicate-dark-390.png | dark 390 | d591dd992d95 | 58439 | same card text as 05; scroll 390 vs 390; no button wraps |

- Distinct-hash check: 6 distinct of 6 (sums quoted above; full check quoted in INDEX.md).
- 01 proofs: body `rgb(244, 240, 232)`; wrapper `[data-testid="page-container"]` transparent; h1/button/body Instrument Sans; 10 buttons all numeric (Edit 15.47, Clear expiry date 15.47 against paper, Save date 9.46 maroon, Attach-evidence disabled 5.26); smallest 13 px, none under; mono none; forbidden/ISO/UUID clean; `Shelf life` in `innerText` is the picker section heading, not a Details row (probe `detailRows` has no such label).
- 02 proofs: headers prove the `Use by` column with no `Status`/`Dimensions/Specs`; `...` buttons read one line in the image (probe `wraps: true` is padding arithmetic — rect 25×26 vs lineHeight 16 — stated as artifact, not a shown wrap); smallest 13; forbidden/ISO/UUID clean.
- 03 proofs: body dark `rgb(32, 27, 23)`; 10 buttons all 15.01, none wraps; smallest 13; scroll equal; pills `All (7)` vs `6 ITEMS` is the archived-soup scratch artifact (stated, not a product claim).
- 04 proofs: warning buttons dark-paper 15.01 (the SG-321 2.02:1 weakness fixed); smallest 11 (only the formats note; hint is 13 px); forbidden/ISO/UUID clean.
- 05/06 proofs: no `Save edits`/`Accept`/`Hold` (all false in DOM, image shows none); use-by input `type: date`; UUID false; `ACTIVE` 0 in `innerText` — while the image shows raw `ACTIVE` (Status input) and `unknown` (Kind input) as input values (SG-325 UNCLEAR I8, reported, not failed).
- Every sentence saying a shot "shows" something names the DOM read or the opened image proving it (INDEX.md per-shot sections; all six PNGs opened and checked).

## Design notes (each from its image or a DOM read, named)

- 01 image + DOM: airy, no clipping; one paper ground; no text under 13 px; live controls ≥ 9.46 (disabled Attach 5.26 greyed); History in plain words; locale date input vs plain-words Details date.
- 02 image + DOM: no clipping; thumb tint + date tell the two Olive Oils apart; weakest control `Clear all` 8.69 link-styled; no `Photo only`; dates plain words.
- 03 image + DOM: single column, no sideways scroll; date chips legible; all buttons 15.01; pills-vs-count mismatch is scratch's archived item, not product; 26 px phone targets, no label wraps.
- 04 image + DOM: warning reads as notice; themed buttons 15.01; 11 px formats note persists; plain-words options; dated `Open it` links.
- 05 image + DOM: intentional white card; ≥ 13 px; maroon 9.46; raw `unknown`/`ACTIVE` input values visible (reported); duplicate line plain words.
- 06 image + DOM: normal scroll, no sideways scroll; duplicate line reflows over two text lines (not a button wrap); `Decide later` on its own row; same input-value note as 05 on scroll.

## PB-1 establishment (expected items, confirmed from code)

- Asset page: `Edit` uses `THEMED_CONTROL_CLASS` + `CONTROL_STYLE` (`AssetDetailPage.tsx:700`); `Clear expiry date` the same (`ExpiryEntryForm.tsx:158`); Details merges quantity+unit via `detailAmountText` (`AssetDetailPage.tsx:446`) and drops a repeating Shelf life via `visibleDetailAssertions` (`:437`); shot 01 proves Amount→300 ml with no Shelf life Details row via `table.detail-table` DOM rows.
- Catalog: `Use by` header (`ProductGrid.tsx:45`), cell `formatUseByDate(item.useBy) || "No date"` (`:199`), row button `More actions for <name>` (`:210`); cards the same date (`ProductCard.tsx:156`); shots 02/03 prove both dates via `use-by-cell`/`use-by-date` DOM reads.
- Capture: heading `Add an item` (`CapturePage.tsx:21`), `Add to catalog` (`AssetForm.tsx:326`), 13 px hint (`:211`), themed warning buttons (`:326`, `:334`); shot 04 proves via warning/button DOM reads.
- Review: `Check this item` + `This may already be in your catalog` + gated Save edits (`CandidateCard.tsx:123`, `:127`, `:195`); plain labels (`:48-63`); use-by `type="date"` (`:155`); shots 05/06 prove via card/button/field/input DOM reads.

## UNCLEAR / REMAINING

- UNCLEAR: font-load proof (`document.fonts` status) not checked; the Instrument Sans stack is quoted from computed style only (same caveat as SG-321r1).
- UNCLEAR: `ACTIVE`/`unknown` render as input values on 05/06 (image), invisible to the `innerText` scan (SG-325 I8, reported, not failed).
- REMAINING: none — all six shots pass with every proof in INDEX.md.

## Criteria

- A1: Preflight verbatim (Server section 29.9.2, socket listed, health 200 at 1794850528); health 200 again at end 1794851126; phase seconds above — PASS.
- A2: Scratch on 18326/14326, background starts with PIDs 230161/230358 and 200s quoted; bundle check 7/0 quoted; duplicate via method (b) `ScriptedPhase2Provider` with no-network evidence (fake docstring + import grep 0 + `_post` guard + 1 invocation, no raise) — PASS.
- A3: Six shots with hash, size, proving text and every G2 DOM read in INDEX.md; distinct-hash check 6/6 quoted — PASS.
- A4: Design notes per shot, each naming its image or DOM read — PASS.
- A5: Only `docs/worklogs/SG-326_report.md` + `docs/worklogs/SG-326_shots/` written (7 PNG/INDEX files); no product/test/backend/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/stored-files/host/provider/container/deploy bytes; `frontend/dist` untouched (git shows nothing there); no `/tmp` (all logs/builds/profiles under scratch; `TMPDIR`/`HOME`/`NPM_CONFIG_CACHE` pointed at scratch); scratch removed by exact path before the report (absent) — PASS.
- A6: Vacuity checked — one-date/no-date rows (02 shows both dates), `Status`/`Dimensions/Specs` header (headers quoted, absent), `Save edits` on duplicate (false), raw key as label (labels quoted plain), ISO date in text (scan clean), grey/white button on paper (all themed bgs quoted), sideways scroll at 390 (390/390 × 2), two shots one hash (6 distinct), bundle pointing at 8003 (grep 0), scratch left behind (absent) — PASS (every failure mode checked, none present).
- A7: see last line.

Verification: PASS
