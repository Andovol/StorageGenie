# SG-223 audit — D-28: unlink exact, re-render faithful-but-unlinked (pairing defect, not model fault), cutout probe guard-refused, rated 98

Immutable audit: base `ab6e5c1` → G1 `4f1b4fd` (driver + live verify + exact unlink, no send) → work `de10b7e` (render + refusal + link decision) → report `4c7221b` → merge `04692d1` (origin's D-29) → receipt `ff891c7`/`9fff5c1` (transcript + mapped read-back; Work-HEAD 4c7221b). Local `--ff-only` to the exact tip (`9fff5c1` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-223 exit=0`. Receipt note `Dispatch-ID: SG-223 | Report: docs/worklogs/SG-223_report.md` IS on the remote — own read-back finds `4c7221b` via `git log --notes`, transcript shows notes + branch pushes `rc=0`. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — eighth clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Unlink exact (independently read):** `SG-223_unlink.json` carries pair, `delete_rowcount` and before/after counts; `asset_evidence` 17→16 with nothing else moved; the Costiță route re-read shows exactly the SG-220 render. The SG-218 Evidence + ledger + audit rows all survive (link-only surgery).
- **Render #4 RENDERED, correctly UNLINKED (image opened by this audit):** `SG-223_render_costita.jpg` (1195x896, 653,722 B) reproduces the PIKOK can closely — mark, label text, pig, ring pull all legible. Faithful to its source, wrong product for the asset → unlinked with reason in `SG-223_link_decision.json`. F-SG223-1 stands on live bytes: source photo `ad90…` (sha `f9d71a40…`) IS the PIKOK can (opened as `SG-223_source_costita.png`), so SG-218 never invented a tin from a vacuum pack — the defect is the asset-photo pairing. Correction 2 appended to the faithfulness note; Correction 1's input attribution superseded, the audit-miss admission unchanged.
- **Render #5 REFUSED, honestly (guard math re-verified):** `SG-223_guard_miso.json` — projection `0.012437125 + 5×0.17028 + 0.17028 = 1.034117125` vs cap `1.02168` (pilot remainder tightest) → `over_cap`, no request built, no POST, no cost. The formula is unchanged from SG-219/220 (not weakened to force the send); synthetic over-cap + no-authority refusals proven. Consequence: with 5 unknown-cost rows charged at full worst case, NO further pilot render can clear the guard — the pilot is blocked by headroom, not by count (6 billed left, 0 spendable). This is the D-30 fork below, not a slice defect.
- **Money:** 1 POST, 1 billed (credits `0.0`, upstream `0.068499`); D-20/D-14 held (product ledger today 0.273168/2.00, month 0.285605125/10.00); pilot 4/10 billed. DB post-state: evidence 21→22, provider_call 33→34, audit_event 94→95, asset_evidence 17→16, null-cost 5→5, known sums unchanged; no UPDATE.
- **My mid-flight push, cost realized:** the D-29 record landed while SG-223 ran; the transcript shows the `automation` push rejected, then fetch + `merge --no-ff` ("Already up to date" — the decision file touched no Coder path) + push `091dba3..ff891c7` green, plus the D-29 addendum doc. Total cost: one rejected push and one merge cycle, zero rework, zero re-verification — the rule still binds; decision records wait for quiet turns.
- **Scope:** 37 files — driver `backend/scripts/sg223_render.py` + `docs/worklogs/SG-223_*`; zero product/test bytes, no migration, no restart. Contract 0.50.0 live proof. Elapsed 488 s vs ≈600 s; render POST 8.9 s vs 300 s bound.
- **Secrets:** literal gate exit 1 EMPTY; live-value key gate `matching_bytes=0` (1314 + 18 files).

## Rating

**Holistic: 98/100, no flag.** Exact unlink with counted proof; a re-render judged source-first with the pairing defect named instead of a second wrong link; a live guard refusal honored without touching the formula; a packet premise refuted with bytes and the correction corrected. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used. Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| Pairing defect (PIKOK photo on Costiță asset) | Recorded (Correction 2); canonical-photo decision rides D-30, never an in-slice repair |
| Cutout probe unrun + guard wall (no pilot render can clear it) | D-30 fork for the owner — classify the 5 stale null rows, grant wider headroom, or park |
| Pre-send driver KeyError (2nd slice running) | Fixed pre-send, zero billed impact, disclosed; pattern noted — driver authors: carry the full spec dict, never a subset |
| My D-29 mid-flight push | Cost realized (1 rejected push + 1 trivial merge); rule restated — decision records wait for quiet turns |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
