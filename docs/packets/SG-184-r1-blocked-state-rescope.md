# SG-184 — R1: re-scope SG-175 blocked-state repair as a clean slice (DRAFT, next session)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: DRAFT prepared 2026-10-13 from SG-173/175 audits; scope-approved D2 (R1 re-scope, breach acknowledged). RE-REVIEW against the tree before dispatch next session; do not dispatch from this text without that pass.**
**DATABASE: separately isolated disposable test database/storage; production GET observations only.**
**Restart: none. Autonomy: L2.** No STOP-breach waiver: the SG-175 run (90 FLAG:SAFETY, denied-Docker continuation) is not blessed by this slice — the repair is re-derived and re-proven cleanly. Held SG-175 code stays UNSERVED until this slice lands.

## Why this exists

SG-173 isolated the defect class: `candidates.py::get_candidate` returns proposal-embedded `review_task_ids`; `decide_candidate` gates accept/edit on live `ReviewTask` rows; resolving a task does not erase snapshots, so the UI dead-ends on stale IDs (hypotheses; verify on the resolved base). SG-175's repair direction was verified functional but its run breached PB-2 and acceptance/deploy were held. Expected scope (re-verify each path exists before changing it): `backend/app/api/v1/candidates.py` + narrowly a reusable live-task helper in existing `backend/app/services/candidates.py` only if needed; inspect `backend/app/api/v1/jobs.py`, `backend/app/api/v1/enrich.py`, `backend/app/services/candidates.py`, `services/dedup.py` snapshot writers before altering semantics; historical snapshots stay historical, never rewritten.

## G1 — Repair the live response at its source

Re-derive (do not port hunks blindly from the held candidate): live `ReviewTask` rows (matching subject_ref, household_id, status=open) govern accept/edit gating and the returned `review_task_ids`, so a resolved task stops blocking. FAIL-then-PASS against pre-change code on disposable state: stale-ID reproduction (resolve → GET shows live IDs), accept/edit unblocked after resolution, still blocked with genuinely open tasks. Counter-controls: foreign-household 403s, historical-snapshot rows untouched (byte-compare a sampled snapshot before/after).

## G2 — Button, keyboard and visible reason consistency

`frontend/src/components/CandidateCard.tsx` (Accept enablement + the duplicated blocked sentence — F-SG171-5 cleanup approved here) and `frontend/src/routes/ReviewPage.tsx` (shortcut A): one visible reason, keyboard reachable, no two divergent blocked wordings. Presentation-only acceptance per `CO-25`: committed screenshots plus an owner checklist — but the Architect (0.47 screenshot rules) independently opens every image; a written screenshot audit alone is not evidence.

## G3 — Measured probe evidence, not assertion labels

Every repaired behavior ships a failing-then-passing focused test in the in-scope test files (`backend/tests/test_candidate_read.py`, `backend/tests/test_candidates.py`, `CandidateCard.test.tsx`, `ReviewPage.test.tsx`; module-local fixtures `candidate_read_db`/`candidate_db` may change, `plugin_db` control unchanged, no conftest/fixture-scope widening). Probe reads EXPIRY/acceptance state through the actual asset GET after actual completion POST, with missing-assertion and wrong-date negative controls on the same reader.

## Constraints and acceptance

- Write ceiling `docs/worklogs/SG-184*` + the in-scope product/test files above; nothing else. No migration/schema/dependency/lockfile change; no production row/evidence write; no paid call; no auth/credential/infra change; no restart/rebuild/recreate (serving is a later rider, never this slice).
- Disposable `DATABASE_URL`/`STORAGE_ROOT` asserted before any app import; scripted/fake providers only; no `.env` copy/dump.
- ALL optional environment/Docker probes excluded; ANY privileged denial STOPS the whole slice (`PB-2`); the SG-175 breach class must not recur — a denial followed by continuation fails the slice regardless of green tests.
- Ordinary commands 120s; focused disposable tests/probes 600s (uncalibrated); no full suite; no watcher.
- Start/end health GET; contract 0.47.0 echo with actual source; requested/resolved base, Work-HEAD, settings identity, lane budget/deadline/elapsed.
- A1: stale-ID root repaired at source with live-row gating + snapshot preservation proof.
- A2: UI consistency with screenshot evidence + owner checklist, no divergent wordings.
- A3: FAIL-then-PASS focused tests with negative controls on real readers; no placebo (the test must drive the repaired path).
- A4: first token SG-184; `docs/worklogs/SG-184_report.md`; FIRST READ (packet premises checked/corrected) / DURING EXECUTION / REMAINING with dispositions. Partial honest proof, never invented completeness.

Guards: PG-EV-01/02/03/04/05/06/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10.

Receipt: commits carry `Dispatch-ID: SG-184`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-184 | Report: docs/worklogs/SG-184_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates before any serving rider. No close or deploy inside this slice.
