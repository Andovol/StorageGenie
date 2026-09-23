# Blueprint coverage review — missed features (2026-09-23)

**Source:** `inception/generic_asset_catalog_expiry_tracker_blueprint.md` v3 (39,790 B, read in full 2026-09-23).
**Method:** every item below was checked against the tree with a targeted grep the same day; "absent" means zero hits in the stated scope, quoted per row. SG-098 was in flight (reads only, no writes); nothing below depends on its outcome.
**Status:** findings only — no design, no slices proposed. Next session reviews this file and scopes the work.

## Genuinely missed (never decided away)

| ID | Blueprint item | Absence proof (2026-09-23) |
|---|---|---|
| **G1** | Journey F: tiered expiry reminders + notification engine (§2.2, §3.1, §9.1) | Tiers exist as DATA only (`backend/app/plugins/expiry_tracker.py` tier profiles, `descriptor.py` vocabulary); `notif\|remind\|tier` over `backend/app` returns only tier-profile plumbing — no scheduler, no sender, no reminder surface |
| **G2** | Expiry dashboard, urgency-sorted (§11.2 screen 7) | No dashboard route/component in `frontend/src`; independently proved absent before (F-SG096-1 lineage: F-SG066-1) |
| **G3** | Location tree: `location` + `asset_location` entities, §9.2 storage locations, "locations" on asset detail (§4.2, §11.1) | `relation\|location` over `backend/app/models` → no files found |
| **G4** | Asset relations: `asset_relation` entity, "relationships" on asset detail (§4.2, §11.1) | Same grep → no files found |
| **G5** | Lifecycle states DRAFT → PENDING_REVIEW → ACTIVE → ARCHIVED → DISPOSED + MERGED redirect (§4.3) | `backend/app/models/asset.py:23`: `status` is a free string defaulting `"ACTIVE"` — no state machine |
| **G6** | Merge action: decision lists "accept, edit, split, merge, hold, reject" (§7, journey A) | `backend/app/api/v1/candidates.py:17`: actions `accept/edit/hold/reject` + separate `split` (`:92`); `split_candidate` exists in `candidates.py`, no merge path |
| **G7** | HEIC/HEIF ingest (§5.2 step 1: JPEG/PNG/WebP/HEIC/HEIF/TIFF/PDF) | `heic\|heif` over `backend/` → no files found (TIFF repaired SG-019; HEIC never added) |

## Decided away (not missed — do not re-propose without reopening)

- Second cloud provider (`D83`, one provider only) · automatic planning schedule (Phase 3 non-goal; `ChatPage.tsx:98` "sends nothing on a schedule") · semantic/similarity search (deferred Phase 2+, explicit) · Context Scene / image generation (§1.4 non-goal — "optional presentation plugin only, later")
- Governance complete: `docs/adr/ADR-001`…`ADR-010` all exist; no Stage-1 guardrail evidence has fired yet, so the §10 tracking log has nothing to record

## Reading (opinion, for the review)

- G1+G2 are the hole that matters: journey F is the only MVP journey with no serving slice. G3–G6 are core-model gaps that get pricier as the catalog lives without them (relations and locations especially — backfilling beats declaring).
- Suggested staging (unde decided): finish Enrich (synthesis → persistence → live re-confirms), then a notification stage (engine + dashboard + tiers on real dates), L3-style with per-slice approvals.
