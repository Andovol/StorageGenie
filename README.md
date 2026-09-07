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
