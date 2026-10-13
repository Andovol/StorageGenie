SG-188 — R3 + data semantics: resolve guard, cursor and archived visibility — CHANGED

RESULT: CHANGED (CO-48 class 1). G1: a bare (absent or {}) POST /v1/review-tasks/{id}/resolve of a data-required `expiry.manual_entry` task now answers 422 naming the missing field (`expiry_date`) while the task stays open and the lived assertion stays {"status":"unknown"}; the real manual-entry path (POST /v1/plugins/expiry-tracker/assets/{id}/expiry) still writes accepted data and returns resolved_review_task_ids. G2: a malformed/undecodable `cursor` is a 422 on GET /v1/assets and GET /v1/review-tasks (no silent page-1); default GET /v1/assets excludes ARCHIVED while explicit status=ARCHIVED still lists them; the expiry status engine ALREADY excluded non-ACTIVE assets (SG-111) — the packet premise is corrected in (a)1, no engine change exists in this diff, and that criterion's test passes on base too. No schema/migration; no UI change; no production write; no restart.

model opencode-go/deepseek-v4.1-flash · effort max — read from own process args (/proc/2161451/cmdline: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`), PB-4. Served-model response metadata not available; no substitute claimed. `max` catalogue-valid, uncalibrated vs D120/D15-high (G-A9, stated).
Work dir /home/andrei/StorageGenie · branch automation · remote git@github.com:Andovol/StorageGenie.git.
BASE ref requested automation -> resolved d7f6ba9906809357659454e6ea594a7aa6dc3c92 (== local HEAD == origin/automation at start; clean). WORK_HEAD (product commit) e911cdc; evidence commit 0f62d45c95cbce677d3c5bd6c0756a1dfaeea8a4 (docs-only). This report lands in the receipt-paste commit and carries no hash of its own (CO-55b).

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim): "**Contract version: 0.47.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents."
Source readback: VERSION=0.47.0. `bash /home/andrei/storagegenie-contract/rules_check.sh` output verbatim: `G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract` / `G-L5 UNCHECKED gh-unauthenticated` / `G-L7 UNCHECKED gh-unauthenticated` / `G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275` / `G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933` / `G-L6 BYTES total[codex]=2275 unseen=architect-layer,state-file,other-ritual-files` / `G-L6 BYTES total[opencode]=1933 unseen=architect-layer,state-file,other-ritual-files`; exit 3 (reported as read, not re-run around). CODER_PRODUCTION.md declared surface: project has a live service, a datastore and a rendered surface; this slice's production interaction = the two health GETs only.

Health (CO-92): START 200 {"status":"ok","db":"ok","storage":"ok"} read as the session's first command batch seconds after lane start (second-level timestamp not captured in the output — disclosed; bounded to lane start + first-command latency); END epoch 1791921798 = 20:03:18Z 200 {"status":"ok","db":"ok","storage":"ok"} (SG-188_health_start.log, SG-188_health_end.log) -> HEALTH: unchanged, OK.
Lane: unit dispatch-storagegenie@SG-188.service; MainPID 2161382; RUN_BUDGET_S=2100 (/etc/dispatch/storagegenie.conf); start epoch 1791921307 (ExecMainStartTimestamp 2026-10-13 19:55:07Z); deadline 1791923407 = 20:30:07Z; elapsed at report writing (start 1791921307 -> as-of 1791921857 = 20:04:17Z) = 550 s of 2100.

(a) issues / deviations / surprises

1. PB-1 premise correction (loud, PB-3): the packet's "no archived policy in compute_status" is WRONG on this tree. `compute_status` filters `lifecycle.active_clause()` (SG-111 ISS-2, expiry_engine.py:241-249); commit 3913381 introduced it and is an ancestor of the SG-181 base 785fe7d. Re-derived F-SG181-7 against the SG-181 probe itself: `SG-181_probe_g2.py:219` archives exp_x, and the `status_after_archive` log line shows the archived asset absent from rows AND unresolved_rows — the unresolved row is a different id (01a1360a-720d-...), the ACTIVE non-perishable, misattributed in the report as the archived row. No engine change was made; test_expiry_status_reports_archived_nowhere PASSES on base and candidate (captured in SG-188_focused_base.log). A2's "unresolved rows drop the archived row" is therefore VACUOUS on the base tree — declared, no diff manufactured to satisfy it.
2. Guard scope (stated decision, CO-04): refusal fires on a bare payload only (absent or {}), for task_type `expiry.manual_entry` — exactly the packet's accepted boundary; a resolve carrying any payload still closes the task as today, which keeps the approved candidate-level journeys (test_phase2/phase3_e2e resolve with {"resolution": "will enter manually"}) green in the authoritative set. A route that writes no data cannot accept "carry the date" without rewriting approved journeys; SG-173's planned wording was "refuse dataless resolution ... (409/422 with pointer)"; D7/the packet chose 422.
3. Cursor twins (CO-17): the exact falsy-cursor construct exists 3 times in backend/app/api/v1 — assets.py:294-304 (fixed), review_tasks.py:24-30 (fixed; file inside the write ceiling), jobs.py:116 (OUTSIDE the ceiling — reported, not changed).
4. Default-ARCHIVED exclusion lives in `list_assets` only; the shared `_apply_asset_filters` (which also backs `asset_facets`) is NOT changed, so facet counts keep the ARCHIVED bucket (the reachable-by-selection count). Stated boundary; the packet named the list surface.
5. Coupled tests updated under CO-38 with the approving slice named in-comment (SG-188/D8): test_assets_crud.py::test_asset_cursor_pagination_and_mixed_filters; test_search.py::{test_search_q_returns_exact_mixed_fixture_ids, test_search_q_rebuild_restores_matches, test_search_asset_type_returns_exact_mixed_fixture_ids, test_search_has_evidence_returns_exact_ids_for_both_polarities}. Expectations narrowed to the default-non-archived surface; explicit-ARCHIVED inclusion controls added. Both files FAIL on base against the candidate suite (captured).
6. mypy: candidate 41 errors / 9 files == base 41 / 9. Error-line diff shows the SAME sites, only line shifts from this slice's insertions (+7 assets.py, +24 review_tasks.py) — no new error, nothing silenced.
7. No privileged op attempted (ALL optional environment/Docker probes excluded) -> no denial -> the PB-2 stop path was never reached; nothing routed around.
8. Constraints: write ceiling respected (review_tasks.py, assets list/cursor path, expiry_engine.compute_status untouched, focused tests incl. coupled-test updates, docs/worklogs/SG-188*); no schema/migration (no models/alembic change); no UI change (no frontend file touched; CatalogPage untouched); no production write (two health GETs); no paid call ($0, 0 provider calls); no infra change; no restart. Disposable DB/storage: per-test temp engine + dependency override (SG-187 pattern) with temp storage_root monkeypatched; base worktree runs its own temp engine; no .env handled. Ordinary commands far under 120 s; focused runs 6-24 s (<600 s); no full suite; no watcher. Temporary helpers only under /tmp/opencode/sg188* (base worktree + raw logs), none left in the repo tree.
9. Gates: ruff clean on the five touched files; mypy counts above. No frontend touched -> no tsc/eslint run (stated, not silently skipped).
10. Guard outcomes: PG-EV-01/02 (both FAIL arms captured failing on base: bare resolve 200 {"status":"resolved"}; malformed cursor 200 page-1; archived id inside the default list) · PG-EV-03 n/a (no stop path) · PG-EV-04 n/a (no external request built) · PG-EV-05 properties stated throughout (25-row walk re-derived: 25 real rows, one tied timestamp set, 3 pages at limit=10; real routes only) · PG-EV-06 no production rows created · PG-EV-07 every fixture drives the real routes · PG-EV-09 both FAIL/PASS captures committed · PG-EV-13 base worktree at the packet BASE commit with its own disposable engine · PG-SC-01 read+write paths read before scoping · PG-SC-02 n/a (no new field) · PG-SC-03 n/a · PG-SC-09 criteria keyed to identity (row state, id sets, route status) · PG-SC-10 nothing written into ignored paths · PG-SC-12 base worktree at d7f6ba9, real routes · PG-IC-01 no blanket-constraint collision · PG-IC-07 no fixed time used (no wall-clock dependency; the engine test's `as_of` is a request parameter) · PG-IC-09 all premises re-verified against the tree (one corrected, (a)1) · PG-DP-03 n/a (no owner-reported symptom; production GET-only) · PG-PR-01/03/04/07/10 no production write, no privileged touch, disposable state, no secrets.

(b) actions

- Work commit e911cdc (5 files, +388/-28): backend/app/api/v1/review_tasks.py (DATA_REQUIRED_TASK_TYPES + `_missing_data_name` + 422 guard; list cursor 422), backend/app/api/v1/assets.py (list cursor 422; default ARCHIVED exclusion), backend/tests/test_sg188_semantics.py (new, 5 tests), backend/tests/test_assets_crud.py (coupled expectations + archived controls), backend/tests/test_search.py (coupled expectations + archived control).
- Evidence commit 0f62d45c95cbce677d3c5bd6c0756a1dfaeea8a4 (docs-only, 9 files): focused candidate/base logs, authoritative log, ruff, mypy x2, health start/end, worklog. Receipt-paste commit (this report) follows; notes-ref receipt published last.
- Push (observed at readback): `d7f6ba9..0f62d45 automation -> automation` (exit 0); ls-remote readback refs/heads/automation = 0f62d45c95cbce677d3c5bd6c0756a1dfaeea8a4.
- External / production effects (CO-85): NONE with side effects — no deploy, restart, migration, provider/paid call, credential or infra change; production store untouched (GETs only: the two health probes). Disposable DB/storage for every test/run.
- Durations (UTC, box clock): lane start 1791921307 = 19:55:07Z; orientation + FIRST READ + setup 304 s (-> 1791921611 = 20:00:11Z); implementation + focused FAIL/PASS + product commit ~109 s (-> commit 20:02:00Z); base captures + authoritative run + gates + evidence commit ~119 s (0f62d45 at 20:03:59Z); elapsed at report writing 1791921857 = 20:04:17Z -> 550 s of RUN_BUDGET_S=2100 (deadline 20:30:07Z). No single command over 60 s; no bound hit.
- Retry count 0 (no re-dispatch). Test-command count 3 pytest invocations (focused candidate x1, base FAIL x1, authoritative candidate x1) + 2 gate commands (ruff x1, mypy x2). Provider-call count 0; spend $0.000000. Failed prove executions: 0.
- Highest-impact action: the resolve guard in backend/app/api/v1/review_tasks.py closing F-SG181-3 (a data-required task could be closed with the data still unknown), plus the default ARCHIVED exclusion in backend/app/api/v1/assets.py.

(c) verification

FAIL half — candidate suite against BASE, isolated worktree /tmp/opencode/sg188-base @ d7f6ba9 (tests copied in, never in-place; SG-188_focused_base.log):

    $ venv/bin/python -m pytest -q -rA tests/test_assets_crud.py tests/test_search.py tests/test_sg188_semantics.py
    E   AssertionError: {"id":"01a136db-a4d1-7581-abb6-d087d1f5a70d","status":"resolved","subject_ref":"01a136db-a482-7bd0-a252-cd76ef8a6b34"}
    E   assert 200 == 422
    tests/test_sg188_semantics.py:101 (bare resolve: base closes the task 200 while the expiry data stays unknown)
    E   AssertionError: {"items":[{... "status":"ACTIVE" ...}], ...}
    E   assert 200 == 422
    tests/test_sg188_semantics.py:186 (malformed cursor: base returns page 1 silently)
    E   AssertionError: assert '01a136db-a768-...31c5' not in {'01a136db-a74f-...4d2a', '01a136db-a75f-...073b3', '01a136db-a768-...31c5'}
    tests/test_sg188_semantics.py:245 (archived id present in the default list)
    tests/test_assets_crud.py:64 (default walk includes archived on base)
    tests/test_search.py:97/157/193/226 (D8-coupled expectations)
    8 failed, 12 passed, 5 warnings in 6.42s   exit=1
    (passed on base: the two controls — non-perishable no task, identifier_collision bare resolve — AND test_expiry_status_reports_archived_nowhere, the declared-vacuous criterion, (a)1.)

PASS half — focused candidate (SG-188_focused_candidate.log):

    $ venv/bin/python -m pytest -q -rA tests/test_assets_crud.py tests/test_search.py tests/test_sg188_semantics.py
    20 passed, 5 warnings in 5.44s   exit=0
    PASSED tests/test_sg188_semantics.py::test_bare_resolve_refused_for_data_required_task_and_real_entry_resolves
    PASSED tests/test_sg188_semantics.py::test_controls_non_perishable_needs_no_task_and_non_data_task_resolves_bare
    PASSED tests/test_sg188_semantics.py::test_malformed_cursor_refused_and_valid_25_row_walk_is_lossless
    PASSED tests/test_sg188_semantics.py::test_default_asset_list_excludes_archived_and_explicit_filter_includes
    PASSED tests/test_sg188_semantics.py::test_expiry_status_reports_archived_nowhere

PASS half — authoritative derived set on the candidate (SG-188_authoritative_candidate.log; PB-7: every file driving the changed routes/symbols, test_evidence_upload.py first per the SG-187 a7 import-order precedent):

    $ venv/bin/python -m pytest -q -rA tests/test_evidence_upload.py tests/test_sg188_semantics.py tests/test_assets_crud.py tests/test_search.py tests/test_saved_searches.py tests/test_asset_facets.py tests/test_sg111_lifecycle.py tests/test_sg107_expiry_engine.py tests/test_plugin_expiry.py tests/test_candidate_read.py tests/test_dedup.py tests/test_ai_pipeline.py tests/test_phase1_e2e.py tests/test_phase2_e2e.py tests/test_phase3_e2e.py tests/test_export.py tests/test_schemas_common.py
    172 passed, 8 warnings in 23.91s   exit=0

Gates:

    $ ruff check --no-cache app/api/v1/assets.py app/api/v1/review_tasks.py tests/test_sg188_semantics.py tests/test_assets_crud.py tests/test_search.py -> "All checks passed!"  exit=0  (SG-188_ruff.log)
    $ mypy app -> candidate 41 errors / 9 files; base 41 errors / 9 files; error-line diff: same sites, line shifts only (+7 assets.py, +24 review_tasks.py)  (SG-188_mypy_candidate.log, SG-188_mypy_base.log)
    health start (session first command) 200 ok/ok/ok; end 1791921798 = 20:03:18Z 200 ok/ok/ok

INTENT: G1 — code refuses a bare resolve of `expiry.manual_entry` with 422 naming `expiry_date` and leaves task+assertion untouched, while the real /expiry path resolves with data; the check expects 422 + data still unknown + real-entry 200 with resolved_review_task_ids; the packet says exactly that — X, Y, Z agree. G2 — code 422s a malformed cursor on both list surfaces, excludes ARCHIVED from the default asset list while explicit status=ARCHIVED includes it, and the engine reports archived rows nowhere; the check expects exactly that; the packet says exactly that, with the compute_status half already implemented on base (premise correction, (a)1) — the implemented X for that half is "no change", Y and Z agree with the base behaviour.

TWINS (CO-17; exact construct `if cursor:` + `if decoded:` skipping the filter): 3 sites total in backend/app/api/v1; 2 fixed in this slice (assets.py, review_tasks.py); 1 out-of-scope: jobs.py:116 (same skip; file outside the write ceiling — reported, not changed). Data-required resolve callers enumerated: `store_manual_expiry` (expiry_tracker.py:498) writes the accepted assertion and resolves with data — untouched, green; `candidates.split` resolves `candidate.multi_item` — not a data-required type, untouched. No other route or service closes an `expiry.manual_entry` task.

UNCLEAR:
- FIRST READ: one packet premise corrected with measurement (a)1 (compute_status already ACTIVE-only; F-SG181-7 misattributed an ACTIVE non-perishable row as the archived asset). The word "ineligible" in G2 was read as the non-ACTIVE lifecycle rule the engine already enforces; the SG-181 probe's real observation (an ACTIVE non-perishable classified asset listed as `unresolved_rows` reason `dateless`) is left untouched — it is the SG-176/177/178-granted visibility scope (SG-175 T4) plus a semantic nobody decided here, and A2's operational criterion is the archived row. Declared rather than silently widened or silently dropped.
- DURING EXECUTION: (i) the guard is strictly bare-payload-scoped, per the packet's wording; the boundary (a resolution note still closes a data-required task) is stated in (a)2 so the audit can rule on it; (ii) four coupled search tests + one crud test were updated under CO-38 (SG-188/D8 named) rather than left failing against decided behaviour.
- REMAINING: (i) jobs.py cursor twin (out of ceiling); (ii) the non-perishable `unresolved_rows` observation stays with SG-176/177/178 / later decision; (iii) SG-176/177/178 grants untouched, not consumed; (iv) Architect audit/rate before SG-189; no close, no deploy in this slice.
