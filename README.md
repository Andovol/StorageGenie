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
curl -s http://localhost:8003/v1/health
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
curl -sS -X POST 'http://localhost:8003/v1/evidence?household_id=<HOUSEHOLD_ID>' \
  -F 'file=@/path/to/input.jpg;type=image/jpeg'
curl -sS -X POST 'http://localhost:8003/v1/imports?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: <IMPORT_KEY>' \
  -d '{"evidence_ids":["<EVIDENCE_ID_1>","<EVIDENCE_ID_2>"]}'
curl -sS -X POST 'http://localhost:8003/v1/imports/<JOB_ID>/run?household_id=<HOUSEHOLD_ID>'
curl -sS 'http://localhost:8003/v1/imports/<JOB_ID>?household_id=<HOUSEHOLD_ID>'
```

If a run is `FAILED`, inspect the `steps`, `errors`, and `progress` fields, fix
the input or service condition, and resume the same job once:

```sh
curl -sS -X POST 'http://localhost:8003/v1/imports/<JOB_ID>/retry?household_id=<HOUSEHOLD_ID>'
```

When the job reaches `AWAITING_REVIEW`, use the review queue, candidate detail,
and candidate decision routes. An accept/edit decision returns `409` while a
candidate's review tasks remain open; resolve each task first:

```sh
curl -sS 'http://localhost:8003/v1/review-tasks?household_id=<HOUSEHOLD_ID>'
curl -sS 'http://localhost:8003/v1/candidates/<CANDIDATE_ID>?household_id=<HOUSEHOLD_ID>'
curl -sS -X POST 'http://localhost:8003/v1/review-tasks/<TASK_ID>/resolve?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -d '{"resolution":"confirmed"}'
curl -sS -X POST 'http://localhost:8003/v1/candidates/<CANDIDATE_ID>/decision?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -d '{"action":"accept","corrected_fields":{}}'
```

For an expiry-tracker asset, classify it first. If classification returns a
`needs_evidence` assertion, enter the human-supplied date; this resolves the
manual review task and records a user-sourced accepted assertion:

```sh
curl -sS -X POST 'http://localhost:8003/v1/plugins/expiry-tracker/assets/<ASSET_ID>/classification?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -d '{"category":"food"}'
curl -sS -X POST 'http://localhost:8003/v1/plugins/expiry-tracker/assets/<ASSET_ID>/expiry?household_id=<HOUSEHOLD_ID>' \
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

## Phase 2 runbook — AI extraction (Food + Medicine)

Phase 2 adds one cloud vision provider behind the existing provider seam. It
remains LAN-only, single-household, and unauthenticated like the earlier phases,
and it is OFF by default: with the shipped defaults the pipeline skips the AI
steps and behaves like Phase 1 (proved by
`backend/tests/test_ai_pipeline.py::test_default_config_is_phase1_skip`).

### Provider setup

1. Subscribe to OpenCode GO and obtain an API key.
2. Put the key in the host `.env` as `OPENCODE_API_KEY` (see `.env.example`).
   `.env` is gitignored (`.gitignore:7`); the key value is never printed, logged,
   or committed, and the adapter re-reads it from the backend environment only.
3. Enable cloud use explicitly with `SG_CONSENT=true`. Consent is OFF by default;
   without it no provider key is read and no network call is attempted.

### Settings (names only; real values live in the uncommitted `.env`)

| Setting | Purpose | Shipped default |
|---|---|---|
| `SG_PROVIDER_ID` | adapter id; `fake` keeps everything local | `fake` |
| `SG_MODEL_ID` | vision model id for the adapter | `deepseek-v4-flash-vision-exp` |
| `SG_CONFIDENCE_THRESHOLD` | auto-accept floor for non-gated fields (uncalibrated, `G-A9`) | `0.9` |
| `SG_PROMPT_CATEGORY` | versioned prompt selection (`food` or `medicine`) | `food` |
| `SG_PER_JOB_CAP` | per-job worst-case cost cap in USD | `none` (uncapped) |
| `SG_MONTHLY_CAP` | household monthly cap in USD, enforced from the durable `provider_call` ledger | `none` (uncapped) |
| `SG_CONSENT` | cloud consent switch | `false` |

The effective model can also be selected at runtime from the Settings screen
(`GET`/`PUT /v1/settings/ai`; tested models only, currently
`deepseek-v4-flash-vision-exp`). That override lives in the backend process, so
**a backend restart resets it to `SG_MODEL_ID` from the environment**.

### Run the eval

From `backend/`:

```sh
venv/bin/python eval/run.py               # offline: integrity + committed-cache scoring, $0
venv/bin/python eval/run.py --check-only  # integrity checks only
SG_CONSENT=true SG_PROVIDER_ID=opencode-go venv/bin/python eval/run.py --live
```

`--live` is the ONE metered mode: it prints the `$0.05` ceiling and per-call cost,
reads the key from the environment, redacts each image through the shared
`redact_image`, and reuses the same reader path production uses. Every call prints
the provider-returned model, latency, usage, and cost. Do not run `--live` without
intent: it spends real money.

### Budget posture

Per owner fork F2 the caps ship **uncapped**; re-evaluation is owed. The
mechanisms exist and can refuse before any call: the per-job cap is checked by the
router, and the monthly cap is checked by the reader against the committed
`provider_call` ledger so it binds across jobs (not just within one instance). A
refused job fails its `ANALYZING_WITH_AI` step with the cap reason and makes zero
provider calls and zero ledger rows.

### Phase 3 non-goals (owned by the next phase, not delivered here)

- Web enrichment / `search_and_summarize` calls.
- Planning and chat agents.
- Categories beyond the Food and Medicine prompt files.
- Prompt tuning (prompt v1 is frozen; the eval corpus is its guard).
- A second provider or multi-provider routing/fallback.

Phase 2 is proved by `backend/tests/test_phase2_e2e.py` (six offline behaviours on
the real HTTP path, zero network) and closes on blueprint:522.
