# SG-163 — Merge Batch 3 (Q1/D-1012-1): #47 rewrite over #48 + #46 minus lockfile, unserved

Autonomy: L2 (merge execution covered by D-1012-1; verdicts from SG-160). One rewrite (re-derived over the landed #48) plus one REWRITE-minus-smuggled-file. Unserved: the bundle change goes live on the SG-165 deploy rider, never here. `PB-1`–`PB-6` bind (`CODER.md` §14). Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0, `4c23869`); host echo expected 0.46.0 from /home/andrei/storagegenie-contract/VERSION (SG-162 echo) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.**
**Restart: none. Deploy: none** (unserved by design).

## Why this exists

SG-160 verdicts + safe order put these two next: #47 (`palette/candidate-card-button-ux-…`, head `742e1875`) re-expressed OVER the landed #48 version — same 5-button restyle but using the shared `CONTROL_STYLE` / `THEMED_CONTROL_CLASS` exports (CatalogToolbar, verified at base) instead of #47's hardcoded literals, KEEPING #47's only unique value (the blocked-Accept `<span title>` tooltip); and #46 (`palette/chat-form-keyboard-submit-…`, head `78cf8e42`) MINUS `frontend/pnpm-lock.yaml` (ChatPage form wrapping + Enter-submit test). Head SHAs are an explicitly-labelled expectation — re-verify each head at execution; a moved head is a STOP, never a rebase-and-continue. #49 rides SG-164 over #46, never here.

## G1 — rewrite #47 over landed #48; apply #46 minus lockfile

#47: do NOT apply the head's bytes — write the restyle fresh against the current `CandidateCard.tsx` (which carries #48): shared constants for all 5 buttons, tooltip span kept. Prove: no hardcoded `bg-primary`/`bg-card`/`text-primary-foreground`/`border-border` literals remain in the button block (grep quoted), the tooltip exists, and the visual result matches #47's intent per hunk. #46: selected-paths apply of `ChatPage.tsx` + `ChatPage.test.tsx` ONLY (lockfile never staged); prove landed blobs equal the head's corresponding blobs exactly + lockfile absent (three-way proof per SG-162 precedent). Re-prove clean merge-trees at execution; any conflict is a STOP.

## G2 — prove the merged files

Run `CandidateCard.test.tsx` + `ChatPage.test.tsx` and every other test file asserting on the touched symbols (grep and add every hit — a hit is a file). Plus the repo's static gates for the touched files. No full end-to-end sweep, no deploy, no restart.

## Constraints

Scope ceiling: CandidateCard.tsx + ChatPage.tsx + ChatPage.test.tsx + `docs/worklogs/SG-163_*`; no migration, no restart, no deploy. $0 — a metered call is a STOP-and-report. Expected duration ~600s (lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, test/lint 600s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling names exactly which files may change (and one file that must NOT appear), and every criterion is satisfied inside it.

## Acceptance criteria

- A1: #47 re-expressed on shared constants (no hardcoded literals in the button block, tooltip present, per-hunk intent quoted) and #46-minus-lockfile blob-identical (equivalence + absence proofs quoted).
- A2: affected test files green + static gates clean; any red is a STOP with output quoted (no drive-by fixes — report them).
- A3: diff file list == the named files + worklogs; `pnpm-lock.yaml` anywhere in the diff is a STOP.
- A4: SG-163 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); production writes: none (prove by diff file list + tip movement limited to this slice's commits).

## Report

Echo `SG-163` as the first token. Destinations: `docs/worklogs/SG-163_report.md` + test logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
