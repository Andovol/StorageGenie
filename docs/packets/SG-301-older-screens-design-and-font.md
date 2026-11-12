# SG-301 — Older screens to the owner's design bar: Instrument Sans, no developer copy, the tandpfun look on catalog and item panel

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases, plus throwaway SQLite files under scratch for the screenshot app. No live database read or write.
**Restart: none.** No deploy; a rider follows this slice.
**Provider: none.** No key, no `.env`, no spend; the screenshot app runs with every provider off.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line as you received it. A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-10, D27 (*"Both approved."*): SG-301 is the design pass on the older screens plus the Instrument Sans font. Owner, 2026-11-12, D31 (*"D30 and D31 approved"*): the font is served self-hosted from the `@fontsource-variable/instrument-sans` package at an exact pinned version, **and this slice is authorised to run that one `npm install`**. D18: the tandpfun look's colours, font and shapes everywhere, the full design on the catalog and the item panel. Stage C (*"d14 ok"*, L3). The owner: *"design, look and feel are very important, so hold every screen to that."*

## Why this exists

The Pantry (SG-273, SG-300, SG-302) now meets the owner's bar; the screens around it do not. From the audits (`docs/worklogs/SG-300_audit.md` I2, `SG-269_findings.md`) and a grep on `automation` (`UNVERIFIED` until you confirm each):

- **Item panel** `frontend/src/components/shell/ItemInspectorDrawer.tsx`: *"Bounding-box overlay omitted: no bounding-box data exists…"* (~`:380`), *"Uses If-Match: {version} for optimistic concurrency"* (~`:445`), *Kind of item* showing raw values such as `product` (~`:394`), and cut-out tabs.
- **Asset page** `frontend/src/routes/AssetDetailPage.tsx`: the same If-Match line (~`:756`).
- **Expiry page** `frontend/src/routes/ExpiryPage.tsx` (~`:171`): *"…in blueprint urgency order. Filtering a category narrows the read on the server; the uncategorized count below comes from the served analytics summary and is never merged into the expiry stream."*
- **Catalog** `frontend/src/routes/CatalogPage.tsx` with `frontend/src/components/catalog/ProductCard.tsx` (~`:41`, `raw: "Source Only"`): enum words such as `product` and `Source Only` on cards.
- **Inbox** `frontend/src/routes/InboxPage.tsx`: raw ids and step states such as `COMPLETED` (F11).
- **Font:** `--font-sans` in `frontend/src/theme/tokens.css` (~`:32`) is the system stack; the comment at ~`:36` reserves the swap for this slice.

**The design values** (SG-273's table; the tokens already exist in `tokens.css`, light and `.dark`): ground `--paper`, text `--ink`, secondary `--ink-muted`, lines `--line`, accent `--primary` (dark text uses `--link`, SG-302), **`border-radius: 0`**, joined square tabs, uppercase spaced labels (letter-spacing .04–.12em) with a count header such as *"23 ITEMS"*, photos borderless on the paper, **no text under 13 px**. Do not copy tandpfun code.

## G0 — Preflight

Copy these lines exactly:

```
mkdir -p output/SG-301-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-301-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-301/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-301/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make and `ruff` call; a missing venv `python` is a STOP. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch only in `output/SG-301-scratch/`; `/tmp` is denied on this lane. **Run `date +%s` at the start of every goal and gate step and quote the stamps.** `output/` itself and `output/dispatch` are never touched.

## G1 — The font (D31)

- In `frontend/`: `npm view @fontsource-variable/instrument-sans version license` (quote both), then `npm install --save-exact @fontsource-variable/instrument-sans@<that version>`. **This is the only install authorised.** A network or registry failure is a STOP with the verbatim error — no other source, no CDN link, no Google Fonts URL.
- `package.json` gains exactly that one dependency, exact version; `package-lock.json` changes only for it (quote `git diff --stat` and the added lock entries' names).
- Import it once at the app entry (`frontend/src/main.tsx`) and set `--font-sans` to `"Instrument Sans Variable", ` followed by the existing system stack, in one place. Prove the built CSS contains the `@font-face` and the woff2 file is emitted into the build output (name and size).

## G2 — No developer copy on the owner's screens

**Criterion, not a list** (`DISPATCH.md` §2a): any text the owner can see that names an implementation detail — an id or UUID, an enum value (`product`, `unknown`, `Source Only`, `COMPLETED`, `AWAITING_REVIEW`, …), an HTTP or API term (`If-Match`, `PATCH`, `endpoint`, `served`, `stream`), a blueprint or slice reference, or a sentence explaining what the code does or omits. **Enumerate it yourself** on the Inbox, Expiry page, Catalog (cards and filters), item panel and asset page — grep and read the rendered DOM — and compare with the expectations above; report the difference either way in a table: screen · text · replaced with / removed.

- **Enum values** read as plain words through **one shared label map** (for example `frontend/src/lib/labels.ts`): `product` → *Product*, `Source Only` → *Photo only* (or your better plain word; say why), step states → *Done*, *Waiting for you*, *Skipped (AI off)* — a skipped step never reads as done (F11).
- **Developer sentences are removed**, not reworded. The Expiry page keeps at most one plain line of help, for example *"Food and other dated things, soonest first."*
- **Ids are never shown**; where an id is the only label, show the item's name, or *"Unnamed item"*.
- **Do not change** behaviour, routes, data, or the If-Match header itself — only what is displayed.

## G3 — The tandpfun look on the catalog and the item panel (D18)

Catalog: the paper ground, the count header (*"23 ITEMS"*), joined square filter tabs, photos borderless on the paper in the grid, labels in the spaced uppercase style, square corners. Item panel: the same ground, square corners, no cut-out tabs (joined square tabs if tabs remain), labels in the label style, nothing under 13 px. Inbox and Expiry page: tokens, square corners, ≥ 13 px — no layout redesign. **Pantry, one line only:** the EXPIRED label in `frontend/src/routes/PantryPage.tsx` (~`:196`, `fontSize: 11`) becomes ≥ 13 px (SG-302 audit I1); nothing else on the Pantry changes. **Every text pair on these screens, light and dark, read from the DOM, into `docs/worklogs/SG-301_contrast.md`** (element · fg/bg · ratio, both themes · font size, checked against the 13 px floor · size class · pass at 4.5:1 / 3:1). A failing pair on these screens is fixed here.

## G4 — Tests, FAIL-then-PASS

New `*.sg301.test.tsx` files: `--font-sans` begins with `"Instrument Sans Variable"`; the label map turns each enum value you found into its plain word; none of the developer sentences you enumerated renders (one assertion each); the item panel and asset page render no `If-Match` text; an Inbox step whose output is skipped does not read *Done*. Logs `docs/worklogs/SG-301_fail.log`, `SG-301_pass.log` (`PG-EV-09`); FAIL logs hold names and first assertion only. An older test asserting removed text is updated here, each named.

## G5 — The full gate, once, on the candidate (before any screenshot)

In order, exact counts (`PG-IC-08`), each into `docs/worklogs/SG-301_<step>.log`: `ruff` on any backend file (expected none); `eslint` on every changed frontend file; `tsc --noEmit`; the frontend build with `outDir` in scratch (`PG-SC-12`); `make backend-test` once (host suite, two deselected, image proof — **the image build runs `npm ci` against the new lockfile; it must pass**); `make frontend-test` once; every SG-301 test file and every older test file you changed, twice consecutively (`PG-DP-04`). The pre-existing `eslint` error in `App.household-nav.test.tsx` and the repo-wide mypy reds are out of scope. A red is fixed here only within scope; an old test asserting behaviour this slice did not mean to change is a **STOP and report**.

## G6 — Screenshots, after the gate

Scratch app exactly as SG-300 and SG-302 did (`docs/worklogs/SG-300_shots/INDEX.md`): fresh SQLite under `output/SG-301-scratch/` by the project's migrations, test data through the API with generated images (food and non-food, one item with no name, one with a skipped AI step in the Inbox), every provider off; backend `127.0.0.1:18301`, frontend from the scratch build on `127.0.0.1:14301`, **built with `VITE_API_BASE=http://127.0.0.1:18301`** (a bundle pointing at 8003 is a STOP). DevTools via a Node script in scratch (built-in `WebSocket`, no install). **Stop servers by the PIDs you started; never `pkill -f`.**

Into `docs/worklogs/SG-301_shots/`, in this order:

| Shot | Theme | Width |
|---|---|---|
| Catalog | light, dark | 1280 |
| Catalog | dark | 375 |
| Item panel open | light, dark | 1280 |
| Inbox with the skipped step | dark | 1280 |
| Expiry page | dark | 1280 |
| Asset page | light | 1280 |

**Proof per shot:** sha256 (12 characters) and size; no two shots share a hash (quote the check); in `INDEX.md` the proving text **and the computed `font-family` of the page heading, both read from the DOM**. A shot failing its proof is retaken once, then reported failed. Servers stopped and shown gone; **`output/SG-301-scratch/` removed by that exact path.**

## Acceptance criteria

- **A1** — G1: version and licence quoted; exactly one dependency, exact version; lock diff limited to it; `@font-face` and the woff2 in the build output.
- **A2** — G2: the enumeration table; the shared label map; no developer sentence, raw enum, id or HTTP term visible on the five screens.
- **A3** — G3: catalog and item panel in the look; nothing under 13 px; `SG-301_contrast.md` from DOM-read values, every pair passing.
- **A4** — G4 tests FAIL on base, PASS on candidate; updated tests named.
- **A5** — G5 gate green with counts; image build with `npm ci` passing.
- **A6** — G6 shots with hash, size, proving text and DOM-read font family; distinct-hash check; servers stopped by PID; scratch removed.
- **A7** — Scope as below; zero backend, migration, Dockerfile, compose, `.env`, live database, stored files, host, provider, running-container or deploy bytes; `frontend/dist` untouched.
- **A8** — Preflight proven; health 200 at start and end; phase seconds from the stamps.
- **A9** — `PB-3` vacuity: a failure would look like the system font in a shot, a second dependency, a lock entry not under the font package, a raw enum or id on screen, a developer sentence left, a skipped step reading *Done*, text under 13 px, a pair under its bar, two shots with one hash. Say which you checked.
- **A10** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/package.json`, `frontend/package-lock.json` (the font only); `frontend/src/main.tsx` (the import); `frontend/src/theme/tokens.css`; `frontend/src/routes/{InboxPage,ExpiryPage,CatalogPage,AssetDetailPage}.tsx`; `frontend/src/routes/PantryPage.tsx` (the EXPIRED label size only); `frontend/src/components/shell/ItemInspectorDrawer.tsx`; `frontend/src/components/catalog/*`; components those five screens render **only for displayed text and styling**; a new `frontend/src/lib/labels.ts`. Any other product file is a STOP and report (`PG-EV-03`).
- **Tests:** new `*.sg301*` files; older frontend tests only where they assert removed or reworded text, each named.
- **No backend file.**
- **Authorised runtimes:** the preflight; the one `npm view` and the one `npm install` in G1; the `make` gates; tests; `eslint`; `tsc`; the frontend build; scratch servers on `127.0.0.1:18301` and `:14301`; the project's migrations on scratch files; headless Chrome; a Node DevTools script in scratch. No other install, image or port.
- Evidence: `docs/worklogs/SG-301*` only. No deploy, restart or touch of the running container, its image tag, the live database or the stored files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; `npm view` and `npm install` **300 s** together; host suite **600 s**; image proof **600 s** (it now runs `npm ci` with a new package); frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; scratch server start **60 s** each; one screenshot **60 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **At 1300 s elapsed by your `date +%s` stamps, stop whatever you are doing, commit, write the report, publish.** **There is no optional goal.** Order: G0, G1, G2, G3, G4, G5, then G6 in the table's order. A stop leaves the rest `REMAINING`, never described as done. Expected ≈1250 s (`UNVERIFIED — my estimate`: SG-273, one new screen with 17 shots, took 1277 s; this is copy and styling over five screens, one install and 8 shots) — near the stop line, so commit after each goal.

## Report

Destination: `docs/worklogs/SG-301_report.md`, evidence beside it. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: elapsed against ≈1250 s and every phase's seconds; each premise above confirmed or falsified with file and line; the font version, licence and lock diff; the G2 enumeration table; how G3 was met; each gate step's counts; every red and what was done; the shot table; the contrast summary; changed files; the contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint and criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-301`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-301 | Report: docs/worklogs/SG-301_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
