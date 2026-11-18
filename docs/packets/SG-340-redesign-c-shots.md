# SG-340 — Screenshots of redesign C (item page SG-336/338/339, grouped cards SG-337) on a scratch app, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — the gate is green (`docs/worklogs/SG-337_report.md`: frontend 573, host 817).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-340*` and `docs/worklogs/SG-340_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.**
**Provider: none.** No key, no `.env`, no spend; no network call to any provider.

**Contract:** recorded `0.63.0` (`AGENTS.md`, D42). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-17: *"Then: redesign C — item page as in the mockup (one row per pack, Used up, Add another pack) and same-name packs grouped as one card"*. Stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."*

## Why this exists

Redesign C is gated but never seen. Expected (`UNVERIFIED` — establish each from the code, `PB-1`):

- **Catalog grid:** one card per same-name group with a muted *<N> packs* line (N ≥ 2), the soonest pack's date and photo (`ProductCard.tsx`, `components/catalog/groupPacks.ts`); the title count still counts packs; the grid and attention line share the title's left edge (`AppShell.tsx`, SG-337 G5); a date chip never extends past its card (G4).
- **Item page** (`routes/AssetDetailPage.tsx`): *‹ Your things*; large square photo left (stacked on the phone); 44 px name; muted *<Kind> · <Where> · <N> packs*; one row per live pack (bold date line, muted amount and *added <d Mon>*, *Edit* and *Used up*); *Add another pack* as the one dark primary button; a short definition list; folded *History (<n> changes)*; folded *More about this item*. *Used up* shows *<name> used up · Undo*.

**Binding from SG-321 / SG-326 / SG-333:** fill every input with the native value setter plus `input` and `change` events so React commits it; set the theme and items per row the way SG-333 did (`docs/worklogs/SG-333_report.md`).

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-340-scratch/docker-config output/SG-340-scratch/logs
export DOCKER_CONFIG="$PWD/output/SG-340-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-340/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-340-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-340-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-340/
docker version
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside `docs/worklogs` goes under `output/SG-340-scratch/`** — logs, the seed script, the Node script, Chrome's `--user-data-dir`, npm's cache, every `tee`, `curl -o`, redirect and probe. **Never `/tmp`, for anything.** `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app, servers in the background

A fresh SQLite under `output/SG-340-scratch/` by the project's migrations (`alembic upgrade head`). **Data made through the API exactly as SG-333 did** (`SG-333_report.md` §How: evidence upload of small PNGs made with the backend venv's Pillow, classification, expiry, gone — no import path), **dates computed from the run's own `date`**:

- ***Olive Oil* × 3 packs:** past (yesterday), this week (in 5 days), later (in 6 months); the this-week pack has a photo, the other two none; all three with the same kind of item and the same place (if places are dormant, say so); one with Amount 1 l.
- ***Milk* × 2 packs** (in 2 days with a photo; no date).
- At least 8 single items, some with photos, one with no date, so two rows fill at 5 per row.
- One item marked *Gone*.

**Make the photos look less like test squares than SG-333's:** 256 × 256 PNGs, each a soft two-tone or simple drawn shape (a bottle outline, a box) on a light ground — any no-install method, say which. They remain stand-ins; say so.

Backend started with `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend`, so the root `.env` is not read. Never port 8003, the live container or the stored files.

Ports and the build, literally:

```
export SG340_API=http://127.0.0.1:18340
# frontend build into output/SG-340-scratch/build with VITE_API_BASE="$SG340_API", then:
grep -o '127\.0\.0\.1:18340' <built main js> | wc -l   # must be > 0
grep -o '8003' <built main js> | wc -l                 # must be 0, else STOP
```

**Start every server in the background, never in the foreground**, backend on `127.0.0.1:18340`, frontend on `127.0.0.1:14340`:

```
nohup <server command> > output/SG-340-scratch/logs/<name>.log 2>&1 &
echo $! > output/SG-340-scratch/<name>.pid
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' <url> | grep -q 200 && break; sleep 2; done
```

**Immediately before the first shot, probe both servers again for 200** (SG-333 lost ≈340 s to a preview server that had exited); a server not answering is restarted once the same way, and the restart is stated.

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install). Full-page screenshots. Into `docs/worklogs/SG-340_shots/`, in this order:

| Shot | Screen | Theme | Width | State |
|---|---|---|---|---|
| 01 | Catalog grid | light | 1280 | default (5 per row) |
| 02 | Catalog grid | dark | 390 | 4 per row (visible control) |
| 03 | Catalog grid | light | 1920 | default — how full-bleed looks on a wide screen |
| 04 | Item page of the past *Olive Oil* pack | light | 1280 | as loaded |
| 05 | Same | dark | 1280 | as loaded |
| 06 | Same | light | 390 | as loaded |
| 07 | Same | light | 390 | the this-week row's *Edit* open |
| 08 | Same | light | 1280 | after *Used up* on the later pack — the notice with *Undo* in view |
| 09 | Same | light | 1280 | *History* and *More about this item* both opened |

**08 is the one write**, and only to the scratch database. After 08, click *Undo* and read back that the pack is live again (quote the API read).

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-340_shots/INDEX.md`:**

- sha256 (12) and size; the on-screen text that proves the state.
- **Computed `background-color` of `body` and of the main content wrapper** (name the selector).
- **Computed `font-family` of the page heading, one body text node and one button** (name each).
- **Every visible button and link: label, computed `background-color` and `color`, and contrast ratio as a number** (WCAG, on its effective background). Missing or "n/a" fails the shot.
- **Every visible date line: text, colour, ratio.**
- **Smallest computed `font-size` among visible text nodes**, and every text node under 13 px quoted with its size. **Whether any visible text node's `font-family` contains `mono`** (expected none).
- **Corners:** `border-radius` of one card or tile, one button (expected `0px`).
- **Every visible button's height** (expected ≥ 44 px on 06 and 07).
- On 01–03: every card's name, date line and *packs* line; the number of *Olive Oil* cards (expected 1) and *Milk* cards (expected 1); the title count text; the x of the title, the attention line and the first card (expected equal); grid tracks equal the per-row value; **each date chip's right edge ≤ its card's right edge** (quote both).
- On 04–09: the heading; the muted line; **every pack row's date line and muted line, in order**; the photo tile's `img` `naturalWidth` (or what shows instead); every definition-list row; whether *History* and *More about this item* are folded (04–08) or open (09) — on 09 list every section heading inside *More*.
- On 08: the notice's full text; the number of pack rows before and after; the Undo read-back.
- On 02, 06, 07: `scrollWidth` vs `clientWidth` (expected equal).
- **Layout claims:** any statement that something wraps, crowds or clips quotes that element's `getBoundingClientRect()` **and** says what the image shows there. **A claim the image does not show is a defect.**
- On every shot: **none** of `[object Object]`, `display_name`, `expiry_date`, `Candidate`, `Untitled`, `noname`, `AWAITING_REVIEW`, `ACTIVE`, `ARCHIVED`, `unknown`, `Import Asset`, and **no ISO stamp** (`\d{4}-\d{2}-\d{2}`) in `document.body.innerText` (quote the check; list each hit).
- **No two shots share a hash** — check it and quote the check.

A shot failing its proof is retaken once, then reported failed — **never described as showing what it does not.**

**Design notes, not fixes:** for each shot, two or three lines for an owner who cares about design. **Check each by name, every shot:** clipping, crowding or overflow (a chip or label crossing its box); mismatched surfaces; text under 13 px; weak contrast; developer wording; date wording; how the item page compares with the mockup's layout described above; on 03, whether the 1920 grid looks too large or too sparse. **Open each PNG before writing its notes, then re-read each note against the image: every defect visible in the image is named** (SG-333 missed an overflowing chip and an inset grid that were plain in its own images — do not repeat it). Report it; change nothing.

Stop the servers by the PIDs in the `.pid` files, never `pkill -f`; **remove `output/SG-340-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18340/14340, background starts with PID and 200 quoted, the pre-shot re-probe quoted; bundle check quoted; photos made and given, with evidence of no provider call; dates and the run date.
- **A3** — Nine shots with hash, size, proving text and every DOM read listed in G2; distinct-hash check quoted; 08's Undo read-back quoted.
- **A4** — Design notes per shot, each defect visible in the image named.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like two *Olive Oil* cards, a chip past its card, a first card left of or right of the title, rows in the wrong order, a *Used up* that removed two rows, an Undo that did not restore, a button under 44 px on the phone, an ISO date, `unknown` in text, sideways scroll, two shots with one hash, a bundle pointing at 8003, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-340*`, `docs/worklogs/SG-340_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; one scratch seeding script; the frontend build into scratch; the scratch servers on `127.0.0.1:18340` and `:14340`, in the background; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each (the call itself returns at once); one screenshot **60 s**; ordinary commands **120 s**. No interactive command, no foreground server.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, stop the servers, remove scratch, commit, write the report, publish — whatever is left.** **No optional goal.** Expected ≈900 s (`UNVERIFIED — my estimate`: SG-333, six shots, ≈970 s with one lost run; nine shots here). A stop leaves the rest `REMAINING`, named per shot.

## Report

Destination: `docs/worklogs/SG-340_report.md`. The first line states the slice ID, model and effort read from the process arguments (if not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the servers were started and the photos made; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-340`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-340 | Report: docs/worklogs/SG-340_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
