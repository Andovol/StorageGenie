# SG-042 — paste-to-add photos + mobile camera capture on the Capture screen

**Dispatch-ID:** SG-042 · **Coder:** opencode · **Effort:** medium (`--variant medium`) ·
**Model:** `unknown` (no `--model` on argv; per policy the CLI default is the model, which is omitted)
**Contract:** 0.27.0 (installed `RULES.md` sha256 `a66aa431…` == payload `RULES.sha256`; offline read, no fetch)

**BASE REF:** `automation` → resolved commit `48aa92b1769040dff93ae277c811ca79c434aa4e` (two fields, as required).
**WORK_HEAD:** the commit carrying this file; the exact hash is published in the notes-ref receipt.
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.

**DATABASE:** none. **Restart:** none. **NETWORK:** none (no fetch, no `npm install`; `node_modules` was present).

## Starting tree and premise verification (quoted reads)

- Starting tree **CLEAN**: `git status --porcelain` empty; `HEAD == origin/automation == 48aa92b`.
- `AssetForm.tsx:30-43` `addFiles` — hashes each file and appends `{file, shaPreview}` to `previewFiles` (confirmed).
- `AssetForm.tsx:45-52` `onDrop` → `addFiles(e.dataTransfer.files)` (confirmed).
- `AssetForm.tsx:138-174` drop zone — `onDragOver`/`onDragLeave`/`onDrop`, dashed border, preview `<ul>` with a working `remove` button (confirmed).
- `AssetForm.tsx:154-161` file input — `type="file" multiple accept="image/*,.pdf"` (confirmed).
- `AssetForm.tsx:56-59,101-108` display-name-required guard + label/input — confirmed **untouched**.
- `CapturePage.tsx:46-49` renders `<AssetForm householdId={effective} onCreated=… />` (confirmed; no change needed).
- `frontend/package.json:9` `"test": "vitest run"` (confirmed).
- `client.ts:105-120` `uploadEvidence(householdId, file)` → `FormData` POST `/v1/evidence` (confirmed).
- grep re-verify **before** change: `onPaste` = **0** hits, `capture=` = **0** hits in `frontend/src`.

**Finding F-SG042-1 (path only, content matched).** The packet cites the mock pattern as `AssetDetailPage.test.tsx:7-14` under `components/`; the real file is `frontend/src/routes/AssetDetailPage.test.tsx`, and its lines 7-14 *are* the `vi.hoisted(...)` + `vi.mock("../api/client", () => api)` pattern. I followed the real path; content matched the packet.

## G1 — paste stages photos exactly like dropped files (`AssetForm.tsx`)

`useEffect` installs a **window-level** `paste` listener; on a native `ClipboardEvent` it reads
`e.clipboardData?.files` and, only when `files.length > 0`, calls `e.preventDefault()` and
`addFiles(files)` — the **same path** the drop zone and file input use. Cleanup removes the listener on
unmount.

**Scope decision (delegated): WINDOW with cleanup.** The requirement is "anywhere the capture screen can
receive keyboard focus"; the household `<select>` is on that screen but outside the `<form>`, so a
form-scoped handler would miss it. **Load-bearing evidence:** test (a)/(d) dispatch `paste` on the
focusable display-name input (a real element inside the screen); the event bubbles to the window listener
and the file is staged — see `SG-042_verify.log` Section 3. Pasted bytes are staged verbatim, never renamed.
Text-only paste (`files.length === 0`) stages nothing, errors nothing, disturbs no entry (test (b)). Hint
text now reads "Drag & drop photos here, click to select, or paste" — plain, no AI naming/derivation promise.

## G2 — take-a-photo control (`AssetForm.tsx`)

Added beside the existing multi-file input:
`<label>Take a photo <input type="file" accept="image/*" capture="environment" /></label>` — single shot
(no `multiple`), image-only. The existing multi-file input is **byte-for-byte unchanged** (still
`multiple`, `accept="image/*,.pdf"`): desktop select and `.pdf` handling are unchanged.

## G3 — tests (`frontend/src/components/AssetForm.test.tsx`, new)

Rendered directly with `householdId` + `onCreated` (no router); mocked `../api/client` by the committed
`vi.hoisted` + `vi.mock` pattern. Four named tests: (a) paste stages name+size and remove deletes;
(b) text-only paste stages nothing / disturbs nothing; (c) camera input has `capture="environment"` and
image-only accept and is not multiple; (d) submit with a staged file posts `display_name` + `evidence_ids`.

**FAIL-then-PASS (`PG-EV-09`), both raw in `SG-042_verify.log`:**
- pre-change (feature absent): **4 failed / 4** (test file committed as `24e7b7e` on the base tree);
- post-change: **4 passed / 4**.

**`PG-EV-01` (non-vacuous):** all four expectations were deliberately inverted in one run →
**4 failed / 4** (Section 2), then restored via `git checkout --`.

**Gates:** `npm test` (vitest run) = **15 files / 44 tests passed** (2.89s); `npm run lint` **clean**;
`npm run build` (tsc + vite) **clean** (97 modules). Secret scan in the diff: **0**. No `backend/` diff,
no alembic diff, no frozen-prompt diff, no ignored file staged, nothing pushed to `storagegenie-evidence`.

## Acceptance / property checks (`PG-EV-02`, `PG-EV-05`)

Checked against the **rendered DOM / committed test output**, not command exit codes:
- "a pasted image file appears in the preview list with its name" — test (a) `findByText(/pasted\.png/)` + `/KB/` on rendered output.
- "the camera input carries `capture=\"environment\"`" — test (c) `toHaveAttribute("capture","environment")` and `accept="image/*"` on the rendered input.
- `git status --short` shows **no `backend/` path** (exclude-by-rule `PG-SC-05`, grep-gated).

## Budget (per leg, units)

| Leg | Actual | Budget |
|---|---|---|
| pre-change targeted run | 4.22 s | 120 s |
| post-change targeted run | 0.94 s | 120 s |
| PG-EV-01 mutation run | ~1.7 s test duration | 120 s |
| full suite | 2.89 s | 600 s |
| lint + build | 3.63 s | 600 s |

Overall comfortably below the 1500 s early-close and 2100 s overall bounds. No command was killed; no command hung.

## Live-state ledger

No DB writes · no restart · live spend **$0** (zero provider calls, AI OFF) · no network.
No migration; no new dependency; no frozen-prompt diff.

## Receipt note

Work pushed to `automation` with a clean worktree (`CO-55`). No push to `storagegenie-evidence`; no
`{{RECEIPT_CMD}}`. A single `git notes --ref=refs/notes/storagegenie-coder-reports add` on the WORK_HEAD
carries `Dispatch-ID: SG-042 | Report: docs/worklogs/SG-042_report.md | Work-HEAD: <hash>` as its first
line (`CO-97`), verified with `git notes … show <WORK_HEAD>` (raw quoted below).

## Verdict

Photo bytes are now staged by paste through the existing `addFiles` path and the mobile camera control is
present, with FAIL-then-PASS tests committed on both sides, suite+lint+build green, and the scope ceiling
respected (frontend-only, no backend, no migration, no dependency, $0).

UNCLEAR — FIRST READ: whether "anywhere the capture screen can receive keyboard focus" is satisfied by a window-scoped handler that also fires while focus is outside the AssetForm (e.g. the household select); I read it as yes and chose window.
UNCLEAR — DURING EXECUTION: whether pasted files should be MIME/extension-filtered; G1 says "staged as-is", so I accept clipboard files verbatim and filter only on the camera input's `accept`.
UNCLEAR — REMAINING: whether S2 wants the window listener to survive a second mount point; today AssetForm mounts once (`CapturePage.tsx:46-49`), so one listener is correct.
