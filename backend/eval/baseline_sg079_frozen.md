# SG-079 frozen baseline (multi-corpus runner, SG-085)

**Frozen:** 2026-09-21 by `SG-085` (D107 Phase 5 hardening, slice 1) · **Runner:** `backend/eval/run.py`
with the manifest selector (`--corpus sg079`). **Offline, `$0.000000`**: v3 scoring-only fixtures with
offline-authored `provider_output`; zero provider calls, no network, no images, no `--live`.

Command (from `backend/`): `../venv/bin/python eval/run.py --corpus sg079`.

This record is the reproduction authority for the frozen-baseline test:
`tests/test_eval_corpus.py::test_frozen_baseline_reproduces_every_selected_corpus[sg079]` parses the
fenced JSON block below and asserts byte-equal reproduction. It is **additive** — no existing baseline
file is touched.

Corpus: `backend/eval/corpus/sg079/` — manifest `count=6`, 6 fixtures, no images (scoring-only). These
carry v3 ground truth (11 transcribed-only enrichment fields) plus an offline-authored reference, so
the extended schema and unknowns-honesty are measured through the real `schemas` module, never a live
provider. Reached through the runner, the v1-compatible columns are scored; the v3-specific field
scoring lives in `tests/test_sg079_v3_schema.py`.

## Numbers (this offline run)

- `field_accuracy=1.000` over 6 fixtures
- `unknown_rate=4/4=1.000`
- `correction_rate=0/3=0.000` (`audit_event plugin.assertion.write` rows=3)
- Spend: **$0.000000** (zero provider calls; offline scoring of the committed reference)

```json
{
  "corpus": "sg079",
  "fixtures": [
    {"id": "sg079-01-clean-food", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg079-02-partial-food", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg079-03-glare-medicine", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg079-04-partial-medicine", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg079-05-clean-cosmetics", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg079-06-glare-cosmetics", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0}
  ],
  "field_accuracy": 1.0,
  "unknown_pass": 4,
  "unknown_cases": 4,
  "unknown_rate": 1.0,
  "correction_resolved": 0,
  "correction_created": 3,
  "correction_rate": 0.0,
  "audit_writes": 3
}
```

## Honesty note (non-vacuous)

These six fixtures are authored-perfect references (offline, no live call), so `field_accuracy=1.000`
is expected and is a reproduction pin, not a discrimination proof. Discrimination is proven elsewhere:
`sg029`'s `sg029-03-glare-food` scores 0.000 and two partial-label fixtures score 0.667, and
`tests/test_eval_corpus.py::test_scorer_discriminates_below_one_for_a_recorded_reason` proves the scorer
can go below 1.0. The live v3 discrimination proof is in `tests/test_sg079_v3_schema.py`.
