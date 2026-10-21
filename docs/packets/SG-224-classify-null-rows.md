# SG-224 — D-30: classify the 5 stale null-cost ledger rows (NULL → 0.0, per-row proof, zero sends)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` — exactly FIVE `provider_call` UPDATEs, `cost` NULL → `0.0`, grants D-30, `PG-PR-10`). No other UPDATE; no INSERT; no DELETE; every row reported with identifiers and per-row proof, then left in place (`PG-EV-06`). No migration.
**Restart: none.** No served-code change → no refresh.
**Autonomy: L2** (one retry, root-cause only). Authority: owner D-30 (classify — this message) + D-20 ($2.00/day) + D-14 ($10.00/month), both moot at $0 and still checked.

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

Five unbilled error rows (2×404, 2×429 pre-pilot + SG-219's CEAFĂ 400) sit at `cost=NULL`, so the fail-closed guard charges each a full worst case and every future render refuses (SG-223 #5: 1.034117125 > 1.02168). Each row is provably $0 — error bodies carry no usage object and key spend never moved across any of them. This slice writes that measured fact into the ledger (5 UPDATEs, per-row proof) and proves the wall clears by re-running the guard projection live.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Ledger reader: `scene_spend_so_far(db)` in `backend/app/services/scene/openrouter.py` (`~:288`) — `(sum(cost), count(cost NULL))` over `provider=openrouter` rows. Expected live: known `0.012437125`, unknown **5**. Re-derive, never inherit.
- The 5 (criterion — error rows with no usage and no cost, derived live, never a handed list): SG-223 names 2×404 + 2×429 (pre-pilot, account-level) + 1×400 (SG-219 CEAFĂ `01a15fe8-…`). Expect exactly these 5; any 6th null-cost row, any row WITH a usage object, or any billed row in the set STOPS the slice (`PG-IC-08` either direction — classify nothing by assumption).
- Proof standard per row (all three, committed): (a) the row's stored response/error body carries no `usage`/`cost` object; (b) key spend read immediately pre/post that row's call is byte-identical on the spend fields (or the call predates spend logging — then the row's own body is the whole proof, stated); (c) row id + error quoted.

## G1 — verify the 5, UPDATE exactly the 5, prove the wall clears

- Derive the null-cost set live; assert it is EXACTLY the expected 5 by id and error (404/404/429/429/400); assemble the per-row proof; STOP on any difference.
- UPDATE `cost` NULL → `0.0` on exactly those 5 (per-statement `changes()=1` each, single transaction discipline per repo convention — read it on target, do not invent it; on any statement affecting ≠1 row, ROLLBACK and STOP).
- Re-read `scene_spend_so_far`: expect known `0.012437125`, unknown **0**. Re-run the guard projection live with the SG-223 inputs (spent 0.012437125, worst 0.17028 recomputed from live pricing): expect ≈0.18 proceed vs the pilot-remainder cap. Quote both.
- Zero sends, zero renders, zero billed calls — this slice moves no money and proves none needs moving.

## Constraints

- **Money:** $0 — no sends, no renders, no probes that bill; reads + 5 UPDATEs + local test-less verification only. D-20/D-14 checked and moot (stated with the zero actual).
- **Scope ceiling:** driver `backend/scripts/sg224_classify.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-224_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact; no renders, no sends.
- **Production writes:** EXACTLY the 5 classified UPDATEs (ids + per-row proof quoted); no other write of any kind; rows left in place.
- `PG-EV-09`: derivation, per-row bodies, write log, post-state and guard re-proof committed raw. `PB-2`: any denial (lock, permission) STOPS the whole slice — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; writes 120 s; idle kill never approached. Expected duration ≈300 s (Architect record, `G-A9` uncalibrated; read-only slice, no suite to run).
- Simplicity: derive + 5 UPDATEs + re-proof; no new machinery. Excluded (stated): any other row; cutout re-probe (next slice); bulk run (packets after); CEAFĂ re-render; resolution pin; Generate-button wiring.

## Acceptance criteria

- **A1:** the live null-cost set == exactly the expected 5 (ids + errors quoted); 5 UPDATEs each `changes()=1`; post-state unknown 0, known unchanged; no other delta (full per-table counts pre/post quoted).
- **A2:** guard re-proof live with recomputed worst case: projection ≈0.18 ≤ pilot-remainder cap → `proceed`; synthetic over-cap still refuses (proves the formula unweakened).
- **A3:** report `docs/worklogs/SG-224_report.md`; elapsed vs ≈300 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-224`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-224 | Report: docs/worklogs/SG-224_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-224 | Report: docs/worklogs/SG-224_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-224_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/09/14; PG-SC-03/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
