# SG-164 — Merge Batch 4 (Q1/D-1012-1): #49 theming rewrite over #46, unserved

Autonomy: L2 (merge execution covered by D-1012-1; verdicts from SG-160). Last merge slice: re-derive #49's theming delta over the landed #46, nothing else. Unserved: the bundle change goes live on the SG-165 deploy rider, never here. `PB-1`–`PB-6` bind (`CODER.md` §14). Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0, `4c23869`); host echo expected 0.46.0 from /home/andrei/storagegenie-contract/VERSION (SG-163 echo) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.**
**Restart: none. Deploy: none** (unserved by design).

## Why this exists

SG-160 verdict + safe order put #49 (`palette/chat-form-keyboard-a11y-…`, head `33252132`) last: it duplicates #46's form wrapping (landed in SG-163) and adds theming + no test. THIS slice re-derives ONLY the theming delta over the current `ChatPage.tsx` (which carries #46): category select + both inputs + Send + Log-correction classes + cursor states, per #49's hunks. #49's head bytes are NEVER applied (they would clobber #46); the lockfile is never staged. Head SHA is an explicitly-labelled expectation — re-verify at execution; a moved head is a STOP, never a re-derive-around-it.

## G1 — re-derive #49 theming over landed #46

Write the theming fresh against the current `ChatPage.tsx`: keep #46's `<form onSubmit>` wrapping byte-intact (prove: #46's form hunks + Enter-submit test untouched and green), add exactly #49's class/cursor deltas. Prove per hunk: each theming hunk present, form structure unchanged, no lockfile in index or tree (three-way proof per SG-162 precedent).

## G2 — prove the merged file

Run `ChatPage.test.tsx` (must include #46's Enter-submit test — run it explicitly against the themed tree) and every other test file asserting on the touched symbols (grep and add every hit — a hit is a file). Plus the repo's static gates for the touched file. No full end-to-end sweep, no deploy, no restart.

## Constraints

Scope ceiling: ChatPage.tsx + `docs/worklogs/SG-164_*`; no test-file writes (ship no test — #49 ships none), no migration, no restart, no deploy. $0 — a metered call is a STOP-and-report. Expected duration ~600s (lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, test/lint 600s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling names exactly which file may change (and which must NOT be touched), and every criterion is satisfied inside it.

## Acceptance criteria

- A1: theming delta present per hunk + #46 form wrapping byte-intact (diff quoted) + lockfile absent.
- A2: ChatPage.test green INCLUDING the Enter-submit test + derived files green + static gates clean; any red is a STOP with output quoted (no drive-by fixes — report them).
- A3: diff file list == ChatPage.tsx + worklogs; test files or lockfile in the diff is a STOP.
- A4: SG-164 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); production writes: none (prove by diff file list + tip movement limited to this slice's commits).

## Report

Echo `SG-164` as the first token. Destinations: `docs/worklogs/SG-164_report.md` + test logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
