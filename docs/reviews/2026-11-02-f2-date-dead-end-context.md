# Second-opinion context pack — the AI-no-date dead end (F2)

**Prepared by:** the Architect, 2026-11-02. **Committed before Phase A runs** (`SECOND_OPINION.md`, T3, `D555`).
**Decision:** how a reviewer gets past an imported item whose date the AI could not read.
**Why it matters now:** stage C, the first real Pantry, cannot work while a captured item can get stuck for good. The next build slice, SG-270, fixes this, and no earlier review covered this design.

## The problem in plain words

The owner photographs a grocery. The AI reads it but cannot read a date. The app opens a "date needed" task on the proposed item (the *candidate*) and refuses to accept the candidate until that task is closed. Nothing on any screen can close it. The item never enters the catalog.

## The evidence, verbatim

**The walk, `docs/worklogs/SG-269_findings.md`, row F2:**

> The candidate carries an open `expiry.manual_entry` task and a URL-style link back to the same Review page. The Inbox Resolve button sends a bare resolve, which is refused; Accept is refused while the task is open. There is no date field on the candidate review card and no candidate-level manual-date route.

> `SG-269_j3j4.log`: task subject is the candidate id; bare resolve `422` "task requires the expiry_date"; accept `409` "Candidate has unresolved review tasks"; candidate fields are `display_name`, `asset_type`, `status` only.

**The gate that refuses a bare resolve, `backend/app/api/v1/review_tasks.py:15-19`:**

> SG-188 (D7): data-required task types cannot be closed by a bare resolve. `expiry.manual_entry` is satisfied only by real manual-entry data (`store_manual_expiry` writes the accepted expiry assertion, resolves the task(s) and answers `resolved_review_task_ids`); a bare `{}` resolve would close it while the lived assert stays `{"status": "unknown"}`.

**Owner's direction, 2026-10-30:** *"The presentation is everything, the app should have a beautiful design and be very easy to use."* Stage C approval, 2026-11-02: *"d14 ok"*. The stage's goal, `docs/ROADMAP.md`, stage C row: *"One styled Pantry you can use end to end: see it, use it up, quantities quick to change"*.

**Measured in the code on 2026-11-02 (hypotheses; check them):**

- Three producers of `expiry.manual_entry`: `backend/app/services/candidates.py:757-769` (subject is the candidate id); `backend/app/plugins/expiry_tracker.py:374-397` `_manual_task` (subject is the asset id), used by `classify_asset` and `apply_extraction_result`; `backend/app/plugins/expiry_tracker.py:400-425` `apply_extraction_result` is a mapping for an asset whose extraction needs evidence, and writes `{"status": "unknown"}` with `needs_evidence`.
- Two gates block a commit on any open task: `backend/app/api/v1/candidates.py:50-51` and `backend/app/services/candidates.py:969-979`.
- `store_manual_expiry` refuses an unclassified asset (`expiry_tracker.py:708-710`). Accepting a candidate does not classify (`candidates.py:850-905`). A date form on the asset page renders only after a classification exists (SG-269 row F4, `frontend/src/routes/AssetDetailPage.tsx:540-550`).
- A move to a no-expiry category resolves the asset's open date tasks (`expiry_tracker.py:487-498`), so a shelf-stable item can legitimately never have a date.
- A manual date on an asset also resolves date tasks on split origins sharing its evidence (`expiry_tracker.py:660-702`, `:736-755`).
- The review page has no date entry and no link to the item (`docs/worklogs/SG-262_audit.md`, I1; the date form was removed from it deliberately by SG-262, because it had no asset data).
- `frontend/src/components/CandidateCard.tsx:48` disables Accept when the candidate lists open tasks.
- Live data, `docs/worklogs/SG-269_audit.md`, I1: *"The live app has a provider and 10 candidates against 7 assets"*. How many live candidates hold this task is **not known**; a read of the live database was not part of this review.

## Where it lives

| Thing | File |
|---|---|
| Producers and gates | `backend/app/services/candidates.py` (`:715-775`, `:850-990`, split `:1089`, merge near `:1277`), `backend/app/api/v1/candidates.py:30-78` |
| Date writing, tasks, classify | `backend/app/plugins/expiry_tracker.py:374-504`, `:610-757`; `backend/app/api/v1/plugins.py:184-227` |
| Bare resolve | `backend/app/api/v1/review_tasks.py` |
| How the Expiry page reads an item | `backend/app/services/expiry_engine.py:83-170`, `:263-268` |
| Screens | `frontend/src/routes/ReviewPage.tsx`, `frontend/src/components/CandidateCard.tsx`, `frontend/src/routes/InboxPage.tsx`, `frontend/src/routes/AssetDetailPage.tsx:447-475`, `:540-550` |
| The walk | `docs/worklogs/SG-269_findings.md`, `SG-269_j3j4.log`, `SG-269_j3b.log` |

**Do not read `STATE.md`, `docs/decisions/` or `docs/backlog.md`.** They are not needed here, and this keeps the pass blind.

## What binds it

- **Decided, not reopened:** SG-188's rule that a bare resolve cannot close a date task while the stored value stays unknown (an objection goes under the whole-design check, labelled as such). The asset page stays the date path where asset data is needed (SG-262).
- **Other slices own these and they are not designed here:** F4 keeping the AI's proposed date, F5 and F12 using the AI's proposed category, F7 renaming a control. They run in the slice right after this one.
- **Same slice as this fix:** F1 listing a job's candidates in the inbox with a Review link, F6 linking asset date tasks to the item's page and hiding Resolve where it is always refused, a link from review to the item.
- **Sensitive surface:** the app database (`AGENTS.md`). Existing rows must stay valid; a schema migration must be named and justified.
- **No new provider or image spend** in this stage.

## The options as I see them, without a pick

**Q1 — the design.**

| Option | What happens |
|---|---|
| **O1 Date on the review page** | Add a date entry to the review page and a candidate-level route. The date goes with the candidate; the task closes; Accept then works. |
| **O2 Accept, carry the task** | The date task stops blocking Accept. On commit the task moves to the new item, by re-pointing it or by closing it and opening the asset's own. The date is then entered on the item's page. |
| **O3 Explicit "no date" at review** | The reviewer states there is no date, which closes the task with that reason. Accept works. No task follows the item. |
| **O4 Stop opening the task on the candidate** | The candidate producer no longer opens a blocking task; the commit calls the existing asset-side mapping (`apply_extraction_result`) instead. Candidates already holding such a task need their own answer. |

**Q2 — the edges of whichever design.** Per your Q1 pick, say what should happen for each: a candidate that also holds `candidate.multi_item`; split children and origins; merge; hold and reject; an edit decision; a candidate that turns out to be `duplicate_of_asset`, where no new asset exists to carry a task to; candidates already open on the live database; and the same item while it is still unclassified.

## What would make the whole approach wrong

Name it if the dead end is better removed somewhere else: for instance, if the date should not be required at this point in capture at all, or if this flow should not exist in this form for a Pantry where shelf-stable food carries no date.
