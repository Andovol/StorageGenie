# Bolt's Performance Journal

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.

## 2026-09-17 - Batch Assertion and Attribution Queries for LLM Context Construction
**Learning:** Building LLM context across catalogue items by executing single-entity ORM helper queries (`_active_assertion` and `_source_attributions`) inside an asset iteration loop causes an N+1 query explosion ($3N + 1$ total queries). Batch querying assertions and attributions using `.in_(asset_ids)` and indexing them in-memory reduces context generation time by >90% (e.g. from 0.50s to 0.03s for 100 assets).
**Action:** Whenever constructing domain context or list payloads for multiple entities, batch fetch related assertions and source attributions with `.in_(asset_ids)` and map them in Python instead of querying per entity inside the loop.
