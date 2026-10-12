# SG-160 — Palette PR audit (Q1/D-1012-1): 7 outside PRs, per-PR verdicts, read-only

Autonomy: L2 (Q1 approval covers audit + merge approach; merges wait on this slice's verdicts — checkpoint premise). Read-only audit: NO merges, NO branch moves, NO product code, $0. `PB-1`–`PB-6` bind (`CODER.md` §14). Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0, `4c23869`); host echo expected 0.46.0 from /home/andrei/storagegenie-contract/VERSION (SG-159 receipt echo) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.**
**Restart: none.**

## Why this exists

7 outside (Palette-agent) PRs sit open against `automation`, oldest first (all by Andovol, measured 2026-10-12 via `gh pr list` — re-verify heads at execution, they may have moved): #43 `palette/expiry-form-ux-7564726511398990958` (2026-09-29, ExpiryEntryForm feedback/focus) · #44 `palette/evidence-gallery-a11y-2144200342385872131` (2026-09-30, EvidenceGallery a11y) · #45 `jules-4728848117784794832-06f7c3a6` (2026-10-01, import-modal spinner/aria-busy) · #46 `palette/chat-form-keyboard-submit-4794394533623248732` (2026-10-02, Chat keyboard submit) · #47 `palette/candidate-card-button-ux-764280013337970784` (2026-10-03, CandidateCard buttons) · #48 `palette-candidate-card-ux-1280568577076363185` (2026-10-04, CandidateCard action UX) · #49 `palette/chat-form-keyboard-a11y-14397128668786279135` (2026-10-05, ChatPage keyboard/a11y). The branch refs above are an explicitly-labelled expectation — enumerate the set on the target (criterion: all open PRs against `automation` not created by our dispatches) and report the difference either way.

## G1 — fetch all 7 diffs as bytes

Fetch each PR head + its diff against the merge base. Quote head SHA + base SHA per PR. A fetch that silently yields an empty diff is a finding, not a pass.

## G2 — per-PR audit verdicts

Audit each diff as a Coder report: WHAT it changes (files, hunks), whether it is sound (tests, a11y claims verified against code, no scope smuggling), and exactly one outcome per PR — **MERGE** (audit-clean, land as-is) / **REWRITE** (idea sound, diff not — say what the slice must do) / **CLOSE** (one-line reason). Per G-L7 each audited PR also names its defect lesson: the defect (if any) and why our packets, tests and audit let it through. No verdict may rest on a file you did not read.

## Constraints

Scope ceiling: `docs/worklogs/SG-160_*` ONLY — report + fetch transcript. Any diff outside worklogs is a STOP. No product hunks, no branch moves, no merges (merges ride later slices on these verdicts), no live calls of any kind ($0 — a metered call is a STOP-and-report). No served-code change → no refresh (D145). Secrets: none touched. Expected duration ~600s (lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, one PR fetch 300s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling forbids every write except worklog files, and every criterion is satisfied by worklog files. Full suite does NOT run (nothing to verify — derived-set block not pasted, PB-7 not named).

## Acceptance criteria

- A1: 7/7 PR diffs captured with head + base SHAs quoted; any empty diff reported loudly, never passed silently.
- A2: verdict table with 7 rows (MERGE / REWRITE / CLOSE + one-line reason each) + defect lesson per PR.
- A3: START tip == END tip proven (no branch movement); tree clean at end except worklog files.
- A4: SG-160 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); production writes: none (prove by clean tree + tip equality, both directions).

## Report

Echo `SG-160` as the first token. Destinations: `docs/worklogs/SG-160_report.md` + fetch transcript. Close with FIRST READ / DURING EXECUTION / REMAINING.
