# ADR-001: Local-first storage and migration path

- Status: accepted for Phase 0
- Date: 2026-09-07

## Decision

Phase 0 stores catalog data in SQLite with WAL enabled and stores original evidence on
the local filesystem outside the web root. SQLAlchemy remains the application data
boundary and Alembic remains the schema-migration boundary. The later deployment
option is PostgreSQL plus S3-compatible object storage, reached through those same
boundaries rather than through a second persistence model.

The choice is deliberately local-first: the blueprint calls for SQLite (WAL),
SQLAlchemy/Alembic, and local filesystem storage in the MVP, with PostgreSQL and
S3/MinIO as the production evolution (`inception/generic_asset_catalog_expiry_tracker_blueprint.md:115-128`).
The Phase 0 exit is the manual catalog/search/export flow, not a production-scale
storage deployment (`inception/generic_asset_catalog_expiry_tracker_blueprint.md:495-504`).

## Existing pins

- `backend/app/config.py:4-6` defaults the database to SQLite and the evidence root
  to `./data/storage`.
- `backend/app/db.py:7-24` constructs the SQLAlchemy engine and enables SQLite
  foreign keys, `journal_mode=WAL`, and the configured busy timeout.
- `backend/app/storage/local_store.py:6-28` derives household/hash paths below the
  configured storage root and creates that root without exposing it as a web root.
- `docker-compose.yml:8-14,43` maps the SQLite directory and a named evidence
  volume into the backend container; `backend/Dockerfile:2-7` installs the app in
  the container at `/app`.
- `backend/alembic/env.py:12-25` loads the SQLAlchemy metadata and binds Alembic to
  the configured database URL. The Phase 0 schema is the committed migration
  `backend/alembic/versions/0201cf10c56c_001_core_foundation.py:21-161`.

## Migration-path test

`backend/tests/test_export.py:95-117` computes the current Alembic head with
`ScriptDirectory` and requires the exported `db_revision` to equal that head. The
same test also requires the manifest to include assets, evidence, assertions, and
audit events. `backend/tests/test_export.py:120-170` restores the manifest into a
fresh SQLite database and checks asset/evidence counts and ID sets. These tests keep
the SQLAlchemy/Alembic manifest path honest while the future database/storage
adapters are deferred.

## Deferred alternatives

- PostgreSQL is deferred until deployment needs exceed the single-household local
  Phase 0 profile.
- S3-compatible storage is deferred until remote/object-storage operations are
  justified; no S3 client, bucket, or migration is claimed here.
- FTS5, vector search, and orchestration infrastructure remain separate future
  decisions; they do not alter this storage boundary.

Moving to either deferred backend requires an explicit migration and an extension of
the export/restore and health tests. This ADR does not claim that those adapters
already exist.

## Consequences

Local operation is simple, private by default, and testable with isolated temporary
SQLite databases and storage roots. Backups must keep the database and evidence
manifest together; the blueprint makes that pairing explicit
(`inception/generic_asset_catalog_expiry_tracker_blueprint.md:462-470`).
