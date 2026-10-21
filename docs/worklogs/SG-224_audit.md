# SG-224 audit — D-30: 5 stale null-cost rows classified (per-row proof), guard wall clears, rated 98

Immutable audit: base `e31829a` → work `eda34e9` (driver + 5 UPDATEs + all proof) → report `813febc` → correction `c1e5e8b` → receipt `56fd385` (transcript + mapped read-back; Work-HEAD c1e5e8b). Local `--ff-only` to the exact tip (`56fd385` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-224 exit=0`. Receipt note `Dispatch-ID: SG-224 | Report: docs/worklogs/SG-224_report.md` IS on the remote — own read-back finds `c1e5e8b` via `git log --notes`. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — ninth clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Exactly the 5, each `changes()=1` (independently read):** `SG-224_proof.json` names all five ids (2×404, 2×429, 1×400 CEAFĂ) with bodies carrying zero usage/cost keys; `SG-224_write_log.json` shows one transaction, `committed=true`, `rolled_back=false`; `SG-224_post_state.json` carries revert-hash equality (`revert_five_costs_equals_pre_snapshot`), `other_rows_changed=0`, and full per-table counts identical except the 5 cost cells. No INSERT, no DELETE, no other UPDATE.
- **Wall clears, formula untouched:** pre-wall re-run live (`1.034117125 > 1.02168` refused — SG-223 reproduced) → post (`0.182717125 ≤ 1.02168` proceed); synthetic over-cap + no-authority refusals proven. F-SG224-2 noted (repo `pilot_counts` proxy tightens its helper cap on the classified 400 row) — disclosed, both caps still proceed, no product code touched.
- **Deviations, none deducted:** F-SG224-1 — first run committed correctly then tripped on the author's own false month-vs-today assertion; fixed with a read-only post mode, ZERO new writes, failing transcript preserved. F-SG224-4 — key-gate token self-match corrected to live-value-only scan. Both are tooling iterations caught pre-effect with full disclosure.
- **Scope:** 16 files — driver `backend/scripts/sg224_classify.py` + `docs/worklogs/SG-224_*`; zero product/test bytes, no migration, no restart. Contract 0.50.0 live proof. Elapsed 269 s vs ≈300 s. **Money: $0** (0 sends, 1 free pricing GET).
- **Secrets:** literal gate EMPTY exit 1; live-value key gate `matching_bytes=0` (15 files).

## Rating

**Holistic: 98/100, no flag.** Five rows derived live, proved $0 three ways each, written once each with revert-hash proof, and the guard re-run live on both sides of the wall with the formula byte-identical. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used. Guards: PG-EV-02/03/05/06/09/14; PG-SC-03/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| Guard wall cleared (unknown 5→0) | Cutout probe SG-225 dispatches same turn under L3 — the missing verdict unblocks |
| Repo `pilot_counts` proxy quirk | Recorded, untouched — a future slice may align it if it ever binds |
| Driver assertion + gate-token iterations | Fixed pre-effect, transcripts preserved — pattern note stands (carry full spec, scan live value only) |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
