SG-185 — household-scoped asset idempotency replay (D4, F-SG181-1) repaired — CHANGED

RESULT: CHANGED (CO-48 class 1). `post_asset` now qualifies the replayed row by the requesting household: backend/app/api/v1/assets.py:92 `if a and a.household_id == household_id:`. A foreign key behaves as a fresh key for the requester (own row created, payload honored); same-household replay — changed payload included — still returns the ORIGINAL row (documented in the comment beside the lookup; behavior unchanged). Query-only: NO schema change, NO migration — the only SQL stays IdempotencyKey.key (unique index, models/idempotency.py:14) + Asset.id (PK); the household check qualifies the already-fetched row, so no composite index is required (nothing to measure — no new predicate reaches SQL).

A1 PASS: two-household replay returns own rows both ways with 201s (B key -> B own row: id != A's, household_id == B, payload honored; A key -> A's original row); foreign GET/PATCH still 403 both directions (real routes).
A2 PASS: FAIL-then-PASS captured (base aebe695 run fails exactly at `assert b_body["id"] != a_id` — A's id returned to B; candidate passes); same-household changed-payload control documents original-row semantics; normal same-key replay returns the original row (test 2 + test_export.py::test_asset_idempotency_is_persisted_and_reused).
A3 PASS: no placebo — tests drive post_asset through real routes (TestClient on app.main) on disposable households and assert persisted rows: IdempotencyKey count==1 still mapping to A's asset id, one Asset per household, asset.create AuditEvent with household_id == B.
A4 PASS: first token SG-185; this file; FIRST READ / DURING EXECUTION / REMAINING below.

model opencode-go/deepseek-v4.1-flash · effort max — read from /proc/2040115/cmdline (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`), PB-4; never from a system-prompt identity line. Served-model response metadata not available; no substitute value claimed. `max` catalogue-valid, uncalibrated vs D120/D15-high (G-A9, stated).
Work dir /home/andrei/StorageGenie · branch automation · remote git@github.com:Andovol/StorageGenie.git.
BASE ref requested automation -> resolved aebe695c7a0cd96c3725ab50640ef5adfa599cdc (fetch: == local HEAD == origin/automation; worktree clean at start). WORK_HEAD 341bd6946462dfafb8d4d5ba133a5c279b126f82 (10 files: assets.py fix + new focused test + 8 evidence logs). This report lands in the receipt-paste commit and therefore does not carry its own hash (CO-55b); no field here is "final HEAD".

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim): "**Contract version: 0.47.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents."
Source readback: /home/andrei/storagegenie-contract/VERSION=0.47.0; RULES.md sha256 49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed == RULES.sha256 (installed payload). rules_check.sh (host contract path) exit 3: G-L1 cache-not-at-checkout-tag + G-L5/L7 gh-unauthenticated — documented host shape (SG-184/SG-191/SG-192); no host tag/auth/config touched or repaired. CODER_PRODUCTION.md + PRODUCTION.md read (project declares a live service + live SQLite); this slice's production interaction = the two health GETs only.

(a) issues / deviations / surprises

- SG-185-I1 (G2 sibling map; reported, not widened): exact construct `rg "filter_by(key="` has 4 sites. Fixed: assets.py (this slice). Classified, not fixed: evidence.py:26 — same two-line shape and DOES return a foreign Evidence row (F-SG180-1/2/4 family; packet names this surface out of scope, tests not disturbed, reported as the found sibling); jobs.py:45 — led by Job.idempotency_key with a household check (403 mismatch) and the bare key yields only a 409 rejection, so it never returns a foreign row; households.py:24 — household creation has no requesting-household context, so this family cannot leak there; deps.py only forwards the header. list_assets base filter is already `Asset.household_id == household_id` (:277); archived-visibility D8 was NOT bundled (owner routed it to SG-188).
- SG-185-I2 (semantic consequence, documented per packet): IdempotencyKey.key is globally unique, so a foreign key cannot be re-registered by the requester — the key stays its first household's registration and every foreign-key POST creates a new own row (no replay dedup for that household). This IS the packet-chosen "fresh key for the requester" semantic ("implement the former"); named in the code comment and in REMAINING.
- SG-185-I3 (pre-existing gate debt, not introduced): `mypy app` (strict) = 41 errors / 9 files on BOTH base aebe695 and candidate; assets.py carries 16 on both sides (same error set, line numbers shifted +6 by the added comment). No new errors; nothing silenced with `type: ignore`. ruff on the touched files clean.
- SG-185-I4 (test-isolation pattern, CO-27 finding): the new test file repeats the module-level disposable-env setup + household fixture from test_assets_crud.py because the repo has no shared tests/conftest.py (per-file fixtures already repeat in test_export/test_signals/test_import_jobs). Shared-fixture extraction is outside this packet's ceiling; named, not taken.
- SG-185-I5 (unbound overlay names, CO-08 disclosure): lang/python.md uses {{VENV}}/{{VTEST}}/{{EVIDENCE_DIR}}/{{MIGRATIONS_DIR}}, none bound in AGENTS.md's Values table. Interpretation used: the repo's own conventions (backend/venv/bin/python -m {pytest,ruff,mypy}; Makefile lint/backend-test) — mechanically the same toolchain the Makefile binds; no migration exists in this slice. No secret substituted for any name.
- PB-3 vacuity: no arm is vacuous — the FAIL half is a captured genuine failure (B received A's id on base); the PASS half asserts own-row identity + persisted key/asset/audit rows; foreign 403 controls run through real routes.
- No denial encountered: no privileged op, no docker call, nothing outside this checkout's own git/python; ALL optional environment/Docker probes excluded per packet => the STOP-on-denial path was never reached (nothing routed around).
- No deviations from the packet constraints. Retry count 0; no command hit its bound; no watcher; no full suite. Guard IDs treated as the audit checklist; their substrate is (a)-(c) — no guard-relevant hazard (denial, production write, scope widening, vacuous pass) occurred.

(b) actions

- Work commit 341bd6946462dfafb8d4d5ba133a5c279b126f82 (10 files, +310/-3): backend/app/api/v1/assets.py (comment block + the one-line qualification); backend/tests/test_sg185_asset_idempotency_household.py (new, 2 tests); docs/worklogs/SG-185_{worklog,health_start,fail_base,dev_node,dev_pass,ruff,mypy_candidate,mypy_base}.log.
- Receipt-paste commit (this report + SG-185_verify_candidate.log + SG-185_health_end.log + worklog append), pushed immediately after; notes-ref receipt published last.
- Push: `aebe695..341bd69 automation -> automation` (exit 0); ls-remote readback refs/heads/automation = 341bd6946462dfafb8d4d5ba133a5c279b126f82.
- External / production effects (CO-85): NONE with side effects — no deploy, restart, migration, provider/paid call, credential or infra change. Production store untouched (no read, no write this slice); production interaction = two health GETs (start 19:01:23Z, end 19:03:50Z), both HTTP 200 {"status":"ok","db":"ok","storage":"ok"} -> HEALTH: unchanged, OK. Disposable DATABASE_URL/STORAGE_ROOT asserted pre-import in the test module (lines 19-23) before app import; the base worktree and every pytest run used them; no .env copied or touched (test env set via os.environ only).
- Durations (box clock UTC; lane start epoch 1791917908 = 18:58:28Z, source /proc/stat btime 1785224168 + PID 2040115 starttime 669374042 ticks @100Hz): orientation + contract/overlay reading + premise verification + start health 175 s (18:58:28 -> 19:01:23); implementation + FAIL/PASS + gates 147 s (19:01:23 -> 19:03:50: test authoring, base worktree FAIL run, the fix, dev node + touched-set runs, ruff, both mypy runs); authoritative verification + end health at 19:03:50Z; report + receipt as of report writing 19:05:22Z = epoch 1791918322, total 414 s of RUN_BUDGET_S=2100 (source: process environ; lane deadline 18:58:28Z + 2100 s = 19:33:28Z, PG-PR-06 actual-vs-budget). No single command over 60 s; no bound hit.
- Retry count 0. Test-command count 4 (1 base FAIL run + 3 candidate runs: exact node, dev touched-set, authoritative touched-set). Provider-call count 0; spend $0.000000 (no provider path touched; scripted-only expectation held trivially).
- Highest-impact action: the one-line household qualification in post_asset, which closes F-SG181-1 on the code path (serving it live is the runner's normal deploy, not this slice).

(c) verification

FAIL half — candidate test against BASE behaviour, isolated worktree /tmp/opencode/sg185-base @ aebe695 (candidate test copied in, never an in-place checkout; SG-185_fail_base.log):

    $ /home/andrei/StorageGenie/backend/venv/bin/python -m pytest -q tests/test_sg185_asset_idempotency_household.py   # workdir /tmp/opencode/sg185-base/backend
    >           assert b_body["id"] != a_id
    E           AssertionError: assert '01a136a4-8393-7771-9271-eee7da9f9e9a' != '01a136a4-8393-7771-9271-eee7da9f9e9a'
    tests/test_sg185_asset_idempotency_household.py:72: AssertionError
    1 failed, 1 passed, 2 warnings in 1.78s   exit=1
    (the one passed test is the same-household control, expected green on base too — control arm, not the FAIL arm)

PASS half + existing tests — committed candidate 341bd69, clean tree (SG-185_verify_candidate.log):

    $ git rev-parse HEAD -> 341bd6946462dfafb8d4d5ba133a5c279b126f82   (packet_BASE aebe695c7a0cd96c3725ab50640ef5adfa599cdc)
    $ python -m pytest -q -rA tests/test_sg185_asset_idempotency_household.py tests/test_assets_crud.py tests/test_export.py
    PASSED tests/test_sg185_asset_idempotency_household.py::test_foreign_household_key_never_returns_foreign_row
    PASSED tests/test_sg185_asset_idempotency_household.py::test_same_household_replay_returns_original_row_ignoring_changed_payload
    PASSED tests/test_assets_crud.py::test_manual_create_idempotency_detail_scoping_and_archive
    PASSED tests/test_assets_crud.py::test_asset_cursor_pagination_and_mixed_filters
    PASSED tests/test_assets_crud.py::test_list_rows_carry_evidence_ids_for_the_card_thumbnail
    PASSED tests/test_assets_crud.py::test_attach_evidence_bulk_dedups_and_logs_failed_links
    PASSED tests/test_export.py::test_export_manifest_is_complete_and_downloadable
    PASSED tests/test_export.py::test_export_manifest_restores_into_a_fresh_database
    PASSED tests/test_export.py::test_phase_zero_list_stubs_have_paginated_envelopes[/v1/jobs]
    PASSED tests/test_export.py::test_phase_zero_list_stubs_have_paginated_envelopes[/v1/review-tasks]
    PASSED tests/test_export.py::test_asset_idempotency_is_persisted_and_reused
    11 passed, 2 warnings in 2.37s   exit=0

Gates:

    $ ruff check app/api/v1/assets.py tests/test_sg185_asset_idempotency_household.py -> "All checks passed!"  exit=0  (SG-185_ruff.log)
    $ mypy app -> candidate 41 errors / 9 files == base 41 errors / 9 files; assets.py 16 both sides, identical set, +6 line shift only  (SG-185_mypy_candidate.log, SG-185_mypy_base.log)
    health start 19:01:23Z HTTP 200 ok/ok/ok; end 19:03:50Z HTTP 200 ok/ok/ok  (SG-185_health_start.log, SG-185_health_end.log)

INTENT: code does qualify the replayed row by the requesting household and create the requester's own row for a foreign key; the check expects B never to receive A's row and to receive its own with 201; the approved packet (D4, G1) says exactly that — X, Y, Z agree.

TWINS (CO-17; exact construct `filter_by(key=`): 4 sites total, 1 fixed (assets.py), 3 out-of-scope classified in (a) I1 — evidence.py same-shape (packet-declared out of scope), jobs.py rejects (403/409), households.py has no requesting-household context. No in-scope twin remains.

UNCLEAR:
- FIRST READ: no material ambiguity — premises verified as stated (global lookup :82; assets.py untouched since SG-136 8166e79; defect live in tree). The served defect was not re-probed because the path is POST-only and production was GET-only per packet.
- DURING EXECUTION: two judgment calls recorded: (i) G2's "fix a same-shape sibling" vs the packet's explicit out-of-scope naming of the evidence-key surface — resolved FOR the explicit naming (fix only post_asset; sibling reported); (ii) unbound overlay names {{VENV}}/{{VTEST}}/{{EVIDENCE_DIR}}/{{MIGRATIONS_DIR}} — used the repo's own toolchain/Makefile convention, flagged in I5.
- REMAINING: (i) a foreign-key POST creates a new own row every time for the non-owner household (no dedup there) — inherent to the globally unique key plus the D4 "fresh key" choice; per-household registration would need a schema change (household column + composite unique), deliberately not taken (query-only mandate). (ii) F-SG180 evidence-key family stays open on its own surface. (iii) archived-visibility D8 untouched, owned by SG-188.
