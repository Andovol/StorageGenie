# SG-333 — Screenshots of the catalog redesign (SG-330, SG-331, live as `release-sg332`) on a scratch app, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — the gate is green (`docs/worklogs/SG-331_report.md`).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-333*` and `docs/worklogs/SG-333_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.**
**Provider: none.** No key, no `.env`, no spend; no network call to any provider.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-17: *"First: SG-333 — screenshots of the redesigned catalog (light 1280, dark 1280, phone 390 at 3 and 4 per row), DOM proofs as SG-326"*. Stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."*

## Why this exists

The catalog redesign is live and has never been photographed. Expected (`UNVERIFIED` — establish each from the code, `PB-1`):

- Title *Your things*; button *Add item*; a plain text toolbar; default sort *Use by, soonest first*; grid is the default view.
- Photo-first cards: a square photo tile, the name, and a date line — *Past · <day month>* / *Past its date · <day month>* for a past date, a this-week wording for a date within 7 days (`ProductCard.tsx:59`), the date otherwise, *No date* when none.
- **One attention line** above the grid (`CatalogPage.tsx:72`, e.g. *1 item is past its date*, *2 run out this week*).
- A quiet *Gone* link.
- **Items per row** is a setting remembered per device: wide 4 / 5 / 6 (default 5), narrow (< 640 px) 3 / 4 (default 3), stored under `sg-per-row-wide` / `sg-per-row-narrow` (`CatalogPage.tsx:41–47`). Theme under `sg-theme` (`ThemeProvider.tsx:20`).
- Colours are D41 *Midnight*; font Instrument Sans; square corners.

**Binding from SG-321 / SG-321r1 / SG-326:** fill every input with the native value setter plus `input` and `change` events so React commits it.

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-333-scratch/docker-config output/SG-333-scratch/logs
export DOCKER_CONFIG="$PWD/output/SG-333-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-333/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-333-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-333-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-333/
docker version
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside `docs/worklogs` goes under `output/SG-333-scratch/`** — logs, the Node script, Chrome's `--user-data-dir`, npm's cache, every `tee`, `curl -o` and redirect. **Never `/tmp`, for anything.** `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app, servers in the background

A fresh SQLite under `output/SG-333-scratch/` by the project's migrations (`alembic upgrade head`). **Data, made through the API, dates computed from the run's own `date`** (not hard-coded), so the past and this-week wordings appear:

- **At least 12 live items**, enough to fill two rows at 6 per row.
- **At least 4 with a photo** — a small PNG made in scratch with no install (any method; say which). Give an item its photo by whatever path the app has that needs no provider; if the only path runs through an import, use the scratch-only scripted-provider method of SG-326 (`docs/worklogs/SG-326_report.md`: same steps as `backend/tests/test_sg304_duplicate_pack.py`'s `_setup`, `ScriptedPhase2Provider`). Nothing in `backend/` is changed. **The rest have no photo** — the shots must show both kinds of tile.
- **One item past its date** (yesterday or earlier), **two within this week** (in 2 and 5 days), **one with no date**, the rest later dates.
- **Two live items named *Olive Oil*** with different dates (how two same-name packs look today, before grouping is built).
- **One item marked *Gone*** (archived), so the *Gone* link has something behind it.

Backend started with `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend`, so the root `.env` is not read. Never port 8003, the live container or the stored files.

Ports and the build, literally:

```
export SG333_API=http://127.0.0.1:18333
# frontend build into output/SG-333-scratch/build with VITE_API_BASE="$SG333_API", then:
grep -o '127\.0\.0\.1:18333' <built main js> | wc -l   # must be > 0
grep -o '8003' <built main js> | wc -l                 # must be 0, else STOP
```

**Start every server in the background, never in the foreground**, backend on `127.0.0.1:18333`, frontend on `127.0.0.1:14333`:

```
nohup <server command> > output/SG-333-scratch/logs/<name>.log 2>&1 &
echo $! > output/SG-333-scratch/<name>.pid
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' <url> | grep -q 200 && break; sleep 2; done
```

The call must return at once; a server not answering 200 within 60 s is reported with the last 20 lines of its log, and the slice stops at that point.

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install). Theme set the way SG-326 did. **Items per row is set through the page's own visible control** (the toolbar setting), then the `sg-per-row-*` value is read back from `localStorage` and quoted; if the control cannot be found or used, set the key, reload, and say so. Full-page screenshots (capture beyond the viewport so the whole grid is in the image). Into `docs/worklogs/SG-333_shots/`, in this order:

| Shot | Screen | Theme | Width | Items per row |
|---|---|---|---|---|
| 01 | Catalog, default view, unfiltered | light | 1280 | 5 (default) |
| 02 | Catalog, default view, unfiltered | dark | 1280 | 5 (default) |
| 03 | Catalog, default view | light | 390 | 3 (default) |
| 04 | Catalog, default view | light | 390 | 4 |
| 05 | Catalog, default view | dark | 390 | 3 |
| 06 | Catalog, default view | dark | 390 | 4 |

**No shot writes data.** Changing items per row is a device setting, not a write.

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-333_shots/INDEX.md`:**

- sha256 (12) and size; the on-screen text that proves the state (title, attention line, sort label).
- **Computed `background-color` of `body` and of the main content wrapper** (name the selector).
- **Computed `font-family` of the page heading, one card name and one button** (name each).
- **Every visible button and link: its label, computed `background-color` and `color`, and its contrast ratio as a number** (WCAG formula, computed in the script on its effective background). **A shot with any ratio missing or written as "n/a" fails its proof.**
- **Every card's date-line text, its computed `color`, and its contrast ratio on the card's effective background** — the past and this-week lines by name.
- **Smallest computed `font-size` among visible text nodes**, and every text node under 13 px quoted with its size.
- **Whether any visible text node's computed `font-family` contains `mono`** (expected none — list any).
- **Grid:** the grid element's computed `grid-template-columns` and its track count, and the number of cards whose `getBoundingClientRect().top` equals the first card's — both must equal the shot's items per row. The `localStorage` value of `sg-per-row-wide` / `sg-per-row-narrow` read back.
- **Corners:** computed `border-radius` of one card, its photo tile and one button (expected `0px`; quote).
- **Tiles:** for each photo card, the `<img>`'s `naturalWidth` > 0 (loaded, not broken); for each no-photo card, what the tile shows instead (text or element).
- **The two *Olive Oil* cards:** each one's date text, and whether they can be told apart at a glance.
- On 03–06: `document.documentElement.scrollWidth` vs `clientWidth` (expected equal); every card name that is truncated or wraps (quote its rect and line height); whether any toolbar control wraps onto two lines.
- **Layout claims:** any statement that something wraps, crowds or clips quotes that element's `getBoundingClientRect()` (and its line height) **and** says what the image shows at that place. **A claim the image does not show is a defect.**
- On every shot: **none** of `[object Object]`, `display_name`, `expiry_date`, `Candidate`, `Photo only`, `Dimensions/Specs`, `Create asset`, `Import Asset`, `Untitled`, `Thumbnail unavailable`, `noname`, `AWAITING_REVIEW`, `ACTIVE`, `ARCHIVED`, and **no ISO stamp** (regex `\d{4}-\d{2}-\d{2}`) in `document.body.innerText` (quote the check; list each hit).
- **No two shots share a hash** — check it and quote the check.

A shot failing its proof is retaken once, then reported failed — **never described as showing what it does not. Every sentence saying a shot "shows" something names the DOM read that proves it.**

**Design notes, not fixes:** for each shot, two or three lines on anything that looks wrong to an owner who cares about design. **Check each of these by name, every shot:** clipping or crowding; mismatched surfaces; text under 13 px; weak contrast (dark theme especially); leftover developer wording; date wording; how a no-photo tile looks beside a photo tile; whether the two *Olive Oil* cards can be told apart; card and button sizes on the phone shots (3 vs 4 per row — is 4 too tight to read?). **Open each PNG before writing its notes, and write each note from the image or a DOM read, naming which.** Report it; change nothing.

Stop the servers by the PIDs in the `.pid` files, never `pkill -f`; **remove `output/SG-333-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18333/14333, both started in the background with the PID and the 200 quoted; the bundle check quoted; how photos were given and the evidence that no provider network call happened; the dates used and the run date they were computed from.
- **A3** — Six shots with hash, size, proving text and every DOM read listed in G2; per-row track count equal to the table on every shot; distinct-hash check quoted.
- **A4** — Design notes per shot.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a track count different from the table, a broken photo (`naturalWidth` 0), no attention line with a past item present, a rounded corner, an ISO date in text, a raw status word, a button or date line under 4.5:1, sideways scroll at 390, two shots with one hash, a bundle pointing at 8003, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-333*`, `docs/worklogs/SG-333_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; one scratch seeding script; the frontend build into scratch; the scratch servers on `127.0.0.1:18333` and `:14333`, in the background; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each (the call itself returns at once); one screenshot **60 s**; ordinary commands **120 s**. No interactive command, no foreground server.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, stop the servers, remove scratch, commit, write the report, publish.** **No optional goal.** Expected ≈700 s (`UNVERIFIED — my estimate`: SG-313 shots 640 s engine elapsed). A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-333_report.md`. The first line states the slice ID, model and effort read from the process arguments (if not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the servers were started and the photos given; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-333`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-333 | Report: docs/worklogs/SG-333_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
