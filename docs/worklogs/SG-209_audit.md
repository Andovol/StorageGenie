# SG-209 audit — D-17 muse probe: STOP, endpoints [] re-measured identical, $2.00 unspent, rated 98

Immutable audit: base `0bd5518` → work `f67d8f7` (11 evidence files, +605, zero product/config/test bytes) → report `0add225` → receipt `0858098` (+final gate re-run). Local `--ff-only` to the exact tip (`0858098` == origin/automation at pull); tree clean. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-209 | Report: docs/worklogs/SG-209_report.md | Work-HEAD: f67d8f7...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Twelfth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **STOP verdict (independently confirmed):** `SG-209_g1_endpoints_body.json` = `{"id":"meta/muse-image","endpoints":[]}` (39 bytes) — the live HTTPS body, committed raw. Catalogue body lists 61 ids incl. `meta/muse-image` (row exists; zero endpoints, `supported_parameters` `{}` — the ONLY empty one of 61). Controls in the same run, same key, same client: Google `gemini-3.1-flash-image` 3 endpoints (input_references 0..14, priced), Flux `flux.2-pro` 1 endpoint (input_references 0..8, $0.03/MP). The emptiness is model-specific, not an API gap — the two controls are what turn the observation into a verdict.
- **F-SG209-1 (packet premise false — mine):** "SG-159 read the lane's image path, this probes a different surface" is wrong; both read `https://openrouter.ai/api/v1/images/models/meta/muse-image/endpoints`, byte-identical bodies 5 days apart. The probe's reason for existing dissolves into re-measurement — which is still the correct slice (only a live read could have shown it), and the STOP it executed is the packet's success path. Recorded, attribution `packet`.
- **Money:** ledger TSV 4 rows, all GET/200/`cost_usd=null`; 0 POSTs, 0 billed, actual $0.000000; $2.00 cap UNSPENT (no projection was computable — no pricing lines — and none was needed). Guard selftest (synthetic over-cap refusal + under-cap proceed) + real refusal path executed against the empty-endpoints body, transcripts committed. The never-on-live-pricing caveat is stated loudly in the report (finding #4) — honesty, not vacuity.
- **Secrets:** `PG-SC-05` word-split literal gate re-run over the complete evidence set incl. report + receipt log → exit 1 EMPTY (`SG-209_secret_grep.log`). Bodies key-redacted at capture; header assembled from fragments in-driver. Clean.
- **Scope:** 11 files under `docs/worklogs/SG-209_*` (+`SG-209.log`, same root); zero product/config/test bytes. Disposable SQLite read back then removed, not committed. Zero production writes. Health identical start/end. Elapsed 476 s vs ≈600 s (under). No command over 60 s.
- **Contract:** 0.50.0 echoed with live proof.

## Rating

**Holistic: 98/100, no flag.** The STOP was executed, not approximated: discovery bodies raw, controls proving specificity, spend exactly zero with the cap reported unspent, the synthetic-only guard branch disclosed rather than hidden. `deduction_attribution`: packet (F-SG209-1 — the probe still had to run to learn it). `slowest_waste`: `none`. Guards: PG-EV-02/06/07/09; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03.

## Dispositions

| Item | Destination |
|---|---|
| D-15 transport (`muse-image` via OpenRouter direct) | **REFUTED by measurement** — catalogue row exists, zero endpoints, zero declared params; SG-159's chat no-artifact finding stands. Cutout/scene have no implementable transport |
| Next transport pick | **NEW owner decision (blocking AI work):** (a) fix Google quota/billing (unsuspend D-1009-10), (b) name another measured-working model (e.g. `google/gemini-3.1-flash-image`, `black-forest-labs/flux.2-pro` — both declare `input_references` with pricing on record), or (c) park the AI stages. No slice runs without a pick (`PG-IC-03`) |
| D-14(c-monthly) | Still open (no monthly decision made; probe cap unspent, not converted) |
| Serve rider (SG-207+SG-208 product, live!=tree) | **SG-210 dispatched this turn after push** (standing directive; packet drafted with this audit) |
| Runner `report_unreadable`, **12th instance** | Desk #84 (no re-trigger) |
| npx absent / rootless-/tmp note (F-SG209-2) | Lane shape, reconciled in-slice; recorded for provisioning awareness |

Harness context-size reading unavailable; no conclusion made.
