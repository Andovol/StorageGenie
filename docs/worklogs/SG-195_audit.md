# SG-195 — Route error branches shipped, rated 98 (runner misfired on receipt classification, not a slice fault)

Immutable audit: base `7edf5f5` → work `f757ebd` (5 routes + 1 test module) → evidence `1f46266` (6 logs) → paste `5c99cd7`. Trigger exit 0; engine status `report_unreadable … reason=report_missing` (inactive) + engine partial note (`killed=exit_no_receipt`, `pushed=0`, `note=no`). Against that: the CODER's receipt note `Dispatch-ID: SG-195 | Report: docs/worklogs/SG-195_report.md | Work-HEAD: f757ebd…` IS on the remote (pushed 77d47bb..70c9417 in-slice, read back in-slice AND by this audit via direct show). The dual-annotation second note is missing (run ended before the post-report republish). Diagnosis: runner-side observation failure — the Coder published everything (work, evidence, report, note, pushes, read-backs, all committed with transcripts); the engine saw the paste tip (`head=5c99cd7`) yet recorded `note=no` / `report_missing`. Suspect: stale notes view or report-path check defect in the 0.50.0 run-coder rework — desk's to confirm (ISS-4). Per DISPATCH §2 the failure condition is receipt-based: receipt present → NOT failed. No re-trigger (replay would redo finished work); no debug slice (nothing failed).

Local `--ff-only` to the exact paste HEAD (`5c99cd7` == origin/automation). Scope: product diff exactly 6 files (+324/−12) + 7 worklog files; no backend/router/nav/state. No restart/deploy; no live interaction (jsdom-only, stated). Contract 0.50.0 == expectation, sha match.

Holistic rating: **98/100**, no flag. No slice-side deduction (attribution empty). The two withheld points name the unobserved visual layer — jsdom-only by packet design, no screenshots exist for `D425` — a scope limit, not a defect. `slowest_waste` = `none` (every committed leg's conclusion was used; no superseded leg).

## Evidence accepted

- A1: all five route hunks read in diff — `{query.isError && <div role="alert">Could not load <name>: …}` × 8, sibling shape mirrored; Catalog suppression + Capture replacement + text-only/no-refetch calls all inside constraints, decided+reported. Test module read in full (295 lines): real components/hooks, only api/client mocked; 8 error tests assert named alert + absence of old text; 9 controls assert unchanged paths + alert absence. FAIL genuine (8 failed/9 passed, `role="alert"` structurally absent on base); both runs committed.
- A2: diff within ceiling; census: EXPECTED 5 branched, none already-branched rebuilt, out-of-set reported-not-widened; `CO-101` independently re-verified by this audit (8 strings × {5 routes + test} only, 16 hits). Full frontend suite once: 29 files / 283 passed, exit 0. tsc + eslint clean. Backend untouched/unrun, stated.
- A3: 7 logs + report; 442 s vs ~600 s uncalibrated expectation (under); waste removal obeyed (no pre-commit gate; dev iteration disclosed); constraints answered; dispositions complete; first token SG-195.
- A4 (substance): Coder receipt present + read back twice; branch pushes complete. Caveat: dual note missing; engine classification dissents (ISS-4). Bound lane receipt used by the Coder; retired finalizer untouched.

## Dispositions

| Item | Destination |
|---|---|
| Route error branches (5 routes) | **RESOLVED** — 8 named alerts, tested |
| Out-of-set household queries (Catalog households/facets/saved-searches, Inbox/Analytics households) | SG-196 nav-context packet premises (household-scoped failure modes ride the nav slice) |
| zoom/touch/dark/auth-live + screenshots/driver; backend suite | Stand (later candidates; unrun by design) |
| ISS-4 runner `report_unreadable` misfire (receipt present, engine blind; 0.50.0 run-coder suspect) | Recorded here; desk relay owed at safe boundary; owner informed this turn. No re-trigger, no workaround |

Harness context-size reading unavailable; no conclusion made.
