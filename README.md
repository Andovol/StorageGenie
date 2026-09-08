# StorageGenie

StorageGenie is a Phase 0 local-first asset catalog: manually catalog an item,
attach source photos, search it, and export a consistent backup. The backend is
FastAPI/SQLAlchemy/Alembic and the frontend is React/Vite.

## Phase 0 runbook

### Prerequisites

Install Docker with the Compose plugin, Python 3.12+, Node.js/npm, and Git. The
backend dependency lock is `backend/requirements.lock`; the frontend lock is
`frontend/package-lock.json`. For the checked VPS workspace, the backend test tools
are already available in `/home/andrei/StorageGenie/venv/bin`.

Compose is configured to read the local deployment environment file named by
`docker-compose.yml:15`. If no overrides are needed, create an empty `.env` before
starting Compose; keep any real values uncommitted because `.env` is ignored by
`.gitignore:7`.

### Start the Phase 0 services

From the repository root:

```sh
docker compose up --build -d
```

Apply the schema and create the default single-household seed (Popescu Household
and two users):

```sh
docker compose exec backend python -m alembic upgrade head
docker compose exec backend python -m app.seed
```

Check the backend health endpoint:

```sh
curl -s http://localhost:8000/v1/health
```

Expected output:

```json
{"status":"ok","db":"ok","storage":"ok"}
```

The health route is implemented at `backend/app/api/v1/health.py:15-35` and proves
both database and evidence-storage access.

### Run the suites

Backend, using the project-local environment on the checked workspace:

```sh
cd backend
../venv/bin/python -m pytest -q
../venv/bin/python -m ruff check app tests
../venv/bin/python -m mypy app
```

Frontend:

```sh
cd frontend
npm test -- --run
npm run lint
```

The backend and frontend commands correspond to the scripts and targets in
`Makefile:8-20` and `frontend/package.json:5-10`. `mypy` is advisory in Phase 0;
pytest and Ruff are the required backend gates.

### Data locations and trust boundary

In Compose, SQLite is mounted from `./data/db` into `/data/db` and evidence is in
the named `storage_data` volume mounted at `/data/storage`
(`docker-compose.yml:8-14,43`). In a direct backend run, the defaults are
`backend/data/db/storagegenie.db` and `backend/data/storage`
(`backend/app/config.py:4-6`), while tests use temporary paths. These database,
storage, cache, and environment paths are gitignored (`.gitignore:7-21`) because
they contain local state, user evidence, or secrets rather than reviewable source.
Back up the database and the evidence manifest together.

Phase 0 is LAN-only, for a single household, and has no authentication. Household
scoping is namespacing, never security. Do not expose the Compose ports to an
untrusted network until authentication and deployment controls are implemented.

The Phase 0 test is backend API E2E, not browser automation; frontend behavior
remains covered by its unit/component suite.

## Phase 1 runbook

Phase 1 imports a mixed folder through the deterministic job engine. It remains
LAN-only, single-household, and unauthenticated; household IDs are namespacing,
not a security boundary. No LLM or external provider is involved in this phase.

From the repository root, first upload each file through `POST /v1/evidence` and
keep the returned evidence IDs. Create one import job with an idempotency key,
then run and inspect it:

```sh
curl -sS -X POST 'http://localhost:8000/v1/evidence?household_id=<HOUSEHOLD_ID>' \
  -F 'file=@/path/to/input.jpg;type=image/jpeg'
curl -sS -X POST 'http://localhost:8000/v1/imports?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: <IMPORT_KEY>' \
  -d '{"evidence_ids":["<EVIDENCE_ID_1>","<EVIDENCE_ID_2>"]}'
curl -sS -X POST 'http://localhost:8000/v1/imports/<JOB_ID>/run?household_id=<HOUSEHOLD_ID>'
curl -sS 'http://localhost:8000/v1/imports/<JOB_ID>?household_id=<HOUSEHOLD_ID>'
```

If a run is `FAILED`, inspect the `steps`, `errors`, and `progress` fields, fix
the input or service condition, and resume the same job once:

```sh
curl -sS -X POST 'http://localhost:8000/v1/imports/<JOB_ID>/retry?household_id=<HOUSEHOLD_ID>'
```

When the job reaches `AWAITING_REVIEW`, use the review queue, candidate detail,
and candidate decision routes. An accept/edit decision returns `409` while a
candidate's review tasks remain open; resolve each task first:

```sh
curl -sS 'http://localhost:8000/v1/review-tasks?household_id=<HOUSEHOLD_ID>'
curl -sS 'http://localhost:8000/v1/candidates/<CANDIDATE_ID>?household_id=<HOUSEHOLD_ID>'
curl -sS -X POST 'http://localhost:8000/v1/review-tasks/<TASK_ID>/resolve?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -d '{"resolution":"confirmed"}'
curl -sS -X POST 'http://localhost:8000/v1/candidates/<CANDIDATE_ID>/decision?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -d '{"action":"accept","corrected_fields":{}}'
```

For an expiry-tracker asset, classify it first. If classification returns a
`needs_evidence` assertion, enter the human-supplied date; this resolves the
manual review task and records a user-sourced accepted assertion:

```sh
curl -sS -X POST 'http://localhost:8000/v1/plugins/expiry-tracker/assets/<ASSET_ID>/classification?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -d '{"category":"food"}'
curl -sS -X POST 'http://localhost:8000/v1/plugins/expiry-tracker/assets/<ASSET_ID>/expiry?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' \
  -d '{"expiry_date":"2030-05-06","date_type":"best_before","unit":"piece","source_evidence_ids":["<EVIDENCE_ID>"]}'
```

Search committed assets with `GET /v1/assets?q=<STEM>&household_id=<HOUSEHOLD_ID>`;
inspect one with `GET /v1/assets/<ASSET_ID>?household_id=<HOUSEHOLD_ID>`, and
download the household manifest with `GET /v1/export?household_id=<HOUSEHOLD_ID>`.
SQLite FTS5 is maintained by the asset triggers and the `rebuild_asset_fts`
function in `backend/app/services/fts.py:87-91`. Call it after an out-of-band
restore or bulk database change when the index may be stale; normal API writes
do not need a rebuild. For the checked workspace, the direct maintenance shape
is:

```sh
cd backend
venv/bin/python -c "from app.db import engine; from app.services.fts import rebuild_asset_fts; connection=engine.connect(); rebuild_asset_fts(connection); connection.commit(); connection.close()"
```

Check the offline PostgreSQL-dialect inventory from the repository root with:

```sh
make check-postgres-dialect
```

The unchanged data locations are Compose SQLite `./data/db` mounted at
`/data/db`, the named `storage_data` volume mounted at `/data/storage`, and
direct-backend defaults `backend/data/db/storagegenie.db` and
`backend/data/storage` (`docker-compose.yml:8-14,43`; `backend/app/config.py:4-6`).
Keep database and evidence manifests together when backing up.

Verification map: `backend/tests/test_phase1_e2e.py::test_phase1_exit_condition`
proves one real five-file upload/import fixture, durable failure and retry,
review blocking and resolution, manual expiry entry, atomic-looking committed
asset visibility across assertions/evidence/audit, FTS identity, export IDs,
and the single-run UV-5 duration. Decoder observations are service-tolerant:
the E2E reports each QR/EAN leg as present or degraded. The two real decoder
nodes that require `libzbar` and `tesseract` remain ISS-1 work for the manual
compose pass, whose scope is image build plus compose-up/UI/restart re-proof.
No browser automation is part of this verification map; frontend behavior was
previously covered by its frontend suite and no frontend file is changed here.
