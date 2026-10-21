# SG-223 — D-28: unlink the wrong Costiță render + re-render Costiță-1 + cutout-probe Miso (2 billed renders: #4 and #5 of 10)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — exactly ONE `asset_evidence` DELETE (the SG-218 wrong-render link, ids below) + new Evidence + provider-ledger + audit_event rows ONLY for renders that `render`, grants D-28 + D-27 + D-20 + D-14, `PG-PR-10`). No UPDATE of any row, ever; no other DELETE; every row reported with identifiers and left in place (`PG-EV-06`). No migration.
**Restart: none.** No served-code change → no refresh (the drawer reads live rows; the unlinked bad render disappears and the re-render appears with no deploy).
**Autonomy: L2** (one retry, root-cause only). Authority: owner D-28 (whole recommended plan) + D-27 bounded pilot (≤10 billed — 3 consumed; this slice plans exactly TWO, leaving five; a 6th billed render on a future slice still counts; an 11th billed render on this authority is a STOP) + D-20 ($2.00/day) + D-14 ($10.00/month).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

The Costiță Scene tab shows SG-218's wrong-product render (tin can from a vacuum-pack photo — owner-found, correction on record). D-28: remove its link, re-render the same photo through the proven path, and probe the first-ever cutout (Miso, isolation brief). CEAFĂ stays parked (content-policy fork, never touched in this slice).

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Wrong link (derive live, criterion: the `asset_evidence` row pairing asset `01a0c4ab-…` "Costiță de porc" with render `01a15fdc-f5b6-7f31-9008-2f8d89be8813" SG-218): exactly ONE row expected — DELETE it only, report the pair, verify `asset_evidence` 17→16 live. Any other row count STOPS before writing (`PG-IC-08` either direction). The render's Evidence + ledger rows are NOT deleted.
- Product path: `backend/app/services/scene/openrouter.py` — `render_scene`, `SceneSpendAuthority(grant_id, cap_usd)`, `guard_render_spend` (fail-closed; unknown-cost count is 5 live — re-verify, never inherit). Precedent driver: `backend/scripts/sg220_render.py` (read ON TARGET, inherit the fixed authority handoff; quote where the tree differs).
- Leg: `google/gemini-3.1-flash-image` via OpenRouter (green except asset-specific blocks: SG-219 CEAFĂ RECITATION, SG-218 wrong-product). Precedence (`PG-IC-03`): slug unroutable = BLOCKED — ship the evidence, never substitute.
- Photos (criterion, re-verify live): re-render = Costiță-1 source photo (evidence `01a0c4a0…` no — `01a0c4a1-ad90-…`, raw sha `f9d71a40…`, the SG-218 input); cutout probe = Miso source photo (evidence `01a0c4a0-…`, raw sha `71901cac…`). Open both before any send.
- Frozen scene brief (read from the precedent script on target): "Restage this packaged product on a clean kitchen counter in warm natural daylight; keep the package, its label and its printed text exactly as photographed." (SG-218's committed request — quoted in the D-28 correction note.)
- Cutout brief (NEW — this slice's experiment, stated verbatim): "Isolate this packaged product on a plain seamless white background, front-facing, even studio lighting; the full package with its label and printed text exactly as photographed; no props, no scene, no shadow, no hands." Pass = product isolated on white, label legible; anything else is a finding.

## G1 — unlink (production DELETE, exactly one row)

- Confirm live the exact link pair (Costiță asset ↔ SG-218 render evidence id); DELETE exactly that `asset_evidence` row; verify 17→16 and re-read the Costiță asset route showing only the SG-220 render (`01a15ff5-…`). Any count mismatch STOPS the whole slice (the renders must not run against an unverified link state).

## G2 — two billed renders (Costiță-1 re-render + Miso cutout probe)

- BEFORE EACH send, prove all three bounds else refuse (`over_cap`, STOP — a STOP on the second send still ships the first through `PB-6`): (a) `guard_render_spend` with `SceneSpendAuthority(grant_id="D-28 (renders 4+5 of 10) + D-20 + D-14", cap_usd=<tightest>)`; (b) this slice's billed count ≤ 2 and pilot-billed + planned ≤ 10; (c) worst case from the LIVE pricing lines.
- Drive `render_scene` once per photo: Costiță-1 with the frozen scene brief; Miso with the cutout brief. `refused`/`failed` STOPS that leg with bodies committed — a fix is a finding for the next slice, never an in-slice repair. CEAFĂ is not rendered under any reading. Persist EACH result as it returns (`PG-EV-14`). New renders link to their source assets ONLY if faithful (review-before-link — the SG-218 lesson); an unfaithful render stays unlinked with its bodies committed.
- On each `rendered`: quote Evidence + ledger (+ audit_event) ids; open the stored image + disposition it; per-render judgment — faithfulness vs the source photo first, scene/cutout quality second, stated, no aggregate scores.

## Constraints

- **Money:** ≤2 billed renders this slice (billed #4+#5 of 10 pilot); D-20 + D-14 + pilot-remainder all bind fail-closed pre-send (re-checked before the second send against the first's actual); actuals (both `cost=0.0` AND upstream inference cost) vs projection in the report.
- **Scope ceiling:** driver `backend/scripts/sg223_render.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-223_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact (key name-only, word-split grep-gate exit 1, plus live-value key gate `matching_bytes=0`).
- **Production writes:** EXACTLY the 1 link DELETE named above + new rows only for renders that return image bytes (Evidence + ledger + audit_event per render); no UPDATE; every row quoted and left in place.
- `PG-EV-07`: both photo payloads are REAL Evidence photos, never fixtures. `PG-EV-09`: send + response bodies + ALL transcripts committed raw. `PB-2`: denial STOPS the affected leg and the rest ships — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; each render 300 s; suite NOT run (zero product bytes — stated); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated).
- Simplicity: unlink + 2 renders + link-if-faithful + judgments; no new machinery. Excluded (stated): CEAFĂ re-render; resolution pin; Generate-button wiring; chat-path re-proof; muse; provider-routing contest.

## Acceptance criteria

- **A1:** exactly 1 link DELETE (pair quoted, 17→16 verified live, Costiță route shows only the SG-220 render); link-if-faithful for each new render (criterion stated per render) or explicitly unlinked with reason.
- **A2:** pre-send triple-bound proof before EACH send; actual-vs-projection on BOTH accountings per render; ledger row(s) committed; secret gates empty (commands + outputs committed).
- **A3:** both stored images opened (or 400/refusal body quoted loudly) + dispositioned + per-render judgments with faithfulness first; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-223`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-223 | Report: docs/worklogs/SG-223_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-223 | Report: docs/worklogs/SG-223_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-223_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
