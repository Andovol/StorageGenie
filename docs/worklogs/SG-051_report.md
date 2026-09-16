SG-051 — test-truth: stale CTA tests assert the dialog (opencode, medium)

Dispatch-ID: SG-051 · Coder: opencode · Effort: medium (process argv `--variant medium`, PID 598945)
· Model: `unknown` (no `--model` on argv; per policy the CLI default is the model and is omitted —
`CO-78`) · Contract: 0.27.0.
BASE REF: `origin/automation` — BASE COMMIT (resolved): `2df30a40fe14f68152c3c6237258eea3610bf164`
(start HEAD; worktree clean at start, `git status --porcelain` empty).
WORK_HEAD: the commit carrying this report + worklog + verify log (resolved hash published in the
receipt note; labelled work commit, not a tip, `CO-55c`).
Work dir: `/home/andrei/StorageGenie` · Remote: `git@github.com:Andovol/StorageGenie.git` (as on host).
Autonomy: L2 (slice autonomy). Spend: `$0` slice-metered · Network: none · DB: none · Restart: none.
AI stays OFF: this is a test-only slice; no model call, no endpoint, no network.
Live-state ledger: no DB writes, no jobs, no live requests; every test ran under vitest with
`../api/client` mocked.

## (a) Issues / deviations / surprises

- **F-1 — one extra import line in `shell.test.tsx` beyond the literal "one-test hunk".** The ceiling
  names `shell.test.tsx` but describes the edit as a "one-test hunk". To satisfy G1's "no `/capture`
  route renders" as a **non-vacuous** property, the test must mount a `/capture` route probe, which
  requires `Route`/`Routes`; `shell.test.tsx:3` was `import { MemoryRouter } from "react-router-dom";`.
  I changed it to `import { MemoryRouter, Route, Routes } from "react-router-dom";` — a second hunk in
  the named file, disclosed here rather than hidden. The alternative (asserting only that the click's
  default was prevented) would have been a weaker, implementation-coupled assertion and the route-probe
  property is exactly what G1/`PG-EV-05` names. `catalog.test.tsx` already imported `Route`/`Routes`
  (line 3), so it is a true one-test hunk. **This is a minimal enabler inside a ceiling-named file, not
  an out-of-ceiling edit** — reported, not silently absorbed.
- **Premises verified live (one corrected).**
  - Stale `shell.test.tsx` tail test at base (lines 245-249): quoted verbatim —
    `test("Import Asset routes to /capture", async () => { renderCatalog(); await
    screen.findByText("Drill"); expect(screen.getByRole("link", { name: /import asset/i
    })).toHaveAttribute("href", "/capture"); });`
  - Stale `catalog.test.tsx` empty-CTA test at base (lines 207-211 — the packet said 207-210): quoted —
    `test("an empty result shows the dashed canvas with the Import New Item CTA to /capture", () => {
    renderWithRouter(<ProductGrid items={[]} density="grid" householdId="h1" />); expect(
    screen.getByText(/import new item/i)).toHaveAttribute("href", "/capture"); });` The end line was
    211, not 210; the test body is the same test the packet named.
  - Modal contract (unchanged): `AssetImportModal.tsx:160-165` — `role="dialog"`, `aria-modal="true"`,
    `aria-label="Import assets"`; both rewritten tests assert exactly `getByRole("dialog", { name:
    "Import assets" })`.
  - Interception hunks that the FAIL leg reverts (`PG-EV-01`): `AppHeader.tsx:86-106` — `<Link
    to="/capture" onClick={(event) => { event.preventDefault(); setImportOpen(true); }}>` plus the
    conditional `<AssetImportModal>` at `AppHeader.tsx:107-109`; `ProductGrid.tsx:293-303` — the
    empty-state `<Link to="/capture" onClick={… preventDefault(); setImportOpen(true); }>` plus the
    conditional mount at `ProductGrid.tsx:308-310`. Both product files were untouched in the shipped
    diff.
  - `BASE` at start = `origin/automation` = `2df30a4` — the packet's premises are live; no product
    file differs from base.
- **No STOP.** Every shipped requirement is enabled by a file the ceiling names; the only friction is
  F-1, handled inside the named file.
- **No "pre-existing failure" claim is made.** The base targeted run was green (2 files / 40 tests,
  1.29 s) before any change, so no pre-existing failure exists to cite.
- **Mutation run not separately owed.** The FAIL leg is a real behavioural fail on both rewritten
  tests (offending DOM quoted below), so per G2's optional clause no separate mutation run is
  performed. Stated explicitly, not skipped silently.

## (b) Actions

Changed paths (test-only; nothing else):
- `frontend/src/components/shell/shell.test.tsx` (G1) — line 3 import gains `Route, Routes` (F-1);
  the tail test is rewritten from the bare-`href` assertion to: render `CatalogPage` under
  `Routes` with a `/capture` probe, `await screen.findByText("Drill")`, `fireEvent.click` the
  `Import Asset` link, then assert `getByRole("dialog", { name: "Import assets" })` is present and
  `queryByText("capture probe")` is absent. Renamed to what it proves:
  `"the header Import Asset CTA opens the import dialog and does not render /capture"`.
- `frontend/src/components/catalog/catalog.test.tsx` (G1, one-test hunk) — the empty-CTA test is
  rewritten to render `ProductGrid items={[]}` under `Routes` with a `/capture` probe, assert the
  dashed canvas (`catalog-grid-empty`), click `Import New Item`, then assert the dialog is present and
  `capture probe` is absent. Renamed: `"an empty result shows the dashed canvas whose Import New Item
  CTA opens the import dialog"`.
- `docs/worklogs/SG-051.log`, `SG-051_report.md`, `SG-051_verify.log`.

Temporary mutation (reverted, not in the shipped diff): `AppHeader.tsx` and `ProductGrid.tsx`
interception `onClick` props removed for the FAIL leg, then `git checkout --` restored. `git diff` of
both product files is empty and `diff` against the `HEAD` blob prints identical for each (`PG-EV-09`).
Push: `automation`. No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. External effects: none.

## (c) Verification

Artifacts (rendered DOM + raw committed output, never exits — `PG-EV-02`; raw in `SG-051_verify.log`):
- **FAIL leg (`PG-EV-01`), LABEL: real behavioural FAIL.** Interceptions reverted, then
  `vitest run src/components/shell/shell.test.tsx src/components/catalog/catalog.test.tsx` →
  `Test Files 2 failed (2)` / `Tests 2 failed | 38 passed (40)`, 1.35 s. Both failures quote the DOM:
  `<body><div><div>capture probe</div></div></body>` — i.e. the click navigated to `/capture` and the
  dialog never opened. One failure quoted in full: `FAIL src/components/catalog/catalog.test.tsx >
  ProductGrid > an empty result shows the dashed canvas whose Import New Item CTA opens the import
  dialog / TestingLibraryElementError: Unable to find an accessible element with the role "dialog" and
  name "Import assets"` (`catalog.test.tsx:220`); the second is the identical error at
  `shell.test.tsx:262`. This falsifies both rewritten tests on the retired behaviour.
- **Green run:** full suite = `21 passed (21)` files / `131 passed (131)` tests, 3.85 s; `eslint src`
  exit 0 (no output); `npm run build` (`tsc && vite build`) exit 0 — `1960 modules transformed`,
  292.21 kB JS / 86.95 kB gzip, built in 1.74 s. Test count is unchanged from base (131); the rewrite
  changes assertions, not counts.
- **Properties asserted (`PG-EV-05`), not commands:** "clicking the header Import Asset CTA opens the
  import dialog"; "clicking the grid's Import New Item CTA opens the import dialog"; "`/capture` does
  not render on either CTA click" (route probe, non-vacuous). Both tests assert the rendered dialog,
  never the bare `href`.
- `PG-EV-09`: FAIL leg and green run are both raw in `SG-051_verify.log`; intercept restoration is
  proven byte-identical there.
- Scope gates: `git diff` names only the two test files (worklogs added after) · `git diff -- backend/`
  empty · `git status -- backend/alembic backend/migrations` empty (no migration) · `git diff --
  frontend/package.json frontend/package-lock.json` empty (no new dependency) · secret scan of the two
  test files: 0 real matches (`password|secret|token|api[_-]?key|PRIVATE KEY|AKIA|ghp_`, grep exit 1) ·
  `git check-ignore` exit 1 on both paths (neither ignored) · nothing pushed to
  `storagegenie-evidence` · no DB / restart · live spend `$0` · no ignored file staged.
- **Vacuous-pass statement.** No acceptance criterion is claimed vacuously. The route-probe assertions
  render a real `/capture` route that would appear if navigation happened (proven by the FAIL leg,
  where exactly that DOM appears); the dialog assertion looks up the real `role="dialog"` node the
  unchanged modal renders. The only pre-existing stale pass this slice removes is the two `href`
  assertions themselves — verified at base and quoted in (a). No empty-diff / empty-set / skipped-gate
  pass is reported.
- INTENT: both CTA tests now prove the click opens the dialog and does not route, matching the SG-047
  product behaviour; X (code) / Y (checks) / Z (approved packet G1–G3) agree.
- TWINS: `import-modal.test.tsx` "CTA wiring (G2)" still carries the equivalent coverage for the full
  `AppHeader` component and the empty `ProductGrid`; this slice removes the two now-redundant stale
  assertions rather than duplicating them, and leaves the twin file untouched.

## Receipt (note on the coder-reports notes ref)

Work committed and pushed to `automation`, worktree clean (`CO-55`). No push to
`storagegenie-evidence`; no `{{RECEIPT_CMD}}` (per this packet's M20-corrected block). The note was
added on WORK_HEAD with the first line carrying both `Dispatch-ID:` and `Report:` (`CO-97`), the notes
ref pushed explicitly to `origin`, the refspec fetched explicitly (`<ref>:<ref>`, M21 — a bare fetch
never updates a notes ref), and the `git notes --ref=refs/notes/storagegenie-coder-reports show
<WORK_HEAD>` output is pasted verbatim in the delivery message (it cannot live inside this file, which
is itself part of the commit the note is attached to — same as SG-047/SG-050). If that `show` output
is absent from the delivery, this step was not executed and should be called out loudly. Final line:
`note=yes`.

## (d) UNCLEAR

- **FIRST READ:** whether the `shell.test.tsx` "one-test hunk" ceiling permitted the one extra import
  line needed for a non-vacuous `/capture` route probe. The ceiling names the file; the requirement
  names the property; I resolved it by treating the import as part of the named file's one test and
  disclosing it as F-1, rather than downgrading to a weaker no-navigation proxy.
- **DURING EXECUTION:** whether the FAIL leg was a genuine behavioural fail or an import hollow. It is
  the former — the reverted tree navigates and the DOM shows `capture probe`; quoted in the verify log.
- **REMAINING:** (1) the CTA links still expose `href="/capture"` for middle-click / open-in-new-tab
  (intentional, SG-047 F-1, unassigned); (2) `shell.test.tsx` now imports `Route`/`Routes` used only by
  the rewritten test — intentionally kept, lint-clean; (3) the `.rules-cache/` contract directory is
  absent from this checkout, so the `G-L1` fetch/version check could not be run locally — the packet
  header (`Contract 0.27.0`) and `STATE.md:1` (`Version 0.27.0`) are the version evidence used.
