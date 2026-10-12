# SG-161 — Merge Batch 1 (Q1/D-1012-1): land #43 + #45 by real hunks, unserved

Autonomy: L2 (merge execution covered by D-1012-1; verdicts from SG-160). Applies two audit-clean outside PRs onto `automation`. Unserved: the bundle change goes live on the SG-165 deploy rider, never here. `PB-1`–`PB-6` bind (`CODER.md` §14). Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0, `4c23869`); host echo expected 0.46.0 from /home/andrei/storagegenie-contract/VERSION (SG-160 echo) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.**
**Restart: none. Deploy: none** (unserved by design).

## Why this exists

SG-160 audited 7 outside PRs (MERGE 3 / REWRITE 4) with an overlap matrix and safe order. THIS slice lands the two independent clean merges first, oldest first: #43 (`palette/expiry-form-ux-…`, head `6d34e6e9`, ExpiryEntryForm double-submit guard + tooltip + focus-ring) and #45 (`jules-4728848117784794832-…`, head `3676e69f`, AssetImportModal aria-busy + spinner). Head SHAs are an explicitly-labelled expectation — re-verify each head at execution (heads may move); a moved head is a STOP, never a rebase-and-continue. The remaining verdicts (#44, #46, #47, #48, #49) ride later slices, never this one.

## G1 — apply both heads by real hunks

Land #43 + #45 onto the resolved base so the merged files carry the PRs' hunks blob-identical (cherry-pick, patch application, or manual hunks — decide and report; prove equivalence per hunk, quoting blob SHAs or an empty residual diff). Both merge-trees were clean vs automation at audit (SG-160 merge-tree proof) — re-prove at execution; any conflict is a STOP.

## G2 — prove the merged files

Run the affected suites: `ExpiryEntryForm.test.tsx` + `shell/import-modal.test.tsx` and every other test file asserting on the touched symbols (grep the test tree for the changed component names and add every hit — a hit is a file). Plus the repo's static gates for the touched files (`npm run lint`, `tsc --noEmit` or the Makefile equivalents — read them, do not inherit my names). No full end-to-end sweep, no deploy, no restart.

## Constraints

Scope ceiling: the two component files + `docs/worklogs/SG-161_*`; no migration, no restart, no deploy, no served-code activation (bundle lands on disk, goes live on SG-165). $0 — a metered call is a STOP-and-report. Expected duration ~600s (lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, test/lint 600s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling names exactly which files may change, and every criterion is satisfied inside it.

## Acceptance criteria

- A1: both heads applied with blob-identical proof quoted per PR (head SHA + equivalence evidence).
- A2: affected test files green + static gates clean; any red is a STOP with the failing output quoted (no drive-by fixes of unrelated reds — report them).
- A3: diff file list == the two component files + worklogs; anything else is a STOP.
- A4: SG-161 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); production writes: none (prove by diff file list + tip movement limited to this slice's commit).

## Report

Echo `SG-161` as the first token. Destinations: `docs/worklogs/SG-161_report.md` + test logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
