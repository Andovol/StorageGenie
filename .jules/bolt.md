# Bolt's Performance Journal

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.

## 2026-09-24 - Batch Querying Assertions in Analytics Stats Computation
**Learning:** In analytics services computing stats across household assets, evaluating helper functions (like classification slug and active expiry date) per asset introduced an N+1 query pattern (2 queries * N assets). Batch fetching all active assertions for the target asset IDs and field paths in a single query (`Assertion.asset_id.in_(active_asset_ids)`) and building an in-memory lookup map reduces SQL round-trips from `2N + 1` to `2` database queries.
**Action:** When aggregating asset metrics across multiple assertion fields, batch load assertions for active assets in a single query ordered by creation time instead of calling per-asset query functions.
