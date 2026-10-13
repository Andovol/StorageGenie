SG-186 — R6 evidence-integrity detection repair: serve-time content verification + household-scoped evidence key replay — CHANGED

RESULT: CHANGED (CO-48 class 1). `GET /v1/evidence/{id}/file` now recomputes the stored bytes' sha256 and refuses a mismatch with an explicit 500 `evidence_integrity_error` (corrupt bytes never served, no fallback); the evidence upload's idempotency replay is qualified by the requesting household (SG-185 I1 sibling, same two-line shape confirmed on FIRST READ). Query-only for the sibling; no schema change and no migration — the comparison uses the existing `Evidence.sha256` column.

A1 PASS: same-byte-mutated fixture refused at serve time (500, explicit error; base served 200 + divergent sha); missing-original 404 and foreign-household 403 controls unchanged; SG-180 probe's `missing_original_controls` + `counter_control_missing_thumb_404` PASS both trees.
A2 PASS: per-read overhead measured on the real route (see (c)); every /file and /thumb consumer enumerated with coverage per caller — (a)3/(a)4.
A3 PASS: tests drive the real serve route on disposable storage (mutate → 500; delete → 404; pristine → 200 with sha match; corrupted row sha → 500 with `PRAGMA integrity_check`=ok); no placebo — the base half fails for the intended reasons, raw.
A4 PASS: first token SG-186; this file; FIRST READ / DURING EXECUTION / REMAINING below.

model opencode-go/deepseek-v4.1-flash · effort max — read from own process args (/proc/2053733/cmdline: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`), PB-4. Served-model response metadata not available; no substitute claimed. `max` catalogue-valid, uncalibrated vs D120/D15-high (G-A9, stated).
Work dir /home/andrei/StorageGenie · branch automation · remote git@github.com:Andovol/StorageGenie.git.
BASE ref requested automation -> resolved 91aacb7d44de24b2949ce80eb5c0150a92f71b17 (== local HEAD == origin/automation at start; clean). WORK_HEAD (product commit) 0dd037d832fac64f8cd699a670d7b3df13320ab8; evidence commit c009213150f0686801ec0939352ed1cc88c99931 (docs-only). This report lands in the receipt-paste commit and carries no hash of its own (CO-55b).

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim): "**Contract version: 0.47.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents."
Source readback: VERSION=0.47.0; sha256(RULES.md)=49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed == RULES.sha256 payload. CODER_PRODUCTION.md declared surface: project has a live service; this slice's production interaction = the two health GETs only.

Health (CO-92): START 19:11:15Z body {"status":"ok","db":"ok","storage":"ok"} (HTTP code lost to a -w format slip; re-captured 19:18:38Z HTTP 200; both in SG-186_health_start.log); END 19:19:27Z HTTP 200 {"status":"ok","db":"ok","storage":"ok"} -> HEALTH: unchanged, OK.
Lane: unit dispatch-storagegenie@SG-186.service; runner pid 2053624; RUN_BUDGET_S=2100 (/etc/dispatch/storagegenie.conf); start epoch 1791918601 (btime 1785224168 + starttime 669443334 @100Hz) = 19:10:01Z; deadline 1791920701 = 19:45:01Z; elapsed at report writing 1791919185 = 19:19:45Z -> 584 s of 2100.

(a) issues / deviations / surprises

1. PB-1 premises verified on target: base serve path trusts the DB row at evidence.py:101-104 (untouched since SG-006; d43d793 history); base replay at :25-26 IS the same two-line shape SG-185 fixed -> sibling taken in-slice per the packet's own conditional, not deferred.
2. GATE (semantic necessity, stated loudly per G2): verification applies to every `source_kind` EXCEPT `transcript`. `store_text_evidence` (SG-080) sets `sha256` to a composed artifact digest (household + source evidence + item index + text), not the bytes' hash — unrecomputable from the file alone; comparing it would 500 every legitimate transcript read (test_sg080's /file leg is real). Fail-closed for the future: every other kind is verified, so a new non-content-hash kind fails loudly (500), never skips silently. Residual: a tampered transcript file is served unverified; anchoring it needs a stored content hash (schema) or job-linked recompute — not reachable from the row. Exemption pinned by test_transcript_artifact_digest_rows_keep_serving (passes on base and candidate; control, not a FAIL arm).
3. Original-only coverage: thumbnails are derived artifacts with no row hash to compare against; the /thumb route is unchanged (pre-slice metadata trust). Residual: a tampered thumbnail is served 200; no anchor exists for derived files. Reported rather than silently narrowed.
4. TOCTOU residual: the file is hashed, then FileResponse re-reads the path; a mutation inside that window is not caught. Hash-then-FileResponse was chosen so response headers (ETag/Last-Modified/content-disposition) stay byte-identical to pre-change; an in-memory serve would close the window at a header-semantics cost. Documented residual, code comment at the site.
5. Global content addressing (pre-existing, out of scope, surfaced by the sibling work): `filter_by(sha256=sha)` (evidence.py:77; evidence_service.py:175/242) resolves identical bytes to the FIRST household's row — B uploading byte-identical content receives A's row JSON (201) and B's own GET /file on it is 403. Re-confirmed on the candidate by SG-180 probe `cross_household_sha_dedup_returned_a_row` PASS. This is the schema's global unique content address, not the key-replay path; fixing it is a schema/design decision — reported, not widened.
6. SG-180 probe expectation flip, labelled: `cross_household_key_replay_returns_a_row` FAILs on the candidate because the probe encodes the pre-fix semantics (B receives A's row) that SG-185/D4 + this slice deliberately changed; that single line is the candidate probe's exit 1. Its `same_size_corruption_served` flips DEFECT_OBSERVED (base 200 + divergent sha) -> PASS (500) — the existing real-route counter-control.
7. mypy pre-existing debt (not introduced): `mypy app` 41 errors / 9 files on BOTH base and candidate; evidence.py carries the same 4 errors both sides (+25 line shift). No new errors; nothing silenced with `type: ignore`. ruff on the touched files clean.
8. No privileged op attempted (ALL optional environment/Docker probes excluded) -> no denial -> the PB-2 stop path was never reached; nothing routed around.
9. PB-3 vacuity: no arm vacuous — the FAIL half is a captured genuine failure (B received A's id raw; mutation + corrupted-row legs served 200 on base); the PASS half asserts own-row identity, persisted key/row state, and real-route statuses; controls (pristine 200/sha match, delete 404, transcript 200) run on both trees.
10. Constraints: write ceiling respected (evidence.py + focused test + docs/worklogs/SG-186*); no schema/migration (no models/alembic change in the commits); no frontend change; no production write; no paid call ($0, 0 provider calls); no infra change; no restart. Disposable DATABASE_URL/STORAGE_ROOT asserted pre-import (test module lines 19-23; probe asserts too); no .env handled. Ordinary commands far under 120 s; focused run 11.27 s (<600 s); no full suite; no watcher.
11. Guard outcomes: PG-EV-01/02 (mutated-byte and corrupted-row gates seen to fail on base; artifacts verified by post-state), PG-EV-03 n/a (no stop path needed), PG-EV-04 n/a (no external request built), PG-EV-05 properties stated throughout, PG-EV-06 no production rows created, PG-EV-07 fixtures drive the real routes, PG-EV-09 both FAIL/PASS captures committed, PG-EV-13 base worktree sets its own disposable env pre-import (no secret file copied), PG-SC-01 read+write paths read before scoping, PG-SC-02 n/a (no new field), PG-SC-03 n/a, PG-SC-09 criteria keyed to identity (bytes vs row sha; benign drift cannot move them), PG-SC-10 nothing written into ignored paths, PG-SC-12 base worktree at the packet BASE commit, real routes/files, PG-IC-01 no blanket-constraint collision, PG-IC-07 no fixed time used, PG-IC-09 all premises re-verified against the tree, PG-DP-03 n/a (no owner-reported symptom; production GET-only), PG-PR-01/03/04/07/10 no production write, no privileged touch, disposable state, no secrets.

(b) actions

- Work commit 0dd037d832fac64f8cd699a670d7b3df13320ab8 (8 files, +661/-1): backend/app/api/v1/evidence.py (+26/-1 net: helper `_stored_content_sha256`, `_ARTIFACT_DIGEST_SOURCE_KINDS`, replay qualification, serve-time compare -> 500 + warning log); backend/tests/test_sg186_evidence_serve_integrity.py (new, 4 tests); 6 SG-186 logs.
- Evidence commit c009213150f0686801ec0939352ed1cc88c99931 (docs-only: overhead probe, 2 overhead logs, 2 SG-180 probe logs, health start, worklog). Receipt-paste commit (this report + SG-186_health_end.log) follows; notes-ref receipt published last.
- Push: `91aacb7..c009213 automation -> automation` (exit 0); ls-remote readback refs/heads/automation = c009213150f0686801ec0939352ed1cc88c99931.
- External / production effects (CO-85): NONE with side effects — no deploy, restart, migration, provider/paid call, credential or infra change; production store untouched (GETs only: the two health probes). Disposable DB/storage for every test/probe; probe temp dirs under /tmp (sg180-g1-*, sg186-overhead-*) left in place, disposable.
- Durations (UTC, box clock): lane start 1791918601 = 19:10:01Z; orientation + FIRST READ + start health ~74 s (19:10:01 -> 19:11:15); implementation + FAIL/PASS + authoritative + gates + probes + push 510 s (19:11:15 -> 19:19:45); elapsed at report writing 1791919185 -> 584 s of RUN_BUDGET_S=2100 (deadline 19:45:01Z). No single command over 60 s; no bound hit.
- Retry count 0 (no re-dispatch; the base FAIL run was re-captured to its log, same demonstration). Test-command count 3 pytest invocations (base FAIL; candidate focused; candidate authoritative) + 4 probe runs + 3 gates. Provider-call count 0; spend $0.000000.
- Highest-impact action: the read-time sha256 comparison at backend/app/api/v1/evidence.py:143-157 — the only detector of same-length content corruption (F-SG182-2), now enforced on the serve path; sibling replay qualification closes the SG-185 I1 family on this surface.

(c) verification

FAIL half — candidate test against BASE, isolated worktree /tmp/opencode/sg186-base @ 91aacb7 (test copied in, never in-place; SG-186_fail_base.log):

    $ venv/bin/python -m pytest -q tests/test_sg186_evidence_serve_integrity.py   # workdir /tmp/opencode/sg186-base/backend
    >           assert b_body["id"] != a_id
    E           AssertionError: assert '01a136b1-ce59-7553-b6f2-bba3f9810fd4' != '01a136b1-ce59-7553-b6f2-bba3f9810fd4'
    tests/test_sg186_evidence_serve_integrity.py:158: AssertionError
    3 failed, 1 passed, 2 warnings in 1.44s   exit=1
    (failed: mutation leg served 200; corrupted-row-sha leg served 200; foreign-key leg returned A's row; the passed test is the transcript control, green on base too.)

PASS half — focused file on the candidate (SG-186_dev_pass.log):

    $ venv/bin/python -m pytest -q -rA tests/test_sg186_evidence_serve_integrity.py
    4 passed, 2 warnings in 1.53s   exit=0
    PASSED test_serve_refuses_same_length_mutation_and_keeps_missing_original_404
    PASSED test_serve_refuses_corrupted_row_sha_despite_ok_integrity_check
    PASSED test_foreign_household_key_never_returns_foreign_evidence_row
    PASSED test_transcript_artifact_digest_rows_keep_serving
    (the 2 warnings quote the warning-log lines: expected vs stored sha pairs for the two refusal legs)

PASS half — authoritative derived set on the candidate (PB-7 derivation: every test file that POSTs /v1/evidence or GETs /v1/evidence/{id}/file; SG-186_verify_candidate.log):

    $ venv/bin/python -m pytest -q -rA tests/test_sg186_evidence_serve_integrity.py tests/test_evidence_upload.py \
        tests/test_sg080_ingest_pipeline.py tests/test_sg127_followup_batch.py tests/test_sg130_png_thumb_backfill.py \
        tests/test_phase1_e2e.py tests/test_phase2_e2e.py tests/test_phase3_e2e.py
    82 passed, 2 warnings in 11.27s   exit=0

Gates:

    $ ruff check --no-cache app/api/v1/evidence.py tests/test_sg186_evidence_serve_integrity.py -> "All checks passed!"  exit=0  (SG-186_ruff.log)
    $ mypy app -> candidate 41 errors / 9 files == base 41 errors / 9 files; evidence.py same 4 errors both sides, +25 line shift only  (SG-186_mypy_candidate.log, SG-186_mypy_base.log)
    health start 19:11:15Z ok/ok/ok (code re-capture 19:18:38Z HTTP 200); end 19:19:27Z HTTP 200 ok/ok/ok

G2 overhead — real route GET /file, disposable state, PDF fixtures (SG-186_probe_overhead.py; SG-186_overhead_candidate.log, SG-186_overhead_base.log):

    size      candidate mean   base mean   delta      hash-only floor
    256 KiB   6.527 ms         6.346 ms    +0.181 ms  0.299 ms
    2 MiB     15.756 ms        13.780 ms   +1.976 ms  1.849 ms
    8 MiB     45.093 ms        38.166 ms   +6.927 ms  7.099 ms
    20 MiB    93.990 ms        78.466 ms  +15.524 ms 16.607 ms
    overhead ~= one sha256 pass over the bytes (~0.8-1.0 ms/MB); no gate needed — the /file route is a viewer/download path, thumbnails (the grid hot path) are untouched.

Existing counter-control rerun (SG-180_probe_g1.py, real route, disposable; SG-186_sg180_probe_candidate.log, _base.log): `same_size_corruption_served` base DEFECT_OBSERVED (200, served sha != row sha) -> candidate PASS (500); `missing_original_controls` PASS both (file 404, thumb 200); `counter_control_missing_thumb_404` PASS both; `cross_household_key_replay_returns_a_row` base PASS (old defect) -> candidate FAIL (intended semantics change, probe encodes the old expectation; candidate exit 1 is that single line); `cross_household_sha_dedup_returned_a_row` PASS both (global content addressing unchanged, (a)5).

INTENT: serve path does hash the stored bytes and refuse a row mismatch with an explicit 500; the check expects mutated-file and corrupted-row fixtures refused / pristine 200+sentinel sha / missing 404; the approved packet (D5, G1) says exactly that — X, Y, Z agree. Sibling: replay lookup does qualify by the requesting household and same-household replay returns the ORIGINAL row; the check expects B never to receive A's row and B's own bytes to produce B's own row; the packet's sibling block (SG-185/D4 shape) says exactly that — X, Y, Z agree.

TWINS (CO-17; exact construct `filter_by(key=`): 4 sites total, 2 fixed (assets.py:88 SG-185; evidence.py:59 here), 2 classified out of scope: jobs.py:45 (bare key yields a 409 rejection and the row read is household-checked — never returns a foreign row), households.py:24 (household creation has no requesting-household context). Adjacent `filter_by(sha256=sha)` family counted and reported in (a)5.

UNCLEAR:
- FIRST READ: no material ambiguity. Premises verified (serve path at base :101-104; replay shape at :25-26); the sibling IS the same shape so the packet's conditional takes it in-slice. One judgment call: the transcript exemption gate was not named by the packet but is forced by SG-080's artifact-digest design (re-verified at evidence_service.py:277-302 and by test_sg080's real /file read) — taken as a gate and reported at the site plus (a)2 rather than skipped silently.
- DURING EXECUTION: three recorded calls — (i) 500 for mismatch (server-side data corruption; explicit detail string); (ii) hash-then-FileResponse over in-memory serve to keep response headers byte-identical (TOCTOU residual in (a)4); (iii) the SG-180 probe's G1.4 expectation flip labelled as the intended semantics change, not a regression.
- REMAINING: (i) transcript rows serve without content verification — no recomputable anchor in the row; a schema-stored content hash needs a decision; (ii) thumbnails unverified (derived artifacts; no anchor); (iii) verify-to-send TOCTOU window; (iv) identical-byte cross-household sha dedup returns the first household's row (schema-level; needs its own grant); (v) mypy 41/9 pre-existing debt -> canonical register; (vi) Architect audit/rate before SG-187; no close, no deploy in this slice.
