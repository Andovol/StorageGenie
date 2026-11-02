SG-275 — Accepting an already committed candidate from before SG-270 must not create a second item
Model: opencode-go/deepseek-v4.1-flash; effort: max (read from process args: `opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`)
Working directory: /home/andrei/StorageGenie; remote: git@github.com:Andovol/StorageGenie.git
BASE ref: origin/automation; resolved BASE commit: 19be9e300e134b53ab7b83ffc53267b07251d9e3
WORK_HEAD: 51b3cbaaef85be383df7d476a743df0008c2ab13
Contract echo: `**Contract version: 0.56.0**` — /home/andrei/storagegenie-contract/CODER.md line 3; AGENTS.md records 0.56.0.

(a) Issues / deviations / surprises
- G1's expected shape is followed: `_prepare_commit_steps` reads the commit step's output before resetting it, and when that output names this candidate and a created asset, records it in the review step's `committed_assets` map. The existing branch in `commit_job_candidate` then returns that asset with `created` false and checks its household before returning.
- Sounder variation, stated: I record only outputs with `created: true`, matching the map writer's own gate (`result.get("created") is True`). A duplicate commit's output names the existing target asset with `created: false`; adding that to the created-asset map would change a repeat duplicate from `duplicate_linked` to `committed` and claim an asset the candidate did not create. Duplicates already create nothing on repeat, so the required class is unaffected.
- A3 answered: no pre-SG-270 row can have an item its job's commit output no longer names. Before SG-270 `commit_job_candidate` selected the job's first-created candidate and created one asset; split children shared the job but could not commit (the first-created origin is state `split`, which `commit_candidate` refuses), so a pre-SG-270 job held at most one committed item and its commit output named it. Since SG-270 every created item has a `committed_assets` entry, so a later commit overwriting the output does not lose earlier items. Failed commits have no asset id. The fallback therefore closes the whole older-row class.
- FAIL log is assertion-level, not a collection abort: 2 failed, 2 passed, 13 deselected. The two failures are the required older-row accept and edit cases; the failed-retry and new-row cases pass on base. PASS on the candidate is 17 passed.
- A ruff C901 appeared after the first patch (11 branches > 10); the commit-output read moved into `_created_asset_from_commit_step`, keeping behaviour identical. The PASS and affected-twice runs were repeated on the final code.
- Scoped mypy follows imports and reports 3 pre-existing errors in `app/models/base.py` and `app/services/audit_service.py`; none is in the changed file. The repo-wide mypy reds remain out of scope and are not claimed clean.
- `npx` is not on PATH on this lane; the local binaries (`frontend/node_modules/.bin/tsc`, `vitest`, `eslint`) and `npm run build` were used. No network, key, `.env`, live database, provider, restart or deploy.
- Scratch `output/SG-275-scratch/` was removed by exact path after the base worktree was removed; `output/` itself and `output/dispatch` were not touched.

(b) Actions
Changed product/test files: backend/app/api/v1/candidates.py, backend/tests/test_sg270_flow.py, frontend/src/components/CandidateCard.tsx, frontend/src/routes/ReviewPage.tsx, frontend/src/routes/InboxPage.tsx, frontend/src/routes/ReviewPage.test.tsx, frontend/src/routes/InboxPage.test.tsx, frontend/src/routes/theme-adoption.test.tsx. `backend/app/services/candidates.py` was read but needed no change.
Commits: 51b3cba (G1/G2/G3 product, tests and evidence logs); this report is committed after it.
Push: origin/automation moved to the report commit (observed after push).
External effects: none. Provider calls: 0 network; scripted provider only. Restart/deploy: none.
Health: start 200 at 2026-11-02T15:40:56Z; end 200 at 2026-11-02T15:47:20Z.
Durations: engine start epoch 1793633975 (`output/dispatch/SG-275.growth` first line); end epoch 1793634440; engine elapsed 465 s at end-health against ≈500 s expected (`UNVERIFIED — my estimate`), and under the 1500 s publish bound. Phases over 60 s: the host suite 74.36 s and the whole `make backend-test` 110 s (15:44:10Z to 15:46:00Z, including the image build); no other phase exceeded 60 s (frontend suite 12.39 s, build 2.96 s, image proof 1.93 s, affected runs 2–7 s).
Test-command count: 11 pytest/vitest/make invocations; two were final-code re-runs after the helper extraction.
No skipped G item. G0, G1, G2 and G3 all have observed outcomes.

(c) Verification
G0 preflight: docs/worklogs/SG-275_preflight.log — `docker version` shows a Server section, version_rc 0; `docker run --rm busybox true` rc 0; DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-275/docker.sock.
FAIL against base 19be9e3 in an isolated worktree with the candidate test copied in (temporary SQLite only):
  docs/worklogs/SG-275_fail_old_row.log — 2 failed, 2 passed, 13 deselected in 2.94 s. Failures are the intended older-row assertions (repeat accept/edit returned a different asset; item count would be 2), not an import abort.
PASS against the candidate:
  docs/worklogs/SG-275_pass_old_row.log — 17 passed in 6.13 s.
Final gate: `make backend-test` rc 0:
  docs/worklogs/SG-275_backend_gate.log — host suite 781 passed, 2 deselected, 49 warnings in 74.36 s; image proof 2 passed, 6 deselected in 1.93 s (the two marked tests stayed deselected in the host run).
Frontend: docs/worklogs/SG-275_frontend_test.log — 30 test files passed, 336 tests passed in 12.39 s; `make frontend-test` rc 0.
Affected files twice consecutively:
  docs/worklogs/SG-275_backend_twice.log — RUN 1 17 passed, RUN 2 17 passed (5.98 s / 6.87 s).
  docs/worklogs/SG-275_frontend_twice.log — RUN 1 48 passed, RUN 2 48 passed (2.26 s / 2.30 s).
Lint/type: docs/worklogs/SG-275_lint_type.log — ruff all checks passed; scoped mypy 3 pre-existing errors in 2 imported files, 0 in the changed file. docs/worklogs/SG-275_eslint.log — rc 0 on all changed frontend files. docs/worklogs/SG-275_tsc.log — rc 0.
Frontend deploy build: docs/worklogs/SG-275_frontend_build.log — `npm run build` rc 0; tsc + vite built in 2.96 s.
Changed-paths reconciliation: the 8 changed files are all inside the packet's scope; the other 13 files are `docs/worklogs/SG-275*` evidence. Zero schema, migration, model, Dockerfile, compose, lockfile, dependency, env, host, provider, running-container or deploy bytes.
Constraints: temporary test databases only; no live database read or write. Restart: none. Provider: none. BASE ref and resolved commit stated above as two fields. Scratch removed by exact path; `output/dispatch` untouched.

A1 outcome: the pre-SG-270 accept test returns the same asset with `created` false, job COMPLETED; the edit test does the same through the edit action; both keep the asset count at 1.
A2 outcome: the failed commit's step output carries no asset id, the retry through `/v1/imports/{id}/retry` creates exactly one item, and a new row's repeat accept still returns the same item with `created` false.
A3 outcome: answered above with the commit-output/selection reasoning; no older row can hold an item the output no longer names.
A4 outcome: both fallbacks are gone (`CandidateCard.tsx`, `ReviewPage.tsx`, `InboxPage.tsx`), their fixtures now carry the required fields, and the 336-test frontend suite is green.
A5 outcome: FAIL-then-PASS logs are committed; host, image-proof and frontend suites green; affected files run twice; build rc 0; counts quoted.
A6 outcome: scope reconciled; zero forbidden bytes.
A7 outcome: preflight proven before the gate; health 200 at start and end.
A8 vacuity: a failure would have looked like an item count of 2 or `created` true on a repeat. The base run did show both (the failure log), and the candidate run showed neither: count 1 and `created` false on both older-row repeats.
A9: last line below.

INTENT (behaviour-changing items):
- G1 code reuses a prior commit's own output before reopening the step; the check expects one item and `created` false on a repeat; the packet asks for exactly that. Agree.
- G2 code reads the required fields directly; the check expects the same blocked/enabled and link behaviour; the packet says the backend always sends them. Agree.

TWINS: the two removed fallbacks were searched across `frontend/src`; no other `??` read of `blocking_review_task_ids`, `review_task_ids` for blocking, or `subject_kind` remains. Out of scope and unchanged: the SG-270 audit's other REMAINING items and the parked mypy/eslint debt.

UNCLEAR
FIRST READ: whether the commit-output fallback should also carry duplicate rows; decided created-only for the reason in (a), with duplicate behaviour preserved.
DURING EXECUTION: `npx` absent from PATH; local frontend binaries used. The scoped mypy run follows imports and shows pre-existing debt outside the changed file.
REMAINING: SG-270 audit REMAINING lines keep their destinations and are not this slice's work — screens unseen (SG-273), the false date task from non-date `needs_evidence` (SG-271), pre-existing rejected-candidate task rows counted read-only by the rider (SG-276), and the accepted-candidate reload's missing item link (SG-271). No new REMAINING item from this slice.

Verification: PASS
