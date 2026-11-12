# SG-319 — The screenshots SG-318 owes: plain words on the catalog, asset page, item panel, Expiry and Inbox, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — SG-318's gate is green (`docs/worklogs/SG-318_report.md`: frontend 55 files / 477 tests, host 805 + 2 deselected, image proof 2, eslint only the known error).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-319*` and `docs/worklogs/SG-318_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.** No deploy; a rider follows once these screens are seen.
**Provider: none.** No key, no `.env`, no spend; every provider off.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D18, D33 (*"D33 approved."*: the wording slice, its screenshots, rider); stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."*

## Why this exists

SG-318 (`0e04e0a..8dd5717`, report `docs/worklogs/SG-318_report.md`) replaced developer text with plain words (expected, `UNVERIFIED` — establish each): catalog chips through `labelAssetType` (*Food & beverages*); the asset page's Details table (no `[object Object]`, rows named *Kind of item*, *Status*, *Unit*, dates as *7 Nov 2026*) and History (*Today, 19:06*, *Added*, *Accepted*); *No photo yet* at 13 px in the evidence gallery and as the item panel's fallback when a photo fails to load; *Unnamed item* for nameless items (some *Untitled item* literals are known to remain in `CatalogPage.tsx`, `PantryPage.tsx`, `OpenedCountdownSection.tsx` — report what you see); Expiry dates as *7 Nov 2026* and tier pills only for *Use first* / *Use soon*; Inbox `PENDING` as *Not started* and steps *Checking your upload*, *Reading the photo*, *Making items*. **Its tests check the source; nothing has shown the screens.**

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-319-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-319-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-319/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-319/
docker version
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-319-scratch/`, npm's cache there too if needed; **no `/tmp` for anything, including `tee`, `curl -o` and Chrome's profile.** `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app, servers in the background

As SG-311 did (`docs/worklogs/SG-311_report.md` § *How the skipped AI step was made*): a fresh SQLite under `output/SG-319-scratch/` by the project's migrations (`alembic upgrade head`); test data **through the API** with generated images — food and non-food, one item with no name, one expired food item, a few due soon, one counted and one amount item, **one item whose photo file is missing or unreadable** (so the panel's fallback shows; say how you made it), one nameless item, items in several Expiry tiers, and **one Inbox import whose AI step is skipped** (it puts a *Review status* select on Inbox) (backend started with `SG_CONSENT=false SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend`; then `POST /v1/evidence`, `POST /v1/imports`, `POST /v1/imports/{id}/run`). Never port 8003, the live container or the stored files.

Ports and the build, literally:

```
export SG319_API=http://127.0.0.1:18319
# frontend build into scratch with VITE_API_BASE="$SG319_API", then:
grep -o '127\.0\.0\.1:18319' <built main js> | wc -l   # must be > 0
grep -o '8003' <built main js> | wc -l                 # must be 0, else STOP
```

**Start every server in the background, never in the foreground.** The shape, for each of the backend (`127.0.0.1:18319`) and the frontend (`127.0.0.1:14319`):

```
nohup <server command> > output/SG-319-scratch/<name>.log 2>&1 &
echo $! > output/SG-319-scratch/<name>.pid
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' <url> | grep -q 200 && break; sleep 2; done
```

The call must return at once; a server not answering 200 within 60 s is reported with the last 20 lines of its log, and the slice stops at that point. **SG-312 lost its screenshots to a foreground start that held the call for 600 s — this is the one thing this slice must not repeat.**

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install; Chrome's `--user-data-dir` under scratch). Theme set the way SG-311 did. Into `docs/worklogs/SG-318_shots/`, in this order:

| Shot | Screen | Theme | Width |
|---|---|---|---|
| 01 | Catalog, the grid | light | 1280 |
| 02 | Asset page of a dated food item, scrolled to **Details and History** | light | 1280 |
| 03 | Asset page, the evidence area of an item with no photo | dark | 1280 |
| 04 | Item panel open on the item whose photo fails to load | light | 1280 |
| 05 | Expiry page | light | 1280 |
| 06 | Inbox, the skipped-step import open | light | 1280 |

The panel opens by a click on a card through the same DevTools session; say how.

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-318_shots/INDEX.md`:**

- sha256 (12) and size; the on-screen text that proves the state.
- **Computed `background-color` of `body` and of the main content wrapper** (name the selector you read).
- **Computed `font-family` of the page heading, of one body text node, and of one button** (name each element).
- **Computed `background-color` and `color` of every visible `button`** (text, background), so the white-`--card` controls are measured, not guessed.
- **Smallest computed `font-size` among visible text nodes**, and every text node under 13 px quoted with its size.
- **Contrast ratio** (WCAG formula, computed in the script from the two computed colours) of the heading, a body node and one button against their effective background.
- **Whether any visible text node's computed `font-family` contains `mono`** (expected none — list any).
- On 01: every card's category chip text (expected plain words, no `_`).
- On 02: every Details row as rendered (label → value) and every History line as rendered.
- On 03: the gallery's empty text and its computed `font-size`.
- On 04: whether any `<img>` in the panel has `naturalWidth` 0 while displayed (expected none); the fallback text as rendered.
- On 05: every row's date text and every tier pill's text.
- On 06: every step label as rendered and the job date.
- On every shot: **none** of `[object Object]`, `food_beverages`, `documents_other`, `non_perishable`, `Thumbnail unavailable`, `Untitled asset`, `noname`, `Analyzing with ai`, `AWAITING_REVIEW`, `consent_disabled`, `If-Match`, and **no ISO stamp** (regex `\d{4}-\d{2}-\d{2}`) in `document.body.innerText` (quote the check; list each hit with where it appears).
- On every shot: the computed `display` of the *Menu* button (expected `none`).
- **No two shots share a hash** — check it and quote the check.

A shot failing its proof is retaken once, then reported failed — **never described as showing what it does not. Every sentence saying a shot "shows" something names the DOM read that proves it.**

**Design notes, not fixes:** for each shot, two or three lines on anything that looks wrong to an owner who cares about design. **Check each of these by name, every shot:** clipping or crowding; mismatched surfaces (white on paper); text under 13 px; weak contrast; leftover developer wording; **date format** (an ISO date such as `2026-11-07` is a finding); **status words that say something untrue** (e.g. *In progress* for something waiting); category and heading names that contradict each other. Report it; change nothing.

Stop the servers by the PIDs in the `.pid` files, never `pkill -f`; **remove `output/SG-319-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18319/14319, both started in the background with the PID and the 200 quoted; the bundle check quoted; the skipped-step import made and how.
- **A3** — Six shots with hash, size, proving text and every DOM read listed in G2; distinct-hash check quoted.
- **A4** — Design notes per shot.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a non-paper `body`, a system font or Arial on a button, an uppercase step name, a skipped step reading *Done*, an ISO date, *Menu* displayed at 1280, a removed string in `innerText`, two shots with one hash, a bundle pointing at 8003, a server call that did not return, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-319*`, `docs/worklogs/SG-318_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; the frontend build into scratch; the scratch servers on `127.0.0.1:18319` and `:14319`, in the background; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each (the call itself returns at once); one screenshot **60 s**; ordinary commands **120 s**. No interactive command, no foreground server.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, stop the servers, remove scratch, commit, write the report, publish.** **No optional goal.** Expected ≈700 s (`UNVERIFIED — my estimate`: SG-313 640 s for four shots; SG-316 needed three attempts for seven). **Write each design-note sentence from the image or a DOM read, and name which** — a note not checked against its own shot is a defect. A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-319_report.md`. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the servers were started and the skipped step made; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-319`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-319 | Report: docs/worklogs/SG-319_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
