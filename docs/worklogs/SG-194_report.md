SG-194 — jobs.py cursor twin: malformed cursor is a 422 on GET /v1/jobs, never a silent page-1 repeat (CHANGED)

RESULT: CHANGED (CO-48 class 1). `list_jobs` (backend/app/api/v1/jobs.py:115-121) now mirrors the SG-188 cursor shape: a truthy-but-undecodable cursor (and the empty cursor) is refused 422 {"detail":"malformed cursor"} instead of silently repeating page 1; an absent cursor and a valid cursor walk behave exactly as before. Work commit 8a67ce3 (2 files, +149/-6); evidence commit e2e2693 (docs-only). This report lands in the receipt-paste commit and carries no hash of its own (CO-55b).

model opencode-go/deepseek-v4.1-flash · effort max — read from /proc/233513/cmdline (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`), PB-4; never from a system-prompt identity line. Served-model response metadata not available; no substitute claimed. `max` catalogue-valid, uncalibrated vs D120/D15-high (G-A9, stated).
Work dir /home/andrei/StorageGenie · branch automation · remote git@github.com:Andovol/StorageGenie.git.
BASE ref requested `automation` → resolved commit 03d24b466fded5342ff1c01da5ddc3077361939d (== local HEAD == origin/automation at start after fetch; worktree clean). WORK_HEAD (product commit) 8a67ce3f21bfbd7b21a3a8b52d7503ede3bfe84a; evidence commit e2e2693dbc31eb112b4588455c1101d69eaf1920.

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim): "**Contract version: 0.50.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents."
Source readback: VERSION=0.50.0 — identical to the packet's expected 0.50.0, NO difference. sha256(RULES.md)=49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed == RULES.sha256 payload (installed payload, clean). rules_check.sh output verbatim: `G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract` / `G-L5 UNCHECKED gh-unauthenticated` / `G-L7 UNCHECKED gh-unauthenticated` / `G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275` / `G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933` / `G-L6 BYTES total[codex]=2275 unseen=architect-layer,state-file,other-ritual-files` / `G-L6 BYTES total[opencode]=1933 unseen=architect-layer,state-file,other-ritual-files`; exit 3 (known shape, reported as read). CODER_PRODUCTION.md declared surface: live service + datastore + rendered surface; this slice's production interaction = the two health GETs only.

Health (CO-92): START epoch 1792097981 = 20:59:41Z 200 {"status":"ok","db":"ok","storage":"ok"}; END epoch 1792098210 = 21:03:30Z identical → HEALTH: unchanged, OK (SG-194_health_start.log, SG-194_health_end.log).

Lane: unit dispatch-storagegenie@SG-194.service; MainPID 233463; ExecMainStartTimestamp 2026-10-15 20:57:11Z (epoch 1792097831); RUN_BUDGET_S=2100 (/etc/dispatch/storagegenie.conf) → deadline 1792099931 = 21:32:11Z; elapsed at report writing (as of 1792098328 = 21:05:28Z) = 497 s of 2100 (23.7%).

(a) issues / deviations / surprises

1. PB-1 premises verified exactly on target: jobs.py:115-121 held `if cursor:` + `if decoded:` — a truthy-but-undecodable cursor skipped the filter and repeated page 1 (captured verbatim pre-fix in SG-194_ladder.log: 200 with the full page-1 body). The SG-188 shape is present in assets.py:301-311 and review_tasks.py:47-55. Construct was live; no STOP needed; nothing manufactured.
2. Twin census (CO-17): class = decode_cursor result tested for truthiness before gating the list filter. Total 3 call sites of decode_cursor in backend/app: 1 live (jobs.py:116, fixed here) + 2 already fixed (assets.py, review_tasks.py, SG-188) + 0 further sites (EXPECTED 1 + 2 held). Out-of-class, reported not widened: locations.py:115 (`cursor == location.id or cursor in seen` — Location-id string membership, no decode_cursor) and scene/openrouter.py:543 (`if decoded is None:` on a JSON payload, not a cursor).
3. Full suite is NOT all-green on this host — disclosed loudly (PG-EV-10): 722 passed, 2 failed, both in tests/test_signals.py (barcode/OCR). Both rows run ALONE on the base per D443: identical failure with the same host warnings (`Barcode extraction unavailable: pyzbar/libzbar is not installed`; `OCR extraction unavailable: tesseract is not installed or it's not in your PATH`) → host environment misses, base-identical, unrelated to this slice; comparison run committed (SG-194_base_reruns.log). CO-37 classification: environment (the measured mechanism is the warning lines at execution time; the test file's introducing commit is 8715d4e (SG-015) but no product commit is the cause). No count carried from an earlier slice (D443).
4. PB-3 vacuity (stated loudly): of the three new rows, two (absent-cursor first page, valid walk) pass on base AND candidate by design — they are the packet's "behavior unchanged" controls and discriminate nothing. The discriminating FAIL half is the malformed/empty-cursor row: base 1 failed / 2 passed, candidate 3 passed; both runs committed and signed.
5. No privileged operation attempted → no denial → the PB-2 stop path was never reached; nothing routed around. No sudo, no alternate identity/mount, no host config change; Docker never touched (docker.sock unused this slice).
6. Cross-project concurrency: a pip P515 dispatch (PID 210705) was in flight on the host during this slice — permitted, no interaction, no shared ref touched (SG-193-I4 precedent).
7. Constraints: write ceiling respected — diff is the jobs.py G1 hunk (+1 net line) + one new test module + docs/worklogs/SG-194* only; test_sg188_semantics.py NOT extended (a new module was sufficient; no coupling reason existed); no other route/service/schema/migration/config/frontend file. Production datastore never opened (two health GETs only; PG-EV-06: rows exist in disposable DBs only). Base leg ran in an isolated worktree at /tmp/opencode/sg194-base @ 03d24b4 with the main venv (SG-189 pattern), removed after; scratch logs moved into docs/worklogs/SG-194*. No secret in logs (none needed). Ordinary commands bounded 120 s; full suite bounded 600 s, used 59.04 s; no command killed; no visible timeout finding; idle kill 900 s never approached. No interactive prompt or polling loop.
8. Gates: ruff clean on the two touched files (exit 0); mypy app 41 errors / 9 files on candidate == base, error-site set identical modulo line shifts, jobs.py zero errors — no new error, nothing silenced (python.md gate). Frontend untouched → frontend suite not run (stated, not silently skipped).
9. Receipt: published on WORK_HEAD during this slice (transcript in (c)); the dual annotation on the receipt-paste commit is post-report by construction (CO-55b) and is not claimed inside this file.

(b) actions

- Work commit 8a67ce3f21bfbd7b21a3a8b52d7503ede3bfe84a (2 files, +149/-6): backend/app/api/v1/jobs.py (the G1 hunk: `if cursor is not None` + `if decoded is None: raise HTTPException(422, "malformed cursor")`; filter arithmetic untouched) and backend/tests/test_sg194_jobs_cursor.py (new, 142 lines, 3 tests, sg188-style disposable-DB fixture).
- Evidence commit e2e2693dbc31eb112b4588455c1101d69eaf1920 (docs-only, 12 files): ladder, focused pre-commit, focused base FAIL, focused candidate PASS, full suite, base reruns, ruff, mypy x2, health start/end, worklog.
- Push (observed at readback): 03d24b4..e2e2693 automation -> automation (exit 0); ls-remote readback refs/heads/automation = e2e2693dbc31eb112b4588455c1101d69eaf1920 (work commit 8a67ce3 contained).
- External / production effects (CO-85): NONE with side effects — production reads only (the two health GETs); no deploy, restart, migration, schema change, provider/paid call, credential or infra change; no .env handled; disposable DB/storage for every test.
- Durations (UTC box clock; source: lane ExecMainStartTimestamp + `date -u` stamps inside each committed log): orientation + FIRST READ + recon 203 s (20:57:11 → 21:00:34); implementation + focused pre-commit + work commit 26 s (→ 21:01:00); verification leg 144 s (21:01:06 → 21:03:30: base FAIL, focused PASS, full suite 59.04 s inside, base reruns, gates, health END); evidence commit + push + receipt + report as of 21:05:28Z; elapsed total as of report writing 497 s of 2100 (23.7%; deadline 21:32:11Z). Worklog freeze was at 21:03:44Z (393 s) — this file's figure supersedes it. No single command over 60 s (full suite 59.04 s, bound 600 s); no bound hit.
- Retry count 0 (no re-dispatch). Test-command count 6 pytest invocations (ladder 1, focused pre-commit 1, base FAIL 1, focused PASS 1, full suite 1, base rerun-of-2-nodes 1) + 3 gate commands (ruff x1, mypy x2). Provider-call count 0; application spend $0.000000 (no app spend exists on this path); platform spend not exposed — stated, not substituted. Failed prove executions 0 (the FAIL→PASS pair is one demonstration, CO-35).
- Highest-impact action: the jobs.py list-cursor 422 guard — the third and last live cursor twin closed, so a malformed cursor can no longer read as a valid empty page.

(c) verification

FAIL half — candidate test vs BASE, isolated worktree /tmp/opencode/sg194-base @ 03d24b4 (candidate test sha256 d3e07009e88f164dbc9ab293151721c82df6432534dcefbc1a5447059eb7a479 equal in both trees; SG-194_focused_base.log):

    $ venv/bin/python -m pytest -q -rA tests/test_sg194_jobs_cursor.py   (cwd=/tmp/opencode/sg194-base/backend)
    E   AssertionError: assert 200 == 422
    E    +  where 200 = <Response [200 OK]>.status_code
    tests/test_sg194_jobs_cursor.py:84 (malformed cursor: base returns page 1 silently)
    E   AssertionError: {"items":[{"id":"01a1415d-eca9-74f0-a38a-2b242f8ae869","job_type":"import","state":"CREATED",...}],"next_cursor":null,"total":1}
    1 failed, 2 passed, 2 warnings in 2.33s   exit=1
    PASSED tests/test_sg194_jobs_cursor.py::test_absent_cursor_is_first_page_unchanged
    PASSED tests/test_sg194_jobs_cursor.py::test_valid_cursor_walk_is_lossless

PASS half — focused candidate post-commit (CANDIDATE HEAD 8a67ce3 == published work commit; BASE echoed 03d24b4; SG-194_focused_candidate.log):

    $ venv/bin/python -m pytest -q -rA tests/test_sg194_jobs_cursor.py tests/test_import_jobs.py tests/test_export.py tests/test_sg127_followup_batch.py
    20 passed, 2 warnings in 4.85s   exit=0
    (new module 3 nodes: malformed+empty 422, absent first page vs db order, lossless 3-page walk over 25 tied-timestamp jobs;
     the other three files carry every existing /v1/jobs consumer)

Full suite on candidate (D443; SG-194_suite_candidate.log):

    $ timeout 600 venv/bin/python -m pytest -q -rA tests/
    2 failed, 722 passed, 32 warnings in 59.04s   exit=1
    FAILED tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier
    FAILED tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence
    -> both run alone on base 03d24b4 (SG-194_base_reruns.log): 2 failed in 1.23s exit=1, same rows,
       same cited mechanism: WARNING app.services.signals Barcode extraction unavailable: pyzbar/libzbar is not installed;
       WARNING app.services.signals OCR extraction unavailable: tesseract is not installed or it's not in your PATH

Gates:

    $ ruff check --no-cache app/api/v1/jobs.py tests/test_sg194_jobs_cursor.py -> "All checks passed!" exit=0 (SG-194_ruff.log)
    $ mypy app -> candidate 41 errors / 9 files == base 41 / 9; error-site diff empty modulo line numbers; jobs.py has no error entries (SG-194_mypy_candidate.log, SG-194_mypy_base.log)
    health start 1792097981 = 20:59:41Z 200 ok/ok/ok; end 1792098210 = 21:03:30Z 200 ok/ok/ok

Receipt (CO-60/CO-97; bound lane notes-ref; mapped refspec; transcript as executed):

    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
    local_tip_before=802d798f0112b8278d8bac9c664582b59c615192
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-194 | Report: docs/worklogs/SG-194_report.md | Work-HEAD: 8a67ce3f21bfbd7b21a3a8b52d7503ede3bfe84a" 8a67ce3f21bfbd7b21a3a8b52d7503ede3bfe84a
    add_exit=0
    $ git push origin refs/notes/storagegenie-coder-reports
       802d798..12e9e93  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    notes_push_exit=0
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg194-fetched
    $ git notes --ref=refs/notes/sg194-fetched show 8a67ce3f21bfbd7b21a3a8b52d7503ede3bfe84a
    Dispatch-ID: SG-194 | Report: docs/worklogs/SG-194_report.md | Work-HEAD: 8a67ce3f21bfbd7b21a3a8b52d7503ede3bfe84a
    show_exit=0
    remote notes tip: 12e9e93ae71df9951619ae89ee622354c6c9404e

The report-path check by the runner fires after this file is committed and pushed (the report did not exist at note time — same construction as SG-193's transcript). The dual annotation on the receipt-paste commit is republished after this file is committed — a post-report step by construction (CO-55b); its show output cannot appear inside this file. The retired finalizer was not used; no other publisher sought.

INTENT: G1 — code refuses an undecodable (and the empty) cursor on GET /v1/jobs with 422 `malformed cursor` and leaves absent/valid cursor behavior byte-identical; the check expects malformed+empty 422, absent first page in db order, lossless 3-page walk over 25 tied-timestamp jobs; the approved packet says exactly that. X=Y=Z.

TWINS (CO-17; class = decode_cursor result tested for truthiness before gating the list filter): 3 sites total in backend/app (all decode_cursor call sites); 1 live (jobs.py:116 — fixed in this slice), 2 already fixed (assets.py:302, review_tasks.py:48 — SG-188); 0 further sites. Out-of-class, reported not widened: locations.py:115, scene/openrouter.py:543.

acceptance
- A1 MET: malformed cursor → 422 {"detail":"malformed cursor"} on GET /v1/jobs (empty cursor too); valid/absent behavior unchanged — FAIL half on base + PASS on candidate, both committed (transcripts above; PG-EV-09).
- A2 MET: diff is the G1 hunk in jobs.py (+1 net line) + one new test module only (git diff --stat 03d24b4..HEAD: 2 files, +149/-6); twin census reported (1 live + 2 already fixed + 0 new); full backend suite run once on candidate — 722 passed, 2 failed, both failures proven base-identical by the D443 single-row base rerun; frontend untouched and unrun (stated, not silent).
- A3 MET: 11 committed logs + worklog + this report; elapsed per leg vs the ~300 s expectation (uncalibrated, SG-189 basis): 497 s as of report writing — over the estimate, attributed in (b) (203 s orientation+FIRST READ, 26 s implementation+commit, 144 s verification, remainder freeze); constraints answered below; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-194.
- A4 MET: notes-ref receipt on refs/notes/storagegenie-coder-reports with first line `Dispatch-ID: SG-194 | Report: docs/worklogs/SG-194_report.md` + Work-HEAD; published, pushed (802d798..12e9e93, exit 0), mapped-fetch read-back verified (show transcript above); remote notes tip 12e9e93ae71df9951619ae89ee622354c6c9404e; branch pushes complete (origin/automation == e2e2693 + this report's commit); bound lane receipt used, never the retired finalizer.

constraints — every stated constraint answered
Scope ceiling jobs.py G1 hunk + one test module + docs/worklogs/SG-194* — answered (exact diff, (b) first line; test_sg188_semantics.py untouched, no reason existed). No other route/service/schema/migration/config/frontend file — answered (diff scope only; models/alembic empty). Production datastore never opened — answered (two health GETs; every test row in disposable SQLite; base worktree used its own temp engine). Ordinary commands bounded 120 s; visible timeout finding; never approach idle kill 900 s — answered (no command killed; full suite given its own 600 s bound, used 59.04 s; idle kill never approached). No interactive prompt or polling loop — answered (bounded one-shot commands only). No sudo, no alternate identity/mount, no host config change — answered (none used; zero denials; Docker untouched). No secret in logs — answered (health bodies, ids and hashes only; no credential needed or used). PG-EV-06 rows in disposable DBs only — answered. Twin census — answered (TWINS). Full suite per D443 — answered (once on candidate; base only the new rows' FAIL half + the 2 old failing rows alone; no carried count). Runtime-vs-lane budget seconds + source — answered ((b): 497 s of 2100 as of 21:05:28Z; source: lane timestamp + logged `date -u` stamps; platform spend not exposed, stated not substituted). PG-EV-02 (gate verifies the result) — answered (test-tree assertions on real routes; log files exist at cited paths). PG-EV-03 — n/a (no stop path reached, nothing to disclose-as-substitute). PG-IC-01 — answered (no criterion requires what the exclusions forbid; suite runs and health GETs are reads/executions). PG-IC-07 — answered (no fixed time used; created_at ties are fixture data, not wall clock). PG-IC-09 — answered (all packet premises re-verified on target, (a)1-2). PG-DP-02 — not triggered (restart: none; no deploy surface claimed). PG-PR-03 — answered (zero denials; no workaround used). PG-PR-06 — answered ((b) durations with sources).

skipped (CO-103) — frontend suites (no frontend file touched or in ceiling); extension of test_sg188_semantics.py (a new focused module was sufficient; stated, not silent); deploy/restart steps (packet: none); PG-DP-02 substitute (no deploy surface claimed).

State of the world: branch automation at e2e2693 + this report's receipt-paste commit; work commit 8a67ce3 contained; jobs.py cursor twin closed — all three list surfaces refuse malformed cursors; service untouched, running the pre-slice deployment (restart: none, by packet); production DB untouched; notes-ref receipt published and read back.

UNCLEAR
- FIRST READ: the packet's premise held exactly (construct live at 115-121; SG-188 shape in the two fixed files); contract expectation 0.50.0 matched the host with no difference; BASE == local HEAD == origin/automation, clean. Nothing needed interpretation.
- DURING EXECUTION: the 2 full-suite failures were classified environment after the D443 single-row base rerun produced the identical failure + the pyzbar/tesseract warnings (not assumed — measured). The focused pre-commit run (SG-194_focused_precommit.log) is ladder evidence, not the authoritative PASS half — the post-commit run is. The empty cursor ("" from `?cursor=`) was treated as malformed per the SG-188 shape; on base it silently repeated page 1, on candidate it is 422 — the packet's "undecodable" read as covering it.
- REMAINING: (1) the two environmental signal rows stay red on this host until libzbar/tesseract are installed — whoever owns host provisioning should see (a)3; (2) Architect audit/rating of this slice; (3) live serving of this repair is NOT part of this packet — the next close-out deploy rider serves it; (4) no close, no deploy, no restart in this slice (by packet).
