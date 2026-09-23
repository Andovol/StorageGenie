# Bolt's Performance Journal

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.

## 2026-09-23 - Inverted Token Index for Taxonomy Fuzzy Resolution
**Learning:** Sequential linear scanning across 5,600+ taxonomy rows to compute token set similarities (Jaccard) spends significant CPU time on pairs with zero set intersection. Building a cached inverted index mapping individual tokens to matching candidate rows restricts candidate evaluation to sets with non-zero intersection, dropping resolution times from ~4.6ms to ~0.28ms per query (~16x speedup).
**Action:** When doing fuzzy token-set Jaccard/Dice matching against static or rarely-changing candidate corpora, construct an inverted token index to prune non-intersecting candidate rows before computing similarity scores.
