# SG-197 — Close-out deploy rider: serve the two rated slices since SG-193 (one rebuild + one recreate + verify)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend rebuild + one recreate.**
**Autonomy: L3.** Production authorization basis: owner D-3 approval 2026-10-16 (chat "D3 - approved."; recorded `docs/decisions/2026-10-16-close-out-deploy-d3.md`) executing the standing close-out directive; audits `docs/worklogs/SG-194_audit.md` (98, no flag) + `docs/worklogs/SG-195_audit.md` (98, no flag). Dispatch settings ride the trigger, never this packet. No product repair is implemented here.

Authoring date (metadata, never a gate): 2026-10-16.

## Why this exists

SG-193 served SG-185..SG-190 (container `e8a6ed6985ef`, image `c3b85d5a…`, bundle `fd4a916e…` 324210 B — EXPECTED pre-state, re-read on target). Two rated G1 commits landed after and are EXPECTED unserved — verified by the Architect with `git log --oneline 3c89c69..HEAD` and `git diff --stat 3c89c69..HEAD -- backend frontend` on 2026-10-16 (8 files, +473/−18), re-verify on target, do not trust this list:
- EXPECTED `8a67ce3` SG-194 jobs list cursor — malformed cursor is a 422 (SG-188 shape mirrored) + focused tests (`backend/app/api/v1/jobs.py`, `backend/tests/test_sg194_jobs_cursor.py`)
- EXPECTED `f757ebd` SG-195 failed queries render a named role=alert on Catalog, Inbox, Analytics, Planning, Capture + focused error-branch tests (5 route files + `frontend/src/routes/query-error-alerts.test.tsx`)

Verify each EXPECTED hash is an ancestor of HEAD (reachability form); never assert HEAD equals any hash (`PG-IC-07`).

Previous reports' open items answered: SG-194 REMAINING closed in its audit except serving (this rider) + known-host env rows to STATE (no project action); SG-195 REMAINING out-of-set queries ride SG-196 nav premises (not this rider) + zoom/touch/dark/auth-live stand; ISS-4 runner `report_unreadable` misfire is a runner-observation defect with receipt present (receipt-based failure condition held, no re-trigger) — known shape, not a slice fault. SG-196 nav packet is next in queue; this rider changes no nav/state/router.

Expected recorded/published/host contract 0.50.0; previous host echo from SG-195_report.md FIRST READ (`/home/andrei/storagegenie-contract/`, complete 0.50.0 copy, RULES.md hash verified). Echo version/source and report differences. Known host rules_check exit-3 shape is independently explained there, not a license to repair host tags/auth.

Waste cut (`D434`/`D436`): none owed — most recent audit SG-195 names `slowest_waste = none`; SG-194's `5s precommit-focused` was already removed (SG-195 obeyed: no pre-commit gate). Full suite waived per `PG-DP-02` with substitute below (`D443`: candidate full suite already ran per slice; base FAIL halves committed in-slice).

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, schema head and authoritative table counts (enumerate tables on target). Check the product diff merged-vs-served: EXPECT exactly the two sets above — report the actual diff; any product change OUTSIDE that set is STOP before deployment (`PG-EV-08`: the production observable is the served bundle/API shape — capture it before AND after). "STOP and report" is not satisfiable by disclosure (`PG-EV-03`).

Docker endpoint rule (SG-191 correction, carried — read twice, then obey): every Docker call runs with `DOCKER_HOST` set to YOUR unit's own runtime socket as YOUR process environment names it — never a prior unit's path, never the default. The default-socket Docker listing is EXCLUDED up front as a known-denied optional operation: never run `docker` without `DOCKER_HOST`, never read `/var/run/docker.sock`, never use it as a probe. ANY new privileged denial, on any endpoint, STOPS the whole slice (`PB-2`, no optional-read exception); disclosure never substitutes for stopping.

Then, through the lane socket only: build the backend image exactly once, then recreate the backend container exactly once (`PG-PR-04`: this is how the code becomes live). No host config changes. Second build/recreate issuance is STOP.

## G2 — Verify the two repairs are served, without claiming more

Observe a new container identity and start time (recreate proven by container ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent, not a reliability rate. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. If owner activity changes counts, report direct discriminating evidence; do not hide unexplained deltas.

Run the two slices' focused test modules in-process against the merged tree (enumerate them from the two reports on target — EXPECT the SG-194 cursor tests + the SG-195 error-branch tests; report the actual set either way). Full suite waived per `PG-DP-02`; substitute is this targeted run plus post-recreate read-only identity/health/schema/counts/pages/preflight verification. No browser interaction causing writes; no paid calls.

Prove the serve live: served bundle hash DIFFERENT from `fd4a916e…` unless the build proves byte-identical for a stated reason (a retained hash over changed product bytes CONTRADICTS the purpose — STOP rather than claim an unserved serve). Walk `/review`, `/inbox`, `/catalog` through the new server (read-only GETs) plus CORS preflight. EXPECT SG-195's out-of-set queries + SG-190 REMAINING (nav context, zoom/touch/dark, density) unchanged and name them as such. Application provider spend prohibited.

## Constraints

Scope: `docs/worklogs/SG-197*` only. No product, configuration, schema, migration or test edits. No production INSERT/UPDATE/DELETE, manual resolving, imports or evidence-store mutation. Reads are git / lane-socket docker inspect / curl GETs / read-only SQLite enumeration; the only executed runtimes are the authorized build and recreate (`PG-IC-01`: no criterion requires what these exclusions forbid — cross-product worked: G1/G2 need lane-socket build+recreate (modify-versus-call exception stated here), in-process test execution (named runtime), read-only GETs/enumeration; nothing else). Ordinary reads/verification bounded at 120 s per command, build at 600 s (uncalibrated inherited precedent); visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity, no alternate mount, no host config change. No secret or credential in any log or committed artifact (none is needed).

Full suite waived per `PG-DP-02` with substitute above. Runtime-vs-lane budget reported with seconds and source, never guessed (`PG-PR-06`: seconds, from the lane's own stamps).

## Acceptance and report

- A1: one rebuild + one recreate THROUGH THE LANE SOCKET, direct new running-instance proof, health green and explicit application/schema/count deltas; served bundle hash recorded and DIFFERENT from `fd4a916e…` unless byte-identical-for-reason is proven.
- A2: actual base/hash and merged-vs-served diff checked — only the two expected sets differ; still-open items expressly identified as unchanged (SG-195 out-of-set → SG-196 premises; zoom/touch/dark/density stand); work diff only SG-197 namespace.
- A3: command logs and final report `docs/worklogs/SG-197_report.md`; elapsed per leg and total vs observed lane bound; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-197.
- A4: notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-197 | Report: docs/worklogs/SG-197_report.md`, Work-HEAD recorded, branch/report push complete. Use bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`; no silent deployment on any unrated/blocked result.
