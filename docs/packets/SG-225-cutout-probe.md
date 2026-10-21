# SG-225 — L3 bulk stage: first cutout probe (Miso, isolation brief, render 5 of 10 billed)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + provider-ledger + audit_event rows ONLY for a render that returns image bytes, grants D-29 + D-27 + D-20 + D-14, `PG-PR-10`). No UPDATE/DELETE of any row, ever; new rows reported with identifiers and left in place (`PG-EV-06`). No migration.
**Restart: none.** No served-code change → no refresh.
**Autonomy: L3** (stage D-31; checkpoints only on `G-K2`/assumption-change/stage end; one retry, root-cause only). Authority: owner D-29 (bulk run) + D-31 (L3 stage) + D-27 (≤10 billed — 4 consumed; this slice plans exactly ONE, leaving five; an 11th billed render on this authority is a STOP) + D-20 ($2.00/day) + D-14 ($10.00/month).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-223's cutout leg was refused by the guard it was meant to test under; SG-224 cleared the wall (unknown 5→0, re-proof 0.1827 ≤ cap). This slice runs the missing verdict: the first-ever cutout render (Miso, isolation brief). Link-if-faithful (review-before-link — the SG-218 lesson); the drawer cutout tab still shows the honest copy (display is a separate product slice, explicitly out of scope).

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Product path + guards: `backend/app/services/scene/openrouter.py` — `render_scene`, `SceneSpendAuthority(grant_id, cap_usd)`, `guard_render_spend` (fail-closed; unknown-cost count is now 0 — re-verify live, never inherit). Precedent driver: `backend/scripts/sg223_render.py` (read ON TARGET; inherit the fixed authority handoff + the link-decision pattern; quote where the tree differs).
- Leg: `google/gemini-3.1-flash-image` via OpenRouter (green except asset-specific blocks: SG-219 CEAFĂ RECITATION, SG-218/223 pairing). Precedence (`PG-IC-03`): slug unroutable = BLOCKED — ship the evidence, never substitute.
- Photo: Miso source photo (evidence `01a0c4a0-…`, raw sha `71901cac…` — re-verify live). Confirm pilot-unused for CUTOUT specifically (a scene row for this photo exists; a cutout row must not — live ledger query, zero expected, STOP otherwise).
- Cutout brief (same as SG-223 packet, unrun): "Isolate this packaged product on a plain seamless white background, front-facing, even studio lighting; the full package with its label and printed text exactly as photographed; no props, no scene, no shadow, no hands." Pass = product isolated on white, label legible; anything else is a finding. CEAFĂ is not rendered under any reading.

## G1 — one cutout render, all three bounds checked BEFORE the send

- Confirm the Miso photo has no cutout render row live (ledger query over input hashes, both sha forms); open it before the send.
- BEFORE the send, prove all three bounds else refuse (`over_cap`, STOP): (a) `guard_render_spend` with `SceneSpendAuthority(grant_id="L3 bulk stage (cutout probe, billed 5 of 10) + D-20 + D-14", cap_usd=<tightest>)`; (b) this slice's billed count ≤ 1 and pilot-billed + 1 ≤ 10; (c) worst case from the LIVE pricing lines (recompute).
- Drive `render_scene` once with the cutout brief. `refused`/`failed` STOPS with bodies committed — a fix is a finding for the next slice, never an in-slice repair. Persist EACH result as it returns (`PG-EV-14`).
- On `rendered`: quote Evidence + ledger (+ audit_event) ids; open the stored image + disposition it; per-render judgment — isolation first (white background? full product? label legible?), then faithfulness; link to the Miso asset ONLY if faithful AND isolated (else stays unlinked with reason).

## Constraints

- **Money:** ≤1 billed render this slice (billed 5 of 10); D-20 + D-14 + pilot-remainder all bind fail-closed pre-send; actuals (both `cost=0.0` AND upstream inference cost) vs projection in the report.
- **Scope ceiling:** driver `backend/scripts/sg225_cutout.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-225_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact (key name-only, word-split grep-gate exit 1, plus live-value key gate `matching_bytes=0`).
- `PG-EV-07`: the photo payload is the REAL Miso Evidence photo, never a fixture. `PG-EV-09`: send + response bodies + ALL transcripts committed raw. `PB-2`: denial STOPS the whole slice — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; the one render 300 s; suite NOT run (zero product bytes — stated); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated).
- Simplicity: confirm + 1 render + link-if-faithful-and-isolated + judgment; no new machinery. Excluded (stated): drawer cutout branch (separate product slice); CEAFĂ re-render; resolution pin; bulk packets (after this verdict); Generate-button wiring.

## Acceptance criteria

- **A1:** exactly ≤1 billed render; `rendered` with Evidence + ledger ids quoted and link decision recorded with reason, or `refused`/`failed` STOPPED with bodies committed; Miso photo confirmed cutout-unused live pre-send.
- **A2:** pre-send triple-bound proof and actual-vs-projection on BOTH accountings; ledger row(s) committed; secret gates empty (commands + outputs committed).
- **A3:** stored image opened + dispositioned + per-render judgment (isolation first); elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-225`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-225 | Report: docs/worklogs/SG-225_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-225 | Report: docs/worklogs/SG-225_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-225_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
