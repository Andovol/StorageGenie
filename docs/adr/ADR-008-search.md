# ADR-008: Deterministic FTS5 search before semantic search

## Status

Accepted for Phase 1.

## Decision

Catalog search uses a SQLite FTS5 external-content index over asset identity,
display name, and household ID. Asset insert, update, and delete triggers keep
the index synchronized; `rebuild_asset_fts(connection)` is the named,
re-runnable backfill callable after the migration. Search input is quoted as
literal FTS5 tokens before `MATCH`, so operators, quotes, and wildcards cannot
be supplied as query syntax. Existing household/type/status/evidence filters,
the `(created_at DESC, id DESC)` cursor, and response envelope remain the
source of truth. Relevance ranking is intentionally not introduced: rank-based
cursors would invalidate the existing cursor envelope. Revisit only with
evidence and Phase 4 facets.

The reusable helper is in `backend/app/services/fts.py`. The SQLite-only
Alembic revision is
`backend/alembic/versions/20260908_sg017_fts.py`; its external-content
projection is needed because the asset primary key is text while SQLite maps
external FTS content by integer rowid.

## Postgres migration path

`backend/tests/test_postgres_dialect.py` compiles every SQLAlchemy metadata
table offline with PostgreSQL's dialect, without a server or driver. The FTS5
revision is excluded by rule because FTS5 is SQLite-specific and has no
PostgreSQL equivalent; the current Postgres deployment path therefore carries
the catalog schema but must choose a Postgres-native full-text implementation
(or a semantic/vector index) separately. The divergence is explicit rather
than hidden by a skipped dialect check.

## Future semantic/vector criterion

Semantic or vector search may be considered only when deterministic token
search is insufficient on measured query-quality evidence, with an agreed
embedding model, freshness/rebuild policy, privacy review, and a cursor/facet
contract that does not break the current catalog envelope.
