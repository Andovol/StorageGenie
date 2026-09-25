# Bolt's Performance Journal

## 2026-09-24 - Batch Fetching Assertions to Eliminate N+1 DB Queries in Analytics Aggregation
**Learning:** Iterating over assets and making per-asset DB queries to fetch active assertions (such as classification and expiry date) creates an N+1 query pattern ($2N + 1$ queries). Batching assertion queries using `Assertion.asset_id.in_(active_ids)` reduces database roundtrips to $2$ queries total ($O(1)$ DB roundtrips).
**Action:** When aggregating or serializing asset attributes from EAV or assertion tables, batch assertion queries by asset IDs into a single IN query instead of making per-entity queries inside a loop.

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.
