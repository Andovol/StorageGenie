# SG-041 report — production exposure shape: built UI served same-origin, loopback-only bind, deploy proof: GREEN

**BASE REF:** `automation` → resolved commit `cec98374fcb0ba72e761fba60cc06fc99448b877` (two fields, as required).
**WORK_HEAD:** the commit carrying this file; the exact hash is published in the notes-ref receipt
(`refs/notes/storagegenie-coder-reports`), added last with no commit after.
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per `CO-78` (from process arguments, never an identity line):** own process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort **`medium`**; no
`--model` flag on argv (packet: CLI default, omitted per policy) → model **`unknown`** (a flag that does not
exist is not a guess I am willing to make).
**DATABASE:** production SQLite `/data/db/storagegenie.db` (host bind `./data/db`), writes limited to
`alembic upgrade head` + `app.seed` (D54, `PG-PR-10`). **Restart:** compose stack only. **NETWORK:** build
pulls only (npm ci + image/pip metadata); the app made no egress, `SG_CONSENT=false`, zero provider calls.
**Spend:** `$0` metered.

## Verdict

GREEN. The default Compose shape is now one service: the backend image serves the JSON API **and** the built
UI on one loopback port (`127.0.0.1:8003:8000`). The UI is compiled from the committed `frontend/` sources in
a node build stage with `VITE_API_BASE=https://storagegenie.dynv6.net`; the stale on-disk `frontend/dist` is
excluded from the build context and never committed. On the live host the built `index.html` and its hashed
asset are served by the app (`<div id="root"></div>` + `/assets/index-khM4mS2k.js`), `/v1` unknowns return
`application/problem+json` and are never shadowed by HTML, `/docs`/`/openapi.json` still answer, health is
exactly `{"status":"ok","db":"ok","storage":"ok"}`, `ss` shows 8003 on `127.0.0.1` only, and two consecutive
bring-ups are both healthy. Nothing is exposed: DNS/TLS/nginx remain outside this slice.

## Premise findings (verified in-slice; corrections are findings, not obstacles)

1. **`F-SG041-1` — the client does not hardcode `8003`.** `frontend/src/api/client.ts:12` is
   `const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";`. The packet's "hardcodes
   `http://localhost:8003`" is the *compose dev* `environment: VITE_API_BASE=http://localhost:8003`
   (`docker-compose.yml:35` old), not the source. Verified against the tree.
2. **`F-SG041-2` — pre-change unmatched routes are plain JSON, not problem+json.** The acceptance says
   pre-change `GET /catalog/x` is `404 application/problem+json`. Measured on the base app: `GET /` →
   `200 application/json {"name":...}`, `GET /catalog/whatever` → `404 application/json {"detail":"Not Found"}`,
   `GET /v1/this-route-does-not-exist` → `404 application/json {"detail":"Not Found"}`. FastAPI's default
   unmatched-route handler runs because the app registers its problem handler for `fastapi.HTTPException`,
   which is not in the MRO of Starlette's router-404. I left the pre-change observation as measured and made
   the new catch-all emit `application/problem+json` for `/v1` unknowns (the post-change half of the criterion).
3. **`F-SG041-3` — the production service cannot keep the `./backend:/app` bind.** The multi-stage image bakes
   the UI at `/app/static`; a source bind at `/app` shadows it. Design call (reported, not hidden): the backend
   default service drops the source bind and `--reload` (code goes live by image build, `PG-PR-04`); the `dev`
   profile keeps the frontend dev server. Backend live-reload is not restored by `--profile dev`.
4. **Pre-state DB is empty (no STOP trigger).** `alembic_version=0201cf10c56c`, 0 rows in every data table,
   `provider_call` absent — matches the packet's expected pre-state.

## G1 — static serving in the app (`backend/app/main.py`)

- `_static_root()` resolves `SG_STATIC_DIR`, default `/app/static` (the path the image build produces).
- `GET /` returns the built `index.html` (`200 text/html`, `<div id="root"></div>`); the catch-all
  `/{full_path:path}` is registered **after** all `/v1` routers and is **not** in the OpenAPI schema.
- SPA fallback: an unknown non-`/v1` path returns the same `index.html`; a real file under the static root is
  served (hashed assets); traversal is refused by an `is_relative_to` containment check.
- `/v1` is never shadowed: `/v1/this-route-does-not-exist` → `404 application/problem+json`
  `{"type":"about:blank","title":"Not Found","status":404,"detail":"Not Found: /v1/this-route-does-not-exist"}`.
- `/docs` and `/openapi.json` still `200` (`/v1/health` present in the schema).
- **Absent-static fallback (named):** with no built UI the app still starts and serves `/v1`; `GET /` returns
  the legacy JSON placeholder `{"name":"StorageGenie","version":"0.1.0"}` and SPA paths return problem+json 404.

## G2 — production compose shape (`docker-compose.yml`, `backend/Dockerfile`, `.dockerignore`)

- Backend is the only default service, published `127.0.0.1:8003:8000`; frontend moved behind
  `profiles: ["dev"]` and published `127.0.0.1:5173:5173`. `docker compose config --services` = `backend`;
  `--profile dev` = `backend, frontend`. Healthcheck and `restart: unless-stopped` unchanged.
- `backend/Dockerfile` is multi-stage: `node:20-alpine` runs `npm ci` + `npm run build` (same base image tag
  the old `frontend/Dockerfile` used) with build arg/default `VITE_API_BASE=https://storagegenie.dynv6.net`;
  the pinned `python:3.12.11-slim-bookworm@sha256:519591…` runtime copies `/ui/dist` to `/app/static`.
  Build context widened to the repo root, so `.dockerignore` (new) is used.
- `.dockerignore` exclusions and their exceptions: VCS/local state (`.git`, `.gitignore`, `.cache`,
  `.rules-cache`), caches (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`), host dependency
  trees (`venv`, `frontend/node_modules`, `frontend/.vite`, `frontend/.scratch`), the stale/ignored
  `frontend/dist` (must be rebuilt, never reused), live data (`data`, `backend/data`), `docs`, and the secret
  `.env`. Nothing else is excluded; the backend and frontend sources remain in context.
- `frontend/` sources and `frontend/Dockerfile` are untouched — the build consumes them as-is.

## G3 — deploy proof on the host (live leg, D54)

Order ran pre-state → build → up → migrate → seed → verify.

- **Pre-state quoted:** stack down (`docker compose ps` 0 services; two exited containers), listener
  `LISTEN 127.0.0.1:8000` only (a foreign loopback process, not StorageGenie; no 8003/5173),
  `alembic current` = `0201cf10c56c`, all data tables 0 rows.
- **Build text verdict (never the exit code):** `Image storagegenie-backend Built`; node stage built
  `dist/assets/index-khM4mS2k.js` (251.56 kB). Baked asset property (`PG-EV-05`): 5×
  `https://storagegenie.dynv6.net`, 0× `http://localhost:8000`.
- **Migrate:** `0201cf10c56c → 20260908_sg013_observation → 20260908_sg014_candidate → 20260908_sg017_fts →
  20260912_sg025_provider_call → 20260914_sg035_foundations`; `alembic current` = `20260914_sg035_foundations (head)`.
- **Seed:** `Seeded household 01a0a029-1477-7ca0-b200-bce78a96c679 name=Popescu Household`;
  users `01a0a029-147b-7190-a0c8-64ea7bd649e6`, `01a0a029-147b-7190-a0c8-64fade707109`. Left in place.
- **Shape by value:** health `{"status":"ok","db":"ok","storage":"ok"}`; `/` `200 text/html` with
  `<div id="root"></div>` and `/assets/index-khM4mS2k.js`; `/catalog/whatever` `200 text/html`;
  `/v1/this-route-does-not-exist` `404 application/problem+json`; asset `200`; `/docs` `200`.
- **Loopback proof:** `ss -ltnp` → `127.0.0.1:8003` (rootlesskit) and the pre-existing foreign
  `127.0.0.1:8000`; **no** `0.0.0.0`/`::` listener for 8003/8000/5173.
- **Two consecutive bring-ups:** first `up -d` healthy; second `docker compose up -d --build` healthy
  (cached image, same container, no recreate needed). The rootless default-builder read-only activity warning
  on run 2 is quoted verbatim in the verify log; it is the expected `default`-builder denial and was not routed
  around (run 1 used the project-local `BUILDX_CONFIG`).
- **Exposure evidence:** `docker stats --no-stream` → `85.85MiB / 7.688GiB` (1.09%), port `8003`.

## G4 — README access truth

The trust-boundary paragraph now states the app binds **loopback only** and that the public entry is the host
standard's nginx + https + login (planned, not yet live). A new `### Production shape (single service)` section
documents the in-image build, `docker compose up --build -d`, migrate/seed, the `127.0.0.1:8003` health URL, the
`SG_STATIC_DIR`/absent-static fallback, and the `dev` profile fallback. Stale line-number references were
corrected; every Phase 0–3 runbook section is retained.

## Gates

- **FAIL-then-PASS, both runs raw in `SG-041_verify.log` (`PG-EV-09`):** pre-change
  `5 failed, 1 passed in 0.69s`; post-change `6 passed in 0.66s`.
- **Gate seen failing (`PG-EV-01`):** an in-process probe expecting `/v1` unknown to be `text/html` failed with
  `served content-type: application/problem+json` (exit 1). The earlier pre-change pytest run is itself the
  failing gate for the changed property.
- **Artifact is the served response (`PG-EV-02`):** curl of `/`, `/catalog/whatever`,
  `/v1/this-route-does-not-exist`, `/assets/index-khM4mS2k.js`, `/docs`, and the health JSON — not command exits.
- **Property not command (`PG-EV-05`):** the baked bundle’s API base is `https://storagegenie.dynv6.net`,
  counted in the built asset (5×) with `localhost:8000` at 0×.
- **Live rows reported (`PG-EV-06`):** seed ids above, left in place.
- **Before observable (`PG-EV-08`):** pre-state stack/listener/alembic/rows quoted.
- **Two consecutive runs (`PG-DP-04`):** both bring-ups healthy.
- Full suite: `2 failed, 186 passed in 12.43s`; base re-run at `cec9837`: `2 failed, 180 passed in 12.93s`
  (the same 2 `test_signals` decoder env reds — pyzbar/zbar and tesseract — proved at base, not inherited).
- `ruff check app tests`: `All checks passed!`. `mypy app/main.py`: 2 errors (the pre-existing `unused-ignore`
  at the two exception handlers, base had the same 2; delta 0). New test file: mypy clean.
- Secret scan of the diff: 0 occurrences of the provider key prefix. `git diff --check` clean.
- No migration added (alembic/model diff empty; only `upgrade head` ran). No frozen-prompt diff. No frontend
  diff. `frontend/dist` still gitignored (`git check-ignore` confirms). No ignored file staged.
- Nothing pushed to `storagegenie-evidence`; `{{RECEIPT_CMD}}` not run (packet says not to).
- No vacuous pass: the new tests invoke the real app and assert served bodies; the host proof uses the real
  built asset; the pre-change run fails as required.

## Live-state ledger

| Item | Value |
|---|---|
| Live DB writes | `alembic upgrade head` → head `20260914_sg035_foundations`; `app.seed` → household `01a0a029-1477-7ca0-b200-bce78a96c679`, users `01a0a029-147b-7190-a0c8-64ea7bd649e6`, `01a0a029-147b-7190-a0c8-64fade707109` (left) |
| Live spend | `$0` (no provider calls; `SG_CONSENT=false`) |
| Network | build pulls only (npm ci, docker/pip metadata); no app egress |
| Surface touched | production SQLite only, via the two authorised commands |

## Notes / standing-line items

- `docker compose config` prints the host `.env` secrets (including `OPENCODE_API_KEY`) to stdout. Existing
  behaviour, outside this ceiling, unchanged by me; I never committed or quoted the value. Destination: the
  Architect/exposure slice.
- The stale, gitignored `frontend/dist` (built earlier with the `localhost:8000` fallback) was left on disk
  (gitignored) and excluded from the build context; the image rebuilds from source.
- `ss` cannot attribute the pre-existing `127.0.0.1:8000` listener to a pid at this privilege; it is not a
  StorageGenie process (no uvicorn/vite match) and it is loopback, so it does not affect the shape.

UNCLEAR — FIRST READ: whether `G-A7`'s "one mount" required the development service to lose its source mounts;
I kept production at one bind (the data mount) and left the frontend dev mounts under the `dev` profile.
UNCLEAR — DURING EXECUTION: whether dropping the backend source bind (forced by `/app/static` being under
`/app`) is an acceptable loss of backend live-reload; reported as a design call.
UNCLEAR — REMAINING: whether the Architect wants `docker compose config`'s plaintext-secret emission addressed
in the exposure slice, or treats it as accepted operator tooling.
