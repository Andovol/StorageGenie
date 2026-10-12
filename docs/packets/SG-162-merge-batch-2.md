# SG-162 — Merge Batch 2 (Q1/D-1012-1): #44 minus lockfile + #48, unserved

Autonomy: L2 (merge execution covered by D-1012-1; verdicts from SG-160). Lands one REWRITE (minus smuggled file) plus one clean MERGE, both independent files. Unserved: the bundle change goes live on the SG-165 deploy rider, never here. `PB-1`–`PB-6` bind (`CODER.md` §14). Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0, `4c23869`); host echo expected 0.46.0 from /home/andrei/storagegenie-contract/VERSION (SG-161 echo) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.**
**Restart: none. Deploy: none** (unserved by design).

## Why this exists

SG-160 verdicts + safe order put these two next (oldest first): #44 (`palette/evidence-gallery-a11y-…`, head `03304b13`: EvidenceGallery a11y fix + first test + `.jules/palette.md`, MINUS the smuggled `frontend/pnpm-lock.yaml`) and #48 (`palette/candidate-card-ux-…`, head `33f079f3`: CandidateCard restyle via shared constants, whole head). Head SHAs are an explicitly-labelled expectation — re-verify each head at execution; a moved head is a STOP, never a rebase-and-continue. #47's rewrite lands over #48 in SG-163, never here.

## G1 — apply #44-minus-lockfile + #48 by real hunks

Land #44 WITHOUT `frontend/pnpm-lock.yaml` (cherry-pick then excise, or selected-paths apply — decide and report): prove the landed component + test + journal bytes equal the head's corresponding blobs exactly, AND prove the lockfile is absent (no `pnpm-lock.yaml` added, no second lockfile in the tree). Land #48 whole: landed blob equals head blob exactly. Re-prove clean merge-trees at execution; any conflict is a STOP.

## G2 — prove the merged files

Run the affected suites: the newly-landed `EvidenceGallery.test.tsx` + `CandidateCard.test.tsx` and every other test file asserting on the touched symbols (grep and add every hit — a hit is a file). Plus the repo's static gates for the touched files. No full end-to-end sweep, no deploy, no restart.

## Constraints

Scope ceiling: EvidenceGallery files + CandidateCard.tsx + `.jules/palette.md` + `docs/worklogs/SG-162_*`; no migration, no restart, no deploy. $0 — a metered call is a STOP-and-report. Expected duration ~600s (lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, test/lint 600s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling names exactly which files may change (and one file that must NOT appear), and every criterion is satisfied inside it.

## Acceptance criteria

- A1: #44 landed minus lockfile (per-blob equivalence quoted + lockfile-absence proven) and #48 blob-identical (head SHA + equivalence quoted).
- A2: affected test files green + static gates clean; any red is a STOP with output quoted (no drive-by fixes — report them).
- A3: diff file list == the named files + worklogs; `pnpm-lock.yaml` anywhere in the diff is a STOP.
- A4: SG-162 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); production writes: none (prove by diff file list + tip movement limited to this slice's commits).

## Report

Echo `SG-162` as the first token. Destinations: `docs/worklogs/SG-162_report.md` + test logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
