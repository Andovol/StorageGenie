# SG-340 report — screenshots of redesign C (grouped cards SG-337, item page SG-336/338/339) on a scratch app, proven from the DOM

SG-340 | model and effort: not visible in the process arguments, so they are stated as not visible and nothing is inferred | working directory `/home/andrei/StorageGenie` | remote `git@github.com:Andovol/StorageGenie` | BASE ref `origin/automation` resolved to `d90849b15718a568d45210a3ab3155d19a56e5bf` | WORK-HEAD `d90849b15718a568d45210a3ab3155d19a56e5bf` (HEAD == BASE before the report commit; the report commit hash is in the publish output below).

## Time (from `date +%s` stamps)

- Session start 1794995049. Stop-rule point (1100 s) = 1794996149. Scratch removed 1794995599; report written after. The 1100 s rule never triggered. REMAINING: none.
- G0 preflight 1794995060 (verbatim block + `date +%s`; `docker version` shows a Server section 29.9.2, socket `/run/dispatch-storagegenie-SG-340/docker.sock` listed; health `curl http://127.0.0.1:8003/v1/health` = 200).
- G1 migrate 1794995101–1794995101 (rc 0, `sg340.db` 396K, head `20261102_sg279_candidate_state`); backend start 1794995263–65 (PID 2441402, 200); seed 1794995267–68 (rc 0, 13 live + 1 gone, `provider_call` 0); build 1794995272–75 (rc 0, 3.00 s, `index-BZq9--2P.js` 387.48 kB); bundle check 1794995278 (9 / 0); frontend start 1794995281–83 (PID 2442154, 200). Chrome 1794995378–79 (PID 2444845, `/json/list` answers).
- G2 shoot 1794995382–1794995445 (rc 0, ALL_DONE 9; re-probe 200/200 quoted in the driver log before shot 01). Proofs inspected 1794995449–1794995541; all nine PNGs opened and checked; INDEX written 1794995555. End health 200 at 1794995596 (live `8003` = 200; scratch servers down `000` after PID-stop, expected).
- Elapsed ≈ 550 s (5049→5599). No optional goal.

## How the servers were started and the photos made

- Preflight exactly as the packet with `DOCKER_CONFIG`/`DOCKER_HOST` under scratch, `PATH` with the backend venv, `TMPDIR` pointed at scratch, `PYTEST_ADDOPTS` pointed at scratch, `echo`, `ls -l` of the socket dir, `docker version`, `curl` health, then `date +%s`.
- DB: `DATABASE_URL=sqlite:////home/andrei/StorageGenie/output/SG-340-scratch/sg340.db`, `STORAGE_ROOT` under scratch, `alembic upgrade head` from `backend/` (rc 0, head `20261102_sg279_candidate_state` — the same head SG-333 proved).
- Seed `output/SG-340-scratch/seed.py` (scratch, removed): no `/v1/imports` path at all — `POST /v1/households`, `POST /v1/evidence` (multipart PNG), `POST /v1/assets`, `POST /v1/plugins/expiry-tracker/assets/{id}/classification {"category":"food"}`, `POST /v1/plugins/expiry-tracker/assets/{id}/expiry {"expiry_date":…}`, `POST …/gone {"reason":"used_up"}` via httpx from the backend venv (no install). PNGs made with the backend venv's Pillow (no install — 256×256, light warm two-tone ground + one simple drawn shape: green bottle, blue carton, amber box, honey jar, cream sack, tea tin; 1025–1469 bytes each). They remain stand-ins; they prove loaded vs placeholder tiles, not real photography. The packet's first classification URL premise (`/v1/assets/…/classification`) was wrong — the router prefix is `/v1/plugins/expiry-tracker` (proved by `frontend/src/api/client.ts:319` and the 405 log); the seed uses the real path. Nothing in `backend/` was changed.
- No provider network: the seed never calls the import/run path; backend ran with `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY= SG_CONSENT=false`, `cwd=backend` (root `.env` not read); `provider_call` table count is 0 after seeding (sqlite check quoted in `seed.log`); backend log shows only household/asset/evidence/classification/expiry/gone routes.
- Backend: `DATABASE_URL`, `STORAGE_ROOT`, `CORS_ORIGINS=http://127.0.0.1:14340`, fake-provider envs, `cwd=backend`, `nohup ./venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 18340 > scratch/logs/backend.log 2>&1 &`, PID file, wait loop for 200 on `/v1/health` (PID 2441402, 200 quoted).
- Frontend: `VITE_API_BASE=http://127.0.0.1:18340`, `NPM_CONFIG_CACHE` under scratch, `node node_modules/vite/bin/vite.js build --outDir scratch/build` from `frontend/` (rc 0), then `nohup node …/vite.js preview --host 127.0.0.1 --port 14340 --strictPort --outDir scratch/build > scratch/logs/frontend.log 2>&1 &`, PID file, wait loop for 200 on `/` (PID 2442154, 200 quoted; pre-shot re-probe 200/200 quoted in `shoot` log).
- Bundle check on `build/assets/index-BZq9--2P.js`: `grep -o 127.0.0.1:18340 | wc -l` = 9 (> 0); `grep -o 8003 | wc -l` = 0 (else STOP, did not stop).
- Driver: one headless Chrome (`/usr/bin/google-chrome --headless=new --no-sandbox`, `--user-data-dir` under scratch, `HOME` pointed at scratch, `--remote-debugging-port 18341`), one page target, one DevTools WS session, built-in `WebSocket` only. Theme via `localStorage["sg-theme"]` + reload, `household_id` the same way (SG-333 method); per-row through the page's own visible `.sg-per-row-button` click (returns `clicked:4` on 02, quoted; defaults remove the keys, no click). Full-page screenshots (`captureBeyondViewport:true`, full-content clip) into `docs/worklogs/SG-340_shots/`.
- Places: the same kind `food_beverages` for every asset; Where absent — locations are dormant (`sg_locations_enabled=false`, `backend/app/api/v1/locations.py:3` gate) — stated, so the muted line reads `<Kind> · <N> packs` with no Where.

## Shots (full proofs in `docs/worklogs/SG-340_shots/INDEX.md`)

Run date 2026-11-18; dates computed from it in the seed (`date.today()`): past 2026-11-17, Milk 2026-11-20, Olive-week 2026-11-23, later 2027-05-18 (≈+181 d), Rice 2026-12-17 / Beans 2027-01-16 / Honey 2027-02-15 / Tea 2027-03-17 / Salt 2027-04-16 / Flour 2027-05-16 / Vinegar 2027-06-15, no-date Pasta + Milk-no-date, gone Old Jam 2026-12-27 (behind `Gone (1)`).

| # | file | theme / width | sha12 | bytes | proving DOM text |
|---|---|---|---|---|---|
| 01 | 01-catalog-light-1280-5.png | light 1280 | 638c0ca8860a | 128617 | `Your things`, `13 things`, `Gone (1)`, `1 item is past its date and 2 run out this week. Show them`, sort `Use by, soonest first`; grid 5 tracks; `sg-per-row-wide` null (default) |
| 02 | 02-catalog-dark-390-4.png | dark 390 | 09a10527ebc3 | 54843 | same title/attention/sort on dark; 4 tracks, control `clicked:4`, `sg-per-row-narrow=4` |
| 03 | 03-catalog-light-1920-5.png | light 1920 | 825230828246 | 181705 | same title/attention/sort; 5 tracks |
| 04 | 04-item-light-1280.png | light 1280 | 7f22b32d233c | 82493 | `Olive Oil`, muted `Food & beverages · 3 packs`, rows `Past · 17 Nov` / `Use by 23 Nov 2026` / `Use by 18 May 2027` |
| 05 | 05-item-dark-1280.png | dark 1280 | 8b0a9ab9f14a | 81987 | same heading/muted/rows on dark |
| 06 | 06-item-light-390.png | light 390 | a1e64eeb8b67 | 58153 | same heading/muted/rows, stacked |
| 07 | 07-item-light-390-edit.png | light 390 | f2089995973d | 77577 | same + `clicked-edit:pack-row-…2a9f…`, `Manual expiry entry` in view |
| 08 | 08-item-light-1280-usedup.png | light 1280 | 7895855c0abb | 78553 | `clicked-usedup:pack-row-…2ad8…`, rowsBefore 3 → 2 rows, notice `Olive Oil used up · Undo`, muted `2 packs` |
| 09 | 09-item-light-1280-open.png | light 1280 | c204b3e3ca95 | 145728 | same 3 rows, `History (3 changes)` + `More about this item` both `aria-expanded true`, More heads 5 |

Every shot (probe fields in INDEX.md): `body` bg light `rgb(243, 242, 239)` / dark `rgb(18, 20, 25)`; wrapper `[data-testid="page-container"]` transparent (both AppShell main and PageContainer div carry that testid — proved by code read); heading/body/button fonts all `"Instrument Sans Variable", system-ui, …` (named selectors per shot); every visible button/link carries a numeric WCAG ratio (01 min 5.44 over 31 ctrls, 02 min 7.57 over 22, 03 min 5.44, 04 min 12.74 over 23, 05 min 10.88, 06/07 min 12.74, 08 min 12.74, 09 min 4.80 over 32 on disabled `Attach evidence` — none missing or "n/a"); every visible date line carries a numeric ratio on its effective background (catalog past 7.42 light / 9.56 dark, soon 7.26, later 15.36 / 15.32, none 5.44 / 7.57 — past and this-week lines named); smallest font 13 px, under-13 `[]`, mono `false` on all nine; corners card/tile/button all `0px`; pack buttons (`Edit`/`Used up`/`Add another pack`/`-1`/`+1`/`Save amount`) height 44 on 06/07 (pre-existing chrome — nav/back/History/More toggles 16–32, form `Save date` 32 / `Clear` 26 — listed, not pack actions); catalog cards listed per shot in INDEX (Olive 1, Milk 1 each; title `13 things`; x title 24 = attention 24 = first card 24; tracks equal per-row 5/4/5; each date chip right edge ≤ card right edge — e.g. 01 Olive cardR 248.2 chipR 160.1, 02 Olive 103.5=103.5 touches not past — quoted per card); item shots list every pack row date+muted in order (quoted above; `1 l · added 18 Nov` on the later row), tile `img naturalWidth 256` (loaded, not broken; fallback icon only where no photo), definition rows `['Kind of item Food & beverages']` (Where absent — dormant, Brand `—` hidden by code), History/More `false/false` on 04–08 and `true/true` on 09 with More heads `['Shelf life','Amount left','Use it up','Evidence','Details']`; 08 notice full text quoted, rows 3→2, Undo `clicked-undo` → rows 3 with API read-back `GET /v1/assets/01a1ee0e-2ad8-7003-b6be-4e0c4d9fc6ec?household_id=…` → `status ACTIVE` (quoted; the `shots.json` shorthand `laterGone=found` meant the id lookup, the status read is ACTIVE); phone shots scroll 390=390 equal; layout claims each quote a `getBoundingClientRect` plus what the image shows (02 chip wrap inside the card, 02 attention two lines with no sideways scroll, 03 huge/sparse tiles, 06 stacked photo-top — INDEX design notes); forbidden/ISO scans `hits []` / `isoHits []` on all nine (the Details `17 Nov 2026` is owner words, not an ISO stamp — the regex `\d{4}-\d{2}-\d{2}` proves it); distinct hashes 9/9 quoted above.

No shot was retaken (all nine passed first try) — no shot is described as showing what it does not; every "shows" sentence in INDEX names the DOM read or the opened image proving it. All nine PNGs were opened before the design notes below were written.

## Design notes (each from its image or a DOM read, named)

- 01: airy 5-across, no clip (chipR<cardR all 10); one paper ground; stand-in photos distinct (bottle/carton/box/jar) — louder than grey cubes but placeholder reads fine (image + DOM); muted 5.44 passes; owner date words; grid shares the title edge (x 24=24=24 proves G5); chip never past its card (proves G4).
- 02: same on dark, weakest 7.57; 4 per row via the visible `4` control; past chip wraps inside its card (chipR=cardR, image two lines) — allowed wrapping, not overflow; attention two lines, no sideways scroll (390=390); tight but legible, owner call 3 vs 4.
- 03: same as 01 at 1920; no clip/overflow (1905=1905); tiles very large with ample ground — not broken but sparse/oversized, owner call whether to cap width or offer 6.
- 04: mockup layout proved — `‹ Your things`, square photo left, 44 px name, muted kind+packs, one row per live pack in date order with `Edit`+`Used up`, `Add another pack` the one dark primary, one definition row, two folds closed (image + DOM).
- 05: same on dark; washes/contrasts pass (past 9.56, Add 10.88, pack buttons 15.32); no mismatch.
- 06: stacked photo-top (image); pack buttons 44 pass; small chrome named (Menu 30, back/History/More 16) — pre-existing, legible; no sideways scroll; `Edit`+`Used up` fit per row.
- 07: week-row editor open (`Manual expiry entry`, image + `editRes`); no clip; form Save 32 / Clear 26 under 44 named; native date `11/23/2026` is browser locale, not body text (ISO scan [] still holds).
- 08: notice in view with `Undo`, rows 3→2 and muted 3→2 packs (image + DOM), Undo restores 3 with API ACTIVE — proved, no cross-pack change; plain wording, no clip.
- 09: both folds open with 3 history entries and 5 More heads (image + DOM); Details owner words (`Live` not `ACTIVE`, `Kept`, no `[object Object]`); weakest 4.8 disabled `Attach evidence` passes but closest — named; `None left — mark it gone below` on a never-counted item observed; fallback photo correct (opened pack has none, week pack's 256-px photo shows).

## Contract

I received no contract version line for this run, so I echo no version line (stating this exactly as instructed, never the project file's `AGENTS.md` line). The contract folder was never read; the denial was never probed, so no STOP arose.

## UNCLEAR / REMAINING

- UNCLEAR: font-load proof (`document.fonts` status) not checked; the Instrument Sans stack is quoted from computed style only (same caveat as SG-333).
- UNCLEAR: photo tiles are drawn Pillow stand-ins (method + sizes quoted) — they prove loaded vs placeholder tiles, not real photography.
- UNCLEAR: the `shots.json` shorthand `laterGone=found` is only the id lookup; the restore proof is the quoted API `status ACTIVE` read above.
- REMAINING: none — all nine shots pass with every G2 DOM read in INDEX.md.

## Criteria

- A1 — Preflight `docker version` Server section shown, socket listed, health 200 at start (1794995060) and 200 at end (live 8003 at 1794995596); phase seconds above from stamps. PASS.
- A2 — Scratch app on 18340/14340, background starts with PIDs 2441402/2442154 and 200s quoted, the pre-shot re-probe 200/200 quoted; bundle check 9/0 quoted; photos via evidence upload of Pillow PNGs (method + sizes quoted) with no-provider evidence (no import path, `provider_call` 0, fake envs, `cwd=backend`); dates used with the run date 2026-11-18 they were computed from. PASS.
- A3 — Nine shots with hash, size, proving text and every G2 DOM read in INDEX.md; per-row track counts equal the table (5/4/5 with x 24=24=24 and chipR≤cardR quoted per card); distinct-hash 9/9 quoted; 08's Undo read-back (rows 3, API ACTIVE) quoted. PASS.
- A4 — Design notes per shot, each naming its image or DOM read and checking every named item; every defect visible in the image named (02 chip/attention wrap, 03 sparse, 06 small chrome, 07 Save/Clear heights + US date locale, 09 4.8 disabled contrast + `None left` wording). PASS.
- A5 — Only `docs/worklogs/SG-340_shots/` (9 PNG + INDEX.md) plus this report written; no product/test/backend/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/stored-files/host/provider/container/deploy bytes; `frontend/dist` untouched (nothing in `git status` beyond the two worklog paths); no `/tmp` (all logs/builds/profiles/caches under scratch via `TMPDIR`/`NPM_CONFIG_CACHE`/`HOME`/`--user-data-dir`, scratch removed by exact path before the report — absent). PASS.
- A6 — Vacuity checked: two Olive cards (1 card + `3 packs` quoted per shot), chip past its card (chipR≤cardR per card quoted), first card off the title edge (24=24=24 quoted), rows in the wrong order (past/week/later quoted in order), Used up removing two rows (3→2 quoted), Undo not restoring (rows 3 + API ACTIVE quoted), button under 44 on the phone (pack buttons 44 quoted; small chrome/form controls listed), ISO date (scans [] quoted), `unknown` in text (scans [] quoted), sideways scroll (390=390 ×3 quoted), two shots one hash (9/9 quoted), bundle pointing at 8003 (grep 0), scratch left behind (absent). PASS.
- A7: see last line.

Verification: PASS
