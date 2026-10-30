# Second-opinion context pack — the household-and-document half of roadmap row 11

**Prepared by:** the Architect, 2026-10-30. **Committed before Phase A runs** (`SECOND_OPINION.md`, `T3`, `D555`).
**Decision:** the implementation approach for the owner-approved household-and-document stage (D6): how Documents/other gets a date, how the app lets a user classify an item, how reclassification keeps an existing date, and how the expiry-date form behaves. The owner approved the stage and its outcome; the implementation choice is the Architect's and is what this review attacks.
**Why it matters now:** the stage's work packet is not yet committed. The 0.56.0 `T3` trigger binds every project: a blind pass runs before the Architect commits a packet that introduces a design choice no earlier review covered. This is that pass.

## The problem in plain words

Roadmap row 11 is the last product row in flight. Its cosmetics countdown is built and served; its **household-and-document half** is not. The app's category list already serves **Household chemicals** and **Documents/other** as active categories, and the chat fallback for both is already live (SG-073). But:

1. **A document cannot hold a date.** The Documents/other category is marked `has_expiry=False`, so the classify path writes no date record and no manual-entry task, and the manual-entry route refuses it as "non-perishable". Its shipped 60-day and 30-day reminder windows therefore never fire. The blueprint calls Documents/other *"Long-lead windows (60/30 day) … reminder-only"*.
2. **The app has no way to put an item into either category.** The only writer of the expiry plugin's category label is the API route `POST /v1/plugins/expiry-tracker/assets/{asset_id}/classification`; the frontend has no call to it. The README documents a curl flow.
3. **Reclassifying an item would erase its active date.** `classify_asset` writes a `{"status": "unknown"}` / `needs_evidence` expiry assertion, and `_write_assertion` supersedes the previous active one — including an accepted date.
4. **An accepted date cannot be corrected in the app.** The asset page renders the manual-entry form only while the expiry assertion is `needs_evidence`; an accepted date has no edit path. The form also finds the first assertion whose path ends with `expiry_date`, which can be an old superseded record or a bare candidate field rather than the active plugin record.

The stage's outcome (D6): a Household chemicals or Documents/other item can be classified, given a date, seen in the Expiry page and reminded at its category windows; documents gain their 60/30-day windows; an accepted date can be corrected; reclassification does not lose a date. No migration; no production data write by the deploy; no provider call.

## The evidence, verbatim

**Roadmap row 11 (`docs/ROADMAP.md:29`):**

> | 11 | Opened-date countdown for cosmetics plus household and document polish | Partly built | **The countdown and the edit/clear path are built and served** (SG-240, live in the SG-241 serve; SG-256 built the edit/clear, served live by SG-257 on 2026-10-28 as container `40bee778` / image `b2c42abd`): the write path `POST /v1/plugins/expiry-tracker/assets/{id}/opened` and the pure read path `GET /v1/plugins/expiry-tracker/opened` (`backend/app/services/opened_countdown.py`), the `opened_date` assertion in `backend/app/plugins/expiry_tracker.py`, the section `frontend/src/components/OpenedCountdownSection.tsx` on `frontend/src/routes/ExpiryPage.tsx`. Still missing: a dedicated screen (it is a section on the Expiry page) and the household-and-document-polish half of the row | S |

**The blueprint's category table (`inception/generic_asset_catalog_expiry_tracker_blueprint.md:383-384`):**

> | 4 | Household chemicals | Basic expiry only | Minimal special logic |
> | 5 | Documents/other | Long-lead windows (60/30 day) | No consumption/expiry concept in the strict sense; reminder-only |

**The blueprint's date rule (`:396`):**

> If AI extraction cannot find or confidently read an expiry-relevant date, the field is left `needs_evidence` and the user must enter it manually before the asset is treated as having a resolved expiry state. Categories with no applicable expiry concept (clothing, tools, most documents) simply have no expiry assertion — the system must never force a date onto a category that doesn't logically need one, and must never fabricate a plausible-sounding date when none is visible.

**SG-073's own open question (`docs/worklogs/SG-073_report.md:129`):**

> **REMAINING:** whether Documents/other should eventually carry `has_expiry=True` so its `long-lead-60-30` windows can drive a real reminder; this slice kept the shipped `has_expiry=False` (blueprint "reminder-only") and the question is left for the owner/Architect.

**The shipped category data (`backend/app/plugins/expiry_tracker.py:127-133`, `:152-167`):**

```python
HOUSEHOLD_TIERS = {
    NotificationTier.UPCOMING.value: 30,
}
DOCUMENTS_TIERS = {
    NotificationTier.UPCOMING.value: 30,
    NotificationTier.LONG_LEAD.value: 60,
}

    "household_chemicals": Category(
        "household_chemicals",
        "Household chemicals",
        True,
        True,
        HOUSEHOLD_TIERS,
        NotificationTier.UPCOMING.value,
    ),
    "documents_other": Category(
        "documents_other",
        "Documents/other",
        True,
        False,
        DOCUMENTS_TIERS,
        NotificationTier.LONG_LEAD.value,
    ),
```

**The classify path (`backend/app/plugins/expiry_tracker.py:426-450`):**

```python
def classify_asset(db: Session, asset: Asset, category: Category, tier: str | None) -> dict[str, object]:
    if tier is not None and tier not in category.tier_defaults:
        raise ExpiryValidationError(f"Invalid notification_tier: {tier}")
    profile = category.profile(tier)
    classification = {"category": category.slug, "label": category.label, "profile": profile}
    _write_assertion(db, asset, CLASSIFICATION_FIELD, classification, "user", "accepted", None)
    expiry_assertion: Assertion | None = None
    task: ReviewTask | None = None
    observed = _observed_date(db, asset) if category.has_expiry else None
    if category.has_expiry:
        if observed is None:
            expiry_assertion = _write_assertion(
                db, asset, EXPIRY_FIELD, {"status": "unknown"}, "deterministic", "needs_evidence", None
            )
            task = _manual_task(db, asset)
        else:
            expiry_assertion = _write_assertion(
                db,
                asset,
                EXPIRY_FIELD,
                {"expiry_date": observed[0], "date_type": DateType.EXPIRY_DATE.value},
                "deterministic",
                "proposed",
                observed[1],
            )
    return {"classification": classification, "expiry_assertion": expiry_assertion, "review_task": task}
```

**The supersede rule (`backend/app/plugins/expiry_tracker.py:344-348`):**

```python
    previous = _active_assertion(db, asset.id, field_path)
    if previous is not None:
        if previous.review_state == review_state and json.loads(previous.value_json) == value:
            return previous
        previous.review_state = "superseded"
```

**The manual-entry refusal (`backend/app/plugins/expiry_tracker.py:602-610`):**

```python
def store_manual_expiry(
    db: Session, asset: Asset, entry: dict[str, object], evidence_ids: list[str] | None
) -> tuple[Assertion, list[ReviewTask]]:
    classification = get_classification(db, asset.id)
    if classification is None:
        raise ExpiryValidationError("Asset must be classified before manual expiry entry")
    category = json.loads(classification.value_json)["category"]
    if not CATEGORIES[category].has_expiry:
        raise ExpiryValidationError("Manual expiry entry is not applicable to non-perishable assets")
```

**The reminder writer (`backend/app/services/reminders/service.py:62-67`):**

```python
    for row in status["rows"]:
        asset_id = row["asset_id"]
        if asset_id in existing:
            continue
        if window_days_for(row["tier"], row["category"]) is None:
            continue
```

**The only classification writer (`backend/app/api/v1/plugins.py:125-153`):**

```python
@router.post("/assets/{asset_id}/classification")
def classify(
    asset_id: str,
    payload: dict[str, object],
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    _plugin(payload)
    asset = _asset(db, asset_id, household_id)
    try:
        category = expiry_tracker.canonical_category(payload.get("category"))
        tier = payload.get("notification_tier")
        if tier is not None and not isinstance(tier, str):
            raise ExpiryValidationError("notification_tier must be a string")
        result = expiry_tracker.classify_asset(db, asset, category, tier)
    except ExpiryValidationError as exc:
        raise _error(exc) from exc
    db.commit()
    task = result["review_task"]
    expiry_assertion = result["expiry_assertion"]
    return {
        "plugin_id": expiry_tracker.PLUGIN_ID,
        "version": expiry_tracker.PLUGIN_VERSION,
        "classification": result["classification"],
        "expiry_assertion": _assertion_view(
            expiry_assertion if isinstance(expiry_assertion, Assertion) else None
        ),
        "review_task": task.id if isinstance(task, ReviewTask) else None,
    }
```

**The frontend has no classify call.** `frontend/src/api/client.ts` exports `enterManualExpiry` (`:231`), `recordOpenedDate` (`:308`) and `clearOpenedDate` (`:316`); a grep for `classify` over `frontend/src` returns no hit. `README.md:179-186` documents the curl flow instead.

**The asset page's form condition (`frontend/src/routes/AssetDetailPage.tsx:330`, `:403-405`):**

```tsx
  const expiryAssertion = assertions.find((item) => item.field_path.endsWith("expiry_date"));
...
      {expiryAssertion?.review_state === "needs_evidence" && (
        <ExpiryEntryForm assetId={asset.id} householdId={householdId} evidenceIds={evidence.map((item) => item.id)} />
      )}
```

**The form's own find (`frontend/src/components/ExpiryEntryForm.tsx:18-19`):**

```tsx
  const expiry = assetQuery.data?.assertions?.find((assertion) => assertion.field_path.endsWith("expiry_date"));
  const state = expiry?.review_state || "needs_evidence";
```

**The served taxonomy already carries the two categories (`backend/app/plugins/descriptor.py:156-167`):**

```python
        CategoryDescriptor(
            "household_chemicals",
            "Household chemicals",
            True,
            BehaviorProfile("basic-expiry", False, "fallback"),
        ),
        CategoryDescriptor(
            "documents_other",
            "Documents/other",
            True,
            BehaviorProfile("long-lead-60-30", False, "fallback"),
        ),
```

**The last recorded live category census (`docs/worklogs/SG-240_report.md:30`, read-only, 2026-10-24):**

> (h) measured read-only in G5: 1 household, 7 ACTIVE assets, 1 accepted classification (`food_beverages`), **0 cosmetics**, **0 accepted opened dates** - the new section will render its empty state live.

**The live deploy (`docs/ratings.md`, SG-257 row; `docs/releases/2026-10-28-sg256.md`):** container `40bee778` from image `b2c42abd`; no migration; the 29-table census identical; the live clear/edit was not exercised (owner data).

## Where it lives (read these — all inside this repository)

| What | Where |
|---|---|
| category data and tier windows | `backend/app/plugins/expiry_tracker.py:106-169` |
| classify path and supersede rule | `backend/app/plugins/expiry_tracker.py:322-451` |
| manual entry and its refusal | `backend/app/plugins/expiry_tracker.py:270-287`, `:602-652` |
| reminder writer | `backend/app/services/reminders/service.py:31-83` |
| expiry engine tiers and buckets | `backend/app/services/expiry_engine.py:49-80`, `:231-314` |
| classification route | `backend/app/api/v1/plugins.py:125-172` |
| served taxonomy | `backend/app/plugins/descriptor.py:126-177`; `backend/app/api/v1/assets.py:35-67` |
| frontend API client | `frontend/src/api/client.ts:231-323` |
| asset page and date form | `frontend/src/routes/AssetDetailPage.tsx:325-469`; `frontend/src/components/ExpiryEntryForm.tsx:1-91` |
| the opened-date edit/clear pattern (already shipped) | `frontend/src/components/OpenedCountdownSection.tsx:23-181` |
| tests to extend | `backend/tests/test_plugin_expiry.py:68-160`; `backend/tests/test_sg233_reminders.py:99-150`; `frontend/src/routes/AssetDetailPage.test.tsx`; `frontend/src/components/ExpiryEntryForm.test.tsx` |
| roadmap row 11 | `docs/ROADMAP.md:29`, `:38` |
| SG-073's open question | `docs/worklogs/SG-073_report.md:129` |
| the blueprint's category table and date rule | `inception/generic_asset_catalog_expiry_tracker_blueprint.md:378-396` |
| the owner's stage approval | `docs/decisions/2026-10-30-session-approvals.md` — D6 |
| the project's sensitive areas | `AGENTS.md` — "Project rules" |

## What binds it

**Rule IDs (quoted where the rule's own text matters):**

- **G-A1** — "PROVENANCE OR IT IS NOT A FACT. Every load-bearing claim carries where it came from."
- **G-A4** — "BEFORE ASSERTING X, NAME WHAT WOULD BE TRUE IF X WERE FALSE."
- **G-A6** — "ROOT CAUSE, NOT BAND-AIDS."
- **G-A7** — "SIMPLICITY OVER MACHINERY. Prefer the smaller mechanism."
- **G-A10** — "ASK WHAT ALREADY EXISTS BEFORE DESIGNING IT … AND IT FIRES IN THE DELETE DIRECTION TOO."
- **G-K2** — "These reach the owner however trivial they look: production data destruction or any production write, secrets / infrastructure / database-role changes, anything touching a declared sensitive surface, anything irreversible or outward-facing."
- **G-K3** — "EACH PROJECT DECLARES ITS SENSITIVE SURFACES — anything reaching one needs the owner's sign-off on a written plan for that work alone."
- **PG-PR-01** — "Establish the capability model BEFORE writing a slice that depends on privileges."
- **PG-PR-03** — "A denied privileged operation is a STOP, not a signal to route around."
- **PG-PR-04** — "A packet demanding live proof of new code must say how the code becomes live — or state that the running service must not be touched."
- **PG-SC-01** — "Before drafting a defect slice, read the WRITE path and the READ path."
- **PG-SC-02** — "A slice that adds a NEW recorded field must trace it to where it is READ BACK."
- **PG-SC-07** — "Whenever a packet defines a bar, say what happens to subjects with insufficient data to be judged against it."
- **PG-SC-12** — "A proof must run against the real thing, not a stand-in the proof itself supplies."
- **PG-EV-07** — "A demand for an artifact … names the emitting code path and the read that proves it exists today."
- **PG-IC-01** — "Before shipping a packet containing a blanket exclusion … run the CROSS-PRODUCT."
- **PG-IC-07** — "Never put a fixed date or time in a packet."
- **PG-IC-09** — "A premise taken from a durable note, an earlier packet or a prior session's summary is re-verified against the current tree."
- **The project's own rule (`AGENTS.md`, "Project rules"):** "Sensitive areas: the stored photos and files, the app database, and the dispatch key and host. Every plan touching one goes to the owner alone, at every autonomy level."
- **The blueprint's date rule (`:396`, `:590`):** "the system must never force a date onto a category that doesn't logically need one, and must never fabricate a plausible-sounding date when none is visible"; "Never fabricate an expiry date; unknown must remain unknown until manually entered."

**Decisions already taken (not reopened):**

- **D-1024-8** — roadmap row 11 and its close-deploy rider are one L3 stage; SG-240/SG-241 served the cosmetics countdown, SG-256/SG-257 served the opened-date edit/clear.
- **D4** — the opened date is editable and clearable; a clear is a null active assertion through the existing write path. This is the pattern the household-and-document half should follow where a date is corrected.
- **D6** — the owner approved this stage: *"d6 - approved"*. The outcome is fixed; the implementation approach is the Architect's.
- **D-1024-17/18/19** — row 14's second provider and fallback are deferred; no local provider; actual-cost logging. Not reopened here.
- **D-1024-15/16** — no local models on the server; model and provider choices are the owner's. This stage uses no provider.

## The options as the Architect sees them (no pick shown — that is what makes Phase A blind)

### D-A — How Documents/other gets a date

- **A1 — Flip the category to `has_expiry=True`.** The category already ships `DOCUMENTS_TIERS = {upcoming: 30, long_lead: 60}` and the descriptor already says `long-lead-60-30`; the only gate is the flag. Classify would then write the same `needs_evidence` record and manual task every other dated category gets, and manual entry would accept it. The flag's name says "expiry" even though the blueprint says "reminder-only"; the disposal-guidance field stays false for documents.
- **A2 — Add a separate reminder-date path.** Keep `has_expiry=False`; add a new `plugin:expiry-tracker/reminder_date` field, a writer, a reader, a manual-entry route and a form field for documents. This keeps the word "expiry" off documents, but it duplicates the date machinery and adds a second date type the engine must learn.
- **A3 — Leave documents date-less.** Close the row as "documents are non-perishable and get no reminders"; the blueprint's 60/30 windows stay unreachable. The smallest change is no change, but it rejects the blueprint's own reading and the SG-073 question.
- **A4 — Generalise the category flag.** Rename or add a `has_validity_date`/`reminder_only` field to the `Category` contract and the descriptor, then let documents carry a date without the word "expiry". This is the most honest naming, but it touches the plugin contract, the served taxonomy and every category consumer.

### D-B — How the app lets a user classify an item

- **B1 — A control on the asset detail page.** A select of the served taxonomy's active categories plus Save; it calls the existing classification route and re-reads the asset. The page already has the asset and its assertions, so the current category can be shown.
- **B2 — A control in the review workspace.** After a candidate is committed, the review page's asset section gets the same control. It fits the import flow but only reaches newly imported items, not existing ones.
- **B3 — Keep it API-only.** The README's curl flow stays the only path; the app's category labels remain unreachable from the screen. No frontend work, but the product gap stays for the owner's daily use.
- **B4 — A settings/taxonomy editor.** A full category-management screen (row 15's territory) that also assigns categories. Larger, and it mixes row 15 into row 11.

### D-C — How reclassification keeps an existing date

- **C1 — Skip the placeholder when an active expiry exists.** In `classify_asset`, write the `needs_evidence` placeholder (or the observed-date proposal) only when there is no active expiry assertion. An accepted or proposed date survives a category change; a category with no date still gets the placeholder and task.
- **C2 — Copy the old accepted date into a new accepted assertion.** Re-assert the old value under the new classification, leaving an audit trail of the reclassification. More writes, more audit rows, and the same value twice.
- **C3 — Reset the date and require re-entry.** Keep today's behaviour: the old date is superseded, the user re-enters it. Simplest, but the UI control would silently lose the owner's data.
- **C4 — Block reclassification when a date exists.** The UI refuses to change the category until the date is cleared; the backend still allows the API path. Safer for the UI, but the API path still loses the date.

### D-D — How the expiry-date form behaves

- **D1 — Show the form for a classified category with windows; pre-fill the latest active date.** The form is rendered whenever the asset's classification profile has `tier_defaults`, regardless of the expiry state; it reads the active plugin assertion (not a superseded or bare one), pre-fills an accepted or proposed date, and Save writes an accepted date. This also gives proposed dates an accept path and accepted dates an edit path.
- **D2 — Keep the `needs_evidence` gate; add an Edit button for accepted dates.** The page shows the form only for `needs_evidence` and a separate Edit control for an accepted date; both use the same form. Slightly more UI state, but the form's existing contract stays narrower.
- **D3 — Keep the form as it is.** Accepted dates stay uneditable and documents still show no form; the backend can still accept a POST, but the screen cannot reach it.
- **D4 — A separate date-history screen.** Show every assertion and let the user pick one to re-accept. Larger, and it exposes the provenance model to the owner as a table rather than a form.

## What the pick is NOT allowed to assume

- That flipping `has_expiry` is safe for every consumer. The reviewer must trace every reader of `has_expiry` and of the expiry assertions (analytics, chat, planning, reminders, opened countdown, export) and say what changes for documents.
- That a document's OCR date is a validity date. The `_observed_date` path proposes any `20xx-xx-xx` found in OCR; for a document that may be an issue date. The reviewer must say whether the proposal is acceptable, must be suppressed for documents, or must be labelled.
- That the live household has documents or household items. The last recorded census has 1 accepted category (`food_beverages`); no later category census is recorded. The first live view may be empty.
- That the UI control is safe on the asset page without an optimistic-concurrency check. The classify route has no `If-Match`; the asset page's PATCH uses one. The reviewer must say whether the classification control needs one.
- That the stage is small. The reviewer must name what would make it two slices instead of one, or a larger design.

## What the reviewer should produce

For each of **D-A**, **D-B**, **D-C**, **D-D**: a pick, the evidence for it, one option the list misses, and the riskiest unverified premise. Then a short statement of what would make the whole approach wrong. The pick is a **recommendation**, never a decision; the owner's approval is the stage, not the implementation.
