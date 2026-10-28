# SG-256 — Row 11 polish: an opened date can be edited and cleared

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.** No database is opened, read or written; tests use temporary SQLite files.
**Restart: none.** The running container, its image tag and the host are untouched. The deploy rider is a separate slice.
**Provider: none.** No provider is called, no key is read or printed, **no spend**. Target: **$0**.

**Contract chain:** recorded `0.53.0` (this packet's commit) == published payload `contract-v0.53.0` == the host's contract `0.53.0` (the SG-255 receipt echo) == the echo this report must carry from `/home/andrei/storagegenie-contract/CODER.md` line 3.

**Previous report's open items:** SG-255 closed A-vs-D (D stands) and left only the root-owned `~/.docker` pending in the engine arc, so `DOCKER_CONFIG` stays required; the whole-suite image layout is recorded and needs no action. Nothing else applies.

## Why this exists

Roadmap row 11 is served: the opened-date countdown exists, but an opened date **cannot be edited or cleared once set** — the UI offers the date input only when `opened_date === null` (`frontend/src/components/OpenedCountdownSection.tsx:72-93`), so a saved date is permanent. The write path already supersedes (`backend/app/plugins/expiry_tracker.py:335-369`, `store_opened_date` at `:506-528`), so editing needs only a UI path. Clearing has no representation: the read path `_accepted_opened_date` (`backend/app/services/opened_countdown.py:49-72`) returns `None` for a non-string value, so **a null active assertion is the smallest honest representation** — it supersedes the date, keeps the old one as history, writes the same audit row, and the countdown returns null.

The owner approved this plan on 2026-10-28 (`"D4 - approved"`, D4 in `STATE.md`), inside the approved row-11 stage; the work slice is followed by its own deploy rider under the standing rule.

## G0 — Docker preflight before any gate claim

`make backend-test` runs the image proof, so prove the lane runtime first: `docker version` must show a **Server** section, and `docker run --rm busybox true` must return **rc 0**. If either fails, **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`); do not restart the daemon, use another socket or sudo. Set `DOCKER_CONFIG` to a writable temp directory if the default fails (`D536`), as SG-252/SG-255 did. The lane socket is expected under `/run/dispatch-storagegenie-SG-256/`; a different path is a finding.

## G1 — The clear action, through the one write path

1. Add `clear_opened_date(db, asset)` to `backend/app/plugins/expiry_tracker.py`, beside `store_opened_date`. It applies the **same** category checks (an accepted classification; a category with `opened_date_tracking`) and raises the same `ExpiryValidationError`. If there is **no active accepted `opened_date` assertion**, it is a **no-op**: return `None`, write nothing — no assertion row, no audit row. Otherwise call `_write_assertion(db, asset, OPENED_DATE_FIELD, None, "user", "accepted", None)`, so the previous assertion becomes `superseded`, a new active assertion holds JSON `null`, and the `plugin.assertion.write` audit row records `value: null`.
2. Add `POST /v1/plugins/expiry-tracker/assets/{asset_id}/opened/clear` to `backend/app/api/v1/plugins.py`: the existing `_plugin`, `_asset` (404 unknown asset, 403 household mismatch) and 422 mapping; no required body fields; returns `{"asset_id": ..., "assertion": _assertion_view(assertion)}` — `assertion` is `null` for the no-op. Use POST, not DELETE: the history and the audit row stay.
3. **Do not change** `_accepted_opened_date` or `_write_assertion`; verify the read path already treats a non-string value as `None` (it does). If it does not, STOP and report.
4. Editing needs **no backend change**: the existing `POST .../opened` already supersedes. Prove it with a test if one is not already present.

## G2 — The UI: Edit and Clear on a row that has a date

In `frontend/src/components/OpenedCountdownSection.tsx`, for `row.opened_date !== null`:
- an **Edit** control that reveals a date input pre-filled with the current date and a **Save** button calling the existing `recordOpenedDate`; on success the new date shows in the row;
- a **Clear** control calling the new `clearOpenedDate`; on success the section re-reads and the row returns to the no-date form.
- Keep the no-date path unchanged. Labels in the existing style: `Edit opened date for {name}`, `Save opened date for {name}`, `Clear opened date for {name}`. Invalidate the same `["opened-countdown", householdId]` query through the existing `onSaved`; show errors through the existing `role="alert"` path. **No confirmation modal**: one item, reversible by re-entering the date, and the old value stays in the superseded assertion.
- Add `clearOpenedDate(assetId, householdId)` to `frontend/src/api/client.ts`, posting `{}` to the clear route; add `OpenedDateClearResponse = { asset_id: string; assertion: Assertion | null }` to `frontend/src/api/types.ts`. Do not widen `OpenedDateResponse`.

## G3 — Tests

Backend, in `backend/tests/test_sg240_opened_countdown.py`:
- record a date, then clear: 200; the old assertion is `superseded`; exactly one active assertion remains and its value is `None`; the countdown row has `opened_date`, `days_open`, `days_remaining` and `window_end` all null;
- the clear leaves an audit row with `action="plugin.assertion.write"`, `after.value is None`, and the previous state in `before`;
- clearing an item with no active date is a no-op: 200, `assertion: null`, **no new assertion row and no new audit row**;
- a non-tracking category is 422, an unclassified asset 422, an unknown asset 404, a household mismatch 403 — the same shape as the existing write tests;
- an edit through the existing `POST .../opened` supersedes the old date and the countdown shows the new date (`test_second_write_supersedes_the_first` proves the supersede; add the read-back if missing).

Frontend, in `OpenedCountdownSection.test.tsx`:
- an opened row shows Edit and Clear and not the no-date form; Edit + Save posts the new date and re-reads; Clear posts to the clear route and, after the re-read, the row shows the no-date form (`No opened date yet`) and the input;
- an unopened row shows the input and Save, and no Edit/Clear;
- the existing tests stay green.

## G4 — Verification and the gate

- The new tests must be **seen to FAIL on the pre-change code** (the clear route is 404; the Edit/Clear controls are absent) and **pass on the candidate**; commit both runs (`PG-EV-09`).
- `make backend-test` once: the host suite green with the new tests among the passes, the two marked tests still **deselected**, then the image proof. Quote the host-suite counts; no fixed count is imposed — report the exact numbers and do not force them (`PG-IC-08`). The two pre-existing environmental reds must stay absent.
- `make frontend-test` once: the full frontend suite green; quote its counts.
- `curl -s http://127.0.0.1:8003/v1/health` at start and end: both 200, unchanged.
- `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation (the dispatch shell has no python on PATH; SG-252/SG-255 did the same).

## Acceptance criteria

- **A1** — the clear action writes a null active assertion through `_write_assertion`, keeps the old date as `superseded`, writes the audit row, and the countdown returns null; the no-op case writes nothing.
- **A2** — the clear route uses the existing guards and returns 200, 422, 404 and 403 in the named cases.
- **A3** — the UI shows Edit and Clear only on a dated row; Save edits and re-reads; Clear clears and returns the row to the form; the no-date path is unchanged.
- **A4** — the new tests are FAIL-then-PASS with both logs committed; `make backend-test` and `make frontend-test` are green; counts quoted.
- **A5** — scope is only the seven named product files plus `docs/worklogs/SG-256*`; zero schema, migration, Dockerfile, compose, lockfile, dependency, model, database, host, provider, running-container or deploy bytes. The deploy rider is separate.
- **A6** — the Docker preflight is proven before the gate; health 200 at start and end.
- **A7** — `PB-3` vacuity: what each check would look like if it failed — the clear test finding the old date still active; the countdown still showing the date; the no-op writing a row; the UI not showing the controls; a suite red. None of these may be the observed result.
- **A8** — the report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed product files:** `backend/app/plugins/expiry_tracker.py`, `backend/app/api/v1/plugins.py`, `backend/tests/test_sg240_opened_countdown.py`, `frontend/src/components/OpenedCountdownSection.tsx`, `frontend/src/components/OpenedCountdownSection.test.tsx`, `frontend/src/api/client.ts`, `frontend/src/api/types.ts`. Reads of any file are allowed.
- Evidence: `docs/worklogs/SG-256*` only.
- **No** schema, migration, `backend/app/models/**`, `backend/Dockerfile`, `docker-compose.yml`, `backend/requirements.lock`, dependency, the running container, its image tag, the host's packages, the database, or any provider. **No deploy.**
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`): never route around the socket, sudo or a missing package.
- No browser, no frontend production build beyond what the suite needs, no network in the tests.

## Hang bounds

Docker preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1200 s.** Expected ≈300 s, bracketed from this lane's recent actuals (149, 398, 447, 569 s): the backend host suite (~65 s), the frontend suite, one image proof, the new tests and their FAIL runs dominate. If new work passes 1200 s, stop starting, commit, write the report, publish the receipt.

## Report

Destination: `docs/worklogs/SG-256_report.md`, evidence logs beside it (`docs/worklogs/SG-256_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈300 s expectation and names every phase over 60 s.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-256 | Report: docs/worklogs/SG-256_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
