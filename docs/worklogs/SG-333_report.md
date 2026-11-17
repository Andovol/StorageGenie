# SG-333 report — screenshots of the catalog redesign on a scratch app, proven from the DOM

Slice SG-333. Model and effort are not visible in my process arguments, so I state neither and infer nothing. Working directory `/home/andrei/StorageGenie`. Remote `origin` = `git@github.com:Andovol/StorageGenie.git`. BASE ref `origin/automation`, resolved BASE commit `a369a44acafed4832fe0c4c46a00f478acd813fb` (HEAD == BASE before the report commit; the report commit hash is in the publish output below).

Contract: I received no contract version line for this run, so I echo no version line.

## Time

- Start 1794950973. Stop-rule point (1100 s) = 1794952073. Cleanup (scratch removed) 1794951943; report written after. The 1100 s rule never triggered. REMAINING: none.
- G0 preflight 1794951006–1010 (verbatim block + `date +%s`; `docker version` shows a Server section 29.9.2; socket `/run/dispatch-storagegenie-SG-333/docker.sock` listed; health `curl http://127.0.0.1:8003/v1/health` = 200).
- G1 migrate 1794951086 (rc 0, `sg333.db` 396K, head `20261102_sg279_candidate_state`); backend start 1794951091–93 (PID 1914117, 200); seed 1794951144–45 (rc 0, 12 live + 1 gone, `past=1 soon=2`); build 1794951154–58 (rc 0, 2.91 s); bundle check 1794951160 (7 / 0); frontend start (serving pair) 1794951661–62 (PID 1930640, 200). First frontend preview (PID from 1794951164) exited on its own before the shots; the first shoot run 1794951288–1632 failed all six (0 cards, `ERR_CONNECTION_REFUSED`, hashes 43ec…/401f… — discarded, retaken once per the packet). Second shoot 1794951698–1766 (rc 0, ALL_DONE 6).
- G2 proofs inspected 1794951774–1859; all six PNGs opened and checked; INDEX written 17949519xx. Health 200 at end: live `8003` = 200 at 1794951937; scratch servers answered 200 during the run and were stopped by PID (000 after stop, expected).
- Elapsed ≈ 970 s (1794950973→1794951943). No optional goal.

## How the servers were started and the photos given

- Preflight exactly as the packet with `DOCKER_CONFIG`/`DOCKER_HOST` under scratch, `PATH` with the backend venv, `TMPDIR` pointed at scratch, `PYTEST_ADDOPTS` pointed at scratch, `echo`, `ls -l` of the socket dir, `docker version`, `curl` health, then `date +%s`.
- DB: `DATABASE_URL=sqlite:////home/andrei/StorageGenie/output/SG-333-scratch/sg333.db`, `STORAGE_ROOT` under scratch, `alembic upgrade head` from `backend/` (rc 0).
- Seed `output/SG-333-scratch/seed.py` (scratch, removed): no `/v1/imports` path at all — `POST /v1/households`, `POST /v1/evidence` (multipart PNG), `POST /v1/assets`, `POST …/classification {"category":"food"}`, `POST …/expiry {"expiry_date":…}`, `POST …/gone {"reason":"used_up"}` via httpx from the backend venv (no install). PNGs made with the backend venv's Pillow (no install — 48×48 solid red/green/blue/yellow, 126–129 bytes). Nothing in `backend/` was changed.
- No provider network: the seed never calls the import/run path; backend ran with `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY= SG_CONSENT=false`, `cwd=backend` (root `.env` not read); `app/services/providers/fake.py:1` docstring reads "no network, no key, no SDK" and `grep -rE "requests|httpx|urllib|urlopen|socket"` on that file returns 0 hits; `provider_call` table count is 0 after seeding (sqlite check); backend log shows only evidence/asset/classification/expiry/gone routes, no import run.
- Backend: `DATABASE_URL`, `STORAGE_ROOT`, `CORS_ORIGINS=http://127.0.0.1:14333`, fake-provider envs, `cwd=backend`, `nohup ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 18333 > scratch/logs/backend.log 2>&1 &`, PID file, wait loop for 200 on `/v1/health` (PID 1914117, 200 quoted).
- Frontend: `VITE_API_BASE=http://127.0.0.1:18333`, `NPM_CONFIG_CACHE` under scratch, `node node_modules/vite/bin/vite.js build --outDir scratch/build` from `frontend/` (rc 0), then `nohup node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 14333 --strictPort --outDir scratch/build > scratch/logs/frontend2.log 2>&1 &`, PID file, wait loop for 200 on `/` (PID 1930640, 200 quoted; the earlier preview PID exited before the shots and was replaced — stated, not hidden).
- Bundle check on `build/assets/index-CVimjnED.js`: `grep -o 127.0.0.1:18333 | wc -l` = 7 (> 0); `grep -o 8003 | wc -l` = 0 (else STOP, did not stop).
- Driver: one headless Chrome (`/usr/bin/google-chrome`, `--headless=new --no-sandbox`, `--user-data-dir` under scratch, `HOME` pointed at scratch), one page target, one DevTools WS session, built-in `WebSocket` only. Theme via `localStorage["sg-theme"]` + reload (SG-326 method); `household_id` seeded the same way. Per-row through the page's own visible control (`.sg-per-row-button` click returns `clicked:4` on 04/06, quoted; defaults remove the key, no click). Full-page screenshots (`captureBeyondViewport:true`, full-content clip) into `docs/worklogs/SG-333_shots/`.

## Shots (full proofs in `docs/worklogs/SG-333_shots/INDEX.md`)

Run date 2026-11-17; dates computed from it: past 2026-11-16 (Olive Oil #1), this-week 2026-11-19 (Milk) and 2026-11-22 (Olive Oil #2), later 2026-12-17 (Rice) / 2027-01-16 / 2027-02-15 / 2027-03-17 / 2027-05-16 / 2027-06-05 / 2027-07-25 / 2027-09-13, no-date Pasta, gone Old Jam 2026-12-27 (behind `Gone (1)`).

| # | file | theme / width | sha12 | bytes | proving DOM text |
|---|---|---|---|---|---|
| 01 | 01-catalog-light-1280-5.png | light 1280 | 7e186ab1dfe4 | 86966 | `Your things`, `12 things`, `Gone (1)`, `1 item is past its date and 2 run out this week. Show them`, sort `useby` / `Use by, soonest first`; grid 5 tracks, firstRow 5; `sg-per-row-wide` null (default), active `5:true` |
| 02 | 02-catalog-dark-1280-5.png | dark 1280 | 6e1b097c1f34 | 86507 | same title/attention/sort as 01 on dark; 5 tracks, firstRow 5; `sg-per-row-wide` null, active `5:true` |
| 03 | 03-catalog-light-390-3.png | light 390 | 48ca1f1bf413 | 49901 | same title/attention/sort; narrow dates `Past · 16 Nov` / `19 Nov` / `22 Nov` / `No date`; 3 tracks, firstRow 3; `sg-per-row-narrow` null (default), active `3:true` |
| 04 | 04-catalog-light-390-4.png | light 390 | 0452ff2819a9 | 45795 | same title/attention/sort; 4 tracks, firstRow 4; `sg-per-row-narrow` = `4`, control `clicked:4`, active `4:true` (visible-control set) |
| 05 | 05-catalog-dark-390-3.png | dark 390 | 6835ae53cd28 | 49587 | same title/attention/sort on dark; 3 tracks, firstRow 3; `sg-per-row-narrow` null, active `3:true` |
| 06 | 06-catalog-dark-390-4.png | dark 390 | 698f4ec38faf | 45498 | same title/attention/sort on dark; 4 tracks, firstRow 4; `sg-per-row-narrow` = `4`, control `clicked:4`, active `4:true` |

Every shot (probe fields in INDEX.md): `body` bg light `rgb(243, 242, 239)` / dark `rgb(18, 20, 25)`; wrapper `[data-testid="page-container"]` transparent; heading/card-name/button fonts all `"Instrument Sans Variable", system-ui, …` (named selectors per shot); every visible button/link carries a numeric WCAG ratio (01 min 5.44 over 33 ctrls, 02 min 7.57, 03/04 min 5.44 over 24, 05/06 min 7.57 — none missing or "n/a"); every card date line carries a numeric ratio on the card's effective background (past 8.37 light / 11.71 dark, soon 8.0 / 12.99, later 15.36 / 15.32, none 5.44 / 7.57 — past and this-week lines by name); smallest font 13 px, under-13 `[]`, mono `[]` on all six; corners card/tile/button all `0px`; tiles 4× `<img naturalWidth 48>` (loaded, not broken) + 8× `fallback-icon(Package)` per shot; Olive Oils `Past its date · 16 Nov` vs `Use by 22 Nov · 5 days` wide (`Past · 16 Nov` vs `22 Nov` narrow), told apart at a glance by tile color + date wash/text (image + DOM); phone shots scroll `390` vs `390` equal, `trunc []`, toolbar container wraps to two rows on narrow (image; DOM `toolbarTops [187,187,192,234,234,238,224,224]` on 03) while no control's own text wraps (probe `toolbarWrap:true` is the 44 px min-height artifact — stated, image is the authority); forbidden/ISO scans `hits []` / `isoHits []` on all six; distinct hashes 6/6 quoted above.

The first shoot run (6 shots, 0 cards, `ERR_CONNECTION_REFUSED`) was discarded and every shot retaken once in the second run — no shot is described as showing what it does not; every "shows" sentence in INDEX names the DOM read or the opened image proving it. All six PNGs were opened before the design notes below were written.

## Design notes (each from its image or a DOM read, named)

- 01 (image + DOM): no clipping/crowding — airy 5-across grid, DOM `trunc []` proves no name clips; one paper ground (DOM body vs transparent wrapper); photo tiles are loud solid scratch colors against quiet grey cubes (image — scratch artifact, placeholder itself reads fine); no text under 13 px (DOM); weakest contrast 5.44 muted passes 4.5, image crisp; no leftover wording (`Uncategorized` is the designed word, `Show them` designed, `Add item` present not `Import Asset`); dates in owner words with year on later cards, `No date yet` (DOM + image); cubes sit well beside photos; Olive Oils told apart by red/green tiles + washes (image + DOM).
- 02 (image + DOM): same layout on dark; one dark ground; solids pop on dark (image, scratch); weakest 7.57 — dark text stronger than light; all else as 01.
- 03 (image + DOM): 3 per row breathes at 390 (tiles ~108.7 px DOM, image); narrow short dates (`Past · 16 Nov`, bare `19 Nov`) read well; no sideways scroll (DOM 390/390) and no trunc; toolbar two rows by design, no control wraps (image); muted 5.44 passes.
- 04 (image + DOM): 4 per row via the visible `4` control (DOM `clicked:4`); tiles ~79.5 px — tighter than 03 but every name/date stays one-line in the image and DOM `trunc []` proves none wraps or truncates; readable, 3 airier — owner call.
- 05 (image + DOM): dark 3 per row, same comfort as 03; weakest 7.57, highly legible; all else as 03 on dark.
- 06 (image + DOM): dark 4 per row via visible control; same tight-but-readable verdict as 04 with dark minima 7.57; owner call between airy 3 and dense 4.

## UNCLEAR / REMAINING

- UNCLEAR: the driver's `toolbarWrap` boolean is a minHeight artifact (44 px buttons vs 13 px text) — it reads true on all six shots while the images show no control text wrapping; the images plus `trunc []` and `toolbarTops` are the authority (stated in INDEX per shot).
- UNCLEAR: font-load proof (`document.fonts` status) not checked; the Instrument Sans stack is quoted from computed style only (same caveat as SG-326).
- UNCLEAR: photo tiles are solid scratch colors ( Pillow red/green/blue/yellow) — they prove loaded vs placeholder tiles, not real photography.
- REMAINING: none — all six shots pass with every G2 DOM read in INDEX.md.

## Criteria

- A1 — Preflight `docker version` Server section 29.9.2 shown, socket listed, busybox n/a (not required here), health 200 at start (1794951006 preflight) and 200 at end (live 8003 at 1794951937); phase seconds above from stamps. PASS.
- A2 — Scratch app on 18333/14333, background starts with PIDs 1914117/1930640 and 200s quoted; bundle check 7/0 quoted; photos via evidence upload of Pillow PNGs (method + sizes quoted) with no-provider evidence (no import path, fake docstring, import-grep 0, `provider_call` 0); dates used with the run date 2026-11-17 they were computed from. PASS.
- A3 — Six shots with hash, size, proving text and every G2 DOM read in INDEX.md; per-row track count equal to the table on every shot (5/5/3/4/3/4 with firstRow equal); distinct-hash check 6/6 quoted. PASS.
- A4 — Design notes per shot, each naming its image or DOM read and checking every named item. PASS.
- A5 — Only `docs/worklogs/SG-333_shots/` (6 PNG + INDEX.md) plus this report written; no product/test/backend/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/stored-files/host/provider/container/deploy bytes; `frontend/dist` untouched (nothing in `git status` beyond the two worklog paths); no `/tmp` (all logs/builds/profiles/caches under scratch via `TMPDIR`/`NPM_CONFIG_CACHE`/`HOME`/`--user-data-dir`, scratch removed by exact path before the report — absent). PASS.
- A6 — Vacuity checked: track count vs table (all equal, listed), broken photo (`naturalWidth` 48 on all 4 photo cards per shot, none 0), attention line present with a past item (quoted on all six), rounded corner (all `0px`), ISO date in text (scans `[]`), raw status word (scans `[]` incl. `ACTIVE`/`ARCHIVED`), button/date line under 4.5:1 (minima 5.44 light / 7.57 dark, all ≥4.5), sideways scroll at 390 (390/390 ×4), two shots one hash (6 distinct quoted), bundle pointing at 8003 (grep 0), scratch left behind (absent). PASS.
- A7: see last line.

Verification: PASS
