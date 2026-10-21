# SG-219 — D-27 pilot renders 3+4 of 10: two scene renders via the product path (last two pilot-unused photos, store + ledger)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + provider-ledger + audit_event rows ONLY, grants D-27 + D-20 + D-14, `PG-PR-10`). No UPDATE/DELETE of existing rows, ever; new rows reported with identifiers and left in place (`PG-EV-06`). Future scene packets name all three row kinds (SG-218 correction).
**Restart: none.** No served-code change → no refresh.
**Autonomy: L2** (one retry, root-cause only). Authority: owner D-27 bounded pilot (≤10 billed renders TOTAL — SG-217/218 consumed 2; this slice plans exactly TWO, leaving six; a 5th pilot render on a future slice still counts; an 11th render on this authority is a STOP) + D-20 ($2.00/day) + D-14 ($10.00/month).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-217/218 proved the product path on two assets. Two eligible food photos remain pilot-unused; rendering both in this slice completes the eligible set (4/4) and closes the replication question — the pilot's evidence base is then finished, with six renders banked for implementation slices. Any path failure is a finding for the next slice, never an in-slice repair.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Product path: `backend/app/services/scene/openrouter.py` — `render_scene`, `SceneSpendAuthority(grant_id, cap_usd)`, `guard_render_spend` (fail-closed incl. unknown-cost rows). Precedent driver: `backend/scripts/sg218_render.py` (one invocation = one render; SG-219 needs TWO invocations or a two-render driver — read it ON TARGET and extend its shape; quote where it differs).
- Leg: `google/gemini-3.1-flash-image` via OpenRouter (green SG-216/217/218; refs 0..14; ~6e-05/token; BYOK `cost=0.0` + upstream ~$0.068/render at the provider default). Precedence (`PG-IC-03`): this slug proving unroutable is BLOCKED for this slice — ship the evidence, never substitute another image slug.
- Pilot count live: SG-217 + SG-218 consumed renders 1–2 (both 2026-10-21, on/after the D-27 record date). The pre-pilot Muse row (2026-10-12) stays excluded by date. Re-derive ALL spend figures live — never inherit a total.

## G1 — two scene renders, all three bounds checked BEFORE EACH send

- Enumerate food/clear-label assets with Evidence photos ON TARGET and pick the TWO pilot-unused eligible photos (used already: Miso Soup evidence `01a0c4a0-…` SG-217, Costiță-1 evidence `01a0c4a1-ad90-…` SG-218, SG-159's two precedent photos — all excluded; expected remainder: CEAFĂ + Costiță second photo — verify live, never assume). Criterion, not a list — report enumeration + picks. Open both photos before the first send.
- BEFORE EACH send, prove all three bounds else refuse (`over_cap`, STOP — a STOP on the second render still ships the first through `PB-6`): (a) `guard_render_spend` projection with `SceneSpendAuthority(grant_id="D-27 bounded pilot (renders 3+4 of 10) + D-20 + D-14", cap_usd=<tightest money bound>)`; (b) this slice's render count ≤ 2 and pilot-consumed + planned ≤ 10; (c) worst case from the LIVE pricing lines (recompute; SG-218's 2580-token figure is a reference, not a bound).
- Drive `render_scene` once per photo with the frozen brief (read from the precedent script on target). `refused`/`failed` STOPS that leg with bodies committed. Persist EACH result as it returns (`PG-EV-14`).
- On each `rendered`: quote Evidence + ledger (+ audit_event) ids; open the stored image + disposition it; per-render judgment — asset faithfulness vs scene quality, stated, no aggregate scores.

## Constraints

- **Money:** ≤2 billed renders this slice (3+4 of 10 pilot); D-20 + D-14 + pilot-remainder all bind fail-closed pre-send (re-checked before the second send against the first's actual); actuals (both `cost=0.0` AND upstream inference cost) vs projection in the report.
- **Scope ceiling:** driver `backend/scripts/sg219_render.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-219_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact (key name-only, word-split grep-gate exit 1, plus live-value key gate `matching_bytes=0`).
- `PG-EV-07`: both photo payloads are REAL Evidence photos, never fixtures or mocks. `PG-EV-09`: sends + response bodies + ALL transcripts committed raw. `PB-2`: denial STOPS the affected leg and the rest ships — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; each render 300 s; suite NOT run (zero product bytes — stated); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-218 same shape took 267 s for one render).
- Simplicity: enumerate + 2 renders + ledger + judgments; no new machinery. Excluded (stated): cutout pipeline; UI wiring; resolution pin; chat-path re-proof; muse; provider-routing contest.

## Acceptance criteria

- **A1:** exactly ≤2 billed renders; each `rendered` with Evidence + ledger ids quoted, or `refused`/`failed` STOPPED with bodies committed; photo enumeration + picks reported (both pilot-unused).
- **A2:** pre-send triple-bound proof before EACH send (projection math + remainders) and actual-vs-projection on BOTH accountings; ledger row(s) committed; secret gates empty (commands + outputs committed).
- **A3:** both stored images opened + dispositioned + per-render judgments; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-219`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-219 | Report: docs/worklogs/SG-219_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-219 | Report: docs/worklogs/SG-219_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-219_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
