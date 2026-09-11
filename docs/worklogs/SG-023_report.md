SG-023 — Manual compose pass on opencode/medium (D30): PARTIAL — G1 green, G2 STOP on Dockerfile pip layer, G3/G4 unanswered, receipted

BASE ref: `automation` → resolved commit `e0adff9e36e76ab1ea427dcb4237fb605e4f884b`
  (packet tip at slice start; two fields, never one).
WORK_HEAD: recorded in receipt note (CO-55(b) — report must not carry the hash of the commit
  that contains it; work-HEAD placed on the notes ref instead of inside this report).
Work dir: `/home/andrei/StorageGenie` | origin: `git@github.com:Andovol/StorageGenie.git`
Slice window: 2026-09-11 14:14:08 UTC → ~14:20 UTC (≈360 s of 2100 s budget; early-close 1800 s never reached).
MODEL: `unknown` — no model id appears in the runner argv
  (`opencode run --auto --dir /home/andrei/StorageGenie --variant medium ...` quoted verbatim from
  `/proc/$PPID/cmdline`) nor in the environment (`CODER=opencode`, `OPENCODE=1`, `OPENCODE_PID=1111296`
  present; no model variable). Per standing rule: quoted after every slice, `unknown`, never guessed.
EFFORT: `medium` — provenance: `--variant medium` in the same parent-process argv (proven readable).
CODER: `opencode` (argv + `CODER=opencode` + `OPENCODE=1`).

## Verdict

PARTIAL slice WITH receipt (a success per the packet's transport-kill clause): G1 fully green with all
stops obeyed; G2 builder route holds and the SG-013 apt layer installs, but the image does NOT complete —
Dockerfile step `[7/7]` fails deterministically over two attempts; G3 (ISS-1 in-image) and G4 (remap/up/UI/
restart) are UNANSWERED for lack of the image, loudly reported with their exact delta. No criterion passed
vacuously: nothing is claimed from an empty set, a skipped gate, or a host-side substitute.

## G1 — capability + collision probe: PASS (actual ~75 s of 120 s bound)

- Starting tree state: CLEAN — `git status --porcelain` empty at 14:14 UTC. SG-022 LEG4 clean (2026-09-11
  12:41 UTC) confirmed continuous; wedge question stays closed. No STOP before other goals.
- Docker verdict: `docker info` exit 0 — Client+Server 29.6.2, Context `rootless`
  (`unix:///run/user/1000/docker.sock`), rootlesskit 3.0.2/slirp4netns, Containers 0 / Images 0,
  Docker Root Dir `/home/andrei/.local/share/docker`. No denial — whole-slice STOP not triggered.
  `docker context ls`: `rootless *`; `default` errors on `/var/run/docker.sock` (expected, no root socket).
  `docker buildx ls`: `rootless*` / node `rootless` `running v0.31.2 linux/amd64 (+3)` selected;
  `default` → `Cannot load builder default: permission denied ... unix:///var/run/docker.sock` (expected
  under rootless, not a STOP). Binaries named, never assumed: `docker` /usr/bin/docker,
  `python3` /usr/bin/python3 (3.12.3), `curl` /usr/bin/curl; `pytest` absent on host PATH (in-image path
  reserved for G3, never assumed).
- Per-port occupants (read-only `ss -tlnp` + `/dev/tcp` + `curl /v1/health` — all three signals obtained,
  so the never-bind-blind STOP (`PG-SC-07`) is not triggered):
  - `8000` OPEN, foreign, EXPECTED — `ss` shows `127.0.0.1:8000 LISTEN` (unprivileged view, no process
    name); `curl :8000/v1/health` → `404`. Recorded, not touched, no stop. (Packet premise said
    docker-proxy/2449 ex privileged `ss` — unprivileged view cannot confirm the pid; difference noted,
    not bent to match.)
  - `8001` OPEN, foreign, EXPECTED — `ss` shows `127.0.0.1:8001 ... users:(("uvicorn",pid=730504,fd=7))`;
    `curl` → `404`. Recorded, not touched, no stop.
  - `8003` CLOSED/free — `/dev/tcp/127.0.0.1/8003` connection refused, `curl` exit 7 (`000`). No foreign
    occupant → G4 ports gate PASSES (candidate, not reservation).
  - `5173` CLOSED/free — same refusal/exit 7. G4 ports gate PASSES.
  - Cross-check, untouched: `0.0.0.0:8002 users:(("python",pid=3780707,fd=5))` — matches desk foreign map.
- `docker compose config` exit 0 — valid as-handed. `.env` present (`-rw------- 600, 203B`) — presence
  only, contents never read (`CO-44`). `frontend/Dockerfile` EXISTS (181B, `node:20-alpine`, EXPOSE 5173).
- Handed-tree corrections (premises verified before building; differences are findings):
  compose still `8000:8000` / `VITE_API_BASE=http://localhost:8000` (D20 remap NOT pre-applied — adopted
  as-handed, not duplicated); `README.md` names `:8000` on 12 lines (`:40,104,106,109,110,117,125,126,
  127,129,138,140` — packet said "~10 lines :40,104-140"; actual count 12); `.cache/` did NOT exist and
  `.gitignore` had NO `.cache` entry (SG-021 crash left neither — verified before adding).

## G2 — builder-state + image build: STOP (actual ~45 s of 1500 s bound)

- Desk #18 route FIRST: created project-owned `.cache/buildx` (was absent — adopted nothing, duplicated
  nothing) + exactly one `.gitignore` entry (`.cache/` + comment, `PG-SC-10` builder-state never
  committed). `/home/andrei/.docker/buildx` never touched; `DOCKER_CONFIG` never relocated.
  `BUILDX_CONFIG=/home/andrei/StorageGenie/.cache/buildx` exported for every build invocation.
- Builder selection quoted: `docker buildx ls` under the route → `rootless*` / node `rootless` running
  `v0.31.2`; activity-path read-only failure did NOT recur — desk route holds, second workaround not
  attempted (`PG-IC-03` STOP wins where stated, and here no STOP was needed on the route leg).
- Build: `docker compose build backend` attempt 1 (14:14:33 UTC, 22.8 s) → exit 1. Failing layer quoted:
  `> [7/7] RUN pip install --no-cache-dir --no-build-isolation --no-deps -e .` →
  `pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'hatchling.build'` (exit code 2),
  `Dockerfile:7`. Attempt 2 (L2 single transient retry, 14:15:06 UTC, ~20 s) → identical exit 1; apt step
  `[3/7] RUN apt-get update && apt-get install -y --no-install-recommends curl tesseract-ocr libzbar0
  && rm -rf /var/lib/apt/lists/*` shows `CACHED` — the SG-013 apt lines DID install (attempt-1 success
  cached), so the apt hypothesis is PROVED while the image is not. Deterministic → STOP stands; no
  Dockerfile redesign beyond the failing line's evidence (ceiling).
- New defect finding with destination (no base-commit pre-existing claim — none made): `backend/
  pyproject.toml:51-52` declares `requires = ["hatchling"]` / `build-backend = "hatchling.build"`, but
  `backend/requirements.lock` (uv pip compile) contains NO hatchling entry; the Dockerfile installs the
  lock then runs `pip install --no-build-isolation --no-deps -e .`, which needs hatchling present without
  isolation. Fix (lock vs Dockerfile) belongs to a follow-up slice — reported, never quietly edited.

## G3 — ISS-1 re-proof in image: UNANSWERED (needs the G2 image; 0 s spent, no vacuous claim)

- `docker compose run` gate never invoked image-less (an image-less run can only fail vacuously — not run,
  loudly reported). No decoder green claimed from host-side substitutes.
- Node IDs resolved for the follow-up (not executed):
  `tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`
  (barcode_qr via qrcode+EAN → `app/services/signals.py:100-113` pyzbar/libzbar path) and
  `tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` (tesseract path).
- ISS-1 stays owned by this pass per the packet — carried as exact delta, no further carry authorized.
- mypy not run (no code change in slice — stated, not silently omitted).

## G4 — remap, up, health, suites, UI, restart: UNANSWERED (ports gate passed, image gate not; 0 s spent)

- Ports gate HAD passed (8003+5173 free, 8000+8001 foreign expected) but `up` needs the unbuilt image.
- D20 remap deliberately NOT applied: `docker-compose.yml` stays `8000:8000`, `VITE_API_BASE` stays
  `http://localhost:8000`, `README.md` `:8000` lines untouched — applying them without the live proof
  (`up` + healthy JSON from `:8003`) would strand an unproved product change. Exact delta for follow-up.
- No `up`, no health curl against `:8003`, no exec suites, no UI bytes, no restart — none claimed.
- Zero catalog writes performed (no live service exists to write to; health+suites+shell only per bounds).

## Live-state ledger

- Runs now: NOTHING under this project — `docker info` showed 0 containers/0 images at probe; this slice
  started none (build cache only). Foreign listeners on 8000/8001/8002 untouched; 8003/5173 free at probe
  time (recheck owed before any future bind — a candidate is not a reservation).
- Proved per goal: G1 all legs; G2 route + apt layer; G3/G4 explicitly unproved (evidence above).
- Stops: ONE — G2 image STOP on Dockerfile:7 pip layer (deterministic, quoted). No privilege denial bound
  any step (`docker info`/build ran unprivileged under rootless; no `sudo`/socket/chmod attempted).
- README corrections: none (no live behavior observed to contradict the runbook; `:8000` lines carried as
  delta, not corrected).
- Remaining delta for follow-up: (1) fix the `hatchling.build` unavailability (lock and/or Dockerfile:7);
  (2) rebuild backend green; (3) run the two decoder nodes + full suite in-image; (4) apply D20 remap
  (compose publish + `VITE_API_BASE` + README `:8000`→`:8003` lines) with pre-bind listener recheck;
  (5) up, `:8003` health JSON, exec suites, served-UI bytes, `restart backend`→healthy. ISS-1 re-proof
  rides that slice (this pass owns it — no further carry).

## Files and receipt

- Changed: `.gitignore` (one builder-state entry) + `docs/worklogs/SG-023.log` + `docs/worklogs/SG-023_report.md`
  (this file). Every output path named here is committed. `.cache/buildx/` contents never committed
  (`PG-SC-10`). Worktree left clean (`CO-55`); running containers reported (none), none torn down.
- Receipt: `git notes --ref=refs/notes/storagegenie-coder-reports` carries
  `Dispatch-ID: SG-023 | Report: docs/worklogs/SG-023_report.md | Work-HEAD: <work commit hash>`
  on the work HEAD (exact hash in the note message, quoted in the dispatch result line),
  verified locally via `show` (quoted in the dispatch result line). No push to `storagegenie-evidence`,
  no legacy `{{RECEIPT_CMD}}` (dead per packet).

## Elapsed vs budget (per leg, with units)

- G1 probe: ~75 s actual / 120 s bound. G2 build: ~45 s actual / 1500 s bound (attempt-1 22.8 s +
  attempt-2 ~20 s). G3: 0 s / 600 s suite bound (gate not invocable — no image). G4: 0 s / 600 s suite
  bound (gate not invocable — no image). G5/G6: ~120 s / ordinary 120 s probes each. Slice total ≈360 s /
  2100 s overall; 1800 s early-close never reached. No command hung; every command ran under a stated
  timeout (120 s ordinary, 1500 s build).

UNCLEAR — FIRST READ: none.
UNCLEAR — DURING EXECUTION: none.
UNCLEAR — REMAINING: lock-vs-Dockerfile fix choice for the `hatchling.build` layer (owner/desk design call).
