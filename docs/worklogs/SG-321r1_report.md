# SG-321r1 report

SG-321r1 | model opencode-go/muse-spark-1.3-contributor | effort xhigh (read from process arguments: `opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/muse-spark-1.3-contributor --variant xhigh`) | working directory /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref `origin/automation`, resolved BASE commit 38d75860f96d3952cb8e0d1a2d5b5a6860c0b9af | WORK_HEAD 38d75860f96d3952cb8e0d1a2d5b5a6860c0b9af (pre-report HEAD; HEAD == origin/automation; the report commit hash is in the publish output)

Contract: I received no contract version line for this run. Nothing from AGENTS.md is quoted here as the contract line.

## Time

- Start 1794686982. Stop-rule point (1100 s) = 1794688082. Cleanup end 1794687565 = 583 s. Report written after.
- G0 preflight 1794686982 (1 s). `docker version` Server section present (29.9.2); socket `/run/dispatch-storagegenie-SG-321r1/docker.sock` present; health `curl http://127.0.0.1:8003/v1/health` = 200 at start; live health 200 at end 1794687565 with body `{"status":"ok","db":"ok","storage":"ok"}`.
- G1 migrate 1794687043 (rc 0, `sg321r1.db` 396K); seed 1794687087 (rc 0, 6 assets, candidate `proposed` with `duplicate_of_asset`, `PROVIDER_INVOCATIONS 1`); build 1794687095 (rc 0, 2.79 s); bundle check (7 / 0); backend start 1794687103–1794687105 (PID 3003935, 200); frontend start 1794687108–1794687110 (PID 3004066, 200); verify 1794687113 (6 assets via live API).
- G2 chrome start 1794687295 (HeadlessChrome 145.0.7632.6, `--no-sandbox` after the sandbox-less launch crashed — FATAL sandbox message quoted in `logs/chrome.log`, retried with the flag); shots 1794687307–1794687318 (11 s, rc 0, all five captured); follow-up DOM fills 1794687393–1794687398 (rc 0); grid/table probe 1794687426–1794687432 (rc 0); micro-probes 1794687446–1794687497. Teardown 1794687559 (ports 000/000); scratch removed by exact path 1794687565 (absent).

## How servers started and the duplicate made

- Preflight exactly as packet with `DOCKER_CONFIG`/`DOCKER_HOST` under scratch, `PATH` with backend venv, `echo`, `ls`, `docker version`, `curl` health, then `date +%s`.
- DB: `DATABASE_URL=sqlite:////home/andrei/StorageGenie/output/SG-321r1-scratch/sg321r1.db`, `STORAGE_ROOT` under scratch, `alembic upgrade head` from `backend/` (rc 0, head `20261102_sg279_candidate_state`).
- Seed `output/SG-321r1-scratch/seed.py` (scratch, removed): method (b) — the same steps as `backend/tests/test_sg304_duplicate_pack.py::_setup` (`ScriptedPhase2Provider` from `tests/test_phase2_e2e.py` with the olive output carrying `2032-06-18`), plus a second Olive Oil (`2031-02-03`), Rice (`2030-08-12`), Pasta, Milk, Wrench. Household `SG-321r1 Scratch`; evidence PNGs generated in-process; assets/classifications/expiries/import all through `TestClient` with a `get_db` override onto the scratch file. Log `logs/seed.log` proves: `PROVIDER_INVOCATIONS 1`, `CANDIDATE_STATE proposed`, `CANDIDATE_ASSET_ID None`, `matches=[duplicate_of_asset asset_id=OO1]`, household id `01a1dbaf-ba01-…`, candidate id `01a1dbaf-bbac-…`.
- No provider network: `backend/app/services/providers/fake.py` docstring reads `no network, no key, no SDK` and its code imports only `uuid`, `copy.deepcopy` and in-process types (grep for `requests|httpx|urllib|urlopen|socket` in that file: no hits); `ScriptedPhase2Provider` returns a caller-supplied dict with cost 0.0005 and records bytes/prompts in-process; the seed script patches `OpenCodeGoProvider._post` to raise `AssertionError("network must never be attempted")`, and the run completes with 1 invocation and no raise — so no network call happened.
- Backend: `DATABASE_URL`, `STORAGE_ROOT`, `CORS_ORIGINS=http://127.0.0.1:14321`, `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY= SG_CONSENT=false`, `cwd=backend`, `nohup backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 18321 > scratch/logs/backend.log 2>&1 &`, PID file, wait loop for 200 on `/v1/health` (PID 3003935, 200 quoted).
- Frontend: `VITE_API_BASE=http://127.0.0.1:18321`, `NPM_CONFIG_CACHE` under scratch, `node node_modules/vite/bin/vite.js build --outDir scratch/build` from `frontend/` (rc 0), then `nohup node vite preview --host 127.0.0.1 --port 14321 --strictPort --outDir scratch/build > scratch/logs/frontend.log 2>&1 &`, PID file, wait loop for 200 on `/` (PID 3004066, 200 quoted).
- Bundle check on `build/assets/index-Dz-S0ven.js`: `grep -o 127.0.0.1:18321 | wc -l` = 7 (> 0); `grep -o 8003 | wc -l` = 0 (else STOP, did not stop).
- Driver: one browser, one page target, one DevTools WS session. Theme via `localStorage["sg-theme"]` + reload; viewport via `Emulation.setDeviceMetricsOverride`; fills via native setter + `input`/`change` (driver returns `set:Rice`, `set:olive oil `, `set:Olive Oil`); clicks via `button.click()` (`clicked` × 3); counts via in-page fetch (6 before, 7 after).

## Shots (full proofs in `docs/worklogs/SG-304_shots_r1/INDEX.md`)

| # | file | theme / width | sha12 | bytes | proving DOM text |
|---|---|---|---|---|---|
| 01 | 01-same-name-warning-one-light-1280.png | light 1280 | 2bcc7ac2bc88 | 52183 | warning `You already have Rice (use by 12 Aug 2030).` + `Add another pack \| Open it(link) \| Cancel`, dates `12 Aug 2030` |
| 02 | 02-same-name-warning-two-dark-1280.png | dark 1280 | a479faff3027 | 57378 | warning `You already have these: Olive Oil (use by 3 Feb 2031) Open it / Olive Oil (use by 6 May 2030) Open it` + `Add another pack \| Cancel`, dates `3 Feb 2031, 6 May 2030` |
| 03 | 03-duplicate-card-light-1280.png | light 1280 | 0fda626a414b | 82627 | card `This photo matches Olive Oil (use by 6 May 2030).` + `It's another pack \| It's the same pack \| Decide later`; Accept/Hold absent; `Save edits` present (G-1); existing item id absent from `innerText` |
| 04 | 04-duplicate-card-dark-390.png | dark 390 | 6ad6ac22473d | 135869 | same card text; same button visibility; scroll 390 vs 390; every button `getClientRects().length === 1` (no label wraps) |
| 05 | 05-three-olive-oils-light-1280.png | light 1280 | 931d20cae24e | 47260 | catalog search `Olive Oil`, `Showing: 3 items`, 3 rows `Olive Oil \| Uncategorized \| Photo only \| — \| just now/4 min ago`; counts 6→7; expiries `2032-06-18` (new), `2031-02-03`, `2030-05-06` via in-page detail fetch (cards print no expiry) |

- Distinct-hash check: 5 distinct of 5 (full sums quoted in INDEX.md).
- 01 proofs: body `rgb(244, 240, 232)`, `#root` transparent; h1 24px Instrument Sans 15.39:1; wordmark 20px 15.47:1; 4 buttons with ratios 15.47 / 8.59 / 8.59 / 9.46; smallest 11px (4 helper nodes); warning text 14.68; mono none; forbidden none; ISO none; thumb 0.
- 02 proofs: body `rgb(32, 27, 23)`; h1 15.64:1; wordmark 15.01:1; buttons 15.01 / **2.02** / **2.02** / 9.46; warning text 13.05; smallest 11px; mono/forbidden/ISO none; thumb 0.
- 03 proofs: body paper; h1 15.39:1; card buttons 9.46 / 15.47 / 15.47 (+ `Save edits`, `Reject` 15.47); smallest 11px (confidence lines; `State:`/`proposed`/job 12px); mono none; forbidden none; ISO none in `innerText` (the `expiry_date` input visibly holds `2032-06-18` — input values are not in `innerText`; flagged in design notes, not a proof failure); thumb 0; scroll 1265/1265.
- 04 proofs: body dark; h1 15.64:1; buttons 15.01 / 15.01 / 9.46 / 15.01 / 15.01 / 15.01 / 15.01 with rects (Menu 57x30, icon 32x32, choices 119/128/94x26); smallest 11px; scroll 390/390; mono/forbidden/ISO none; thumb 0.
- 05 proofs: no `h1`/`h2` on catalog (selector null; substitute `Showing:`/`3 ITEMS` 13px Instrument Sans `rgb(25, 25, 25)` ≈15.47 by the same colour pair); wordmark 15.47; 12 buttons all with numeric ratios (11 × 15.47, `Clear all` 8.69); header `Import Asset` is an anchor, not a button (tag read); smallest 13px, none under; mono/forbidden/ISO none; thumb 0; scroll 1265/1265.
- Every sentence saying a shot "shows" something names the DOM read proving it (INDEX.md sections quoted above; all five PNGs opened and checked).

## Design notes (each from its image or DOM read, named)

- 01 image + DOM warning text: the warning is a calm beige box (`rgb(236,235,233)` on paper), not red — reads as a notice, matching "warning, not error". Its three actions read distinctly (`Add another pack` creates anyway, `Open it` goes to the existing pack, `Cancel` backs out). Crowding: none — the image shows breathing room; no clipping. Mismatched surfaces: none. Text under 13px: only the 11px filename helper and format note (DOM). Weak contrast: none failing (lowest button 8.59). Leftover wording: the `Kind of item` select defaults to `unknown` (image). Date format: plain words `12 Aug 2030` (DOM).
- 02 image + DOM links: the two matches each carry an identical `Open it` link (DOM `warnLinks` × 2, image) — only the dates tell the packs apart. Warning-vs-error: dark box `rgb(46,42,38)` with light text, still neutral (image + DOM). Weak contrast: `Add another pack` / `Cancel` at **2.02:1** in the dark (DOM) — genuinely weak, same class as the known P10 dark-button issue; the image shows them as washed pink-on-grey. Date format plain words × 2 (DOM). No mono, no clipping (image).
- 03 image + DOM card text: the three choices read distinctly — solid maroon `It's another pack` (DOM bg `rgb(110,48,46)`, 9.46:1) against paper `It's the same pack` / `Decide later` (15.47:1). `Save edits` still shows below the fields (image bottom edge + DOM `saveEditsVisible true`) — gap G-1 as expected, photographed not fixed. Leftover wording: raw `Candidate 01a1dbaf-…` heading plus `State: proposed · Job: …` 12px metadata (DOM innerHead, image), and raw field keys (`display_name`, `status`, `expiry_date`, `lot`) with 11px `Confidence · Source` lines (image + DOM under-13 list). Date format split: card line plain words `6 May 2030` (DOM) but the `expiry_date` input holds ISO `2032-06-18` (image; invisible to the `innerText` ISO check). Mismatched surfaces: white card on paper reads as an intentional card (image). The card runs below the fold (image cuts at `Save edits`) — normal page scroll, not clipping.
- 04 image + DOM rects: no sideways scroll (390/390 DOM); no button label wraps onto two lines (every button `getClientRects().length === 1`, DOM; image shows `It's the same pack` on one line at 128x26). Phone button sizes from DOM rects: choices 119/128/94 × 26, `Save edits` 83x26, `Reject` 60x26, `Menu` 57x30 — usable targets. In the 04 image the header occupies two rows (wordmark above; `Menu`/theme/import below) — header layout at 390px, not label wrapping. Dark choice hierarchy same as 03 (image). Same leftover wording and ISO-input caveat as 03.
- 05 image + DOM rows: the search narrowed (`Olive Oil` in box and `Search: Olive Oil` chip, `Showing: 3 items` — DOM + image). An owner still cannot tell the packs apart on this screen: rows print no expiry, only relative `Added` (`just now`, `4 min ago` — DOM rows + image); the three dates (`2032-06-18`, `2031-02-03`, `2030-05-06`) come from in-page detail fetches, labelled as API reads. Leftover wording: `Photo only` × 3 and `Uncategorized` × 3 repeat on every row (image + DOM). No clipping or crowding (image is airy); no text under 13px (DOM smallest 13); weakest control `Clear all` 8.69:1 (DOM). The three-choices / warning-vs-error checks do not apply to the catalog screen.

## PB-1 establishment

- F9 confirmed from code `AssetForm.tsx:28 findSameNamePacks` (trimmed lower-case compare, live-only filter) + `:305-338 same-name-warning` (one line vs list, buttons/links `Add another pack` / `Open it` / `Cancel`); shots 01/02 prove it renders with one date (`12 Aug 2030`) and two dates (`3 Feb 2031`, `6 May 2030`) via DOM warning text.
- F10 confirmed from code `CandidateCard.tsx:24 duplicateLine` (name + date, never id) + `:96-106` three choices with Accept/Hold hidden via `isDuplicate`; gap G-1 confirmed at `:147-155 Save edits` not gated. Shots 03/04 prove the card renders with `This photo matches Olive Oil (use by 6 May 2030).` via DOM card text on the SG-322-fixed code (open duplicate reads with no `asset_id`, `CANDIDATE_ASSET_ID None` in the seed log); shot 05 proves `It's another pack` commits a third pack (counts 6→7, three `Olive Oil` rows).

## UNCLEAR / REMAINING

- UNCLEAR: font-load proof (`document.fonts` status) not checked; the Instrument Sans stack is quoted from computed style only.
- REMAINING: none — all five shots pass on the fixed code with every proof in INDEX.md.

## Criteria

- A1: Preflight proven (Server section 29.9.2, socket present, health 200 start 1794686982 and end 1794687565 with body); phase seconds above — PASS.
- A2: Scratch on 18321/14321, background starts with PIDs 3003935/3004066 and 200s quoted; bundle check 7/0 quoted; duplicate via method (b) `ScriptedPhase2Provider` with no-network evidence (`fake.py` docstring + import grep + `_post` guard + 1 invocation, no raise) — PASS.
- A3: Five shots with hash, size, proving text and every G2 DOM read in INDEX.md; distinct-hash check 5/5 quoted — PASS.
- A4: Design notes per shot, each naming its image or DOM read — PASS.
- A5: Only `docs/worklogs/SG-321r1_report.md` + `docs/worklogs/SG-304_shots_r1/` written (6 files); no product/test/backend/migration/Dockerfile/compose/lockfile/`.env`/live-DB/stored-files/host/provider/container/deploy bytes; `frontend/dist` untouched (mtime Nov 9); no `/tmp` (all logs/builds/profiles under scratch; `TMPDIR` pointed at scratch); scratch removed by exact path before the report (absent) — PASS.
- A6: Vacuity checked — no warning on match (01/02 `warnPresent true` after submit); one match where two exist (02 lists two dates); raw id on card (`oo1InText false`); Accept/Hold shown (both false); ISO date (regex scan clean on all five); sideways scroll at 390 (390/390); unchanged count after click (6→7, changed); two shots one hash (5 distinct); bundle pointing at 8003 (grep 0); scratch left behind (absent) — PASS (every failure mode checked, none present).
- A7: see last line.

Verification: PASS
