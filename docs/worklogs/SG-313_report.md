SG-313 | model opencode-go/muse-spark-1.3-contributor effort xhigh (inferred from STATE.md next-slot "SG-313 on Muse" and AGENTS.md rotation Haiku/high → Muse/xhigh; process arguments were not exposed in this run) | cwd /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> resolved 5e23b0772efd31e4119e6f9b3e7fa121fb55b4a9 | WORK_HEAD 5e23b0772efd31e4119e6f9b3e7fa121fb55b4a9 (pre-report HEAD; the report commit hash is in the publish output)

# SG-313 report: SG-312's screenshots, proven from the DOM

**Result: G0, G1, G2 done. No product or test byte changed. Verification: PASS.**

## Elapsed and phase seconds (stamps from `date +%s`)

- Start 1794506157. Stop-rule point (1100 s) = 1794507257. Scratch removed 1794506793 (636 s), end health 1794506797 (640 s). Well under the stop line; no stop, no REMAINING for time.
- G0 preflight 1794506157 → 1794506175 (18 s): `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-313/docker.sock`, `ls -l` shows `docker.sock`, `docker version` Server section present (Client 29.9.2, Server 29.9.2), health `200` on 8003 at start.
- G1 migrate 1794506287 → 1794506291 (4 s, rc 0, head `20261102_sg279_candidate_state`); frontend build 1794506297 (2.64 s, rc 0, `vite build --outDir ../output/SG-313-scratch/ui`); bundle check 7 hits `127.0.0.1:18313`, 0 hits `8003`; backend up 1794506307 → 1794506309 (PID 560870, `200 {"status":"ok","db":"ok","storage":"ok"}`); frontend up 1794506315 → 1794506317 (PID 561135, `200`); seed 1794506366 (9 assets + 1 skipped-step import, rc 0).
- G2 shots 1794506614 → 1794506748 (134 s, 4 shots, rc 0); retake 01 1794506695 (byte-identical PNG, improved step query); servers stopped 1794506793 by PID (no `pkill -f`); scratch removed by exact path `rm -rf /home/andrei/StorageGenie/output/SG-313-scratch` (rc 0); health end 1794506797 `200 {"status":"ok","db":"ok","storage":"ok"}`.

## How the servers were started and the skipped step made

Both servers started in the background, never in the foreground — the one thing SG-312 lost its shots to. Shape used, each in a single Bash call that returned at once:

- Backend (cwd `backend`): `DATABASE_URL=sqlite:////home/andrei/StorageGenie/output/SG-313-scratch/scratch.db STORAGE_ROOT=/home/andrei/StorageGenie/output/SG-313-scratch/storage SG_CONSENT=false SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY= CORS_ORIGINS=http://127.0.0.1:14313 nohup ./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18313 > ../output/SG-313-scratch/backend.log 2>&1 < /dev/null & echo $! > ../output/SG-313-scratch/backend.pid`, then the 30×2 s poll loop (200 in 2 s, PID 560870 quoted from the `.pid` file).
- Frontend (cwd `frontend`): `nohup ./node_modules/.bin/vite preview --host 127.0.0.1 --port 14313 --outDir ../output/SG-313-scratch/ui --strictPort > ../output/SG-313-scratch/frontend.log 2>&1 < /dev/null & echo $! > ../output/SG-313-scratch/frontend.pid`, poll loop (200 in 2 s, PID 561135 quoted).
- The `&` binding returned at once (verified with a `sleep 5` probe: start/end stamps in the same call, no wait); no call ever held 600 s.

Skipped AI step, as SG-311 did (`docs/worklogs/SG-311_report.md` § *How the skipped AI step was made*): backend started with `SG_CONSENT=false SG_PROVIDER_ID=fake` and empty `OPENCODE_API_KEY/JINA_API_KEY/OPENROUTER_API_KEY`, cwd `backend` (root `.env` not read); then `POST /v1/evidence` (multipart generated PNG), `POST /v1/imports` with that evidence, `POST /v1/imports/{id}/run`. Run output proves the skip: `ANALYZING_WITH_AI COMPLETED {"status":"skipped","reason":"consent_disabled"}`, `BUILDING_CANDIDATES COMPLETED {"status":"skipped","reason":"consent_disabled"}`, job state `AWAITING_REVIEW`. The Inbox renders these as `Analyzing with ai: Skipped (AI off)` / `Building candidates: Skipped (AI off)`, never `Done`.

Test data through the API only, with generated images (Pillow solid PNGs): household `SG-313 Scratch`; Milk 1000 ml expired 2026-11-07 (amount, expired), Eggs 12 piece 2026-11-12 (counted, critical), Cheese 200 g 2026-11-15 (urgent), nameless 250 g 2026-11-20 (no name, upcoming), Yogurt 2026-11-27 (upcoming), Warranty Papers documents_other 2026-12-27 (non-food paper, long_lead), Rice 2027-02-10 (safe), Ketchup food dateless (unresolved `needs_evidence`), Wrench non_perishable dateless (non-food, unresolved `dateless`). Expiry status confirms every tier: `by_tier {none:1, critical:1, urgent:1, upcoming:2, long_lead:1, safe:1}`, `by_bucket {expired:1, this-week:2, this-month:2, safe:2}`, unresolved 2.

## Shot table (full proofs in `docs/worklogs/SG-312_shots/INDEX.md`; every sentence saying a shot "shows" names the DOM read)

| # | file | state | sha12 | bytes | proving DOM text |
|---|---|---|---|---|---|
| 01 | 01-inbox-light-1280.png | light 1280 | 3a80f9fd7394 | 73363 | h1 "Inbox" (`h1.page-header`); job card `aria-label="Import job, Waiting for you"` + date div `Today, 17:59`; detail `Waiting for you · 6/8 complete`; candidate `sg313-import · Waiting for you`; review `Date needed · High · Open / Ketchup` |
| 02 | 02-expiry-light-1280.png | light 1280 | 7acd840d4ce4 | 92382 | h1 "Expiry"; `Food and other dated things, soonest first.` (`p(first)`); buckets Expired(1)/This week(2)/This month(2)/Safe(2)/Unresolved(2); pills `Use first, Use soon, Upcoming×2, Long lead, Safe` |
| 03 | 03-asset-dark-1280.png | dark 1280 | 73eb8ef9c44f | 62300 | h1 "Milk"; `Live · 1000 ml left` (not `qty`); `Enrich costs up to $0.05 a press` (not per-press); `Date confirmed` (not evidence state); `Manual expiry entry` |
| 04 | 04-pantry-light-375.png | light 375 | e5629725a63b | 28399 | h1 "Pantry"; `7 ITEMS` (`[data-testid="pantry-count"]`); `What you have, and what to use first.`; `USE SOON` Milk EXPIRED / Eggs Use today / Cheese Use in 3 days |

- Body ground: 01 `rgb(244, 240, 232)`, 02 `rgb(244, 240, 232)`, 03 `rgb(32, 27, 23)`, 04 `rgb(244, 240, 232)` — light = `--paper` `40 35.3% 93.3%`, dark = `--paper` `26.7 16.4% 10.8%` (comparison of the computed `background-color` of `body` against the token values in `frontend/src/theme/tokens.css:37,71` proves the paper ground; the report sentence "body is on paper" names this comparison). Wrapper `[data-testid="page-container"]` is `rgba(0, 0, 0, 0)` on all four (transparent; paper shows from `body`).
- Fonts (computed `font-family`, same session): every heading (`h1.page-header`), every body node (`p(first)` or page-root `div`), and every button on all four shots is `"Instrument Sans Variable", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` — the button stack proves the SG-312 `button { font: inherit }` rule (`tokens.css:94-101`); SG-311 read Arial on buttons, now Instrument Sans on `Switch to dark theme`, `Import job`, `Edit`, `Use it up`, `−1`, `Save date`, `Clear expiry date` (each named in INDEX.md with its selector).
- Every visible `button` bg/color (INDEX.md lists all): 01 two buttons (theme toggle white `--card` `rgb(255,255,255)`/`rgb(28,25,23)`, job card paper `rgb(244,240,232)`/`rgb(25,25,25)`); 02 one button (theme toggle white card); 03 ten buttons (`Edit` dark card `rgb(28,26,24)`, `Enrich`/`Save shelf life`/`Save date` primary `rgb(110,48,46)` on `rgb(250,250,249)`, `Used up/Thrown away/Given away` `rgb(15,14,13)` on ink, `Clear expiry date` dark card, `Attach evidence` `rgb(38,35,32)`); 04 twenty-five buttons (`Menu` paper, theme toggle white card, 7 transparent `Open …` image buttons, 8 white-card `Edit`/`Take off 1` + 8 white-card `Use it up` — the white `--card` Pantry controls are measured as `rgb(255,255,255)` on paper `rgb(244,240,232)`, not guessed).
- Smallest font-size: `13px` on all four (01 `a "Catalog"`, 02 `a "Catalog"`, 03 `a "Catalog"`, 04 `button "Menu"`); under-13px nodes: none on any shot (`under13: []` quoted).
- Contrast (WCAG from the two computed colours, script-computed): 01 heading `15.39` / body `15.39` / button `17.49`; 02 `15.39` / `5.32` (muted 13px, passes 4.5:1) / `17.49`; 03 `15.64` / `15.64` / `15.90`; 04 `15.39` / `5.32` / `15.47` (Menu paper button).
- 01 steps (Selected-job `section`, `strong` parents): `Validating input: Done`, `Tidying the details: Done`, `Checking the file: Done`, `Analyzing with ai: Skipped (AI off)`, `Building candidates: Skipped (AI off)`, `Looking for duplicates: Done`, `Your review: Waiting for you`, `Saving: In progress`; job date `Today, 17:59` (job-card date divs `["Today, 17:59"]`). The three mapped names match SG-312 (`Checking the file`, `Tidying the details`, `Looking for duplicates`, `Your review`, `Saving`); the two skipped steps read `Skipped (AI off)`, never `Done`; `Validating input`/`Analyzing with ai`/`Building candidates` are the `sentenceCase` fallback (backend names with no map entry) — reported, not hidden.
- Menu display at 1280: 01 `none`, 02 `none`, 03 `none` (all `.nav-menu-toggle` computed `display`, expected `none` per `tokens.css:285-297` + `App.tsx:91` class). 04 (375) `flex` (visible, expected below 768).
- 02 tiers: `["Use first", "Use soon", "Upcoming", "Upcoming", "Long lead", "Safe"]` (`[data-testid="tier-pill"]` texts; expired Milk correctly carries no pill, tier null).
- 04 header: `nav` height `93px`; children tops `a:16, Menu button:13, .nav-menu:0 (h 0, collapsed), theme:12, Import Asset:52` — tops are not equal, so children sit on **two rows** (Import drops under the logo row at 375).
- Absence 01–03 (`document.body.innerText` + `/Import [0-9a-f]{8}/`): `optimistic concurrency:absent`, `blueprint:absent`, `Phase 0:absent`, `AWAITING_REVIEW:absent`, `consent_disabled:absent`, `If-Match:absent`, `evidence state:absent`, `per-press:absent`, `Import-hex:absent` (all three shots, quoted in INDEX.md).
- Distinct-hash: `4 files, 4 distinct 12-char prefixes` (`3a80f9fd7394, 7acd840d4ce4, 73eb8ef9c44f, e5629725a63b`).

I opened every screenshot myself (image reads of all four PNGs before writing this report).

## Design notes, not fixes

- 01 Inbox light: the fallback step names read `Analyzing with ai` / `Building candidates` / `Validating input` — sentence-case with a lowercase `ai`, inconsistent with the mapped `Checking the file` / `Tidying the details` style; the two skipped rows are the only ones saying `Skipped (AI off)`, which reads clearly. The theme-toggle button is white `--card` on paper while the job card is paper — two whites that do not match. No text under 13px; contrast passes.
- 02 Expiry light: rows are paper cards with a `--line` border on the paper ground — calm and grouped; the expired Milk row correctly shows no tier pill, but a first-time owner might expect an `Expired` pill where the tier would be. Tier pills are 13px muted (`5.32:1`, passes) but sit far right of the date, visually detached from the tier they name. No crowding at 1280.
- 03 Asset dark: `Live · 1000 ml left`, `Enrich costs up to $0.05 a press`, `Date confirmed` all read plain — the developer wording is gone. The native `Choose Files` control is white on dark (the only white-on-dark control; every `button` is Instrument Sans on dark tokens, measured). `Used up / Thrown away / Given away` are `rgb(15,14,13)` chips on `rgb(32,27,23)` — subtle, almost the same surface. Nothing clipped; nothing under 13px.
- 04 Pantry 375: the header is two rows (93px; Import sits at top 52 under the logo row tops 12–16) — the one-row-375 question from SG-312 is settled: it does not fit on one row. Pantry tile `Edit` / `Use it up` / `−1` are white `rgb(255,255,255)` on paper `rgb(244,240,232)` — the mismatched white-on-paper surface SG-312 left open, now measured on every tile. `EXPIRED` is 13px, nothing smaller; the generated solid-color photos are placeholders, not a design verdict.

## Contract line

No contract line received in this packet's context. The packet states `0.59.0` (`AGENTS.md`, D30) but gives no line of my own to echo, and this lane denies the contract folder, so I did not read it.

## UNCLEAR / REMAINING

- REMAINING: none in the shot list. All four shots taken with full DOM proofs, distinct hashes quoted, servers stopped by PID, scratch removed by exact path.
- UNCLEAR: whether the Instrument Sans woff2 actually loaded (`document.fonts` status not checked); the shots prove the computed stack, not a face-load proof (same gap SG-311 noted).
- UNCLEAR: `frontend/dist` untouched — the build used `--outDir ../output/SG-313-scratch/ui`; `dist` mtime not checked explicitly (same gap SG-311 noted). No `frontend/dist` byte appears in `git status`.
- The `Analyzing with ai` / `Building candidates` / `Validating input` fallback names are reported above, not fixed (scope ceiling: no product byte).

## One line per criterion

- **A1** — Preflight proven (Server section, socket present, `docker version` rc 0, health 200 start 1794506175 and end 1794506797); phase seconds from stamps above.
- **A2** — Scratch app on 18313/14313, both started in the background with PID (560870/561135) and 200 quoted; bundle check quoted (7 / 0); skipped-step import made by consent-off + `fake` provider, `consent_disabled` quoted from the run output and `Skipped (AI off)` from the DOM.
- **A3** — Four shots with hash, size, proving text and every DOM read listed in G2 (body/wrapper bg, three fonts, every button bg/color, min-size + under-13, three contrasts, 01 steps + date, 01–03 Menu `none`, 02 tiers, 04 header 93px + tops, 01–03 absence); distinct-hash check quoted (4/4).
- **A4** — Design notes per shot above (two–three lines each, report-only, no fix).
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes (`git status` shows only `docs/worklogs/SG-312_shots/` untracked before this report); `frontend/dist` untouched; no `/tmp` (Chrome profile, cache and tmp under scratch; `curl -o /dev/null` only); scratch removed by exact path before this report (`rm -rf …/output/SG-313-scratch`, rc 0).
- **A6** — `PB-3` vacuity: a failure would look like a non-paper `body`, a system font or Arial on a button, an uppercase step name, a skipped step reading `Done`, an ISO date, `Menu` displayed at 1280, a removed string in `innerText`, two shots with one hash, a bundle pointing at 8003, a server call that did not return, scratch left behind. Checked: body paper on all four (244,240,232 / 32,27,23), buttons Instrument Sans (no Arial), steps plain + skipped `Skipped (AI off)`, date `Today, 17:59`, Menu `none` at 1280, all nine strings absent, 4/4 distinct hashes, bundle 7/0, both server calls returned at once, scratch removed. None observed.
- **A7** — see last line.

Verification: PASS
