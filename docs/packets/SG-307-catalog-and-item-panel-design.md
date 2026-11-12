# SG-307 — The catalog and the item panel in the tandpfun look, in plain words, and no white controls on paper

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write.
**Restart: none.** No deploy; a screenshot slice and a rider follow this slice.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that.**

**Approval:** owner D18 (*the tandpfun look's colours, font and shapes everywhere, the full design on the catalog, item panel and Pantry view*), D27; stage C (*"d14 ok"*, L3); the plan review SG-305/SG-306 moved the catalog and item panel here. The owner: *"design, look and feel are very important, so hold every screen to that."* **This slice builds and gates only; its screenshots are their own slice** (a full build slice lost its shots twice: SG-301, SG-312).

## Why this exists

The catalog and the item panel are the two screens the owner will use most, and the last ones still in the old look. Seen in screenshots (`docs/worklogs/SG-301_audit.md` I7, `docs/worklogs/SG-308_audit.md`, `docs/worklogs/SG-313_audit.md` I3–I4); locations are `UNVERIFIED` hypotheses — **establish each from the file before changing it**:

- **Catalog:** monospace time stamps (*"2m ago"*) and `item` chips (`frontend/src/components/catalog/ProductCard.tsx:208`, `ProductGrid.tsx:188`, `:223`, `font-mono`); a developer label *"Source Only"* (`ProductCard.tsx:41`); rounded thumbnails and a white toolbar (`frontend/src/routes/CatalogPage.tsx`).
- **Item panel** (`frontend/src/components/shell/ItemInspectorDrawer.tsx`): tab *"Isolated Cutout"* (`:16`); developer sentences *"Bounding-box overlay omitted: …"* (`:376`) and *"No isolated cutout exists yet. Cutouts arrive with the AI stages — nothing is being processed."* (`:345`); *"Kind of item: Uncategorized"* shown for a food item (`:390`); rounded fields and cut-out tabs.
- **White controls on paper** (SG-313, measured `rgb(255,255,255)` on `rgb(244,240,232)`): the Pantry tiles' *Edit* / *Use it up* / *−1*, the theme toggle, the Inbox *Review status* select; on the dark asset page the native file input is white.
- **The header at 375 px** wraps to two rows, 93 px tall (SG-313 shot 04): *Import Asset* drops under the logo.

## The look (D18; the tokens already exist in `frontend/src/theme/tokens.css`, light and `.dark`)

Ground `--paper`, text `--ink`, secondary `--ink-muted`, lines `--line`, accent `--primary` (dark-mode link text `--link`); **`border-radius: 0`**; joined square tabs; uppercase spaced labels (letter-spacing .04–.12em) with a count header such as *"23 ITEMS"*; grid `repeat(auto-fill, minmax(165px, 1fr))`; photos borderless on the paper; **no text under 13 px**; Instrument Sans everywhere, **no monospace in owner-facing text**. The Pantry (`frontend/src/routes/PantryPage.tsx`) is the finished reference — match it. Do not copy tandpfun code.

## G0 — Preflight

```
mkdir -p output/SG-307-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-307-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-307/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-307/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-307-scratch/` (npm's cache there too); **no `/tmp` for anything**; no `.vite/` or other untracked folder left in the tree (`git status --short` clean except `output/`, before the report). `output/` itself and `output/dispatch` are never touched. **No server is started in this slice.**

## G1 — Inventory first, then the catalog

**Inventory:** list every component the catalog and the item panel render, the test files that render them, and every owner-facing string in them that is developer wording, an enum, monospace or under 13 px. Quote it in the report. Commit.

Then the catalog: the look above on the page, the toolbar, the grid and the card; time stamps and chips in the body font and plain words (*"2 min ago"* is fine; an enum becomes a word through `frontend/src/lib/labels.ts`); *"Source Only"* and every other developer label become words an owner understands (say your words and why); a count header in the label style. Commit.

## G2 — The item panel

The look above: square fields, joined square tabs, paper ground, `--line` rules. Tab names and empty states in plain words — e.g. *Photo*, *Cut-out*, *In a scene*; an empty cut-out says, in one short line, that none exists yet, never how the system works; **the bounding-box sentence is removed from the screen** (keep any test hook as a `data-` attribute). *Kind of item* shows the item's real kind for a food item — **establish why it reads *Uncategorized* (which field it reads, `:390`); if the fix needs a backend change, report it and change nothing there.** Commit.

## G3 — No white controls on paper, and the 375 header

Buttons, selects and the native file input on a paper page use the paper or a transparent ground with a `--line` border (dark: the dark paper), **from one place in `tokens.css`** where possible — name the rule; the Pantry tiles' buttons, the theme toggle and the *Review status* select must come out of it. At 375 px the header fits **one row** (e.g. *Import Asset* shortened to an icon with an `aria-label`, or the theme toggle into the menu — your choice, say why). Commit.

**Do not change** behaviour, routes, API calls, data, Inbox, Expiry or the asset page beyond the shared control rule.

## G4 — Tests, FAIL-then-PASS, then the full gate

In `*.sg307.test.tsx`: no `font-mono` class and no developer string from your inventory in the rendered catalog and panel; the plain tab names and empty-state line; the count header; the control rule (a rendered button's ground is not `--card`/white); the 375 header rule (by class or media rule). Logs `docs/worklogs/SG-307_fail.log` and `SG-307_pass.log`, FAIL logs names and first assertion only. Older tests asserting replaced wording or styling are updated, each named.

The full gate as SG-312's G3 (`docs/packets/SG-312-sg301-design-follow-ups.md`), logs `docs/worklogs/SG-307_<step>.log`, exact counts; the SG-307 files and every changed older file twice.

## Acceptance criteria

- **A1** — Inventory quoted; G1–G3 each met, the report saying how and naming the file; the *Kind of item* cause stated either way.
- **A2** — G4 FAIL on base, PASS on candidate; updated older tests named.
- **A3** — Gate green with counts; files twice green.
- **A4** — Zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before the report.
- **A5** — Preflight; health 200 start and end; phase seconds from stamps.
- **A6** — `PB-3` vacuity: a failure would look like a `font-mono` class or a developer string still rendered, a rounded corner, a white button on paper, a two-row header at 375, a test that passes on base. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/src/routes/CatalogPage.tsx`; `frontend/src/components/catalog/*` (not `mockProducts.ts` unless a test needs it, named); `frontend/src/components/shell/ItemInspectorDrawer.tsx`; `frontend/src/theme/tokens.css`; `frontend/src/lib/labels.ts`; `frontend/src/App.tsx` and `frontend/src/components/shell/AppHeader.tsx` (the 375 header only); components the catalog and panel render, **for displayed text and styling only**. Any other product file is a STOP and report (`PG-EV-03`).
- **Tests:** new `*.sg307*` files; older tests only where they assert replaced wording or styling, each named.
- **No backend file.**
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the frontend build into scratch. No install, no server, no browser.
- Evidence: `docs/worklogs/SG-307*` only. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2, G3, G4; commit after each. Expected ≈1000 s (`UNVERIFIED — my estimate`: SG-312, three screens of CSS and copy plus the gate, reached the gate's end at ≈1100 s including a 600 s hang; SG-301 run 1 ≈933 s). A stop leaves the rest `REMAINING`; **the gate (G4) is never skipped to finish G3 — if time is short, leave G3 `REMAINING` and run G4.**

## Report

Destination: `docs/worklogs/SG-307_report.md`. The first line states the slice ID, model and effort **read from the process arguments** (`ps -o args= -p $PPID` or your equivalent; if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; the inventory; each premise confirmed or falsified with file and line; how each goal was met; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-307`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-307 | Report: docs/worklogs/SG-307_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
