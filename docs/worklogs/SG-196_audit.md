# SG-196 — Nav household context + count shipped, rated 98 (runner misfired on receipt classification again, not a slice fault)

Immutable audit: base `04f1852` -> work `faea4d6` (G1+G2+G3, 21 files +565/-161) -> evidence `ce27175` (7 logs) -> paste `7843995`. Trigger exit 0; engine status `report_unreadable ... inactive reason=report_missing`. Against that: the CODER's receipt note `Dispatch-ID: SG-196 | Report: docs/worklogs/SG-196_report.md | Work-HEAD: faea4d6...` IS on the remote (pushed 3284f33..70d7ae3 in-slice, read back in-slice via mapped fetch AND by this audit via notes list + show). The dual-annotation paste note is missing (same construction as SG-195). Diagnosis: second instance of the ISS-4 runner-observation failure — the Coder published everything (work, evidence, report, note, pushes, read-backs, all committed with transcripts); the engine recorded `report_missing` while the paste commit sat on the branch. Per DISPATCH section 2 the failure condition is receipt-based: receipt present -> NOT failed. No re-trigger (replay would redo finished work); no debug slice (nothing failed).

Local `--ff-only` to the exact paste HEAD (`7843995` == origin/automation). Scope: product diff exactly 21 frontend files + 1 new test module + migration-required test edits; no backend/router structure/new routes. No restart/deploy; no live interaction (jsdom-only, stated). Contract 0.50.0 == expectation, sha match.

Holistic rating: **98/100**, no flag. No slice-side deduction (attribution empty). The interim control-coupling episode was caught by the slice's own FAIL half and repaired once, amended unpushed (CO-54) — the FAIL half working as designed, not a needless loop. `slowest_waste` = `none` (every committed leg's conclusion was used).

## Evidence accepted

- A1: `HouseholdContext.tsx` read in full (56 lines) — single `useHouseholds`, localStorage-first + first-fallback + auto-persist rail, memoized value, guarded consumer hook. `App.tsx` migration + nav selector/badge/alert read in diff. New test module read in full (264 lines): real App/routes/context/hooks, only api/client mocked; 8 prove rows assert single fetch, in-session propagation, fresh-mount persistence, nav alert, badge count/name, honest zero, facets + saved-searches alerts; 5 controls assert absence on loaded/pending paths. No placebo — every row drives its failure path through the mocked api seam. FAIL genuine (8 failed/5 passed on base, structural reasons quoted, sha-equal module, both runs committed per PG-EV-09). Existing-test edits verified assertion-preserving (no removed expect/it/test/describe lines in the test diff; mock-shape + provider wrappers only, preserved behavior named in-code).
- A2: census log read — base 10 `useHouseholds(` lines (= 9 product sites + 1 hook definition, matching the packet's EXPECTED 9 + AppHeader outlier reported-not-widened); target 3 (definition + provider + AppHeader, same cache key, one network request). isError census: new = provider/nav + Catalog facets + saved-searches; Capture/Planning re-sourced to context (reported-not-rebuilt); nothing else widened. Full frontend suite once on candidate: 30 files / 296 passed, exit 0 (own count: SG-195's 283 + 13 new). tsc + eslint exit 0 at work HEAD. Backend untouched/unrun, stated.
- A3: 7 logs + report; 816 s vs ~900 s uncalibrated expectation (under); constraints answered; dispositions complete; first token SG-196.
- A4: WORK receipt present + read back twice; branch pushes complete (04f1852..ce27175, paste after). Caveat: dual paste note missing; engine classification dissents (ISS-4 2nd instance). Bound lane receipt used by the Coder; retired finalizer untouched.

## Dispositions

| Item | Destination |
|---|---|
| Shared context + nav selector/badge/alert + Catalog branches | **RESOLVED** — 1 provider query, propagated selection, named alerts, honest badge |
| AppHeader outlier (own useHouseholds, same cache key) + ReviewPage inline review-tasks query | Follow-up micro-slice candidate (both reported-not-widened by the ceiling) |
| zoom/touch/dark/auth-live + backend suite | Stand (unrun by design; SG-190 REMAINING leftovers) |
| Runner `report_unreadable` misfire, 2nd instance (receipt present, engine blind) | Recorded here; desk #84 follow-up owed at safe boundary; owner informed this turn. No re-trigger, no workaround |

Harness context-size reading unavailable; no conclusion made.
