SG-017 | FTS5 search + Postgres-dialect CI check + observed-date kind scope

BASE ref requested: automation
BASE resolved: acdad450a1b855f0e23225badab6d3fc7b75a475
Implementation commit before report: 6bb02b6
WORK_DIR: /home/andrei/StorageGenie
Origin: git@github.com:Andovol/StorageGenie.git
Coder: codex
Model: unknown (no model id appeared in readable process arguments; CLI default was used)
Reasoning effort: high (verified from live process arguments: `codex exec ... -c model_reasoning_effort=high`)
Autonomy: L3, Phase 1 slice 6 of 7
Elapsed: approximately 1,100 s (18 min 20 s) / 2,100 s (35 min) overall bound; no command was killed

Implemented

- Added `backend/app/services/fts.py` with literal FTS5 token sanitization, SQLite external-content FTS5 storage for `asset_id`, `display_name`, and `household_id`, synchronization triggers, and the named callable `rebuild_asset_fts(connection)`. A compatibility bootstrap is limited to legacy/test SQLite databases created through `Base.metadata.create_all`; migrated databases use the Alembic revision.
- Updated only the non-empty `q` branch of `backend/app/api/v1/assets.py`. It performs sanitized `MATCH` narrowing and then applies the pre-existing household/type/status/evidence filters. The existing response serializer, `(created_at DESC, id DESC)` ordering, cursor envelope, and empty/no-q behavior remain unchanged. Relevance ranking is not introduced because rank cursors would break the existing cursor envelope; revisit requires evidence and Phase 4 facets.
- Added exactly one migration, `backend/alembic/versions/20260908_sg017_fts.py`, with the external-content projection, insert/update/delete triggers, and backfill. Temp SQLite proof covered `upgrade head`, `downgrade -1`, and `upgrade head`.
- Added FTS-specific tests for multi-token search, hostile syntax literals (`" OR "1"="1` and an unterminated quote), same-named cross-household identity isolation, rebuild recovery, trigger lifecycle, migration transitions, and the 10k fixture.
- Added `backend/tests/test_postgres_dialect.py`. It enumerates 13 expected SQLAlchemy metadata tables, asserts that inventory against `Base.metadata.tables`, and compiles every table to PostgreSQL DDL offline. The SQLite-only FTS migration is excluded by explicit rule in the module docstring because FTS5 has no PostgreSQL equivalent.
- Added ADR-008 documenting deterministic FTS5 first, the semantic/vector quality and privacy criterion, and the FTS5/PostgreSQL divergence.
- Restricted `backend/app/plugins/expiry_tracker.py::_observed_date` to `ocr` and `barcode_qr`; the diff is confined to that function. EXIF-only dates now require evidence review while OCR dates remain proposed with evidence linkage.
- Added `check-postgres-dialect` and removed the stale `|| true` from the frontend lint line in `Makefile`.

Verification

- SG-017 targeted group: 19 passed / 5 warnings. This includes both polarities of the existing search filters, FTS read-back, hostile inputs, household isolation, rebuild, trigger insert/update/delete, migration round-trip, dialect compilation, and both ISS-2 regression legs.
- 10k latency: one run on shared `ubuntu` hardware, Linux 6.8.0-136-generic-x86_64 with glibc 2.39; 10,000 assets with evidence links on a subset; 20 requests. p50 was 16.31 ms and p95 was 19.53 ms, below the 300 ms target. This is not presented as a rate. Query plan: `SEARCH asset USING INDEX ix_asset_household_id (household_id=?)`; `LIST SUBQUERY 1`; `SCAN asset_fts VIRTUAL TABLE INDEX 0:M3`; `USE TEMP B-TREE FOR ORDER BY`.
- `tests/test_export.py::test_export_manifest_is_complete_and_downloadable`: 1 passed.
- `make check-postgres-dialect`: 1 passed.
- `cd frontend && npm run lint`: exit 0 with no lint output.
- Ruff: clean for `app tests alembic`.
- Mypy advisory: 40 errors in 9 files / 51 checked sources; these are existing untyped/unused-ignore findings and no out-of-ceiling repairs were made.
- Final full backend: 57 collected, 54 passed, 3 failed. The two carried ISS-1 failures are `backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `backend/tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence`; they match the packet-start baseline at `acdad450a1b855f0e23225badab6d3fc7b75a475`, which was 46 passed / 2 failed. No decoder-dependent test was imported or added here.

Findings and scope

- New finding: `backend/tests/test_candidates.py::test_candidate_migration_upgrade_downgrade_upgrade` is red after SG-017 because its `downgrade -1` assumption predates the new head. Alembic correctly downgrades SG-017 only and leaves the SG-014 candidate table. The exact test passed at BASE. Destination is the standing SG-014 lever line; the out-of-ceiling test was not modified.
- The packet’s ARCHITECT.md, PACKET.md, DISPATCH.md, and PRODUCTION.md routing files are absent from this checkout; the committed packet, AGENTS.md, and STATE.md were used and the discrepancy is reported.
- No frontend product code, new runtime dependency, semantic search, facets, saved searches, route decorator outside the existing assets GET path, new source/review enum value, live DB, restart, secret, `.env`, SSH, docker, sudo, or infrastructure change was made.
- No criterion passed vacuously: the FTS function is invoked by populated queries, the hostile cases assert identity, rebuild deletes and restores rows, migration transitions inspect schema state, the dialect test asserts its own inventory, and the 10k fixture executes 20 measured requests.

Output paths committed by SG-017:

- `Makefile`
- `backend/app/api/v1/assets.py`
- `backend/app/plugins/expiry_tracker.py`
- `backend/app/services/fts.py`
- `backend/alembic/versions/20260908_sg017_fts.py`
- `backend/tests/test_search.py`
- `backend/tests/test_plugin_expiry.py`
- `backend/tests/test_postgres_dialect.py`
- `docs/adr/ADR-008-search.md`
- `docs/worklogs/SG-017.log`
- `docs/worklogs/SG-017_report.md`

G6 receipt is the final notes-ref action after this report commit; no commit follows it. The note carries `Dispatch-ID: SG-017`, the report path, and the final Work-HEAD.

UNCLEAR — FIRST READ: The four method-routing files named by AGENTS.md were absent; the committed packet, AGENTS.md, and STATE.md supplied the available contract.
UNCLEAR — DURING EXECUTION: ISS-1 decoder legs remained red because pyzbar/libzbar and tesseract are unavailable; no privileged workaround was attempted. The new SG-014 migration-test assumption finding also remains open.
UNCLEAR — REMAINING: Manual compose must re-prove the two decoder nodes; the SG-014 downgrade-test lever needs a later test-contract repair; semantic/vector search remains deferred.
