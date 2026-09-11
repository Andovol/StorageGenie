# SG-023 — Manual compose pass: image, ISS-1 re-proof, up, UI, restart (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** D12 manual compose pass (L2 single slice) under D30 — same scope as SG-021, Coder retargeted codex→opencode per D29, effort `medium` (default for the new Coder, uncalibrated per `G-A9`; scope unchanged). This slice's approval IS D30. SG-021 history (not re-litigated): three attempts, zero product verdicts — attempt-1/2 BLOCKED by environment (docker denial, then rootless + foreign-port STOPs, rated 96/97), attempt-3 killed twice pre-slice by the codex quota wall. Desk `Andovol/Launcher#18` ANSWERED+CLOSED: `BUILDX_CONFIG` project-local route + port `8003`. Approvals carried: D12 (manual pass first) + D20 (`8003`) + BUILDX_CONFIG route. This attempt is run 1 of a NEW Coder entry point — first-run provisional per `PG-DP-04`, and a green here doubles as the owed opencode run-2 (ISS-7). Prior art: SG-021's packet (G-structure reused), SG-018's probe shape, SG-013's denial handling, SG-020's exit proof, SG-022's opencode lane proof (97 — trigger→work→report→receipt all valid).
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; decoder legs are proved HERE (this pass owns ISS-1 — no further carry).

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (Effort is proven readable from process arguments — do the same. Owner standing requirement: the report quotes model provenance after EVERY slice — opencode serves multiple models.)

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: live mounts, zero catalog writes. Restart: own backend container only (allowlisted `restart: unless-stopped`).** This slice touches the live host, authorised by D12+D30 with these explicit bounds: `docker compose build/run/up/exec/restart` against THIS project's compose file only; no `docker volume/server` inspection beyond the probe (a past denial — report, don't route around); no catalog writes (health checks + test exec use temp DBs; the running service is exercised, never written to); D20-authorized port remap ONLY (backend host port 8000→8003 with VITE_API_BASE + runbook carried — desk #18 CLOSED answer ex privileged `ss`: 8000 docker-proxy/2449 · 8001 shoperos-api/761216 · 8002 shoperos-mcp/3780707 all foreign, 8003+5173 listener-free candidates, owner selected 8003 per D20; recheck listeners immediately before binding — a candidate is not a reservation); `BUILDX_CONFIG` project-local placement ONLY (one new gitignored dir e.g. `.cache/buildx` + one `.gitignore` entry if not already present — verify first, SG-021's crash may have left either state; builder-state contents are never committed per `PG-SC-10`); no other port reconfiguration; no `.env` content changes (presence check only — secrets stay secret, `CO-44`). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): at 1800 s elapsed STOP starting new work, close out with what proved, publish the receipt — a partial slice WITH a receipt is a success. Report elapsed per leg. Coder-side `python`/`pytest`/`docker` may be absent on the host PATH — resolve actual binaries/verbs first and name them, never assume.

## Why this exists

Everything Phase 1 proved ran in-process (TestClient + temp DBs). Unproved on live infrastructure: the image builds with the new apt packages (SG-013's Dockerfile lines never built — `docker build` was unrunnable in-sandbox); the two decoder legs (ISS-1) go green where libzbar/tesseract exist; `compose up` survives the shared host (ports `8000`+`8001` live foreign per desk #18 CLOSED answer — NOT reclaimable, D20 remaps backend to host port `8003`, rechecked before binding); the UI serves; restart recovers to healthy. Host tree was observed clean 2026-09-11 12:41 UTC (SG-022 LEG4) — if dirt is present at start, quote it and STOP before any other goal (the wedge question reopens; do not work around it). Handed tree facts (verify — `PG-IC-09`): `docker-compose.yml` publishes `8000:8000` + `5173:5173` (this slice remaps backend to `8003:8000` per D20 — verify whether a prior attempt already applied this); bind-mounts `./backend` + `./data/db`, names volume `storage_data`, requires `.env` (`env_file`), runs uvicorn `--reload`, healthchecks `GET /v1/health`, frontend `npm run dev` with `VITE_API_BASE` (verify current value — carry to `http://localhost:8003` per D20 if not already carried), both `restart: unless-stopped`; `.gitignore` state for `.cache/` UNVERIFIED after the SG-021 crash (verify before adding); backend health proves DB+storage (`health.py`); runbook `README.md` names `:8000` across ~10 lines (`:40,104-140` — verify current state, carry each to `:8003` if not already carried).

## G1 — capability + collision probe (report only; every leg has a stop)

- `docker info` (or the compose equivalent that works here): denial (e.g. the known `docker volume ls` nobody:nogroup shape) → STOP THE WHOLE SLICE with the exact denial quoted (the fallback is desk-side provisioning, not a workaround — name it, do not attempt it). Runtime per D15 is desk-provisioned rootless (shared-socket grant declined): resolve actual binaries/verbs first and name them — rootless costs this tree nothing (no <1024 binds, no host cgroup/storage-driver dependence, relayed to desk).
- TCP occupancy of `8000`, `8001`, `8003` and `5173` on the host (read-only probe, e.g. `/dev/tcp` or the toolchain's equivalent — your call): record WHO answers each port. `8000` + `8001` answering foreign is EXPECTED — record, do not stop, do not touch either. `8003` or `5173` answering foreign is a STOP with the occupancy evidence quoted. If no occupancy signal is obtainable at all (probe tool absent and no equivalent), STOP with that evidence — never bind blind (`PG-SC-07`: no judgement without data).
- `docker compose config` validity + `.env` presence (never content) + `frontend/Dockerfile` existence (unverified premise — confirm or report absent).
- Stopping is a SUCCESS where stated; stopping because a probe "feels risky" without a denial or collision is NOT grounds to stop.

## G2 — builder-state placement + image build (only if G1 grants docker)

- Desk #18 route FIRST (no host grant exists for `/home/andrei/.docker/buildx` — do not request one, do not touch that path): create the project-owned builder-state dir (e.g. `.cache/buildx` + the one `.gitignore` entry from the ceiling — VERIFY FIRST whether SG-021's crash left either behind; adopt existing state, do not duplicate), export `BUILDX_CONFIG` pointing at it for every build/compose invocation, keep the `rootless` context (do not relocate `DOCKER_CONFIG`), explicitly select/retain the intended rootless builder and verify with `docker buildx ls` (quote the selection). If the activity-path read-only failure persists under this route, STOP with the evidence quoted — the desk route is exhausted and the follow-up reopens desk-side with the receipt; a second in-slice workaround is not attempted (`PG-IC-03`: the STOP wins).
- `docker compose build backend` (bound 1500 s): proves the SG-013 apt lines (`tesseract-ocr`, `libzbar0`) install on bookworm-slim. Build failure → STOP with the failing layer quoted (do not redesign the Dockerfile beyond the failing line's evidence).

## G3 — ISS-1 re-proof in the image (only if G2 built; no ports, no live writes)

- `docker compose run --rm --no-deps backend venv/bin/python -m pytest -q tests/test_signals.py` (or the in-image equivalent path — resolve, don't assume): the two named decoder nodes must go GREEN. Quote both. Any other red is a finding with a destination, never silent. Then the full backend suite in the same shape: green except NOTHING (in-image there is no sandbox excuse — any non-decoder red is a defect finding).

## G4 — remap, up, health, suites, UI, restart (only if G1 shows 8003 + 5173 free of foreign occupants; 8000 + 8001 foreign is expected)

- D20 remap FIRST (the only authorized product-file change this slice besides the builder-state dir): backend publish `8000:8000`→`8003:8000` in `docker-compose.yml` (verify whether already applied — adopt, don't duplicate), `VITE_API_BASE` `http://localhost:8000`→`http://localhost:8003` (compose env + the `README.md` runbook lines that name `:8000`), then `docker compose config` to prove validity. Re-run the listener check immediately before `up` — the desk's free-port evidence is a candidate, not a reservation. Any other product/migration/port change need is a STOP with evidence, never a quiet edit.
- `docker compose up -d --build` (or up since G2 built — your call): `GET http://localhost:8003/v1/health` via curl returns the runbook's expected JSON (if curl to `:8003` hits anything but our backend, that IS the collision signal — STOP with the occupancy evidence quoted; the world where the feature works and this criterion fails is *someone bound 8003 between probe and bind* — that STOP is the correct outcome, not a slice failure); backend suite via `compose exec`; frontend `npm run build`-clean OR dev-server HTML shell containing the app root via curl (your call by what the tree supports — prove served bytes, never a log line claiming serve); `docker compose restart backend` → healthy again within the healthcheck retries (quote the recovery).
- No catalog writes in any leg (health + suites + shell only); any write need is a STOP.

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-023.log` and `{{WORKLOG_DIR}}/SG-023_report.md`, first token `SG-023`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget PER LEG with units. State model/effort provenance from process arguments — the MODEL line is an owner standing requirement (D30): quote it after every slice, `unknown` only if truly undeterminable. The report carries the live-state ledger: what runs now (containers, ports, health), what was proved per goal, every stop with its evidence, and the exact remaining delta (if any) for a follow-up.

## G6 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-023 | Report: docs/worklogs/SG-023_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: prove-and-report slice with TWO authorized product changes — the D20 remap (`docker-compose.yml` backend publish, `VITE_API_BASE`, `README.md` runbook `:8000` lines — each VERIFIED before applying, adopted if a prior attempt already applied it) and the builder-state placement (one gitignored dir + one `.gitignore` entry — same verify-first). Permitted changes ONLY: those two, `README.md` runbook corrections where live behavior contradicts it (quote each), `docs/worklogs` files, the G6 note mechanism. Builder-state contents are never committed and never force-added (`PG-SC-10`). Any other product/migration/port/compose-file change need is a STOP with evidence, never a quiet edit ("STOP and report" is not satisfiable by disclosure). Where a STOP and a retry itch meet, the STOP wins (`PG-IC-03`) — one L2 retry covers transients, never a routed STOP. The 1800 s early-close rule above binds all goals.
- Cross-product (`PG-IC-01`): G2 needs only the Dockerfile as built; G3 needs only the built image; G4 needs only free ports + `.env` presence. No goal requires what the ceiling forbids. Recorded here once, not per criterion.
- Secrets: never read out, print, or commit `.env` contents — presence check only, redact per `CO-44`.
- Privileged-denial: a denied `sudo`/`docker` operation is reported as unanswered with its exact text per the block above, not routed around. No `sudo docker`, no socket chmod, no group changes — the confinement is the finding if it binds.
- Stash: worktree ends clean per `CO-55`. Running containers are REPORTED (names, ports, health), not left ambiguous — but do not tear down what `up` started unless it is unhealthy (state either way).
- Test scope: every gate names what it checked with counts and elapsed; a gate emitting no output is a FAIL. mypy not run (no code change expected — say so, don't silently omit).
- Budget: 120s ordinary probes, 1500s build leg, 600s suite legs, 1800 s early-close, 2100s overall — actual-versus-budget per leg with units.
- Simplicity: verify before asserting; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- Starting tree state quoted (clean expected per SG-022 LEG4 — any dirt is a STOP before all other goals, quoted).
- G1 evidence quoted per leg (docker verdict, per-port occupant for 8000/8001/8003/5173, config validity, `.env` presence, frontend Dockerfile verdict), each with its stop obeyed or explicitly passed; unobtainable occupancy signal is a STOP, never a bind.
- G2 builder selection quoted (`buildx ls`) + activity path writable under the route, or STOP with the persisting denial.
- G2 build green with apt-layer evidence quoted, or STOP with the failing layer.
- G3 decoder nodes green IN THE IMAGE (node IDs + output quoted); full in-image suite with any non-decoder red named as defect finding.
- G4 (remap + up, only if 8003/5173 free): remap diff quoted + `config` valid, pre-bind recheck quoted, healthy JSON from `:8003` quoted, exec suites quoted, served-UI bytes quoted, restart→healthy recovery quoted; (if 8003/5173 occupied): STOP with occupancy evidence, no rebind attempted. `:8000` + `:8001` foreign is expected, never touched.
- README corrections, if any, each quote the contradicted line and the live evidence.
- Live-state ledger complete (containers/ports/health/stops/delta).
- MODEL provenance quoted (owner standing requirement) + effort provenance.
- Worklog + report committed; notes ref carries the `Dispatch-ID: SG-023` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — from process arguments (proven readable), never from a system-prompt identity line. The model line is required by the owner after every slice.

## Budget

120s probes, 1500s build, 600s suite legs, 1800 s early-close, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
