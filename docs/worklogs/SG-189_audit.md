# SG-189 — R7 guard direction fix, three-way split, clean proof

Immutable audit: base `b4a995312aabe927ec108d871cd5531fc8b2abe4` → work `02f1214` (drill script + its test only) → evidence `908430b` → report `57a202b`. Forced-command status at end: `result=done id=SG-189 exit=0`; status verb after: `result=reject reason=replay` (correct: receipted). Mapped notes fetch read the receipt; settings envelope-sourced (command). Local pulled `--ff-only` to the exact report HEAD. Scope diff: `backup_restore_drill.py` (+6/−1, `_guard` only) + `test_backup_drill.py` (+51/−2, five geometries through the ACTUAL helper); 10 worklogs. No product route, no other script, no production open (not even ro), no installs.

Holistic rating: **97/100**, no flag. Contract 0.47.0 echoed verbatim.

## Evidence accepted (re-read in the diff)

- The product hunk is exactly the packet G1: equal → "equals" message; prod-inside-work → corrected "is inside work-dir" message; work-inside-prod (`resolved in work.parents`) → NEW rejection with the true geometry. Missing + readability arms untouched; signature and mkdir side effect unchanged.
- The equality split beyond the literal ask is inside A1's letter (every rejection names its true geometry — the old shared message also misnamed identity) and is disclosed with an accepted-set diff (CO-18: only work-inside-prod left the accepted set, intended). No scope creep.
- FAIL leg genuine: candidate test bytes sha256-verified equal across trees; base shows the two wrong-message mismatches plus DID NOT RAISE on work-inside-prod (3 failed, 5 passed). PASS: probe candidate 9/9, focused 11/11 (8 drill nodes + 3 runbook nodes, runbook invocation still disjoint by reading, not reworded).
- CO-101 cross-check done right: SG-182's committed probe re-run, 22 checks, the single fail IS the dated pre-fix expectation (inversion itself) — quoted message proves the fix rather than hiding behind it.
- Twins: `in .*parents` class count reconfirmed 1; jobs.py:116 is a different construct on a product route — reported, untouched, queued post-SG-190 per packet design.
- Nothing breached, mismatched, looped or denied (no privileged op attempted → PB-2 path never reached, correctly not claimed as tested).

## Dispositions

| Item | Destination |
|---|---|
| F-SG182-1 (guard direction + messages) | **RESOLVED** — both directions + equality rejected, true-geometry messages, 5-geometry tests through the actual helper |
| jobs.py:116 cursor twin | Still queued post-SG-190 micro-slice (unchanged) |
| SG-182 probe artifact's dated expectation | Left as history (correct — the re-run log documents the inversion) |
| Serve | Normal deploy course, not this slice |

Harness context-size reading unavailable; no conclusion made.
