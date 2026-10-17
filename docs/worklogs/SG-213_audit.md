# SG-213 audit — D-18(b): Google retry fails on 402 prepayment-depleted; wall stands, rated 98

Immutable audit: base `916aa53` → G1 `5958ba1` → work `0740d44` (11 evidence files + worklog, +613, zero product/config/test bytes) → report `0f22238` → receipt `254bdff` (+gate pass D). Local `--ff-only` to the exact tip (`254bdff` == origin/automation at pull); tree clean. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-213 | Report: docs/worklogs/SG-213_report.md | Work-HEAD: 0740d44...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Sixteenth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Wall (independently read):** `SG-213_g1_render_body.json` = 402 `prepayment credits are depleted` + the exact billing surface (`https://ai.studio/projects`, billing#prepay), cost null. Discovery re-measured live: slug listed, 3 endpoints, `input_references` 0..14 all three, pricing 6.6e-05/6e-05/6e-05 — matches SG-209's handed-over values. The wall moved shape (429 transient-quota → 402 depleted-prepay) but stands: billing-side state, clears only on owner action, never on retry.
- **Spend:** ledger TSV 3 rows (2×200 free reads, 1×402 send, all `cost_usd null`); 1 POST total (packet bound ≤2); actual $0.000000 vs pre-printed worst case $1.083781125 ≤ $2.00; cap UNSPENT; arc spend unchanged. Guard selftest + real refusal path committed.
- **STOP discipline:** G2 not run, no second POST for the Vertex-routing question (packet forbade exactly-beyond-planned sends — honoured; the untested Vertex route is stated, not snuck). Classification of 402 into the 429/quota family is the only reading the stop discipline permits; disclosed as inference (finding UNCLEAR-2).
- **Driver bug F-SG213-2:** dict-keyed `supported_parameters` mishandling inherited from the SG-209 driver (whose render leg never ran) — self-caught BEFORE any billed call, fixed, validated offline against the committed body, re-proven live. Zero billed impact; disclosed with the mechanism.
- **Secrets:** word-split gate re-run over the complete set incl. report + receipt log → exit 1 EMPTY (`SG-213_secret_grep.log` passes A–D). Bodies key-redacted at capture.
- **Scope:** 11 files + worklog under `docs/worklogs/SG-213_*` (+fixture copy, same root); zero product/config/test bytes. Disposable SQLite read back then removed, never committed. Health identical start/end. Elapsed 255 s vs ≈600 s (under). No command over 60 s.
- **Contract:** 0.50.0 echoed with live proof.

## Rating

**Holistic: 98/100, no flag.** The billed re-check answered the owner's question with a quotable body; the STOP was executed, not negotiated; the in-slice bug never touched money; the Vertex gap is stated, not filled by assumption. `deduction_attribution`: empty (nothing deducted). `slowest_waste`: `none`. Guards: PG-EV-02/03/05/06/07/09; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03.

## Dispositions

| Item | Destination |
|---|---|
| D-18(b) outcome: WALL UP (402 depleted-prepay at Google AI Studio) | **NEW owner decision D-23:** (i) billing action at ai.studio (exact surface in the body), (ii) authorise one Vertex-routed POST test, or (iii) park the AI stages. Implementation stays blocked either way |
| Runner `report_unreadable`, **16th instance** | Desk #84 (no re-trigger) |
| SG-214 serve rider (SG-212 product, unserved) | **Dispatched this turn after push** (standing directives; packet drafted with this audit) |

Harness context-size reading unavailable; no conclusion made.
