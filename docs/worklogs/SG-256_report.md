SG-256. model=opencode-go/deepseek-v4.1-flash effort=max, read from /proc/2903693/cmdline (opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max); served model=unknown (no provider call). dir=/home/andrei/StorageGenie; remote=git@github.com:Andovol/StorageGenie.git; BASE ref=origin/automation; BASE COMMIT=4942b3740401c6b97db73869293d1a569ba357e1; WORK_HEAD=405625e57d0d6476d4338928025b2c9a14907514 (product commit b3c18f38d1bdd10c8258fc1c69f0198b53cb2a4a; the evidence commit 405625e adds only docs/worklogs/SG-256_*.log).

Contract chain: repo AGENTS.md records 0.53.0; /home/andrei/storagegenie-contract/VERSION says 0.53.0; CODER.md line 3 verbatim: "**Contract version: 0.53.0** — **echo this line verbatim in your receipt.** It is the only proof that you". The local contract clone is at fa76c7c ("Contract payload 0.53.0") and still carries no contract-v0.53.0 tag (its tags stop at contract-v0.33.0), the same local tag gap SG-252/SG-255 reported, not a version mismatch.

(a) Issues / deviations / surprises

I1. G0 default docker path denied. The first call showed Client 29.9.2 but no Server section, and `docker run --rm busybox true` returned the verbatim "permission denied while trying to connect to the docker API at unix:///var/run/docker.sock", rc 1. With DOCKER_CONFIG=/tmp/opencode/sg256-docker and DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-256/docker.sock, `docker version` showed Server 29.9.2 and the run returned rc 0. The lane socket is exactly at the expected path. DOCKER_HOST was unset in the dispatch shell, as in SG-255. CLI environment only; no daemon restart, no alternate privileged route.

I2. PB-1 difference: the packet says the pre-change clear route is 404; the observed base response was 405 Method Not Allowed (the clear path has no route on base, and Starlette answers 405 rather than 404). The new tests still fail for the intended reason (no clear action); the FAIL log records 405. Finding, not an obstacle.

I3. The unchanged `_write_assertion` records the audit `before` as `{"field_path": "opened_date", "review_state": "superseded"}` because it flips the previous assertion to superseded before writing the audit row. The clear test asserts that observed value; the old date itself is preserved in the superseded assertion, which the same test asserts. Packet G1.3's do-not-change instruction was followed: `_accepted_opened_date` was read at backend/app/services/opened_countdown.py:49-72 and already returns None for a non-string JSON value; it and `_write_assertion` were not changed. `OpenedDateResponse` was not widened; the clear response has its own `OpenedDateClearResponse` type.

I4. Targeted lint (ruff on the three backend files, eslint on the four frontend files) is green and logged as extra evidence. Repo-wide lint was not run because the project records pre-existing mypy app reds in nine untouched files and one pre-existing eslint error in App.household-nav.test.tsx.

(b) Actions

Changed paths: backend/app/plugins/expiry_tracker.py, backend/app/api/v1/plugins.py, backend/tests/test_sg240_opened_countdown.py, frontend/src/api/client.ts, frontend/src/api/types.ts, frontend/src/components/OpenedCountdownSection.tsx, frontend/src/components/OpenedCountdownSection.test.tsx; evidence docs/worklogs/SG-256_g0_docker_preflight.log, SG-256_g3_backend_fail.log, SG-256_g3_backend_pass.log, SG-256_g3_frontend_fail.log, SG-256_g3_frontend_pass.log, SG-256_g4_backend_gate.log, SG-256_g4_frontend_gate.log, SG-256_health.log, SG-256_targeted_lint.log; this report. Work commit b3c18f3 (message "SG-256: clear an opened date through a null assertion; UI Edit/Clear"), evidence commit 405625e; pushed automation 4942b37..405625e. The report commit follows and is pushed separately; it adds only this report. The receipt note is added last to refs/notes/storagegenie-coder-reports; it moves no product branch (CO-86).

External effects: one git push of the two work commits; docker build/run through the lane socket built and tagged storagegenie-backend:prover (the prover tag only; the running container and its image tag were untouched); no database, provider, browser, host package, sudo, service or running-container action. Health start (before edits) and end (21:13:44Z): both http=200 {"status":"ok","db":"ok","storage":"ok"} -- HEALTH: unchanged, OK.

Commands: PATH=$PWD/backend/venv/bin:$PATH for every make invocation; venv pytest 9.1.1; node v24.14.1 / vitest 1.6.1. Test commands 7 (G3 four, host suite, image proof, frontend suite); retries 0; reruns 0; killed commands 0; provider calls 0; spend $0.

Durations (box clock, UTC): lane start 2026-10-28T21:06:58Z (epoch 1793221618); report composition begins 21:15:58Z (epoch 1793222158); elapsed 540 s against the ≈300 s expectation (+240 s, 80%). Phases over 60 s: the make backend-test target, which ran from 21:11:42Z to before the 21:13:44Z health check (its host-suite component 68.94 s; its other measured components: image frontend build 13.0 s, image export 10.6 s, image proof 1.87 s). Fast remainder, each under 60 s: preflight and base worktree setup, FAIL runs 4.31 s and 1.59 s, targeted PASS runs 4.24 s and 1.47 s, targeted lint, frontend suite 12.50 s, commits and report.

(c) Verification

A1 PASS -- the clear supersedes the old date and leaves one active null assertion; the countdown row has opened_date, days_open, days_remaining and window_end all null. Log: docs/worklogs/SG-256_g3_backend_pass.log, "21 passed, 2 warnings in 4.24s", rc 0. The four clear tests are the discriminating cases in docs/worklogs/SG-256_g3_backend_fail.log (base: "4 failed, 17 passed, 2 warnings in 4.31s", rc 1); the fifth new test (edit read-back) passes on base by design because the write path already supersedes (packet G1.4).

A2 PASS -- the clear route uses `_plugin`, `_asset` and the existing 422 mapping; the guard test observes 422 for a non-tracking category, 422 for an unclassified asset, 404 for an unknown asset and 403 for a household mismatch, and the dated asset remains accepted after the 403. Same pass log and count as A1.

A3 PASS -- the opened row shows Edit and Clear, not the no-date form; Edit pre-fills the current date, Save posts the new date and re-reads; Clear posts {} to the clear route, re-reads, and the row returns to "No opened date yet" with the input; the unopened row keeps the input and Save and shows no Edit/Clear. Log: docs/worklogs/SG-256_g3_frontend_pass.log, "8 passed (8)", rc 0. On base the same candidate test file gives "3 failed | 5 passed (8)" (the three controls/edit/clear cases), rc 1: docs/worklogs/SG-256_g3_frontend_fail.log.

A4 PASS -- FAIL-then-PASS logs are committed (paths above). `make backend-test` once: host suite "748 passed, 2 deselected, 48 warnings in 68.94s (0:01:08)", image proof "2 passed, 6 deselected in 1.87s", rc 0; the base was 743 passed (docs/worklogs/SG-255_g3_gate_pass_1.log), so the five new host tests are among the passes, the two marked tests stay deselected in the host suite and pass in the image proof, and no red is present. Log: docs/worklogs/SG-256_g4_backend_gate.log. `make frontend-test` once: "Test Files 30 passed (30)", "Tests 310 passed (310)", 12.50 s, rc 0. Log: docs/worklogs/SG-256_g4_frontend_gate.log.

A5 PASS -- product scope is exactly the seven named files (git diff --stat 4942b37..b3c18f3: 7 files, 429 insertions, 1 deletion); evidence is docs/worklogs/SG-256_* only. No schema, migration, backend/app/models/**, Dockerfile, compose, requirements.lock, dependency, model, database, host package, provider, running-container or deploy byte. The only external artifact is the prover image tag written by the existing gate.

A6 PASS -- docker preflight before the gate: Server 29.9.2 present and `docker run --rm busybox true` rc 0 (docs/worklogs/SG-256_g0_docker_preflight.log); health 200 at start and end with the identical body (docs/worklogs/SG-256_health.log).

A7 PASS -- vacuity check. If clear had not superseded, the old date would still be the active accepted assertion and the null countdown test would fail; observed: old date superseded, one active null assertion, countdown all null. If the no-op had written, the opened-assertion count (0) or the total audit count would rise; observed: unchanged. If the UI lacked the controls, the Edit/Clear tests would fail; observed: they failed on base and pass on candidate. If a suite were red or a gate skipped, rc would be nonzero or the counts absent; observed: both rc 0 with printed counts, and the two marked tests ran in the image proof. None of the failure shapes is the observed result.

A8 PASS -- last line.

INTENT: clear code writes a null active accepted opened_date through `_write_assertion`, supersedes the old date, writes the same audit row, and returns None only when no active accepted assertion exists; the check expects exactly that and the countdown nulls; the packet G1/A1 says the same. Route code adds POST /opened/clear with the existing guards and `{asset_id, assertion}`; the check expects 200/422/404/403 and null for the no-op; the packet G1/G2/A2 says the same. UI code shows Edit and Clear only on a dated row, Save reuses recordOpenedDate, Clear uses clearOpenedDate, both invalidate ["opened-countdown", householdId]; the check expects the controls only on dated rows and the row returning to the form after clear; the packet G2/A3 says the same.

TWINS: none; this is a feature, not a defect fix (CO-17).

Skipped as unnecessary: browser check (no rendered-surface claim; the component test drives the real controls); frontend production build (the suite is the packet's gate; packet says no build beyond it); provider call (none in scope, $0); database open (tests use temporary SQLite files); restart/deploy (packet forbids; the deploy rider SG-257 is separate); default DOCKER_CONFIG probe was not skipped -- it was tried first and failed as I1 records.

UNCLEAR
FIRST READ: the packet's base-FAIL note expected 404 from the absent clear route; the observed base answer was 405, recorded as I2. The route is absent either way, so the discriminating test outcome is unchanged.
DURING EXECUTION: why Starlette answers 405 rather than 404 for the extra path segment was not investigated further; the test failure is the same and the base route inventory is the packet's premise. Labelled inference, not a measurement.
REMAINING: no open product item for this slice. The root-owned ~/.docker remains pending in the engine arc, so DOCKER_CONFIG and an explicit DOCKER_HOST remain required; the live container is untouched and the deploy rider is SG-257.

Verification: PASS
