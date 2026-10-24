# StorageGenie — product roadmap

Date: 2026-10-23. Source: the product blueprint in `inception/generic_asset_catalog_expiry_tracker_blueprint.md` compared against the code at commit `54c387a` (branch `automation`).

Parked ideas that wait on a named trigger live in `docs/backlog.md`. This file holds what the product itself still needs.

How to read the table: Status is Built (works today), Partly built (works halfway, one piece missing), or Missing (not built). Evidence names a file or screen that proves the status. Size is Small (a day or two), Medium (several days), or Large (a project of its own). Order is the recommended build sequence.

## Next action

**Row 11 — opened-date countdown for cosmetics** is in flight (SG-240 and its close-deploy rider): record when a cosmetic was opened, then count the days against the category's after-opening window, and make the daily pass visible in the server log while the slice is there.

**Then row 14 — the remaining missing photo AI features:** a second photo reader wired into the provider router, with the local option, the fallback and the spending limits (owner, 2026-10-24 — D-1024-12). Rows 15, 16 and 8 stay parked behind it.

## Roadmap

| Order | Feature in plain words | Status | Evidence | Size |
|---|---|---|---|---|
| 1 | Create items by hand, attach photos, search them, export a backup | Built | `backend/app/api/v1/assets.py`, `backend/app/api/v1/evidence.py`, screens `frontend/src/routes/CatalogPage.tsx` and `AssetDetailPage.tsx`, test `backend/tests/test_phase0_e2e.py` | S |
| 2 | Import box with retry (start an import, watch progress, resume after failure) | Built | `backend/app/api/v1/jobs.py`, `backend/app/services/job_service.py`, screen `frontend/src/routes/InboxPage.tsx`, test `backend/tests/test_phase1_e2e.py` | M |
| 3 | Read labels automatically (text from photos, barcodes, photo dates, duplicate check) | Built | `backend/app/services/signals.py`, `backend/app/services/dedup.py`, test `backend/tests/test_signals.py` | M |
| 4 | Review desk (photo beside the proposal, accept, edit, merge, split, hold, reject) | Built | Screen `frontend/src/routes/ReviewPage.tsx`, `backend/app/api/v1/candidates.py`, test `backend/tests/test_review_split.py` | M |
| 5 | Expiry dates by hand (type the date, leave unknown when unsure, never guessed) | Built | Screen `frontend/src/routes/ExpiryPage.tsx`, form `frontend/src/components/ExpiryEntryForm.tsx`, rules `backend/app/plugins/expiry_tracker.py` | S |
| 6 | Photo reading for food and medicine (the app proposes the item and date, the user corrects it) | Built | `backend/app/services/providers/router.py`, `backend/app/services/candidates.py`, test `backend/tests/test_phase2_e2e.py` | M |
| 7 | Web lookup with sources shown (product facts carry their source, weak facts say unverified) | Built | `backend/app/services/enrich/`, `backend/app/api/v1/enrich.py`, component `frontend/src/components/WebAlternates.tsx` | M |
| 8 | Daily use-up suggestions by manual run (user confirms each one, nothing runs itself) | Partly built | `backend/app/services/planning/service.py`, `backend/app/api/v1/planning.py`, screen `frontend/src/routes/PlanningPage.tsx`; runs only when tapped, no schedule | S |
| 9 | Expiry reminders that reach the user (timed warnings before things expire) | Partly built | Math exists in `backend/app/services/expiry_engine.py` (its own header says no sender and no schedule); dashboard exists in `frontend/src/routes/ExpiryPage.tsx`; no sender and no schedule anywhere in `backend/app/` | M |
| 10 | Category chat for food and medicine (answers from owned items only, with consent step) | Built | `backend/app/services/chat/service.py`, `backend/app/api/v1/chat.py`, screen `frontend/src/routes/ChatPage.tsx` | M |
| 11 | Opened-date countdown for cosmetics plus household and document polish | Partly built | Data flag exists in `backend/app/plugins/expiry_tracker.py` (cosmetics tracks opened date, food and medicine show disposal help); proposals carry it in `backend/app/services/candidates.py`; no dedicated countdown screen for opened items | S |
| 12 | Home summaries (waste trends and category totals from the user's own data) | Built | `backend/app/services/analytics/service.py`, `backend/app/api/v1/analytics.py`, screen `frontend/src/routes/AnalyticsPage.tsx` | S |
| 13 | Places, links between items, saved searches, and advanced filters | Built | `backend/app/api/v1/locations.py`, `backend/app/api/v1/relations.py`, saved-search model `backend/app/models/saved_search.py`, filters in `frontend/src/routes/CatalogPage.tsx` | M |
| 14 | Second AI provider and local option with fallback and spending limits | Partly built | Router and limits exist in `backend/app/services/providers/router.py`; one real photo reader plus a test fake (`backend/app/services/providers/`); scene-only web reader in `backend/app/services/scene/`; no second photo reader wired | M |
| 15 | Category editor in settings (change lists without editing code) | Missing | Taxonomy is read-only through `backend/app/api/v1/plugins.py`; settings screen `frontend/src/routes/SettingsPage.tsx` has no editor | S |
| 16 | Restore from backup (bring an exported file back) | Missing | Export only: `GET /v1/export` in `backend/app/api/v1/exports.py`; no restore path | S |
| 17 | Sign-in and household enforcement | Intentionally out | Household scoping exists (`backend/app/api/v1/households.py`, `backend/app/api/v1/users.py`); no passwords by design for the single-household server | — |
| 18 | Move database and storage later (only when this computer is no longer enough) | Intentionally later | Runs on local files today (`docker-compose.yml`, local data folders); move only when scale demands it | L |

Rows 1–8, 10, 12–13 are done and need no further work. Row 9 closed on 2026-10-24 (SG-235–SG-239: the in-app daily caller, the Expiry page's Read/Dismiss, one live reminder in production). The build order from here is rows 11, 14, 15, 16, then 8 on a schedule — **row 14 first after row 11**, by the owner's priority of 2026-10-24 (D-1024-12). Rows 17–18 stay as written until the owner says otherwise.
