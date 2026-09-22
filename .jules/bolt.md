# Bolt's Performance Journal

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.

## 2026-09-17 - Batch Assertion Queries for Analytics Asset Aggregations
**Learning:** In analytics/stats services that inspect assertions (e.g. classification or expiry date) across active assets in a household, querying assertions inside a per-asset loop introduces an N+1 query bottleneck (2N queries). Querying all active assertions for `Assertion.asset_id.in_(active_ids)` in a single query reduces DB round-trips from O(N) to O(1).
**Action:** Always batch-fetch entity assertions using `.in_(asset_ids)` when aggregating stats or building batch asset responses.
