# Bolt's Performance Journal

## 2026-09-25 - LRU Caching for Google Taxonomy Scoring
**Learning:** `resolve_google_type` compares non-exact proposal strings against 5,500+ vendored taxonomy rows using Jaccard token set similarity. Without memoization on the proposal scoring helper (`_score_proposal`), each proposal query spent ~6ms executing 5,500 similarity comparisons. Caching normalized proposal score outputs with `@lru_cache(maxsize=2048)` reduces execution time for warm proposals to under 0.002ms (~3,000x speedup) while allowing dynamic threshold checks to function properly.
**Action:** When computing similarity against large offline/vendored datasets, memoize the raw scoring pipeline function so threshold evaluation remains dynamic while skipping repeated dataset scans.

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.
