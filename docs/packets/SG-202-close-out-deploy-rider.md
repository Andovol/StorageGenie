# SG-202 — Close-out deploy rider: serve the SG-196 + SG-198 frontend delta (one rebuild + one recreate + verify)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend rebuild + one recreate.**
**Autonomy: L4.** Production authorization basis: owner D-5 approval 2026-10-17 (chat "D5-D7 - as recommended."; recorded `docs/decisions/2026-10-17-d5-d6-d7-answers-l4-window.md`) executing the standing 2026-09-28 close-out directive; audits `docs/worklogs/SG-196_audit.md` (98, no flag) + `docs/worklogs/SG-198_audit.md` (98, no flag). Dispatch settings ride the trigger, never this packet. No product repair is implemented here.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

SG-197 served SG-194 + SG-195 (container `a77e3f2f…`, image `e3b7c0aa…`, bundle `8ba02c64…` — EXPECTED pre-state, re-read on target). Two rated G1 commits landed after and are EXPECTED unserved — verified by the Architect with `git log --oneline f757ebd..HEAD` and `git diff --stat f757ebd..HEAD -- backend frontend` on 2026-10-17 (24 files, +622/−170, frontend only; 21 + 4 file-touches less `import-modal.test.tsx` touched by both), re-verify on target, do not trust this list:
- EXPECTED `faea4d6` SG-196 — shared household context (one fetch), nav selector + household alert, Inbox open-task badge, Catalog facets/saved-search alerts (`frontend/src/hooks/HouseholdContext.tsx`, `App.tsx`, `components/shell/AppHeader.tsx`, `routes/{Inbox,Catalog,Analytics,Planning,Capture,Chat,Expiry}Page.tsx`, `hooks/useAssets.ts`, plus `App.household-nav.test.tsx`)
- EXPECTED `144190c` SG-198 — AppHeader onto the household context, ReviewPage onto shared `useReviewTasks`; declared behavior-preserving ("no observable behavior change", `SG-198_report.md:7`)

Verify each EXPECTED hash is an ancestor of HEAD (reachability form); never assert HEAD equals any hash (`PG-IC-07`).

Previous reports' open items answered: SG-199 REMAINING (density numbers, auth-live, live-container rendering, zoom/touch/dark) — unchanged and carried, now decided as D-6/D-7 whose proposal slice is next, NOT this rider; ISS-4 runner `report_unreadable` misfire (4th instance at SG-199) is a runner-observation defect with receipt present (receipt-based failure condition held, no re-trigger), filed Launcher #84 — known shape, not a slice fault. SG-196's report-vs-audit delta line (`+556` vs audit `+565`, 9 lines) is a records discrepancy, docs-only, out of this rider's scope. This rider changes no nav/state/router logic beyond what the two commits already contain.

Expected recorded/published/host contract 0.50.0; previous host echo from SG-195_report.md FIRST READ (`/home/andrei/storagegenie-contract/`, complete 0.50.0 copy, RULES.md hash verified). Echo version/source and report differences. Known host rules_check exit-3 shape is independently explained there, not a license to repair host tags/auth.

Waste cut (`D434`/`D436`): none owed — most recent audit SG-199 names `slowest_waste = none`; SG-195 already removed the `5s precommit-focused` gate (obeyed since). Full suite waived per `PG-DP-02` with substitute below (`D443`: base FAIL halves committed in-slice).

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, schema head and authoritative table counts (enumerate tables on target). Check the product diff merged-vs-served: EXPECT exactly the two sets above — report the actual diff; any product change OUTSIDE that set is STOP before deployment (`PG-EV-08`: the production observable is the served bundle/API shape — capture it before AND after). "STOP and report" is not satisfiable by disclosure (`PG-EV-03`).

Docker endpoint rule (SG-191 correction, carried — read twice, then obey): every Docker call runs with `DOCKER_HOST` set to YOUR unit's own runtime socket as YOUR process environment names it — never a prior unit's path, never the default. The default-socket Docker listing is EXCLUDED up front as a known-denied optional operation: never run `docker` without `DOCKER_HOST`, never read `/var/run/docker.sock`, never use it as a probe. ANY new privileged denial, on any endpoint, STOPS the whole slice (`PB-2`, no optional-read exception); disclosure never substitutes for stopping.

Then, through the lane socket only: build the backend image exactly once, then recreate the backend container exactly once (`PG-PR-04`: this is how the code becomes live). No host config changes. Second build/recreate issuance is STOP.

## G2 — Verify the two served slices, without claiming more

Observe a new container identity and start time (recreate proven by container ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent, not a reliability rate. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. If owner activity changes counts, report direct discriminating evidence; do not hide unexplained deltas.

Run the two slices' focused test modules in-process against the merged tree (enumerate them from the two reports on target — EXPECT `App.household-nav.test.tsx` plus the SG-198 `ReviewPage.test.tsx` additions; report the actual set either way). Full suite waived per `PG-DP-02`; substitute is this targeted run plus post-recreate read-only identity/health/schema/counts/pages/preflight verification. No browser interaction causing writes; no paid calls.

Prove the serve live: served bundle hash DIFFERENT from `8ba02c64…` unless the build proves byte-identical for a stated reason (a retained hash over changed product bytes CONTRADICTS the purpose — STOP rather than claim an unserved serve). Walk the routes SG-196 touched through the new server (read-only GETs): `/inbox`, `/catalog`, `/analytics`, `/planning`, `/capture`, `/review`, plus CORS preflight. EXPECT the app shell with the household nav selector/alert, the Inbox open-task badge and the Catalog facets/saved-search alerts to be served from the new bundle. EXPECT SG-199 REMAINING (density numbers, auth-live, live-container rendering, zoom/touch/dark) unchanged and name them as such. Application provider spend prohibited.

## Constraints

Scope: `docs/worklogs/SG-202*` only. No product, configuration, schema, migration or test edits. No production INSERT/UPDATE/DELETE, manual resolving, imports or evidence-store mutation. Reads are git / lane-socket docker inspect / curl GETs / read-only SQLite enumeration; the only executed runtimes are the authorized build and recreate (`PG-IC-01`: no criterion requires what these exclusions forbid — cross-product worked: G1/G2 need lane-socket build+recreate (modify-versus-call exception stated here), in-process test execution (named runtime), read-only GETs/enumeration; nothing else). Ordinary reads/verification bounded at 120 s per command, build at 600 s (uncalibrated inherited precedent); visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity, no alternate mount, no host config change. No secret or credential in any log or committed artifact (none is needed).

Full suite waived per `PG-DP-02` with substitute above. Runtime-vs-lane budget reported with seconds and source, never guessed (`PG-PR-06`: seconds, from the lane's own stamps).

## Acceptance and report

- A1: one rebuild + one recreate THROUGH THE LANE SOCKET, direct new running-instance proof, health green and explicit application/schema/count deltas; served bundle hash recorded and DIFFERENT from `8ba02c64…` unless byte-identical-for-reason is proven.
- A2: actual base/hash and merged-vs-served diff checked — only the two expected sets differ; still-open items expressly identified as unchanged (SG-199 density/auth-live/live-container/zoom/touch/dark stand; ISS-4 carried); work diff only SG-202 namespace.
- A3: command logs and final report `docs/worklogs/SG-202_report.md`; elapsed per leg and total vs observed lane bound; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-202.
- A4: notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-202 | Report: docs/worklogs/SG-202_report.md`, Work-HEAD recorded, branch/report push complete. Use the bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`; no silent deployment on any unrated/blocked result.
