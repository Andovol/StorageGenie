# SG-298 audit — SG-272's gate is green; run 1 was lost to a mistyped socket path

**Score 92/100; no flag** (run 2). Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh`, from both receipts' `Settings:` lines. Run 2 diff `468a17b..8be5bb8` (product: `assets.py`; tests: `test_sg272_flow.py`, `test_plugin_expiry.py`, `sg136_asset_dict_baseline.json`); receipt on the notes ref, `published_head=yes`. **Elapsed:** run 1 ≈85 s (its stamps); run 2 ≈625 s by the trigger file (20:16:11Z → 20:26:36Z) against ≈650 s expected. Read: report run 2 sections, the full product and oracle diff, `get_gone_reason`'s tail, the rail assertions' locations, gate counts.

## What holds (run 2)

- **R3:** `_gone_reason_from_assertions()` applies `get_gone_reason`'s rule to the loaded rows (accepted, latest `created_at`, JSON value, reason in `GONE_REASONS`); `JSONDecodeError` is a `ValueError`, so the malformed-value case matches; bare `except Exception` removed. **Rail:** serializer equals `get_gone_reason` on every gone and put-back case in `test_sg272_flow.py`. Fixture diff is exactly three `"gone_reason": null` lines. `test_sg136_assertion_batch.py` 4/4.
- **R2:** perishability established from code (`food` → `food_beverages`, non-empty tiers) before the oracle was changed to SG-272's rule; comment says G0b superseded G5.
- **G3:** candidate-subject test added and **fails under the named mutation**, reverted, `review_tasks.py` diff empty. **It corrected my packet** with evidence: the test cannot pass on `391e6c8`, which has no gone filter at all (`PB-1` working as designed).
- **Gate, full:** ruff, eslint (12 files), tsc, build rc 0 (`frontend/dist` untouched); host suite **801 passed, 2 deselected**; image proof **2 passed**; frontend **39 files, 359 tests**; named files twice: 8/8, 4/4, 24/24, and 14 tests in 4 files, twice.
- Phase stamps present, as asked.

## Findings

I1. **Run 1 used a socket path the packet never named and reported it as the "exact packet values".** Packet: `unix:///run/dispatch-storagegenie-SG-298/docker.sock`; run 1: `unix:///run/dispatch-storagegenie-SG-298.sock`, then a "retry" with the same wrong string, then a BLOCKED stop. **Attribution: coder.** Cost: one retry and ≈85 s. Run 1 is not rated separately (precedent: SG-271 run 1). **Model issue → owner and desk** (D25).

I2. **Test-order hazard (pre-existing, not SG-272's):** `test_sg136_assertion_batch.py` sets `DATABASE_URL` at import time; when another module imports `app.db` first, its tests open the default `sqlite:///./data/db/storagegenie.db` and fail (`unable to open database file`). The full suite orders it safely (801 passed). A test that can resolve the app's default database path is a sensitive-surface risk even when the path is absent. **Destination: `docs/backlog.md`** (W7), not stage C.

I3. **G3 base premise wrong in my packet** ("passes on the base too"). **Attribution: packet.** Caught and corrected by the Coder.

I4. **`make backend-test` ran twice** (first capture kept only the tail) — ≈88 s duplicated. `slowest_waste`.

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** model execution (run 1).
- **Root cause:** a path transcribed by hand from prose; the report then asserted conformity without comparing.
- **Correction:** retry packet carried the preflight as a literal code block plus an `echo "$DOCKER_HOST"`; run 2 passed G0 first time.
- **Recurrence guard:** every environment value a packet sets goes in a literal command block, never inline prose.
- **Owner impact:** ≈710 s across two runs; cost `unavailable`.

## Model note

Muse's fourth rotated slice. Run 2 was careful and complete: premises established before every change, a packet error corrected with evidence, a quirk diagnosed rather than papered over. Run 1 shows a new weakness: **a hand-copied value misquoted and then claimed as exact.**

`slowest_waste`: ≈88 s duplicate backend suite run for log capture.
