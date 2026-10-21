# SG-220 — D-27 pilot render 3 of 10: one scene render via the product path (Costiță-2, the render SG-219 left unattempted)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + provider-ledger + audit_event rows ONLY, grants D-27 + D-20 + D-14, `PG-PR-10`). No UPDATE/DELETE of existing rows, ever; new rows reported with identifiers and left in place (`PG-EV-06`). Future scene packets name all three row kinds (SG-218 correction stands).
**Restart: none.** No served-code change → no refresh.
**Autonomy: L2** (one retry, root-cause only). Authority: owner D-27 bounded pilot (≤10 billed renders TOTAL — SG-217/218 consumed 2 billed; SG-219's 400 was unbilled; this slice plans exactly ONE, leaving seven; an 11th billed render on this authority is a STOP) + D-20 ($2.00/day) + D-14 ($10.00/month).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-219 stopped after its first leg failed on an asset-specific content-policy block (CEAFĂ, RECITATION 400, unbilled) and left its second pick unattempted per the packet's stop rule. The block does not touch this asset. This slice renders the left-over pick — Costiță-2, pilot-unused — through the proven path: one billed render, stored, ledgered, judged.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Product path: `backend/app/services/scene/openrouter.py` — `render_scene`, `SceneSpendAuthority(grant_id, cap_usd)`, `guard_render_spend` (fail-closed incl. unknown-cost rows — the live count is now 5 after SG-219's null-cost row, not 4). Precedent driver: `backend/scripts/sg219_render.py` (read ON TARGET; inherit its FIXED authority handoff — SG-219 F-SG219-1 `KeyError: 'authority'` is already root-caused and fixed; do not reintroduce it; quote where the tree differs).
- Leg: `google/gemini-3.1-flash-image` via OpenRouter (green SG-216/217/218; the SG-219 400 was an asset content block, not a leg or transport failure). Precedence (`PG-IC-03`): this slug proving unroutable is BLOCKED — ship the evidence, never substitute.
- Photo: Costiță de porc second photo, evidence `01a0c4a1-acbd-7541-83b7-ce9d04730716` (565,806 B, sha256 `63b3ec70…` per SG-219's enumeration — re-verify live, never inherit). Confirm ON TARGET it is still pilot-unused before the send; if it is used, STOP (do not pick a substitute photo in-slice).
- CEAFĂ (evidence `01a0c4a0-…` no — `01a0c445-…`) stays parked: no render of that asset under this slice for any reason (content-policy fork belongs to a future decision, never an in-slice repair).
- Pilot count live: 2 billed renders on/after the D-27 record date (SG-217/218). The pre-pilot Muse row (2026-10-12) and SG-219's unbilled 400 stay excluded from the billed count. Re-derive ALL spend figures live.

## G1 — one scene render, all three bounds checked BEFORE the send

- Confirm the Costiță-2 pick is pilot-unused ON TARGET (live ledger: no successful scene render row for this photo after the D-27 record date); open it before the send.
- BEFORE the send, prove all three bounds else refuse (`over_cap`, STOP): (a) `guard_render_spend` projection with `SceneSpendAuthority(grant_id="D-27 bounded pilot (render 3 of 10) + D-20 + D-14", cap_usd=<tightest money bound>)` — cap_usd is the tightest of daily-remainder/monthly-remainder/pilot-remainder computed live (unknown-cost count is 5 now); (b) this slice's render count ≤ 1 and pilot-billed + 1 ≤ 10; (c) worst case from the LIVE pricing lines (recompute; prior figures are references, not bounds).
- Drive `render_scene` exactly once with the frozen brief (read from the precedent script on target). `refused`/`failed` STOPS with bodies committed — a fix is a finding for the next slice, never an in-slice repair. Persist EACH result as it returns (`PG-EV-14`).
- On `rendered`: quote Evidence + ledger (+ audit_event) ids; open the stored image + disposition it; per-render judgment — asset faithfulness vs scene quality, stated, no aggregate scores.

## Constraints

- **Money:** ≤1 billed render this slice (3 of 10 pilot); D-20 + D-14 + pilot-remainder all bind fail-closed pre-send; actuals (both `cost=0.0` AND upstream inference cost) vs projection in the report; CEAFĂ is not rendered under any reading of this packet.
- **Scope ceiling:** driver `backend/scripts/sg220_render.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-220_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact (key name-only, word-split grep-gate exit 1, plus live-value key gate `matching_bytes=0`).
- `PG-EV-07`: the photo payload is the REAL Costiță-2 Evidence photo, never a fixture or mock. `PG-EV-09`: send + response bodies + ALL transcripts committed raw. `PB-2`: denial STOPS the whole slice — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; the one render 300 s; suite NOT run (zero product bytes — stated); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated).
- Simplicity: confirm + 1 render + ledger + judgment; no new machinery. Excluded (stated): CEAFĂ re-render; cutout pipeline; UI wiring; resolution pin; chat-path re-proof; muse; provider-routing contest.

## Acceptance criteria

- **A1:** exactly ≤1 billed render; `rendered` with Evidence + ledger ids quoted, or `refused`/`failed` STOPPED with bodies committed; pick confirmed pilot-unused live.
- **A2:** pre-send triple-bound proof (projection math with the live unknown-cost count + remainders) and actual-vs-projection on BOTH accountings; ledger row(s) committed; secret gates empty (commands + outputs committed).
- **A3:** stored image opened (or 400 body quoted loudly if failed) + dispositioned + per-render judgment; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-220`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-220 | Report: docs/worklogs/SG-220_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-220 | Report: docs/worklogs/SG-220_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-220_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
