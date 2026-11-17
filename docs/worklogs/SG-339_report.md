# SG-339 report — a pack row shows its new date (or No date) right after save or clear

SG-339 | model and effort: not visible in the process arguments, so they are stated as not visible and nothing is inferred | working directory `/home/andrei/StorageGenie` | remote `git@github.com:Andovol/StorageGenie` | BASE ref `origin/automation` resolved to `726381c4d84e30ec2ac09fbdb520e58bbda3aee1` | WORK-HEAD `76cde9e2abe63208a5d3bc5393991e3515d44afe` (2 commits: G1 + G2 logs; report commit follows).

## Time (from `date +%s` stamps)

- Session start 1794956327. G0 preflight 1794956327–1794956328 (health 200, `docker version` shows Server, busybox rc 0).
- G1 FAIL run `docs/worklogs/SG-339_fail.log` 1794956378–1794956383: 2 failed | 8 passed (10); PASS run `SG-339_pass.log` 1794956390–1794956392: 10 passed; G1 commit 1794956404.
- G2: eslint 1794956412–1794956417; tsc 1794956428–1794956435 (clean); build 1794956459–1794956470; backend 1794956472–1794956588; frontend 1794956592–1794956623; twice first 1794956627–1794956631, second 1794956645–1794956650; end health 200 at 1794956631.
- Scratch `output/SG-339-scratch/` + `frontend/output/` removed 1794956667; gate-log commit 1794956670. Elapsed ≈351 s — inside the 1100 s stop line.

## G1 — Tests then the fix

- Premise about `PackEditor` amount refresh **confirmed**: `frontend/src/routes/AssetDetailPage.tsx:574-577` `invalidatePacks` does `qc.invalidateQueries({ queryKey: ["item-packs"] })` + `qc.invalidateQueries({ queryKey: ["asset", detail.id] })`, called on `decMut`/`incMut`/`patchMut` onSuccess (`:581`, `:586-588`, `:595-598`). Comparison: reading those lines shows the prefix key.
- Every production page using `ExpiryEntryForm` **named**: only `frontend/src/routes/AssetDetailPage.tsx:604` inside `PackEditor`. Comparison: `rg -n "ExpiryEntryForm" frontend/src` returns that plus `ExpiryPage.tsx:16` which imports only `DATE_TYPE_LABELS` (not the component), and tests `ExpiryEntryForm.test.tsx`, `sg324-p1.sg324.test.tsx`, `AssetDetailPage.test.tsx`, `sg336-item-page.sg336.test.tsx`. No other production caller.
- Change `frontend/src/components/ExpiryEntryForm.tsx:83-85` (submit) and `:101-103` (clear): after the existing `["asset", assetId, householdId]` invalidation, also `await qc.invalidateQueries({ queryKey: ["item-packs"] })` and `await qc.invalidateQueries({ queryKey: ["assets"] })` (prefix keys). Nothing else in the form changed — comparison `git diff origin/automation -- frontend/src/components/ExpiryEntryForm.tsx` shows only those 4 added lines.
- T9 (`frontend/src/sg336-item-page.sg336.test.tsx:289-327`): pack-1 starts `2030-05-06`, mock `enterManualExpiry` rewrites that pack's accepted expiry in `store` to the payload date, then Edit → type `2031-02-03` → Save date. Asserts the write args `("pack-1","hh",{expiry_date:"2031-02-03"},"a-exp-1")`, then `apiGet` calls with path exactly `"/v1/assets"` grew past the before-count, then the row's `pack-date` reads `Use by 3 Feb 2031`. T10 (`:329-356`): mock `clearExpiryDate` replaces that pack's expiry assertions with classification + `assertion("a-exp-cleared","plugin:expiry-tracker/expiry_date",null,"accepted")`, then Edit → Clear expiry date. Asserts `("pack-1","hh","a-exp-1")`, the same list-read growth, then `pack-date` reads `No date`. Both fed by the existing `apiGet` mock which serves the packs list as `{ items, next_cursor }` for path `"/v1/assets"` and detail by id — the shape SG-338 added (comparison: `sameNamePacks.ts:22-26` list read `/v1/assets` + `q`/`limit` + `items` filtered by trimmed lower-cased name).
- FAIL before (`SG-339_fail.log`): 2 failed | 8 passed, both fail `expected 1 to be greater than 1` at the list-read growth wait, and the DOM dump shows the row still `Use by 6 May 2030`. PASS after (`SG-339_pass.log`): 10 passed. One commit `a4431b15 SG-339 G1`.
- SG-338 STOP test `frontend/src/routes/AssetDetailPage.test.tsx:582-618` `Clear writes the null active and empties the form` now passes **unchanged**. Quote before and after (identical — comparison `git diff origin/automation -- frontend/src/routes/AssetDetailPage.test.tsx` is empty):
```
  test("Clear writes the null active and empties the form", async () => {
    assetBody = classifiedFood;
    api.clearExpiryDate.mockImplementation(() => {
      assetBody = {
        ...before,
        assertions: [
          classificationAssertion("a-class", "food_beverages", { critical: 1, urgent: 7, upcoming: 30 }),
          assertion(
            "a-exp",
            "plugin:expiry-tracker/expiry_date",
            { expiry_date: "2030-05-06", date_type: "best_before" },
            "superseded",
            "2026-01-02T00:00:00+00:00"
          ),
          assertion(
            "a-exp-cleared",
            "plugin:expiry-tracker/expiry_date",
            null,
            "accepted",
            "2026-01-03T00:00:00+00:00"
          ),
        ],
      };
      return Promise.resolve({ asset_id: "asset-1", assertion: null });
    });
    renderPage();

    // SG-338: the manual date form now lives in the pack row's Edit.
    await openPackEdit("asset-1");
    fireEvent.click(await screen.findByRole("button", { name: "Clear expiry date" }));

    await waitFor(() =>
      expect(api.clearExpiryDate).toHaveBeenCalledWith("asset-1", "hh", "a-exp")
    );
    await waitFor(() => expect(screen.getByLabelText("Date")).toHaveValue(""));
    expect(screen.queryByRole("button", { name: "Clear expiry date" })).not.toBeInTheDocument();
  });
```
Standalone run after the fix: `AssetDetailPage.test.tsx` 23 passed (was 22+1 STOP).

## Gate (G2)

- `eslint` (`SG-339_eslint.log`): only the known pre-existing `App.household-nav.test.tsx:2:10 'fireEvent' is defined but never used` error — comparison `grep` shows no other file errors.
- `tsc --noEmit` (`SG-339_tsc.log`, 0 bytes): clean, RC 0.
- Build into scratch (`SG-339_build.log`): `✓ built in 3.06s`, RC 0; `frontend/dist` untouched (comparison `git status` shows no `frontend/dist` entry; `git check-ignore frontend/dist` confirms ignored).
- `make backend-test` (`SG-339_backend.log`): host `817 passed, 2 deselected`; image proof `2 passed, 6 deselected`; RC 0 — backend unchanged, as required.
- `make frontend-test` (`SG-339_frontend.log`): **81 passed (81 files), 565 passed, 0 failed** — expected 0 after this (SG-338 left 1 failed / 562 passed of 563; +2 new tests = 565).
- Twice (`SG-339_twice.log`): `sg336-item-page` + `AssetDetailPage.test.tsx` + `ExpiryEntryForm.test.tsx` + `sg324-p1` — 4 passed, 45 passed, twice (both runs `4 passed / 45 passed`).
- Health 200 at start and end (end probe with the twice-run command output).

## Changed files

Frontend product only: `frontend/src/components/ExpiryEntryForm.tsx` (+4 lines), `frontend/src/sg336-item-page.sg336.test.tsx` (+73 lines: T9+T10). Evidence: 8 `docs/worklogs/SG-339_*.log` + this report. Comparison `git diff --name-only origin/automation` lists exactly those 10 paths. No backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp` writes (comparison `grep -r "/tmp" docs/worklogs/SG-339_*.log` shows no match; every command ran with `TMPDIR="$PWD/output/SG-339-scratch"` and `PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-339-scratch/pytest"`); tree clean except `output/` (pre-existing `SG-324-scratch`, `dispatch` only); scratch `output/SG-339-scratch/` and stray `frontend/output/` removed (verified `ls` rc before this report).

## Contract, UNCLEAR, REMAINING

- Contract: I received no contract version line.
- UNCLEAR: none.
- REMAINING: none.

## Criteria

- A1 — Preflight ran literally (socket listed, Server shown, busybox rc 0, health 200 start/end); phase seconds from stamps above; total ≈351 s inside 1100 s.
- A2 — G1 with file and line above; `PackEditor` amount-refresh premise confirmed at `AssetDetailPage.tsx:574-577`; every page using `ExpiryEntryForm` named (only `AssetDetailPage` production).
- A3 — T9, T10 FAIL before (`SG-339_fail.log`, 2 failed, row stays `Use by 6 May 2030`, no second list read) and PASS after (`SG-339_pass.log`, 10 passed); SG-338 STOP test red before (SG-338 `1 failed | 562 passed`), green after (23/23), quoted identical with empty diff proving unchanged.
- A4 — Gate green with exact counts (frontend 81 files / 565 tests, 0 failed; backend 817+2 / 2+6; eslint known-only; tsc clean; build rc 0); the four named files twice green (45×2).
- A5 — Frontend files only (comparison `git diff --name-only` lists only the two product files + logs); no backend/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/provider/container/deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before the report.
- A6 — Vacuity checked: failure looks like a row still showing the old date with `expected 1 to be greater than 1` (no second packs-list read) — seen in FAIL log; the tests assert the second list read grew AND the new text; the SG-338 test was not edited (empty diff); the suite is 0-failed, not a hidden deletion.
- A7 — See last line.

Verification: PASS
