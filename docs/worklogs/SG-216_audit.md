# SG-216 audit — D-23: Google wall DOWN, G1+G2 both 200 (BYOK), rated 98

Immutable audit: base `5a69bf6` → G1 `a549bd7` → work `0266e51` (render evidence) → report `820cc9c` → receipt `46dc134` (transcript + mapped read-back; Work-HEAD 820cc9c). Local `--ff-only` to the exact tip (`46dc134` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-216 exit=0`. Receipt note `Dispatch-ID: SG-216 | Report: docs/worklogs/SG-216_report.md` IS on the remote — own read-back: `git log --notes` finds `820cc9c`, and the transcript's corrected mapped fetch (`refs/notes/sg216-readback`) reads the note back `show_exit=0`, verified by this audit. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — first clean trigger since SG-204 (no new ISS-4 instance).

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Wall DOWN (independently read):** `SG-216_g1_render_body.json` + `SG-216_g2_render_body.json` both carry `data[0].b64_json` (155,324 / 116,876 chars) + `media_type=image/jpeg`, decoding to the committed `SG-216_g1_render.jpg` (116,493 B, sha256 `faf1f85c…`) and `SG-216_g2_render.jpg` (87,656 B, sha256 `db08c866…`) — both opened by this audit: neutral gray cup / mug on white, no customer data, no PII. Discovery re-measured live: slug present (61 ids), 3 endpoints (Vertex us / AI Studio / Vertex global), `input_references` 0..14 on all three, pricing 6.6e-05/6e-05/6e-05 — matches SG-213's handed-over values.
- **Money (both caps, both accountings):** bodies report `usage.cost=0.0` + `usage.is_byok=true` with `cost_details.upstream_inference_cost` 0.045903 + 0.045597 = 0.091500. Pre-send projection from live pricing × 2 planned renders + live spend: $1.081344 daily / $1.093781125 monthly — both `proceed`, fail-closed on either cap. Actual $0.0915 upstream ($0 OpenRouter credits) vs D-20 $2.00/day and D-14 $10.00/month — both UNBREACHED on either accounting. Ledger `SG-216_ledger.tsv` 7 rows (5 free reads + 2 sends at `cost_usd=0.0`); live spend re-read `usage=0.012437125` (arc, +$0.01 vs SG-213's $0.002437125 — recorded, out of scope) with `usage_daily=0.0`, `usage_monthly=0.012437125`; external `$5 key_limit` noted (binds only if BYOK removed).
- **STOP discipline:** neither STOP family fired because both legs answered 200 with bytes — G2 ran exactly as the packet authorised (STOP-on-402/429/artifact-less wired but unneeded). 7 OpenRouter calls total (5 GETs + 2 POSTs), zero beyond the planned POSTs. G2 request body carries a real `data:image/png;base64,…` input_references payload from the committed fixture (byte-identical to SG-213's, sha256 `19731907…`).
- **Receipt self-correction (disclosed, CO-21 pattern):** the first mapped read-back used a `--ref` path git-notes re-prefixed (nonexistent `refs/notes/refs/remotes/…`) and reported no note; the Coder re-fetched mapped under `refs/notes/` and read the note back `show_exit=0` with `cat-file` proof — all committed verbatim in `SG-216_receipt.log`. No re-trigger, no loss.
- **Scope:** 27 files, all under `docs/worklogs/SG-216_*`; zero product/config/test bytes. Disposable SQLite read back in transcripts then removed, never committed. Health start/end identical `[200] {"status":"ok","db":"ok","storage":"ok"}`. Elapsed 181 s at health-end vs ≈600 s (under). No command over 60 s.
- **Secrets:** word-split literal gate 4 passes over the complete set incl. report + receipt log → exit 1 EMPTY (`SG-216_secret_grep.log`); live-credential key-value gate → exit 1, `matching_bytes=0` (`SG-216_key_grep.log`).
- **Contract:** 0.50.0 echoed with live proof.

## Rating

**Holistic: 98/100, no flag.** Both billed legs answered the owner's question end to end with the cost reported on both accountings (BYOK upstream stated, not hidden behind `cost=0`); the STOP wiring, spend guards on both caps, receipt self-correction and gates were all executed and disclosed. `deduction_attribution`: empty (nothing deducted). `slowest_waste`: `none` — every CO-79 phase output was used (discovery, spend reads, dry plan, both renders, post-spend, health, gates). Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03.

## Dispositions

| Item | Destination |
|---|---|
| D-18(b)/D-23 outcome: WALL DOWN (200+bytes both legs; BYOK $0.0915 upstream) | **NEW owner decision D-27:** recurring-spend word for the cutout/scene implementation (~$0.0459/image measured at 512) — transport precondition met, the slice stays blocked on spend authority |
| Provider attribution unknown (no `provider` sent; response carries none) | Parked — a routing probe needs another billed POST; only on owner word |
| Arc total +$0.01 between slices; $5 key limit | Record-only (measured, out of scope; key limit binds only if BYOK removed) |
| Runner clean (no misfire) | Nothing filed — ISS-4 stays at 18 on desk #84 |
| Cutout/scene implementation | Blocked on D-27, not on transport — needs its own approved slice |

Harness context-size reading unavailable; no conclusion made.
