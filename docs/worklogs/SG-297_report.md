# SG-297 report — full gate on SG-272 (STOP at backend suite: two reds need out-of-scope changes)

SG-297 | model opencode-go/claude-haiku-5-5 effort high (read from process arguments: `--model opencode-go/claude-haiku-5-5 --variant high`) | cwd /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie | BASE ref origin/automation | resolved BASE commit e845baf08fa3569a8b1645373f01c6bd7c867f66 | WORK_HEAD 04ab2f0691182a6b3ab705c4c5d3276cf05a00b6 (product fix + tests + gate logs; the report commit is quoted in the receipt).

**Outcome: STOP at G2 step 3.** I2 and I3 are fixed and proven FAIL-then-PASS. ruff, eslint, tsc and the frontend build are green. `make backend-test` is red on two causes that need files outside this slice's scope or a choice the owner must make. Per the packet, the gate stops there: steps 4 and 5 and the image proof were not run. No deploy, no restart, no live database, no stored files, no provider.

## Elapsed

Not measured by a clock in this run (UNVERIFIED). Estimate: over the ≈500 s expectation. Phases over 60 s: the host suite run (`make backend-test`, pytest 78.14 s), and the SG-136 and plugin diagnosis (several pytest runs, base and candidate).

## Preflight (G0)

- `docker version` shows a Server section (Engine 29.9.2) with `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-297/docker.sock`, `DOCKER_CONFIG=/tmp/opencode/sg297-dockercfg`; `docker run --rm busybox true` rc 0.
- `backend/venv/bin/python` is present (symlink to `/usr/bin/python3`); `ruff 0.16.5`, SQLAlchemy 2.0.52.
- Health `curl -s http://127.0.0.1:8003/v1/health`: 200 at start, 200 at end.
- Git: `origin/automation` = `e845baf` = local HEAD at start; `391e6c8` (SG-272 base) and `3dcfd82` (SG-272 report) present; worktree clean at start.

## G1 — I2 and I3

- **Facts established:** `ReviewTask` has no `subject_kind` column; the kind is derived after the page by a batched lookup. `subject_ref` is one id column; candidate and asset ids are separate uuid7 namespaces (`enrich.py` creates candidates with their own ids). So `subject_ref NOT IN (SELECT asset.id WHERE household AND NOT ACTIVE)` hides only gone-asset subjects; candidate-subject tasks are unaffected.
- **Fix:** `review_tasks.py` gets `_visible_tasks(db, household_id)`, which applies the gone filter in the query with `lifecycle.active_clause()` (no status literal; the only `ACTIVE` left is in the docstring). The list and `total` both use it. The post-page list comprehension is removed. A page now holds its full limit of visible tasks and the cursor is correct.
- **Test:** `test_sg297_gone_task_hidden_before_pagination` in `backend/tests/test_sg272_flow.py`: gone subject's task sits among the first N; page 1 must hold 2 visible tasks, `total` must be 3, page 2 must return the remaining visible task, and the gone task must not appear in either page.
- **FAIL on the pre-fix code:** `docs/worklogs/SG-297_fail_tasks.log`: `1 failed` (page 1 returned one visible task; first assertion `['…'] == ['…']`, right side has one more item).
- **PASS after the fix:** `docs/worklogs/SG-297_pass_tasks.log`: `1 passed`.

## G2 — the full gate, in order

1. **ruff** (8 changed backend files from `git diff --name-only 391e6c8..HEAD -- backend/`, plus the two files edited here): first run rc 1, `C901 list_assets is too complex (11 > 10)` at `backend/app/api/v1/assets.py:286`. The base `391e6c8` passes ruff on that file, so this was SG-272's. Fixed (see R1). Re-run: rc 0, "All checks passed!" (`docs/worklogs/SG-297_ruff.log`).
2. **eslint** on the 12 changed frontend files (`docs/worklogs/SG-297_eslint.log`): rc 0, no output. **tsc --noEmit** (`SG-297_tsc.log`): rc 0. **Frontend build** (`tsc` + `vite build`, written to a scratch `outDir` so `frontend/dist` on the host was not overwritten; the scratch copy was removed): rc 0, built in 2.61 s (`SG-297_build.log`).
3. **make backend-test**: rc 2. pytest: **4 failed, 796 passed, 2 deselected** in 78.14 s (`SG-297_backend-test.log`). make stops on the failing host suite, so the **image proof did not run**.
4. **make frontend-test**: NOT RUN (stop).
5. **SG-272 and SG-297 test files twice**: NOT RUN (stop).

## Reds found and what was done

**R1 — ruff C901 on `list_assets` (fixed here).** The gone-reason batch lookup was inline in `list_assets`, which pushed its complexity to 11. Fix: the same code moved verbatim into `_gone_reasons(db, asset_ids)` in `assets.py`; the call site is one line. Behaviour is unchanged. Re-run ruff is green.

**R2 — `backend/tests/test_plugin_expiry.py::test_clear_expiry_date_supersedes_and_resolves_the_manual_task` (STOP).** Fails at `test_plugin_expiry.py:905`: `assert all(row["asset_id"] != asset.id for row in status["unresolved_rows"])`. The test asserts the SG-271 G5 rule (a cleared date is off the unresolved list and counted quietly). SG-272 G0b I1 deliberately changed that: a cleared perishable date now lists as "No date" (`test_sg272_flow.py::test_cleared_perishable_date_lists_as_no_date` asserts this and `summary.dateless == 0`, while this test asserts `summary.dateless == 1`). The two expectations cannot both hold. D443: run alone on base `391e6c8`, this test **passes** there, so SG-272 caused it. A fix needs either editing `test_plugin_expiry.py` (out of scope) or reverting SG-272 I1 (a product-behaviour change). **Owner decision.**

**R3 — `backend/tests/test_sg136_assertion_batch.py` (STOP).** Run alone on the candidate: **3 failed, 1 passed** (`test_assertion_select_count_constant_in_k`, `test_lazy_per_asset_access_is_the_n_plus_one`, `test_output_is_byte_identical_to_prechange_baseline`; the empty-world test passes). Run alone on base `391e6c8`: **all 4 pass**, so SG-272 caused them. Root cause, read from the code:
- `assets.py:184`: `_asset_to_dict` calls `get_gone_reason(db, asset.id)` for every asset, one extra assertion SELECT per asset. That is the N+1 SG-136 forbids (`k=3 issued 4 assertion SELECTs`, expected 1; lazy `saw 12`, expected 6).
- The byte-identical test fails on the new `gone_reason` key in the detail output (`{'gone_reason': None}`). That key is SG-272's deliberate API addition, and the fixture `tests/fixtures/sg136_asset_dict_baseline.json` predates it.

Not fixed here. The byte-identical failure can only be cleared by removing the key (changes SG-272's API) or by editing the baseline fixture and SG-136 test (out of scope). The SELECT part could be batched inside `assets.py` by reading the already-loaded assertions, but the module stays red regardless and whether `gone_reason` stays on the detail payload is a design decision for the owner, so I did not change the serializer on this STOP path. **Owner decision.**

## Changed files (commit `04ab2f0`)

- `backend/app/api/v1/review_tasks.py` — I2/I3: `_visible_tasks` used for page and `total`; post-page filter removed.
- `backend/app/api/v1/assets.py` — R1 only: `_gone_reasons` extracted from `list_assets`; behaviour unchanged.
- `backend/tests/test_sg272_flow.py` — new test `test_sg297_gone_task_hidden_before_pagination`.
- `docs/worklogs/SG-297_{fail_tasks,pass_tasks,ruff,eslint,tsc,build,backend-test}.log`, this report.

Scratch `output/SG-297-scratch/` (build outDir, base extraction for D443) removed by exact path. `output/` itself and `output/dispatch` not touched.

## Contract

Rule-set version recorded here: `0.58.0` (`AGENTS.md`, as received). The contract folder was not read.

## UNCLEAR / REMAINING

- REMAINING: `make backend-test-image` (image proof) not run (stop at host suite).
- REMAINING: `make frontend-test` not run (stop).
- REMAINING: SG-272/SG-297 test files twice-consecutive not run (stop).
- REMAINING (owner): R2 and R3 need a decision (see above).
- UNCLEAR: elapsed time not clock-measured.
- UNCLEAR: no test covers "candidate-subject tasks unaffected"; the claim rests on the id-namespace fact above.

## Constraints

- A1 — met: I2 filter in the query before pagination; page full; `total` excludes hidden; FAIL and PASS logs; I3 uses `lifecycle.active_clause()`, no status literal.
- A2 — met: ruff clean on changed backend files; eslint rc 0 on 12 files; tsc rc 0; build rc 0.
- A3 — NOT met: backend host suite 4 failed (R2, R3); image proof not run; frontend suite not run.
- A4 — NOT met: twice-consecutive run not reached.
- A5 — met: R1 fixed with reason; R2 and R3 are STOPs with failing names and first assertions.
- A6 — met: no schema, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored file, host, provider, running container or deploy bytes changed. `frontend/dist` not touched. The test suites use their own temp databases (the sg136 module sets `DATABASE_URL` to a temp path at import); I did not separately audit every test fixture for live-database access.
- A7 — met: preflight proven; health 200 at start and end.
- A8 — vacuity: short page (observed on the pre-fix run, absent after the fix); `total` counting hidden tasks (not separately observed: the FAIL run stopped at the first assertion); lint error (observed C901, fixed, now clean); red suite rows (observed, 4 failed, listed); pass-once-fail-second (not checked, step 5 not run).
- A9 — see last line.

Verification: FAIL — full gate stopped at backend suite: R2 test_plugin_expiry.py:905 (SG-272 I1 vs SG-271 G5) and R3 test_sg136_assertion_batch.py (SG-272 gone_reason in _asset_to_dict); image proof, frontend suite and twice-run not run
