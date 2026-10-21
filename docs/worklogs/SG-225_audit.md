# SG-225 audit — first cutout probe: isolation passes, exact-label fidelity fails, correctly unlinked, rated 98

Immutable audit: base `bd1186a` → G1 `75830b9` (driver + live verify, no send) → work `7b138f1` (render + decision) → report `e717b2a` → receipt `bc07ee8` (transcript + mapped read-back; Work-HEAD e717b2a). Local `--ff-only` to the exact tip (`bc07ee8` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-225 exit=0`. Receipt note `Dispatch-ID: SG-225 | Report: docs/worklogs/SG-225_report.md` IS on the remote — own read-back finds `e717b2a` via `git log --notes`. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — tenth clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **RENDERED, isolation pass, faithfulness fail (image opened by this audit):** `SG-225_render_miso.jpg` (1195x896, 479,144 B, sha re-hashed == result) shows the VITASIA pack full-bleed on seamless white — isolation criteria met (white corners, positive margins, no props). The bottom-left word reads ERO7EN-shaped, not FROZEN, and the chicken badge is dark-red full-chicken vs the source's gold line-art head — matching the report's two measured defects (detail crops committed). Unlink decision recorded with reason; Miso keeps exactly its 3 prior links (`asset_evidence` 16→16).
- **Cutout-unused proved pre-send:** raw-sha 0 rows, data-URL-sha 1 row (the SG-219 scene row), cutout-brief-sha 0 rows — live ledger, not assumption. Request carries the real photo (decoded data URL sha == raw photo sha).
- **Money:** 1 POST, 200, credits `0.0`, upstream `0.068243`; pre-send projection 0.182717125 ≤ cap 1.02168 (unknown 0 post-SG-224); synthetic over-cap + no-authority refusals proven. D-20/D-14 held (today 0.341411/2.00, month 0.353848125/10.00). Pilot billed 4→5; 5 remain under D-27 counting, bulk authority D-29 stands by.
- **Scope:** 29 files — driver `backend/scripts/sg225_cutout.py` + `docs/worklogs/SG-225_*`; zero product/test bytes, no migration, no restart. Contract 0.50.0 live proof. Elapsed 779 s vs ≈600 s (review/crops phase; no command over 60 s; G-A9 uncalibrated).
- **Deviations, none deducted:** health start via `docker ps` + end probe `[200]` (no served-code change, disclosed); post-mode authoring iteration with zero new sends, failing transcript preserved; `response_id` null by product rule.
- **Secrets:** literal gate exit 1 EMPTY (pre + post-receipt); live-value key gate `matching_bytes=0` (1364/1365 + 22).

## Rating

**Holistic: 98/100, no flag.** The missing verdict now exists with measurements: isolation proven (white-ring minimums, margins, no-props), label-exactness disproven (two quoted defects with crops). The link decision applied the SG-218 lesson correctly — faithful-and-isolated links, anything else stays out with a reason. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used. Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| Cutout verdict (isolation pass, label fail) | Bulk cutouts wait on a better brief — finding for a future slice, never bulk-rendered blind |
| Miso cutout unlinked | Recorded with reason; Miso links unchanged (upload, transcript, scene) |
| Bulk scenes (D-29) | SG-226 dispatches same turn under L3 — remaining products, review-before-link, link faithful only |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
