# SG-326 — Screenshots of polish A and B (SG-324, SG-325) on a scratch app, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — the gate is green (`docs/worklogs/SG-325_report.md`: frontend 72 files / 526 tests, host 817 + 2 deselected, image proof 2).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-326*` and `docs/worklogs/SG-326_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.** No deploy; a rider follows once these screens are seen.
**Provider: none.** No key, no `.env`, no spend; no network call to any provider.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner, 2026-11-16: *"Then … polish B on Muse …, shots, rider, then my shelf trial."* Stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."*

## Why this exists

Polish A (SG-324, gated by SG-324r1) and polish B (SG-325) changed what the owner sees on the asset page, catalog, capture form and review card. Before the rider puts them live, each screen is photographed and read from the DOM. Expected (`UNVERIFIED` — establish each from the code, `PB-1`):

- **Asset page:** *Edit* and *Clear expiry date* in the theme's control style (`AssetDetailPage.tsx:700`, `ExpiryEntryForm.tsx:158`); Details shows *Amount* as one row (*300 ml*), no *Shelf life* row repeating *Kind of item*.
- **Catalog:** a *Use by* column (`ProductGrid.tsx:45`) with each item's date or *No date*; no *Dimensions/Specs*; row button named *More actions for <name>*; cards show the same date (`ProductCard.tsx`).
- **Capture form:** heading *Add an item*, button *Add to catalog*, 13 px hint; the same-name warning's buttons in the theme's control style.
- **Review card, duplicate:** heading *Check this item*, *This may already be in your catalog*, no *Save edits*, *Accept* or *Hold*; plain field labels; the use-by field a date field.

**Binding from SG-321 / SG-321r1:** fill every input with the native value setter plus `input` and `change` events so React commits it; the catalog search must narrow (if it does not, report it and read the dates anyway).

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-326-scratch/docker-config output/SG-326-scratch/logs
export DOCKER_CONFIG="$PWD/output/SG-326-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-326/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-326-scratch"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-326/
docker version
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside `docs/worklogs` goes under `output/SG-326-scratch/`** — logs, the Node script, Chrome's `--user-data-dir`, npm's cache, every `tee`, `curl -o` and redirect. **Never `/tmp`, for anything.** `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app, servers in the background

A fresh SQLite under `output/SG-326-scratch/` by the project's migrations (`alembic upgrade head`). Data, made through the API:

- **Two live items named *Olive Oil*** with accepted use-by dates 6 May 2030 and 3 Feb 2031; **one live *Rice*** with no date; **one item with Amount 300 and Unit ml** and a kind of item set, used for the asset page shot; a few others so the catalog is not empty.
- **One import whose candidate is a duplicate of the first *Olive Oil*** (`duplicate_of_asset`), open for review, carrying a new date. Make it with **no provider spend** by a scratch-only Python script that runs the same steps as `backend/tests/test_sg304_duplicate_pack.py`'s `_setup` (`ScriptedPhase2Provider`) against the scratch database — SG-321r1's method (`docs/worklogs/SG-321r1_report.md`). Nothing in `backend/` is changed.

Backend started with `SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend`, so the root `.env` is not read. Never port 8003, the live container or the stored files.

Ports and the build, literally:

```
export SG326_API=http://127.0.0.1:18326
# frontend build into output/SG-326-scratch/build with VITE_API_BASE="$SG326_API", then:
grep -o '127\.0\.0\.1:18326' <built main js> | wc -l   # must be > 0
grep -o '8003' <built main js> | wc -l                 # must be 0, else STOP
```

**Start every server in the background, never in the foreground**, backend on `127.0.0.1:18326`, frontend on `127.0.0.1:14326`:

```
nohup <server command> > output/SG-326-scratch/logs/<name>.log 2>&1 &
echo $! > output/SG-326-scratch/<name>.pid
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' <url> | grep -q 200 && break; sleep 2; done
```

The call must return at once; a server not answering 200 within 60 s is reported with the last 20 lines of its log, and the slice stops at that point.

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install). Theme set the way SG-321r1 did. Into `docs/worklogs/SG-326_shots/`, in this order:

| Shot | Screen | Theme | Width |
|---|---|---|---|
| 01 | Asset page of the 300 ml item, Details and the expiry controls in view | light | 1280 |
| 02 | Catalog, table view, searched to *Olive Oil* — two rows, two dates | light | 1280 |
| 03 | Catalog, card view, unfiltered | dark | 390 |
| 04 | Add an item, name *olive oil* typed and saved → the same-name warning with two matches | dark | 1280 |
| 05 | Review page, the duplicate card | light | 1280 |
| 06 | Review page, the duplicate card | dark | 390 |

**No shot writes.** Saving on 04 only raises the warning; do not click *Add another pack*.

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-326_shots/INDEX.md`:**

- sha256 (12) and size; the on-screen text that proves the state.
- **Computed `background-color` of `body` and of the main content wrapper** (name the selector).
- **Computed `font-family` of the page heading, one body text node and one button** (name each).
- **Every visible button: its label, computed `background-color` and `color`, and its contrast ratio as a number** (WCAG formula, computed in the script on its effective background). **A shot with any button's ratio missing or written as "n/a" fails its proof.**
- **Smallest computed `font-size` among visible text nodes**, and every text node under 13 px quoted with its size.
- **Whether any visible text node's computed `font-family` contains `mono`** (expected none — list any).
- On 01: every Details row (label → value); whether *Shelf life* appears; the computed `background-color` of *Edit* and *Clear expiry date* against the page's.
- On 02 and 03: every *Olive Oil* row's or card's date text; the table's header labels in order (02); the row button's accessible name (02).
- On 04: the warning's full text, every date in it, every button's label.
- On 05 and 06: the card's full text; every visible button's label; **whether *Save edits*, *Accept* or *Hold* is visible** (expected none); every field label; the use-by input's `type` and `value`; **whether any id (UUID pattern) appears in `innerText`** (expected no).
- On 03 and 06: `document.documentElement.scrollWidth` vs `clientWidth` (expected equal) and whether any button wraps its label onto two lines.
- **Layout claims:** any statement that something wraps, crowds or clips quotes that element's `getBoundingClientRect()` (and its line height) **and** says what the image shows at that place. **A claim the image does not show is a defect** (SG-321 and SG-321r1 reported a header wrap the image did not show).
- On every shot: **none** of `[object Object]`, `duplicate_of_asset`, `display_name`, `expiry_date`, `Candidate`, `Photo only`, `Dimensions/Specs`, `Create asset`, `Untitled`, `Thumbnail unavailable`, `noname`, `AWAITING_REVIEW`, and **no ISO stamp** (regex `\d{4}-\d{2}-\d{2}`) in `document.body.innerText` (quote the check; list each hit). `ACTIVE` is a known leftover (SG-325 UNCLEAR): report each hit, do not fail on it.
- **No two shots share a hash** — check it and quote the check.

A shot failing its proof is retaken once, then reported failed — **never described as showing what it does not. Every sentence saying a shot "shows" something names the DOM read that proves it.**

**Design notes, not fixes:** for each shot, two or three lines on anything that looks wrong to an owner who cares about design. **Check each of these by name, every shot:** clipping or crowding; mismatched surfaces (white on paper); text under 13 px; weak contrast; leftover developer wording; date format; **whether two same-name items can be told apart at a glance** (02, 03); button sizes on the phone shots. **Open each PNG before writing its notes, and write each note from the image or a DOM read, naming which.** Report it; change nothing.

Stop the servers by the PIDs in the `.pid` files, never `pkill -f`; **remove `output/SG-326-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18326/14326, both started in the background with the PID and the 200 quoted; the bundle check quoted; how the duplicate candidate was made, and the evidence that no provider network call happened.
- **A3** — Six shots with hash, size, proving text and every DOM read listed in G2; distinct-hash check quoted.
- **A4** — Design notes per shot.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like two *Olive Oil* rows with one date or none, a *Status* or *Dimensions/Specs* header, *Save edits* on the duplicate card, a raw field key as a label, an ISO date in text, a grey or white button on paper, sideways scroll at 390, two shots with one hash, a bundle pointing at 8003, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-326*`, `docs/worklogs/SG-326_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; one scratch seeding script; the frontend build into scratch; the scratch servers on `127.0.0.1:18326` and `:14326`, in the background; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each (the call itself returns at once); one screenshot **60 s**; ordinary commands **120 s**. No interactive command, no foreground server.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, stop the servers, remove scratch, commit, write the report, publish.** **No optional goal.** Expected ≈900 s (`UNVERIFIED — my estimate`: SG-321r1 five shots ≈940 s by its stamps). A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-326_report.md`. The first line states the slice ID, model and effort read from the process arguments (if not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the servers were started and the duplicate made; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-326`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-326 | Report: docs/worklogs/SG-326_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
