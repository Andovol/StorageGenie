# SG-016 — Inbox + review workspace UI (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 slice 5 of 7 (plan `docs/superpowers/plans/2026-09-08-phase-1-deterministic-import.md`, D9, D10 resume). SG-015 landed (`8715d4e`, rated 97): plugin routes live, full suite green except ISS-1. Every backend route this UI needs exists and is proved — except candidate READ-BACK, which has no GET route (decisions return state, but nothing serves a candidate by id). This slice is frontend-first with one bounded read-only backend addition.
**Established premises (verify, do not re-derive):** ISS-1 decoder legs stay carried (no test depends on real decoders); PDF evidence quarantines at EXTRACTING; EXIF-as-expiry-source flaw is ISS-2 carried to SG-017 (do not touch `expiry_tracker.py` here); extensions payloads nest attributes under the `attributes` key (`plugins.py:163-176` — flat payloads carrying `plugin_id` are rejected, so the UI nests).

> Facts below are what I believe from the tree that carries this packet. **They are EXPECTED conditions,
> not established truth. Verify each before building on it; a difference is a finding, not an obstacle.**
> For any number, path or quoted line I hand you: if your figures differ from mine, investigate and
> explain — **do not bend your answer to match mine. Correcting me is worth more than agreeing with me.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (Effort is proven readable from process arguments — do the same.)

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** No migration. No live database; backend proof (if any backend line changes) is in-process via `TestClient` + temp DBs (`PG-PR-04`). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): finish inside 2100s, report elapsed against it. Coder-side `node`/`npm`/`python` may be absent on the host PATH — resolve the actual binaries (SG-009/SG-011 proved `venv/bin/` for python; find the node toolchain the same way and name it, never assume `npm`).

## Why this exists

The import pipeline is headless: jobs, candidates, collisions, and manual-entry tasks exist behind routes, but no screen shows a pending import, its progress, its failure, or a candidate beside its source evidence. Handed contract facts (verify each against the tree before building): `GET /v1/imports/{job_id}` returns steps with states/attempts/outputs/errors plus `progress{completed,total,failed,pending}` (SG-012 shape, `job_service.py:serialize_job`); the DEDUPLICATING step output carries `candidate_id` (SG-014); `POST /v1/candidates/{id}/decision` takes `{action: accept|edit|hold|reject, corrected_fields}` and blocks on open tasks with 409 (SG-014); `GET /v1/review-tasks` envelope + `POST .../resolve` (SG-014, alias intact); plugin classify/expiry/extensions GET+POST under `/v1/plugins/expiry-tracker/assets/{asset_id}/...` (SG-015); asset detail carries assertions (incl. `plugin:` fields), evidence, and audit history (Phase 0 + SG-014 lifecycle rows). Frontend patterns to reuse: household selector + localStorage default + 200 ms debounce + cursor `Load more` (`CatalogPage.tsx:16-36,114-122`), `useAssets` hook shape, `client.ts`/`types.ts` client discipline, router in `App.tsx`, jsdom component tests + `tsc --noEmit` + `eslint` clean (SG-009 gates, still binding).

## G1 — candidate read-back (the ONE backend addition; read-only, additive)

- Add `GET /v1/candidates/{candidate_id}` (household-checked 404/403, returns id/state/job_id/proposal fields/dedup_matches/review_task_ids/evidence_ids). Optionally surface `candidate_id` linkage in the job view ONLY as an additive field AND only if the SG-012/SG-014 suites stay byte-green — any red reverts the linkage, never the tests.
- No other backend behavior change: no new table, no migration, no route modification, no `expiry_tracker.py` touch (ISS-2 lives there). Prove with the SG-012…SG-015 backend suites green (minus the two named ISS-1 decoder nodes) plus one new test module for the GET route.

## G2 — Inbox screen (`PG-EV-05`, blueprint §11.1-1)

- New `InboxPage` route: job list (state, progress counts, errors) via `GET /v1/jobs` + per-job detail on select; failed jobs show step errors with a working retry action; review-task queue with resolve actions; empty states for no-jobs and no-tasks (assert both — an unasserted empty state is a vacuity risk).
- Property, not command: a job that the backend reports FAILED with step errors must render the error text and an enabled retry control bound to that job's id (test with fixture ids from the loaded payload — no fixed-id replay).

## G3 — Review workspace (blueprint §11.3 behaviors are the acceptance)

- New `ReviewPage` route driven by candidate id: source evidence image(s) rendered BESIDE candidate fields (evidence visible while accepting — assert co-presence in the DOM, not just two passing renders); per-field confidence + extraction source shown; `Unknown`/hold first-class (hold posts `hold`, never a guessed value); accept / edit-with-corrections / hold / reject all wired with the ids from the loaded candidate; duplicate/identifier-collision matches shown with their blocking effect explained (accept disabled or 409-surfaced while tasks open — assert one).
- Manual expiry entry form with date-type selector posting to the plugin expiry route (nested payload shape); `needs_evidence` state shown before entry, resolved state after (re-read, not optimistic UI).
- Keyboard: accept / reject / prev / next handlers bound and tested by simulated key events.
- Batch accept for safe non-critical fields is the LAST goal, explicitly droppable: implement as client-side fan-out over single-decision calls only (no backend change); if time/space press, drop it and report dropped-with-reason rather than half-building it.

## G4 — Discrimination proof instead of hollow fail-first (`PG-EV-01`)

- New-file UI tests cannot fail pre-change by missing code (an import error is not a failing baseline). Instead: every behavior test above ALSO runs against a deliberately wrong mock response (wrong ids, swapped states, missing evidence) and must FAIL there — quote one passing run and one discriminating-failure run per behavior group in the committed frontend log. A test that passes on both is deleted, not kept.

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-016.log` (backend-relevant legs) + frontend log alongside the frontend work + `{{WORKLOG_DIR}}/SG-016_report.md`, first token `SG-016`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units. State model/effort provenance from process arguments.

## G6 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-016 | Report: docs/worklogs/SG-016_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `frontend/src/routes/InboxPage.tsx` + `frontend/src/routes/ReviewPage.tsx` (new) + `frontend/src/components/JobCard.tsx` + `frontend/src/components/CandidateCard.tsx` + `frontend/src/components/ExpiryEntryForm.tsx` (new) + focused test files per component/route + `frontend/src/App.tsx` (route registration only) + `frontend/src/api/client.ts` + `frontend/src/api/types.ts` (endpoint additions only) + backend `GET /v1/candidates/{candidate_id}` route + additive job-view linkage (G1 bounds) + its one backend test module + `docs/worklogs` files + the G6 note mechanism. No migration, no other backend behavior change, no new runtime dependency, no `.env`/restart/secrets/infra, no AI/LLM/provider code, no expiry dashboard/urgency view (deferred per plan — attempting it is out of scope). Anything else is a STOP ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — G1 needs no migration and no existing-route change; G2/G3 need no backend change beyond G1. Recorded here once, not per criterion.
- Exclusions by rule: no backend route decorator outside the single new GET route is added or modified (`PG-SC-05`); grep-gate backend decorators and report the match list.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`. Provider keys do not exist in this phase; the frontend carries none.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: `npm test -- --run` + `npm run lint` + `tsc --noEmit` (SG-009 gates, all binding) with file/test counts quoted; backend SG-012…SG-015 suites green except the two named ISS-1 decoder nodes; every gate names what it checked; a gate emitting no output is a FAIL. mypy advisory — quote, fix nothing outside the ceiling.
- Budget: 120s per ordinary command, 600s per suite leg, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`). Reuse CatalogPage/hook/client patterns before inventing new ones.
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- Inbox renders jobs with states/progress/errors from loaded ids; FAILED shows error text + working retry bound to that job; review queue lists with resolve; both empty states asserted.
- Review renders evidence beside fields (DOM co-presence), confidence + source per field, duplicates with blocking effect (accept blocked while tasks open, proved once by 409 or disabled control).
- Accept/edit/hold/reject post with loaded candidate ids; manual expiry entry nests the payload, shows `needs_evidence` before and resolved state after via re-read; keyboard handlers fire on simulated keys.
- Every behavior test has a quoted discriminating-failure run against a wrong mock; tests passing on both mocks do not exist.
- `tsc --noEmit` 0, `npm run lint` 0, component suite green with counts; backend suites unregressed (ISS-1 nodes named if excluded).
- G1 GET route proved by backend test with 403/404 legs; additive linkage only if suites stay green, else reverted and reported.
- Worklog(s) + report committed; notes ref carries the `Dispatch-ID: SG-016` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — from process arguments (proven readable), never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
