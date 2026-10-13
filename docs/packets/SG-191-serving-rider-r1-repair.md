# SG-191 — Serving rider: build, recreate and verify the waived R1 repair live (DRAFT, dispatch on owner go)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend rebuild + one recreate.**
**Autonomy: L3.** Sole production authorization basis: owner waiver D13 (serve the SG-175/R1 merged repair) + audit `docs/worklogs/SG-184_audit.md` (96, no flag, waiver recommended). Dispatch itself awaits owner go (D14). No product repair is implemented here — the repair is already merged and re-proved; this slice makes it live.

## Why this exists

D13 waived the SG-175 `FLAG:SAFETY` hold for serving. Served bundle is still the pre-repair `1b4680a0…` (SG-174 lineage, verified again in `SG-184_served_baseline.log`); merged tree carries the live-ID repair (`0b42e7d`, re-proved by SG-184). This rider builds and recreates exactly once and proves the new instance serves the repaired behavior. Unlike SG-174 (which expected identical bundles), CHANGED bundles are expected here — and only the waived change.

Expected recorded/published/host contract 0.47.0; previous host echo comes from SG-184_report.md, `/home/andrei/storagegenie-contract/VERSION`. Echo version/source and report differences. Known host rules_check exit 3 is independently explained in that report, not a license to repair host tags/auth.

## G1 — Pre-state, one rebuild, one recreate

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, schema head and authoritative table counts. Enumerate tables on target rather than assuming a prior list. Check the product diff merged-vs-served: EXPECT exactly the waived R1 files (`backend/app/api/v1/candidates.py`, `backend/app/services/candidates.py`, `frontend/src/components/CandidateCard.tsx`, `frontend/src/routes/ReviewPage.tsx`, plus their tests) — report the actual diff; any product change OUTSIDE that set is STOP before deployment.

Reuse the granted lane: `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` exactly once, then `docker compose up -d --no-deps backend` exactly once (`PG-PR-04`: this is how the code becomes live). Read grant/capability without attempting privileged writes as a probe. `PG-PR-03`: privilege denial is STOP, never sudo/another identity/another mount. No host config changes. Second build/recreate issuance is STOP.

## G2 — Verify the repaired behavior is served, without claiming more

Observe a new container identity and start time (recreate proven by container ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent, not a reliability rate. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. If owner activity changes counts, report direct discriminating evidence; do not hide unexplained deltas.

Prove the repair live: candidate GET for a resolved-task candidate returns live `review_task_ids` (empty where none open — the repaired shape SG-184 proved disposable); blocked Accept enablement follows the live response. Walk `/review`, `/inbox`, `/catalog` through the new server (read-only GETs) plus CORS preflight. EXPECT the still-unrepaired stories unchanged (bare-Resolve, active-unclassified visibility, SG-176/177/178 scope) and name them as such — this deploy fixes R1 only. New bundle/image hashes are expected (product bytes changed); a retained image ID with identical bundles would CONTRADICT the purpose — report and STOP rather than claim a serve that did not happen. No browser interactions causing writes; no paid calls.

## Constraints

Scope: `docs/worklogs/SG-191*` only. No product, configuration, schema, migration or test edits. No production INSERT/UPDATE/DELETE, manual resolving, imports or evidence-store mutation. Ordinary reads/verification bounded at 120 s per command, build at 600 s (uncalibrated inherited precedent); visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop.

Full suite waived per `PG-DP-02`; substitute is post-recreate read-only identity/health/schema/counts/pages/preflight verification plus SG-184's executed re-proof (failpre 4F/6P, passpost 10P, UI 18P, probe PROBE_OK). No new code has to pass a new behavior test. Application provider spend prohibited; actual Coder-platform spend unavailable unless directly exposed. Runtime-vs-lane budget reported with seconds and source, never guessed (`PG-PR-06`: seconds, from the lane's own start/stop stamps).

## Acceptance and report

- A1: one rebuild + one recreate, direct new running-instance proof, health green and explicit application/schema/count deltas; served bundle hash recorded and DIFFERENT from `1b4680a0…` unless the build proves byte-identical for a stated reason.
- A2: actual base/hash and product diff checked — only the waived R1 set differs from the served base; work diff only SG-191 namespace; still-broken stories expressly identified as unchanged.
- A3: command logs and final report `docs/worklogs/SG-191_report.md`; elapsed per leg and total vs observed lane bound; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-191.
- A4: notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-191 | Report: docs/worklogs/SG-191_report.md`, Work-HEAD recorded, branch/report push complete. Use bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-02/03; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`; no silent deployment on any unrated/blocked result.
