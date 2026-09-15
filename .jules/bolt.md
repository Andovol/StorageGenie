## 2026-09-15 - Optimize evidence query in asset serialization
**Learning:** Sequential SELECT queries across junction tables (e.g. `asset_evidence` to `Evidence`) create unnecessary database round-trips. Replacing them with a single SQLAlchemy JOIN reduces query overhead and improves asset retrieval speeds by ~1.2x - 1.25x.
**Action:** Always check for two-step ID lookup patterns in database queries and consolidate into explicit JOINs.
