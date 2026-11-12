# SG-311 report — screenshots of the SG-301 screens, proven from the DOM

SG-311 | model opencode-go/claude-haiku-5-5 | effort high (from process args: `opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/claude-haiku-5-5 --variant high`) | cwd /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation → resolved c3c0d9b958826a4e873bd3a816de184e7eb75ae7 | WORK_HEAD c3c0d9b958826a4e873bd3a816de184e7eb75ae7 (pre-report HEAD; the report commit hash is in the publish output).

Contract: the repo's `AGENTS.md` (in my context at session start) records `Rule-set version recorded here: 0.59.0 (D30, 2026-11-12)`; I echo that line from the file. The contract folder was not read. No separate contract version line was received in this run.

## Time (stamps from `date +%s`)

- Start 1794493899. Stop-rule point (1100 s) = 1794494999. Final cleanup stamp 1794494783 = 884 s.
- G0 preflight: 1794493899 → 1794493900 (1 s). Docker `version` Server section present; socket `/run/dispatch-storagegenie-SG-311/docker.sock` present; health 200 `{"status":"ok","db":"ok","storage":"ok"}`.
- G1 migrate 1794493962 → 1794493963 (1 s, rc 0); frontend build into scratch 1794493963 → 1794493966 (3 s, rc 0); servers up 1794493966 → 1794493968.
- Lost time: the first server start was killed when its shell call hit the 400 s tool timeout (1794493968 → 1794494375); servers were restarted 1794494381 → 1794494383. A second call also waited out its 120 s timeout (the `&` binding kept the shell attached). Both are my errors, not product faults.
- Seed 1794494529 → 1794494530 (1 s, 14 assets, one import job).
- Shots: first DevTools attempts 1794494580 → 1794494614 failed (see "Browser" below); final run 1794494670 → 1794494714 (44 s, 7 shots). Retake of shot 05 1794494761 → 1794494772 (11 s). Stop/kill/removal 1794494783.
- Health at end: `curl` 8003 `/v1/health` at 1794494842 = `http=200`, body `{"status":"ok","db":"ok","storage":"ok"}`.

## How the skipped AI step was made

No provider, no key, no consent. `backend/app/config.py:46` defaults `sg_consent: bool = False`; `backend/app/services/providers/reader.py:106-107` returns `(False, "consent_disabled")` from `ai_status()` when consent is off, and `reader.run_ai_extraction` writes `{"status":"skipped","reason":"consent_disabled"}` (seen in the run output). The backend was started with `SG_CONSENT=false SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend`, so the root `.env` (556 bytes) was not read and not opened by me. The import: `POST /v1/evidence` (multipart), `POST /v1/imports` with that evidence, `POST /v1/imports/{id}/run`. Run output: `ANALYZING_WITH_AI COMPLETED {"status":"skipped","reason":"consent_disabled"}`, `BUILDING_CANDIDATES COMPLETED {"status":"skipped","reason":"consent_disabled"}`; job state `AWAITING_REVIEW`. The Inbox shows these as `ANALYZING WITH AI: Skipped (AI off)` and `BUILDING CANDIDATES: Skipped (AI off)`.

Test data (through the API only): household "SG-311 Scratch"; 14 assets: Juice (500 ml, expired 5 days ago), Cheese (200 g, expired 3 days ago), Milk (1000 ml, expired yesterday), Yogurt (today), Apples (tomorrow), Eggs (12 piece, 3 days), Bread (5 days), Oats, Rice, Pasta (dated later), Ketchup and Soup (no date), Wrench (non-food, `non_perishable`), and one item with no name. Each has a generated PNG as evidence. Counted items: piece units; amount items: ml/g/kg units.

Bundle check (scratch build `VITE_API_BASE=http://127.0.0.1:18311`): `rg -o '127\.0\.0\.1:18311'` on `build/assets/index-U9E7nyB3.js` = 7; `rg -o '8003'` = 0. No bundle points at 8003.

## Shot table (sha256 first 12, bytes; full proofs in `docs/worklogs/SG-301_shots/INDEX.md`)

| # | file | state | sha256 (12) | bytes | proving DOM text |
|---|---|---|---|---|---|
| 01 | 01-pantry-header-light-1280.png | light 1280 | de7fb4692a45 | 47289 | h1 "Pantry"; "13 ITEMS"; EXPIRED x6 |
| 02 | 02-pantry-header-dark-1280.png | dark 1280 | 247bcc17fc63 | 47506 | h1 "Pantry"; EXPIRED x6; `html.dark` true |
| 03 | 03-pantry-header-light-375.png | light 375 | d1df0594de84 | 32381 | h1 "Pantry"; EXPIRED x6; scrollWidth 375 = clientWidth 375 |
| 04 | 04-catalog-header-light-1280.png | light 1280 | 8dc42db0ab76 | 91233 | "Showing: 14 items" |
| 05 | 05-inbox-skipped-import-dark-1280.png | dark 1280 | e6bb380dc8f4 | 85059 | h1 "Inbox"; job card "Import job · Waiting for you" opened; "ANALYZING WITH AI: Skipped (AI off)" |
| 06 | 06-expiry-dark-1280.png | dark 1280 | 909d2209e56c | 92692 | h1 "Expiry"; "Food and other dated things, soonest first." |
| 07 | 07-asset-light-1280.png | light 1280 | e0899a66b642 | 63636 | h1 "Juice"; "Live · qty 500 ml" |

Fonts (computed, same session): h1 and one body text node on every shot: `"Instrument Sans Variable", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`. Buttons (`Edit`, `Use it up`, `Choose Files`) on shots 01, 02, 03, 07: `Arial`.

EXPIRED computed font-size on shots 01, 02, 03: `13px` (6 labels each, `querySelectorAll` leaves with text EXPIRED).

Header (`<nav>`, computed background): shot 01 `rgb(244, 240, 232)` light (body `rgb(250, 250, 249)`); 02 `rgb(32, 27, 23)` dark (body `rgb(15, 14, 13)`); 03 `rgb(244, 240, 232)`; 04 `rgb(244, 240, 232)`; 06 `rgb(32, 27, 23)`; 07 `rgb(244, 240, 232)`. Shot 05 nav: `rgb(32, 27, 23)` (the first attempt read a `<header>` with transparent background; the retake reads the nav).

Absence check (`document.body.innerText`, shots 05, 06, 07): `optimistic concurrency`, `blueprint`, `Phase 0`, `AWAITING_REVIEW`, `consent_disabled`, `If-Match`, and `/Import [0-9a-f]{8}/` — all **absent** on 05, 06, 07. The skipped-step label quoted from 05: `ANALYZING WITH AI: Skipped (AI off)`; `BUILDING CANDIDATES: Skipped (AI off)`; not `Done`.

Distinct-hash check (`sha256` of the seven PNGs in `SG-301_shots/`): 7 files, 7 distinct 12-char prefixes (`distinct 7` printed by the script).

Attempt-1 of shot 05 failed its proof: the click hit the header's "Import Asset" dialog, not the job card, so the skipped step was not on screen. It was retaken once (allowed). The failed PNG is kept as `05-inbox-skipped-import-dark-1280.ATTEMPT1-FAILED.png` (sha256 12 `9a895560c3e6`, 73291 bytes; distinct from all seven). It is not in the INDEX.

Browser: `/usr/bin/google-chrome` crashed on launch in this environment (crashpad `--database is required`, then trap). Shots were taken with the Playwright `chromium_headless_shell-1208` already in `~/.cache/ms-playwright` (Chromium 145.0.7632.6), driven over DevTools from a Node script in scratch. No install.

## Design notes (one line per shot; not fixes)

- 01 (Pantry light 1280): buttons (`Edit`, `Use it up`, `−1`) are in Arial, not Instrument Sans, so the button row looks like a different system.
- 02 (Pantry dark 1280): the EXPIRED label and the dark header read cleanly; the Import Asset button is light on dark, the Menu box is a dark outline, so the header's two button styles do not match.
- 03 (Pantry light 375): the header wraps to two rows (Import Asset drops under the logo); the card grid and buttons stay clear, nothing clipped.
- 04 (Catalog light 1280): the "2m ago" date column and the `item` category chips use a monospace font, not Instrument Sans; the toolbar stacks two chip rows in different styles.
- 05 (Inbox dark 1280): the job card shows the raw timestamp `2026-11-12T14:42:10`, and the review queue rows say only "Date needed · High · Open / item" with no item name.
- 06 (Expiry dark 1280): the layout is clear; "No tier" pills sit at the right edge with no visual grouping to the tier they describe.
- 07 (Asset light 1280): the "Manual expiry entry" card is white on the cream paper, a mismatched surface; "per-press cap $0.05" is developer wording; the native "Choose Files" control is Arial.

## Contract, UNCLEAR and REMAINING

- UNCLEAR: whether the Instrument Sans woff2 actually loaded (`document.fonts` status) was not checked; the shots show the declared stack in computed style, not a face-load proof.
- UNCLEAR: `frontend/dist` was not modified by my commands (the build wrote to scratch with `--outDir`), but its mtime was not checked explicitly. Vite may have written `frontend/node_modules/.vite` cache; not product bytes.
- REMAINING: none in the shot list. Shots 01 to 04, 06 and 07 keep their PNGs from session 1; their DOM proofs are from session 2 (same URLs and themes). Shot 05 is from session 2.
- The live uvicorn on port 8000 (PID 378982) belongs to someone else; not touched.

## Criteria

- **A1** — Preflight proven (Docker Server section, socket present, `docker version` rc 0); health 200 at start (1794493899) and end (1794494842, `http=200`); phase seconds from stamps above.
- **A2** — Scratch app on 18311 and 14311; bundle check quoted (7 / 0); skipped-step import made by consent-off and provider `fake`, reason `consent_disabled` quoted from the run output.
- **A3** — Seven shots with hash, size, proving text, both font families, the EXPIRED size on Pantry, the header background, the absence check on 05/06/07, and the distinct-hash check quoted.
- **A4** — Design notes, one line per shot (above).
- **A5** — Only `docs/worklogs/SG-311_report.md` and `docs/worklogs/SG-301_shots/` written. No product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored file, host, provider, container or deploy bytes changed. No `/tmp` used (Chrome profile, crash dumps and logs in scratch). Scratch removed by exact path before this report: `rm -rf /home/andrei/StorageGenie/output/SG-311-scratch` (rc 0).
- **A6** — Vacuity checked: system font in DOM (heading and body both Instrument Sans stack; buttons Arial and noted); removed string in innerText (absent on 05/06/07); skipped step reading Done (reads "Skipped (AI off)"); EXPIRED under 13 px (13 px on 01–03); two shots with one hash (7 distinct); bundle pointing at 8003 (0); scratch left behind (removed). None observed.
- **A7** — see last line.

Verification: PASS
