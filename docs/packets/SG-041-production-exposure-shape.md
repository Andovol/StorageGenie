# SG-041 — production exposure shape: built UI served same-origin, loopback-only bind, deploy proof (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D49 (live-use pass first) needs direct internet access (D51); the host standard (`VPS.md` S1, adopted D53) is: the app binds **loopback only, one port**; the Architect then files an exposure request naming port/hostname/login; the owner creates the dynv6 hostname (DONE: `storagegenie.dynv6.net` created 2026-09-14 and verified resolving to `87.106.66.242` from the workstation); Launcher adds the nginx vhost, certbot certificate and nginx-level login after the owner approves the write. **This slice makes the app loopback-shaped, serves the built UI from the same one port, and deploys it — it does NOT expose anything.** DNS/TLS/nginx are entirely outside it. **Authoring date (metadata, never a gate):** 2026-09-14. mypy advisory stands. Transport: the standard job_spawn lane.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** is added by this slice (an alembic diff is a STOP — the deploy only runs `upgrade head`); frozen prompts (`extract-food-v1.md`, `extract-medicine-v1.md`, `extract-cosmetics-v1.md`, `planning-v1.md`, `chat-v1.md`) are read-only context; **compose/buildx print exit 0 even on build failure — output TEXT is the verdict source, never the exit code** (SG-024); rootless docker is the runtime — `default` builder/socket denials are expected, never routed around; the project-local `BUILDX_CONFIG` route stands (SG-023/024). **AI stays OFF**: `SG_CONSENT=false`, no provider calls, **$0 metered**. Health probe per `CO-92` (start: stack down → `unanswered` with the listener evidence is acceptable, SG-031 precedent; end: quoted).
**Guards invoked (0.25.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-06` live-rows-reported · `PG-EV-08` before-observable · `PG-EV-09` both-runs-committed · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-08` expectation-bounds · `PG-IC-09` premises-live · `PG-PR-01` capability-model · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-goes-live · `PG-PR-06` runtime-vs-budget · `PG-PR-10` which-db-and-grant · `PG-DP-01` delivery-by-delivery-path · `PG-DP-04` two-consecutive-runs.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite, 1800s build+up leg, 300s migrate/seed. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: the production SQLite (`/data/db/storagegenie.db`, host bind `./data/db`) — `alembic upgrade head` + `app.seed` ONLY, AUTHORISED by the owner for this slice (D54, 2026-09-14; `PG-PR-10`).** Expected pre-state: an early schema revision, **no real data** (no real assets/evidence/jobs — SG-039 found the durable `provider_call` table absent); capture `alembic current` + per-table row counts BEFORE any write; **any unexpected real rows → STOP and report; do not write over them.** Seed rows (household + the two users) are reported with their identifiers and left in place (`PG-EV-06`). No other writes to any database. **Restart: the compose stack (rebuild + `up -d`) — nothing else.** **NETWORK: none for the app** (docker registry pulls for the build only).

## Why this exists

The live pass needs the app reachable from the internet, and the host standard routes that through **one loopback port + nginx + a login** (`VPS.md` S1). Today's compose shape is the opposite: `8003:8000` and `5173:5173` publish on all interfaces (`docker-compose.yml:6,30`), the UI is the Vite **dev server** (`frontend/Dockerfile:7`), and the client hardcodes `http://localhost:8003` as its API base (`frontend/src/api/client.ts:12`) with CORS pinned to `http://localhost:5173` (`backend/app/config.py:19`) — a tunnel-shaped dev setup. This slice converts it to the production shape and proves it on the real host: one container, one loopback port, the built UI served by the backend itself.

## G1 — static serving in the app (`backend/app/main.py`)

Serve the built frontend from the same FastAPI app, mounted AFTER all `/v1` routers:
- `GET /` returns the built `index.html` (`200`, `text/html`, containing `<div id="root"></div>` — the marker at `frontend/index.html:9`) instead of today's JSON placeholder (`main.py:66-68`).
- SPA fallback: an unknown non-`/v1` path (e.g. `GET /catalog/whatever`) returns the same `index.html` (client-side routing).
- **`/v1` is never shadowed:** `GET /v1/this-route-does-not-exist` still returns the app's JSON problem shape (`404`, `application/problem+json` — `main.py:33-44`), never HTML.
- `/docs` and `/openapi.json` keep working (or the report says why not).
- The static root is a path inside the image the build stage produced; when it is absent (e.g. a bare dev run without a built UI), the app must still start and serve `/v1` — name the chosen fallback behaviour in the report.

## G2 — the production compose shape (`docker-compose.yml`, `backend/Dockerfile`)

- **The backend is the only default service**, published **`127.0.0.1:8003:8000`** (loopback only — `VPS.md` S4).
- **The frontend dev server moves behind a `dev` profile** (`profiles: ["dev"]`), still `127.0.0.1:5173:5173`; `docker compose up` (no profile) starts the backend only; `--profile dev` restores today's two-service development setup.
- **The UI is BUILT from the committed frontend sources during the image build** — not from the dev server, not from a committed `dist`. `frontend/dist` is gitignored and **must never be committed** (`PG-SC-10`). A multi-stage `backend/Dockerfile` (node builder → python runtime) is the apparent route; if the build context must widen to the repo root, a `.dockerignore` (new) is in the ceiling. Decide the mechanism, report it.
- **Build the UI with `VITE_API_BASE=https://storagegenie.dynv6.net`** (the public origin; same-origin once exposed — no runtime CORS logic). If you find that value wrong for the built artifact, stop and say so before choosing another.
- Healthcheck and `restart: unless-stopped` stay.

## G3 — deploy proof on the host (this is the live leg; D54)

Order: pre-state → build → up → migrate → seed → verify.
1. **Pre-state quoted** (`PG-EV-08`): stack down / listener state (`ss -ltnp`), `alembic current`, per-table row counts.
2. `docker compose up --build -d` (rootless; BUILDX_CONFIG route) — build TEXT quoted; a build failure is read from the output text, never exit 0.
3. `docker compose exec backend python -m alembic upgrade head` (300s) — head quoted.
4. `docker compose exec backend python -m app.seed` (300s) — output quoted; row ids reported.
5. **The shape proven, by value:** `curl -s http://127.0.0.1:8003/v1/health` → `{"status":"ok","db":"ok","storage":"ok"}` · `curl -s http://127.0.0.1:8003/` → built index (quote the `<div id="root">` line and one hashed asset reference) · `ss -ltnp` → 8003 on `127.0.0.1` **only**, and **no** `0.0.0.0`/`::` listener for 8003/8000/5173.
6. **Two consecutive bring-ups** (`docker compose up -d --build` a second time) both healthy (`PG-DP-04`).
7. `docker stats --no-stream` one sample (memory) + the listening port quoted — the evidence the Architect's exposure request needs (`VPS.md` S6).

## G4 — README access truth (`README.md`)

- Replace the stale access/trust text (`README.md:86-88`: "LAN-only … Do not expose the Compose ports to an untrusted network until authentication and deployment controls are implemented") with the current truth: the app binds **loopback only**; the public entry is the host standard's nginx + https + login (planned, not yet live).
- Add a short **production shape** section: build-in-image, `docker compose up --build -d`, migrate/seed, the loopback health URL, and that the `dev` profile is the development fallback. Keep every existing phase runbook intact (edit only what is now false; append the rest).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-041.log`, `{{WORKLOG_DIR}}/SG-041_report.md`, `{{WORKLOG_DIR}}/SG-041_verify.log` (FAIL-then-PASS both runs raw; deploy evidence; `ss` / `docker stats` output; two-bring-up proof). First token `SG-041`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0` — zero provider calls); live-state ledger (live DB writes: migrate + seed rows, by id; network: build pulls only); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/main.py` · `backend/Dockerfile` · `docker-compose.yml` · `.dockerignore` (new, only if the build context widens) · `README.md` · `backend/tests/test_production_serving.py` (new) · `docs/worklogs` (3 files). **Anything else is a STOP** — including `frontend/` source and `frontend/Dockerfile` (the build uses them as-is; a needed frontend change is a finding: STOP if it blocks, otherwise report and ship the rest). No new dependencies, no `backend/app/config.py` change, no `.env` change.
- Every requirement above names a file the ceiling enables it (packet lesson M6/M9/M10); if you find one that does not, STOP and say which.
- **Live-write authority is exactly:** `alembic upgrade head` + `app.seed` against the production SQLite (D54). Nothing else writes. Unexpected pre-existing real data → STOP (`PG-IC-08`). AI off; no provider key is read.
- Cross-product (`PG-IC-01`): G1 needs the mount point inside the ceiling; G2 the compose + Dockerfile files; G3 the running stack (no restart is ordered after you exit); G4 README. A blanket exclusion is written with its exception in the same sentence (e.g. `.dockerignore` may exclude `frontend/node_modules` from the BUILD CONTEXT — nothing else).
- `PG-IC-03`: no remediation step shares a condition with a stop-gate — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. The full backend suite runs, so the §3 conditional derived-test-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s ordinary probes · 600s backend suite · 1800s build+up leg · 300s migrate/seed · **2100s early-close** (at 2100s elapsed: stop starting new work, commit what is finished, write the report, publish the receipt) · **2700s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): one mount + one profile + one build stage; nothing else.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads (in particular `main.py:66-68` root JSON, `client.ts:12`, `docker-compose.yml:6,30`, `frontend/Dockerfile:7`).
- **FAIL-then-PASS, both runs committed (`PG-EV-09`):** pre-change `GET /` returns `application/json` (not the HTML marker) and `GET /catalog/x` is `404` problem+json; post-change `GET /` → `200 text/html` with `<div id="root">`, `/catalog/x` → the same index (SPA fallback), `/v1/this-route-does-not-exist` → `404` `application/problem+json` (never HTML), `/docs` still `200`.
- Gates are seen to fail (fed a wrong expectation in the same run, `PG-EV-01`); the artifact checked is the SERVED response, not the command exit (`PG-EV-02`); the property stated is "the built bundle's API base is `https://storagegenie.dynv6.net`", checked against the built asset (`PG-EV-05`).
- Deploy: health JSON exactly `{"status":"ok","db":"ok","storage":"ok"}` via `127.0.0.1:8003`; UI served; `ss` proves loopback-only; two consecutive bring-ups healthy; memory sample quoted.
- DB: migrate head quoted; seed ids reported and left; pre-state counts quoted; no unexpected rows.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; touched files add zero mypy errors; secret scan 0; **no migration added** (alembic diff empty); no frozen-prompt diff; no ignored file staged (`frontend/dist` included); nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: live DB writes (seed ids + migrate head), live spend `$0`, network = build pulls only.
- **Receipt note on the notes ref (proven shape, unchanged obligation):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-041 | Report: docs/worklogs/SG-041_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary probes · 600s backend suite · 1800s build+up leg · 300s migrate/seed · 2100s early-close · 2700s overall; $0 metered; actual-versus-budget per leg with units.
