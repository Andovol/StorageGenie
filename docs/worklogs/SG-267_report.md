result=done id=SG-267 inactive
debug-report-begin
SG-267 — Phase B critique: the first real Pantry

**Contract version: 0.56.0**

Model: unknown; reasoning effort: unknown. Process arguments and provider metadata were unavailable; system-prompt identity was not treated as measurement.

BASE REF requested: `origin/automation`.
BASE resolved commit: unknown. The supplied repository root has no `.git` entry. These findings concern the supplied files; their correspondence to the requested ref is unverified.

**STOP / Scope Deviation**
A delegated lifecycle investigation reported an attempted read of `/home/andrei/storagegenie-contract`, outside the repository, which was denied and returned no contents. That violated the repository-only read constraint and triggered the packet's denial STOP. No further tools were used after the delegated results returned. The findings already gathered are reported below, not presented as an unqualified successful run.

No database, browser, credentials, external network, health probe, restart, test execution, commit, push or publication operation was performed. I wrote nothing. This message is the only report supplied for engine publication.

**Extra Files**
Beyond the six explicitly requested documents, the following files were read, including delegated reads and content-search hits. Paths are repository-relative; search-only content inspections are included.

```text
.contract/CODER.md
.contract/SOURCE
docs/releases/2026-11-02-sg262.md
docs/packets/SG-267-second-opinion-b-critique-first-pantry.md
inception/generic_asset_catalog_expiry_tracker_blueprint.md

backend/alembic/versions/0201cf10c56c_001_core_foundation.py
backend/alembic/versions/20260908_sg013_observation.py
backend/alembic/versions/20260908_sg014_candidate.py
backend/alembic/versions/20260914_sg035_foundations.py
backend/alembic/versions/20260916_sg048_name_optional.py
backend/alembic/versions/20260923_sg100_enrich_snapshot.py
backend/alembic/versions/20261023_sg233_reminder.py

backend/app/api/v1/assets.py
backend/app/api/v1/candidates.py
backend/app/api/v1/enrich.py
backend/app/api/v1/exports.py
backend/app/api/v1/locations.py
backend/app/api/v1/planning.py
backend/app/api/v1/plugins.py
backend/app/api/v1/relations.py
backend/app/api/v1/reminders.py
backend/app/api/v1/review_tasks.py
backend/app/main.py
backend/app/models/assertion.py
backend/app/models/asset.py
backend/app/models/enrich_snapshot.py
backend/app/models/reminder.py
backend/app/models/review_task.py
backend/app/plugins/descriptor.py
backend/app/plugins/expiry_tracker.py
backend/app/plugins/registry.py
backend/app/schemas/asset.py
backend/app/services/analytics/service.py
backend/app/services/assertion_service.py
backend/app/services/asset_service.py
backend/app/services/candidates.py
backend/app/services/chat/service.py
backend/app/services/dedup.py
backend/app/services/enrich/client.py
backend/app/services/enrich/jina.py
backend/app/services/enrich/scoring.py
backend/app/services/enrich/snapshots.py
backend/app/services/expiry_engine.py
backend/app/services/fts.py
backend/app/services/google_taxonomy.py
backend/app/services/lifecycle.py
backend/app/services/opened_countdown.py
backend/app/services/planning/service.py
backend/app/services/providers/prompts/extract-food-v4.md
backend/app/services/providers/reader.py
backend/app/services/providers/schemas.py
backend/app/services/reminders/daily.py
backend/app/services/reminders/service.py
backend/scripts/backfill_asset_lifecycle.py

backend/tests/test_asset_facets.py
backend/tests/test_assets_crud.py
backend/tests/test_import_jobs.py
backend/tests/test_plugin_expiry.py
backend/tests/test_production_serving.py
backend/tests/test_runbook_commands.py
backend/tests/test_saved_searches.py
backend/tests/test_search.py
backend/tests/test_sg098_enrich_endpoint.py
backend/tests/test_sg111_lifecycle.py
backend/tests/test_sg119_brand_alternates.py
backend/tests/test_sg130_png_thumb_backfill.py
backend/tests/test_sg188_semantics.py
backend/tests/test_sg194_jobs_cursor.py
backend/tests/test_sg233_reminders.py
backend/tests/test_sg240_logging_config.py
backend/tests/test_sg240_opened_countdown.py

frontend/package.json
frontend/src/components/AssetCard.test.tsx
frontend/src/components/AssetForm.tsx
frontend/src/components/CandidateCard.tsx
frontend/src/components/ExpiryEntryForm.tsx
frontend/src/components/WebAlternates.tsx
frontend/src/components/catalog/ProductCard.tsx
frontend/src/components/catalog/catalog.test.tsx
frontend/src/components/catalog/mockProducts.ts
frontend/src/components/shell/AssetImportModal.tsx
frontend/src/components/shell/ItemInspectorDrawer.tsx
frontend/src/components/shell/drawer.test.tsx
frontend/src/components/shell/shell.test.tsx
frontend/src/routes/AnalyticsPage.test.tsx
frontend/src/routes/AssetDetailPage.test.tsx
frontend/src/routes/AssetDetailPage.tsx
frontend/src/routes/CapturePage.tsx
frontend/src/routes/CatalogPage.tsx
frontend/src/routes/ChatPage.test.tsx
frontend/src/routes/ChatPage.tsx
frontend/src/routes/ExpiryPage.tsx
frontend/src/routes/InboxPage.test.tsx
frontend/src/routes/InboxPage.tsx
frontend/src/routes/ReviewPage.test.tsx
frontend/src/routes/ReviewPage.tsx
frontend/src/routes/theme-adoption.test.tsx
frontend/src/theme/ThemeProvider.tsx
frontend/src/theme/theme.test.tsx
frontend/src/theme/tokens.css
frontend/src/types/product.test.ts
```

Correction to that inventory: `frontend/src/components/WebAlternates.tsx` was named in the requested roadmap but was not reported as a contents read by these investigations; exclude it from the extra-files list. Repository-root and `.contract` directory listings were also inspected. The denied outside-repository path returned no file contents.

**C-1: Walk, Repairs, Then Pantry**
(a) Strongest case against: “every step that cannot complete” is too narrow an acceptance standard. The code contains two capture journeys and two competing category controls; a screen-by-screen walkthrough could pass while the complete Pantry journey remains confusing.

Manual capture creates an asset directly and navigates to its detail (`frontend/src/components/AssetForm.tsx:103-122`); import creates a job and navigates to Inbox (`frontend/src/components/shell/AssetImportModal.tsx:136-157`). These are not one linear capture/inbox/review flow.

The inspector's “category” control writes `asset_type`, whereas actual expiry classification uses `plugin:expiry-tracker/classification` through a separate operation (`frontend/src/components/shell/ItemInspectorDrawer.tsx:90-107,156-167`; `frontend/src/routes/AssetDetailPage.tsx:310-341`). A user can therefore change a category-looking control without establishing C-2 Pantry membership.

The known date-task hand-off is supported by source: tasks use an asset ID, Inbox routes every subject to `/review/…`, and Review fetches a candidate (`backend/app/plugins/expiry_tracker.py:374-393`; `frontend/src/routes/InboxPage.tsx:50`; `frontend/src/routes/ReviewPage.tsx:37`).

(b) Unverified premise: removing outright blockers will make recording groceries sufficiently easy for repeated use. Static reads establish fragmentation, not its actual time or abandonment cost.

(c) Settling observation: cover manual creation and import separately, following the same item through accepted classification, date decision and finding it again. Record wrong turns and repeated entry, not only impossible steps. Keep the initial walk read-only; any observation requiring real capture or acceptance needs a separately authorized test-data boundary or the owner's exercise.

**C-2: Accepted Food Classification Only**
(a) Strongest case against: accepting an item does not classify it. Extracted `category_proposed` is gated and materialized as its own assertion; it does not become accepted expiry classification (`backend/app/services/candidates.py:76-89,850-905`). Manual creation also does not establish classification (`backend/app/services/asset_service.py:38-77`). Classification is a separate “Save category” action (`frontend/src/routes/AssetDetailPage.tsx:447-475`).

Consequently, successfully captured food can be absent from Pantry while remaining in the general catalog. Reusing the expiry response does not expose these omissions: the engine skips unclassified assets before creating either dated or unresolved entries (`backend/app/services/expiry_engine.py:263-268`).

A further exclusion risk is semantic: the UI describes Non-perishable as “No date; no expiry reminder” (`frontend/src/routes/AssetDetailPage.tsx:483-485`). Opinion: an owner might select that for shelf-stable groceries, thereby excluding them from Pantry. The inspected sources do not prove this has happened or require shelf-stable food to use that category.

(b) Unverified premise: all groceries receive accepted `food_beverages`, and the owner understands that food identity and expiry applicability are different questions.

(c) Settling observation: trace refrigerated, frozen, shelf-stable and undated groceries through both capture paths. Record accepted classification and destination after each action. Confirm that unclassified items remain findable in the general catalog with a clear route to classification; Pantry must not silently imply that these items do not exist.

**C-3: A Small Map, Not Another Plugin Yet**
(a) Strongest case against: this contradicts the current Stage C description, “a module is a registered plugin” (`docs/ROADMAP.md:43`). The actual registry registers Expiry Tracker, whose taxonomy contains all six categories (`backend/app/plugins/registry.py:81-90`; `backend/app/plugins/descriptor.py:134-173`). A view-level Pantry map creates another meaning of “module,” outside registry validation.

This is not evidence that a second plugin must be built now. It is evidence that the recommendation and roadmap need reconciliation. Opinion: an explicit presentation-level assignment is safer than claiming the plugin/module split is complete.

Keeping stored paths is supported: classification and expiry identifiers already use the existing prefix (`backend/app/plugins/expiry_tracker.py:27-32`). No objection to preserving those identifiers.

(b) Unverified premise: Stage C needs module membership only in this view, not in taxonomy discovery, backend behavior dispatch, planning or other consumers.

(c) Settling observation: check a single mapping contract for all canonical categories plus missing/unknown classification. It must give accepted food one Pantry destination, preserve general-catalog fallback, respond correctly to reclassification, and leave other dated categories' expiry behavior unchanged. State whether this is a temporary product-view assignment rather than a completed registered-module architecture.

**C-4: Separate Packs, Name Groups, Earliest-Date Action**
(a) Strongest case against: names are display labels, not stable product identity. They may be user-entered text, a filename stem, `"Imported item"`, or a provider's description such as `"unlabeled milk carton"` (`backend/app/services/asset_service.py:24-35`; `backend/app/services/candidates.py:583-589`; `backend/app/services/providers/prompts/extract-food-v4.md:19-21`). Name-only grouping can combine different products and split repeated purchases of the same product.

The attached action makes this consequential: “take one off” might target the wrong pack. Quantity is also not necessarily a pack count. The prompt transcribes counts or amounts with units, including quantities such as `500 g` (`backend/app/services/providers/prompts/extract-food-v4.md:26-32`); quantity and unit default to null (`backend/app/schemas/asset.py:8-15`). “One pack,” “one unit” and “one gram” cannot be inferred interchangeably.

Repeat capture encounters another boundary: barcode collisions create review tasks, and unresolved tasks block commitment (`backend/app/services/dedup.py:92-105,220-231`; `backend/app/services/candidates.py:966-979`). This does not prove automatic merging, but the separate-pack rule needs a working duplicate-review route.

(b) Unverified premise: equal names identify interchangeable stock, quantities have compatible meanings, and earliest printed date identifies the pack actually being consumed. Unknown dates, ties and opened packs remain unspecified.

(c) Settling observation: exercise same-name/different-product, same-product/different-name, unnamed, mixed-unit, unknown-date, opened-pack and repeated-barcode cases. Verify separate records survive capture, groups are expandable, incompatible amounts are not summed, and the action identifies its target and unit. Retain separate packs; treat name grouping as presentation, not sufficient authority for an ambiguous stock action.

**C-5: ARCHIVED, Undo Edge, Reason Assertion**
(a) Strongest case against: schema reuse is plausible, but it does not establish correct reversible behavior.

The no-migration premise is supported by committed schema: status is an existing string column; the transition policy is Python; assertions already have a string field path and text JSON value (`backend/alembic/versions/0201cf10c56c_001_core_foundation.py:38-52,126-141`; `backend/app/services/lifecycle.py:43-49`). Adding this edge and a suitably named reason assertion does not inherently require a schema migration. The deployed schema was not inspected.

However, adding the edge also enables generic PATCH restoration through the shared transition validator (`backend/app/api/v1/assets.py:432-443`). The update schema has no reason field, and the update helper commits its own transaction (`backend/app/schemas/asset.py:18-24`; `backend/app/services/asset_service.py:109-135`). Status and reason need an atomic operation, not two independently committed writes.

Relevant readers and consequences:

- Default catalog excludes ARCHIVED, so restoration makes the same record visible again (`backend/app/api/v1/assets.py:295-298`).
- Expiry and opened countdown reactivate retained dates, not fresh dates. A restored item may immediately be expired (`backend/app/services/expiry_engine.py:248-290`; `backend/app/services/opened_countdown.py:84-107`).
- Reminder listing is not lifecycle-filtered. Existing unread/read/dismissed reminders survive; same-day asset reminders suppress another creation (`backend/app/api/v1/reminders.py:75-89`; `backend/app/services/reminders/service.py:52-65`).
- Review tasks are not lifecycle-filtered or recreated by restoration. Resolved or absent date tasks do not automatically become open tasks (`backend/app/api/v1/review_tasks.py:44-80`; `backend/app/services/asset_service.py:109-135`).
- Analytics, chat and planning readmit ACTIVE items; existing suggestions remain independently listed (`backend/app/services/analytics/service.py:249-330`; `backend/app/services/chat/service.py:148-155`; `backend/app/services/planning/service.py:112-132,490-496`).

These are potential semantic failures to settle, not proof every retained reminder or task is wrong. Historical records may intentionally remain.

(b) Unverified premise: restoration means “the same pack was mistakenly marked gone,” with its old quantity, expiry and opened date still valid. It must not silently mean replenishment. Repeated cycles also need a rule for whether the accepted reason describes the current archive or the last historical archive.

(c) Settling observation: on an Alembic-migrated temporary database, test archive/restore cycles, atomic status/reason persistence, stale-version handling and failure between writes. Compare catalog, expiry, countdown, reminders, tasks, analytics and grounding before/during/after. Include zero quantity, proposed/missing dates and changed data while archived. Preserve terminal DISPOSED/MERGED behavior and unrelated assertions. No new revision is needed merely for this representation; compatibility and behavior still need proof.

**C-6: Linen Shelf Only in Pantry**
(a) Strongest case against: “fonts from the existing build” is not currently equivalent to the chosen direction. The roadmap names Fraunces and DM Sans, but existing typography uses system fonts and the package manifest contains no font dependency (`docs/ROADMAP.md:31`; `frontend/src/theme/tokens.css:32-33,75-79`; `frontend/package.json:12-30`).

Global token changes would also affect other screens: typography/colors are root variables consumed by the body, and theme selection changes document-root classes (`frontend/src/theme/tokens.css:1-47,75-79`; `frontend/src/theme/ThemeProvider.tsx:46-52`).

Captured photos remain visually heterogeneous; the live card uses evidence thumbnails and `objectFit: "contain"`, while derived imagery is explicitly mock-only (`frontend/src/components/catalog/ProductCard.tsx:6-14,55-64,121-146`). Opinion: beige cards alone may not reproduce the board's impression. This does not reopen the chosen direction or require bringing Stage D forward.
debug-report-truncated: kept=200 dropped=24 lines
debug-report-end
