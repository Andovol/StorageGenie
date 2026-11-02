SG-270 — Flow fixes: an imported item can always be reached, accepted and finished on its own page
Model: opencode-go/deepseek-v4.1-flash; effort: max (read from process args: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`)
Working directory: /home/andrei/StorageGenie; remote: git@github.com:Andovol/StorageGenie.git
BASE ref: origin/automation; resolved BASE commit: efdedcf2171a9106a359dacb414d6a6fe0323aec
WORK_HEAD: 9bacf4cf91a00779b41d242ee77960deffd0e07e
Contract echo: `**Contract version: 0.56.0**` — /home/andrei/storagegenie-contract/CODER.md line 3; AGENTS.md records 0.56.0.

(a) Issues / deviations / surprises
- G2 was a real fourth dead end: base `commit_job_candidate` took the first-created candidate (the retired split origin), so the first child accept failed and a second child found COMMITTING already complete. Fixed with the review step's decided `candidate_id` plus a `committed_assets` idempotency map in the same step output; no job-state machinery added. `job_service.py` was not needed.
- First `make backend-test` failed in the image's frontend build on a duplicate property introduced in `CandidateCard.test.tsx` by my own test edit (tsc TS1117). Fixed the test file; the second `make backend-test` was green. This is a test-verification retry, not a product retry.
- The first FAIL-proof attempt aborted at collection because the new test imported `manual_task_change`, a helper added by this slice. That is not a valid failing baseline (python overlay), so the test now composes the expected asset-side payload from the existing `EXPIRY_FIELD`; the recorded FAIL run is assertion-level, 11 failed / 2 passed.
- `needs_evidence` is provider-global, not date-specific. Food prompt v4 rule 20: "true when any date the category requires is unknown. Food & beverages always require a date decision, so any null `expiry_date` sets this flag." Cosmetics prompt v4 rule 21: "true when the opened-date decision the category requires is unknown." Schema `schemas.py:140-145` only requires a non-empty `unknowns` list. Therefore it can be true when the missing unknown is `opened_date` (or any other unknown), and `candidates.py` still opens an `expiry.manual_entry` task. False date task for a later slice; not changed here.
- A rejected candidate left open before this slice still lists as `subject_kind=candidate`, `data_required=true`, Resolve hidden, Review link to `/review/<candidate>`; no data cleanup was run.
- Accepted-candidate reload: GET returns `state=accepted`, `review_task_ids=[]`, `blocking_review_task_ids=[]`, `asset_id=null` for a new asset (the response field was never persisted), so the item link is gone after reload. Not built for, as instructed.
- Baseline mypy: scoped run is 9 errors before and 9 after; identical categories, only line shifts. Repo-wide mypy reds and the one pre-existing eslint error in `App.household-nav.test.tsx` (`fireEvent` unused) remain out of scope; that file was touched only to add the two new ReviewTask fields and still carries the pre-existing error.
- No HTTP provider call, no key, no `.env`, no live database, no deploy, no restart. Scripted providers only.

(b) Actions
Changed files: backend/app/services/candidates.py, backend/app/api/v1/candidates.py, backend/app/api/v1/review_tasks.py, backend/app/plugins/expiry_tracker.py, frontend/src/api/client.ts, frontend/src/api/types.ts, frontend/src/components/CandidateCard.tsx, frontend/src/routes/InboxPage.tsx, frontend/src/routes/ReviewPage.tsx, frontend/src/routes/AssetDetailPage.tsx; existing tests updated: backend/tests/test_sg270_flow.py (new), frontend CandidateCard/InboxPage/ReviewPage/AssetDetailPage tests, frontend/src/App.household-nav.test.tsx (new required fields only).
Commits: 5326940 (G1/G2/G6 backend+tests), ace31de (G4 review-task read), c4fbadd (G3/G4/G5 frontend), 9bacf4c (evidence logs + final test-file proof fix).
Push: origin/automation moved to 9bacf4c (observed after push).
External effects: none. Provider calls: 0 network; scripted invocations confined to tests.
Health: start 200 (2026-11-02T15:07:42Z); end 200 (2026-11-02T15:34:30Z) — unchanged, OK.
Durations: start epoch 1793632062, end epoch 1793633670, elapsed 1608 s as of end-health (≈1500 s expected; +108 s from the image-build retry). Phases over 60 s: backend host suite 78.59 s; `make backend-test` including image build ≈150 s. Highest-impact action: moving the date task to the asset in the same transaction as the asset, which removes the F2 dead end without a new route.
Test-command count: 17 targeted/full invocations; retry count: 1 verification retry (image build).
No skipped G item. G1, G2, G3, G4, G5, G6, G7 all have observed outcomes.

(c) Verification
FAIL against base efdedcf in an isolated worktree with the candidate's test copied in (temp SQLite only):
  docs/worklogs/SG-270_fail_new_tests.log — 11 failed, 2 passed in 4.49 s. Failures are the intended assertions (409 on date-only accept, missing blocking split, task still on candidate, missing subject fields), not an import abort.
PASS against the candidate:
  docs/worklogs/SG-270_pass_new_tests.log — 13 passed in 4.94 s.
Final gate: `make backend-test` rc 0 (host suite then image proof):
  host re-read docs/worklogs/SG-270_backend_gate.log — 777 passed, 2 deselected, 49 warnings in 78.59 s.
  image proof — 2 passed, 6 deselected in 2.25 s (the two marked tests remain deselected in the host run).
Frontend: docs/worklogs/SG-270_frontend_test.log — 30 test files passed, 336 tests passed in 14.20 s; `make frontend-test` shape (`npm test -- --run`) rc 0.
Affected files twice consecutively:
  docs/worklogs/SG-270_affected_twice.log — RUN 1 123 passed / RUN 2 123 passed.
  docs/worklogs/SG-270_frontend_affected_twice.log — RUN 1 59 passed / RUN 2 59 passed.
Lint/type: docs/worklogs/SG-270_lint_type.log — ruff all checks passed; mypy 9 errors in 3 files. docs/worklogs/SG-270_mypy_base.log — the same 9 errors on base (0 new, scoped; absolute debt 9/whatever the repo-wide count is, not claimed clean).
Frontend deploy build: docs/worklogs/SG-270_frontend_build.log — `npm run build` rc 0, tsc + vite built in 2.96 s.
Docker preflight: Server section present, `docker run --rm busybox true` rc 0, DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-270/docker.sock.
Changed-paths reconciliation: every changed path is inside the packet's scope ceiling; no schema, migration, model, Dockerfile, compose, lockfile, dependency, env, host, provider, container or deploy bytes.

A1 outcome: date-only accept and edit both 200; multi_item still 409; moved task on asset with `review_task.move` audit; manual date, clear and non-perishable each resolve it; commit wrote no `plugin:expiry-tracker/expiry_date` assertion.
A2: hold leaves the task open; reject closes it with resolution `{candidate_rejected: <id>}`; duplicate target accepted-date and accepted-null both close naming the target, target-with-open-task closes joining the existing id, other-household target raises CandidateBlockedError and moves nothing; split closes origin tasks with `{split: <origin>}`; merge behaviour unchanged (test_sg112_merge still green).
A3: producers of `expiry.manual_entry` enumerated: (1) candidates.build_candidate_from_extraction (candidate subject, from extraction.needs_evidence); (2) expiry_tracker._manual_task (asset subject), called by apply_extraction_result and by classify_asset. Packet ranges match; the extra call sites are the difference. needs_evidence meaning above.
A4: driven split test creates two assets, each child's own date task follows its asset; accepting the same child twice returns the same asset with created=false and the asset count stays 2. Single-candidate jobs unchanged (existing tests green).
A5: GET /v1/jobs/{id}/candidates is listed in the Inbox with name, state and Review link; split origins are labelled "retired split origin" and get no link. Audit I1 driven: a dated AI-read item opens no task at all (test passes on base and candidate), so it was as unreachable as F1 before this slice.
A6: asset rows link to /assets/<id>, candidate rows to /review/<id>, unknown rows link nowhere; Resolve absent when data_required; existing response fields preserved (added subject_kind/data_required).
A7: accept response link renders; duplicate says "Open the existing item"; date-only accept enabled on button and keyboard, any other blocking task disables both; unclassified item shows "Choose a category, then add a date if it has one." while the date form stays hidden.
A8: classify-to-food then non-perishable test passes through the real writer; classify response type carries resolved_review_task_ids; split-origin orphan resolves on non-perishable with audit resolution `{manual_entry_orphan: true, asset_id: ...}` matching store_manual_expiry.
A9: FAIL/PASS logs committed; host suite, image proof and frontend suite green; affected files twice; build rc 0; counts quoted.
A10: scope reconciled; zero forbidden bytes.
A11: Docker preflight proven before the gate; health 200 at start and end.
A12 vacuity: failure would have looked like a 409 on date-only accept (observed 200), a task still on the candidate (observed subject_ref=asset), a second asset (observed one for duplicate/repeat accept), a Review link to a 404 (observed asset link resolves; split origin unlinked), or Resolve still showing on a data-required row (observed absent). None was observed.
A13: last line below.

INTENT (behaviour-changing items):
- G1 code moves the open date task to the asset at commit; the check expects subject_ref=asset and an open task; the packet says the task follows the item. Agree.
- G2 code commits the decided candidate and records committed_assets; the check expects one asset per child and one on repeat; the packet says each child commits and repeat is idempotent. Agree.
- G4 code derives subject_kind from live candidate/asset rows; the check expects item/candidate links and hidden Resolve; the packet says truthfully. Agree.
- G5 code enables accept on blocking_review_task_ids; the check expects enabled for date-only and disabled for multi_item; the packet says date-only only. Agree.

TWINS: task-link class was searched by subject_kind consumers; InboxPage was the only row renderer changed. ReviewPage and AssetDetailPage have no other task-subject link. Out of scope not changed: the non-empty resolve bypass (W9), F4/F5/F7/F12, F8, F3/F13, F9/F10, styling.

UNCLEAR
FIRST READ: whether G2 needed job_service changes; reading showed candidate selection + step reset suffice, so job_service.py stayed untouched.
DURING EXECUTION: the split-origin orphan test needed a pre-existing open task seeded directly (the new split path now closes origin tasks), which the packet explicitly allows for pre-existing-row cases.
REMAINING: screens unseen (no browser) as in SG-269 I2; the false date task from non-date needs_evidence remains for a later slice; pre-existing rejected-candidate task rows remain for the live rider to count; accepted-candidate reload still has no asset_id.

Verification: PASS
