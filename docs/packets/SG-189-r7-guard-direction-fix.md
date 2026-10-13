# SG-189 — R7: operator `_guard` direction fix (DRAFT, next session)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: DRAFT prepared 2026-10-13 from SG-182 G1 proof; scope-approved D10 (smallest reversible operator fix; may ride an operator grant). RE-REVIEW against the tree before dispatch next session.**
**DATABASE: none touched — all proof on scratch temp directories; production DB/storage never opened.**
**Restart: none. Autonomy: L2.**

## Why this exists

Proven defect F-SG182-1 on the ACTUAL helper: `backend/scripts/backup_restore_drill.py::_guard` rejects work==prod and prod-inside-work but ALLOWS work-inside-prod — the exact case its message claims to stop — so a drill storage destination can land inside its own copy source (recursive-copy shape, deliberately never executed). Twin search found no other `_guard`-style comparator in repo scripts (class count 1). Documented mkdtemp runbook form stays disjoint, so reachability is only via explicit `--work-dir` inside the storage root.

## G1 — Reject the missing direction, correct the message

Fix the condition to also reject work-inside-prod (`resolved in work.parents` alongside the existing cases) and correct the prod-inside-work message, which currently names the opposite geometry. Extend the helper's own cases (equal/parent/child/disjoint/missing) through the ACTUAL `_guard` on scratch directories — SG-182's `SG-182_probe_g1.py` guard cases are the regression shape, re-derived on target, not copied. The drill itself is never executed on the recursive shape (shape proof only, as in SG-182). README runbook invocation verified still disjoint after the change (read the invocation, do not reword the runbook unless it misstates the guard).

## Constraints and acceptance

- Write ceiling: `backend/scripts/backup_restore_drill.py` + its focused test(s) (`backend/tests/test_backup_drill.py` — extend, do not fork), `docs/worklogs/SG-189*`. No other operator script; no product route; no production run; no installs; no infra change.
- Proof on scratch temp dirs only; production DB/storage never opened for any access (the missing-DB STOP case is proven against a scratch nonexistent path, never a production path).
- ALL optional environment/Docker probes excluded; ANY privileged denial STOPS the whole slice.
- Ordinary commands 120s; focused tests 600s; no full suite; no watcher.
- Start/end health GET; contract 0.47.0 echo + source; base/Work-HEAD/settings/lane budget/deadline/elapsed.
- A1: all five geometries (equal / prod-inside-work / work-inside-prod / disjoint / missing) behave per the corrected contract through the ACTUAL helper, with messages naming the true geometry.
- A2: existing focused drill/runbook nodes still green (6 passed shape); runbook invocation still disjoint by reading.
- A3: FAIL-then-PASS — pre-change helper allows work-inside-prod (the SG-182 observation), post-change rejects; no placebo (cases call `_guard`, not a reimplementation).
- A4: first token SG-189; `docs/worklogs/SG-189_report.md`; FIRST READ / DURING EXECUTION / REMAINING with dispositions.

Guards: PG-EV-01/02/03/04/05/06/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10.

Receipt: commits `Dispatch-ID: SG-189`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-189 | Report: docs/worklogs/SG-189_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates before SG-190. No close or deploy in this slice.
