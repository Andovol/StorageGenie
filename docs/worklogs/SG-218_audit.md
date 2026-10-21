# SG-218 audit — D-27 pilot render 2 of 10 RENDERED on a second asset, rated 98

Immutable audit: base `848d951` → G1 `d068ad5` (driver + plan, no send) → work `3a46fcf` (render) → report `e86d183` → receipt `6d46ebe` (transcript + mapped read-back; Work-HEAD e86d183). Local `--ff-only` to the exact tip (`6d46ebe` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-218 exit=0`. Receipt note `Dispatch-ID: SG-218 | Report: docs/worklogs/SG-218_report.md` IS on the remote — own read-back finds `e86d183` via `git log --notes`; per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — third clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **RENDERED (independently read):** `SG-218_render_result.json` = status `rendered`, HTTP 200, `image_model=google/gemini-3.1-flash-image`, `transport=image_api`, Evidence `01a15fdc-f5b6-…`, ledger `01a15fdc-f5be-…`, 731,496 B JPEG sha256 `ce4794a2…` — matches the committed `SG-218_render.jpg` byte-for-byte (re-hashed by this audit). Opened by this audit: PIKOK pork-meat tin on wood, label text fully preserved and legible, linen outside the label area, no people, no PII. Asset faithfulness high; scene quality high — concurring.
- **Second asset, pilot-unused photo:** enumeration live (6 candidates, 3 eligible; Miso Soup excluded as SG-217's photo, SG-159 precedent photos excluded by storage key). Pick Costiță de porc (evidence `01a0c4a1-ad90-…`, 1,259,505 B, sha `f9d71a40…`), opened pre-send; request body carries its real data-URL (1,679,362 chars).
- **Money (triple bound, both accountings):** authority cap = min(daily 2.00, monthly 9.98756288, pilot 9×0.17028=1.53252) = 1.53252; guard inputs live (spent 0.012437125, 4 unknown-cost rows, worst 0.17028) → projection 0.86383713 ≤ 1.53252 `proceed`. Synthetic over-cap and no-authority refusals proven. Actual: credits `0.0`, upstream `0.068256` (1120 image tokens) — under on both accountings; daily 0.22794/2.00, monthly 0.240377125/10.00, pilot 2/10. One POST total.
- **Findings (all disclosed with destinations, none deducted):** F-SG218-6 — the product path writes one `audit_event` row with the Evidence commit (ids quoted); the packet's "rows ONLY" line was one row short as literally worded, and bypassing it would have meant bypassing the product path the packet demands — the Coder chose correctly and corrected SG-217's "no other table written" with the live id. F-SG218-4 — attempt marker is container-local; durable guards are the live pilot count + authority (no re-run attempted). F-SG218-2 — 2580-token bound re-derived live (baseline max(1290, 1120)×2), not inherited.
- **Scope:** 19 files — driver `backend/scripts/sg218_render.py` (lane tooling) + `docs/worklogs/SG-218_*`; zero product/test bytes, no migration, no restart. Contract 0.50.0 live proof. Elapsed 267 s vs ≈600 s; render 8.8 s vs 300 s bound.
- **Secrets:** literal gate 3 passes exit 1 EMPTY; live-value key gate `matching_bytes=0` over evidence root and full worklogs tree.

## Rating

**Holistic: 98/100, no flag.** Second green render on a second asset with the same triple-bound discipline; every packet premise re-verified live; the one literal-vs-intent collision (audit_event row) resolved the right way and disclosed with the correction to the prior audit. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used (enumeration, plan, guard, render, post-spend, health, gates). Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| Pilot 2/10 RENDERED | D-27 continues — 8 of 10 remain (STATE ordered work) |
| audit_event row (packet wording one row short) | Recorded here + in the packet lineage; future scene packets name Evidence + ledger + audit_event |
| Attempt-marker durability | Parked — a driver hardening for a future slice if re-runs ever occur |
| Resolution pin / cutout / UI wiring / routing | Parked — each needs its own owner word (product-code or billed scope) |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
