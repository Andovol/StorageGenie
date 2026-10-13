# SG-192 — Serving rider, corrected: lane-socket Docker only, default-socket read excluded (dispatch on owner go)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend rebuild + one recreate.**
**Autonomy: L3.** Production authorization basis: owner waiver D13 (serve the SG-175/R1 merged repair) + audit `docs/worklogs/SG-191_audit.md` (89, no flag, STOP was correct, mis-probe corrected here). Dispatch itself awaits owner go (D15). No product repair is implemented here.

## Why this exists

SG-191 stopped correctly before any build: its capability read hit the KNOWN-denied default Docker socket, which the packet had failed to exclude (packet defect F-SG191-1, owned). The granted per-unit lane socket was present and untouched. This packet is SG-191 with that single mechanical correction: Docker is driven ONLY through the unit's own lane socket, and the default-socket read is excluded up front, so no denial can occur from it. Mission unchanged: build, recreate once, prove the waived R1 repair served. CHANGED bundles are expected (repair never served); only the waived R1 set may differ from the served base.

Expected recorded/published/host contract 0.47.0; previous host echo comes from SG-191_report.md, `/home/andrei/storagegenie-contract/VERSION`. Echo version/source and report differences. Known host rules_check exit 3 is independently explained there, not a license to repair host tags/auth.

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, schema head and authoritative table counts. Enumerate tables on target rather than assuming a prior list. Check the product diff merged-vs-served: EXPECT exactly the waived R1 files (`backend/app/api/v1/candidates.py`, `backend/app/services/candidates.py`, `frontend/src/components/CandidateCard.tsx`, `frontend/src/routes/ReviewPage.tsx`, plus their tests) — report the actual diff; any product change OUTSIDE that set is STOP before deployment.

Docker endpoint rule (the SG-191 correction — read twice, then obey): every Docker call in this slice runs with `DOCKER_HOST` set to YOUR unit's own runtime socket as YOUR process environment names it (`RUNTIME_DIRECTORY`/`RUNTIME_SOCKETS`, same mechanism SG-172/SG-174 exercised) — never a prior unit's path, never the default. The default-socket Docker listing is EXCLUDED up front as a known-denied optional operation (SG-179 lever): never run `docker` without `DOCKER_HOST`, never read `/var/run/docker.sock`, never use it as a probe. Container identity via the default endpoint stays UNVERIFIED by design. ANY new privileged denial, on any endpoint, STOPS the whole slice (`PB-2`, no optional-read exception); disclosure never substitutes for stopping.

Then, through the lane socket only: `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` exactly once, then `docker compose up -d --no-deps backend` exactly once (`PG-PR-04`: this is how the code becomes live). No host config changes. Second build/recreate issuance is STOP.

## G2 — Verify the repaired behavior is served, without claiming more

Observe a new container identity and start time (recreate proven by container ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent, not a reliability rate. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. If owner activity changes counts, report direct discriminating evidence; do not hide unexplained deltas.

Prove the repair live: candidate GET for a resolved-task candidate returns live `review_task_ids` (empty where none open — the repaired shape SG-184 proved disposable); blocked Accept enablement follows the live response. Walk `/review`, `/inbox`, `/catalog` through the new server (read-only GETs) plus CORS preflight. EXPECT the still-unrepaired stories unchanged (bare-Resolve, active-unclassified visibility, SG-176/177/178 scope) and name them as such — this deploy fixes R1 only. New bundle/image hashes are expected (product bytes changed); a retained image ID with identical bundles would CONTRADICT the purpose — report and STOP rather than claim a serve that did not happen. No browser interactions causing writes; no paid calls.

## Constraints

Scope: `docs/worklogs/SG-192*` only. No product, configuration, schema, migration or test edits. No production INSERT/UPDATE/DELETE, manual resolving, imports or evidence-store mutation. Ordinary reads/verification bounded at 120 s per command, build at 600 s (uncalibrated inherited precedent); visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity, no alternate mount, no host config change.

Full suite waived per `PG-DP-02`; substitute is post-recreate read-only identity/health/schema/counts/pages/preflight verification plus SG-184's executed re-proof (failpre 4F/6P, passpost 10P, UI 18P, probe PROBE_OK). No new code has to pass a new behavior test. Application provider spend prohibited; actual Coder-platform spend unavailable unless directly exposed. Runtime-vs-lane budget reported with seconds and source, never guessed (`PG-PR-06`: seconds, from the lane's own stamps).

## Acceptance and report

- A1: one rebuild + one recreate THROUGH THE LANE SOCKET, direct new running-instance proof, health green and explicit application/schema/count deltas; served bundle hash recorded and DIFFERENT from `1b4680a0…` unless the build proves byte-identical for a stated reason.
- A2: actual base/hash and product diff checked — only the waived R1 set differs from the served base; work diff only SG-192 namespace; still-broken stories expressly identified as unchanged.
- A3: command logs and final report `docs/worklogs/SG-192_report.md`; elapsed per leg and total vs observed lane bound; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-192.
- A4: notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-192 | Report: docs/worklogs/SG-192_report.md`, Work-HEAD recorded, branch/report push complete. Use bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-02/03; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`; no silent deployment on any unrated/blocked result.
