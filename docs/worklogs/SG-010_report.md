SG-010 — Phase 0 exit report

Status: implementation and local verification complete; final notes publication is the runner handoff.

Ref and provenance
- BASE ref requested: `automation`
- BASE resolved: `97ea0eb2048b63f19cf475388867551a72e8b0d2`
- WORK_HEAD (implementation/doc commit): `001e52b928b965f78a149d7f95f7970cd09d3cd8`
- Remote: `git@github.com:Andovol/StorageGenie.git`
- Work dir: `/home/andrei/StorageGenie`
- Coder: `codex`; reasoning effort: `high` (from live process arguments); model ID: `unknown` (no model ID in process arguments or provider metadata).

Acceptance evidence

1. E2E exit proof — `backend/tests/test_phase0_e2e.py::test_phase0_exit_condition` uses one temporary household/database/storage fixture and runtime IDs. It proved `POST /v1/assets` → 201, JPEG upload → 201, `POST /v1/assets/{id}/evidence` → 200, exact-ID search via `q`, export membership of the created asset and evidence IDs, and detail evidence plus a `display_name` assertion with `source_type=user` and `review_state=accepted`. The fail-first command exited 1 with `1 failed, 1 warning in 0.71s` at the missing `asset.accepted` row. After the permitted audit-path repair, the final targeted command exited 0 with `1 passed, 1 warning in 0.64s` (1.02s wall bound timer). This was not an empty collection, fixed-ID replay, skipped gate, or partial leg.

2. Duration measurability — The same test reads only its own `audit_event` rows, finds exactly one `asset.create` and one `asset.accepted`, asserts non-null timestamps, sorted rows, accepted-after-created ordering, and `accepted_at - created_at >= timedelta(0)`. No column, endpoint, or migration was added.

3. ADRs — `docs/adr/ADR-001-local-first-storage.md` traces SQLite/WAL, local filesystem, SQLAlchemy/Alembic, and deferred PostgreSQL/S3 decisions to `backend/app/db.py`, `backend/app/config.py`, `backend/app/storage/local_store.py`, `docker-compose.yml`, `backend/alembic/env.py`, the committed migration, and the blueprint. It names the export runtime-head assertion and fresh-database restore test. `docs/adr/ADR-002-evidence-provenance.md` traces immutable evidence, hashing, accepted/superseded assertions, audit writes, detail provenance, and the deferred table recipe to existing service/model/migration/blueprint lines; it does not describe absent code as present.

4. README/runbook — `README.md` contains prerequisites, `docker compose up --build -d`, migration, `app.seed`, the expected `{"status":"ok","db":"ok","storage":"ok"}` health response, backend/frontend suites, data paths, gitignore rationale, and the BM-8 note: Phase 0 is LAN-only, single-household, and unauthenticated; household scoping is namespacing, never security. Static verification found all 10 named paths and all 8 command patterns in the tree. Docker itself was not started because this slice forbids service restart/datastore writes; that is not reported as a live-service pass.

5. Full gates — From `backend/`, `timeout 600s ../venv/bin/python -m pytest -q` exited 0 with `24 passed, 1 warning in 1.46s`; the suite was non-empty. `timeout 120s ../venv/bin/python -m ruff check app tests` exited 0 with exact output `All checks passed!`, checking 47 Python files (40 app, 7 tests) with 0 findings. `timeout 120s ../venv/bin/python -m mypy app` exited 1 with `Found 43 errors in 10 files (checked 40 source files)`; this is advisory and unchanged by out-of-scope cleanup. Frontend `npm test -- --run` from `frontend/` reported 3 files/7 tests passed and `npm run lint` exited 0. The existing Starlette/httpx and React Router warnings are reported, not hidden.

6. Scope and files — The committed output paths are `backend/app/services/asset_service.py`, `backend/tests/test_phase0_e2e.py`, `docs/adr/ADR-001-local-first-storage.md`, `docs/adr/ADR-002-evidence-provenance.md`, `README.md`, `docs/worklogs/SG-010.log`, and `docs/worklogs/SG-010_report.md`. No migration, frontend source, `.env`, secret, production database, restart, infrastructure, or privileged operation was changed. The only product repair is the audit-path `asset.accepted` row proved necessary by the fail-first test.

7. Timing and bounds — Ordinary commands used a 120s bound; the backend suite used 600s; overall packet budget was 2100s. Final measured gate legs were 1.02s target, 1.98s suite, 0.02s Ruff, 0.16s mypy, and under 0.1s runbook check, all within bounds. No command timed out or was killed.

8. Commit/receipt handoff — Implementation/doc commit is `001e52b928b965f78a149d7f95f7970cd09d3cd8`. The evidence commit containing this report is the final notes target. After pushing `automation`, the last operation must be `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-010 | Report: docs/worklogs/SG-010_report.md | Work-HEAD: <final-evidence-commit>" <final-evidence-commit>`, followed by local and runner remote readback. The first note line must contain both `Dispatch-ID:` and `Report:`. No commit may follow the note; the dispatch result must report `note=yes`.

UNCLEAR: FIRST READ — The packet’s expected API legs existed, but `asset.accepted` did not; `docs/adr/`, `README.md`, and the E2E test were absent, and repository contract copies were unavailable.
UNCLEAR: DURING EXECUTION — The fail-first result was a real missing audit row, the final 24-test backend suite and Ruff gate were green, and the initial root-level npm attempt was corrected by using the documented `frontend/` directory.
UNCLEAR: REMAINING — The runner must push `automation`, attach/read back the notes receipt, and report `note=yes`; 43 advisory mypy findings and non-live Docker verification remain open by scope.
