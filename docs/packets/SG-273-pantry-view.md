# SG-273 — The Pantry view: what you have and what to use soon, in the tandpfun look, with screenshots of it and of SG-271's and SG-272's screens

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases, plus one throwaway SQLite file under scratch for the screenshot app. No live database read or write.
**Restart: none.** No deploy; a rider follows this slice.
**Provider: none.** No key, no `.env`, no spend; the screenshot app runs with every provider off.

**Contract:** recorded `0.58.0` (`AGENTS.md`). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line as you received it. A denial on that folder is expected and is not a STOP.

**Approval:** owner, stage C (*"d14 ok"*, L3, 2026-11-02); D18 (the tandpfun theme, full design on the Pantry view); the owner's 2026-11-10 brief: *"Then SG-273, the Pantry view, with screenshots of the SG-271 and SG-272 screens."* and *"design, look and feel are very important, so hold every screen to that."*

## Why this exists

Stage C's outcome is *"One styled Pantry you can use end to end: see it, use it up, quantities quick to change"* (`docs/ROADMAP.md`). Gone, put back and one-tap quantities are built and gated (SG-272, SG-297, SG-298). There is no Pantry screen: no file under `frontend/src/routes/` names it (expected; verify). This slice builds it. **Design quality is a first-class requirement** — the owner judges this screen by how it looks.

## The look — the owner's chosen design (D18), from tandpfun/wardrobe's `src/styles.css` (MIT; read 2026-11-02, not run)

| Element | tandpfun value | Here |
|---|---|---|
| Ground | `--paper: #f4f0e8` | Pantry background |
| Text | `--ink: #191919`; secondary `--muted: #66625d` | as given |
| Lines | `--line: #cfc8bc` | 1 px rules and tile edges |
| Accent | `--accent: #6e302e` | already ours: `--primary: 2 41% 30.6%` in `frontend/src/theme/tokens.css` |
| Shapes | `border-radius: 0`; joined square filter tabs | as given |
| Labels | uppercase, `letter-spacing` .04–.12em; a count header in that style (the owner's screenshot shows "80 PIECES") | as given, e.g. "23 ITEMS" |
| Grid | `repeat(auto-fill, minmax(165px, 1fr))`; photos borderless on the paper | as given |
| Small type | 16 rules at 9–11 px | **Enlarge: no text under 13 px** (D18; SG-271 was faulted for 12 px) |
| Dark mode | none in tandpfun | **Keep ours** (`.dark` in `tokens.css`): a dark paper, ink and line of your design, same shapes |
| Font | Instrument Sans Variable | **Not in this slice** (a new package; no install on this lane). Use `var(--font-sans)` so a later slice swaps it in one place |

- Add the paper, ink, muted-ink and line colours as **named tokens in `tokens.css`** (light and `.dark`), so later screens reuse them. Do not restyle any other screen.
- **Contrast, measured:** compute the WCAG contrast ratio for every text-on-ground pair you use, light and dark; body text ≥ 4.5:1, large text ≥ 3:1 (WCAG 2.x AA). Quote every ratio. One below its bar is fixed, not reported.
- **Real photos:** this slice uses generated test images only (the owner's photos are a sensitive surface). Say so; the owner's first look is with real photos.
- **Do not copy tandpfun code.** These values are the design; if you copy any file or block, its MIT notice travels with it — report it.

## G0 — Preflight

Copy these lines exactly:

```
mkdir -p output/SG-273-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-273-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-273/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-273/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make and `ruff` call; a missing venv `python` is a STOP — install nothing. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch only in `output/SG-273-scratch/`, removed by that exact path at the end; never touch `output/` itself or `output/dispatch`. **Run `date +%s` at the start of every goal and gate step and quote the stamps.**

**Prove a real screenshot first** (`STATE.md`: SG-271's headless Chrome wrote a 5169-byte PNG, possibly blank). Find a headless Chrome or Chromium on the host (`command -v chromium chromium-browser google-chrome`); render `about:blank` and a page with one large black square to PNG in scratch (`--user-data-dir` in scratch; `/tmp` is denied), and prove the second is not blank by a pixel measure (for example, Python reading the PNG and counting non-white pixels). **If no browser exists or every capture is blank, the screenshot goal (G4) is reported `REMAINING` with the evidence, and G1–G3 still run.** No package install.

## G1 — The Pantry view

- **Route `/pantry`**, a menu link to it, in the shell like the other screens (`frontend/src/components/shell/AppShell.tsx`). The roadmap says the link appears only when the journey works end to end — G2's journey test is that proof.
- **What enters:** ACTIVE assets whose accepted category is `food_beverages` (`lifecycle.active_clause()`; the category is an accepted assertion — **establish** how the catalog filters by category today: `list_assets` and `_facet_queries` in `backend/app/api/v1/assets.py`). **A small category-to-module map**, named as temporary in its docstring, says `food_beverages → pantry`; the Pantry view reads it. Prefer reusing `GET /v1/assets` with an existing filter; add a backend parameter only if none fits, and say which.
- **Unsorted items do not vanish:** ACTIVE assets with no accepted category are counted on the Pantry view as a clear "Not sorted yet" line that links to where they can be sorted.
- **Two parts:** **Use soon** first — items the expiry engine (`backend/app/services/expiry_engine.py`, `compute_status`) already calls expired or due soon; **establish** its "soon" window and reuse it, never a new number — then **Everything**, the full grid. An item appears in Use soon and in Everything.
- **Each pack is its own tile, no grouping by name** (names are not product identity). A tile: the photo (or a quiet placeholder when there is none), the name, the quantity as SG-272 shows it ("No count yet" / "No amount yet" when empty), the date or "No date". On the tile: **−1** for a counted item and **Use it up** — reuse SG-272's actions and wording (`ItemInspectorDrawer.tsx`, `CatalogPage.tsx`, the `/gone` and `/quantity/decrement` routes), never a second implementation. An amount item opens SG-272's quick amount edit. Opening a tile opens the item panel as the catalog does.
- **Empty state:** no food yet → one sentence and the way to add an item; never a blank page.
- **Mobile and desktop:** the grid holds at 375 px and 1280 px wide with no horizontal scroll.
- Household scoping as the catalog has it; the pantry is shared by the household (Q26).

## G2 — Tests, FAIL-then-PASS

Backend (in `backend/tests/test_sg273_pantry.py`) and frontend (`*.sg273.test.tsx` beside the files they test):

- only ACTIVE `food_beverages` assets are listed; a gone item leaves and comes back on put back; a non-food item never appears; an unsorted item is counted in "Not sorted yet";
- Use soon holds exactly what `compute_status` calls expired or soon, for one item each side of the window's edge;
- −1 and Use it up on a tile call the existing routes and the tile updates;
- **the journey:** create an item by hand → classify it food → it is on the Pantry view → −1 → Use it up → it is gone and listed in the catalog's Gone view.

Logs `docs/worklogs/SG-273_fail.log` and `SG-273_pass.log` (`PG-EV-09`). **Keep FAIL logs short:** failing test names and the first assertion only.

## G3 — The full gate, once, on the candidate (before any screenshot)

In order, exact counts (`PG-IC-08`), each into `docs/worklogs/SG-273_<step>.log`:

1. `ruff check` on every backend file this slice changed (`PG-EV-15`).
2. `eslint` on every frontend file this slice changed; `tsc --noEmit`; the frontend build with `outDir` in scratch so `frontend/dist` is untouched (`PG-SC-12`). The pre-existing `eslint` error in `App.household-nav.test.tsx` and the repo-wide mypy reds are out of scope.
3. `make backend-test` once — host suite green, the two marked tests deselected, the image proof passing.
4. `make frontend-test` once.
5. Every SG-273 test file twice consecutively (`PG-DP-04`).

**A red is fixed here only if** the fix stays in this slice's own files and changes nothing another slice built. An old test that fails is run alone on the base (`D443`); one asserting behaviour this slice did not mean to change is a **STOP and report** with names and the first assertion. `theme-adoption.test.tsx` (`frontend/src/routes/`) is the existing pattern for theme tests — extend it for the new tokens if it applies.

## G4 — Screenshots, after the gate — required, not optional

Run the app **only on scratch**: a copy of nothing live — a fresh SQLite file under `output/SG-273-scratch/` with the schema made by the project's own migrations, test data made through the API (about a dozen food items with generated test images, mixed counted and amount quantities, some due soon, one expired, one unsorted, one gone), every provider off; backend on `127.0.0.1:18273`, frontend served from the scratch build on `127.0.0.1:14273`. Never port 8003, never the live container, never the stored files.

Capture, **light and dark, at 1280×800 and 375×812**, PNG into `docs/worklogs/SG-273_shots/`:

1. **Pantry view:** full page; the Use soon part; the empty state; a tile after −1.
2. **SG-272's screens:** the item panel with Use it up / Put back and quantity controls; the catalog's Gone view; the asset page of a gone item with its reason.
3. **SG-271's screens:** the Review page for a committed candidate ("In your catalog", "Open item"); the asset page with a proposed date and shelf life ("Date proposed"); the Expiry page with a dateless note; an Inbox step row. Where one needs a state that cannot be made without a provider, say so and skip that one shot.

Name files `<screen>-<light|dark>-<width>.png`. **Per image, quote its size in bytes and its non-background pixel share** — a blank or error page is a failed shot, retaken once, then reported. Write `docs/worklogs/SG-273_shots/INDEX.md`: one line per image, what it shows. Stop the two scratch servers and show they are gone.

**The screenshots are evidence for the owner's design review, not a test.** Do not change any screen because of them; note in the report anything that looks wrong.

## Acceptance criteria

- **A1** — `/pantry` with a menu link; only ACTIVE food; "Not sorted yet" count; Use soon from the engine's own window (quoted); one tile per pack; −1 / Use it up reuse SG-272; empty state; no horizontal scroll at 375 px.
- **A2** — The look: tokens added light and dark; radius 0, uppercase spaced labels, the 165 px grid, the count header; no text under 13 px (say how you checked); every contrast ratio quoted and at its bar.
- **A3** — G2's tests FAIL on the base and PASS on the candidate, logged; the journey test passes.
- **A4** — ruff, eslint, tsc clean; build rc 0; backend suite green with image proof; frontend suite green; counts quoted.
- **A5** — SG-273 test files green twice consecutively.
- **A6** — Screenshots: the real-screen proof; every image with bytes and pixel share; `INDEX.md`; servers stopped; anything that looks wrong noted. Or `REMAINING` with the browser evidence.
- **A7** — Scope as below; zero migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes; `frontend/dist` untouched.
- **A8** — Preflight proven; health 200 at start and end; phase seconds from the stamps.
- **A9** — `PB-3` vacuity: a failure would look like a non-food or gone item on the Pantry, a Use soon list differing from the engine, a tile action not reaching the route, text under 13 px, a contrast ratio under its bar, a blank screenshot, a red suite row, a test passing once and failing the second time. Say which you checked; none observed.
- **A10** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** a new Pantry route and its components under `frontend/src/routes/` and `frontend/src/components/`; `frontend/src/components/shell/AppShell.tsx` (menu link and route); `frontend/src/App.tsx` if routes live there; `frontend/src/api/client.ts` and `types.ts`; `frontend/src/theme/tokens.css` (new tokens only); the temporary module map; and, **only if no existing filter fits**, one read-only parameter in `backend/app/api/v1/assets.py`. SG-272's components may be **imported**; changing them is a STOP unless a gate red forces it, named.
- **Tests:** new `*.sg273*` files; `theme-adoption.test.tsx` if extended.
- **Any other product file is a STOP and report** (`PG-EV-03`). Reads of any file are allowed.
- **Authorised runtimes:** the preflight, the `make` gates, the tests, `ruff`, `eslint`, `tsc`, the frontend build, **the two scratch servers on `127.0.0.1:18273` and `:14273`, the project's migrations on the scratch file, and headless Chrome against them.** No package install, no other image, no other port.
- Evidence: `docs/worklogs/SG-273*` only. No deploy, no restart, no touch of the running container, its image tag, the live database or the stored files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **300 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; scratch server start **60 s** each; one screenshot **60 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **At 1300 s elapsed by your `date +%s` stamps, stop whatever you are doing, commit, write the report, publish.** This is a stop rule, not a target. **There is no optional goal.** Order: G0, G1, G2, G3, G4 (shots in the order listed: Pantry, SG-272, SG-271). A stop inside G4 leaves the rest `REMAINING`. Expected ≈1100 s (`UNVERIFIED — my estimate`: SG-298's gate-and-small-fix took ≈625 s on this lane; a new screen plus screenshots has no measured precedent here).

## Report

Destination: `docs/worklogs/SG-273_report.md`, evidence beside it. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: elapsed against ≈1100 s and every phase's seconds from the stamps; the design calls you made and why (one line each); every contrast ratio; each gate step's counts; every red and what was done; the screenshot table; changed files; the contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint and criterion.

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-273`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-273 | Report: docs/worklogs/SG-273_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
