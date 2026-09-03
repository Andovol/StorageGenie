SG-005 — Phase 0 foundation verification and repair report

BASE REF: automation
BASE resolved: 535a2d3fb858f5e8d88906c07035c9318e578312
WORK_HEAD: 4532f2727d06363c5f8af9a28696d6c797202bd8
Work dir: /home/andrei/StorageGenie
Remote: git@github.com:Andovol/StorageGenie.git
Model: unknown (no model ID in process arguments or provider metadata)
Reasoning effort: high (process arguments contained `-c model_reasoning_effort=high`)
Timeouts: 120s ordinary commands; 600s suite/migration/rebuild commands; 2100s overall. No command was killed or hung.

## G1 — truthful health and start/end delta

The baseline source inspection found that `/v1/health` executed `SELECT 1` and attempted to create the storage directory, but always returned top-level `status: "ok"` even when a component status was `error`. The repair now reports top-level `error` and HTTP 503 whenever either component fails. Storage health checks that the configured root is an existing, accessible directory; it does not create missing paths.

Required start legs, before the repair:

- Exact curl command: `curl -s http://localhost:8000/v1/health`
- Verbatim output: `Not Found`; exit `0`. This is the foreign shared-host service on port 8000, not this checkout.
- Exact fallback command: `python3 -c "from fastapi.testclient import TestClient; from app.main import app; print(TestClient(app).get('/v1/health').json())"`
- Verbatim terminal result: `ModuleNotFoundError: No module named 'sqlalchemy'`; exit `1`. The fallback was attempted and unanswered because this confined run had no backend dependencies.

The repaired failure was demonstrated before the restored success, against scratch-only paths. With a valid temporary SQLite DB and a missing temporary storage root, TestClient returned verbatim:

```text
503
{'status': 'error', 'db': 'ok', 'storage': 'error'}
```

After restoring the temporary storage directory, the same probe returned:

```text
200
{'status': 'ok', 'db': 'ok', 'storage': 'ok'}
```

These failing and restoring runs are also committed in `docs/worklogs/SG-005.log`.

Required end legs:

- Exact curl command: `curl -s http://localhost:8000/v1/health`
- Verbatim output: `Not Found`; exit `0`.
- Exact fallback command: `python3 -c "from fastapi.testclient import TestClient; from app.main import app; print(TestClient(app).get('/v1/health').json())"`, resolved to the clean temporary dependency environment’s `python3`.
- Verbatim output: `{'status': 'ok', 'db': 'ok', 'storage': 'ok'}`; exit `0`.

Delta: the curl leg remained the foreign 404 (`Not Found` → `Not Found`); the application fallback moved from unavailable at baseline to a truthful healthy response after the temporary dependency environment was provisioned and the repair was applied. The explicit repaired-leg delta is missing storage → HTTP 503/error, then restored storage → HTTP 200/ok. No production service was restarted.

## G2 — non-vacuous pytest and isolation

Added `backend/tests/test_health.py` with three invoked TestClient tests:

- healthy DB/storage returns HTTP 200 and all three statuses `ok`;
- missing storage returns HTTP 503 with top-level and storage `error`;
- a failing DB probe returns HTTP 503 with top-level and DB `error`.

The full backend command collected `3` tests and reported `3 passed` in `0.49s` with exit `0` (plus two dependency deprecation warnings). This is non-vacuous; exit 5 was not observed after the test was added. The module sets a temporary SQLite URL and temporary storage root before importing the app. No test uses `/data/db/storagegenie.db`, `/data/storage`, or `./data/`; no rows were created outside temporary space.

## G3 — lint gates

Final Ruff command: `cd backend && ruff check .` with exit `0` and output:

```text
All checks passed!
```

The pre-existing applied migration has one trailing-space W291 at its `Revises:` docstring line. The migration was not edited, as required. A precise Ruff per-file W291 exception for that one applied revision was added; all other Ruff rules and files remain checked. This is a disclosed lint exception, not an empty or skipped gate.

Mypy was run advisory with `mypy app`: `43 errors in 10 files`, exit `1`. The errors are pre-existing strict-typing findings and were not broadened into this foundation slice.

Frontend lint was run as-is from the repository root with `npm run lint --prefix frontend`. The underlying command emitted `sh: 1: eslint: not found`; the existing script’s `|| true` made the script exit `0`. There were no emitted ESLint diagnostics to count because ESLint was unavailable. The `|| true` was retained because an observed-clean ESLint run did not occur.

## G4 — migration state

The only version file is `backend/alembic/versions/0201cf10c56c_001_core_foundation.py`, with head revision `0201cf10c56c` and `down_revision = None`. A fresh scratch SQLite database upgraded with `alembic upgrade head`; `alembic current` reported `0201cf10c56c (head)`, and the scratch `alembic_version` row was `0201cf10c56c`. The expected foundation tables were created. Head and applied revision match, so zero new migrations were added. No applied migration file was edited.

The fresh application connection independently observed `foreign_keys = 1` and `journal_mode = wal`; the busy-timeout observation is recorded below. No live database was migrated or written.

## G5 — busy timeout, lockfile, and base image

`backend/app/db.py` now names `SQLITE_BUSY_TIMEOUT_MS = 5000` and applies `PRAGMA busy_timeout=5000` in the existing SQLite connect listener, with a comment describing locked-writer wait semantics. A fresh connection reported verbatim:

```text
{'busy_timeout': 5000, 'foreign_keys': 1, 'journal_mode': 'wal'}
```

Added `backend/requirements.lock` with exact runtime, development, and build dependency versions. A clean temporary Python 3.12.3 environment installed the lockfile with exit `0`; the local package then built using the locked Hatchling `1.32.0` with `--no-build-isolation` and exit `0`; `pip check` reported `No broken requirements found.` The verification environment reported FastAPI `0.141.1`, Hatchling `1.32.0`, and Ruff `0.16.5`.

`backend/Dockerfile` now uses `python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7`. Docker Hub reported the tag active; its amd64 image digest was `sha256:c00fc7b44d844b6da22861ec24af43968a5200eac4ec607b4725d585165d6b49`, and its OCI index digest was the digest pinned above. The Dockerfile installs `requirements.lock` before copying source, then installs the local package from the locked build backend. An actual Docker build is unanswered: the Docker client was available, but the API returned permission denied for `/var/run/docker.sock`; no sudo or privilege workaround was attempted.

## G6 — committed outputs and scope

The work commit contains these allowed outputs and repairs:

- `backend/app/api/v1/health.py`
- `backend/app/db.py`
- `backend/Dockerfile`
- `backend/pyproject.toml`
- `backend/requirements.lock`
- `backend/tests/test_health.py`
- `docs/worklogs/SG-005.log`

This report is `docs/worklogs/SG-005_report.md`, supplied as the sole report output for the receipt publisher and therefore committed by the receipt commit. No UI, asset/evidence/export behavior, expiry/LLM/OCR, worker infrastructure, `.env`, live DB, live storage, or service was changed. The worktree was clean before publisher invocation except for this canonical untracked report.

## G7 — evidence prefill and publisher

The requested header is exactly `contract_sync=refresh version=0.17.2`. The work commit to push is `4532f2727d06363c5f8af9a28696d6c797202bd8`. The first mandated prefill from the non-ancestor candidate `324857cf24b53c7f85f827c18bdc27cf7ca66158` returned non-fast-forward; no force push was used. The prior evidence tip was merged content-neutrally, producing this candidate. The mandated prefill and fetch equality will be verified before invoking the unmodified publisher:

```text
git push origin 4532f2727d06363c5f8af9a28696d6c797202bd8:refs/heads/storagegenie-evidence
git fetch origin refs/heads/storagegenie-evidence
git rev-parse origin/storagegenie-evidence
```

Publisher command, unmodified:

```text
/opt/storagegenie-dispatch/finalize_dispatch_report.sh SG-005 "contract_sync=refresh version=0.17.2" docs/worklogs/SG-005_report.md 4532f2727d06363c5f8af9a28696d6c797202bd8
```

The final handoff quotes the prefill return code and equality, publisher return code, receipt hash, `Dispatch-ID: SG-005` trailer, and final clean-tree proof. No Coder-side SSH check was attempted because the dispatch key is absent in the confined run.

UNCLEAR — FIRST READ: The repository contains the SG-005 packet and project AGENTS.md/STATE.md, but no repository copies of the referenced ARCHITECT.md, PACKET.md, DISPATCH.md, PRODUCTION.md, CLOSE.md, LEDGER.md, or RATIONALE.md; the available project instructions and packet were used.
UNCLEAR — DURING EXECUTION: Backend dependencies and lint tools were absent from the initial confined environment; a clean temporary environment was used for verification. Docker API access remained permission-denied and the actual image build is unanswered; no privileged route was attempted.
UNCLEAR — REMAINING: Frontend ESLint remains advisory/unavailable because the existing dependency tree has no eslint executable; the pre-existing applied migration W291 is excluded precisely rather than edited. Publisher artifact hashes and final clean-tree state are supplied in the handoff after G7.
