# SG-193 — Close-out deploy rider: serve the six rated slices since SG-192 (one rebuild + one recreate + verify)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend rebuild + one recreate.**
**Autonomy: L3.** Production authorization basis: owner D-1 approval 2026-10-14 (chat "D1 - approved"; recorded `docs/decisions/2026-10-14-close-out-deploy.md`) executing the standing close-out directive; audit `docs/worklogs/SG-192_audit.md` (97, no flag). Dispatch settings ride the trigger, never this packet. No product repair is implemented here.

Authoring date (metadata, never a gate): 2026-10-14.

## Why this exists

SG-192 served R1 (container `8f5b9707d92e`, image `865a0e05…`, bundle `ac0039d6…` 322169 B). Six rated G1 commits landed after and are EXPECTED unserved — verified by the Architect with `git log 358023b..HEAD -- backend frontend` on 2026-10-14, re-verify on target, do not trust this list:
- EXPECTED `341bd69` SG-185 household-scoped asset key replay + two-household tests
- EXPECTED `0dd037d` SG-186 serve-time sha256 + household-scoped evidence replay
- EXPECTED `07d4ea8` SG-187 Inbox Start + rejection hygiene + import-surface truth
- EXPECTED `e911cdc` SG-188 bare-resolve 422 + malformed-cursor 422 + ARCHIVED default
- EXPECTED `02f1214` SG-189 `_guard` both containment directions (operator drill script, rides the image)
- EXPECTED `dc36291` SG-190 responsive shell (13 frontend files)

Previous report's open items answered: SG-192 REMAINING-1 (dual-annotation note) is Architect-side, no Coder action; REMAINING-2 (audit/rate) is done; REMAINING-3 (SG-176/177/178 scope + STILL-UNREPAIRED stories) is EXPECTED unchanged and named in A2; REMAINING-4 (R1 SERVED) is now the base, not the mission. SG-192's DURING-EXECUTION items were dispositioned in-report — no action.

Expected recorded/published/host contract 0.47.0; previous host echo from SG-192_report.md (`/home/andrei/storagegenie-contract/VERSION`, verbatim line quoted there). Echo version/source and report differences. Known host rules_check exit 3 is independently explained there, not a license to repair host tags/auth.

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, schema head and authoritative table counts (enumerate tables on target). Check the product diff merged-vs-served: EXPECT exactly the six sets above — report the actual diff; any product change OUTSIDE that set is STOP before deployment (`PG-EV-08`: the production observable is the served bundle/API shape — capture it before AND after).

Docker endpoint rule (SG-191 correction, carried — read twice, then obey): every Docker call runs with `DOCKER_HOST` set to YOUR unit's own runtime socket as YOUR process environment names it — never a prior unit's path, never the default. The default-socket Docker listing is EXCLUDED up front as a known-denied optional operation: never run `docker` without `DOCKER_HOST`, never read `/var/run/docker.sock`, never use it as a probe. ANY new privileged denial, on any endpoint, STOPS the whole slice (`PB-2`, no optional-read exception); disclosure never substitutes for stopping.

Then, through the lane socket only: build the backend image exactly once, then recreate the backend container exactly once (`PG-PR-04`: this is how the code becomes live). No host config changes. Second build/recreate issuance is STOP.

## G2 — Verify the six repairs are served, without claiming more

Observe a new container identity and start time (recreate proven by container ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent, not a reliability rate. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. If owner activity changes counts, report direct discriminating evidence; do not hide unexplained deltas.

Run the six slices' focused test modules in-process against the merged tree (enumerate them from the six reports on target — EXPECT the SG-185 two-household replay tests, SG-186 integrity tests, SG-187 journey/hygiene tests, SG-188 resolve/cursor/archived tests, SG-189 guard geometries, SG-190 driver checks where runnable in-process; report the actual set either way). Full suite waived per `PG-DP-02`; substitute is this targeted run plus post-recreate read-only identity/health/schema/counts/pages/preflight verification. No browser interaction causing writes; no paid calls.

Prove the serve live: served bundle hash DIFFERENT from `ac0039d6…` unless the build proves byte-identical for a stated reason (a retained hash over changed product bytes CONTRADICTS the purpose — STOP rather than claim an unserved serve). Walk `/review`, `/inbox`, `/catalog` through the new server (read-only GETs) plus CORS preflight. EXPECT the still-unrepaired stories unchanged (SG-176/177/178 scope; SG-192 REMAINING-3 STILL-UNREPAIRED list — enumerate from that report on target) and name them as such. Application provider spend prohibited.

## Constraints

Scope: `docs/worklogs/SG-193*` only. No product, configuration, schema, migration or test edits. No production INSERT/UPDATE/DELETE, manual resolving, imports or evidence-store mutation. Reads are git / lane-socket docker inspect / curl GETs / read-only SQLite enumeration; the only executed runtimes are the authorized build and recreate (`PG-IC-01`: no criterion requires what these exclusions forbid). Ordinary reads/verification bounded at 120 s per command, build at 600 s (uncalibrated inherited precedent); visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity, no alternate mount, no host config change. No secret or credential in any log or committed artifact (none is needed).

Full suite waived per `PG-DP-02` with substitute above. Runtime-vs-lane budget reported with seconds and source, never guessed (`PG-PR-06`: seconds, from the lane's own stamps).

## Acceptance and report

- A1: one rebuild + one recreate THROUGH THE LANE SOCKET, direct new running-instance proof, health green and explicit application/schema/count deltas; served bundle hash recorded and DIFFERENT from `ac0039d6…` unless byte-identical-for-reason is proven.
- A2: actual base/hash and merged-vs-served diff checked — only the six expected sets differ; still-broken stories expressly identified as unchanged; work diff only SG-193 namespace.
- A3: command logs and final report `docs/worklogs/SG-193_report.md`; elapsed per leg and total vs observed lane bound; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-193.
- A4: notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-193 | Report: docs/worklogs/SG-193_report.md`, Work-HEAD recorded, branch/report push complete. Use bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`; no silent deployment on any unrated/blocked result.
