# SG-232 — Standing close-deploy rider, retry (root-cause fix for F-SG231-1; re-proof, no product delta expected)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend rebuild + one recreate.**
**Autonomy: L2 (the one retry).** Production authorization basis: standing owner directive 2026-09-28 (`G-O4`; `AGENTS.md` Close-out row) + SG-231 audit (retry owned by Architect; fault was the Coder's first call, not the packet). Dispatch settings ride the trigger, never this packet. No product repair is implemented here.

Authoring date (metadata, never a gate): 2026-10-23.

## Why this exists

SG-231 stopped before the build: its first docker call ran without `DOCKER_HOST` (F-SG231-1, self-inflicted, `PB-2` STOP correctly honored — audit `SG-231_audit.md`, rated 90). Zero rebuilds/recreates, zero production effect; pre-state re-confirmed live==tree read-only (served bundle == SG-222/SG-228, health green, DB unchanged). The standing close-deploy remains owed. This is the L2 retry with the root-cause fix below — not a blind re-run.

Verify the merged-vs-served product diff is EXPECTED empty at runtime (`backend/app` + `frontend/src` — SG-231 measured 0 lines) — report the actual diff; any runtime product change is served and named exactly, a diff outside the served paths is STOP. Named premises carried from SG-231 (do not re-litigate, verify on target): (a) non-runtime delta = `STATE.md` + four non-imported `backend/scripts` drivers (inside the `backend/` build context, outside the runtime surface); (b) Catalog page mounted at `/` (`/catalog` serves the SPA shell 200 via fallback). Never assert HEAD equals any hash (`PG-IC-07`).

Expected recorded/published/host contract 0.50.0; previous host echo from `SG-231_report.md:7` (host copy, 0.50.0). Echo version/source and report differences.

Waste cut: SG-231 audit names `slowest_waste = none`. Full suite waived per `PG-DP-02` with substitute below (read-only post-recreate verification; zero product bytes change).

## G0 — Socket first (root-cause fix for F-SG231-1; runs before anything Docker)

Print the lane socket from YOUR unit's own process environment, `export DOCKER_HOST` to it, then prove the server line with `docker version` (the server section must answer — a client-only block is NOT proof). No `docker` invocation of any kind — not `version`, not `compose`, not a probe — before the export. A second default-endpoint call is the SG-231 repeat and STOPS the slice again (`PB-2`).

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes (EXPECTED index `345bbe8c…`, JS `43c05c51…`, CSS `c3b58cda…` per SG-231 — re-read, do not trust), schema head and authoritative table counts (`PG-EV-08`: capture the production observable before AND after).

Then, through the lane socket only: build the backend image exactly once, then recreate the backend container exactly once (`PG-PR-04`). No host config changes. Second build/recreate issuance is STOP.

## G2 — Verify the serve, without claiming more

Observe a new container identity and start time (ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. Owner-activity deltas get direct discriminating evidence, never hidden.

Suite stays waived per `PG-DP-02`; substitute is post-recreate read-only identity/health/schema/counts/pages/preflight verification. Walk the shell routes read-only (`/`, `/catalog`, `/inbox`, one Scene-tab page). No writes; no paid calls. Application provider spend prohibited.

## Constraints

Scope: `docs/worklogs/SG-232*` only. No product/config/schema/migration/test edits. No production INSERT/UPDATE/DELETE, imports or evidence-store mutation. Reads are git / lane-socket docker / curl GETs / read-only SQLite; only executed runtimes are the G0-verified build and recreate (`PG-IC-01`). Reads/verification ≤120 s per command, build ≤600 s (inherited precedent); visible timeout finding; idle kill 900 s never approached. No prompt or polling loop. No sudo/alternate identity/mount/host config. No secret in any artifact. Runtime-vs-lane budget in seconds from the lane's own stamps (`PG-PR-06`).

## Acceptance and report

- A1: G0 proven (export + server line) BEFORE any other docker call; one rebuild + one recreate THROUGH THE LANE SOCKET; new running-instance proof; health green; explicit deltas (EXPECTED none); bundle hashes recorded (SAME-as-before only with byte-identical-build reason).
- A2: base/hash echoed separately; merged-vs-served diff checked (EXPECTED runtime-empty); named premises (a)(b) verified; work diff only SG-232 namespace.
- A3: command logs + report `docs/worklogs/SG-232_report.md`; elapsed per leg vs lane bound; constraints answered; FIRST/DURING/REMAINING dispositioned. First token SG-232.
- A4: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-232 | Report: docs/worklogs/SG-232_report.md`, Work-HEAD recorded, push + mapped read-back. Bound lane receipt only.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`.
