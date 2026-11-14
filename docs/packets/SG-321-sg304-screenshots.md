# SG-321 — The screenshots SG-304 owes: the same-name warning and the duplicate-photo choices, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — SG-304's gate is green (`docs/worklogs/SG-304r2_report.md`: frontend 58 files / 493 tests, host 810 + 2 deselected, image proof 2, eslint only the known error).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-321*` and `docs/worklogs/SG-304_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.** No deploy; a rider follows once these screens are seen.
**Provider: none.** No key, no `.env`, no spend; no network call to any provider.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D33, D35; stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."*

## Why this exists

SG-304 (G1 `60ba8cd`, G2 `122a269`; tests SG-304r2) added two screens, expected (`UNVERIFIED` — establish each from the code, `PB-1`):

- **F9, manual capture:** saving an item whose name matches a live item shows a warning (`data-testid="same-name-warning"`, `frontend/src/components/AssetForm.tsx:305-338`) — one line with the existing item's date, or a list when there are two or more — with *Add another pack*, *Open it* and *Cancel*.
- **F10, review card:** a photo matching an existing item shows *This photo matches <name> (use by <date>).* (`CandidateCard.tsx:24`) with *It's another pack*, *It's the same pack*, *Decide later*; Accept and Hold hidden. **Known gap G-1:** *Save edits* still shows on that card (`CandidateCard.tsx:147-155`) — photograph it as it is; do not fix it.

**Its tests check the code; nothing has shown the screens.**

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-321-scratch/docker-config output/SG-321-scratch/logs
export DOCKER_CONFIG="$PWD/output/SG-321-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-321/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-321/
docker version
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside `docs/worklogs` goes under `output/SG-321-scratch/`** — logs into `output/SG-321-scratch/logs/`, the Node script, Chrome's `--user-data-dir`, npm's cache, every `tee`, `curl -o` and redirect. **Never `/tmp`, for anything** (SG-304r2 left a log in `/tmp`; this must not repeat). `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app, servers in the background

A fresh SQLite under `output/SG-321-scratch/` by the project's migrations (`alembic upgrade head`). Data:

- **Two live items named *Olive Oil*** with distinct expiry dates (e.g. 6 May 2030 and 3 Feb 2031), made through the API; **one live item named *Rice***; a few other items so the catalog is not empty.
- **One import whose candidate is a duplicate of the first *Olive Oil*** (`duplicate_of_asset`), still open for review, carrying a new date. Make it with **no provider spend**, by one of these, and say which and how: (a) the backend's own `fake` provider, **only if you establish from its code that it makes no network call**; or (b) a scratch-only Python script that runs the same steps as `backend/tests/test_sg304_duplicate_pack.py`'s `_setup` (`ScriptedPhase2Provider`) against the scratch database. Nothing in `backend/` is changed.

Backend started with `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend` (as SG-311 did), so the root `.env` is not read. Never port 8003, the live container or the stored files.

Ports and the build, literally:

```
export SG321_API=http://127.0.0.1:18321
# frontend build into output/SG-321-scratch/build with VITE_API_BASE="$SG321_API", then:
grep -o '127\.0\.0\.1:18321' <built main js> | wc -l   # must be > 0
grep -o '8003' <built main js> | wc -l                 # must be 0, else STOP
```

**Start every server in the background, never in the foreground.** The shape, for each of the backend (`127.0.0.1:18321`) and the frontend (`127.0.0.1:14321`):

```
nohup <server command> > output/SG-321-scratch/logs/<name>.log 2>&1 &
echo $! > output/SG-321-scratch/<name>.pid
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' <url> | grep -q 200 && break; sleep 2; done
```

The call must return at once; a server not answering 200 within 60 s is reported with the last 20 lines of its log, and the slice stops at that point.

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install). Theme set the way SG-311 did. Into `docs/worklogs/SG-304_shots/`, in this order:

| Shot | Screen | Theme | Width |
|---|---|---|---|
| 01 | Add item form, name *Rice* typed, saved → the warning with **one** match | light | 1280 |
| 02 | Add item form, name *olive oil* (lower case, trailing space) → the warning with **two** matches listed | dark | 1280 |
| 03 | Review page, the duplicate card | light | 1280 |
| 04 | Review page, the duplicate card | dark | 390 |
| 05 | After *It's another pack* is clicked on that card: the catalog showing three *Olive Oil* items, each with its own date | light | 1280 |

Each form and click is driven through the same DevTools session; say how. **Shot 05 is the only step that writes:** the click on *It's another pack*, once, on the scratch app.

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-304_shots/INDEX.md`:**

- sha256 (12) and size; the on-screen text that proves the state.
- **Computed `background-color` of `body` and of the main content wrapper** (name the selector).
- **Computed `font-family` of the page heading, of one body text node, and of one button** (name each element).
- **Computed `background-color` and `color` of every visible `button`.**
- **Smallest computed `font-size` among visible text nodes**, and every text node under 13 px quoted with its size.
- **Contrast ratio** (WCAG formula, computed in the script from the two computed colours) of the heading, a body node, every button in the warning or card, and the warning's own text against its effective background.
- **Whether any visible text node's computed `font-family` contains `mono`** (expected none — list any).
- On 01 and 02: the warning's full text as rendered, every date in it, and every button's label.
- On 03 and 04: the card's full text; every visible button's label; **whether *Accept* or *Hold* is visible** (expected neither); whether *Save edits* is visible (expected yes — gap G-1); **whether the existing item's id appears in `innerText`** (expected no).
- On 04: `document.documentElement.scrollWidth` vs `clientWidth` (expected equal — no sideways scroll) and whether any button wraps its label onto two lines.
- On 05: every *Olive Oil* card's date text; the asset count from `GET /v1/assets` before and after the click.
- On every shot: **none** of `[object Object]`, `duplicate_of_asset`, `duplicate_linked`, `as_new_pack`, `Exact duplicate of asset`, `Untitled asset`, `noname`, `AWAITING_REVIEW`, `If-Match`, and **no ISO stamp** (regex `\d{4}-\d{2}-\d{2}`) in `document.body.innerText` (quote the check; list each hit). `Thumbnail unavailable` is a known leftover (polish slice): report each hit, do not fail on it.
- **No two shots share a hash** — check it and quote the check.

A shot failing its proof is retaken once, then reported failed — **never described as showing what it does not. Every sentence saying a shot "shows" something names the DOM read that proves it.**

**Design notes, not fixes:** for each shot, two or three lines on anything that looks wrong to an owner who cares about design. **Check each of these by name, every shot:** clipping or crowding; mismatched surfaces (white on paper); text under 13 px; weak contrast; leftover developer wording; date format; **whether the three choices read as clearly different actions**; **whether the warning looks like a warning or like an error**; button sizes on the phone shot. Report it; change nothing.

Stop the servers by the PIDs in the `.pid` files, never `pkill -f`; **remove `output/SG-321-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18321/14321, both started in the background with the PID and the 200 quoted; the bundle check quoted; how the duplicate candidate was made, and the evidence that no provider network call happened.
- **A3** — Five shots with hash, size, proving text and every DOM read listed in G2; distinct-hash check quoted.
- **A4** — Design notes per shot.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like no warning on a name match, one match where two exist, a raw id on the card, *Accept* or *Hold* shown on a duplicate, an ISO date, sideways scroll at 390, an unchanged asset count after *It's another pack*, two shots with one hash, a bundle pointing at 8003, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-321*`, `docs/worklogs/SG-304_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; one scratch seeding script; the frontend build into scratch; the scratch servers on `127.0.0.1:18321` and `:14321`, in the background; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each (the call itself returns at once); one screenshot **60 s**; ordinary commands **120 s**. No interactive command, no foreground server.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, stop the servers, remove scratch, commit, write the report, publish.** **No optional goal.** Expected ≈700 s (`UNVERIFIED — my estimate`: SG-319 587 s for six shots). **Write each design-note sentence from the image or a DOM read, and name which** — a note not checked against its own shot is a defect. A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-321_report.md`. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the servers were started and the duplicate made; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-321`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-321 | Report: docs/worklogs/SG-321_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
