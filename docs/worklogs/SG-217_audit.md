# SG-217 audit — D-27 pilot render 1 of 10 RENDERED via the product path, rated 98

Immutable audit: base `6e36e91` → G1 `14b18bf` (driver + plan, no send) → work `24ba81e` (render + report) → worklog `c632c9d` → receipt `121dcae` (transcript + mapped read-back; Work-HEAD c632c9d). Local `--ff-only` to the exact tip (`121dcae` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-217 exit=0`. Receipt note `Dispatch-ID: SG-217 | Report: docs/worklogs/SG-217_report.md` IS on the remote — own read-back: `git log --notes` finds `c632c9d`, and the transcript's mapped fetch reads it back `show_exit=0`, verified by this audit. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — second clean trigger in a row (no new ISS-4 instance).

## Verified (parsed from the committed artifacts, not the report's §(c))

- **RENDERED (independently read):** `SG-217_render_result.json` = status `rendered`, HTTP 200, `image_model=google/gemini-3.1-flash-image`, `transport=image_api`, Evidence `01a15f6f-13ba-…`, ledger `01a15f6f-13c4-…`, 703,036 B JPEG sha256 `41d619db…` — matches the committed `SG-217_render.jpg` byte-for-byte (re-hashed by this audit). Opened by this audit: Vitasia Miso Soup 500 g pack on a kitchen counter, label text fully preserved and legible, props outside the label area, no people, no PII. Asset faithfulness high; scene quality high — concurring with the report's judgment.
- **Real photo in the request:** `SG-217_request.json` (1,708,028 chars) carries a `data:image/` data-URL payload; the picked Miso Soup photo (evidence `01a0c4a0-…`, 1,280,694 B, sha `71901cac…`) was enumerated live (6 candidates, 4 eligible, SG-159 photos excluded by storage key) and opened before the send.
- **Money (triple bound, both accountings):** authority cap = min(daily remainder 2.00, monthly remainder 9.98756288, pilot remainder 10×0.17028=1.7028) = 1.7028; guard inputs live (`spent=0.012437125`, 4 unknown-cost rows, worst 0.17028) → projection 0.86383713 ≤ 1.7028 `proceed`. Synthetic over-cap (`2.87308 > 1.7028`) and no-authority refusals proven in the committed logs. Actual: OpenRouter `cost=0.0`, upstream `0.068184` (1120 image tokens) — under the 0.17028 projection on both accountings; daily 0.159684/2.00, monthly 0.172121125/10.00, pilot 1/10. One POST total, zero beyond planned.
- **DB post-state (both directions):** evidence 18→19 (scene_render 1→2), openrouter provider_call 8→9, null-cost 4→4, known sum unchanged 0.012437125. Exactly 1 new Evidence + 1 new ledger row, ids quoted, left in place; no UPDATE/DELETE. The ledger row-level `model` column carries the orchestrator (precedent since SG-158) while `output_payload` preserves `image_model=google/…` + full usage — no information loss, disclosed.
- **Findings closed in-slice:** F-SG217-1 explains SG-216's +$0.01 (pre-pilot Muse row `01a13137-fe82…`, 2026-10-12, predates D-27, excluded by date, left in place). F-SG217-3 bound choice disclosed with headroom math (2580 tokens ≈ 2× the path's ~1K default, covers measured 1120; 8192 would refuse on pre-existing null rows and prove nothing). F-SG217-6 health-start deviation disclosed — end probe `[200]` + `docker inspect` (container up 3 days, healthy) with no restart and no served-code change leaves nothing the missing start probe could have distinguished.
- **Scope:** 19 files — driver `backend/scripts/sg217_render.py` (lane-run tooling, NOT served code) + `docs/worklogs/SG-217_*`; zero product/test bytes, no migration, no restart. Contract 0.50.0 echoed with live proof.
- **Secrets:** word-split literal gate 5 passes exit 1 EMPTY; live-value key gate `matching_bytes=0`. Elapsed 326 s at health-end vs ≈600 s (under). No command over 120 s; render 10.0 s vs 300 s bound.

## Rating

**Holistic: 98/100, no flag.** The product path rendered end to end on the first pilot render with the spend authority enforced on three bounds simultaneously, every premise re-verified live, both historical mysteries (the +$0.01, the 8192 refusal) explained with evidence instead of smoothed over, and all deviations disclosed with the reason the outcome is unaffected. `deduction_attribution`: empty (nothing deducted). `slowest_waste`: `none` — every CO-79 phase output was used (enumeration, plan, guard, render, post-spend, health, gates). Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| Pilot render 1 RENDERED (product path proven) | D-27 continues — 9 of 10 renders remain (STATE ordered work) |
| Resolution unpinned (provider default; 512 pin would need product code) | Parked — a pin slice needs an owner word (product-code change) |
| Cutout pipeline + UI wiring | Separate slices, each needs its own owner word (never approved) |
| Endpoint route unobserved | Parked — routing probe needs another billed POST, owner word only |
| Pre-pilot Muse ledger row | Record-only — predates D-27, excluded by date, left in place |
| Runner clean (no misfire) | Nothing filed — ISS-4 stays at 18 on desk #84 |

Harness context-size reading unavailable; no conclusion made.
