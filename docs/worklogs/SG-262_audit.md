# SG-262 audit — the three SG-258 findings

**Score 96/100; no flag.** Audited from the diff `ba213ca..bb31786`. The product change is the approved E2, F1 scoped and G2; every claim checked against the diff and logs matches. Gate counts read from the logs: host 764 passed, 2 deselected; image proof 2 passed; frontend 329 passed; build rc 0. FAIL-then-PASS logs show the 3 backend and 4 frontend failures on the base. No schema, migration, model, Dockerfile or compose byte.

New test bodies read: the backend tests drive the real classify route and read back task rows; the form and review-page tests assert absence and the displayed word. No placebo.

## Findings

I1. **The review page now has no date entry and no link to the asset page.** The packet asked for this to be reported, not built. E2 accepted the asset page as the date path. **Folded into the stage C walk** (`docs/ROADMAP.md`).

I2. **Packet premise wrong:** it said a split task's origin can be another asset; the code's origin is a Candidate id, and classify does not touch it. The Coder corrected it. Packet deduction. **Closed**; the open task it leaves is I5.

I3. **The new backend tests plant the open task by hand** rather than creating it through classify (`_open_task`). The filter is the same and `task_type` matches `_manual_task`, so the behaviour holds by reading (`expiry_tracker.py:374-397`), but the path classify-to-food then classify-to-non-perishable has no direct test. The packet did not name the production writer (`PG-SC-02`). Packet deduction. **Backlog W8.**

I4. `resolved_review_task_ids` is missing from the classify response type in `frontend/src/api/client.ts:264-270`, outside the ceiling because the packet named `types.ts`. No reader consumes it. **Backlog W8.**

I5. A split-origin date task stays open when a child asset moves to a no-expiry category, as instructed. **Backlog W8.**

I6. **Found by this audit, not caused by this slice:** `frontend/src/routes/InboxPage.tsx:50` links every task to `/review/<subject_ref>` and labels it "candidate", but classify's date tasks carry an asset id as their subject, and `backend/app/api/v1/review_tasks.py:20` restricts a bare resolve on this task type. `UNVERIFIED — my inference from reading; not driven`: such a task may have no working path from the inbox. Could bear on why the catalog holds so few items. **Folded into the stage C walk.**

## Rating

Deductions are the packet's (I2, I3, I4). Elapsed 991 s against ≈900 s expected. Slowest phase the audit did not use: none over the 75.68 s full backend suite, which it did use.
