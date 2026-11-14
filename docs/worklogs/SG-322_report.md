SG-322 | model/effort: not visible in process arguments (not inferred) | cwd /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation, resolved 31eeac4 (packet named 17cf09e, an ancestor; `git diff --stat 17cf09e 00a1457 -- backend/app frontend/src` is empty, so product code is identical) | WORK_HEAD e733b7c (last code commit; the report commit is named in the publish output)

Contract line: none received. (I did not read the contract folder and did not echo any version line from AGENTS.md.)

Elapsed: 407 s at report draft (start 1794686358). Phases (epoch stamps from `date +%s`):
- G0 preflight: 1 s (docker server up, `busybox true` rc 0, health 200 at start and 200 at end, 1794686764)
- G0 rescue commit 83a5eb5: ~8 s
- G1 analysis (reads): ~5 s
- G2 backend test file, commit 00a1457, FAIL run on pre-fix tree: 1794686441 -> 1794686449
- G1 fix, commit 10bb024, PASS run: 1794686458 -> 1794686463
- G2 frontend test, commit e733b7c, run: 1794686483 -> 1794686508
- eslint + tsc + build into scratch: 1794686514 -> 1794686527
- make backend-test: 1794686531 -> 1794686649 (118 s)
- make frontend-test: 1794686652 -> 1794686674 (22 s)
- named files twice: 1794686680 -> 1794686706 (26 s)
- cleanup and verification: 1794686725 -> 1794686765

## A1 — G0 preflight and SG-321 rescue
- Preflight: `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-322/docker.sock`, socket present (srw-rw---T andrei). `docker version` printed a Server section (Engine 29.9.2), rc 0. `docker run --rm busybox true` rc 0. Health `curl ... /v1/health` = 200 at start and 200 at end.
- Rescue: `git cat-file -t 2fcc629` printed `commit` (the commit exists; it is not an ancestor of origin/automation). Checked out only `docs/worklogs/SG-321_report.md` and `docs/worklogs/SG-304_shots` from it, committed as 83a5eb5 "SG-321 evidence (rescued by SG-322; its push was refused)". 12 files, 436 insertions, the same 12 files the commit held (`git show --stat 2fcc629`). Nothing else from that commit.

## A2 — G1: cause, condition, callers
- Premise CONFIRMED. `backend/app/services/candidates.py` (pre-fix, `committed_asset_id`, lines 1015-1027) took its first hop from `proposal.get("asset_id")` with no check on `candidate.state`. A duplicate proposal carries the matched item in `asset_id` (`backend/app/services/dedup.py:213`, `proposal["asset_id"] = asset_id`), so an open duplicate read returned the matched item.
- Frontend: `frontend/src/routes/ReviewPage.tsx:100`: `candidate && candidate.asset_id ?` selects the *In your catalog* branch. SG-304's test used `asset_id: null` (`frontend/src/routes/ReviewPage.sg304.test.tsx:19`), which is why it passed.
- Condition named: `DECIDED_CANDIDATE_STATES = frozenset({"accepted", "edited"})` (`backend/app/services/candidates.py:1018`). The first hop runs only when `candidate.state in DECIDED_CANDIDATE_STATES` (line 1032). Decided means accepted (same pack and another pack both set `accepted`, see `api/v1/candidates.py` decision path) or edited. Open (`proposed`), `held`, `rejected`, `split`, `merged` do not take the first hop. SG-271 (a decided candidate shows In your catalog) and the SG-270 / SG-275 hops are unchanged.
- Fix placement: `committed_asset_id` itself, because all callers share it and the rule belongs at the read.
- Callers checked (grep quoted, run after the fix): `grep -rn "committed_asset_id" backend/ --include=*.py` gives `candidates.py:1021` (definition), `api/v1/jobs.py:170` (Inbox list, `_candidate_list_item`), `api/v1/candidates.py:275` (GET candidate, the ReviewPage read). No other caller.
- Falsified part: the packet's case (4), *another pack* -> the new item, already held on base. On base the four cases same pack, another pack, Inbox same, Inbox another all passed. Only open and held (and the Inbox open read) failed.

## A3 — G2 FAIL on base, PASS on candidate
- Backend FAIL, `docs/worklogs/SG-322_fail.log` (pre-fix tree, product code = 17cf09e): 3 failed, 4 passed, 7 total.
  - FAILED test_open_duplicate_reads_with_no_asset_id: read asset_id `01a1dba5-ebe5-7f52-8ea5-c8275b87c87f` is not None (this is the existing item id).
  - FAILED test_held_duplicate_reads_with_no_asset_id: read asset_id `01a1dba5-ed29-7fb3-a065-274f7dec26c4` is not None.
  - FAILED test_inbox_read_agrees_with_the_candidate_read[open]: `01a1dba5-f075-7f43-bd3d-b48d6719d209 == None` failed (Inbox read carried the existing item).
- Backend PASS on candidate, `docs/worklogs/SG-322_pass.log`: 7 passed (names only).
- The five backend cases:
  1. open: asset_id None, state `proposed`, duplicate_of_asset match id == target. PASS. (Base read value: target id, see above.)
  2. held: asset_id None, state `held`, match id == target. PASS. (Base read value: target id.)
  3. same pack: asset_id == existing item id, state `accepted`, status `duplicate_linked`. PASS.
  4. another pack: asset_id == new item id (decided["asset_id"]), not target; status `committed`, created True. PASS.
  5. Inbox (`GET /v1/jobs/{id}/candidates`) agrees with the candidate read for open, same, another: three parametrized cases. PASS.
  Caveat: the raw asset_id values for cases 2-5 on the candidate tree were not logged; those asserts compare equality and passed. Only the base failure values above are recorded.
- Frontend `ReviewPage.sg322.test.tsx`: 2 passed on the current tree (`docs/worklogs/SG-322_frontend_sg322.log`: "Tests 2 passed (2)"). The frontend product tree is unchanged from base, so this run is also the base result. It cannot FAIL on base: no frontend product file may change (scope ceiling), and the defect is in the API read, which the frontend test feeds the correct shapes. It is a regression guard, not a FAIL-then-PASS proof. Fixtures use the keys `GET /v1/candidates/{id}` returns (`api/v1/candidates.py:277-288`) and the match fields the page reads (`type`, `asset_id`, from `CandidateCard.tsx:31-94`). I did not capture a live JSON response; the match dict has more keys in `dedup.py`, and only the keys the page reads are in the fixture.
- Ordering: the G1 analysis came first, then the test file, then the FAIL run on the pre-fix tree, then the edit. The edit follows the FAIL evidence, as the packet's "FAIL on base, PASS on candidate" needs.

## A4 — gate (exact counts)
- `eslint src`: 1 problem, the known `App.household-nav.test.tsx:2:10` ('fireEvent' is defined but never used). Nothing else. rc 1 (known only).
- `tsc --noEmit`: rc 0.
- `vite build --outDir <scratch build> --emptyOutDir`: rc 0, "built in 3.18s". Output in scratch only.
- `make backend-test`: host suite `817 passed, 2 deselected` rc 0; image proof `2 passed, 6 deselected` rc 0 (docker build of backend/Dockerfile, run with --network none).
- `make frontend-test`: `Test Files 59 passed (59)`, `Tests 495 passed (495)`, rc 0. 0 failed.
- Named files, run twice each: backend `tests/test_sg322_*.py tests/test_sg304_*.py tests/test_sg271_*.py`: 19 passed, rc 0, twice. Frontend `vitest run sg322 sg304 sg271`: 9 files, 27 tests passed, rc 0, twice.
- Older tests broken by the fix: none. Full suites green. No older test changed, none loosened.

## A5 — scope and bytes
- No migration. `git diff --name-only 17cf09e HEAD` contains no Dockerfile, compose, lockfile, `.env`, migration, `frontend/dist` or `output/` path.
- Product files changed by this slice: `backend/app/services/candidates.py` only (commit 10bb024, 12 insertions, 4 deletions). No frontend product file.
- New test files: `backend/tests/test_sg322_duplicate_read.py`, `frontend/src/routes/ReviewPage.sg322.test.tsx`.
- `frontend/dist` untouched (mtime 2026-11-09; the build wrote to scratch).
- No live database read or write, no provider, no key, no container other than the authorized image proof, no deploy, no server started.
- Scratch `output/SG-322-scratch` removed before the report; `output/dispatch` left as found.
- DEVIATION, not reversed: `/tmp` was written. pytest's default temp root `/tmp/pytest-of-andrei` (dirs `pytest-2`, `pytest-3`, `pytest-4`) was used by the backend runs because I did not set `--basetemp`. I did not remove it; it is pytest's own folder and holds earlier runs too.
- Also not used: `python` and `npx` are not on the shell PATH. I used `backend/venv/bin/python` and `frontend/node_modules/.bin/*` directly, and ran `make` with the venv on PATH.
- Tree: only `docs/worklogs/SG-322*` files are new (committed with this report).

## A6 — PB-3 vacuity: what I checked
- Open duplicate still carrying asset_id: checked, base run shows it (FAIL), candidate run clean (PASS).
- Decided duplicate losing asset_id: checked, cases 3 and 5-same PASS with asset_id == target.
- Another pack pointing at the old item: checked, case 4 asserts asset_id != target and == decided["asset_id"]. Passed on base too (so the packet's failure mode was not present on base).
- Inbox disagreeing with the candidate read: checked, parametrized case 5.
- Frontend test fed a hand-made shape: fixtures follow the endpoint's key list; not a live capture (see A3). Stated, not hidden.
- A test passing on base: the frontend test does (by design, see A3). The backend open/held cases do not pass on base.
- A red suite: none; host 817 green, frontend 495 green.

## A7
Verification: PASS

## Changed files (this slice)
- backend/app/services/candidates.py (10bb024)
- backend/tests/test_sg322_duplicate_read.py (00a1457)
- frontend/src/routes/ReviewPage.sg322.test.tsx (e733b7c)
- docs/worklogs/SG-321_report.md, docs/worklogs/SG-304_shots/* (rescue, 83a5eb5)
- docs/worklogs/SG-322_{fail,pass,lint,tsc,build,backend,frontend,frontend_sg322,named_backend_x1,named_backend_x2,named_frontend_x1,named_frontend_x2}.log, docs/worklogs/SG-322_report.md (this commit)
- Not this slice, inherited from origin/automation commit 31eeac4: AGENTS.md, STATE.md, docs/packets/SG-322-duplicate-card-reachable.md, docs/worklogs/SG-304r2_audit.md.

## UNCLEAR / REMAINING
- Frontend FAIL-on-base is not achievable under the scope ceiling (no frontend product change). The frontend test is a regression guard; it passes on base by design.
- Raw asset_id values for backend cases 2-5 on the candidate tree were not logged; only the base failure values are recorded (see A3).
- Rejected duplicates: now read with asset_id None (before, the matched item). The card then shows decision buttons for a rejected candidate; `api/v1/candidates.py` returns 409 "Candidate is rejected" on a decision. This is the same as any rejected non-duplicate candidate before this change. Not tested; flagged for the owner.
- Held after accepted: the decision path lets an accepted candidate be held (only rejected, split, merged return 409). A held candidate that was committed still reads its item through the SG-270/SG-275 hops, which the packet keeps unchanged. Not tested.
- `edited` counts as decided (in DECIDED_CANDIDATE_STATES); no test exercises the edit path directly.
- `/tmp/pytest-of-andrei` written by pytest's default basetemp (see A5 deviation).
- Model/effort not visible in process arguments; not inferred.
- BASE: the packet named 17cf09e; the BASE ref origin/automation resolved to 31eeac4 from the local remote-tracking ref (not fetched at the start). Product code is identical between them (see header).
- Ruff and mypy were not run (not in the gate list).
- The publish sequence was run after this report commit; see the publish output for the push results.
