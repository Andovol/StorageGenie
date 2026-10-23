# SG-231 — Standing close-deploy rider: rebuild + one recreate + verify (re-proof, no product delta expected)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend rebuild + one recreate.**
**Autonomy: L2.** Production authorization basis: standing owner directive 2026-09-28 ("Always do a live deploy before session close", `G-O4`; `AGENTS.md` Close-out row) executing after D-33 (all renders accepted, zero product delta since SG-222). Dispatch settings ride the trigger, never this packet. No product repair is implemented here.

Authoring date (metadata, never a gate): 2026-10-23.

## Why this exists

The last serve (SG-222) put the SG-221 tree live (image `d6c6a106`, container `f419758d` — EXPECTED pre-state, re-read on target). Since then only drivers, evidence, records and decision files have landed (SG-223–SG-230 + D-32/D-33 — EXPECTED docs-only, re-verify on target, do not trust this list). The standing close-out directive fires before session close regardless of product delta (`AGENTS.md:23` literal; the `SG-230` (b) finding is answered by running the rider, not by skipping it). This rider re-proves live==tree and reports it.

Verify the merged-vs-served product diff is EXPECTED empty — report the actual diff; any product change is served and named exactly (that is this rider's purpose), but a diff outside the served backend/frontend paths is STOP before deployment. Never assert HEAD equals any hash (`PG-IC-07`).

Expected recorded/published/host contract 0.50.0; previous host echo from `SG-226_report.md:4` (`/home/andrei/storagegenie-contract/CODER.md` line 3, 0.50.0). Echo version/source and report differences.

Waste cut: none owed — most recent audits name `slowest_waste = none`. Full suite waived per `PG-DP-02` with substitute below (read-only post-recreate verification; zero product bytes change).

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, schema head and authoritative table counts (enumerate tables on target). Check the product diff merged-vs-served: EXPECT empty — report the actual diff either way (`PG-EV-08`: capture the production observable before AND after).

Docker endpoint rule (SG-191 correction, carried — read twice, then obey): every Docker call runs with `DOCKER_HOST` set to YOUR unit's own runtime socket as YOUR process environment names it — never a prior unit's path, never the default. Never run `docker` without `DOCKER_HOST`, never read `/var/run/docker.sock`, never use it as a probe. ANY new privileged denial, on any endpoint, STOPS the whole slice (`PB-2`); disclosure never substitutes for stopping.

Then, through the lane socket only: build the backend image exactly once, then recreate the backend container exactly once (`PG-PR-04`: this is how the code becomes live). No host config changes. Second build/recreate issuance is STOP.

## G2 — Verify the serve, without claiming more

Observe a new container identity and start time (recreate proven by container ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent, not a reliability rate. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. If owner activity changes counts, report direct discriminating evidence; do not hide unexplained deltas.

With zero product change expected, the full suite stays waived per `PG-DP-02`; substitute is post-recreate read-only identity/health/schema/counts/pages/preflight verification. Walk the app shell routes with read-only GETs (`/`, `/catalog`, `/inbox`, plus one Scene-tab page proving the accepted renders serve). No browser interaction causing writes; no paid calls. Application provider spend prohibited.

## Constraints

Scope: `docs/worklogs/SG-231*` only. No product, configuration, schema, migration or test edits. No production INSERT/UPDATE/DELETE, manual resolving, imports or evidence-store mutation. Reads are git / lane-socket docker inspect / curl GETs / read-only SQLite enumeration; the only executed runtimes are the authorized build and recreate (`PG-IC-01`). Ordinary reads/verification bounded at 120 s per command, build at 600 s (uncalibrated inherited precedent); visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity, no alternate mount, no host config change. No secret or credential in any log or committed artifact (none is needed).

Full suite waived per `PG-DP-02` with substitute above. Runtime-vs-lane budget reported with seconds and source, never guessed (`PG-PR-06`: seconds, from the lane's own stamps).

## Acceptance and report

- A1: one rebuild + one recreate THROUGH THE LANE SOCKET, direct new running-instance proof, health green and explicit application/schema/count deltas (EXPECTED none); served bundle hash recorded, SAME-as-before only with the byte-identical-build reason stated.
- A2: actual base/hash and merged-vs-served diff checked — EXPECTED empty; any delta served and named exactly; work diff only SG-231 namespace.
- A3: command logs and final report `docs/worklogs/SG-231_report.md`; elapsed per leg and total vs observed lane bound; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-231.
- A4: notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-231 | Report: docs/worklogs/SG-231_report.md`, Work-HEAD recorded, branch/report push complete. Use the bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`; no silent deployment on any unrated/blocked result.
