# SG-297 audit — the task-list fix is right; the gate found two SG-272 escapes and stopped where told

**Score 90/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high`, from the receipt's `Settings:` line (all `source=command`). Diff `e845baf..dd9b1b6` (product: `review_tasks.py`, `assets.py`, `test_sg272_flow.py`); receipt on the notes ref, `published_head=yes`. **Elapsed ≈406 s** against ≈500 s expected, measured from the trigger's own output file (created 20:01:29Z, last written 20:08:15Z); the report did not clock it. Read: report, the full product diff, `lifecycle.active_clause`, `_asset_to_dict`, `get_gone_reason`, `test_plugin_expiry.py:880–906`, the SG-271 audit I1 and SG-272 packet G0b.

## What holds

- **I2/I3 fix is correct:** `_visible_tasks()` filters `subject_ref NOT IN (non-ACTIVE asset ids of the household)` in the query, before the cursor, using `~lifecycle.active_clause()`; list and `total` share it; the post-page filter is gone. `Asset.id` is non-null, so `NOT IN` has no NULL trap.
- **FAIL-then-PASS logged** for the short page; the test drives the real route path (page 1, page 2, gone task absent).
- **R1 (ruff C901) fixed** by a verbatim extraction; behaviour unchanged (diff read).
- **Stopped exactly as the packet said** on R2 and R3, with `D443` base runs proving SG-272 caused both, and root causes read from code. eslint, tsc, build green; build written to scratch so `frontend/dist` on the host was untouched.

## Findings

I1. **R2 is not an owner decision.** `test_plugin_expiry.py:903–906` asserts SG-271 G5's rule (a cleared date is off Unresolved, `dateless == 1`). The SG-271 audit (its I1) called that a defect and SG-272 G0b fixed it on purpose; the SG-272 test asserts the fix. The old oracle should have been updated in SG-272 (`PG-SC-11`, as it did for `test_sg111_lifecycle.py`). **Destination: SG-298** — update the oracle to the SG-272 rule. **Escape on SG-272's row (coder).**

I2. **R3 is a real SG-272 defect plus a stale baseline.** `_asset_to_dict` (`assets.py:184`) calls `get_gone_reason()` per asset — the N+1 SG-136 forbids — inside a bare `except Exception` that would hide a failure as `None`. `gone_reason` on the detail payload is SG-272's specified read-back (packet G1/G2), so the baseline fixture `tests/fixtures/sg136_asset_dict_baseline.json` is updated, not the field removed. **Not an owner decision. Destination: SG-298.** **Escape on SG-272's row (coder).**

I3. **Gate steps 4–5 and the image proof did not run** (correct stop). **Destination: SG-298** runs the whole gate again on the new candidate.

I4. **Report did not clock elapsed or phases** (`CO-79`), the second Haiku report without timings. **Attribution: coder.** Next packets for Haiku require `date +%s` at each phase start.

I5. **UNCLEAR "candidate-subject tasks unaffected" is untested.** **Destination: SG-298** adds the test.

I6. **A8 "`total` excludes hidden" not observed failing** (the FAIL stopped at the first assertion). The PASS run asserts `total == 3`, so the behaviour is covered; noted only.

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** prompt gap. **Root cause:** SG-297's packet made "a test asserting old behaviour SG-272 deliberately changed" a STOP without naming which old behaviours SG-272 changed, so the Coder could not tell a stale oracle from a regression; and SG-272's own audit could not see R3 because its gate never ran.
- **Correction:** SG-298 names both and fixes them, then gates.
- **Recurrence guard:** a gate packet lists every behaviour the gated slice changed on purpose, with the old tests that assert the old behaviour, so a stale oracle is fixed in-slice, not stopped on.
- **Owner impact:** ≈406 s; cost `unavailable`.

## Model note

Haiku's fifth rotated slice and first gate slice: a clean in-scope fix, a correct stop, base-run attribution done unasked. Weakness repeats: no timings in the report.

`slowest_waste`: none — every phase's output was used.
