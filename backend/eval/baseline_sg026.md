# SG-026 eval baseline (fake only, single run — a baseline, not a target)

Corpus: `backend/eval/corpus/` — 5 smoke fixtures (clean, glare, clutter,
partial-label, no-date-visible). Runner: `backend/eval/run.py`
(`venv/bin/python eval/run.py` from `backend/`).

## Numbers (this run)

- `field_accuracy=0.833` over 5 fixtures
  (fixture scores: clean 1.000, glare 1.000, clutter 0.167,
  partial-label 1.000, no-date-visible 1.000)
- `expected_unknown_cases=3/4`
- `correction_rate=0/3=0.000`
  (`audit_event` `plugin.assertion.write` rows=3)

## Notes

- The clutter fixture carries an INTENTIONAL provider miss (bread date
  guessed instead of flagged) so the scorer is proven to discriminate:
  a scorer that cannot go below 1.000 measures nothing. The 0.833 is
  therefore a measured baseline, not a vacuous pass.
- Correction rate is 0/3 because the scoring run applies the bridge but
  resolves nothing — no tuning or resolution is performed in this slice
  (tuning here would be a scope breach per the packet).
- No real photos, no key, no network, nothing leaves the box.
