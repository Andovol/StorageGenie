# SG-174 — Standing close-out rebuild, one recreate and live verification

`PB-1`–`PB-6` bind (`CODER.md` §14). Authoring date 2026-10-12 (metadata).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: production SQLite read-only.** No schema migration or application data write.
**Restart: exactly one backend recreate.**
**Autonomy: L2.** Sole production authorization: AGENTS Close-out standing owner directive, "Always do a live deploy before session close", and the present owner close request. Product repairs are pending, not shipped. SG-173 diagnosis has been audited, rated 97 with no flag; see SG-173_audit.md for provenance limitations.

## Why this exists

Owner asks to close. This rider fulfills the standing deploy directive even though SG-173 changed diagnostic artifacts only. Expected live image is 9064d2ce (re-observed in SG-173); backend/frontend bytes are expected unchanged from that deployment. Verify that expectation on target. A reproducible build may retain its image ID and identical bundle hashes: neither is failure here, and neither is proof of recreation. Do not invent a changed bundle requirement or claim that the story repairs are served.

Expected recorded/published/host contract 0.46.0; previous host echo comes from SG-173_report.md, `/home/andrei/storagegenie-contract/VERSION`. Echo version/source and report differences. Known host rules_check exit 3 is independently explained in that report, not a license to repair host tags/auth.

## G1 — One rebuild and one recreate

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, schema head and authoritative table counts. Enumerate tables on target rather than assuming the prior 28-table list. Confirm backend/frontend/models/migrations have no changes against the deployed product base from SG-172 (`3ae5541`); report actual diff if expectation differs and STOP before deployment.

Reuse SG-172's documented granted lane: `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` exactly once, then `docker compose up -d --no-deps backend` exactly once. Read grant/capability without attempting privileged writes as a probe. PG-PR-03: privilege denial is STOP, never sudo/another identity/another mount. No host config changes.

## G2 — Verify new running instance without claiming a repair

Observe a new container identity and start time. Health must be ok for DB/storage; repeat six health GETs as the existing close-out precedent, not an inferred reliability rate. Re-read hashes, schema and table counts; require no migration and no slice-caused row change. If owner activity changes counts, report direct discriminating evidence; do not hide unexplained deltas.

Verify `/review` for one enumerated existing candidate, `/inbox`, `/catalog` through the new server (read-only GETs), and existing CORS preflight. Expect existing Review/classification/Resolve story defects still present; this deploy does not fix them. Bundle/image hashes may match BEFORE because product bytes are unchanged. Recreate is proven by container ID/Created, not RestartCount resetting. No browser interactions causing writes; no paid API calls.

## Constraints

Scope: docs/worklogs/SG-174* only. No product, configuration, schema, migration or test edits. No production INSERT/UPDATE/DELETE, manual resolving, imports or evidence-store mutation. One rebuild and one recreate only; second issuance is STOP. Ordinary reads/verification bounded at 120s per command, build at 600s (uncalibrated inherited precedent); visible timeout finding; never approach idle kill 900s. No interactive prompt or polling loop.

Full suite waived per PG-DP-02; substitute is post-recreate read-only identity/health/schema/counts/pages/preflight verification plus SG-173's already executed targeted regression controls. No new code has to pass a new behavior test. Application provider spend prohibited; actual Coder-platform spend unavailable unless directly exposed. Runtime-vs-lane budget/stop window must be reported with seconds and source, not guessed.

## Acceptance and report

- A1: one rebuild + one recreate, direct new running-instance proof, health green and explicit application/schema/count deltas.
- A2: actual base/hash and product diff checked; work diff only SG-174 namespace; old code/known defects expressly identified as unchanged.
- A3: command logs and final report docs/worklogs/SG-174_report.md; elapsed per leg and total vs observed lane bound; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned.
- A4: notes-ref receipt on refs/notes/storagegenie-coder-reports published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-174 | Report: docs/worklogs/SG-174_report.md`, Work-HEAD recorded, branch/report push complete. Use bound lane receipt, never legacy finalize_dispatch_report.sh. First report token SG-174.

Guards invoked: PG-DP-01, PG-DP-02, PG-IC-07, PG-PR-03, PG-PR-04, PG-PR-06, PG-PR-10. Stop follows PB-6; no silent deployment on any unrated/blocked result.
