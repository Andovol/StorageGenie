# ADR-006: Deterministic duplicate policy

## Status

Accepted for Phase 1 deterministic imports.

## Decision

- Exact SHA-256 evidence is treated as an existing asset proposal when the
  evidence row is already linked through `asset_evidence`; the proposal names
  that asset and the commit path creates no second asset (`backend/app/services/dedup.py:19-30,122-131`,
  `backend/app/services/candidates.py:113-122`).
- Perceptual similarity uses the SG-013 dHash and the named
  `settings.dhash_near_threshold` setting. A distance at or below the setting
  is an advisory `similar` match; accepting it independently creates a new
  asset (`backend/app/services/dedup.py:37-57,145-149`,
  `backend/app/config.py:14`).
- A validated `barcode_qr` observation whose value equals an existing
  `identifier` assertion creates an `identifier_collision` review task and
  blocks commit while that task is open (`backend/app/services/dedup.py:60-96,167-219`,
  `backend/app/api/v1/candidates.py:57-64`,
  `backend/app/services/candidates.py:116-131`).
- Identifier assertions use `field_path="identifier"`. No earlier assertion
  convention existed in `backend/tests/test_assertions.py` or
  `backend/tests/test_assets_crud.py`; the convention is established here.
- There is no semantic similarity policy in Phase 1. Ambiguous split/merge
  decisions remain review work; this slice contains no path that alters an
  existing asset from deduplication (`backend/app/services/dedup.py`).
- Accepted/edit decisions create a new asset, deterministic assertions,
  evidence links, and an initial `asset.lifecycle.created` audit row in the
  same SQLAlchemy transaction (`backend/app/api/v1/candidates.py:67-90`,
  `backend/app/services/candidates.py:42-122`).

## Consequences

The review queue stores collision tasks using the existing `ReviewTask`
columns (`backend/app/models/review_task.py:8-19`), so this slice adds only the
authorised `candidate` revision (`backend/alembic/versions/20260908_sg014_candidate.py`).
The route and detail history expose lifecycle audit rows without adding an
event table (`backend/app/api/v1/assets.py:274-310`).
