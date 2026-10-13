SG-187 — R2 capture/import journey repair — CHANGED

RESULT: CHANGED (CO-48 class 1). G1: the Inbox selected-job panel now offers "Start import job" on a CREATED job and posts the real `/v1/imports/{id}/run` (the modal's proven call), with honest Starting…/terminal rendering; FAILED keeps Retry only. G2: a failing upload row (unknown-household FK) now removes the already-written original + thumbnails (best-effort, logged) and returns a readable 422 ("unknown household: evidence cannot be stored"); unexpected failures return a clean 500; oversize keeps 413; the full-buffer read (F-SG180-10) is noted, not redesigned. G3: the modal accepts and names the backend's full set (PNG, JPG, WebP, TIFF, HEIC, PDF), pre-checks the 20 MiB cap client-side with the limit named, and the note states enforced reality ("…up to 20 MiB per file."); the stale DQ9 25 MB line is gone. No schema/migration, no new cancel writer, no provider/infra change, no production write, no restart.

model opencode-go/deepseek-v4.1-flash · effort max — read from own process args (/proc/2129026/cmdline: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`), PB-4. Served-model response metadata not available; no substitute claimed. `max` catalogue-valid, uncalibrated vs D120/D15-high (G-A9, stated).
Work dir /home/andrei/StorageGenie · branch automation · remote git@github.com:Andovol/StorageGenie.git.
BASE ref requested automation -> resolved acdf81f5003c3794da0ca6c4e15a4257d05d7ade (== local HEAD == origin/automation at start; clean). WORK_HEAD (product commit) 07d4ea8; evidence commit 6ebe555f0e36342acbb50c945943665039162aca (docs-only). This report lands in the receipt-paste commit and carries no hash of its own (CO-55b).

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim): "**Contract version: 0.47.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents."
Source readback: VERSION=0.47.0. `bash /home/andrei/storagegenie-contract/rules_check.sh` output verbatim: `G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract` / `G-L5 UNCHECKED gh-unauthenticated` / `G-L7 UNCHECKED gh-unauthenticated` / `G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275` / `G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933` / totals; exit 3 (reported as read, not re-run around). CODER_PRODUCTION.md declared surface: project has a live service, a datastore and a rendered surface; this slice's production interaction = the two health GETs only.

Health (CO-92): START 19:38:18Z HTTP 200 {"status":"ok","db":"ok","storage":"ok"} (SG-187_health_start.log); END 19:45:34Z HTTP 200 {"status":"ok","db":"ok","storage":"ok"} (SG-187_health_end.log) -> HEALTH: unchanged, OK.
Lane: unit dispatch-storagegenie@SG-187.service; runner pid 2128981; RUN_BUDGET_S=2100 (/etc/dispatch/storagegenie.conf); start epoch 1791919602 (btime 1785224168 + starttime 669543470 @100Hz) = 19:26:42Z; deadline 1791921702 = 20:01:42Z; elapsed at report writing 1791920790 = 19:46:30Z -> 1188 s of 2100.

(a) issues / deviations / surprises

1. PB-1 premises verified with corrections: modal is at components/shell/AssetImportModal.tsx — help promise at base :249-253 (packet said :252, within the block), `accept=` at :209, 25 MB comment at :16 — all confirmed. evidence.py catch-alls at base :85-91 (packet said :85-97; SG-186's shift). jobs.py replay at :39-44 IS already household-403 (confirmed FIRST READ; NOT re-repaired).
2. G1 route side already worked on base: the backend journey tests (CREATED -> /run -> AWAITING_REVIEW, foreign 403, run-on-FAILED stays FAILED) PASS on base too — they are controls, not FAIL arms. The G1 defect was purely the missing frontend control; its FAIL arm is the new InboxPage test (captured failing on base). Stated loudly per PB-3: no vacuous arm.
3. G2 failing baseline captured on the real route (SG-180 probe, disposable): BASE `upload_unknown_household_orphan_file` DEFECT_OBSERVED — 422 with the raw `(sqlite3.IntegrityError) FOREIGN KEY … [SQL: INSERT …]` detail and 3 orphan files (original + thumb256 + thumb512); CANDIDATE PASS — 422 "unknown household: evidence cannot be stored", orphan_files []. The new backend test fails on base at the raw-detail assertion and would also fail the no-orphan assertion; it passes on candidate.
4. G2 cleanup design: `_remove_written_artifacts` removes original + every configured thumbnail and attempts `rmdir` of the sha-prefix dir; a cleanup failure is logged (`exc_info`), never swallowed. In the IntegrityError race branch the existing "return the race row" behavior is preserved and the winner's file is kept when our path IS its storage key; only a distinct-path copy is removed. Unexpected (non-validation, non-IntegrityError) upload failures now answer a clean 500 instead of base's raw 422 — an intentional, reported widening of behavior; no test or probe relied on the old 422-raw for that branch.
5. G3 accepted set = the backend's (ALLOWED_MEDIA/config.allowed_mime_types): TIFF/HEIC/HEIF/PDF added to `accept=` and the client predicate; client size pre-check rejects >20 MiB naming the limit; the note reads "PNG, JPG, WebP, TIFF, HEIC or PDF, up to 20 MiB per file." — the DQ9 25 MB target line and its exports (DQ9_TARGET_MB/SERVER_CAP_MB) were removed; grep shows no other importer. Server remains authoritative (413 test preserved).
6. Cancellation (F-SG180-8): no cancel writer built. UI check: the only "Cancel" affordance is the modal's dialog-dismiss (discards staged files, closes; nothing advertised as a job cancel). No dishonest cancel text found to correct. JobCard left select-only — inspected, no card-level control demanded; the Start lives on the selected-job panel where the Retry precedent lives.
7. Authoritative invocation artifact (disclosed): the first authoritative backend invocation listed the two new files FIRST; test_assertions/test_assets_crud fixtures rely on being the first app importer (their `os.environ["DATABASE_URL"]` lands after app.db already bound the default relative sqlite URL and ./data/db is absent) -> 92 passed, 5 setup ERRORS. Re-run with test_evidence_upload.py (an env-setting module) first: 97 passed, 0 errors. Not product-caused; the same 5 files were green in the corrected order. This is a pre-existing test-isolation fragility of those files, reported not fixed (CO-16).
8. Screenshot harness (presentation hunk, CO-73): dependency-free static harness (esbuild bundle of the REAL component source + tokens.css, node_modules symlink) loaded by host Playwright-cache chrome-headless-shell 149. First capture was blank (import.meta.env undefined under esbuild iife) — one failed capture attempt, fixed with `--define:import.meta.env={}`, re-captured. Both shots opened and described below. Not the deployed app; no API request made by the harness.
9. CO-08 note: AGENTS.md's Values table binds no {{VENV}}/{{VTEST}}/{{EVIDENCE_DIR}}/{{MIGRATIONS_DIR}}; the harness used is backend/venv/bin/python -m pytest (established repo practice, SG-186 precedent) because the packet itself commands focused tests. Placeholder text was never used; nothing substituted silently.
10. No privileged op attempted (ALL optional environment/Docker probes excluded) -> no denial -> the PB-2 stop path was never reached; nothing routed around.
11. Constraints: write ceiling respected (backend evidence upload + jobs replay paths confirmed-not-changed, Inbox/modal/JobCard surfaces, focused tests, docs/worklogs/SG-187*); no schema/migration (no models/alembic change); no new cancel writer; no provider change; no production write (GETs only: two health probes); no paid call ($0, 0 provider calls); no infra change; no restart. Disposable DATABASE_URL/STORAGE_ROOT asserted pre-import (test modules; probe asserts temp root); no .env handled. Ordinary commands far under 120 s; focused runs 2-15 s (<600 s); no full suite; no watcher. Temporary helpers only under /tmp/opencode/sg187* (base worktree + harness), none in the repo tree.
12. Gates: ruff clean on the touched files; mypy app 41 errors / 9 files on BOTH base and candidate (no new errors; nothing silenced); tsc --noEmit clean (0 lines); eslint clean on the four touched frontend files.
13. Guard outcomes: PG-EV-01/02 (both FAIL arms captured failing on base: orphan+raw detail; Start absent; G3 wording/staging/cap) · PG-EV-03 n/a (no stop path) · PG-EV-04 n/a (no external request built) · PG-EV-05 properties stated throughout · PG-EV-06 no production rows created · PG-EV-07 fixtures drive the real routes · PG-EV-09 both FAIL/PASS captures committed · PG-EV-13 base worktree sets its own disposable env pre-import · PG-SC-01 read+write paths read before scoping · PG-SC-02 n/a (no new field) · PG-SC-03 n/a · PG-SC-09 criteria keyed to identity (row state, bytes on disk, route status) · PG-SC-10 nothing written into ignored paths · PG-SC-12 base worktree at the packet BASE commit, real routes/files · PG-IC-01 no blanket-constraint collision · PG-IC-07 no fixed time used · PG-IC-09 all premises re-verified against the tree · PG-DP-03 n/a (no owner-reported symptom; production GET-only) · PG-PR-01/03/04/07/10 no production write, no privileged touch, disposable state, no secrets.

(b) actions

- Work commit 07d4ea8 (8 files, +385/-15): backend/app/services/evidence_service.py (helper `_remove_written_artifacts` + row-failure cleanup/race-keep), backend/app/api/v1/evidence.py (IntegrityError -> 422 readable; unexpected -> 500 readable; import added), backend/tests/test_sg187_capture_journey.py (new, 2 tests), backend/tests/test_sg187_rejection_hygiene.py (new, 2 tests), frontend/src/components/shell/AssetImportModal.tsx (accepted set + 20 MiB pre-check + note), frontend/src/routes/InboxPage.tsx (run mutation + Start control), frontend/src/components/shell/import-modal.test.tsx (+3 tests), frontend/src/routes/InboxPage.test.tsx (+2 tests).
- Evidence commit 6ebe555f0e36342acbb50c945943665039162aca (docs-only: 4 focused logs, 2 authoritative logs, base/candidate SG-180 probe logs, mypy x2, ruff/tsc/eslint logs, health start/end, worklog, 2 screenshots). Receipt-paste commit (this report) follows; notes-ref receipt published last.
- Push: `acdf81f..6ebe555 automation -> automation` (exit 0); ls-remote readback refs/heads/automation = 6ebe555f0e36342acbb50c945943665039162aca. Notes: refs/notes/storagegenie-coder-reports readback = 6ebe555f0e36342acbb50c945943665039162aca (first line `Dispatch-ID: SG-187 | Report: docs/worklogs/SG-187_report.md`).
- External / production effects (CO-85): NONE with side effects — no deploy, restart, migration, provider/paid call, credential or infra change; production store untouched (GETs only: the two health probes). Disposable DB/storage for every test/probe; probe temp dirs under /tmp (sg180-g1-*) left in place, disposable.
- Durations (UTC, box clock): lane start 1791919602 = 19:26:42Z; orientation + FIRST READ + setup ~696 s (19:26:42 -> 19:38:18); implementation + focused FAIL/PASS + product commit 436 s (19:38:18 -> 19:45:34); authoritative runs + gates + probes + screenshots + evidence commit ~40 s; elapsed at report writing 1791920790 -> 1188 s of RUN_BUDGET_S=2100 (deadline 20:01:42Z). No single command over 60 s; no bound hit.
- Retry count 0 (no re-dispatch). Test-command count 7 pytest/vitest invocations (focused candidate x2, base FAIL x2, authoritative candidate backend x2 [first an invocation-order artifact, corrected], derived frontend x1) + 2 probe runs + 5 gates (ruff, mypy x2, tsc, eslint). Provider-call count 0; spend $0.000000. Failed prove executions: 1 (blank screenshot capture, fixed materially).
- Highest-impact action: the Inbox Start control (frontend/src/routes/InboxPage.tsx) closing the approved-but-broken SC-02/03 journey, plus the row-failure cleanup in backend/app/services/evidence_service.py closing the F-SG180-9 orphan.

(c) verification

FAIL half — candidate tests against BASE, isolated worktree /tmp/opencode/sg187-base @ acdf81f (tests copied in, never in-place; SG-187_fail_base_backend.log):

    $ venv/bin/python -m pytest -q -rA tests/test_sg187_capture_journey.py tests/test_sg187_rejection_hygiene.py
    E   AssertionError: assert 'FOREIGN KEY' not in '(sqlite3.In...e/e/20/gkpj)'
    E   'FOREIGN KEY' is contained here:
    E     (sqlite3.IntegrityError) FOREIGN KEY constraint failed
    E     [SQL: INSERT INTO evidence (...) VALUES (...) RETURNING created_at, updated_at]
    tests/test_sg187_rejection_hygiene.py:87: AssertionError
    1 failed, 3 passed, 2 warnings in 2.78s   exit=1
    (the 3 passed are the controls: G1 journey legs and the 413/422 caps — green on base too.)

FAIL half — frontend, same base worktree (SG-187_fail_base_frontend.log):

    $ vitest run --root /tmp/opencode/sg187-base/frontend src/routes/InboxPage.test.tsx src/components/shell/import-modal.test.tsx
    FAIL  src/routes/InboxPage.test.tsx > a CREATED job offers Start, calls /run, and shows the terminal state (SG-187 G1)
    FAIL  src/components/shell/import-modal.test.tsx > the size note states the enforced 20 MiB cap and the full accepted set
    FAIL  src/components/shell/import-modal.test.tsx > backend-accepted formats stage (TIFF, HEIC, PDF)
    FAIL  src/components/shell/import-modal.test.tsx > a file over the 20 MiB server cap is rejected client-side with the limit named
    4 failed | 23 passed (27)   exit=1

PASS half — focused candidate (SG-187_dev_pass_backend.log, SG-187_dev_pass_frontend.log):

    $ venv/bin/python -m pytest -q -rA tests/test_sg187_capture_journey.py tests/test_sg187_rejection_hygiene.py
    4 passed, 2 warnings in 2.01s   exit=0
    PASSED test_created_job_start_reaches_awaiting_review_with_foreign_403
    PASSED test_run_on_failed_job_stays_failed_and_retry_recovers
    PASSED test_unknown_household_upload_leaves_no_orphan_and_speaks_plainly
    PASSED test_oversize_413_and_mismatch_422_leave_no_files
    $ vitest run src/routes/InboxPage.test.tsx src/components/shell/import-modal.test.tsx
    Test Files 2 passed (2) · Tests 27 passed (27)   exit=0

PASS half — authoritative derived set on the candidate (PB-7: every file referencing store_evidence + the routes changed; SG-187_verify_candidate_backend.log, SG-187_verify_candidate_frontend.log):

    $ venv/bin/python -m pytest -q -rA tests/test_evidence_upload.py tests/test_sg187_capture_journey.py tests/test_sg187_rejection_hygiene.py tests/test_sg186_evidence_serve_integrity.py tests/test_sg080_ingest_pipeline.py tests/test_import_jobs.py tests/test_assertions.py tests/test_asset_facets.py tests/test_assets_crud.py tests/test_export.py tests/test_saved_searches.py tests/test_search.py tests/test_sg048_name_optional.py
    97 passed, 14 warnings in 12.35s   exit=0
    $ vitest run src/routes/InboxPage.test.tsx src/components/shell/import-modal.test.tsx src/components/JobCard.test.tsx src/routes/theme-adoption.test.tsx
    Test Files 4 passed (4) · Tests 41 passed (41)   exit=0

Gates:

    $ ruff check --no-cache app/api/v1/evidence.py app/services/evidence_service.py tests/test_sg187_*.py -> "All checks passed!"  exit=0  (SG-187_ruff.log)
    $ mypy app -> candidate 41 errors / 9 files == base 41 errors / 9 files  (SG-187_mypy_candidate.log, SG-187_mypy_base.log)
    $ tsc --noEmit -> 0 lines, exit=0  (SG-187_tsc.log); eslint touched files -> no output, exit=0  (SG-187_eslint.log)
    health start 19:38:18Z ok/ok/ok; end 19:45:34Z ok/ok/ok

G2 real-route baseline/after (SG-180_probe_g1.py, disposable state; SG-187_sg180_probe_base.log, SG-187_sg180_probe_candidate.log):

    base      upload_unknown_household_orphan_file  DEFECT_OBSERVED  status=422  detail="(sqlite3.IntegrityError) FOREIGN KEY constraint failed [SQL: INSERT INTO evidence ...]"  orphan_files=[original, thumb256, thumb512]
    candidate upload_unknown_household_orphan_file  PASS             status=422  detail="unknown household: evidence cannot be stored"  orphan_files=[]
    (candidate probe exit 1 is the known SG-185 replay-expectation line `cross_household_key_replay_returns_a_row` FAIL, unchanged from SG-186; base probe exit 1 likewise.)

Presentation evidence (CO-73, screenshots the audit reads; static harness mounts the REAL component source + tokens.css; not the deployed app; no API request):

    docs/worklogs/SG-187_shots/import-modal-760x900.png (35095 B) and import-modal-390x844.png (31985 B)
    opened and described: the "Import assets" dialog renders the dropzone help, and the note reads "PNG, JPG, WebP, TIFF, HEIC or PDF, up to 20 MiB per file." at both widths; no "25 MB" string appears; checkbox help "Checked: the import job is created and run immediately."; Pending queue (0); Cancel + Process 0 Items.

Owner checklist (CO-25, wording hunk): (1) note lists PNG/JPG/WebP/TIFF/HEIC/PDF and the enforced 20 MiB cap — no DQ9 25 MB claim; (2) TIFF/HEIC/PDF stage instead of being skipped; (3) an over-20-MiB file is skipped with "larger than the 20 MiB server limit"; (4) Inbox CREATED job shows Start import job; FAILED shows Retry failed job only.

INTENT: G1 — code posts `/v1/imports/{id}/run` from the Inbox Start control on CREATED only and renders the returned state honestly; the check expects CREATED->AWAITING_REVIEW via real route with foreign 403 and FAILED-stays-FAILED controls; the approved packet says exactly that — X, Y, Z agree. G2 — code removes written artifacts when the row fails and answers readable errors; the check expects no orphan bytes + non-raw detail + preserved 413; the packet says exactly that — X, Y, Z agree. G3 — code accepts/states the backend set and pre-checks 20 MiB; the check expects staging of TIFF/HEIC/PDF, rejection naming 20 MiB, and a note matching enforced reality; the packet says exactly that — X, Y, Z agree.

TWINS (CO-17; exact construct `except Exception` -> `detail=str(e)` into the client): 3 sites total in backend/app/api/v1; 2 handled in this slice (evidence.py's generic catch-all replaced; the FK path now an explicit readable IntegrityError branch); 1 out-of-scope: users.py:29-31 (409 with raw `str(e)`, household-create path — not a capture/import surface; reported). Other `except Exception` handlers (households.py:44, jobs.py:75, health.py, assets.py:433-506, chat.py, plugins.py, candidates.py, planning.py) put TYPED domain-exception text in `detail`, not raw database text — enumerated and classified, none changed. Adjacent construct reported: `store_text_evidence` also writes its file before the row flush; its docstring declares the file a deliberate harmless orphan cleaned with the temp DB — left as designed (out of scope).

UNCLEAR:
- FIRST READ: premises verified with the corrections in (a)1; the one judgment call: G1's "Start where the promise points" was implemented on the selected-job panel (the Retry precedent's home) rather than on JobCard — the packet names the Inbox surface, not a card control; JobCard was inspected and left select-only, reported.
- DURING EXECUTION: (i) unexpected upload exceptions now 500-clean where base answered 422-raw (no covered path depended on the old shape; disclosed in (a)4); (ii) the first authoritative invocation's ordering artifact (a)7 was corrected by re-ordering, not by touching tests; (iii) the blank screenshot capture was a harness bug (import.meta.env), fixed and re-captured — one failed prove execution on the visual criterion.
- REMAINING: (i) test_assertions/test_assets_crud import-order fragility (reported, CO-16); (ii) full-buffer upload memory shape F-SG180-10 noted, not redesigned (packet); (iii) no cancel writer, no cancel affordance to correct (F-SG180-8 out per packet); (iv) mypy 41/9 pre-existing debt -> canonical register; (v) Architect audit/rate before SG-188; no close, no deploy in this slice.
