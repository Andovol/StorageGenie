# SG-298 — Fix SG-272's two gate reds (a stale oracle and a per-item query), then run the full gate to the end

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** No deploy; the rider follows this slice.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.58.0` (`AGENTS.md`). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line as you received it. A denial on that folder is expected and is not a STOP.

**Approval:** owner, stage C (*"d14 ok"*, L3), and *"Start SG-272"* (2026-11-09). This finishes SG-272's gate.

## Why this exists

SG-297 (`e845baf..dd9b1b6`, report `docs/worklogs/SG-297_report.md`) fixed the task-list paging (I2, I3) and stopped, correctly, at `make backend-test`: **4 failed, 796 passed, 2 deselected**. Both causes are SG-272's and were proven so by running each test alone on `391e6c8` (it passes there). The audit (`docs/worklogs/SG-297_audit.md`) decided both; **neither is an owner decision**:

- **R2 — a stale oracle.** `backend/tests/test_plugin_expiry.py::test_clear_expiry_date_supersedes_and_resolves_the_manual_task`, lines ~903–906, asserts SG-271 G5's rule: a cleared date is off `unresolved_rows` and `summary.dateless == 1`. SG-271's audit called that a defect (a cleared milk date vanished from Unresolved), and SG-272 G0b changed it on purpose: a cleared **perishable** date lists on Unresolved as *No date* (reason `dateless`), and only a Non-perishable item is counted quietly. `test_sg272_flow.py::test_cleared_perishable_date_lists_as_no_date` asserts the new rule.
- **R3 — a per-item query plus a stale baseline.** `backend/app/api/v1/assets.py` `_asset_to_dict` (~`:184`) calls `get_gone_reason(db, asset.id)` (`backend/app/services/asset_service.py:209`) for every asset — one extra assertion SELECT per asset, the N+1 `backend/tests/test_sg136_assertion_batch.py` forbids (*"k=3 issued 4 assertion SELECTs"*, expected 1; lazy *"saw 12"*, expected 6). It sits in a bare `except Exception` that turns any failure into `None`. `gone_reason` on the detail payload is SG-272's specified read-back, so it **stays**; the baseline `backend/tests/fixtures/sg136_asset_dict_baseline.json` predates it.

**What SG-272 changed on purpose** — an old test asserting the **old** side of any of these is a stale oracle: update it in this slice, name it in the report, and say which line below it follows. Anything not on this list that turns red is a STOP.

1. A cleared perishable expiry date lists on Unresolved as *No date*; only Non-perishable is counted quietly (`expiry_engine.py`).
2. `ARCHIVED → ACTIVE` is allowed (put back) (`lifecycle.py`; `test_sg111_lifecycle.py` already updated).
3. The reminders list admits ACTIVE assets only (`reminders.py`).
4. Open review tasks of a non-ACTIVE asset are hidden from the list and from `total` (`review_tasks.py`, as SG-297 fixed it).
5. List and detail asset payloads carry `gone_reason` (`assets.py`).
6. Dedicated routes for gone, put back, decrement, increment (`assets.py`, `asset_service.py`).

**RETRY — the one retry this slice gets.** Run 1 stopped as BLOCKED in G0 because it set `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-298.sock` — **not the path this packet names**: the socket is the file `docker.sock` **inside the directory** `/run/dispatch-storagegenie-SG-298/`. SG-297 reached the daemon with the same pattern. Its report also said it used the "exact packet values"; it did not. **This run copies the commands below verbatim**, and before any docker call prints `echo "$DOCKER_HOST"` and `ls -l /run/dispatch-storagegenie-SG-298/` into the log. Only if `docker version` still has no Server section **with the exact string below** is it a BLOCKED STOP. Write this run's report to `docs/worklogs/SG-298_report.md`, replacing run 1's, and keep run 1's text under `## Run 1 (stopped in G0, wrong socket path)` at the end.

## G0 — Preflight

Copy these lines exactly:

```
mkdir -p output/SG-298-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-298-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-298/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-298/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and `docker run --rm busybox true` is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make and `ruff` call; if the venv `python` is missing, report the exact error and STOP — install nothing. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch only in `output/SG-298-scratch/`, removed by that exact path; never touch `output/` itself or `output/dispatch`. **Run `date +%s` at the start of every goal and gate step and quote the stamps** — the report computes each phase's seconds from them.

## G1 — R3: the gone reason without a per-item query

- `_asset_to_dict` takes the gone reason from **the assertions already loaded on the asset** (`asset.assertions`, the relationship SG-136 reads), using the same rule as `get_gone_reason`: field `GONE_REASON_FIELD`, `review_state == "accepted"`, the latest by `created_at`, `value.reason` if it is a non-empty string, else `None`. **Establish** (`PB-1`) that `asset.assertions` holds every review state and that `get_gone_reason`'s ordering matches; if the relationship is filtered or ordered differently, say how and handle it.
- **No bare `except`.** A malformed value gives `None` by the same checks `get_gone_reason` makes, nothing broader.
- **Behaviour rail:** for every asset in `test_sg272_flow.py`'s gone and put-back cases, the serializer's `gone_reason` equals `get_gone_reason(db, id)`. Add that assertion to `test_sg272_flow.py`. `get_gone_reason` stays for its other caller (`asset_service.py:~249`).
- **Baseline:** in `sg136_asset_dict_baseline.json`, add only the `gone_reason` key per asset, with the value the serializer now gives. **The fixture's diff must be exactly those added keys**; any other changed byte is a STOP.
- `test_sg136_assertion_batch.py`: 4 of 4 pass, quoted. Its FAIL half is SG-297's log (`docs/worklogs/SG-297_backend-test.log`); do not re-run it on the base.

## G2 — R2: the stale oracle

- Update `test_plugin_expiry.py` lines ~903–906 to rule 1 above: the cleared item **is** in `unresolved_rows` with reason `dateless`, and `summary.dateless == 0`. **Establish** first that the test's asset is perishable (not classified Non-perishable); if it is Non-perishable, the old assertion was right and this is a STOP.
- Fix the comment to say SG-272 G0b superseded SG-271 G5.
- The test passes; quote it.

## G3 — the candidate-subject case (SG-297's UNCLEAR)

One test in `test_sg272_flow.py`: a household with one candidate-subject task and one gone asset's task; the list returns the candidate's task and `total` counts it. SG-297 found candidate and asset ids are separate uuid7 namespaces and `ReviewTask` has no `subject_kind` column — confirm, and if a candidate id can equal an asset id, say so and STOP. This test protects existing behaviour, so it passes on the base too; say so, and show it **fails** with `_visible_tasks` mutated to keep only tasks whose `subject_ref` is an ACTIVE asset id — the plausible wrong filter, which would hide candidate tasks (revert the mutation by exact edit, show the diff is clean).

## G4 — The full gate, once, on the candidate

**This runs before the report and is never dropped.** In this order, exact counts (`PG-IC-08`), each into `docs/worklogs/SG-298_<step>.log`:

1. `ruff check` on every backend file in `git diff --name-only 391e6c8..HEAD -- backend/` (`PG-EV-15`).
2. `eslint` on every frontend file in `git diff --name-only 391e6c8..HEAD -- frontend/`; `tsc --noEmit`; the frontend build with `outDir` in scratch so `frontend/dist` is untouched (`PG-SC-12`). The pre-existing `eslint` error in `App.household-nav.test.tsx` and the repo-wide mypy reds are out of scope.
3. `make backend-test` once — host suite green, the two marked tests deselected, **and the image proof run and passing**.
4. `make frontend-test` once.
5. Every SG-272, SG-297 and SG-298 test file **twice consecutively** (`PG-DP-04`): `backend/tests/test_sg272_flow.py`, `backend/tests/test_sg136_assertion_batch.py`, `backend/tests/test_plugin_expiry.py`, and the four `frontend/src/**/*.sg272.test.tsx` files.

**A red is fixed here only if** the fix stays in the scope below, does not change what SG-272 does on screen or in the API, and is either a defect in SG-272's code or a stale oracle under lines 1–6. Re-run that step and say what changed and why. **Anything else is a STOP and report** with the failing test names and first assertion; stopping there is a success. An old test failing on the candidate is run alone on `391e6c8` (`D443`) and the report says whether it fails there. **Keep logs short:** a FAIL log holds the failing test names and first assertion only.

## Acceptance criteria

- **A1** — R3: no per-asset gone-reason SELECT; `test_sg136_assertion_batch.py` 4/4; the rail assertion passes; fixture diff is exactly the added keys (quote `git diff --stat` and one hunk); no bare `except`.
- **A2** — R2: the test asserts rule 1 and passes; the asset proven perishable.
- **A3** — G3 test passes, and fails under the named mutation; mutation reverted, diff shown clean.
- **A4** — ruff, eslint, tsc clean on the named files; build rc 0.
- **A5** — Backend suite green (counts), image proof passing, frontend suite green (counts).
- **A6** — The named files green twice consecutively, both counts quoted.
- **A7** — Every red fixed is named with its reason and which line 1–6 it follows, or a STOP with names.
- **A8** — Scope only as below; zero schema, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes; `frontend/dist` untouched.
- **A9** — Preflight proven; health 200 at start and end; phase seconds from the `date +%s` stamps.
- **A10** — `PB-3` vacuity: a failure would look like a SELECT count above 1, a fixture diff touching other keys, a `gone_reason` differing from `get_gone_reason`, a cleared perishable missing from Unresolved, a mutation that does not fail G3, a red suite row, a test that passes once and fails the second time. Say which you checked; none observed.
- **A11** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product file:** `backend/app/api/v1/assets.py`. Other SG-272 product files (`git diff --name-only 391e6c8..3dcfd82`, excluding `docs/`) only for a G4 red as G4 allows.
- **Tests:** `backend/tests/test_sg272_flow.py`, `backend/tests/test_plugin_expiry.py` (the R2 lines only, plus any other stale oracle under lines 1–6, each named), `backend/tests/fixtures/sg136_asset_dict_baseline.json` (added keys only), SG-272's `*.sg272.test.tsx` files. `test_sg136_assertion_batch.py` is **not** edited.
- **Any other product or test file is a STOP and report — do not change it** (`PG-EV-03`). Reads of any file are allowed.
- **Authorised runtimes:** the preflight, the `make` gates, the tests, `ruff`, `eslint`, `tsc`, the frontend build. **No browser, no local app server, no other image, no package install.**
- Evidence: `docs/worklogs/SG-298*` only. Test rows only in temporary databases (`PG-EV-06`). No deploy, no restart, no touch of the running container or its image tag, the live database or the stored files.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **300 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **At 1300 s elapsed by your `date +%s` stamps, stop whatever step you are in, commit, write the report, publish.** This is a stop rule, not a target. **There is no optional goal.** Order: G0, G1, G2, G3, G4 steps 1–5. Expected ≈650 s (`UNVERIFIED — my estimate`: SG-297 took ≈406 s for G0 to step 3; step 3 again plus the frontend suite and the twice-runs are not yet measured on this lane).

## Report

Destination: `docs/worklogs/SG-298_report.md`, evidence beside it. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: elapsed against ≈650 s and every phase's seconds from the stamps; each gate step's counts; every red and what was done; changed files; the contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint and criterion.

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-298`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-298 | Report: docs/worklogs/SG-298_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
