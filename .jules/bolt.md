# Bolt's Performance Journal

## 2026-09-28 - Inverted Token Index & Sub-scoring Caching for Taxonomy Search
**Learning:** Fuzzy Jaccard string matching against ~5,500 taxonomy nodes creates a severe CPU bottleneck (~4.3ms/call) when linearly iterating all entries. Building an inverted token index (`dict[str, tuple[int, ...]]`) restricts scoring to entries sharing >=1 token, cutting candidate evaluation from 5,500 down to 10-50 entries. Decorating the candidate scoring function (`_score_candidates(proposal_tokens)`) rather than top-level resolution functions with `@lru_cache` allows tests/code to monkeypatch threshold attributes while still caching search results.
**Action:** For large set-similarity searches, build an inverted index on tokens to prune disjoint items before computing distance. Cache candidate scoring on hashable token sets rather than top-level gate functions when gate thresholds may be dynamic or monkeypatched in tests.

## 2026-09-14 - Direct JOIN for Many-to-Many Asset-Evidence Queries
**Learning:** Fetching many-to-many relationships by first executing `db.execute(association.select().where(...))` and then `db.query(Model).filter(Model.id.in_(ids))` adds an unnecessary SQL query round-trip per entity serialization. Doing `db.query(Model).join(association, Model.id == association.c.model_id).filter(...)` accomplishes the same in a single database round-trip.
**Action:** When serializing entities with junction tables in FastAPI endpoints, always use ORM `.join()` to fetch related models in a single query rather than selecting IDs first.

## 2026-09-17 - Pre-fetch Household Observations/Assertions for Deduplication Jobs
**Learning:** In multi-evidence job steps (like `deduplicate_job`), invoking functions that query all household observations or assertions inside a loop over evidence IDs creates an N+1 query bottleneck. Pre-fetching household phash rows and identifier assertions once before the loop reduces database round-trips from O(N) to O(1).
**Action:** Always pre-fetch household-scoped context datasets before looping over evidence IDs in job processing steps.
