# SG-302 — Pantry warning text readable in dark mode, every text pair measured, "Capture" a link, dark shots retaken

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases, plus throwaway SQLite files under scratch for the screenshot app. No live database read or write.
**Restart: none.** No deploy; rider SG-303 follows this slice.
**Provider: none.** No key, no `.env`, no spend; the screenshot app runs with every provider off.

**Contract:** recorded `0.58.0` (`AGENTS.md`). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line as you received it. A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-10, D27/D28 (*"Both approved."*) and the 2026-11-12 start message: *"give it a dark-mode value of at least 4.5:1 (--link in tokens.css is the existing dark tint), re-measure every text colour in light and dark, make the empty state's 'Capture' a link, and retake the dark Pantry screenshots."* Stage C (*"d14 ok"*, L3). The owner: *"design, look and feel are very important, so hold every screen to that."*

## Why this exists

SG-300 (`36be113..a2b8a2d`, rated 92) delivered the Pantry the owner asked for, but its audit (`docs/worklogs/SG-300_audit.md`) found:

- **I1** — the warning text (*EXPIRED*, *"Expired 3 days ago"*, *"Use by tomorrow"*) uses `hsl(var(--primary))` in `frontend/src/routes/PantryPage.tsx` (expected ~`:196` the EXPIRED label, ~`:204` the time-left line; verify). In dark mode `--primary` stays `2 41% 30.6%` (`frontend/src/theme/tokens.css` ~`:51`), which measures **≈1.95:1 on `rgb(15,14,13)`** and ≈1.73:1 on the dark `--paper` (`UNVERIFIED — Architect's calculation from the token values`). WCAG AA needs 4.5:1 for this size.
- **I3** — three dark shots were not taken: Use soon 1280, the notice, the catalog's Gone view.
- **I5** — the empty state (~`:392`) says *"Add an item from Capture"* with no link.

**Premises to falsify first (`PB-1`):**

- `--link` (`tokens.css` ~`:14` light, ~`:54` dark, SG-118's comment) equals `--primary` in light and is `2 41% 72%` in dark — ≈7.4:1 on dark `--paper`, ≈8.3:1 on `rgb(15,14,13)` (`UNVERIFIED — Architect's calculation`). If so, switching the Pantry's warning text to `--link` changes nothing in light and fixes dark. **Establish this from the file; if `--link` fails 4.5:1 on the real surface, choose another value of the same hue that passes and say why.**
- **Which surface the tile text actually sits on in dark** — the page sets `--paper` (~`:327`), yet the audit's measured background was `rgb(15,14,13)` (`--background`, `tokens.css` ~`:44`). **Read the computed background of a tile's text node in the dark DOM** and measure against that, not against a token you assume.
- `.text-link` or an equivalent class may already exist in `tokens.css` (~`:143`); reuse it if it fits rather than a new inline colour.

## G0 — Preflight

Copy these lines exactly:

```
mkdir -p output/SG-302-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-302-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-302/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-302/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make and `ruff` call; a missing venv `python` is a STOP — install nothing. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch only in `output/SG-302-scratch/`; `/tmp` is denied on this lane. **Run `date +%s` at the start of every goal and gate step and quote the stamps**; the report gives each phase's seconds from them. `output/` itself and `output/dispatch` are never touched.

## G1 — The fix

1. **Warning text in dark ≥ 4.5:1.** Every Pantry text that uses the accent (the EXPIRED label, the time-left line for expired and ≤ 2 days, anything else you find using `--primary` as a text colour on this page — enumerate them with a grep and list them) takes `--link` or the value you established above. **Light mode must look exactly as before** (same computed colour; prove it).
2. **Empty state:** *"Capture"* becomes a real `Link` to `/capture` (react-router `Link` is already imported in the file), in the link colour, underlined or otherwise visibly a link, with a focus outline (the existing `--link` outline rule applies). The sentence otherwise stays: *"No food yet. Add an item from Capture and classify it as food to see it here."*
3. **Every text pair on the Pantry page, measured, light and dark.** Enumerate every distinct (text colour, background) pair the page renders — heading, subtitle, *Not sorted yet* line and link, section headings, tile name, time-left (muted and accent), EXPIRED, quantity, *No photo yet*, action buttons, notice text and its *Put back*, the empty state and its link, the tile error text. **Read each computed colour and the computed background behind it from the DOM** through the DevTools session, compute the WCAG ratio, and write a table to `docs/worklogs/SG-302_contrast.md`: element · light fg/bg · ratio · dark fg/bg · ratio · size class (normal or large) · pass at 4.5:1 normal / 3:1 large. **Any pair under its bar is fixed in this slice** if the fix is a colour on this page or a Pantry-only token; a failing pair that belongs to a shared component outside the scope below is reported, not fixed.

**Do not change** the Pantry's layout, order, wording (beyond the link), data rules, or any other screen.

## G2 — Tests, FAIL-then-PASS

In `frontend/src/routes/PantryPage.sg302.test.tsx`: the EXPIRED label and an accent time-left line render with `var(--link)` (or your chosen token), not `var(--primary)`; the empty state contains a link named *Capture* whose `href` ends `/capture`. Logs `docs/worklogs/SG-302_fail.log`, `SG-302_pass.log` (`PG-EV-09`); **FAIL logs hold the failing names and first assertion only.** An SG-300 or SG-273 test asserting `--primary` on these elements is updated here, each named.

## G3 — The full gate, once, on the candidate (before any screenshot)

In order, exact counts (`PG-IC-08`), each into `docs/worklogs/SG-302_<step>.log`:

1. `ruff check` on any backend file changed (expected: none).
2. `eslint` on every frontend file changed; `tsc --noEmit`; the frontend build with `outDir` in scratch so `frontend/dist` is untouched (`PG-SC-12`). The pre-existing `eslint` error in `App.household-nav.test.tsx` and the repo-wide mypy reds are out of scope.
3. `make backend-test` once — host suite green, the two marked tests deselected, the image proof passing.
4. `make frontend-test` once.
5. The SG-302, SG-300 and SG-273 frontend test files twice consecutively (`PG-DP-04`).

**A red is fixed here only if** the fix stays in this slice's scope. An old test that fails is run alone on the base (`D443`); one asserting behaviour this slice did not mean to change is a **STOP and report** with names and the first assertion.

## G4 — Screenshots and the contrast table, after the gate — required

Run the app **only on scratch**, as SG-300 did (`docs/worklogs/SG-300_shots/INDEX.md` — read it for the seed and the DevTools approach): a fresh SQLite file under `output/SG-302-scratch/` made by the project's migrations, test data through the API (about a dozen food items with generated test images; counted and amount items; one expired 3 days, one expired yesterday, several due within 2 and 7 days, some later, one dateless, one unsorted, one gone), every provider off; backend `127.0.0.1:18302`, frontend from the scratch build on `127.0.0.1:14302`. **The scratch build sets `VITE_API_BASE=http://127.0.0.1:18302`** — `frontend/src/api/client.ts` defaults to `http://localhost:8003`, the live app; a scratch bundle without it is a STOP. For the **empty state**, a second scratch database with a household and no food. Never port 8003, never the live container, never the stored files.

Clicks (the notice after Use it up, the catalog's Gone view) and the DOM reads are driven by a small Node script in scratch speaking the Chrome DevTools Protocol to headless Chrome (Node's built-in `WebSocket`; no package install). **Never `pkill -f` a pattern that can match your own command line** (SG-300 lost ≈200 s that way); stop servers by the PIDs you started.

Capture into `docs/worklogs/SG-302_shots/`:

| Shot | Theme | Widths |
|---|---|---|
| Pantry, Use soon in view | dark | 1280, 375 |
| Pantry, Use soon in view | light | 375 (proof light is unchanged) |
| Pantry, the notice after Use it up | dark | 375 |
| Pantry, empty state with the Capture link | dark, light | 375 |
| Catalog, Gone view | dark | 1280 |

**Proof per shot, all three required:** its sha256 (first 12 characters) and size; **no two shots share a hash** — check it and quote the check; and in `docs/worklogs/SG-302_shots/INDEX.md`, the **on-screen text that proves the state, read from the DOM through the same DevTools session**, plus, for the Pantry shots, the computed colour of the EXPIRED label read from the DOM. A shot that fails its proof is retaken once, then reported as failed — never described as showing what it does not. Stop the scratch servers by PID and show they are gone; **remove `output/SG-302-scratch/` by that exact path at the end.**

## Acceptance criteria

- **A1** — G1.1: every accent-text use on the page enumerated; dark ratio ≥ 4.5:1 on the measured surface; light computed colour identical to the base's (quoted).
- **A2** — G1.2: *Capture* is a link to `/capture`, visibly a link, focusable.
- **A3** — G1.3: `SG-302_contrast.md` lists every pair, light and dark, from DOM-read values; every pair passes its bar or is reported as outside scope with its owner.
- **A4** — G2 tests FAIL on base, PASS on candidate, logged; any old test updated is named.
- **A5** — ruff (none expected), eslint, tsc clean; build rc 0; backend suite green with image proof; frontend suite green; counts quoted; the three files twice green.
- **A6** — Every shot in the table with hash, size, DOM-confirmed proving text and the label's computed colour; distinct-hash check quoted; servers stopped by PID; scratch removed by exact path.
- **A7** — Scope as below; zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes; `frontend/dist` untouched.
- **A8** — Preflight proven; health 200 at start and end; phase seconds from the stamps.
- **A9** — `PB-3` vacuity: a failure would look like a dark ratio under 4.5:1, a light colour that changed, *Capture* as plain text, a pair missing from the table, a value typed from a token instead of read from the DOM, two shots with one hash, a scratch bundle pointing at 8003, a red suite row, a test passing once and failing the second time. Say which you checked; none observed.
- **A10** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/src/routes/PantryPage.tsx`; `frontend/src/theme/tokens.css` **only** for a Pantry-only token if `--link` does not serve.
- **Tests:** new `*.sg302*` files; SG-300 and SG-273 frontend tests only where they assert `--primary` on these elements, each named.
- **No backend file.** **Any other product file is a STOP and report** (`PG-EV-03`). Reads of any file are allowed.
- **Authorised runtimes:** the preflight, the `make` gates, the tests, `eslint`, `tsc`, the frontend build, **the scratch servers on `127.0.0.1:18302` and `:14302`, the project's migrations on scratch files, headless Chrome, and a Node DevTools script in scratch.** No package install, no other image, no other port.
- Evidence: `docs/worklogs/SG-302*` only. No deploy, no restart, no touch of the running container, its image tag, the live database or the stored files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **300 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; scratch server start **60 s** each; one screenshot **60 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **At 1300 s elapsed by your `date +%s` stamps, stop whatever you are doing, commit, write the report, publish.** A stop rule, not a target. **There is no optional goal.** Order: G0, G1, G2, G3, then G4 in the table's order with the contrast table last. A stop inside G4 leaves the rest `REMAINING`, never described as done. Expected ≈900 s (`UNVERIFIED — my estimate`: SG-300 took ≈964 s for nine design changes and 12 shots; this is one colour, one link, a measured table and 6 shots).

## Report

Destination: `docs/worklogs/SG-302_report.md`, evidence beside it. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: elapsed against ≈900 s and every phase's seconds from the stamps; each premise above confirmed or falsified, with its file and line; how each G1 line was met; each gate step's counts; every red and what was done; the shot table with hashes, proving text and label colour; the contrast summary (pairs, passes, any out-of-scope failures); changed files; the contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint and criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-302`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-302 | Report: docs/worklogs/SG-302_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
