# SG-334 report — non-catalog nav *Import Asset* becomes *Add item* in catalog-header colours

Slice SG-334. Model and effort are not visible in my process arguments, so I state neither and infer nothing. Working directory `/home/andrei/StorageGenie`. Remote `origin` = `git@github.com:Andovol/StorageGenie.git`. BASE ref `origin/automation`, resolved BASE commit `2110be0f0464c5e609f31b29d515cad8fe6e6e1e` (commit message `SG-333 rated 90; packets SG-334 (Add item nav), SG-336/SG-337 (redesign C)`). WORK_HEAD = the report commit below (quoted with the push output; HEAD before the report commit was the G1 commit `7403e595`).

Contract: I received no contract version line for this run, so I echo no version line. I never attempted to read the contract folder (this lane denies it; the denial is expected and is not a STOP).

## Time

- Start stamp 1794952152. Stop-rule point (1100 s) = 1794953252 — never triggered; total elapsed ≈ 410 s (start 1794952152 → report ~1794952560), inside RUN_BUDGET_S 2100. REMAINING: none.
- G0 1794952152→1794952169: session checks + premise grep (1794952164) + preflight block (1794952169: `docker version` shows a Server section 29.9.2, `docker run --rm busybox true` rc 0, socket `/run/dispatch-storagegenie-SG-334/docker.sock` listed with `srw-rw---T`, health `curl http://127.0.0.1:8003/v1/health` = 200).
- G1 1794952209→1794952259: test written, FAIL run 1794952220, FAIL log 1794952232, fix + PASS 1794952248, post-change grep 1794952252, G1 commit 1794952259.
- G2 1794952271→1794952497: eslint 1794952280, tsc 1794952288, build 1794952305 (2.84 s), backend-test start 1794952321 (host suite 79.97 s), frontend-test 1794952435 (27.55 s), repeats 1794952468/2481/2485/2497, end health 200.
- Cleanup: scratch removed 1794952534 (before this report); report written after.

## Change (G1)

`frontend/src/App.tsx` — the shared legacy nav's import link on every non-catalog route (`showImport = pathname !== "/"`):
- line 156: `aria-label="Import Asset"` → `aria-label="Add item"`;
- lines 171–172: `backgroundColor: "hsl(var(--ink))"` → `"hsl(var(--primary))"`, `color: "hsl(var(--paper))"` → `"hsl(var(--primary-foreground))"` — exactly the catalog header's pair in `frontend/src/components/shell/AppHeader.tsx:98–99`;
- line 176: `<span className="sg-import-label">Import Asset</span>` → `<span ...>Add item</span>`; the `sg-import-label` class is untouched.
- Behaviour preserved: `to="/capture"` + `preventDefault` + `setImportOpen(true)` still opens `AssetImportModal` instead of routing.

Test changes:
- New `frontend/src/sg334-add-item-nav.sg334.test.tsx`: renders `<App />` at `/capture` (as `shell.test.tsx:448` does), asserts a link named *Add item*, no link named and no text reading *Import Asset*, the link's inline `style` containing `--primary` and `--primary-foreground`, and that clicking it opens the `Import assets` dialog while `Add an item` (CapturePage) persists.
- `frontend/src/components/shell/shell.test.tsx:451–452`: comment + assertion `findByRole("link", { name: "Import Asset" })` → `{ name: "Add item" }`.
- `frontend/src/sg330-r2.sg330.test.tsx:91` (absence assertion on the catalog route) untouched and still valid — proven by the full-suite pass.

## Premises (PB-1), each confirmed or falsified

- "The two App.tsx strings are the only product occurrences": CONFIRMED with one nuance — pre-change `grep -rn "Import Asset" frontend/src` returned 6 hits, of which exactly 2 were product code (`App.tsx:156`, `App.tsx:176`); the other 4 were test titles recording the rename (`import-modal.test.tsx:322`, `shell.test.tsx:400`), the old-name assertion (`shell.test.tsx:452`), and the catalog-absence assertion (`sg330-r2.sg330.test.tsx:91`). Post-change grep (quoted under A4) shows zero product occurrences.
- "Legacy link uses `--ink`/`--paper`, catalog header uses `--primary`/`--primary-foreground`": CONFIRMED — `App.tsx:~171–172` vs `AppHeader.tsx:98–99`, matched line-for-line before the edit.
- "`shell.test.tsx:451–452` asserts the old name and is updated": CONFIRMED and done.
- "`sg330-r2.sg330.test.tsx:91` asserts the old name is absent from the catalog and stays valid": CONFIRMED — file untouched, passes in the full suite.
- PB-2 (denied operation / broken preflight = STOP): no denial encountered; docker Server present, busybox rc 0, health 200 at both ends.
- PB-7 (full suites run): done — backend host + image, frontend whole suite, plus named-file repeats.

## Gate (G2), exact counts

- `eslint` (`SG-334_eslint.log`): rc 1 with exactly 1 problem — `frontend/src/App.household-nav.test.tsx:2:10 'fireEvent' is defined but never used`; this is the known pre-existing error in a file this slice does not touch. Comparison proving "only the known error": log tail shows `✖ 1 problem (1 error, 0 warnings)` and no other file path.
- `tsc --noEmit` (`SG-334_tsc.log`): rc 0, empty log (0 lines).
- Build (`SG-334_build.log`): rc 0, `✓ 1973 modules transformed`, `✓ built in 2.84s`, emitted to absolute `--outDir "$PWD/output/SG-334-scratch/build"` (since removed with the scratch).
- `make backend-test` (`SG-334_backend-test.log`): rc 0 — host `817 passed, 2 deselected, 59 warnings in 79.97s`; image proof `2 passed, 6 deselected in 2.08s`. Backend unchanged; this proves it.
- `make frontend-test` (`SG-334_frontend-test.log`): rc 0 — `Test Files 80 passed (80)`, `Tests 555 passed (555)`, 0 failed.
- Repeats, each rc 0: `SG-334_repeat_sg334_1.log` 1 passed (1); `SG-334_repeat_sg334_2.log` 1 passed (1); `SG-334_repeat_shell_1.log` 23 passed (23); `SG-334_repeat_shell_2.log` 23 passed (23).
- Post-change `grep -rn "Import Asset" frontend/src` (rc 0, 5 lines, quoted verbatim):
  - `frontend/src/components/shell/import-modal.test.tsx:322` — test title `(... SG-330 R2: Import Asset -> Add item)` (history note, asserts *Add item*);
  - `frontend/src/components/shell/shell.test.tsx:400` — same kind of test title;
  - `frontend/src/sg334-add-item-nav.sg334.test.tsx:65–66` — absence assertions (excepted by the packet);
  - `frontend/src/sg330-r2.sg330.test.tsx:91` — absence assertion (excepted by the packet).
  - Zero product occurrences remain; `frontend/src/App.tsx` no longer appears.

## Changed files

Versus BASE `2110be0f`: `frontend/src/App.tsx` (M), `frontend/src/components/shell/shell.test.tsx` (M), `frontend/src/sg334-add-item-nav.sg334.test.tsx` (new), `docs/worklogs/SG-334_fail.log`, `SG-334_pass.log`, `SG-334_eslint.log`, `SG-334_tsc.log`, `SG-334_build.log`, `SG-334_backend-test.log`, `SG-334_frontend-test.log`, `SG-334_repeat_sg334_1/2.log`, `SG-334_repeat_shell_1/2.log`, `SG-334_report.md` (new). Two commits: G1 `7403e595` (change + test + shell.test update + fail/pass logs), report commit (this report + gate logs; trailer `Dispatch-ID: SG-334`).

## Criterion lines

- A1 — Preflight ran verbatim with `date +%s` (1794952169): Server 29.9.2 present, busybox rc 0, health 200 at start and 200 at end (1794952497); phase seconds G0 ~17 s, G1 ~50 s, G2 ~226 s, total ≈ 410 s.
- A2 — G1 done with file and line (`App.tsx:156`, `:171–172`, `:176`); every premise above is marked confirmed, the PB-1 product-occurrence nuance named.
- A3 — Test FAILED before (`SG-334_fail.log`: `Unable to find role="link" and name "Add item"`, 1 failed) and PASSES after (`SG-334_pass.log`: 1 passed); logs named.
- A4 — Gate green with the exact counts quoted above; `*sg334*` file twice green (1/1, 1/1), `shell.test.tsx` twice green (23/23, 23/23); final grep quoted verbatim.
- A5 — Frontend files only (`git status` shows only `frontend/src/*` + `docs/worklogs/*`); no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live-database, stored-file, host, provider, container or deploy bytes; `frontend/dist` is git-ignored and untouched; `/tmp` never used (`TMPDIR` and pytest basetemp pointed into the scratch for every command); tree clean except ignored `output/` (its `dispatch` and another slice's `SG-324-scratch` untouched); scratch `output/SG-334-scratch` removed 1794952534 before this report.
- A6 — PB-3 vacuity checked four ways: (1) legacy name still rendered on `/capture` — the FAIL run proves the test detects it; (2) routing instead of dialog — click asserts the `Import assets` dialog appears with `Add an item` persisting; (3) ink colours kept — style-token assertions fail on `--ink`/`--paper`; (4) red suite — full frontend (555) and backend (817+2) suites green after.
- A7 — Verdict line below matches every check above.

UNCLEAR: none. REMAINING: none.

Verification: PASS
