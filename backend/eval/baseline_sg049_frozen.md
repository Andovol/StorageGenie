# SG-049 frozen baseline (multi-corpus runner, SG-085)

**Frozen:** 2026-09-21 by `SG-085` (D107 Phase 5 hardening, slice 1) · **Runner:** `backend/eval/run.py`
with the manifest selector (`--corpus sg049`). **Offline, `$0.000000`**: v2 scoring-only fixtures with
offline-authored `provider_output`; zero provider calls, no network, no images, no `--live`.

Command (from `backend/`): `../venv/bin/python eval/run.py --corpus sg049`.

**Selector design call (reported per the packet):** the plan requires `sg029` + `sg079`. `sg049` HAS a
manifest (`corpus/sg049/manifest.json`, `count=3`) and is INCLUDED in the selector because exclusion
would need a second allow-list the selector would then have to maintain — "every corpus with a manifest
is addressable" is the simpler, non-hardwired rule (`G-A7`). `sg026` stays out: its 5 loose JSON files
sit at `corpus/*.json` with **no manifest**, so `available_corpora()` cannot see them (stated, not
silent).

**Two acceptance senses of "score"** (packet G1 phrases the selector as "the runner addresses any corpus";
G2 phrases it as "score the committed caches"). This runner separates them:
1. **Address** (`main --corpus sg049`) runs the full integrity gate. These fixtures carry no `image`,
   so the gate correctly FAILS LOUDLY (`missing key 'image'`, exit 1). That is the address proof.
2. **Frozen score** — the metrics below come from scoring the committed cache directly
   (`score_fixture` + `run_bridge_sandbox`), bypassing the image gate. This is the **same**
   `score_fixture`/bridge path the runner uses for `sg029`, so the metrics are the runner's own numbers,
   not a fork. The test reproduces them through that path.

This asymmetry is a finding, not a defect: the corpus was authored scoring-only (its own manifest note:
"No images and no metered provider_calls") to measure the v2 scorer; it was never an image corpus.

Corpus: `backend/eval/corpus/sg049/` — manifest `count=3`, 3 fixtures, no images. They carry v2 ground
truth (quantity/unit/asset_type) plus offline-authored references. The v2-specific field scoring lives
in `tests/test_sg049_v2_extraction.py`.

## Numbers (this offline run)

- `field_accuracy=1.000` over 3 fixtures
- `unknown_rate=1/1=1.000`
- `correction_rate=0/0=0.000` (`audit_event plugin.assertion.write` rows=0; no `needs_evidence` fixture)
- Spend: **$0.000000** (zero provider calls; offline scoring of the committed reference)

```json
{
  "corpus": "sg049",
  "fixtures": [
    {"id": "sg049-v2-01-clean-food", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg049-v2-02-partial-medicine", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg049-v2-03-clean-cosmetics", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0}
  ],
  "field_accuracy": 1.0,
  "unknown_pass": 1,
  "unknown_cases": 1,
  "unknown_rate": 1.0,
  "correction_resolved": 0,
  "correction_created": 0,
  "correction_rate": 0.0,
  "audit_writes": 0
}
```
