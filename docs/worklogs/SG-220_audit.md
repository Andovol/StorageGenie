# SG-220 audit — D-27 pilot render 3 of 10 RENDERED (Costiță-2, asset-specific block cleared), rated 98

Immutable audit: base `bb4e19b` → G1 `b2129a8` (driver + live pick confirmation + triple-bound proof, no send) → work/report `1001489` → receipt `9c75a35` (transcript + mapped read-back; Work-HEAD 1001489). Local `--ff-only` to the exact tip (`9c75a35` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-220 exit=0`. Receipt note `Dispatch-ID: SG-220 | Report: docs/worklogs/SG-220_report.md` IS on the remote — own read-back finds `1001489` via `git log --notes`. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — fifth clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **RENDERED (independently read):** `SG-220_render3_result.json` = status `rendered`, HTTP 200, Evidence `01a15ff5-11e3-…`, ledger `01a15ff5-11ec-…`, 664,184 B JPEG sha256 `f3d56bfb…` — matches the committed `SG-220_render3.jpg` byte-for-byte (re-hashed by this audit). Opened by this audit: BARONI vacuum-packed Costiță de porc on a wooden counter, printed label + barcode `2 501242 004372` legible, props outside the label area, no people, no PII. Asset faithfulness high; scene quality high — concurring. SG-219's RECITATION block was asset-specific (CEAFĂ); this asset rendered first try.
- **Pick confirmed live:** Costiță-2 (evidence `01a0c4a1-acbd-…`, 565,806 B, sha `63b3ec70…`) re-verified pilot-unused via live ledger query over both raw and data-URL hashes (0 rows pre-send); CEAFĂ never selected (driver's fixed pick cannot equal the parked id; request body carries only the Costiță-2 data URL).
- **Money:** authority cap = min(daily 2.00, monthly 9.98756288, pilot 8×0.17028=1.36224) = 1.36224; guard inputs live (spent 0.012437125, 5 unknown-cost rows, worst 0.17028) → projection 1.03411713 ≤ 1.36224 `proceed`. Synthetic over-cap + no-authority refusals proven. Actual: credits `0.0`, upstream `0.068229` — under on both accountings; daily 0.204669/2.00, monthly 0.217106125/10.00, pilot 3/10 billed. One POST total.
- **DB post-state:** evidence 20→21, provider_call 32→33, audit_event 93→94, null-cost 5→5, known sums unchanged. Exactly 1 new row of each kind, ids quoted, left in place; no UPDATE/DELETE.
- **Scope:** 24 files — driver `backend/scripts/sg220_render.py` + `docs/worklogs/SG-220_*`; zero product/test bytes, no migration, no restart. Contract 0.50.0 live proof. Elapsed 281 s vs ≈600 s; render 9.3 s vs 300 s bound.
- **Secrets:** literal gate exit 1 EMPTY (output outside the glob — SG-219's lesson applied); live-value key gate `matching_bytes=0` (1248 + 17 files).

## Rating

**Holistic: 98/100, no flag.** The left-over pick rendered exactly as the packet drew it: live pick confirmation, inherited driver fix intact, triple-bound proof with the grown unknown-cost count, both accountings quoted, CEAFĂ untouched. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used. Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| Pilot 3/10 billed RENDERED | D-27 continues — 7 of 10 billed remain |
| CEAFĂ parked (RECITATION) | Unchanged — content-policy fork for a future decision, never in-slice work |
| Resolution pin / cutout / UI wiring / routing | Parked — each needs its own owner word |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
