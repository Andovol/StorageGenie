# SG-262 — The three SG-258 findings: hide the review page's dataless date form, resolve date tasks on a move to a no-expiry category, say "No date"

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** This slice does not deploy; rider SG-263 does.
**Provider: none.** No key, no `.env`, no spend.

**Contract chain:** recorded `0.56.0` (`AGENTS.md`) == published `contract-v0.56.0` == the host's contract, echoed by this report from `/home/andrei/storagegenie-contract/CODER.md` line 3. A different echo is a finding.

**Previous report's open items:** the SG-258 audit's waste was two avoidable full-gate reruns, each caught by a caller or coupled test the packet had not named. So: run the targeted tests and the type check green **before** the one full gate. The callers known to the Architect are named below.

## Why this exists

The owner approved this stage, D7 (2026-10-30, *"D7 - as recommended."*), and scheduled it as stage A of the new roadmap (D10, D11, 2026-11-02): E2 + F1 scoped + G2 + one work slice and one rider. Second opinion: SG-264/SG-265; the choices below are decided and not reopened.

The SG-258 audit (93), verbatim:

> (2) the `ReviewPage` form's data is lost — the optional props render but the review-workspace form shows the default `needs_evidence` and an empty date because the caller passes no active assertion/category; the Coder's I3 only caught the `tsc` prop — FIX QUEUED next stage; (3) the reverse-move task limbo — `classify_asset`'s move to non_perishable writes the null accepted but does not resolve the open `expiry.manual_entry` task, and clear/entry both 422 on non-perishable — FIX QUEUED next stage; (4) the form says `accepted` with no date after a clear — FIX QUEUED next stage (show `dateless`).

(G2 below replaces the audit's `dateless` wording; that is the decision.)

## G0 — Docker preflight before any gate claim

`make backend-test` runs the image proof, so prove the lane runtime first. The default `/var/run/docker.sock` is expected to be denied: set `DOCKER_CONFIG` to a writable temp directory and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-262/docker.sock`; `docker version` must show a **Server** section, and `docker run --rm busybox true` must return **rc 0**. If either fails, **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`); do not restart the daemon, use another socket or sudo. A different lane socket path is a finding. Use `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation. Run `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200.

## G1 — E2: no dataless date form on the review page

The form must not render where its caller supplies no asset data. The asset page stays the date path; add no fetch to the review page.

Expected (each a hypothesis to falsify):

- `frontend/src/components/ExpiryEntryForm.tsx:27` defaults `hasWindows = true`; `:51` returns null when false. Decision: the default becomes `false`.
- `frontend/src/routes/ReviewPage.tsx:60` renders the form without `hasWindows`, so it now renders nothing there. Remove the render if that is cleaner; report which.
- `frontend/src/routes/AssetDetailPage.tsx:541` is the working caller and passes `hasWindows`. **Prove it passes it explicitly**; if it relies on the default, that is a finding to fix inside this slice.
- `frontend/src/routes/ExpiryPage.tsx:16` imports only `DATE_TYPE_LABELS`, so it is not a caller.
- `ExpiryEntryForm.test.tsx` probably renders the form without the prop, and such tests must now pass `hasWindows`.

**Enumerate the callers yourself**; the list above is an expectation, and report any difference. Report whether a reviewer on `ReviewPage` still has a visible way to reach the asset page. If not, report it; do not build one.

## G2 — "No date" for an accepted row with no date

When the active assertion is `accepted` and holds no date, `data-testid="expiry-state"` shows **`No date`**. Every other state is unchanged: `needs_evidence`, `proposed`, and `accepted` with a date (`frontend/src/components/ExpiryEntryForm.tsx:53`, `:109`; `:54` already derives `activeDate`). "Date cleared." at `:98` stays. Expected: `ExpiryEntryForm.test.tsx:66` pins `accepted` for a dated row and stays green. A row whose value is an unknown or malformed shape: state what the form shows and test it.

The Save button's label at `:148` reads `state`; **it must keep working from the real review state**, so keep the display word separate from that logic.

## G3 — F1 scoped: a move to a no-expiry category resolves the date tasks

When `classify_asset` (`backend/app/plugins/expiry_tracker.py:450`) moves an asset to a category with `has_expiry` false, every open date-prompt task for that asset is resolved, and the resolved ids are reported.

**Facts this choice turns on, all hypotheses:**

- Producers of `expiry.manual_entry` found by the Architect, by grep of `backend/app`:
  - `_manual_task` (`expiry_tracker.py:374-397`), `subject_ref` = asset id, used by classify (`:470`) and `apply_extraction_result` (`:400-425`). Both carry the same `proposed_change` (`field_path`, prompt "Enter expiry date manually"), so **they cannot be told apart and both ask for a date**. A no-expiry item can never give one, so **both are resolved**.
  - `backend/app/services/candidates.py:757-769`: `subject_ref` = **candidate id**, so a filter on `subject_ref == asset.id` should not match it. **Left alone**; prove this in a test.
  - Split orphans (`expiry_tracker.py:641-683`, `_orphan_manual_tasks`): a task's origin can be another asset, handled by that code. **Do not change it.** Read it, and report how a split child or origin behaves under the move. If a task exists that is not a date prompt for this asset, it stays open and that is a finding.
- The resolve shape to match: `clear_expiry_date` (`expiry_tracker.py:626-637`) filters on `subject_ref`, `household_id`, `task_type`, `status="open"`, and sets `status = "resolved"`. `store_manual_expiry` is the sibling; `backend/app/api/v1/plugins.py:221-225` reports `resolved_review_task_ids`.
- The classify route (`plugins.py:150-160`) returns `review_task` as one id or None. **Add `resolved_review_task_ids` (a list, empty when none) alongside it; do not change or remove any existing field.** Add it to the frontend type if `frontend/src/api/types.ts` declares this response, and report what reads it (`PG-SC-02`). No screen needs to show it.
- Resolve whether or not an active expiry row exists: today's branch is `elif active is not None` (`expiry_tracker.py:~481`), and a task may be open with none. Establish it and test both.
- **Audit parity:** report whether the sibling routes record an audit event for resolved ids, and match them; do not invent a new pattern.
- A move between two dated categories must not resolve any task. Test it.
- Establish which categories have `has_expiry` false; expected only `non_perishable`. Use the flag, not the slug (`PG-SC-05`).

The expiry split in the new roadmap does not change this: do not restructure the plugin, and do not rename any stored path. If a fix turns out to depend on that structure, say so in the report.

## G4 — Tests and the gate

- New tests FAIL on the pre-change code and PASS on the candidate; commit both runs (`PG-EV-09`) as `docs/worklogs/SG-262_fail_*.log` and `SG-262_pass_*.log`. The base checkout uses the same temporary-SQLite test settings; no secret file is copied (`PG-EV-13`). Discriminating cases: the form rendered with no `hasWindows`; `accepted` shown with no date; a task left open after the move, and no `resolved_review_task_ids`.
- First the targeted tests and `tsc`. Then grep for every test that pins the changed behaviour or the classify response, and fix those **before** the full gate.
- `make backend-test` once: the host suite green, the two marked tests still **deselected**, then the image proof. `make frontend-test` once. Quote exact counts; do not force a fixed number (`PG-IC-08`).
- Run the affected backend test modules and frontend test files **twice consecutively** (`PG-DP-04`).
- Targeted lint on **every changed or new file**: `ruff check` the backend files, `eslint` the frontend files. The repo-wide mypy reds and the one pre-existing eslint error in `App.household-nav.test.tsx` are out of scope. Reconcile the changed paths against the gate's paths (`PG-EV-15`).
- Prove the deploy's own frontend build step exits 0 on the candidate (`PG-SC-12`).

## Acceptance criteria

- **A1** — The review page renders no date form; the asset page still renders and works for a classified category with windows; a test pins each.
- **A2** — An accepted row with no date shows `No date`; the other three states and the Save label are unchanged; tests pin each.
- **A3** — A move to a no-expiry category resolves this asset's open date-prompt tasks and returns their ids in `resolved_review_task_ids`, with or without an active row; a dated-to-dated move resolves none; the existing classify fields are unchanged; a candidate-subject task stays open.
- **A4** — Every producer of `expiry.manual_entry` is enumerated in the report with what happens to its task; the difference from this packet's list is stated either way.
- **A5** — FAIL-then-PASS with both logs committed; host suite, image proof and frontend suite green; affected files run twice; the build step rc 0; counts quoted.
- **A6** — Scope is only the files below; zero schema, migration, Dockerfile, compose, lockfile, dependency, model, database, host, provider, running-container or deploy bytes.
- **A7** — Docker preflight proven before the gate; health 200 at start and end.
- **A8** — `PB-3` vacuity: say what each check would look like if it failed: the form still rendering on the review page, or gone from the asset page; `accepted` still showing with no date; a task still open or the ids missing; a task wrongly resolved on a dated move; a suite red. None may be the observed result.
- **A9** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed product files:** `backend/app/plugins/expiry_tracker.py`, `backend/app/api/v1/plugins.py`, `backend/tests/test_plugin_expiry.py`, `frontend/src/api/types.ts`, `frontend/src/components/ExpiryEntryForm.tsx`, `frontend/src/components/ExpiryEntryForm.test.tsx`, `frontend/src/routes/ReviewPage.tsx`, `frontend/src/routes/ReviewPage.test.tsx`, `frontend/src/routes/AssetDetailPage.tsx`, `frontend/src/routes/AssetDetailPage.test.tsx`.
- **Also allowed:** any other existing test file that pins the old behaviour, changed only as far as the new behaviour requires, each named in the report with why.
- **Reads of any file are allowed.** The only runtimes this packet authorises are the G0 Docker preflight, the `make` gate, the tests and the frontend build; no other container, image or runtime.
- Evidence: `docs/worklogs/SG-262*` only.
- **No changes** to schema, migration, `backend/app/models/**`, `backend/Dockerfile`, `docker-compose.yml`, `backend/requirements.lock`, dependency, `.env`, the **live** running container, its image tag, the host's packages, the database, or any provider. **No deploy.** The G0 and `make backend-test` build and run the existing test image and a throwaway proof container only.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`): never route around the socket, sudo or a missing package.
- No browser; no network in the tests.
- A constraint here you find wrong or impossible is a STOP, and stopping is a success. Not grounds to stop: a test that needs updating for the new behaviour.

## Hang bounds

Docker preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1500 s:** stop starting new work, commit, write the report, publish the receipt. A partial slice with a receipt is a success. Expected ≈900 s, bracketed from this lane's actuals: SG-256 540 s, SG-258 1125 s.

## Report

Destination: `docs/worklogs/SG-262_report.md`, evidence logs beside it (`docs/worklogs/SG-262_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈900 s expectation and names every phase over 60 s. It lists the changed files, the test counts, the FAIL-then-PASS logs, the contract echo, and every `UNCLEAR` / `REMAINING` line. Each constraint gets a line.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-262 | Report: docs/worklogs/SG-262_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
