# SG-316 — The screenshots SG-307 owes: the catalog and item panel in the new look, paper controls, the one-row header at 375, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — SG-307's gate is green at `14c1f1f` (`docs/worklogs/SG-315_report.md`: frontend 54 files / 467 tests, host 805 + 2 deselected, image proof 2, eslint only the known error).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-316*` and `docs/worklogs/SG-307_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.** No deploy; a rider follows once these screens are seen.
**Provider: none.** No key, no `.env`, no spend; every provider off.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D18, D33 (*"D33 approved."*: SG-307, its screenshots, rider); stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."*

## Why this exists

SG-307, SG-307r1 and SG-315 (`0dd3fa7..14c1f1f`, audit `docs/worklogs/SG-307_audit.md`) changed (expected, `UNVERIFIED` — establish each from the file before relying on it): **the catalog** (`frontend/src/routes/CatalogPage.tsx`, `frontend/src/components/catalog/*`, `frontend/src/components/shell/CatalogToolbar.tsx`) — plain status words (*Photo only*, *Cut-out ready*), *2 min ago*, no monospace, square cards on paper, an *N ITEMS* header, joined square tabs; **the item panel** (`frontend/src/components/shell/ItemInspectorDrawer.tsx`) — tabs *Photo / Cut-out / In a scene*, one-line empty states, no bounding-box or *Version* text, categories as *Food & beverages*; **one paper control rule** `sg-paper-control` in `frontend/src/theme/tokens.css`, plus a paper rule for the native file input; **Pantry buttons** on paper (`frontend/src/routes/PantryPage.tsx` `ACTION_STYLE`); **the header at ≤ 480 px** on one row (a media rule in `tokens.css` hides the *Import Asset* text and the count). **Its tests check the source; nothing has shown the screens.**

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-316-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-316-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-316/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-316/
docker version
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-316-scratch/`, npm's cache there too if needed; **no `/tmp` for anything, including `tee`, `curl -o` and Chrome's profile.** `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app, servers in the background

As SG-311 did (`docs/worklogs/SG-311_report.md` § *How the skipped AI step was made*): a fresh SQLite under `output/SG-316-scratch/` by the project's migrations (`alembic upgrade head`); test data **through the API** with generated images — food and non-food, one item with no name, one expired food item, a few due soon, one counted and one amount item, items whose catalog status differs (photo only and, if the API allows it without a provider, one other), and **one Inbox import whose AI step is skipped** (it puts a *Review status* select on Inbox) (backend started with `SG_CONSENT=false SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend`; then `POST /v1/evidence`, `POST /v1/imports`, `POST /v1/imports/{id}/run`). Never port 8003, the live container or the stored files.

Ports and the build, literally:

```
export SG316_API=http://127.0.0.1:18316
# frontend build into scratch with VITE_API_BASE="$SG316_API", then:
grep -o '127\.0\.0\.1:18316' <built main js> | wc -l   # must be > 0
grep -o '8003' <built main js> | wc -l                 # must be 0, else STOP
```

**Start every server in the background, never in the foreground.** The shape, for each of the backend (`127.0.0.1:18316`) and the frontend (`127.0.0.1:14316`):

```
nohup <server command> > output/SG-316-scratch/<name>.log 2>&1 &
echo $! > output/SG-316-scratch/<name>.pid
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' <url> | grep -q 200 && break; sleep 2; done
```

The call must return at once; a server not answering 200 within 60 s is reported with the last 20 lines of its log, and the slice stops at that point. **SG-312 lost its screenshots to a foreground start that held the call for 600 s — this is the one thing this slice must not repeat.**

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install; Chrome's `--user-data-dir` under scratch). Theme set the way SG-311 did. Into `docs/worklogs/SG-307_shots/`, in this order:

| Shot | Screen | Theme | Width |
|---|---|---|---|
| 01 | Catalog, the grid | light | 1280 |
| 02 | Catalog, the grid | dark | 1280 |
| 03 | Item panel open on a food item, *Photo* tab | light | 1280 |
| 04 | Item panel open on the same item, *Cut-out* tab | dark | 1280 |
| 05 | Pantry with the header | light | 375 |
| 06 | Inbox, the skipped-step import open | light | 1280 |
| 07 | Asset page, a food item (the file input in view) | dark | 1280 |

The panel opens by a click on a card through the same DevTools session; say how.

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-307_shots/INDEX.md`:**

- sha256 (12) and size; the on-screen text that proves the state.
- **Computed `background-color` of `body` and of the main content wrapper** (name the selector you read).
- **Computed `font-family` of the page heading, of one body text node, and of one button** (name each element).
- **Computed `background-color` and `color` of every visible `button`** (text, background), so the white-`--card` controls are measured, not guessed.
- **Smallest computed `font-size` among visible text nodes**, and every text node under 13 px quoted with its size.
- **Contrast ratio** (WCAG formula, computed in the script from the two computed colours) of the heading, a body node and one button against their effective background.
- **Computed `border-radius` of a catalog card, its thumbnail and one button** (01–04; expected `0px`), and **whether any visible text node's computed `font-family` contains `mono`** (all shots; expected none — list any).
- On 01–02: the count header text, every card's status word as rendered, one time stamp as rendered.
- On 03–04: the tab names as rendered and which is selected; the empty-state line; the *Kind of item* text; **none** of `Bounding-box`, `Version`, `If-Match`, `Isolated Cutout`, `AI stages` in the panel's `innerText`.
- On 05: the header's height and each child's `getBoundingClientRect().top` (expected one row: tops within 4 px); the tile buttons' computed `background-color` (expected the paper colour, not `rgb(255, 255, 255)`).
- On 06: the *Review status* select's computed `background-color` (expected paper).
- On 07: the file input's computed `background-color` and `color`.
- On 01–04, 06, 07 (1280): the computed `display` of the *Menu* button (expected `none`).
- On every shot: **none** of `optimistic concurrency`, `blueprint`, `Phase 0`, `AWAITING_REVIEW`, `consent_disabled`, `If-Match`, `Source Only`, `Bounding-box` in `document.body.innerText` (quote the check).
- **No two shots share a hash** — check it and quote the check.

A shot failing its proof is retaken once, then reported failed — **never described as showing what it does not. Every sentence saying a shot "shows" something names the DOM read that proves it.**

**Design notes, not fixes:** for each shot, two or three lines on anything that looks wrong to an owner who cares about design. **Check each of these by name, every shot:** clipping or crowding; mismatched surfaces (white on paper); text under 13 px; weak contrast; leftover developer wording; **date format** (an ISO date such as `2026-11-07` is a finding); **status words that say something untrue** (e.g. *In progress* for something waiting); category and heading names that contradict each other. Report it; change nothing.

Stop the servers by the PIDs in the `.pid` files, never `pkill -f`; **remove `output/SG-316-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18316/14316, both started in the background with the PID and the 200 quoted; the bundle check quoted; the skipped-step import made and how.
- **A3** — Seven shots with hash, size, proving text and every DOM read listed in G2; distinct-hash check quoted.
- **A4** — Design notes per shot.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a non-paper `body`, a system font or Arial on a button, an uppercase step name, a skipped step reading *Done*, an ISO date, *Menu* displayed at 1280, a removed string in `innerText`, two shots with one hash, a bundle pointing at 8003, a server call that did not return, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-316*`, `docs/worklogs/SG-307_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; the frontend build into scratch; the scratch servers on `127.0.0.1:18316` and `:14316`, in the background; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each (the call itself returns at once); one screenshot **60 s**; ordinary commands **120 s**. No interactive command, no foreground server.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, stop the servers, remove scratch, commit, write the report, publish.** **No optional goal.** Expected ≈750 s (`UNVERIFIED — my estimate`: SG-313 took 640 s for four shots; this is seven shots and a panel click). A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-316_report.md`. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the servers were started and the skipped step made; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-316`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-316 | Report: docs/worklogs/SG-316_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
