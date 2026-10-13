# SG-175 — Live blocked-task projection and consistent Review acceptance

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: disposable test SQLite; production read-only observation only.**
**Restart: none.** New code remains UNSERVED pending audited deployment.
**Autonomy: L2.** Approved scope: STATE RESUME ordered SG-175; D-1012-14; owner request “packetize and dispatch SG-175’s approved blocked-state repair, including measured probe assertions and duplicate-copy cleanup.” This is implementation of SG-173's audited diagnosis, not another diagnosis slice.

## Why this exists — hypotheses to verify on the resolved base

Expected root cause, confirmed in the Architect's current-tree read: `backend/app/api/v1/candidates.py::get_candidate` returns proposal-embedded `review_task_ids`; `decide_candidate` gates accept/edit on live `ReviewTask` rows matching subject_ref, household_id and status=open. `services/candidates.py` and `services/dedup.py` write proposal snapshots. Resolving a task does not erase those snapshots. SG-173 isolated routes demonstrated stale IDs after resolution and server acceptance with zero live blockers; live read-only observations showed the corresponding UI dead-end. Sources: `docs/worklogs/SG-173_audit.md`, `SG-173_report.md`; reproduce the narrow live observable with GETs only, reporting actual image/health and sanitized response. Expected deployed image d5da5684 is prior SG-174 evidence, not a freshness gate.

Current consumers: `frontend/src/components/CandidateCard.tsx` disables Accept on nonempty review_task_ids; `frontend/src/routes/ReviewPage.tsx` uses that field for shortcut A. CandidateCard renders the identical blocked sentence in both the dedup alert and the standalone block. SG-171 finding F-SG171-5 is approved for cleanup here. Job/enrich response readers and the job-step snapshot also carry task IDs: inspect `backend/app/api/v1/jobs.py`, `backend/app/api/v1/enrich.py`, `backend/app/services/candidates.py` before altering semantics. Historical job-step/proposal snapshots remain historical; do not rewrite their stored data.

SG-173 probe limitations: `docs/worklogs/SG-173_probe.py` prints literal “expiry accepted assertion exists=True” and unconditional PROBE_OK; neither is accepted proof. Its root-venv docstring is wrong: working interpreter observed at `/home/andrei/StorageGenie/backend/venv/bin/python`. Verify that interpreter on execution. Preserve the SG-173 artifacts as historical evidence; adapt reusable verification into `docs/worklogs/SG-175_probe.py`, with the corrected command, measured assertions and raw observations. No need to redesign expiry behavior.

## G1 — Repair the live response at its source

Project the current open task IDs for this candidate AND household into candidate GET's existing review_task_ids field, with the same blocker semantics as the production Accept gate. Include live tasks absent from the proposal; exclude resolved/missing/stale/foreign-household/other-subject IDs. Preserve API shape, household authorization, proposal storage and historical snapshots. Reuse an existing query/helper where appropriate; add no new persistence, schema, task type, route or polling machinery. Re-read all consumers of the changed response; report their disposition.

Design comparison, Architect judgement:

| Approach | Gives | Costs |
|---|---|---|
| Live GET projection using existing task rows (chosen) | Same source as Accept; existing UI field | Read query per GET; report query/runtime delta |
| Delete embedded IDs on every resolution | Smaller response read | More writers and stale legacy rows; would require forbidden production backfill |

The projection replaces the stale snapshot as UI authority; it adds no second state store. Do not introduce unrelated response changes. If current code disproves the hypothesis, correct it under PB-1; a materially different repair is STOP, not silent widening.

## G2 — Keep button, keyboard and visible reason consistent

CandidateCard and ReviewPage must use the live response consistently: blocked means no Accept action from click or shortcut; zero live blockers means Accept offered through both paths. Preserve pending/busy protection for keyboard and button; no repeated mutation while pending. Preserve existing input/textarea shortcut protection and non-Accept actions. Avoid adding a separate task-list-derived blocker which could disagree with the server or be truncated by pagination.

Render the blocked reason exactly once for blocked candidates, both with and without dedup matches, preserving the visible Inbox affordance and dedup information. Unblocked candidates show no blocked reason. Duplicate-copy cleanup means this repeated UI sentence, not document deletion or collapsing historical evidence. Reuse the standalone visible reason established by SG-171; no styling redesign.

## G3 — Replace assertion-shaped labels with measured probe evidence

Adapt the isolated SG-173 probe narrowly. Read back the asset through the real GET route after manual expiry completion; assert a persisted accepted EXPIRY_FIELD assertion with the expected date and provenance shape, and assert the intended task is resolved and returned by the real completion response. Measure values before printing success. Each criterion actually exercised must assert its observed expected outcome before PROBE_OK; distinguish expected still-unrepaired classification/Resolve/visibility behavior from repaired blocked state. Do not pretend SG-176..178 behavior is fixed. Success footer must be unreachable on failed criteria.

Show the assertion checks rejecting a deliberately wrong expected value/controlled missing accepted assertion in disposable data, and verify that the control landed. Use real application readers/writers, not a fake implementation. Keep the independent unchanged control `backend/tests/test_plugin_expiry.py::test_dateless_import_requires_manual_entry_and_reads_back` in verification. Explicit disposable DB/dependency isolation is required before any synthetic write; no provider calls, no production credentials/settings copied to base checkouts. Isolation must cover database AND evidence paths. Restore dependency overrides and close resources.

## Constraints

- Scope ceiling: `backend/app/api/v1/candidates.py`; a narrowly reusable live-task helper in existing `backend/app/services/candidates.py` only if needed; `frontend/src/components/CandidateCard.tsx`, `frontend/src/routes/ReviewPage.tsx`; corresponding `backend/tests/test_candidate_read.py`, `backend/tests/test_candidates.py`, `frontend/src/components/CandidateCard.test.tsx`, `frontend/src/routes/ReviewPage.test.tsx`; `docs/worklogs/SG-175*`. Existing fixtures are module-local (`candidate_read_db`, `candidate_db`, `plugin_db`), not a shared conftest; changes to the first two fixture modules are in scope, plugin control remains unchanged. No fixture/database scope widening.
- No production INSERT/UPDATE/DELETE, POST/PUT/PATCH/DELETE, manual task resolution, import, evidence-store write or row repair. No service rebuild/restart/deploy. Start/end production health GET per CO-92; read-only GET reproduction only. Live final story proof belongs to the post-repair deployed URL, never a temporary Vite server presented as deployment proof.
- No classification UI, taxonomy redesign, Resolve/expiry behavior repair, ordering/visibility repair, Scene wiring, unrelated PR work, host/credential/configuration changes, schema/migrations or paid application calls. SG-176..178 stay pending in STATE.
- Privileged denial is STOP (PG-PR-03); no sudo, alternate identity/mount/socket or routing around it. “STOP and report” requires stopping, not merely disclosing. Finished work follows PB-6.
- Back up mechanical edits; exact-match targeted changes preserve encoding and unrelated bytes; print addressed lines before editing; conservation/diff checks per G-T5. No stash or ignored artifacts force-added. Commit only allowed paths, actual command captures and report.
- Per-command bounds: ordinary reads 120 seconds; tests/build/probe 600 seconds, uncalibrated inherited SG-173 precedent. Visible timeout and STOP on hang; no polling or interactive prompts. Lane owns whole-run budget; report current RUN_BUDGET_S/stop window from the lane environment and elapsed time. If time runs short, publish completed work plus exact remaining criteria under PB-6, never a false success.

## Acceptance criteria — questions and discriminating evidence

- A1: Does GET agree with the production gate? Real-route isolated tests cover open→409, resolution via the real resolution writer→empty live IDs and successful Accept; stale/missing embedded IDs do not block; a live task omitted from proposal does block; foreign household/other subject tasks do not affect this candidate; household mismatch remains denied. Assert proposal snapshots unchanged by GET. No production row repair.
- A2: Do both user paths follow the same state? Render/interaction tests prove blocked button and shortcut do not mutate; response refreshed after resolution enables click and shortcut; pending prevents duplicate Accept. Preserve existing unrelated controls. Prefer minimal integration across the real components; mocks may supply transport responses but must not implement the logic being tested.
- A3: Does duplicate cleanup preserve meaning? Real CandidateCard renders with blocked+dedup and blocked+no-dedup have exactly one reason sentence and the existing Inbox link; unblocked has neither. Keep dedup evidence/advisory behavior.
- A4: Is probe success measured? Real completion POST followed by real GET asserts the accepted expiry value and resolved task; wrong-value/missing-assertion control demonstrably fails and cannot print PROBE_OK. Retain observed values and isolation evidence. Historical SG-173 logs untouched.
- A5: Commit `docs/worklogs/SG-175_failpre.log` and `SG-175_passpost.log` with BOTH runs of discriminating new regression tests against resolved pre-change code and final code. Probe controls/output in `SG-175_probe_out.log`; commands/build/health/scope checks in `SG-175_verify.log`. Failures must be for the intended property, not setup errors. Nonempty fixture/output checks bind. Run focused backend candidate read/gate tests, the unchanged plugin node control, CandidateCard/ReviewPage tests, and deployed frontend's actual typecheck/build command (inspect package scripts). No full suite or directory-wide end-to-end sweep; substitute tests are the named backend/frontend modules. This is UNSERVED verification; later deployed-URL proof remains owed.
- A6: Report requested ref/resolved hash, contract echo/source expected 0.46.0, actual settings identity, WORK_HEAD, query/runtime delta, scope diff, start/end health, actual elapsed versus lane bound, all constraints, and every UNCLEAR/REMAINING disposition. No completion claim for unexecuted criteria.

Guards relied on: PG-EV-01/02/03/05/06/09/13; PG-SC-01/02/04/09/10/12; PG-IC-01/07/09; PG-DP-02/03; PG-PR-03/04/07/10. PG-SC-04: report remaining matches for the obsolete GET snapshot predicate; historical producers need not reach zero.

## Report and receipt

First token `SG-175`. Write `docs/worklogs/SG-175_report.md` and the named sanitized captures. Close with FIRST READ / DURING EXECUTION / REMAINING. State code UNSERVED, production writes none, no restart, next repairs pending. Verify host/lane contract from current source; known host rules_check cache/tag/auth limitations are inherited SG-174 observations, not authority to change host rules. Report current capability/configuration readback without using mutations as probes.

Use the bound notes-ref receipt (CO-60): commit with `Dispatch-ID: SG-175` trailer; publish a note on `refs/notes/storagegenie-coder-reports` whose first line is `Dispatch-ID: SG-175 | Report: docs/worklogs/SG-175_report.md` and includes Work-HEAD; push automation and that notes ref. Read back the note on remote and identify its annotated commit. Legacy finalize_dispatch_report.sh is retired; do not use it.
