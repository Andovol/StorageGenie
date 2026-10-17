# SG-205 audit — D-8 Option B shipped: dark focus-ring 1.7559 → 7.4784, light byte-identical, rated 98

Immutable audit: base `5db6cde` → BEFORE evidence `418bf7b` (driver copy sha `f1bb9890`, before result/log, 2 shots) → work `ec9cd6c` (product fix + after result/log, controls, tests log, worklog, 2 shots) → scope proof `53eb77a` → report `40ccdff` (+health) → receipt transcript `0834ce7`. Local `--ff-only` to the exact report HEAD (`0834ce7` == origin/automation); tree clean. Trigger exit 0; engine status `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-205 | Report: docs/worklogs/SG-205_report.md | Work-HEAD: ec9cd6c...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit, remote notes tip `5d43d9d` re-read by ls-remote (tip advanced past the transcript's `d190e3b` by runner partial-receipt notes; the Dispatch-ID note resolves at the current tip). Per `DISPATCH.md` §2 the failure condition is receipt-based: receipt present → NOT failed. **Eighth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed independently, never copied from the report)

- **A1 product diff** (`5db6cde..ec9cd6c -- frontend/`): ONLY `frontend/src/theme/tokens.css`, +9/−2 — the two outline declarations `.focus-ring:focus-visible` and `.file-pick:focus-within` take `hsl(var(--link))` instead of `hsl(var(--primary))`, plus a 5-line rationale comment. Exactly the authorised shape (G1 + same-file sibling rule).
- **A1/A3 BEFORE→AFTER** (parsed `SG-205_measure.json` + run logs, not the report's §(c)): BEFORE dark `worstSurrounding 1.7559` gate FAIL (run log `focusGateVerdicts light1440:PASS,dark1440:FAIL`, `errors` carries the 2 floor violations); AFTER dark `worstSurrounding 7.4784`, `worstOwnFace 4.2589`, all-meet true, gate PASS both worlds; light `9.4611` both runs, own-face 1.0 on the active primary pills — disclosed baseline, unchanged from SG-203 (ring separated by the 2px offset gap; the packet gated dark own-face, met at 4.2589). Gate arms: the planted below-floor inputs are seen FAILING in BOTH runs (`mustFailObserved true` before and after — `PG-EV-01` holds in the passing run too); boundary 3.0 met, 2.9999 fails, wrong-expectation not-held. Non-vacuous: 2 worlds × 30 stops × 2 runs + 2 file-pick probes + arms; measure 214,603 B on disk (size as stated).
- **Alpha robustness** (checked, immaterial): the driver alpha-composites the ancestor chain (`SG-205_driver.mjs:305-310`); every sampled ring/background colour is opaque `a:1` with no image backdrop. Margins (7.4784 vs 3.0 floor; 1.7559 before) are unflippable by compositing.
- **Light no-regression** (triple-proved, not asserted): stop-by-stop identical ratios in the measure; computed colour identical (`rgb(110,48,46)` both runs — light `--link` == light `--primary` by token value); the two light shots byte-identical (`b4025663b423` both, re-hashed here). Dark shots differ (`6c6164e7` → `54c4af60`).
- **A2 enumeration**: `rg -l focus-ring frontend/src` = 28 files (tokens.css + 23 consumers + 4 tests) — delta 0 in either direction vs the packet's expectation; outline declarations tree-wide = tokens.css only (both rules); served bundle carries both rules (quoted in build log); real-page traversal 30/30 stops ring-class both themes, 0 unclassed. Sub-floor non-`.focus-ring` outside tokens.css: none found. File-pick: dark 1.5816/1.9517 → 6.7361/8.312 in the same slice per the packet's sibling rule; light unchanged.
- **A3 logs**: suite `Test Files 30 passed (30) / Tests 298 passed (298)`, rc=0 (`SG-205_tests_frontend.log:92-93`); controls 26/26 exit 0 (`controlFailures 0`, transport POST-rejected/`serverSawPost false`); health start `ok/ok/ok` → end identical, delta none; elapsed 399 s of `RUN_BUDGET_S=2100` (19.0%) vs packet ≈750 s (under, stated `G-A9`); no command over 120 s (longest evidence: 22 s controls); JS bundle byte-identical base↔candidate (`626d1038` both — the change cannot have touched behaviour outside the two outlines).
- **A4 receipt**: bound lane notes-ref; `add` + push (`6a37d62..d190e3b`), mapped-fetch read-back `show_exit=0`, first line exact, Work-HEAD recorded; report + receipt-log commits pushed. Retired finalizer not used.
- **Contract chain**: recorded 0.50.0 == published 0.50.0 (`G-L1` CLEAN ×3 this session) == host copy (Coder read `/home/andrei/storagegenie-contract/CODER.md:3` live, VERSION 0.50.0, no unbound `{{NAME}}`) == echoed receipt line. Controlled axis equal; no delta.

## Images — all 4 opened by this audit (D425)

| Shot | Disposition |
|---|---|
| before_dark | ring around the focused pill dark-on-dark, barely visible — matches 1.7559 |
| candidate_dark | same control, clearly visible light halo, no artifacts — matches 7.4784 |
| before_light / candidate_light | same frame, dark-red ring on light — mutually identical, no clipping/overlap/data anomaly |

UI + layout + data clean on all 4; masking intact (no legible PII in the close-ups).

## Rating

**Holistic: 98/100, no flag.** Zero audit findings: every independently parsed number matches the report; scope proved by artifact not exit code; light identity triple-proved; arms seen failing in the passing run; no rework, no retry, well under budget. Not 100: per-route traversal beyond Catalog (+file-pick /capture) is stated-not-claimed, so perfection is unprovable. `deduction_attribution`: empty (nothing deducted). `slowest_waste`: `none` (recon/driver, runs, evidence/commit/report — every phase's output used). Guards: PG-EV-01/02/03/05/08/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-03/04.

## Dispositions

| Item | Destination |
|---|---|
| D-8 Option B shipped + served state (tokens.css live only after serve) | **SG-206 serve rider next** (D-5 re-serve due — this slice's product commit) |
| Option C native-button faces | OPEN (D-8 not approved) — may be re-proposed; not re-measured here |
| Option D width-adaptive default | Needs an owner requirement first — untouched |
| Non-Catalog routes not keyboard-traversed | Stated REMAINING; the class inventory is tree-verified, per-route traversal unclaimed — a named next slice only if the owner wants it |
| Runner `report_unreadable` misfire, **8th instance** | Desk #84 (no re-trigger); receipt-based condition held |
| Q1 Raw Data removal (owner: "I don't need it") | **D-12 → SG-207 packet drafted this turn**, dispatched after SG-206 |
| Q3 single-household + selector removal | **D-13 → SG-208 packet drafted this turn**, dispatched after SG-206/207 |
| Q2 AI stages push | **D-14; D7 detail answered in chat this turn** (quota/pick/spend-cap owed by owner) |
| D-10 auto-hide proposal | SUPERSEDED by the Q3 removal directive |
| Auth-live + live-container; native zoom/touch | Blocked / emulated-only, stated |

Harness context-size reading unavailable; no conclusion made.
