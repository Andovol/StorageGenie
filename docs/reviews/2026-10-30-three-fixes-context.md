# Second-opinion context pack — the three SG-258 fixes

**Prepared by:** the Architect, 2026-10-30. **Committed before Phase A runs** (`SECOND_OPINION.md`, T1/T3, `D555`).
**Decision:** the next stage after SG-258 — the three findings the SG-258 audit (93) left.
**Why it matters now:** the household-and-document half is live (SG-258 93 + SG-259 96, release `release-2026-10-30-sg258`); three live-code defects remain; the next stage is a new stage and its rider touches the live host, so the project's second-opinion rule (T1/T3; the live host) requires this blind pass before the D7 decision.

## The evidence, verbatim

**The SG-258 audit (93), the three findings:**

> (2) the `ReviewPage` form's data is lost — the optional props render but the review-workspace form shows the default `needs_evidence` and an empty date because the caller passes no active assertion/category; the Coder's I3 only caught the `tsc` prop — FIX QUEUED next stage; (3) the reverse-move task limbo — `classify_asset`'s move to non_perishable writes the null accepted but does not resolve the open `expiry.manual_entry` task, and clear/entry both 422 on non-perishable — FIX QUEUED next stage; (4) the form says `accepted` with no date after a clear — FIX QUEUED next stage (show `dateless`).

**The review page's caller (`frontend/src/routes/ReviewPage.tsx:60`):**

`...{assetId && <ExpiryEntryForm assetId={assetId} householdId={householdId} evidenceIds={candidate.evidence_ids} />}...`

It passes no `activeAssertion`, no `categorySlug`, no `hasWindows`.

**The form's defaults (`frontend/src/components/ExpiryEntryForm.tsx:21-53`):**

`activeAssertion = null, categorySlug = "", hasWindows = true`; `if (!hasWindows) return null;`; `const state = activeAssertion?.review_state || "needs_evidence";`; the date is pre-filled only from `activeAssertion`.

**The working caller (`frontend/src/routes/AssetDetailPage.tsx`):** it passes the active expiry assertion, the classification category and the profile `hasWindows` to the form; that path shows the real state.

**The reverse move (`backend/app/plugins/expiry_tracker.py`, `classify_asset`):** when the new category is `non_perishable` and an active expiry exists, it writes a null accepted expiry and supersedes the old row; it does not resolve the open `expiry.manual_entry` task. `clear_expiry_date` and `store_manual_expiry` do resolve the task; `store_manual_expiry` refuses a `non_perishable` category (422).

**The form's state (`frontend/src/components/ExpiryEntryForm.tsx:53`):** a null accepted assertion is `review_state="accepted"`; the form shows `accepted` with an empty date.

**The live context:** container `10f7fc58` / image `d620e39d`; 29-table census identical; health 200; the served code/bundle/taxonomy carry the SG-258 controls.

## Where it lives

| What | Where |
|---|---|
| the review page's caller | `frontend/src/routes/ReviewPage.tsx:60` |
| the form's props/state | `frontend/src/components/ExpiryEntryForm.tsx:21-53` |
| the working caller | `frontend/src/routes/AssetDetailPage.tsx` (the `ExpiryEntryForm` render) |
| the reverse move | `backend/app/plugins/expiry_tracker.py` — `classify_asset` |
| the clear/entry task resolution | `backend/app/plugins/expiry_tracker.py` — `clear_expiry_date`, `store_manual_expiry` |
| the SG-258 audit | `docs/worklogs/SG-258_audit.md` |
| the SG-258 report | `docs/worklogs/SG-258_report.md` |
| the SG-258 rating | `docs/ratings.md` — the SG-258 row |
| the live release | `docs/releases/2026-10-30-sg258.md` |
| the project's rules | `AGENTS.md`; `STATE.md` |

## What binds it

**Rule IDs:** `G-A1`, `G-A4`, `G-A6`, `G-A7`, `G-A10`, `G-K2`, `PG-PR-01`, `PG-PR-03`, `PG-PR-04`, `PG-SC-01`, `PG-SC-02`, `PG-SC-07`, `PG-SC-12`, `PG-EV-07`, `PG-IC-01`, `PG-IC-07`, `PG-IC-09`; `SECOND_OPINION.md` T1/T3 (`D555`).

**The project's own rules:** the stored photos and files, the app database, and the dispatch key and host are sensitive surfaces; every plan touching one goes to the owner alone; the live host rider is the only host action.

**Decisions already taken (not reopened):** D6 (`"d6 - approved"`, 2026-10-30) approved the household-and-document stage; SG-258 (93) + SG-259 (96) are live; the three findings are the next stage; the release `release-2026-10-30-sg258`.

## The options as the Architect sees them (no pick shown — that is what makes Phase A blind)

**D-E — the review workspace's date form:**
- **E1 — Pass the data:** the review page (or the form) fetches the asset and passes the active assertion, the category and `hasWindows`; the form shows the real state there.
- **E2 — Hide the form:** the form's default `hasWindows` becomes false; the review page passes none; the asset page is the only date-entry surface.
- **E3 — Leave it:** the review page keeps showing the default `needs_evidence` and an empty date.

**D-F — the reverse move's task:**
- **F1 — Resolve the task in the move:** `classify_asset`'s move to `non_perishable` resolves the open `expiry.manual_entry` task(s), as `clear_expiry_date`/`store_manual_expiry` do.
- **F2 — Add a clear/entry path for `non_perishable`:** the clear/entry routes accept a `non_perishable` asset with a null/active date, so the user can clear or re-enter.
- **F3 — Block the move:** the classify route refuses the move to `non_perishable` while a manual-entry task is open.

**D-G — the dateless copy:**
- **G1 — Show `dateless`:** the form shows `dateless` when the active assertion is a null accepted (or its value has no date).
- **G2 — Show "No date":** the form shows "No date" / the empty input with a "Date cleared" message.
- **G3 — Leave `accepted`.**

**D-H — the stage shape:**
- **H1 — One work slice + one rider:** the three fixes in one small slice, then the standing rider.
- **H2 — Three tiny slices + one rider:** one fix per slice, then the rider.
- **H3 — Fold into the next row-14 stage:** the fixes ride the next row-14 work; no separate stage.

## What would make the whole approach wrong

If the three findings are not real defects — the review workspace's form is a secondary path no owner uses, the reverse move's open task is harmless because the inbox can resolve it, and `accepted`-with-no-date is acceptable copy — then the next stage is busywork and the right answer is E3/F2/G3/H3. If the `ReviewPage` needs a new asset query, the fixes are not one small slice. If the rider is not needed because the fixes are docs-only, H1's rider is wrong.
