# SG-270 — Flow fixes: an imported item can always be reached, accepted and finished on its own page

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** This slice does not deploy; its rider does.
**Provider: none.** No key, no `.env`, no spend. AI journeys use the repo's `ScriptedPhase2Provider` (`backend/tests/test_phase2_e2e.py:187`).

**Contract chain:** recorded `0.56.0` (`AGENTS.md`) == published `contract-v0.56.0` == the host's contract, echoed by this report from `/home/andrei/storagegenie-contract/CODER.md` line 3. A different echo is a finding.

**Previous report's open items:** SG-269's audit I1 (is an AI-read item also unreachable?) is proved here. Its I2 (screens unseen) stays open: this slice has no browser, and screens are proved by component tests only. SG-262's audit I1 and I6 and `docs/backlog.md` W8 are built here.

## Why this exists

Stage C, the first real Pantry, was approved by the owner on 2026-11-02 (*"d14 ok"*). The read-only walk found imported items that get stuck for good. From `docs/worklogs/SG-269_findings.md`:

> **F1** The job reaches `AWAITING_REVIEW` and a candidate exists, but no screen lists it.
>
> **F2** The Inbox Resolve button sends a bare resolve, which is refused; Accept is refused while the task is open. There is no date field on the candidate review card and no candidate-level manual-date route.
>
> **F6** The task's subject is the asset id, but the Inbox labels it "candidate" and links to `/review/<asset-id>`; the Review page fetches `/v1/candidates/<asset-id>` and gets `404 Candidate not found`.

**The F2 design is chosen and not reopened** (blind review `docs/worklogs/SG-274_report.md`, which picked the same): **accept the candidate and carry the date task to the new item.** Accepting acknowledges the item; the date stays visibly owed and is entered on the item's page. A closed task never means a date was supplied.

## G0 — Docker preflight before any gate claim

`make backend-test` runs the image proof, so prove the lane runtime first. The default `/var/run/docker.sock` is expected to be denied: set `DOCKER_CONFIG` to a writable temp directory and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-270/docker.sock`; `docker version` must show a **Server** section, and `docker run --rm busybox true` must return **rc 0**. If either fails, **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`); do not restart the daemon, use another socket or sudo. Use `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation. Run `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. `/tmp` is denied on this lane: scratch goes in `output/SG-270-scratch/`, removed by exact path at the end; never touch `output/` itself or `output/dispatch`.

## G1 — F2: the date task stops blocking, and follows the item

Behaviour wanted:

- **An open `expiry.manual_entry` task on a candidate no longer blocks accept or edit.** Every other open task type still blocks, including `candidate.multi_item`. Name the exempt set once and use it at both backend gates.
- **On commit, in the same transaction as the asset, the task moves to the new asset:** `subject_ref` becomes the asset id, `proposed_change` takes the asset-side shape that `_manual_task` writes, identity and history are kept, and an audit row records the move. It then behaves as any asset date task: a manual date, a clear, or a move to a no-expiry category resolves it.
- **Write no expiry assertion at commit.** The asset may carry a `proposed` date from another field; a `{"status": "unknown"}` row would supersede it. So do not call `apply_extraction_result` here.
- **Hold** leaves the task as it is. **Reject** closes the candidate's open tasks with an audited resolution naming the rejection, never one claiming a date.
- **A duplicate candidate (`duplicate_of_asset`)** creates no asset. Check the target asset belongs to this household. If the target already has an accepted date or an accepted null, close the task with an audited resolution naming the target; otherwise move it to the target, joining an open date task already there rather than making a second.
- **Split:** the origin's date task is closed with an audited resolution naming the split, and each child whose proposal has `needs_evidence` true gets its own open date task, so the child's commit carries it. Children's tasks are in their `review_task_ids`.
- **Merge is unchanged.** A loser holding a date task still blocks (`backend/tests/test_sg112_merge.py:37` pins this). Accept is no longer blocked, so this is not a dead end.
- **Candidates already open on the live database** work without any data change: eligibility comes from live task rows, not from stored snapshots or the new producer output.
- **No new route, no new task type, no migration.**

Expected (each a hypothesis to falsify):

- Gates at `backend/app/api/v1/candidates.py:50-51` and `backend/app/services/candidates.py:969-979`.
- Producers of `expiry.manual_entry`: `candidates.py:757-769` and `backend/app/plugins/expiry_tracker.py:374-397`. **Enumerate them yourself** and report any difference.
- `classify_asset` reuses an open asset task through `_manual_task`; `store_manual_expiry` and `clear_expiry_date` filter on `subject_ref` = asset id, so a moved task needs no special handling there.
- Tests that may pin the old block, to change only as far as the new behaviour requires: `test_ai_pipeline.py`, `test_phase1_e2e.py`, `test_phase2_e2e.py`, `test_phase3_e2e.py`, `test_candidate_read.py`, `test_dedup.py`. **Several of these resolve the date task with a non-empty payload first. Do not change that endpoint** (`review_tasks.py:107-131`), and report which tests depend on it; `docs/backlog.md` W9 owns it.

**Establish and report, do not change:** what the provider's `needs_evidence` means. `candidates.py:757` opens a date task on that one global flag, while `schemas.py:140-145` ties it only to a non-empty `unknowns` list. If it can be true when the date is not the unknown, say so with the prompt's text; that is a false date task for a later slice.

## G2 — Accepting a child of a split must commit that child

**This may be a fourth dead end, found by reading only (`UNVERIFIED — my inference`).** `commit_job_candidate` (`candidates.py:993-998`) takes the job's first-created candidate, which after a split is the retired origin, and `commit_candidate` refuses a state that is not accepted or edited (`:967-968`). Children share the job (`:1165-1170`). So accepting a child may fail the job. A second child may then find every step complete (`backend/app/services/job_service.py:170-172`) and create nothing, silently.

**First drive it:** import a two-item photo through the scripted provider, split, accept each child, and log what happens. Then, if it fails:

- each accepted child creates its own asset, carrying its own date task;
- the commit uses the candidate that was decided (the review step's `output_refs` already records `candidate_id`: `api/v1/candidates.py:68-72`);
- accepting the same candidate twice creates one asset, never two;
- a single-candidate job behaves exactly as before.

If this needs more than `candidates.py`, `api/v1/candidates.py` and `job_service.py`, or a job state change you cannot make safely, **do not force it**: finish the rest, report the cause, and leave it for a named slice.

## G3 — F1: the Inbox lists a job's candidates

Under "Selected job" (`frontend/src/routes/InboxPage.tsx:40`), list the job's candidates from the existing `GET /v1/jobs/{id}/candidates` (`backend/app/api/v1/jobs.py:172`), each with its name, its state and a **Review** link. Retired split origins are labelled, not offered as work. Loading, empty and error states follow the page's existing ones.

**Prove audit I1:** drive an AI-read, dated item through the scripted provider and record whether it opens a task. Expected: none, so before this slice it was as unreachable as F1's. State the answer in the report.

## G4 — F6: date tasks lead somewhere true

- `GET /v1/review-tasks` (`backend/app/api/v1/review_tasks.py:37`) adds, per row, `subject_kind` (`candidate`, `asset` or `unknown`, looked up in one query per page, not one per row) and `data_required` (from `DATA_REQUIRED_TASK_TYPES`, so the rule keeps one owner). Existing fields are unchanged.
- The Inbox task row (`InboxPage.tsx:50`) says "item" or "candidate" truthfully, links an asset task to `/assets/<id>` (`frontend/src/App.tsx:181`) and a candidate task to `/review/<id>`, and links an `unknown` subject nowhere.
- **Resolve is hidden where `data_required` is true**; other task types keep it.
- **A task whose candidate was already rejected before this slice** is left as it is. Report what its row shows; the rider counts them on the live database.

## G5 — From review to the item

- Accept and edit responses carry `asset_id` (`frontend/src/api/client.ts:199-207`). After a decision that returns one, the review page shows a link to the item. For a duplicate, the link says it goes to the existing item.
- A decision also refreshes the review-tasks query (`frontend/src/routes/ReviewPage.tsx:42`), so the Inbox and its badge are right.
- **Accept is enabled for a date-only block**, on the button and on the keyboard (`frontend/src/components/CandidateCard.tsx:48`, `ReviewPage.tsx:49`). Add `blocking_review_task_ids` to the candidate read (live rows, excluding the exempt set; `backend/app/services/candidates.py:946-963` is the shape), and use it for both. `review_task_ids` keeps its meaning. When only a date is owed, the card says one plain line: the date can be added after accepting.
- **On the item's page, an unclassified item says what comes next:** choose a category, then add a date if it has one. The date form stays hidden until then (`frontend/src/routes/AssetDetailPage.tsx:540-550`). Do not add a date-only link that leads to a hidden form.
- Report what the review page shows when an accepted candidate is reloaded (the response's `asset_id` is gone by then). Do not build for it.

## G6 — Backlog W8

- A direct test of classify-to-food then classify-to-non-perishable through the real task writer, with no hand-planted task.
- `resolved_review_task_ids` in the classify type at `frontend/src/api/client.ts:264-270`.
- A split-origin date task **already open** when a child moves to a no-expiry category: resolve it with the existing `_orphan_manual_tasks` (`expiry_tracker.py:660-702`) and an audit row, matching `store_manual_expiry:736-755`.

## G7 — Tests and the gate

- New tests FAIL on the pre-change code and PASS on the candidate; commit both runs (`PG-EV-09`) as `docs/worklogs/SG-270_fail_*.log` and `SG-270_pass_*.log`. The base checkout uses the same temporary-SQLite settings; no secret file is copied (`PG-EV-13`).
- Drive tests through the real routes and real task writers, not planted rows, except for the pre-existing-row cases that need them. Shared fixtures: `backend/tests/test_phase2_e2e.py` and `backend/tests/test_review_split.py`, in scope only for what the new behaviour requires.
- The whole journey has one test: AI cannot read a date → candidate listed → accept → task now on the asset → classify to food → date entered → task resolved → the item on the Expiry page. A second covers shelf-stable: classify to non-perishable resolves the task. A third forces a failure inside the commit and shows neither asset nor moved task survives.
- First the targeted tests and `tsc`. Then grep for every test pinning the changed behaviour and fix those **before** the full gate.
- `make backend-test` once: the host suite green, the two marked tests still **deselected**, then the image proof. `make frontend-test` once. Quote exact counts (`PG-IC-08`).
- Run the affected test files **twice consecutively** (`PG-DP-04`). `ruff check` and `eslint` on **every changed or new file**; the repo-wide mypy reds and the one `eslint` error in `App.household-nav.test.tsx` are out of scope. Reconcile changed paths against the gate's paths (`PG-EV-15`). Prove the deploy's frontend build step exits 0 (`PG-SC-12`).
- **Order:** commit after G1, after G2 and after each later goal, with evidence, so a stop at the budget still ships finished goals.

## Acceptance criteria

- **A1** — A candidate with only a date task can be accepted and edited; `candidate.multi_item` still blocks; the moved task sits on the new asset; a manual date, a clear and a non-perishable move each resolve it; no expiry assertion is written at commit.
- **A2** — Hold, reject, duplicate (three target states), split and merge behave as G1 says, each with a test; audit rows name the real reason; no household crosses.
- **A3** — Every producer of `expiry.manual_entry` is enumerated, with the difference from this packet stated either way. `needs_evidence`'s meaning is reported.
- **A4** — The split journey's result is reported from a driven run: each child creates its own asset, or the cause and a named stop. Accepting twice creates one asset.
- **A5** — A selected job lists its candidates with working Review links. Audit I1 is answered from a driven run.
- **A6** — Asset tasks link to the item; candidate tasks link to review; Resolve is absent on data-required rows and present on others; existing response fields are unchanged.
- **A7** — After accept, a link to the item shows; Accept is enabled by button and keyboard for a date-only block and disabled for any other; the unclassified item says what comes next.
- **A8** — W8's three items are done.
- **A9** — FAIL-then-PASS with both logs committed; host suite, image proof and frontend suite green; affected files run twice; build rc 0; counts quoted.
- **A10** — Scope is only the files below; zero schema, migration, Dockerfile, compose, lockfile, dependency, model, database, host, provider, running-container or deploy bytes.
- **A11** — Docker preflight proven before the gate; health 200 at start and end.
- **A12** — `PB-3` vacuity: say what each check would look like if it failed: a 409 on the date-only accept; a task still on the candidate; a second asset; a Review link to a 404; Resolve still showing. None may be the observed result.
- **A13** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed product files:** `backend/app/services/candidates.py`, `backend/app/services/job_service.py`, `backend/app/api/v1/candidates.py`, `backend/app/api/v1/review_tasks.py`, `backend/app/api/v1/jobs.py`, `backend/app/plugins/expiry_tracker.py`, `frontend/src/api/client.ts`, `frontend/src/api/types.ts`, `frontend/src/routes/InboxPage.tsx`, `frontend/src/routes/ReviewPage.tsx`, `frontend/src/routes/AssetDetailPage.tsx`, `frontend/src/components/CandidateCard.tsx`, and their existing test files; new test files under `backend/tests/` and beside the changed components.
- **Also allowed:** any other existing test file that pins the old behaviour, changed only as far as the new behaviour requires, each named in the report with why.
- **Not in this slice, even if seen:** F4, F5, F7, F12 (the AI's date and category, the two controls: next slice); F8 (a dateless item nagging); F3, F13; F9, F10; any Linen Shelf styling; the non-empty resolve bypass.
- **Reads of any file are allowed.** The only runtimes this packet authorises are the G0 Docker preflight, the `make` gate, the tests and the frontend build.
- Evidence: `docs/worklogs/SG-270*` only.
- **No changes** to schema, migration, `backend/app/models/**`, `backend/Dockerfile`, `docker-compose.yml`, `backend/requirements.lock`, dependency, `.env`, the **live** running container, its image tag, the host's packages, the database, or any provider. **No deploy.**
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`). No browser; no network in the tests.
- A constraint here you find wrong or impossible is a STOP, and stopping is a success. Not grounds to stop: a test that needs updating for the new behaviour.

## Hang bounds

Docker preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1700 s:** stop starting new work, commit, write the report, publish the receipt. A partial slice with a receipt is a success. Expected ≈1500 s (`UNVERIFIED — my estimate`), judged larger than this lane's actuals SG-262 991 s and SG-258 1125 s.

## Report

Destination: `docs/worklogs/SG-270_report.md`, evidence logs beside it (`docs/worklogs/SG-270_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈1500 s expectation and names every phase over 60 s. It lists the changed files, the test counts, the FAIL-then-PASS logs, the contract echo, and every `UNCLEAR` / `REMAINING` line. Each constraint gets a line.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-270 | Report: docs/worklogs/SG-270_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
