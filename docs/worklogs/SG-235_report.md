SG-235 model=opencode-go/deepseek-v4.1-flash effort=max dir=/home/andrei/StorageGenie remote=origin git@github.com:Andovol/StorageGenie.git BASE=d0492383dd6364c26b68f2c12038c757f138af46 (origin/automation) WORK_HEAD=fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1

Spend: $0.000000 actual vs $0 bound (zero provider calls). Contract read: `/home/andrei/storagegenie-contract/CODER.md` line 3 verbatim `**Contract version: 0.52.0** — **echo this line verbatim in your receipt.** It is the only proof that you` (cache VERSION 0.52.0; `AGENTS.md:4` and `STATE.md:6` record 0.52.0).

(a) Issues / deviations / surprises

I1. Contract source echoes 0.52.0, not the 0.51.0 last seen on this host (SG-234). The packet names this host link as STATED; the installed copy now reads 0.52.0, so I echoed 0.52.0 from the source path rather than bending it. The controlled axis (recorded 0.52.0) and the source now agree.

I2. Premise (d) says the grep `lifespan|on_event|create_task|BackgroundTask|APScheduler` over `backend/app/` returns one docstring hit. On the start base the exact pattern returned **zero** hits; adding the word `scheduler` finds the two docstrings (`expiry_engine.py:3`, `analytics/service.py:3`). The absence of a startup hook is confirmed; the packet's hit count is off by the word `scheduler`, not by behaviour.

I3. SG-233's committed smoke gate `test_sg233_diff_touches_only_the_approved_ceiling` is now red on **every** later slice: it asserts its own historical file set (empty diff included) and rejects `backend/Dockerfile`. It is red on the candidate for `backend/Dockerfile` and red on base d049238 because the base diff is empty (`assert [] == ['backend/alembic/versions/20261023_sg233_reminder.py']`, SG-235_verify.log section 7). It is outside this slice's ceiling (the SG-233 test file is not writable here). This is a standing false red for the project; the next slice allowed to touch that file should relax it to a historical, non-blocking check.

I4. The full candidate suite has three reds: the stale SG-233 gate plus two environment gaps (`pyzbar/libzbar` and `tesseract` absent, `test_signals.py`). All three were run alone on base d049238 and fail there for the same reasons (section 7); none is a regression.

I5. Whole-repo `npm run lint` is red on the untouched `frontend/src/App.household-nav.test.tsx` (unused `fireEvent`). It is equally red on base d049238. The touched frontend files are clean under eslint; `tsc && vite build` is green.

I6. Whole-backend `ruff check .` reports 9 pre-existing errors in `backend/scripts/*` (unused imports, two complexity rows). Base reports the same 9; the four touched Python files pass. `mypy app` reports 41 errors on both base and candidate; the only shift is the two pre-existing `main.py` unused-ignore rows moving from lines 58/64 to 59/65 after the added import.

I7. Docker CLI observation was denied (`permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`). No docker operation was required by this slice; no pull, run, build, restart or deploy was attempted. This is reported as unanswered, not routed around.

I8. Ordering rule resolved as: three UNCLEAR lines, then the absolute last line `Verification: PASS` (`CO-104`). The packet asks both for "end with the three UNCLEAR lines" and for the final `Verification:` line; CO-104 governs the last line, so UNCLEAR precedes it.

I9. The 24-hour cadence is measured from the previous pass, not aligned to midnight; the shipped default is the feature constant `DAILY_INTERVAL_SECONDS = 86400.0`, with no setting/env/compose key. A container restart re-runs the startup pass and the unique `(asset_id, as_of_day)` guard makes it a no-op for the same UTC day; a restart after missed days computes today only.

I10. The new scope gate compares `origin/automation...HEAD`, exactly as SG-233's did. It is meaningful and green on the candidate **before** the push (section 2, seven product paths; section 9, ten paths after the evidence commit). Once the push moves `origin/automation` to this HEAD the range is empty and the gate's `REQUIRED_PATHS` assertion becomes red; a rerun after publication is therefore not a product signal. This is the same slice-local limitation as the SG-233 gate in I3 and does not affect the quoted pre-push runs.

(a2) Premises re-verified (quoted, not trusted)

- `backend/app/services/reminders/service.py:3` "The single production writer is ``record_due``."; lines 41-49 `def record_due(db: Session, household_id: str, as_of_day: date | None = None)` ... `day = as_of_day if as_of_day is not None else today_utc()`.
- `backend/app/db.py:15` `engine = create_engine(settings.database_url, connect_args=connect_args)` at import time; `:31` `SessionLocal = sessionmaker(bind=engine, ...)`; `:34` request-scoped `get_db`.
- `backend/app/main.py` start base: `app = FastAPI(title="StorageGenie", version="0.1.0")` at line 29, no lifespan/startup hook; the reminders router used the inline `__import__(...)` at line 83.
- `backend/Dockerfile` start base: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
- `frontend/src/api/client.ts:296/302/310`: `fetchReminders`, `markReminderRead(reminderId, householdId)`, `dismissReminder(reminderId, householdId)`; types at `frontend/src/api/types.ts:391-412`.
- `frontend/src/routes/ExpiryPage.tsx:176` `Unread reminders ({unreadCount})`, key `["reminders", effectiveHousehold]`, unread filter, no action buttons before this slice.
- Alembic heads before and after: one head, `20261023_sg233_reminder`; no new revision and no schema/model/config change.
- `backend/tests/conftest.py` does not exist; the new module carries its own fixtures.
- Starting tree: `## automation...origin/automation`, porcelain empty, HEAD d049238. Health start and end both `{"status":"ok","db":"ok","storage":"ok"}`.

(b) Actions

Product paths (7, all inside the ceiling): `backend/app/services/reminders/daily.py` (new), `backend/app/server.py` (new served entrypoint), `backend/app/main.py` (top-level reminders import + one registration line), `backend/Dockerfile` (one CMD token), `backend/tests/test_sg235_daily_caller.py` (new), `frontend/src/routes/ExpiryPage.tsx`, `frontend/src/routes/ExpiryPage.test.tsx`. Evidence paths: `docs/worklogs/SG-235.log`, `SG-235_report.md`, `SG-235_verify.log`.

Commit fdfc44e `SG-235: daily reminder caller and Expiry read/dismiss actions` is the work HEAD. A docs-only evidence commit follows; it changes no product byte.

Design: `run_daily_pass(session_factory, *, as_of_day=None)` enumerates every `household` row, calls the production `record_due` per household, records and continues on a per-household exception, and closes its own session. `run_daily_forever(session_factory, *, interval_seconds=DAILY_INTERVAL_SECONDS, clock=None, sleep=None)` runs a pass immediately, computes the day from the live clock at each pass, then sleeps 86400 s. `backend/app/server.py` attaches a lifespan to the same FastAPI object and cancels the task on shutdown with a 5.0 s wait; `app.main` itself remains inert on import. The pass runs in `asyncio.to_thread`.

Retries: 0 test retries; one expected pre-commit red on my own scope gate (empty diff before the product commit), fixed by committing before the authoritative run. Provider calls: 0. Production rows created: 0 by construction. External effects: none; no deploy, restart, image build, nginx, cron or host timer.

Elapsed, as of the final report write: 700 s of 1800 s overall (process start 2026-10-24T11:06:01Z). Legs: base backend new nodes 2.72 s of 120 s; candidate backend new nodes 4.19 s of 120 s; discrimination 1.48 s of 120 s; base frontend nodes 5.60 s of 300 s; candidate frontend nodes 2.21 s of 300 s; full backend suite 58.00 s of 600 s (run once); base old reds 1.60 s of 120 s; ruff 0.07 s, mypy 0.34 s, eslint touched 1.05 s (under 120 s each); frontend build 2.69 s of 600 s; receipt note 120 s bound, push 300 s bound, both completed in well under their bounds. No command was killed; no bound was approached; no wall-clock wait was used for cadence or gap tests.

(c) Verification

Q1 caller — PASS. `test_sg235_pass_covers_every_household_with_engine_shaped_rows` measures exactly 2 households, 1 created row for the due first household and 0 for the second, and asserts the stored `(tier, bucket, days_remaining)` equals `GET /v1/plugins/expiry-tracker/status` for the same day (`urgent/this-week/3`). The mutation leg moves the accepted date to +20 days and a later pass stores `upcoming/this-month/16`, so a pass inventing fixture rows cannot pass. It also asserts `daily.record_due is app.services.reminders.service.record_due`. `test_sg235_second_pass_same_day_creates_nothing` reports 2 households visited and 0 created through the caller, DB count stays 1. `test_sg235_loop_does_not_backfill_missed_days` runs a baseline pass at D, then the loop with an injected clock fixed at D+3 and one fake sleep that cancels; clock calls == 1, stored days == {D, D+3}, and D+1/D+2 have zero rows. `test_sg235_loop_cadence_survives_a_failed_pass` asserts `DAILY_INTERVAL_SECONDS == 86400`, the fake sleep records `[86400.0, 86400.0]`, the first pass raises and the second still runs. `test_sg235_lifespan_starts_loop_once_and_cancels` starts the spy exactly once on lifespan entry, sees cancellation on exit, and measures 0.0000 s against the implemented 5.0 s bound. `test_sg235_health_answers_while_a_pass_is_in_flight` blocks the real pass in a worker thread and gets `200 {"status":"ok","db":"ok","storage":"ok"}` in 0.0027-0.0040 s, while the pass later writes its row. `test_sg235_pass_isolates_a_failing_household` records the failing household and still writes the other household's row, returning normally. `test_sg235_suite_starts_no_pass_and_creates_no_relative_db` shows the pytest temp dir empty, `backend/data/` absent before and after a fresh `import app.main`, and asserts the interval; no test ever hands the pass the default `SessionLocal`, and the only in-suite pass uses the temp factory. `test_sg235_diff_touches_only_the_approved_ceiling` prints the seven product paths and rejects anything else (raw section 2).

Q2 actions — PASS. The extended `ExpiryPage.test.tsx` has 13 nodes: 9 existing plus 4 new. An unread row renders `Read reminder r1` and `Dismiss reminder r1` with `focus-ring`; a read row renders neither. Clicking Read finds a `POST` to `/v1/reminders/r1/read?household_id=hh-expiry` and then a second `GET /v1/reminders`; the mocked server keeps the row unread, and the page still shows it with `Unread reminders (1)` — proving the list and count come from the server, never a local decrement. Dismiss finds the same shape on `/dismiss`. A mocked 422 produces `role="alert"` with the server detail, keeps the row and triggers no re-read. Raw sections 4-5: base 4 failed | 9 passed, candidate 13 passed.

Worlds (`PG-SC-09`) — passes-but-wrong is ruled out by the real engine-shaped row plus the date-mutation leg; working-but-fails is ruled out by the existing SG-233 read-then-dismiss round trip (captured unread baseline, `unread_count - 1`, illegal transitions 422), which passed inside the 738-pass full suite, and by the server-controlled unread row surviving a successful read on the page (no local removal, no local count change); the inverse is satisfied because the no-backfill check is a set delta from the D baseline, not an absolute row count.

Property-not-command (`PG-EV-05`) — the four properties are checkable in the committed test bodies and raw logs: one pass per household per day (a single `run_daily_pass` enumerates the table once), a second pass the same day creates nothing (caller-level `reminders_created == 0`, DB count unchanged), missed days are never backfilled (clock-call count 1 and zero rows on D+1/D+2), and the page count is the server's `unread_count` (the page never decrements; the sticky-unread fixture keeps the row).

Runtime-versus-budget (`PG-PR-06`) — measured one pass: **0.0098 s wall clock for 2 households, 1 due, 1 row created** = 0.0049 s/household on scratch SQLite under the pytest tmp dir. Expected production runtime = households × ~0.005 s plus the enumeration query; at the last live read (1 household, not read by this slice) that is ~0.005 s. Observed health latency during a pass: **0.0027-0.0040 s** for a 200. Shutdown bound implemented: **5.0 s**, measured 0.0000 s with the spy. The numbers came from `time.perf_counter()` inside the committed tests and the pytest duration lines in SG-235_verify.log.

Gates — ruff touched files clean (whole repo 9 == 9 base); mypy delta zero (41 == 41 base, new modules zero); frontend touched eslint clean, `tsc`/`vite build` green; base-full lint red and whole-ruff red are pre-existing and cited above. No migration, no dependency change, no email/SMTP path (the only `@` token in the diff is `@pytest.fixture`). Diff touches the seven ceiling paths only (gate output quoted in section 2).

Database (`PG-PR-10`) — scratch temp SQLite under the pytest tmp dir, built by the committed migration; `DATABASE: none` for production. Production SQLite was not read or written; production rows created: 0 by construction. `backend/data/` does not exist after the full suite, and the relative default path was never created.

How code becomes live (`PG-PR-04`) — it does **not** in this slice. No deploy, restart, image build or host timer was run. The running service still serves the previous build and has **no daily pass yet**; the Dockerfile entrypoint and the new module become live only when the next close-deploy rider builds and recreates the container.

FAIL-then-PASS (`PG-EV-09`) — new backend nodes fail on base d049238 (9 failed, 2.72 s) and pass on fdfc44e (9 passed, 4.19 s); new frontend nodes fail with the base `ExpiryPage.tsx` (4 failed | 9 passed) and pass on the candidate (13 passed). Both raw runs are committed in `docs/worklogs/SG-235_verify.log` sections 1-2 and 4-5; the base commit and the tree that produced each failure are named there. Discrimination (`PG-EV-01`): inverting the expected household count to 3 fails with `assert 2 == 3` (section 3), then the assertion was restored.

No vacuity (`PB-3`) — the due fixture would fail on an empty reminder set (exact 1-row and engine-shape assertions); the loop tests assert clock calls and recorded delays, so a loop that never ran fails; the scope gate requires the seven product paths, so an empty diff fails; no criterion rests on an exit code alone.

Receipt — the note was added on WORK_HEAD fdfc44e after the evidence commit, pushed, and read back from the explicitly fetched mapped ref. Executed output (full raw transcript, including the complete note list, is in SG-235_verify.log section 10):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1
error: no note found for object fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1.
EXIT=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-235 | Report: docs/worklogs/SG-235_report.md | Work-HEAD: fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1" fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1
EXIT=0

$ git notes --ref=refs/notes/storagegenie-coder-reports show fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1
Dispatch-ID: SG-235 | Report: docs/worklogs/SG-235_report.md | Work-HEAD: fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1
EXIT=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   d11de68..5b103ed  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
EXIT=0

$ git fetch origin "+refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg235-fetched"
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg235-fetched
EXIT=0

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg235-fetched show fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1
Dispatch-ID: SG-235 | Report: docs/worklogs/SG-235_report.md | Work-HEAD: fdfc44e2eeb253f4cffa0dcf16e67e17cc019aa1
EXIT=0

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg235-fetched list | cut -d" " -f1 | while read -r note; do git cat-file -p "$note"; done | grep -c "Dispatch-ID: SG-235"
1
EXIT=0
```

note=yes

UNCLEAR
FIRST READ: the packet's premise (d) hit count versus the literal grep (I2), and the order of the three UNCLEAR lines versus the mandatory last `Verification:` line (I8). I kept the literal grep result and put Verification last.
DURING EXECUTION: the stale SG-233 diff gate makes any later full-suite run red on base and candidate (I3). It is outside this ceiling; I base-proved it rather than editing another slice's test. Whole-repo lint/ruff reds are likewise pre-existing and base-proved (I4-I6).
REMAINING: the daily caller now exists in the image only; it is not live until the next deploy. The stale SG-233 gate needs a later owner-approved cleanup; email stays out (D-1024-2, no SMTP); `window_days` still reads the engine's private accepted-classification helper inside the untouched reminders API.

Verification: PASS
