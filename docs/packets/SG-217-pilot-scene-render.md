# SG-217 — D-27 pilot render 1 of 10: one context-scene render via the product path (`render_scene`, real asset photo, store + ledger)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + provider-ledger rows ONLY, grants D-27 + D-20 + D-14, `PG-PR-10`). No UPDATE/DELETE of existing rows, ever; new rows reported with identifiers and left in place (`PG-EV-06`).
**Restart: none.** No served-code change → no refresh.
**Autonomy: L2** (one retry, root-cause only). Authority: owner D-27 bounded pilot (≤10 billed renders TOTAL — this slice plans exactly ONE, leaving nine; an 11th render on this authority is a STOP) + D-20 ($2.00/day) + D-14 ($10.00/month).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-216 proved the Google leg green (G1+G2 both 200, BYOK). The product path — `render_scene` (orchestrator rewrite + image-tool call + extract + persist + ledger) — last ran live in SG-159, where the model legs were blocked and no render ever completed. This slice proves the path end to end with a real asset photo: one billed render, stored as Evidence, ledgered, opened and judged. Scope correction on the D-27 record: SG-217 is the SCENE leg only — the cutout/isolation pipeline is a separate producer (spec `2026-10-09-context-scene-design.md` non-goals); cheapest-and-most-load-bearing first.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Product path: `backend/app/services/scene/openrouter.py` — `render_scene` (line ~704), `SceneSpendAuthority(grant_id, cap_usd)` (line ~256; the grant's mere presence is the consent predicate — never flip `sg_consent`), `guard_render_spend` (fail-closed projection incl. unknown-cost rows), `scene_spend_so_far`. Precedent driver: `backend/scripts/sg159_render.py` (one invocation = one render, frozen brief, RENDERS map, AUTHORITY construction, per-leg transcript) — read both ON TARGET; quote where they differ from this packet.
- Leg: `google/gemini-3.1-flash-image` via OpenRouter (proven green SG-216: 3 endpoints, refs 0..14, ~6e-05/token, BYOK `cost=0.0` + upstream ~$0.0459/render at 512). Precedence (`PG-IC-03`): this slug proving unroutable is BLOCKED for this slice — ship the evidence, never substitute another image slug. Orchestrator expectation (SG-159: cheapest routable tool-capable model — re-verify FREE before spending, justify any change).
- Caps live at SG-216: arc usage `0.012437125`, daily `0.0`, monthly `0.012437125`, $5 key limit (binds only if BYOK removed). Re-derive ALL spend figures live — never inherit a total.

## G1 — one scene render, all three bounds checked BEFORE the send

- Enumerate food/clear-label assets with Evidence photos ON THE TARGET and pick ONE real photo (criterion, not a list — report enumeration + pick; never reuse a photo ID from memory).
- BEFORE the send, prove all three bounds else refuse (`over_cap`, STOP): (a) `guard_render_spend` projection with `SceneSpendAuthority(grant_id="D-27 bounded pilot (render 1 of 10) + D-20 + D-14", cap_usd=<tightest money bound>)` — cap_usd is the tightest of daily-remainder/monthly-remainder/pilot-remainder computed live; (b) this slice's render count ≤ 1 and pilot-consumed + 1 ≤ 10; (c) worst case from the LIVE pricing lines. Any bound breached → STOP, billed leg does not run.
- Drive `render_scene` exactly once with the frozen brief (read it from the precedent script on target) + the picked photo. `refused`/`failed` STOPS with bodies committed — a fix is a finding for the next slice, never an in-slice repair (diagnose-then-fix bundle banned). Persist EACH result as it returns (`PG-EV-14`).
- On `rendered`: quote Evidence + ledger ids; open the stored image + disposition it (neutral subject expected, no PII by construction); per-render judgment — asset faithfulness vs scene quality, stated, no aggregate scores.

## Constraints

- **Money:** ≤1 billed render this slice (1 of 10 pilot); D-20 + D-14 + pilot-remainder all bind fail-closed pre-send; actual (both `cost=0.0` AND upstream inference cost) vs projection in the report; unbilled responses spend $0 against no cap (stated if moot).
- **Scope ceiling:** driver `backend/scripts/sg217_render.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-217_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact (key name-only, word-split grep-gate exit 1, plus live-value key gate `matching_bytes=0` — SG-216 pattern).
- `PG-EV-07`: the photo payload is a REAL Evidence photo, never a fixture or mock. `PG-EV-09`: send + response bodies + ALL transcripts committed raw. `PB-2`: denial (key, consent, cap, privilege) STOPS the whole slice — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; the one render 300 s; suite NOT run (zero product bytes — stated); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-159 same shape ~940 s with 3 renders + code).
- Simplicity: enumerate + 1 render + ledger + judgment; no new machinery. Excluded (stated): cutout pipeline; UI wiring (next arc, own word); chat-path re-proof; muse; provider-routing contest (needs another billed POST).

## Acceptance criteria

- **A1:** exactly ≤1 billed render; `rendered` with Evidence + ledger ids quoted, or `refused`/`failed` STOPPED with bodies committed; photo enumeration + pick reported.
- **A2:** pre-send triple-bound proof (projection math + remainders) and actual-vs-projection on BOTH accountings; ledger row(s) committed; secret gates empty (commands + outputs committed).
- **A3:** stored image opened + dispositioned + per-render judgment; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-217`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-217 | Report: docs/worklogs/SG-217_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-217 | Report: docs/worklogs/SG-217_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-217_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
