SG-047 — import modal: staged queue, auto-detect, real pipeline (opencode, medium)

Dispatch-ID: SG-047 · Coder: opencode · Effort: medium (process argv `--variant medium`, PID 570911)
· Model: `unknown` (no `--model` on argv; per policy the CLI default is the model and is omitted —
`CO-78`) · Contract: 0.27.0.
BASE REF: `origin/automation` — BASE COMMIT (resolved): `00e77a8694da723f7a5bbc207294cffb2aee2461`
(start HEAD; worktree clean at start, `git status --porcelain` empty).
WORK_HEAD: the commit carrying this report + worklog + verify log (resolved hash published in the
receipt note; labelled work commit, not a tip, `CO-55c`).
Work dir: `/home/andrei/StorageGenie` · Remote: `git@github.com:Andovol/StorageGenie.git` (as on host).
Autonomy: L3 (D63 wardrobe track, step 5 of 5).
Spend: `$0` slice-metered · Network: app API only (real traffic: one 5 s `GET /v1/health` probe) · DB:
none new · Restart: none. AI stays OFF: the modal calls only `/v1/evidence`, `/v1/imports`,
`/v1/imports/{id}/run` — no model endpoint.
Live-state ledger: **no live jobs created.** All transport (`uploadEvidence`/`apiPost`/`apiGet`) ran
under vitest with `../api/client` mocked; no user-confirmed `Process` action reached a running service,
so no `PG-EV-06` job id exists to report. The only real request was the bounded health probe:
`curl -s --max-time 5 http://localhost:8000/v1/health` → body `Not Found`, exit 0 (a server answers on
:8000 but the route is absent — reported, not acted on; this slice does not depend on it).

## (a) Issues / deviations / surprises

- **F-1 — two existing tests assert the behaviour this slice retires, and neither test file is inside
  the scope ceiling.** Verified at base: `frontend/src/components/shell/shell.test.tsx:245-248`
  ("Import Asset routes to /capture", asserting `getByRole("link", …).toHaveAttribute("href",
  "/capture")`) and `frontend/src/components/catalog/catalog.test.tsx:207-210` ("an empty result shows
  the dashed canvas with the Import New Item CTA to /capture"). The ceiling lists only
  `AssetImportModal.tsx`, `import-modal.test.tsx`, `AppHeader.tsx`, `ProductGrid.tsx`, `docs/worklogs`;
  `shell.test.tsx` and `catalog.test.tsx` are not named. Converting the triggers to `<button>` would
  break both, and the ceiling forbids editing them. **Design call (mine, reported):** keep each trigger
  a React Router `<Link to="/capture">` and intercept the click (`event.preventDefault()`) to open the
  dialog. React Router's `Link` runs the user handler first and skips navigation when
  `defaultPrevented`, so the dialog opens and the route does not change; the `href` is preserved for
  direct navigation, middle-click and open-in-new-tab. This is the same call SG-050 recorded for
  `ProductCard` ("DURING EXECUTION"), so it is a precedent, not a novelty. **Loud caveat:** those two
  old tests now pass *vacuously* w.r.t. their names — they assert the `href`, which is unchanged, and
  no longer exercise the click. Real behavioural coverage for both G2 hunks is therefore placed in the
  new `import-modal.test.tsx` ("CTA wiring (G2)"), which asserts the dialog appears and the `/capture`
  route does **not** render. Recommendation: a follow-up (or a widened ceiling) updates those two
  tests; this slice does not, by rule.
- **Premises verified, all live (not corrected).**
  - `jobs.py:18-20` — `class ImportCreate(BaseModel): evidence_ids: list[str] = …; config: dict = …`.
    `jobs.py:32-75` — `POST /imports`, 201, `Idempotency-Key` header, dedupe + replay, `config=payload.config`.
    `jobs.py:78-85` — `POST /imports/{job_id}/run` → `job_service.run_job`.
  - `client.ts:105-120` — `uploadEvidence(householdId, file)` posts `FormData` to `/v1/evidence` with
    `household_id`, returns `{ id, sha256, storage_key, size_bytes }`.
  - CTA sites: `AppHeader.tsx:78-94` (`<Link to="/capture">… Import Asset`),
    `ProductGrid.tsx:290-295` (`<Link to="/capture">Import New Item</Link>` plus the note
    "Opens the Capture route; the DQ9 import modal arrives with SG-047." — that note is now replaced).
  - `InboxPage.tsx:16-26` — jobs query `GET /v1/jobs`, detail `GET /v1/imports/{id}`, `JobCard` list.
- **No STOP.** Every requirement this slice shipped is enabled by a file the ceiling names. The stale
  tests are a finding with a destination (above), not a requirement that needs an out-of-ceiling edit.
- **Health probe surprise.** `GET /v1/health` is `Not Found` while `curl` exits 0 — i.e. something
  listens on :8000 but that exact route does not exist. Not used by this slice; reported for the host
  record, never claimed as a slice failure.
- **No "pre-existing failure" claim is made anywhere.** The baseline suite was green before the change
  (21 files / 117 tests at base, all pass), so no pre-existing failure exists to cite.
- **Not a violation of AI-OFF.** The modal sends no prompt and touches no model endpoint; the
  auto-detect checkbox maps to the existing `run` endpoint, which is the deterministic pipeline entry
  the packet names.

## (b) Actions

Changed paths (all inside the ceiling; nothing else):
- `frontend/src/components/shell/AssetImportModal.tsx` (new, G1) — accessible dialog
  (`role="dialog"`, `aria-modal`, `aria-label="Import assets"`, `Esc` closes, focus moves to the close
  button on open and back to the invoking element on unmount); dropzone with drag-drop, file select and
  `window` `paste` (the SG-042 clipboard-files path, `clipboardData.files`); client-side PNG/JPEG/WebP
  filter that names every rejected file + reason (never silently dropped); the DQ9 25 MB target named
  with the 20 MB server cap disclosed (`config.py:11`); the auto-detect checkbox defaulting ON with
  both paths stated in plain words; a live pending queue with `Ready`, per-file `Remove` and
  `Cancel` that clears staged bytes and uploads nothing; `Process N Items` disabled at 0, uploading
  each file, creating **one** `/v1/imports` with **one** `Idempotency-Key` (UUID), running it iff
  checked, then closing and navigating to `/inbox`.
- `frontend/src/components/catalog/ProductGrid.tsx` (empty-CTA hunk, G2) — the empty-state CTA opens
  the modal instead of routing; the stale note is replaced; the modal is mounted from the empty branch
  with the existing `householdId` prop.
- `frontend/src/components/shell/AppHeader.tsx` (CTA hunk, G2) — the `Import Asset` link opens the
  modal instead of routing; household id read from `localStorage` then `useHouseholds()[0]` (the
  existing cached query, no new fetch); modal mounted from the header.
- `frontend/src/components/shell/import-modal.test.tsx` (new, G3) — 14 tests: drop / select / paste
  staging, rejection named + skipped, Remove, live count, Process disabled at 0, checked path (exact
  create payload shape + UUID idempotency header + run call + `/inbox`), unchecked path (create only,
  run never called), created job visible on the real `InboxPage`, Cancel discards and uploads nothing,
  Esc closes, focus in/out, and the two CTA-hunk behaviours.
- `docs/worklogs/SG-047.log`, `SG-047_report.md`, `SG-047_verify.log`.

Temporary mutations (reverted, not in the shipped diff): `AssetImportModal.tsx` M1/M2/M3.
Push: `automation`. No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. External effects: none.

Durations (UTC, live): first read ~15:39, health/args read 15:44:55Z, end ~15:47 →
≈ 400 s / 2100 s overall (≈19%). Per leg (actual vs budget): premise+design ~120 s/120 s ·
baseline suite 3.95 s/600 s · hollow run 0.49 s/120 s · implementation ~90 s/120 s · green targeted
1.09 s/120 s · suite+lint+build ~10 s/600 s · M1/M2/M3 ~4 s/120 s · post-revert suite 3.81 s/600 s ·
gates+commit/report+note ~90 s/120 s. Early-close 1500 s not approached. Retries: 0. Provider calls: 0.
Test-command count: 7 vitest invocations (baseline, hollow, green targeted, M1, M2, M3, post-revert).
HIGHEST-IMPACT action: the Link-interception design call (F-1) — it satisfies G2 and keeps the suite
green without an out-of-ceiling edit, and the tradeoff is disclosed.

## (c) Verification

Artifacts (rendered DOM / committed outputs + asserted request shapes, never exits — `PG-EV-02`; raw
in `SG-047_verify.log`):
- **Hollow run (class 8), LABEL: hollow, not evidence.** `import-modal.test.tsx` present, the new
  module parked → vite: `Failed to resolve import "./AssetImportModal" from
  "src/components/shell/import-modal.test.tsx"`, `Test Files 1 failed (1)`, `Tests no tests`, 0.49 s.
  The module was restored and `diff -q` against the saved original reports identical. This is the
  documented pre-change failure (unresolvable import), quoted.
- **Green run:** targeted `import-modal.test.tsx` = `14 passed (14)`, 1.09 s; full suite = `21 passed
  (21)` files / `131 passed (131)` tests, 3.85 s (was 20/117 at base; +1 file, +14 tests).
- **Mutations (`PG-EV-01`), each wrong value fed singly, each reverted byte-identical:**
  - M1 checkbox branch (`if (autoDetect)` → `if (!autoDetect)`) → `2 failed | 12 passed (14)`: the
    checked test fails ("expected 2nd spy call … but called only 1 times") and the unchecked test
    fails ("expected spy to be called 1 times, but got 2 times").
  - M2 idempotency header (header object → `{}`) → `2 failed | 12 passed (14)`: both payload-shape
    tests fail ("expected 1st spy call to have been called with ['/v1/imports', …]").
  - M3 queue count (`Pending queue ({staged.length})` → `Pending queue (0)`) → `1 failed | 13 passed
    (14)`: the staging test fails on the live count.
  Each revert verified with `diff -q … && echo "Mn reverted clean"` (all printed clean).
- `eslint src` exit 0 (no output); `tsc && vite build` exit 0 (`1960 modules transformed`, 292.21 kB
  JS / 86.95 kB gzip, built in 1.67 s).
- **Properties asserted (`PG-EV-05`), not commands:** "rejected files are named + skipped"; "unchecked
  creates without running"; "checked creates one import with one UUID Idempotency-Key then runs then
  routes to /inbox"; "the created job is visible on /inbox"; "Cancel uploads nothing"; "the CTA opens
  the dialog instead of the route".
- `PG-EV-09`: hollow run, green run and all three mutation runs are committed raw in `SG-047_verify.log`.
- Scope gates: changed files exactly the 4 source/test files + 3 worklogs · `git diff -- backend/`
  empty · `git status -- backend/alembic backend/migrations` empty (no migration) ·
  `git diff -- frontend/package.json frontend/package-lock.json` empty (no new dependency) · secret scan
  of the 4 files: 0 real matches (the single hit is the word "tokens" in the pre-existing ProductGrid
  design-token comment) · `git check-ignore` exit 1 on all 4 paths (none ignored) · nothing pushed to
  `storagegenie-evidence` · no DB / restart · live spend `$0` · no ignored file staged.
- **CTA byte-diffs quoted.** `AppHeader.tsx` (from `git diff`):
  `-import { useEffect, useRef } from "react";` → `+import { useEffect, useRef, useState } from "react";`
  plus `+import { AssetImportModal } from "./AssetImportModal";` / `+import { useHouseholds } from
  "../../hooks/useAssets";`; new state block `+  const { data: households } = useHouseholds();` /
  `+  const [importOpen, setImportOpen] = useState(false);` / `+  const householdId = …`; on the
  `<Link to="/capture">`: `+        onClick={(event) => {` / `+          event.preventDefault();` /
  `+          setImportOpen(true);` / `+        }}`; and `+      {importOpen ? (` /
  `+        <AssetImportModal householdId={householdId} onClose={() => setImportOpen(false)} />` /
  `+      ) : null}`. `ProductGrid.tsx`: `+import { AssetImportModal } from "../shell/AssetImportModal";`;
  `+  const [importOpen, setImportOpen] = useState(false);`; the empty CTA
  `-        <Link to="/capture" className="bg-primary text-primary-foreground focus-ring" style={ctaStyle}>`
  → the same `<Link>` split onto lines with the `onClick` intercept; the note
  `-          Opens the Capture route; the DQ9 import modal arrives with SG-047.` →
  `+          Opens the import dialog: drop, select or paste photos. The Capture route stays for direct`
  `+          navigation.`; and the conditional `<AssetImportModal …>` mount. `git diff --stat` = 2 files,
  +33 −3 (the two new files are untracked additions).
- **Vacuous-pass statement.** No acceptance criterion is claimed vacuously. The new tests invoke the
  real component and assert rendered DOM + spy call records; the hollow run fails before the module
  exists and each mutation fails when the implementation is wrong. The one place a pass is *stale* is
  explicitly named: `shell.test.tsx:245-248` and `catalog.test.tsx:207-210` still assert the unchanged
  `href` and no longer test the click — flagged in F-1, not counted toward G2 coverage (which lives in
  the new file). No empty-diff or empty-set pass is reported.
- INTENT: code now opens the DQ9 import dialog from both CTAs and drives the existing import pipeline;
  X (code) and Y (checks) and Z (approved packet G1–G4) agree; nothing is bent.
- TWINS: `CapturePage`/`AssetForm` (manual create) is untouched and still directly reachable at
  `/capture`; `InboxPage` remains the job viewer and is reused as-is by the modal's post-Process
  navigation, not duplicated.

## Receipt (note on the coder-reports notes ref)

Work committed and pushed to `automation`, worktree clean (`CO-55`). No push to
`storagegenie-evidence`; no `{{RECEIPT_CMD}}` (per this packet's M20-corrected block). The note was
added on WORK_HEAD with the first line carrying both `Dispatch-ID:` and `Report:` (`CO-97`), the notes
ref pushed explicitly to `origin`, the refspec fetched explicitly (`<ref>:<ref>`, M21 — a bare fetch
never updates a notes ref), and the `git notes --ref=refs/notes/storagegenie-coder-reports show
<WORK_HEAD>` output is pasted verbatim in the delivery message (it cannot live inside this file, which
is itself part of the commit the note is attached to — same as SG-050). If that `show` output is
absent from the delivery, this step was not executed and should be called out loudly. Final line:
`note=yes`.

## (d) UNCLEAR

- **FIRST READ:** whether G2's "open the modal instead of routing" required changing the trigger
  element to a `<button>` (which would force edits to `shell.test.tsx` / `catalog.test.tsx`, both
  outside the ceiling) or could be satisfied by intercepting the existing `Link`. The ceiling decided
  it: intercept, and disclose the now-stale tests (F-1).
- **DURING EXECUTION:** whether the "25 MB gate target" should also be a client-side size rejection.
  The packet scopes the client filter to format only, so the size is named with the server cap
  disclosed and the server stays the enforcer; no promise exceeds the server.
- **REMAINING:** (1) update `shell.test.tsx:245-248` and `catalog.test.tsx:207-210` once the ceiling
  allows, so they assert the dialog-open behaviour instead of the retired routable href; (2) the modal
  is untested against a live backend (frontend-only ceiling — no job id to evidence); (3) the CTA links
  still expose `href="/capture"` for middle-click/open-in-new-tab — intentional, unassigned.
