# SG-315 report: SG-307's drop-zone highlight restored; 8 old styling assertions moved to the new look

SLICE SG-315 · model and effort: not visible in my process arguments, so not stated and not inferred · working directory /home/andrei/StorageGenie · remote origin git@github.com:Andovol/StorageGenie.git · BASE ref origin/automation, resolved commit 7a1ded934ff46c9bdb0da21b96053f85c411582d · WORK_HEAD 17bc655 (last gate-log commit; the report commit that publishes this file is quoted in the publish step) · contract version line: none received (the contract folder is denied in this lane; I did not read it)

**Result: G1 and G2 done. Gate green: eslint shows only the known error, frontend 0 failed, backend host and image green, changed files twice green. Verification: PASS.**

## Timing (stamps from `date +%s`)

- Elapsed: 1794509658 (G0 start) to 1794509972 (G2 logs committed) = 314 s; the 1100 s stop line was not reached.
- G0 preflight: 658 to 660 (2 s). Premise reads: 660 to 683 (23 s).
- G1 test written, failed on base, fix, eight assertions, candidate run, logs, commit: 683 to 764 (81 s); G1 commit e7f6449 at 106 s, inside the 500 s line.
- G2 eslint 786 (rc 1, known error only); tsc 789 (rc 0); build 794 to 803 (rc 0); `make backend-test` 807 to 906 (rc 0, 99 s); `make frontend-test` 908 to 928 (rc 0, 20 s); files twice 934 to 946 (rc 0 both); end checks and scratch removal 953; G2 logs commit 17bc655 at 972.
- One bash call was refused by a permission rule (external_directory). I retried with the `workdir` parameter and no `cd`, and the retry ran. `npx` is not on PATH here, so vitest ran as `./node_modules/.bin/vitest` (same binary `npm test` uses).

## Premises

- **P1 confirmed.** `frontend/src/components/shell/AssetImportModal.tsx:76` declares `const [dragOver, setDragOver] = useState(false);`, and nothing read `dragOver` before this slice (the drop-zone `style` at lines 208-217 did not use it). `git show 0dd3fa7:frontend/src/components/shell/AssetImportModal.tsx` line 206 reads `className={\`${dragOver ? "border-primary" : "border-border"} bg-card-muted\`}`. The loss is real: the drop zone never showed a file over it.
- **P2 confirmed.** `docs/worklogs/SG-307r1_frontend-test.log` lists 8 failing tests: AssetForm (2), InboxPage (2), theme-adoption (1), shell (3). Each received value in the log is the new class (`sg-paper-control focus-ring`) or the missing one (`focus-ring`, empty class).
- **P3 confirmed from the SG-307r1 report, not re-run here.** The eslint second error is `AssetImportModal.tsx:76 dragOver` (SG-307r1 report § Gate counts); the known error is `App.household-nav.test.tsx:2 fireEvent`. The G2 eslint log now shows only the second one (`docs/worklogs/SG-315_eslint.log`: `App.household-nav.test.tsx`, 1 problem).

## G1: drop zone and the 8 tests

**Item 1 (product, one line).** `frontend/src/components/shell/AssetImportModal.tsx:211`: `borderColor: "hsl(var(--line))"` became `borderColor: dragOver ? "hsl(var(--primary))" : "hsl(var(--line))"`. Same square paper look; only the border colour follows the drag state, as the pre-SG-307 `border-primary` / `border-border` ternary did.

**New test (`frontend/src/components/shell/import-modal.sg315.test.tsx`).** Renders the modal, asserts the rest border, fires `dragOver` and asserts `--primary`, fires `dragLeave` and asserts `--line` again.
- FAIL on base (`docs/worklogs/SG-315_fail.log`): 1 failed; first assertion `expected 'hsl(var(--line))' to be 'hsl(var(--primary))'` at `import-modal.sg315.test.tsx:25`. The run came before any product edit, so the product files were at origin/automation.
- PASS on candidate (`docs/worklogs/SG-315_pass.log`): 5 files, 57 tests, rc 0 (the 5 files: the new test plus the four older files below).

**The 8 tests, one line each.** Every one is decided **(a)**: the old class guarded something the owner still sees, and the new look carries the same thing under the new treatment. No product file was changed for any of them, so there is no **(b)**.

| # | Test (file:line) | Decision | Old assertion → new assertion | Why (product evidence) |
|---|---|---|---|---|
| 1 | AssetForm: "the asset-type select carries the themed control treatment" (`AssetForm.test.tsx:141`) | (a) | `toHaveClass("bg-background", "text-foreground", "border-border")` → `toHaveClass("sg-paper-control", "focus-ring")` | The select is the themed paper control; received `sg-paper-control focus-ring` (log). |
| 2 | AssetForm: "the file pickers are real file inputs hidden behind themed labels" (`AssetForm.test.tsx:152` and `:158`) | (a) | both `closest("label")` lines: `toHaveClass("bg-background", "text-foreground", "border-border")` → `toHaveClass("sg-paper-control", "focus-ring", "file-pick")` | The labels are `${THEMED_CONTROL_CLASS} file-pick` (`AssetForm.tsx:190`, `:206`); received `sg-paper-control focus-ring file-pick`. |
| 3 | InboxPage: "renders failed loaded job detail and retries that loaded id" (`InboxPage.test.tsx:44`) | (a) | `toHaveClass("bg-background", "text-foreground", "border-border")` → `toHaveClass("sg-paper-control", "focus-ring")` | The Retry button uses `THEMED_CONTROL_CLASS` (`InboxPage.tsx:77`). |
| 4 | InboxPage: "lists a loaded review task and resolves its loaded id" (`InboxPage.test.tsx:99`) | (a) | same old → same new | The Resolve button uses `THEMED_CONTROL_CLASS` (`InboxPage.tsx:89`). |
| 5 | theme-adoption: "capture screen rides the shared centered container with no household select" (`theme-adoption.test.tsx:238`) | (a) | same old → same new (`selects[0]`) | The one combobox on that screen is the themed select (log: `sg-paper-control focus-ring`). |
| 6 | shell: "a category pill filters server-side and carries the primary style when active" (`shell.test.tsx:320`) | (a) | `toHaveClass("bg-primary")` → `toHaveClass("sg-paper-control", "focus-ring")`, plus `expect(pill.style.backgroundColor).toBe("hsl(var(--ink))")` and, for the inactive "All (4)" pill, `.style.backgroundColor` `toBe("hsl(var(--paper))")` | Active pill is ink-filled inline (`CatalogToolbar.tsx:156-173`); the old `bg-primary` class is gone, but the active/inactive difference is still asserted. |
| 7 | shell: "Clear all empties all three filters" (`shell.test.tsx:360`) | (a) | `toHaveClass("text-link")` → `expect(clearAll.style.color).toBe("hsl(var(--link))")` and `expect(clearAll.style.textDecoration).toContain("underline")` | Clear all keeps the link colour and underline inline (`CatalogToolbar.tsx:283-290`). |
| 8 | shell: "an empty saved-search list renders a muted None yet" (`shell.test.tsx:581`) | (a) | `toHaveClass("text-muted-foreground")` → `expect(none.style.color).toBe("hsl(var(--ink-muted))")` | The muted text is inline `hsl(var(--ink-muted))` (`CatalogToolbar.tsx:247`). |

Two things kept as they were: the test titles (e.g. "carries the primary style", "renders a muted None yet") still use the old wording, so the diff touches assertions only. No assertion was deleted (see A6).

## Gate counts (G2)

- `eslint src`: rc 1, **1 problem**: `App.household-nav.test.tsx:2` `fireEvent` unused (the known one). `AssetImportModal.tsx:76` no longer appears (`SG-315_eslint.log`). Compare SG-307r1 (2 errors).
- `tsc --noEmit`: rc 0 (`SG-315_tsc.log`, empty).
- `npm run build -- --outDir /home/andrei/StorageGenie/output/SG-315-scratch/build` (runs `tsc && vite build`): rc 0 (`SG-315_build.log`); output went to scratch, `frontend/dist` untouched (mtime 1794256522, before this run).
- `make backend-test`: rc 0. Host: **805 passed, 2 deselected** (74.93 s). Image proof: **2 passed, 6 deselected**. Compare SG-307r1 § Gate counts: 805 passed, 2 deselected; 2 passed, 6 deselected. Same counts (`SG-315_backend-test.log`).
- `make frontend-test`: rc 0. **Test Files 54 passed (54); Tests 467 passed (467); 0 failed** (`SG-315_frontend-test.log`). Compare SG-307r1: 466 tests, 8 failed; the difference is the +1 new sg315 test and the 8 now passing.
- Files twice (9 files, same list both runs: `theme-adoption.test.tsx`, `InboxPage.test.tsx`, `sg307r1-fixes.sg307r1.test.tsx`, `AssetForm.test.tsx`, `import-modal.sg315.test.tsx`, `panel.sg307.test.tsx`, `shell.test.tsx`, `import-modal.test.tsx`, `catalog.sg307.test.tsx`): **Tests 91 passed (91)** both runs, rc 0 both (`SG-315_twice-1.log`, `SG-315_twice-2.log`; 91 equals 91).
  - `import-modal.test.tsx` was not changed here, but it tests the changed product file, so it is included as an extra.

## Changed files (`git diff --stat 7a1ded9 HEAD`: 8 files, 62 insertions, 10 deletions)

- `frontend/src/components/shell/AssetImportModal.tsx` (1 line: drop-zone border)
- `frontend/src/components/shell/import-modal.sg315.test.tsx` (new)
- `frontend/src/components/AssetForm.test.tsx`, `frontend/src/routes/InboxPage.test.tsx`, `frontend/src/routes/theme-adoption.test.tsx`, `frontend/src/components/shell/shell.test.tsx` (assertion lines only)
- `docs/worklogs/SG-315_fail.log`, `docs/worklogs/SG-315_pass.log`, and the gate logs `SG-315_{eslint,tsc,build,backend-test,frontend-test,twice-1,twice-2}.log`

No backend, migration, Dockerfile, compose, lockfile, dependency or `.env` file changed.

## Unclear / remaining

- UNCLEAR: model and effort are not visible in my process arguments; not stated.
- UNCLEAR: contract version line: none received; I did not read the contract folder.
- UNCLEAR: 8 test titles still use the old wording (see table); kept to keep the change to assertions.
- REMAINING: none in G1 or G2. The publish steps follow this commit.

## Criteria

- **A1** Drop-zone highlight restored in `AssetImportModal.tsx:211` (the file named in P1); the 8 tests resolved as (a) above, old and new assertions quoted.
- **A2** `import-modal.sg315.test.tsx`: FAIL on base (`SG-315_fail.log`, 1 failed, `expected 'hsl(var(--line))' to be 'hsl(var(--primary))'`), PASS on candidate (`SG-315_pass.log`, 57/57 across the 5 files).
- **A3** Gate green: eslint 1 problem (the known `App.household-nav.test.tsx:2`); frontend 467 passed, 0 failed; backend host 805/2 deselected, image 2/6; files twice 91/91 both runs. Exact counts above.
- **A4** No backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored file, host, provider, container or deploy change. Docker was used only by `make backend-test`'s image proof, as the packet requires. `frontend/dist` untouched (mtime check above). No `/tmp` used; scratch `output/SG-315-scratch` removed before the report (`ls output` afterwards shows only `SG-301-scratch` and `dispatch`, neither touched by me). The tree is clean except `output/` after this commit.
- **A5** Preflight: `docker version` showed the Server section, rc 0; `docker run --rm busybox true` rc 0; health `http://127.0.0.1:8003/v1/health` returned **200 at start (1794509658)** and **200 at end (1794509953)**. Phase seconds from the stamps above.
- **A6** Vacuity checks: (i) a border that did not change would fail the `--primary` assertion (the FAIL log shows exactly that); (ii) `git diff 7a1ded9 HEAD -- frontend | rg '^-.*\b(test|it|describe)\('` returns nothing, so no test or describe was removed; the only added test lines are the new `describe` and `test` in the sg315 file; (iii) every changed assertion is an equality on a class or an inline style token, never a looser check; the pill check adds an inactive-pill check; (iv) the 8 tests were red before this slice (`SG-307r1_frontend-test.log`); (v) eslint shows only the known error; (vi) no red suite in the final gate.
- **A7** Verification: PASS.

Verification: PASS
