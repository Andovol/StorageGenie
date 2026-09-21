# SG-029 frozen baseline (multi-corpus runner, SG-085)

**Frozen:** 2026-09-21 by `SG-085` (D107 Phase 5 hardening, slice 1) · **Runner:** `backend/eval/run.py`
with the manifest selector (`--corpus sg029`; no flag defaults to `sg029`). **Offline, `$0.000000`**:
the numbers come from the committed `provider_output` cache; zero provider calls, no network.

Command (from `backend/`): `../venv/bin/python eval/run.py --corpus sg029` (or no flag — same corpus).

This record is the machine-readable reproduction authority for the v1-identical guard: the test
`tests/test_eval_corpus.py::test_frozen_baseline_reproduces_every_selected_corpus[sg029]` parses the
fenced JSON block below and asserts byte-equal reproduction. It is **additive** — `baseline_sg029.md`
(the historical metered-run narrative) is byte-untouched.

Corpus: `backend/eval/corpus/sg029/` — manifest `count=10`, 10 fixtures, 10 PNGs, `generate.py`.
Food/Medicine provider_output caches are the metered SG-029 run; the SG-036 cosmetics entries are
offline-authored references. `sg049` and `sg079` are scoring-only corpora and are frozen separately.

## Numbers (this offline run)

- `field_accuracy=0.833` over 10 fixtures
- `unknown_rate=4/7=0.571`
- `correction_rate=0/6=0.000` (`audit_event plugin.assertion.write` rows=6)
- Spend: **$0.000000** (zero provider calls; offline scoring of the committed cache)

```json
{
  "corpus": "sg029",
  "fixtures": [
    {"id": "sg029-01-clean-food", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg029-02-clean-medicine", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg029-03-glare-food", "overall": 0.0, "needs": 0.0, "unknowns": 0.0, "items": 0.0},
    {"id": "sg029-04-clutter-food", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {
      "id": "sg029-05-partial-label-food",
      "overall": 0.6666666666666666,
      "needs": 1.0,
      "unknowns": 0.0,
      "items": 1.0
    },
    {"id": "sg029-06-partial-label-medicine", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {
      "id": "sg029-07-no-date-visible-medicine",
      "overall": 0.6666666666666666,
      "needs": 1.0,
      "unknowns": 0.0,
      "items": 1.0
    },
    {"id": "sg029-08-clean-cosmetics", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg029-09-no-date-visible-cosmetics", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0},
    {"id": "sg029-10-partial-label-cosmetics", "overall": 1.0, "needs": 1.0, "unknowns": 1.0, "items": 1.0}
  ],
  "field_accuracy": 0.833,
  "unknown_pass": 4,
  "unknown_cases": 7,
  "unknown_rate": 0.571,
  "correction_resolved": 0,
  "correction_created": 6,
  "correction_rate": 0.0,
  "audit_writes": 6
}
```

## 7-vs-10 reconciliation (loud, per the packet)

`baseline_sg029.md` documents **7** fixtures (the SG-029 metered run). The corpus on disk holds **10**.
The extra three are the SG-036 cosmetics extension, added after the metered run and never metered:

- `sg029-08-clean-cosmetics` (score 1.000)
- `sg029-09-no-date-visible-cosmetics` (score 1.000)
- `sg029-10-partial-label-cosmetics` (score 1.000)

Which record covers what: **`baseline_sg029.md` covers the 7 metered Food/Medicine fixtures only**
(its header states "7 synthetic fixtures" and its table has 7 rows). **This file** covers all **10**.
No fixture is averaged across the drift: the 7 metered numbers are unchanged history, and the 10-fixture
offline numbers here are the new frozen authority. The `sg029` accuracy moved 0.762 (7-fixture metered)
→ 0.833 (10-fixture offline) because the three cosmetics fixtures score 1.000; that is the additive
extension, not a re-score of the metered seven.
