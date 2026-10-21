# SG-218 — D-27 pilot render 2 of 10: second context-scene render via the product path (new photo, store + ledger)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + provider-ledger rows ONLY, grants D-27 + D-20 + D-14, `PG-PR-10`). No UPDATE/DELETE of existing rows, ever; new rows reported with identifiers and left in place (`PG-EV-06`).
**Restart: none.** No served-code change → no refresh.
**Autonomy: L2** (one retry, root-cause only). Authority: owner D-27 bounded pilot (≤10 billed renders TOTAL — SG-217 consumed 1; this slice plans exactly ONE, leaving eight; a 3rd pilot render on a future slice still counts; an 11th render on this authority is a STOP) + D-20 ($2.00/day) + D-14 ($10.00/month).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-217 proved the product path end to end (Miso Soup, `rendered`, stored, ledgered, triple-bound proof). One render is a single data point on one photo. SG-218 repeats the proven shape on a different asset photo: second stored render, second ledger row, second faithfulness judgment — the pilot's evidence base for whatever implementation follows. No code change is expected; any path failure is a finding for the next slice, never an in-slice repair.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Product path: `backend/app/services/scene/openrouter.py` — `render_scene`, `SceneSpendAuthority(grant_id, cap_usd)`, `guard_render_spend` (fail-closed incl. unknown-cost rows), `scene_spend_so_far`. Precedent driver: `backend/scripts/sg217_render.py` (one invocation = one render; read it ON TARGET and reuse its shape; quote where it differs).
- Leg: `google/gemini-3.1-flash-image` via OpenRouter (green SG-216/SG-217; refs 0..14; ~6e-05/token; BYOK `cost=0.0` + upstream ~$0.045–0.068/render). Precedence (`PG-IC-03`): this slug proving unroutable is BLOCKED for this slice — ship the evidence, never substitute another image slug.
- Pilot count live: SG-217 consumed render 1 (Evidence `01a15f6f-13ba-…`, 2026-10-21, on/after the D-27 record date). The pre-pilot Muse row (2026-10-12) stays excluded by date. Re-derive ALL spend figures live — never inherit a total.

## G1 — one scene render, all three bounds checked BEFORE the send

- Enumerate food/clear-label assets with Evidence photos ON TARGET and pick ONE real photo the pilot has not used yet (SG-217 used Miso Soup evidence `01a0c4a0-…` — excluded; SG-159's two precedent photos stay excluded). Criterion, not a list — report enumeration + pick. Open the photo before the send.
- BEFORE the send, prove all three bounds else refuse (`over_cap`, STOP): (a) `guard_render_spend` projection with `SceneSpendAuthority(grant_id="D-27 bounded pilot (render 2 of 10) + D-20 + D-14", cap_usd=<tightest money bound>)` — cap_usd is the tightest of daily-remainder/monthly-remainder/pilot-remainder computed live; (b) this slice's render count ≤ 1 and pilot-consumed + 1 ≤ 10; (c) worst case from the LIVE pricing lines (SG-217's 2580-token figure is a reference, not a bound — recompute from live lines and the path's actual default).
- Drive `render_scene` exactly once with the frozen brief (read from the precedent script on target) + the picked photo. `refused`/`failed` STOPS with bodies committed. Persist EACH result as it returns (`PG-EV-14`).
- On `rendered`: quote Evidence + ledger ids; open the stored image + disposition it; per-render judgment — asset faithfulness vs scene quality, stated, no aggregate scores.

## Constraints

- **Money:** ≤1 billed render this slice (2 of 10 pilot); D-20 + D-14 + pilot-remainder all bind fail-closed pre-send; actual (both `cost=0.0` AND upstream inference cost) vs projection in the report; unbilled responses spend $0 against no cap (stated if moot).
- **Scope ceiling:** driver `backend/scripts/sg218_render.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-218_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact (key name-only, word-split grep-gate exit 1, plus live-value key gate `matching_bytes=0`).
- `PG-EV-07`: the photo payload is a REAL Evidence photo, never a fixture or mock. `PG-EV-09`: send + response bodies + ALL transcripts committed raw. `PB-2`: denial STOPS the whole slice — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; the one render 300 s; suite NOT run (zero product bytes — stated); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-217 same shape took 326 s).
- Simplicity: enumerate + 1 render + ledger + judgment; no new machinery. Excluded (stated): cutout pipeline; UI wiring; resolution pin; chat-path re-proof; muse; provider-routing contest.

## Acceptance criteria

- **A1:** exactly ≤1 billed render; `rendered` with Evidence + ledger ids quoted, or `refused`/`failed` STOPPED with bodies committed; photo enumeration + pick reported (pilot-unused photo).
- **A2:** pre-send triple-bound proof (projection math + remainders) and actual-vs-projection on BOTH accountings; ledger row(s) committed; secret gates empty (commands + outputs committed).
- **A3:** stored image opened + dispositioned + per-render judgment; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-218`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-218 | Report: docs/worklogs/SG-218_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-218 | Report: docs/worklogs/SG-218_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-218_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
