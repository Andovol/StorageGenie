# SG-256 audit — 96 (row-11 polish landed: an opened date is editable and clearable; the deploy rider is next)

**Verdict:** 96, no flag. **Deduction attribution: mixed** — the packet's ≈300 s expectation was low, and the report's phase accounting leaves the base-checkout/recon time unnamed. The work itself is complete, the new tests drive the real paths, and both gates are green.

## What was read

The full product diff `4942b37..b3c18f3` (7 files, +429/−1), the test additions, the report, every SG-256 log, the receipt on the notes ref, and the base/current suite logs the report cites. The scope diff `4942b37..405625e` is exactly the seven named product files plus `docs/worklogs/SG-256*`.

## What landed

| Item | Evidence | Verdict |
|---|---|---|
| Clear action through the one write path | `expiry_tracker.py` adds `clear_opened_date`: same category/classification guards; no active date = no-op; otherwise `_write_assertion(..., None, ...)` supersedes the date and writes the audit row | PASS |
| Clear route with the existing guards | `plugins.py` adds `POST /assets/{asset_id}/opened/clear`, reusing `_plugin`, `_asset`, `_error`; returns `{asset_id, assertion}` (null on the no-op) | PASS |
| One active null assertion; old date preserved | `SG-256_g3_backend_pass.log` (21 passed); `test_clear_supersedes…` asserts the superseded date, one active null, and a null countdown row | PASS |
| Audit row | `test_clear_leaves_an_audit_row…` asserts `after.value is None`; the `before.review_state` is the observed `superseded` (I3) | PASS |
| No-op writes nothing | `test_clear_without_an_opened_date_is_a_no_op`: 200, `assertion: null`, assertion count 0, audit count unchanged | PASS |
| Guards | `test_clear_uses_the_same_category_and_asset_guards`: 422 non-tracking, 422 unclassified, 404 unknown, 403 mismatch; the dated asset stays accepted | PASS |
| UI Edit and Clear | `OpenedCountdownSection.tsx`: Edit pre-fills the current date, Save reuses `recordOpenedDate`, Clear calls `clearOpenedDate`; both invalidate the same query; the no-date form is unchanged | PASS |
| Frontend tests drive the real controls | `SG-256_g3_frontend_pass.log` (8 passed); on base the same file gives 3 failed / 5 passed — the controls, edit and clear cases fail for the intended reason | PASS |
| FAIL-then-PASS | `SG-256_g3_backend_fail.log` (4 failed / 17 passed; the 4 clear tests); `SG-256_g3_frontend_fail.log` (3 failed / 5 passed) | PASS |
| Gates | `SG-256_g4_backend_gate.log`: host **748 passed, 2 deselected, 0 failed** in 68.94 s, image proof **2 passed**, rc 0; `SG-256_g4_frontend_gate.log`: **30 files / 310 tests**, rc 0 | PASS |
| Docker preflight / health | `SG-256_g0_docker_preflight.log`: Server 29.9.2, busybox rc 0; `SG-256_health.log`: 200 before and after, same body | PASS |
| Scope | 7 product files + SG-256 evidence only; no schema, migration, model, Dockerfile, compose, lockfile, dependency, database, host, provider, container or deploy byte | PASS |
| Receipt | notes ref `refs/notes/storagegenie-coder-reports`, `Dispatch-ID: SG-256`, `Work-HEAD: 405625e`, settings line, contract echo `0.53.0` | PASS |

## Issues and dispositions

| ID | Issue | Status |
|---|---|---|
| I1 | **Report accounting:** elapsed 540 s against the ≈300 s expectation, but the named phases account for ~150 s; the base-checkout/recon time is not broken out, and the report's "each under 60 s" is inconsistent with its own timestamps (frontend FAIL at 21:10:28 after a 21:06:58 lane start). The work and the elapsed are honestly stated; the estimate was the packet's. | **CLOSED — no action.** The elapsed is within this lane's recent range (SG-252 468 s, SG-255 447 s, SG-240 1504 s); the next packet carries a realistic expectation. No code or report rework. |
| I2 | The packet said the pre-change clear path answers 404; the base answered **405** (the path exists with no route). The new tests still fail for the intended reason (no clear action), recorded in the FAIL log. | NOT A DEFECT — packet premise corrected in the record; the discriminating test outcome is unchanged |
| I3 | The unchanged `_write_assertion` records `before.review_state` as `superseded` (it flips the previous row before writing the audit). The old date itself is preserved in the superseded assertion, which the test asserts. | NOT A DEFECT — pre-existing audit semantics, out of this slice's scope; the value is preserved |
| I4 | Targeted ruff/eslint ran; repo-wide lint was not run because the project records pre-existing mypy and eslint reds. | NOT A DEFECT — parked by the owner |
| I5 | The live container was not touched; health 200 at start and end; the deploy is the separate rider. | CLOSED — no deploy in this slice |

Every `UNCLEAR` line is dispositioned above: `FIRST READ` the 404/405 premise (I2); `DURING EXECUTION` the audit `before` state (I3) and the image's existing build (no issue); `REMAINING` no open product item; the deploy rider is SG-257.

## Below-95 investigation (`RATING_ISSUE.md`)

Not loaded: score 96, no flag. The deductions are the packet's low duration expectation and the report's unbroken-out setup time; neither is a correctness or safety finding.

## Rating row inputs

`guards_invoked`: PG-EV-01, PG-EV-02, PG-EV-03, PG-EV-05, PG-EV-09, PG-IC-01, PG-IC-07, PG-IC-08, PG-IC-09, PG-SC-01, PG-SC-02, PG-SC-12, PG-DP-04, PG-PR-03, PG-PR-04, PG-PR-06.
`remaining`: (1) the deploy rider **SG-257** serves the seven-file delta and records the release; (2) the root-owned `~/.docker` remains an engine-arc item, so `DOCKER_CONFIG`/`DOCKER_HOST` stay required; (3) the household-and-document half of roadmap row 11 remains, not in this plan.
`slowest_waste`: none — every named phase's output (both FAIL logs, both gates, the image proof, health) was used by this audit.
`escape`: empty.
