# SG-312 — SG-301's design follow-ups: paper ground on every page, the font in buttons, the Inbox and asset page in plain words

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases, plus throwaway SQLite files under scratch for the screenshot app. No live database read or write.
**Restart: none.** No deploy; a rider follows this slice.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that.**

**Approval:** owner D18 (the tandpfun look's colours, font and shapes everywhere), D27; stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that."* Findings I1–I6 of `docs/worklogs/SG-301_audit.md`, seen in `docs/worklogs/SG-301_shots/` (SG-311).

## Why this exists

SG-301 (live by rider SG-310) brought Instrument Sans, the paper header and plain words, but its screenshots show (`UNVERIFIED` locations — establish each):

- **I1 — the page ground is not paper** except on the Pantry. `body` paints `hsl(var(--background))` (`frontend/src/theme/tokens.css` ~`:88-95`); the Pantry sets `--paper` on its own wrapper (`frontend/src/routes/PantryPage.tsx` ~`:327`). Inbox, Expiry and the asset page show near-black (dark) or near-white (light). The asset page's *Manual expiry entry* card is white on the page.
- **I2 — buttons, selects and the file control render in Arial** (SG-311 read `Arial` from the DOM on *Edit*, *Use it up*, *Choose Files*): form controls do not inherit `font-family` by default.
- **I3 — Inbox:** step names in uppercase internal words (*EXTRACTING DETERMINISTIC SIGNALS*, *COMMITTING*, `labelStepName` in `frontend/src/lib/labels.ts`); the job card's raw timestamp (`frontend/src/components/JobCard.tsx` ~`:53`, `job.created_at`); review rows reading *"item"* with no name.
- **I4 — the *Menu* button shows at desktop width** beside the full navigation (`frontend/src/App.tsx` ~`:94-107`); at 375 px the header wraps to two rows.
- **I5 — asset page wording:** *"Expiry evidence state: accepted"*, *"per-press cap $0.05"*, *"Live · qty 500 ml"* (`frontend/src/routes/AssetDetailPage.tsx`).
- **I6 — Expiry tier pills** *No tier* / *Critical* / *Urgent* (`frontend/src/routes/ExpiryPage.tsx`).

## G0 — Preflight

```
mkdir -p output/SG-312-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-312-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-312/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-312/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). `PATH=$PWD/backend/venv/bin:$PATH` for make and `ruff`. Health at start and end, both 200. **`date +%s` at the start of every step.** Scratch only in `output/SG-312-scratch/` (npm's cache there too); **no `/tmp` for anything**; no `.vite/` or other untracked folder left in the tree at the end (`git status --short` clean except `output/`, before the report). `output/` itself and `output/dispatch` are never touched.

## G1 — The fixes

1. **Paper everywhere:** the page ground on every route is `--paper` (light and dark), from one place — the simplest is the `body`/app-shell background, after which the Pantry's own wrapper colour is redundant. Cards and panels on a page use the paper or a `--line` border, never white.
2. **One font in controls:** `button, input, select, textarea { font: inherit; }` or your equivalent, once, in `tokens.css`.
3. **Inbox:** step names through the label map as plain sentence-case words an owner understands (*Checking the file*, *Reading the photo*, *Asking the AI*, *Making items*, *Looking for duplicates*, *Your review*, *Saving* — your better words, say why); the job card's date as *"12 Nov, 14:42"* (or *"Today, 14:42"*), never ISO; review rows show the item's **name** when the task's data carries it or one existing read gives it — **establish which; if a name needs a backend change, report it and keep *"Unnamed item"*, no backend byte.**
4. **Menu** only below the width where the full navigation is hidden; prove the breakpoint at 1280 and 375. At 375 the header is one row if it fits; if not, say why.
5. **Asset page:** *"Expiry evidence state: accepted"* → *"Date confirmed"* (and its other states in plain words through the label map); *"Last measured spend … per-press cap …"* → one plain line, for example *"Enrich costs up to $0.05 a press"*; *"Live · qty 500 ml"* → *"500 ml left"* with the shared quantity formatter (`frontend/src/lib/quantityText.ts`).
6. **Expiry tiers:** plain words (*Use first*, *Use soon*, nothing for *No tier*), in the label style beside the date, not pinned to the far edge.

**Do not change** behaviour, routes, API calls, data, the catalog body or the item panel (SG-307), or the Pantry beyond removing a now-redundant background.

## G2 — Tests, FAIL-then-PASS

In `*.sg312.test.tsx`: the body's ground token is `--paper`; controls inherit the font (a rule exists and a rendered button's style resolves to it); each new step label and the date format; the tier words; the asset page's new lines; the Menu button hidden at desktop width (by class or media rule). Logs `docs/worklogs/SG-312_fail.log`, `SG-312_pass.log`, FAIL logs names and first assertion only. Older tests asserting replaced wording are updated, each named.

## G3 — The full gate

As SG-301r1's R2 (`docs/packets/SG-301r1-finish-tests-gate-shots.md`), logs `docs/worklogs/SG-312_<step>.log`, exact counts; the SG-312 files and every changed older file twice.

## G4 — Screenshots, after the gate

As SG-311 did (`docs/packets/SG-311-sg301-screenshots.md` G1–G2): backend `127.0.0.1:18312`, frontend `127.0.0.1:14312` **built with `VITE_API_BASE=http://127.0.0.1:18312`**. Into `docs/worklogs/SG-312_shots/`:

| Shot | Theme | Width |
|---|---|---|
| Inbox, the skipped-step import open | light | 1280 |
| Expiry page | light | 1280 |
| Asset page | dark | 1280 |
| Pantry with the header | light | 375 |

**Proof per shot, from the DOM, in `INDEX.md`:** sha256 (12), size, proving text; **the computed background colour of `body` and of the main content wrapper; the computed `font-family` of a heading, a body node and a button**; on Inbox the step labels and the job date as rendered; on 1280 shots whether *Menu* is displayed. Distinct-hash check. **One line of design notes per shot.** Stop servers by PID; **remove `output/SG-312-scratch/` before the report.**

## Acceptance criteria

- **A1** — G1.1–G1.6 each met, the report saying how and naming the file; I3's item-name finding stated either way.
- **A2** — G2 FAIL on base, PASS on candidate; updated older tests named.
- **A3** — Gate green with counts; files twice green.
- **A4** — Four shots with every DOM proof; distinct hashes; design notes.
- **A5** — Zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/` and scratch removed before the report.
- **A6** — Preflight; health 200 start and end; phase seconds.
- **A7** — `PB-3` vacuity: a failure would look like a non-paper body, Arial on a button, an uppercase step name, an ISO date, *Menu* at 1280, *"evidence state"* or *"per-press"* on screen, two shots with one hash, a bundle pointing at 8003. Say which you checked.
- **A8** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/src/theme/tokens.css`; `frontend/src/App.tsx`; `frontend/src/lib/labels.ts`; `frontend/src/components/JobCard.tsx`; `frontend/src/routes/{InboxPage,ExpiryPage,AssetDetailPage,PantryPage}.tsx` (Pantry: the redundant background only); components those three screens render, **for displayed text and styling only**. **Not** `CatalogPage.tsx`, `components/catalog/*`, `ItemInspectorDrawer.tsx` (SG-307). Any other product file is a STOP and report (`PG-EV-03`).
- **Tests:** new `*.sg312*` files; older tests only where they assert replaced wording or styling, each named.
- **No backend file.**
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the frontend build, scratch servers on `127.0.0.1:18312` and `:14312`, the project's migrations on scratch files, headless Chrome, a Node DevTools script in scratch. No install.
- Evidence: `docs/worklogs/SG-312*` only. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; scratch server start **60 s** each; one screenshot **60 s**; ordinary commands **120 s**.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2, G3, G4; commit after each. Expected ≈1050 s (`UNVERIFIED — my estimate`: copy and CSS over three screens ≈250 s, tests ≈150 s, gate ≈300 s, scratch app and 4 shots ≈400 s). A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-312_report.md`. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each premise confirmed or falsified with file and line; how each G1 line was met; test changes named; gate counts; the shot table with proofs and notes; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-312`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-312 | Report: docs/worklogs/SG-312_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
