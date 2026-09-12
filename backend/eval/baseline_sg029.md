# SG-029 eval baseline — synthetic Food/Medicine image corpus, one metered run

Corpus: `backend/eval/corpus/sg029/` — **7** synthetic fixtures (manifest `manifest.json`),
both categories (`food`, `medicine`) across all five case shapes (`clean`, `glare`,
`clutter`, `partial-label`, `no-date-visible`). Images are rendered deterministically by the
committed `generate.py` recipe: no personal images, no EXIF/GPS, zero `/data/storage` reads.

Runner: `backend/eval/run.py`. Offline (reproducible from the committed cache):
`venv/bin/python eval/run.py` from `backend/`. The one metered run (run from the repo root so
`.env` supplies `OPENCODE_API_KEY`, value never printed):
`SG_CONSENT=true SG_PROVIDER_ID=opencode-go venv/bin/python backend/eval/run.py --live`.

## Numbers (this run)

- `field_accuracy=0.762` over 7 fixtures
- `unknown_rate=2/5=0.400`
- `correction_rate=0/4=0.000` (`audit_event plugin.assertion.write` rows=4)
- Spend: **$0.002328** total over 7 calls; ceiling **$0.05** (never approached);
  provider-returned model `deepseek-v4-flash-vision-exp`; per-call $0.000246–$0.000441;
  latency 2.59–3.47 s; one call per fixture, no repair needed.

| fixture | class | category | score | observed reason |
|---|---|---|---|---|
| sg029-01-clean-food | clean | food | 1.000 | name + full date read exactly |
| sg029-02-clean-medicine | clean | medicine | 1.000 | name + full EXP read exactly |
| sg029-03-glare-food | glare | food | 0.000 | model read `2031-08-12` through the glare; truth authored as unknown |
| sg029-04-clutter-food | clutter | food | 1.000 | occluded date correctly reported unknown |
| sg029-05-partial-label-food | partial-label | food | 0.667 | date correctly unknown; model added `items.0.date_type` to `unknowns` |
| sg029-06-partial-label-medicine | partial-label | medicine | 1.000 | torn date correctly unknown |
| sg029-07-no-date-visible-medicine | no-date-visible | medicine | 0.667 | no date; model added `items.0.date_type` to `unknowns` |

Per-call ledger (provider-returned): all 7 calls `model=deepseek-v4-flash-vision-exp`,
`error_state=None`; costs 0.000386, 0.000307, 0.000318, 0.000326, 0.000441, 0.000246,
0.000304 USD; `sum=$0.002328`.

## Verdict

**Prompt v1 is FROZEN — no v2 is recommended.** Every fixture's item name matched
(case/whitespace-normalized) and every legible date was transcribed correctly; the only
non-perfect scores are two measurement artifacts, not prompt defects:

- **Glare rendition is too weak (corpus issue).** The `glare` fixture's semi-transparent band
  leaves enough of the date legible that the model read it correctly. The truth was authored
  as `unknown-expected` under the assumption the band fully obscured the date. The scorer
  therefore penalises a *correct* read. Follow-up (not this slice): make the glare opaque, or
  mark the date legible.
- **`unknowns` set-equality is strict (scorer issue).** For the two partial/no-date fixtures
  the model returned `["items.0.expiry_date", "items.0.date_type"]` while truth listed only
  `items.0.expiry_date`. Both entries are defensible under prompt rule 6 ("one entry per
  unrecoverable field": the date *kind* is also unrecoverable), so the set difference is a
  metric-precision question, not an extraction error. Follow-up: decide whether `date_type`
  belongs in the required unknown set.

## Metered integrity notes

- One successful run; 7 calls; ceiling printed and never approached (`$0.002328 / $0.05`).
- A first metered attempt aborted on fixture 1: the model returned two concatenated JSON
  objects (`{"type": "json_object"}{…payload…}`), which the strict parser rejects on both the
  attempt and the blind re-send. The reader's §5.3 retry now carries a real correction turn
  (`reader.repair_prompt`); the successful run did not need it (every call validated on
  attempt 1). The first attempt made 2 calls whose incurred usage was not captured by the G0
  error ledger (error rows carry `cost=0.0` when the failure precedes a completed 200 body) —
  reported as a limitation, total true spend still ≪ ceiling. Both transcripts are in
  `docs/worklogs/SG-029_verify.log`.
- No real photos; GPS stripped by construction and by the shared `redact_image` at call time.
