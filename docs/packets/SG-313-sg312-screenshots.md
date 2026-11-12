# SG-313 — The screenshots SG-312 owes: paper ground, the font in controls, Inbox step names, Menu hidden on desktop, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — SG-312's gate is green (`docs/worklogs/SG-312_report.md`: frontend 50 files / 450 tests, host 805 + 2 deselected, image proof 2, eslint 0 errors).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-313*` and `docs/worklogs/SG-312_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.** No deploy; a rider follows once SG-312 is rated.
**Provider: none.** No key, no `.env`, no spend; every provider off.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that.**

**Approval:** stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."* SG-312 built the change and passed its gate, but a server started in the foreground hung its run before any screenshot; the screenshots are their own slice.

## Why this exists

SG-312 (`80011d0..58ba0ef`) changed every screen (expected, `UNVERIFIED` — establish each from the file before relying on it): **`body` on `--paper`** from one place (`frontend/src/theme/tokens.css`, `frontend/src/App.tsx`); **a control-font rule** so buttons and inputs use Instrument Sans (`tokens.css`); **Inbox step names** in `frontend/src/lib/labels.ts` (*Checking the file*, *Tidying the details*, *Looking for duplicates*, *Your review*, *Saving*) and the job date as e.g. *5 Mar, 14:42* (`frontend/src/routes/InboxPage.tsx`, `frontend/src/components/JobCard.tsx`); **Menu** given the `nav-menu-toggle` class, hidden at ≥ 768 px; asset page and Expiry tier wording through the label map. **Its tests check the source; nothing has shown the screens.** SG-312's report also leaves these open, which the shots must settle: the header at 375 px fits on one row or not; buttons still on the white `--card` token (asset page *Edit* and *Remove*, the Expiry form's *Clear*, the Pantry tiles' controls); the Expiry tier names *Upcoming*, *Long lead*, *Safe*.

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-313-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-313-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-313/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-313/
docker version
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-313-scratch/`, npm's cache there too if needed; **no `/tmp` for anything, including `tee`, `curl -o` and Chrome's profile.** `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app, servers in the background

As SG-311 did (`docs/worklogs/SG-311_report.md` § *How the skipped AI step was made*): a fresh SQLite under `output/SG-313-scratch/` by the project's migrations (`alembic upgrade head`); test data **through the API** with generated images — food and non-food, one item with no name, one expired food item, a few due soon, one counted and one amount item, items in each Expiry tier, and **one Inbox import whose AI step is skipped** (backend started with `SG_CONSENT=false SG_PROVIDER_ID=fake OPENCODE_API_KEY= JINA_API_KEY= OPENROUTER_API_KEY=` and `cwd=backend`; then `POST /v1/evidence`, `POST /v1/imports`, `POST /v1/imports/{id}/run`). Never port 8003, the live container or the stored files.

Ports and the build, literally:

```
export SG313_API=http://127.0.0.1:18313
# frontend build into scratch with VITE_API_BASE="$SG313_API", then:
grep -o '127\.0\.0\.1:18313' <built main js> | wc -l   # must be > 0
grep -o '8003' <built main js> | wc -l                 # must be 0, else STOP
```

**Start every server in the background, never in the foreground.** The shape, for each of the backend (`127.0.0.1:18313`) and the frontend (`127.0.0.1:14313`):

```
nohup <server command> > output/SG-313-scratch/<name>.log 2>&1 &
echo $! > output/SG-313-scratch/<name>.pid
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code}' <url> | grep -q 200 && break; sleep 2; done
```

The call must return at once; a server not answering 200 within 60 s is reported with the last 20 lines of its log, and the slice stops at that point. **SG-312 lost its screenshots to a foreground start that held the call for 600 s — this is the one thing this slice must not repeat.**

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install; Chrome's `--user-data-dir` under scratch). Theme set the way SG-311 did. Into `docs/worklogs/SG-312_shots/`, in this order:

| Shot | Screen | Theme | Width |
|---|---|---|---|
| 01 | Inbox, the skipped-step import open | light | 1280 |
| 02 | Expiry page, every tier with an item | light | 1280 |
| 03 | Asset page, a food item with a date | dark | 1280 |
| 04 | Pantry with the header | light | 375 |

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-312_shots/INDEX.md`:**

- sha256 (12) and size; the on-screen text that proves the state.
- **Computed `background-color` of `body` and of the main content wrapper** (name the selector you read).
- **Computed `font-family` of the page heading, of one body text node, and of one button** (name each element).
- **Computed `background-color` and `color` of every visible `button`** (text, background), so the white-`--card` controls are measured, not guessed.
- **Smallest computed `font-size` among visible text nodes**, and every text node under 13 px quoted with its size.
- **Contrast ratio** (WCAG formula, computed in the script from the two computed colours) of the heading, a body node and one button against their effective background.
- On 01: every step label as rendered (expected the plain names; the skipped step reads *Skipped (AI off)*, never *Done*) and the job date as rendered.
- On 01–03 (1280): the computed `display` of the *Menu* button (expected `none`).
- On 02: the tier names as rendered.
- On 04: the header's height in px and whether its children sit on one row (compare each child's `getBoundingClientRect().top`; quote the numbers).
- On 01–03: **none** of `optimistic concurrency`, `blueprint`, `Phase 0`, `AWAITING_REVIEW`, `consent_disabled`, `If-Match`, `evidence state`, `per-press` or an `Import <hex>` fragment in `document.body.innerText` (quote the check).
- **No two shots share a hash** — check it and quote the check.

A shot failing its proof is retaken once, then reported failed — **never described as showing what it does not. Every sentence saying a shot "shows" something names the DOM read that proves it.**

**Design notes, not fixes:** for each shot, two or three lines on anything that looks wrong to an owner who cares about design — clipping, crowding, mismatched surfaces (white controls on paper), text under 13 px, weak contrast, leftover developer wording. Report it; change nothing.

Stop the servers by the PIDs in the `.pid` files, never `pkill -f`; **remove `output/SG-313-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18313/14313, both started in the background with the PID and the 200 quoted; the bundle check quoted; the skipped-step import made and how.
- **A3** — Four shots with hash, size, proving text and every DOM read listed in G2; distinct-hash check quoted.
- **A4** — Design notes per shot.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a non-paper `body`, a system font or Arial on a button, an uppercase step name, a skipped step reading *Done*, an ISO date, *Menu* displayed at 1280, a removed string in `innerText`, two shots with one hash, a bundle pointing at 8003, a server call that did not return, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-313*`, `docs/worklogs/SG-312_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; the frontend build into scratch; the scratch servers on `127.0.0.1:18313` and `:14313`, in the background; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each (the call itself returns at once); one screenshot **60 s**; ordinary commands **120 s**. No interactive command, no foreground server.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, stop the servers, remove scratch, commit, write the report, publish.** **No optional goal.** Expected ≈450 s (`UNVERIFIED — my estimate`: SG-311 took 884 s of which ≈550 s were two hung server calls; four shots with more DOM reads). A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-313_report.md`. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the servers were started and the skipped step made; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-313`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-313 | Report: docs/worklogs/SG-313_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
