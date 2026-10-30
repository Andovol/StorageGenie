# SG-258 audit — the household-and-document half: Documents/other holds a date, the asset page classifies, reclassification keeps or clears, the form corrects or clears; rated 93

**Receipt verified:** notes-ref trailer `Dispatch-ID: SG-258 | Report: docs/worklogs/SG-258_report.md | Work-HEAD: a9ede3e89205c3a2ca70f2f80bf921b0725bf70d`, read from the **explicitly fetched mapped ref** (`refs/notes/storagegenie-coder-reports`). Trigger returned `result=done id=SG-258 exit=0`. The work commit `a9ede3e` and the report commit `5a1d3ab` are on `origin/automation`; the report's last line is `Verification: PASS`; the receipt echoes **0.56.0**, equal to the recorded and published 0.56.0 and the host copy.

**Diff verified (base `0d05310` → `a9ede3e`; report `5a1d3ab`):** 23 files, +13,999/−94 — the committed logs dominate; the product/test diff is ~1.5k. Product/test paths: `backend/app/plugins/expiry_tracker.py`, `backend/app/api/v1/plugins.py`, **`backend/app/services/expiry_engine.py`**, `backend/tests/test_plugin_expiry.py`, `backend/tests/test_sg233_reminders.py`, **`backend/tests/test_sg107_expiry_engine.py`**, `frontend/src/api/client.ts`, `frontend/src/components/ExpiryEntryForm.tsx`, `frontend/src/routes/AssetDetailPage.tsx`, `frontend/src/routes/ExpiryPage.tsx` and their tests. **The two bold paths are outside the packet's ceiling (finding 1).** Every other byte is in scope; zero schema, migration, model, Dockerfile, compose, lockfile, dependency, database, host, provider, container or deploy bytes; **$0**; no production row.

- **G1 — Documents/other can hold a date.** `documents_other.has_expiry=True`; the existing 60/30 `DOCUMENTS_TIERS` and `long-lead-60-30` descriptor are live; the OCR observed date is suppressed for documents (the test seeds an OCR date and observes `needs_evidence`, not `proposed`); manual entry accepts the new `valid_until` type and reads it back; the SG-073 test now asserts 200, the placeholder and the task; the 60/30 reminders are tested through `record_due`. **Met.**
- **G2 — the asset page classifies.** The control lists the served active categories and not the retired one, shows the current value, sends the active classification assertion id as `If-Match`, gets 409 on a stale token with the category unchanged, re-reads on success, shows the empty-taxonomy message, and a served-taxonomy drift test round-trips every active id through `canonical_category`. **Met.**
- **G3 — reclassification keeps a date, or clears it deliberately.** A dated-to-dated move keeps the **same assertion id, state and bytes**; a move to `non_perishable` writes a null accepted, supersedes the old row, and the engine reports `dateless`; a needs_evidence or cleared active gets the placeholder/task. The UI confirms the clear. **Met, with the task-limbo finding 3.**
- **G4 — the form corrects or clears.** The form is gated by the classification profile's `tier_defaults`, reads the exact `plugin:expiry-tracker/expiry_date` row with the latest `created_at` (never the superseded row), pre-fills, accepts a proposed date, disables a no-op Save, clears to a null active through `POST .../expiry/clear` (optional `If-Match` on the classify/manual/clear routes), and the Expiry page labels `valid_until` "Valid until". **Met, with the `ReviewPage` finding 2 and the copy finding 4.**
- **G5 — evidence.** FAIL-then-PASS on the base (`12 failed / 17 passed` backend; `16 failed / 26 passed` frontend) and the candidate (`29 passed` twice; `42 passed` twice); full gates `761 passed / 2 deselected` + image proof `2 passed`, frontend `30 files / 324 tests`; targeted lint on every changed file; health 200 start/end; receipt on the notes ref. **Met.**

**Findings, every one with a disposition:**

1. **A6 scope deviation — the engine and the coupled test.** The packet's G3.3 premise (a null accepted expiry makes `compute_status` return dateless) was **false at the base**: the engine returned `unparseable`. The Coder changed `expiry_engine.py` (10 lines, null → `dateless`) and one assertion in the coupled `test_sg107_expiry_engine.py` (the passport is now `needs_evidence` because documents get the placeholder). The report discloses both under `CO-09`/`CO-38`. **Accepted as a necessary dependent widening; the packet's `PG-SC-02`/`PG-IC-09` ceiling defect, not a Coder defect.** The engine change is the correct root fix.
2. **The `ReviewPage` form's data is lost.** The report's I3 found the second caller through a `tsc` error and made the new props optional so the review-workspace form **renders**. It does — but with no `activeAssertion`, no `categorySlug` and `hasWindows=true`, the form now shows the default `needs_evidence` state and an empty date even when the asset has a proposed or accepted expiry; the old form read the asset itself. The `tsc` proved the props, not the behaviour. **FIX QUEUED — the next stage** (the `ReviewPage` passes the active assertion/category, or the form keeps a fallback read). The packet's `PG-SC-02` omitted this caller.
3. **The reverse-move task limbo.** `classify_asset`'s move to `non_perishable` writes the null accepted but does **not** resolve the open `expiry.manual_entry` task. A dateless (`needs_evidence`) or proposed item moved to Non-perishable leaves the task open, and neither `store_manual_expiry` nor `clear_expiry_date` can resolve it (both 422 on a non-perishable category). The test covers an accepted-date move, not this one. **FIX QUEUED — the next stage** (resolve the open tasks in the reverse move; add the test). The packet's G3 omitted it.
4. **The form says "accepted" with no date.** After a clear, the active assertion is an accepted null; the form's "Expiry evidence state" reads `accepted` while the date is empty and the engine says `dateless`. The user-facing text asserts a state the inventory does not mean. **FIX QUEUED — the next stage** (show `dateless` for a null active). Minor copy, `PG-SC-02`'s last clause.
5. **Two avoidable full-gate reruns.** Run 1 was red on the coupled `test_sg107` assertion; run 2 was red on the `ReviewPage` TypeScript prop; run 3 was green. Both were discoverable in the packet's ceiling/caller list. **The `slowest_waste`, ~140 s.** The lever below removes it.

**No flag:** no safety breach (no production write, no restart, no migration, no host change, no sudo, no provider, $0) and no trust breach (the A6 deviation, the coupled test and the `ReviewPage` prop are disclosed; the logs are committed; the gates and health are quoted; the report does not claim the `ReviewPage` data).

**Holistic: 93/100, no flag.** The four product goals are met with real evidence and the report is honest; the slice loses points for the A6 scope deviation, the `ReviewPage` form's lost data, the reverse-move task limbo, the `accepted`-with-no-date copy and the two avoidable gate reruns. The packet's `PG-SC-02`/`PG-IC-09` ceiling and the G3 task omission are the Architect's; the Coder's I3 stopped at the `tsc`, and the reverse-move task was not drawn.

**RATING_ISSUE (below 95):**

1. **Failure class** — prompt gap (the A6 ceiling, the `ReviewPage` caller, the reverse-move task) + model execution (the I3 stopped at `tsc`; the task not drawn) + protocol (`PG-SC-02`).
2. **Root cause** — the packet's ceiling named neither the engine read-back nor the `ReviewPage` caller, and G3 named neither the open-task resolution nor its test.
3. **Exact correction** — the next packet names every caller/twin, every file on the read-back route and every coupled test; the reverse-move goal resolves the open tasks; the form's state shows `dateless` for a null.
4. **Recurrence guard** — the packet's `PG-SC-02`/`PG-IC-09` block: a "twins and read-back route" section before the ceiling, with the `ReviewPage` caller, the engine and the coupled tests named; the G3 task line.
5. **Owner impact** — observed 1125 s against the ≈1500 s expectation; cost `unavailable` (no provider, $0 metered); the live app was not touched; the three fixes are the next stage.

**Lever:** the packet's `PG-SC-02`/`PG-IC-09` "twins and read-back route" block — name every caller, every file the new value is read back through and every coupled test before the ceiling; the reverse-move goal names the open-task resolution; the form's state copy. **Slowest waste:** the two avoidable full-gate reruns (the coupled `test_sg107` and the `ReviewPage` TypeScript prop), ~140 s.

### Dispositions

| Item | Status |
|---|---|
| Documents/other holds a date; the 60/30 reminders; the OCR suppression; `valid_until` | **RESOLVED in code** — live after SG-259; the first live view may be empty (the owner's data) |
| The asset-page classification control; the stale-token 409; the taxonomy drift test | **RESOLVED in code** — live after SG-259 |
| The accepted date kept across dated categories; the reverse move clears | **RESOLVED in code** — live after SG-259; the task limbo is finding 3 |
| The form gate, active read, pre-fill, Accept, no-op Save, Clear, `valid_until` label | **RESOLVED in code** — live after SG-259; the `ReviewPage` data is finding 2; the copy is finding 4 |
| The A6 scope deviation (the engine + the coupled test) | **ACCEPTED** — the dependent widening; the packet guard |
| The `ReviewPage` form's data | **FIX QUEUED** — the next stage |
| The reverse-move task limbo | **FIX QUEUED** — the next stage |
| The form's `accepted`-with-no-date copy | **FIX QUEUED** — the next stage |
| The two avoidable gate reruns | **ACCEPTED as waste** — the lever above |
| The rider SG-259 | **OPEN** — the next step |
| The root-owned `~/.docker` / `DOCKER_CONFIG` | **OPEN, parked** — the engine arc |
| SG-258 receipt + rating row | **RESOLVED** — the receipt read back; this audit and the row committed this turn |
