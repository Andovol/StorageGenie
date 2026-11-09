# SG-272 audit — gone, put back and quantities are built; the full gate has not run

**Score 85/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh`, from the receipt's `Settings:` line. Diff `391e6c8..3dcfd82`, 26 files; receipt on the notes ref, `published_head=yes`. **Partial by the 1300 s stop rule, honestly reported** (`Verification: FAIL — full gate not run`). Read: report, the backend reader-filter, lifecycle and engine hunks, the plant hook's location, `Reminder.asset_id`, `active_clause`.

## What holds

- **The stop rule was kept** at ≈1240 s: evidence and receipt published, the gate named as `REMAINING`. The opposite of SG-271 run 1.
- **G0b:** the quiet count is keyed to `non_perishable` only; a cleared perishable date lists as *No date* again (engine hunk). SG-271's dateless note at 13 px.
- **G1:** only `ARCHIVED → ACTIVE` added (`lifecycle.py`), docstring updated, `test_sg111_lifecycle.py` oracle updated (`PG-SC-11`). Dedicated routes for gone, put back, decrement, increment. Reason stored as a `gone.reason` assertion, read back by list and detail serializers; put back supersedes it.
- **Readers enumerated;** reminders list joins the asset and admits ACTIVE only (`Reminder.asset_id` is non-null, so the inner join drops nothing else); open tasks hidden, rows never mutated.
- **Cycle test with a planted break that fails** — the plant switch lives in `backend/tests/test_sg272_flow.py:160`, not in product code.
- **G3:** server-side decrement; counted vs amount rule written down (`ml/l/g/kg` and names are amounts).
- 6 backend and 14 frontend new tests FAIL on base, PASS on candidate, logs committed.

## Findings

I1. **The full gate did not run:** host suite and image proof, frontend suite, affected files twice, `ruff`, `eslint`, `tsc`, frontend build. **The deploy is held** until a gate slice passes. **Attribution: packet** — my estimate (≈1100 s) was too low a second time for a backend-plus-four-screens slice. **Destination: SG-297** (gate slice, next).

I2. **The task list filters a page after pagination, and `total` still counts hidden tasks** (`review_tasks.py`, SG-272 hunk). A page can come back short and the Inbox count can include gone items' tasks. **Attribution: coder.** **Destination: SG-297.**

I3. **That filter uses the literal `"ACTIVE"`**, not `lifecycle.active_clause()` / `lifecycle.ACTIVE`, against `PG-SC-05` and `lifecycle.py`'s own purpose. **Attribution: coder**, small. **Destination: SG-297.**

I4. **Three files beyond the named list** (`reminders.py`, `review_tasks.py`, `AppShell.tsx`), each named with its reason and inside the allowed directories, as the packet permits. No action.

I5. **The frontend FAIL log is 7519 lines.** Evidence volume. Next packets cap FAIL logs to the failing test names and first assertion.

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** prompt gap (scope against budget).
- **Root cause:** the packet bundled a lifecycle change, four screens and a quantity model into one slice under a 1300 s stop; frontend test debugging alone took ≈330 s.
- **Correction:** SG-297 runs the gate and fixes I2, I3.
- **Recurrence guard:** a slice touching more than two screens puts the full gate before the last screen goal, so a stop leaves a gated subset rather than an ungated whole.
- **Owner impact:** ≈1240 s; cost `unavailable`.

## Model note

Muse's third rotated slice: **kept a hard stop rule exactly**, careful design calls written down, honest FAIL line. One pagination slip.

## Rating

`slowest_waste`: ≈330 s frontend test debugging (async mocks, an OOM loop). Next: SG-297 on Haiku (gate and fixes), then the rider on Muse.
