# SG-226 — L3 bulk stage: scene renders for every product photo without a linked faithful scene (review-before-link, link faithful only)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + provider-ledger + audit_event rows ONLY for renders that return image bytes, plus one `asset_evidence` link row per faithful render, grants D-29 + D-31 + D-20 + D-14, `PG-PR-10`). No UPDATE/DELETE of any row, ever; every row reported with identifiers and left in place (`PG-EV-06`). No migration.
**Restart: none.** No served-code change → no refresh (the drawer reads live links; newly linked renders appear with no deploy).
**Autonomy: L3** (stage D-31; checkpoints only on `G-K2`/assumption-change/stage end; one retry, root-cause only). Authority: owner D-29 (bulk run for all products) + D-31 (L3 stage). Spend: D-20 ($2.00/day) + D-14 ($10.00/month) bind every billed leg fail-closed; D-27's 10-count is SUPERSEDED for bulk renders by D-29 (this decision states the handoff — bulk renders count against daily/monthly headroom, not the pilot 10; pilot ledger stays as-is for the record).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

Pilot verdicts are in: scenes render faithfully for ordinary branded packs (Miso, Costiță-2 linked) with two known failure shapes (CEAFĂ content-policy block stays parked; PIKOK pairing needs a canonical-photo decision, not a re-render). D-29's bulk run now covers every product photo that has no linked faithful scene — each rendered once through the proven path, reviewed, linked only if faithful.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Product path + guards: `backend/app/services/scene/openrouter.py` — `render_scene`, `SceneSpendAuthority(grant_id, cap_usd)`, `guard_render_spend` (fail-closed; unknown-cost count live — re-verify, never inherit). Precedent drivers: `backend/scripts/sg218_render.py`, `sg220_render.py` (read ON TARGET; inherit the fixed authority handoff + review-before-link pattern; quote where the tree differs).
- Leg: `google/gemini-3.1-flash-image` via OpenRouter (green except parked shapes: CEAFĂ RECITATION, unfaithful-label renders). Precedence (`PG-IC-03`): slug unroutable = BLOCKED for that leg — ship the evidence, never substitute.
- Frozen scene brief (read from the precedent script on target): "Restage this packaged product on a clean kitchen counter in warm natural daylight; keep the package, its label and its printed text exactly as photographed."
- Excluded (never rendered in this slice): CEAFĂ (content-policy park); any photo with a linked faithful scene already (Miso SG-217, Costiță SG-220); the PIKOK-can photo (pairing defect — canonical-photo decision pending, re-rendering it reproduces the rejected product).

## G1 — enumerate live, derive the render list, bound it, then render each once

- Enumerate ALL assets with upload Evidence photos ON TARGET (live DB join + byte checks on the volume). Apply the exclusions above by live query (linked faithful scene? policy-parked? pairing-defective?), never by memory. Report enumeration + per-photo disposition (render / skip-with-reason). Expectation (verify, report difference either way): the remaining set is small (DB holds 7 assets; 2 covered, 1 parked, 1 pairing-defective).
- BEFORE ANY send, prove the whole-list bound else STOP before the first send: worst case from the LIVE pricing lines × planned count + known spend ≤ tightest of (daily remainder, monthly remainder); breach on EITHER cap → STOP with the count (split across days is the Architect's next packet, never an in-slice overrun). Re-verify the guard projection before EACH send (prior actuals change the headroom).
- Drive `render_scene` once per listed photo with the frozen brief. Any `refused`/`failed` STOPS that leg with bodies committed and the rest still ships — UNLESS the failure is a content-policy block, which parks that photo immediately (CEAFĂ precedent). Persist EACH result as it returns (`PG-EV-14`).
- Per render: quote Evidence + ledger (+ audit_event) ids; open the stored image + disposition it; per-render judgment — faithfulness to the source photo first, scene quality second, no aggregate scores. Link to the source asset ONLY if faithful (review-before-link); unfaithful renders stay unlinked with reason in a link-decision record.

## Constraints

- **Money:** billed count == derived live list size (recomputed worst case per render from live pricing); D-20 + D-14 bind every leg fail-closed pre-send (each leg) and pre-list (whole list); actuals (both `cost=0.0` AND upstream inference cost) vs projection per render in the report.
- **Scope ceiling:** driver `backend/scripts/sg226_bulk_scene.py` (lane-run tooling, NOT served code) + evidence ONLY `docs/worklogs/SG-226_*`. Zero product/test bytes elsewhere; no migration; no restart; no secret in any artifact (key name-only, word-split grep-gate exit 1, plus live-value key gate `matching_bytes=0`).
- **Production writes:** new Evidence + ledger + audit rows per returned render + ONE link row per faithful render; no UPDATE/DELETE; every row quoted and left in place.
- `PG-EV-07`: every photo payload is a REAL Evidence photo, never a fixture. `PG-EV-09`: sends + response bodies + ALL transcripts committed raw. `PB-2`: denial STOPS the affected leg and the rest ships — disclose verbatim, do not route around. Consent predicate: this packet's quoted authority ONLY. CEAFĂ-shaped blocks park the photo, never route around.
- Hang bounds: reads 120 s; each render 300 s; suite NOT run (zero product bytes — stated); idle kill never approached. Expected duration ≈900 s (Architect record, `G-A9` uncalibrated; ~4 renders + reviews at SG-217/218 pace).
- Simplicity: enumerate + N renders + link-if-faithful + judgments; no new machinery. Excluded (stated): cutout renders (verdict: isolation pass, label fail — bulk cutouts wait on a better brief); CEAFĂ re-render; resolution pin; Generate-button wiring; provider-routing contest.

## Acceptance criteria

- **A1:** live enumeration with per-photo disposition; billed count == derived list size; each `rendered` with Evidence + ledger ids quoted and link decision recorded with reason, each `refused`/`failed` STOPPED with bodies committed; no photo rendered twice, none skipped silently.
- **A2:** whole-list bound proof pre-first-send + per-leg triple-bound proofs; actual-vs-projection on BOTH accountings per render; ledger row(s) committed; secret gates empty (commands + outputs committed).
- **A3:** every stored image opened + dispositioned + per-render judgments (faithfulness first); elapsed vs ≈900 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-226`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-226 | Report: docs/worklogs/SG-226_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-226 | Report: docs/worklogs/SG-226_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-226_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10. Stop follows `PB-6`.
