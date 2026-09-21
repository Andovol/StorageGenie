# Bolt's Performance Journal

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.

## 2026-09-17 - Pre-fetch Household Observations/Assertions for Deduplication Jobs
**Learning:** In multi-evidence job steps (like `deduplicate_job`), invoking functions that query all household observations or assertions inside a loop over evidence IDs creates an N+1 query bottleneck. Pre-fetching household phash rows and identifier assertions once before the loop reduces database round-trips from O(N) to O(1).
**Action:** Always pre-fetch household-scoped context datasets before looping over evidence IDs in job processing steps.
