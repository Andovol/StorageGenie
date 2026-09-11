SG-024 — Hatchling fix, rebuild, ISS-1 re-proof, remap, up, UI, restart (opencode, medium): COMPLETE — all goals green, receipted

BASE ref: `automation` → resolved commit `11d92f159b3ea76aef7e9f498239d36ccd191bb4`
  (packet tip at slice start; two fields, never one).
WORK_HEAD: recorded in receipt note (CO-55(b) — report must not carry the hash of the commit
  that contains it; work-HEAD placed on the notes ref instead of inside this report).
Work dir: `/home/andrei/StorageGenie` | origin: `git@github.com:Andovol/StorageGenie.git`
Slice window: 2026-09-11 ~14:2x UTC (whole slice far below the 1800 s early-close / 2100 s overall
  budget; leg wall-clock not separately instrumented — observed pytest durations 0.94 s / 1.66 s /
  6.38 s / 6.49 s of the 600 s suite bound; lock leg ~60 s of 300 s; build well within 1500 s;
  probes within 120 s; no bound approached).
MODEL: `unknown` — no model id appears in the runner argv
  (`opencode run --auto --dir /home/andrei/StorageGenie --variant medium ...` quoted verbatim from
  `/proc/$PPID/cmdline`) nor in provider metadata reachable from confinement. Per standing rule:
  quoted after every slice, `unknown`, never guessed. (Model is the CLI default and is omitted per policy.)
EFFORT: `medium` — provenance: `--variant medium` in the same parent-process argv (proven readable).
CODER: `opencode` (packet `coder:` head + argv).

## Verdict

COMPLETE slice WITH receipt (a success per the packet's transport-kill clause): G1 re-proved green,
G2 fixed via the documented lock-first→fallback path with step-8 green quoted, G3 ISS-1 re-proved
in-image (both decoder nodes + full suite green-except-nothing), G4 remap+up+health+suites+UI+restart
all quoted. No criterion passed vacuously: every pass names counts, outputs, and elapsed; the two
mid-slice findings (BUILDX_CONFIG, editables) are reported with evidence, not smoothed over.

## G1 — re-verify the gates: PASS

- Starting tree state: CLEAN — `git status --porcelain` empty at slice start (branch `automation`,
  HEAD `11d92f1`). Any dirt would have been a STOP before all other goals; none existed.
- Docker verdict: `docker info` exit 0 — Client+Server 29.6.2, Context `rootless`, Containers 0 /
  Images 0 at probe time. `docker buildx ls`: `rootless` runner `running` (v0.31.2); the `default`
  builder errors (`permission denied ... /var/run/docker.sock`) — not our route, never selected.
  Route re-proved, never inherited.
- Listeners: `8000` foreign (no owning pid; `curl /v1/health` → plain-text `Not Found` — NOT our
  backend), `8001` foreign (`uvicorn` pid 730504; FastAPI `{"detail":"Not Found"}` — NOT our backend).
  `8003`/`5173`: `NO-8003-5173-LISTENERS` (free, twice: G1 probe and G4 pre-bind recheck). 8000/8001
  never touched.
- `docker compose config` valid as-handed (`8000:8000`, `VITE_API_BASE=http://localhost:8000`).
- Premises verified (PG-IC-09), each with live proof: `.cache/buildx` exists + `.gitignore:38`
  `.cache/` entry (adopted, not duplicated); `.env` present 203 B (presence only, CO-44); README
  12× `:8000` lines (`:40,104,106,109,110,117,125,126,127,129,138,140` — matches SG-023's corrected
  count); `uv` 0.11.28 at `/usr/local/bin/uv` (required `UV_CACHE_DIR=/tmp/uv-cache`: the HOME cache
  is read-only — `Failed to initialize cache at /home/andrei/.cache/uv ... Read-only file system`).

## G2 — hatchling fix, LOCK-FIRST: PASS (via documented fallback)

- LOCK-FIRST attempt (bound 300 s): `uv pip compile --all-extras --python-version 3.12
  backend/pyproject.toml -o /tmp/requirements.lock.new` → exit 0, but the output contains NO
  hatchling entry (build-system `requires` are by design invisible to a project-deps compile) AND
  churns 5 unrelated pins (`alembic 1.19.1→1.19.2`, `anyio 4.15.0→4.15.1`,
  `ast-serialize 0.9.0→0.11.1`, `ruff 0.16.5→0.16.7`, `uuid-utils 0.17.0→1.0.0`). Adopting it would
  violate the HATCHLING-SCOPED constraint (reshuffle = STOP, never quiet accept). This is the quoted
  compile-impossible evidence; the fallback ran ONCE, never as a shortcut (PG-IC-03).
- Fallback pins resolved via `uv pip compile`: `hatchling==1.32.0`, `editables==0.6`
  (satisfies the bare `requires = ["hatchling"]` in `pyproject.toml:51`).
- Fallback line (`backend/Dockerfile:7`, the ONLY Dockerfile change):
  `RUN pip install --no-cache-dir "hatchling==1.32.0" "editables==0.6"`
  - The first single-package attempt (hatchling alone) moved the failure from
    `BackendUnavailable: Cannot import 'hatchling.build'` to
    `ModuleNotFoundError: No module named 'editables'` (hatchling's editable-builder dep, absent
    under `--no-build-isolation --no-deps`). Same layer, same cause family (isolation-off room lacks
    build-backend deps) — the ONE line was extended, no redesign. Quoted here, not hidden.
- BUILD ROUTE FINDING: with `BUILDX_CONFIG` unset, builds fail with
  `failed to update builder last activity time: ... read-only file system` (HOME docker dir is
  read-only). With the carried D12 route `BUILDX_CONFIG=/home/andrei/StorageGenie/.cache/buildx`,
  the build proceeds. (Caution recorded: compose/buildx print exit 0 even on build failure — output
  text is the verdict source, never the code.)
- Rebuild (bound 1500 s), step 8/8 green, quoted:
  `Building editable for storagegenie-backend (pyproject.toml): finished with status 'done'`;
  `Successfully installed storagegenie-backend-0.1.0`; export + unpack to
  `docker.io/library/storagegenie-backend:latest` done. No other red layer.
- `requirements.lock`: UNTOUCHED. `pyproject.toml`: untouched.

## G3 — ISS-1 re-proof in the image: PASS (no ports, no live writes)

- Decoder nodes in-image (`docker compose run --rm --no-deps backend python -m pytest -v
  tests/test_signals.py -k "..."`, 2 passed, 5 deselected in 0.94 s), quoted:
  `tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier PASSED [ 50%]`
  `tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence PASSED [100%]`
  (Signal-file gate: `7 passed ... in 1.66 s` on the unfiltered file run.)
- Full backend suite in-image: `66 passed, 11 warnings in 6.38 s` — green EXCEPT NOTHING
  (no sandbox excuse, no non-decoder red).
- Interpreter note: the packet names `venv/bin/python` in-image; the image carries system python
  only (no venv) — used `python` (3.12), resolved not assumed. Identical collection (66 tests).
- mypy NOT run: no Python code changed (Dockerfile + compose + README only) — stated, not silently omitted.
- ISS-1 is owned HERE — no further carry.

## G4 — remap, up, health, suites, UI, restart: PASS

- Precondition rechecked immediately before `up`: `PREBIND-FREE-8003-5173`; 8000/8001 still foreign.
- D20 remap diff (authorized product change): `docker-compose.yml` `ports: ["8000:8000"]` →
  `["8003:8000"]`, `VITE_API_BASE=http://localhost:8000` → `http://localhost:8003`; README 12×
  `http://localhost:8000` → `http://localhost:8003` (post-change: `grep -c 8000` = 0, 12× `:8003`
  runbook lines at the same 12 line numbers). Container-internal port 8000 and `CORS_ORIGINS`
  (`:5173`) unchanged. `docker compose config` proves validity (`published: "8003"`,
  `VITE_API_BASE: http://localhost:8003`).
- `docker compose up -d --build`: `Image storagegenie-backend Built`,
  `Image storagegenie-frontend Built`, `Container storagegenie-backend-1 Healthy` (health-gated
  before frontend start).
- Health: `curl http://localhost:8003/v1/health` → `{"status":"ok","db":"ok","storage":"ok"}`
  (our backend answering — anything else would have been the collision STOP; no collision).
- Exec suite: `docker compose exec -T backend python -m pytest -q tests/` →
  `66 passed, 11 warnings in 6.49 s`.
- UI (OR-leg via dev-server shell, served bytes not a log line): `curl http://localhost:5173/` →
  `<!DOCTYPE html> ... <title>StorageGenie</title> ... <div id="root"></div> ...
  <script type="module" src="/src/main.tsx">`. (`npm run build` not run; shell proof satisfies the leg.)
- Restart: `docker compose restart backend` → `Started`; `ps`: `Up 15 seconds (healthy)` with
  `0.0.0.0:8003->8000/tcp`; post-restart health JSON `ok`; 3×
  `docker inspect ... {{.State.Health.Status}}` → `healthy / healthy / healthy` (within retries).
- Zero catalog writes: suites ran on temp DBs; live DB only health-probed. One read-only
  `pragma integrity_check` → `ok` via host venv python (a co-issued `select count(*) from
  households` errored `no such table` — wrong table-name guess in a read-only probe; artifact only,
  no write, no defect).
- RUNTIME-DIRT FINDING (with destination): running/stopping the stack — and even a read-only sqlite
  open — creates `data/db/*.db-shm` / `*.db-wal` sidecars NOT covered by `.gitignore`
  (`data/db/*.db` matches only the main file). After final proofs, with no holders (`fuser` exit 1)
  and integrity `ok`, removed the 0 B `-wal` + `-shm` remnant; main DB untouched. No `.gitignore`
  change (outside the ceiling) — destination: a future slice may propose ignoring
  `data/db/*.db-shm` + `*.db-wal` (owner decision, not taken here).

## Live-state ledger

- Runs now: NOTHING of this project (stack `stop`ped after proof — `storagegenie-backend-1` and
  `storagegenie-frontend-1` exist, stopped; matches the SG-023 end-state of 0 running containers).
  `docker compose up -d` restores `:8003` (backend) + `:5173` (frontend). Foreign `:8000`/`:8001`
  listeners were never touched. No catalog rows written in any leg (temp DBs only, PG-EV-06/PG-PR-10).
- Proved per goal: G1 gates green · G2 fallback line + step-8 green · G3 2/2 decoder nodes + 66/66
  suite in-image · G4 remap + `:8003` health JSON + 66/66 exec suite + UI bytes + restart recovery.
- Stops: NONE (no STOP triggered; G2's churned-lock outcome was handled by the packet's own
  fallback branch, not a stop).
- Remaining delta: NONE for this pass — D12 manual compose pass is COMPLETE (D32 approval
  satisfied by this slice). Open threads for future slices (not this slice's debt): shm/wal
  gitignore proposal; `npm run build`-clean frontend proof (shell proof stands in).

## Outputs

- `docs/worklogs/SG-024.log` (execution ledger) · `docs/worklogs/SG-024_report.md` (this file)
- Code diff: `backend/Dockerfile` (+1 line), `docker-compose.yml` (2 lines), `README.md` (12 lines)
- Receipt: `git notes --ref=refs/notes/storagegenie-coder-reports` on the work HEAD, verified via
  `show`, quoted in the G6 close-out (result `note=yes`; `note=no` would be FAIL).

UNCLEAR (FIRST READ): none — every packet premise verified live before use; README's 12-line count
  confirmed exactly as-handed.
UNCLEAR (DURING EXECUTION): none blocking — BUILDX_CONFIG had to be set in-shell (carried D12 route,
  not inherited); hatchling-alone needed `editables==0.6` on the same single line; sqlite sidecars
  needed post-proof removal. All quoted with evidence.
UNCLEAR (REMAINING): shm/wal gitignore gap (destination above); next operator runs `up -d` to restore
  live `:8003`.
