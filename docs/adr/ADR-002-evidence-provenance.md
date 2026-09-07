# ADR-002: Evidence and provenance model

- Status: accepted for Phase 0
- Date: 2026-09-07

## Decision

Original evidence is immutable. The system hashes an upload before storing it,
keeps the original bytes at a content-derived path, and treats thumbnails as
regenerable derivatives. Asset facts are assertions with a field path, value,
source type, confidence, review state, and optional source-evidence IDs. Accepted
assertions form the current review chain; changing one supersedes the previous
accepted assertion instead of mutating its historical row. Catalog, evidence, and
assertion mutations emit audit events with actor, action, entity, before/after data,
household, and timestamp.

This implements the blueprint principles that evidence precedes inference and that
human review is explicit (`inception/generic_asset_catalog_expiry_tracker_blueprint.md:22-31`),
as well as its requirements for immutable originals and a full audit trail
(`inception/generic_asset_catalog_expiry_tracker_blueprint.md:132-140,462-470`).

## Existing pins

- `backend/app/services/evidence_service.py:132-169` hashes uploads, rejects
  duplicates by hash, writes the original atomically, and never rewrites an
  existing original. `backend/app/services/evidence_service.py:187-217` persists
  the evidence row and records `evidence.create`.
- `backend/app/models/evidence.py:16-28` stores the household, SHA-256, media type,
  storage key, original filename, source kind, and size; the migration pins the
  corresponding table and uniqueness constraint at
  `backend/alembic/versions/0201cf10c56c_001_core_foundation.py:69-85`.
- `backend/app/models/assertion.py:8-21` stores the provenance and review-state
  fields. `backend/app/services/assertion_service.py:19-47` supersedes the prior
  accepted row, inserts a new accepted row, and records `assertion.upsert`.
- `backend/app/services/asset_service.py:18-67` creates manual field assertions,
  records `asset.create` and `asset.accepted`, and commits them together.
  `backend/app/services/asset_service.py:68-116` records asset updates and
  evidence attachment; `backend/app/api/v1/assets.py:217-243` records archive.
  These are the Phase 0 catalog write paths. Bootstrap household/user seed writes
  are setup data, not user assertion/evidence events.
- `backend/app/api/v1/assets.py:50-114` exposes linked evidence, assertion source
  and review fields, and audit history in asset detail.

The committed exit test `backend/tests/test_phase0_e2e.py:52-143` proves the
single-fixture create → upload → attach → search → export → detail/provenance walk,
and computes the accepted-minus-created audit duration from that fixture's own rows.
`backend/tests/test_evidence_upload.py:38-80` separately proves duplicate hashing,
audit creation, and original-byte stability.

## Deferred alternatives and table recipe

Phase 0 does not add columns or tables for extraction observations, identifiers,
classifications, locations, lifecycle history, or relations. The future recipe is
the blueprint's domain model (`inception/generic_asset_catalog_expiry_tracker_blueprint.md:152-171`):

- `observation`: `id`, `evidence_id`, bounding box, candidate label, raw model
  output, confidence.
- `identifier`: `id`, `asset_id`, identifier type, normalized value,
  verification state.
- `classification`: `asset_id`, taxonomy ID, label, confidence, source.
- `location`: `id`, parent ID, name, location type; pair it with an
  `asset_location` history table carrying asset/location, start/end, and confidence.
- `lifecycle_event`: asset ID, event type, occurred-at time, actor, notes, and
  payload JSON.
- `asset_relation`: source asset ID, relation type, target asset ID, and metadata.

Those tables are deferred alternatives to Phase 0 columns, not undocumented claims
about the current schema. The committed Phase 0 migration creates the present core
tables only (`backend/alembic/versions/0201cf10c56c_001_core_foundation.py:21-161`).
When one is needed, add it through Alembic, preserve evidence/assertion references,
and add a migration plus audit/provenance tests before enabling writes.

## Consequences

Users can distinguish immutable source material from accepted claims, and exports
carry the IDs needed to reconnect both sides. The model intentionally does not
pretend to provide OCR observations, identifiers, lifecycle events, or relational
history before their schemas and write paths are designed.
