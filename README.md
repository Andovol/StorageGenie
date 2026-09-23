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

Compose is configured to read the local deployment environment file named by the
`env_file` key in `docker-compose.yml`. If no overrides are needed, create an empty
`.env` before starting Compose; keep any real values uncommitted because `.env` is
ignored by `.gitignore:7`.

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

### Production shape (single service)

The default Compose shape is one service: the backend image serves the JSON API
**and** the built UI on one loopback port. The UI is built from the committed
frontend sources during the image build (`backend/Dockerfile`, node stage) with
`VITE_API_BASE=https://storagegenie.dynv6.net`; `frontend/dist` is gitignored and
never committed or baked in from disk. The app resolves the built files from
`/app/static` (override `SG_STATIC_DIR` for a bare dev run; with no built UI it
still starts and serves `/v1`, and `GET /` returns the legacy JSON placeholder).

```sh
docker compose up --build -d
docker compose exec backend python -m alembic upgrade head
docker compose exec backend python -m app.seed
curl -s http://127.0.0.1:8003/v1/health
curl -s http://127.0.0.1:8003/            # built index.html
```

`docker-compose.yml` publishes `127.0.0.1:8003:8000` only. `--profile dev` restores
the two-service development setup (the Vite dev server on `127.0.0.1:5173` plus the
backend).

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
(`docker-compose.yml:10-11,43`). In a direct backend run, the defaults are
`backend/data/db/storagegenie.db` and `backend/data/storage`
(`backend/app/config.py:4-6`), while tests use temporary paths. These database,
storage, cache, and environment paths are gitignored (`.gitignore:7-21`) because
they contain local state, user evidence, or secrets rather than reviewable source.
Back up the database and the evidence manifest together.

Phase 0 is for a single household and has no authentication. Household scoping is
namespacing, never security. The app binds **loopback only** (`docker-compose.yml`
publishes `127.0.0.1:8003:8000`); the public entry is the host standard's nginx +
https + login (planned, not yet live). Do not publish the port on a non-loopback
interface until authentication and deployment controls are implemented.

The Phase 0 test is backend API E2E, not browser automation; frontend behavior
remains covered by its unit/component suite.

### Backup and restore drill

The live data is the Compose SQLite file (bind-mounted from `./data/db`) and the
`storagegenie_storage_data` volume. Copy both read-only: the database through
SQLite's native backup API (a raw `cp` of a WAL database is not a backup) and the
evidence directory through a recursive read. `backend/scripts/backup_restore_drill.py`
does both into a fresh temporary directory and never writes to the live paths.
Resolve the volume's host path with
`docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}'`, then:

```sh
backend/venv/bin/python backend/scripts/backup_restore_drill.py \
  --prod-db data/db/storagegenie.db \
  --prod-storage "$(docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}')/_data"
```

The script proves the restore by `sha256sum` equality of the backup and the
restored database, `PRAGMA integrity_check=ok`, identical per-table counts and
named rows, and byte-equal storage hashes; it then removes its temporary
directory, leaving the hashes on stdout. **Restoring production from backup is an
incident, never silent cleanup** (`CO-42`).

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
`backend/data/storage` (`docker-compose.yml:10-11,43`; `backend/app/config.py:4-6`).
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

## Phase 3 runbook — usability block, planning, chat, Cosmetics

Phase 3 keeps the same LAN-only, single-household, unauthenticated stack as Phases
0–2. It adds the usability block (tested-model picker, multi-item split, manual entry
per field, on-screen corrections), a daily planning agent on a button, grounded
category chat, and the Cosmetics category with opened-date tracking. **AI stays OFF
by default**: with the shipped defaults (`SG_PROVIDER_ID=fake`, `SG_CONSENT=false`) a
planning run and a chat call refuse before any provider object is built, and the
import pipeline skips the AI steps exactly as Phase 1.

### What the stage added

- **Model picker** (`GET`/`PUT /v1/settings/ai`): lists the server-side tested-model
  allowlist, selects one at runtime, and an out-of-set id is an enforced `422`. The
  provider key is named nowhere on the response path (exclusion by rule). The
  selection is process-side, so **a backend restart resets it to `SG_MODEL_ID`**.
- **Multi-item split** (`POST /v1/candidates/{id}/split`): a photo holding several
  items becomes one candidate per item, each keeping its own fields, the shared
  evidence and its origin provenance. The request must name every item exactly once;
  a partial selection is an enforced `422` that creates nothing.
- **Manual entry per field + on-screen corrections** (`POST
  /v1/plugins/expiry-tracker/assets/{id}/expiry`, `PATCH /v1/assets/{id}`): every
  field is hand-typeable, `Unknown` stays valid, and an accepted value is superseded
  (never overwritten) with the old value visible in asset history.
- **Daily planning on a button** (`POST /v1/planning/run`): reads the catalogue and
  confirmed label data, is consent-gated before any call, and writes `pending`
  suggestions with backing refs plus one `suggestion` guardrail row. Nothing
  executes: confirm/dismiss are the only transitions (`GET
  /v1/planning/suggestions`, `POST .../confirm`, `POST .../dismiss`); a dismissal with
  a reason writes one append-only `correction` row; an illegal move is `422`.
- **Category chat** (`POST /v1/chat/{category}`): a grounded answer for Food or
  Medicine built from that category's catalogue, sent as delimited untrusted DATA.
  An unsupported category is `422`; the explicit `POST /v1/chat/{category}/corrections`
  is the ONLY write action (user-initiated), and model output alone writes no row.
- **Cosmetics + opened-date**: `cosmetics_personal_care` is active with
  `opened_date_tracking`, and `extract-cosmetics-v1` feeds `ExtractionItem.opened_date`
  through candidate accept to a persisted, gated (`review_state="proposed"`)
  `opened_date` assertion that planning and chat grounding read. An item without an
  opened date stays `null`, never inferred.

### Switches in play (names only; values live in the uncommitted `.env`)

| Setting | Purpose | Shipped default |
|---|---|---|
| `SG_PROVIDER_ID` | adapter id; `fake` keeps everything local | `fake` |
| `SG_MODEL_ID` | vision model id; the Settings picker overrides it at runtime | `deepseek-v4-flash-vision-exp` |
| `SG_PROMPT_CATEGORY` | versioned extraction prompt selection (`food`, `medicine`, `cosmetics`) | `food` |
| `SG_CONFIDENCE_THRESHOLD` | auto-accept floor for non-gated fields (uncalibrated, `G-A9`) | `0.9` |
| `SG_PER_JOB_CAP` | per-job worst-case cost cap in USD | `none` (uncapped) |
| `SG_MONTHLY_CAP` | household monthly cap in USD, enforced from the durable `provider_call` ledger | `none` (uncapped) |
| `SG_CONSENT` | cloud consent switch; OFF means no key read and no call | `false` |

### Run planning and chat

With consent on (`SG_CONSENT=true` and a configured `SG_PROVIDER_ID`) against the API:

```sh
curl -sS -X POST 'http://localhost:8003/v1/planning/run?household_id=<HOUSEHOLD_ID>'
curl -sS 'http://localhost:8003/v1/planning/suggestions?household_id=<HOUSEHOLD_ID>'
curl -sS -X POST 'http://localhost:8003/v1/planning/suggestions/<SUGGESTION_ID>/confirm?household_id=<HOUSEHOLD_ID>'
curl -sS -X POST 'http://localhost:8003/v1/chat/food?household_id=<HOUSEHOLD_ID>' \
  -H 'Content-Type: application/json' -d '{"message":"When does the milk expire?"}'
```

Planning and chat change no catalogue state; each metered call leaves one
`provider_call` ledger row and is consent-gated before the call.

### What stays OFF by default

Nothing calls a provider until `SG_CONSENT=true`; the planning button and the chat
screen then refuse with a visible reason (`consent_disabled`) and make zero calls and
zero rows. No scheduling, no automatic run, no streaming. Caps ship **uncapped** per
owner fork F2 — re-evaluation is owed; when a cap is set the mechanisms refuse
**before** any call (the per-job cap in the router, the monthly cap summed from the
committed ledger across jobs).

### Phase 3 non-goals (owned by the next phase, not delivered here)

- Live web enrichment / `search_and_summarize` (owner: nice-to-have, deferred).
- Auto-scheduling or automatically running suggestions.
- A second provider or multi-provider routing/fallback.
- Streaming chat, or persisted chat history (the transcript is component state only).
- Per-field accept UI for gated values beyond what exists (a proposed `opened_date`
  stays proposed until a later acceptance surface).
- Provider analytics / dashboards.

Phase 3 is proved by `backend/tests/test_phase3_e2e.py` (six gate groups on the real
HTTP path, zero network) plus the per-slice suites, and closes on blueprint:531.

## Enrich runbook — Jina fallback key (`JINA_API_KEY`)

The Enrich lookup is a committed, **unwired** library
(`backend/app/services/enrich/`): OpenFoodFacts first, Jina Search as the
fallback for OFF misses/degradation and non-food input. It is not served by any
route yet. When its endpoint lands, the Jina leg authenticates with
`JINA_API_KEY`.

### Rotate the key

1. Put the key in the host `.env` as `JINA_API_KEY` (see `.env.example`). `.env`
   is gitignored (`.gitignore:6`); the value is never printed, logged, or
   committed.
2. The backend reads it through `Settings.jina_api_key` (declared in
   `backend/app/config.py`). A `JINA_API_KEY` process environment variable is the
   fallback when the field is unset.

### How the key is resolved (precedence)

`resolve_api_key(explicit)` in `backend/app/services/enrich/jina.py` resolves in
this order:

1. **explicit argument** — the test / dependency-injection seam;
2. **`Settings.jina_api_key`** — the declared settings field (host `.env`);
3. **`JINA_API_KEY`** process environment.

No key at any layer degrades loudly (`missing_key:`) and sends **nothing** — the
client never sends an unauthenticated request. The `Authorization: Bearer <key>`
header is added at **send time only** (`authorize()`); builders, snapshots and
log lines carry header **names only**, and the key value is never returned,
stored, or logged.

A worked example of the exact request the driver builds (EU-default base, header
names, repeated `site:` query) is committed at
`docs/enrich-jina-request-example.md`; its shape is asserted against the real
driver constants by
`backend/tests/test_sg082_enrich_jina.py::test_worked_example_artifact_matches_the_real_driver`.

