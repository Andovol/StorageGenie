# SG-279 — One migration widens the candidate state constraint, so split and merge can work on a migrated database

SG-279 model=unknown; effort=unknown (process arguments/provider metadata unavailable within permitted reads; AGENTS.md policy is `model=opencode-go/muse-spark-1.3-contributor effort=xhigh`, not claimed as this run); working directory `/home/andrei/StorageGenie`; remote `git@github.com:Andovol/StorageGenie.git`; BASE ref `origin/automation`; resolved BASE commit `be8e209be5a0cc7543bcaf872a1e542e98fe1a1e`; WORK_HEAD `3179eacdd0bb9516990ad584d48088690bf5f876`.

Contract echo: `**Contract version: 0.56.0**` — `/home/andrei/storagegenie-contract/CODER.md` line 3; `AGENTS.md` records `0.56.0`; published `contract-v0.56.0` matches by version string. A different echo would be a finding; none observed.

Approval: owner, stage C, D16: *"D16 - ok."* Design from SG-277/SG-278 (`docs/worklogs/SG-278_report.md`; row in `docs/reviews/review-ledger.md`). Previous open item `docs/worklogs/SG-276_audit.md` I1 is this slice.

Elapsed: ~560 s wall (16:19–16:28 UTC) against ≈700 s expectation; under by ~140 s. Phases over 60 s: `make backend-test` 74.08 s host pytest + ~10 s image build/export (≈85 s total, `docs/worklogs/SG-279_backend_gate.log:36`). All other phases under 60 s: preflight <10 s, failing route run 3.98 s, passing route run 1.71 s, rehearsal 1.07 s, targeted 5-test run 2.49 s, new-file twice 2.39 s / 2.33 s, ruff <5 s, image `ls` <5 s.

## Changed files

Product (scope ceiling only):

- `backend/alembic/versions/20261102_sg279_candidate_state.py` (new) — `down_revision = "20261023_sg233_reminder"`, batch rebuild widens `ck_candidate_state` to seven states, downgrade restores five with pre-DDL refusal on `split`/`merged`.
- `backend/app/services/candidates.py` (Candidate model only) — adds `CheckConstraint("state IN ('proposed', 'accepted', 'edited', 'held', 'rejected', 'split', 'merged')", name="ck_candidate_state")` + import; no other logic touched (`git diff` 7 insertions, 1 deletion).
- `backend/tests/test_sg279_candidate_state.py` (new) — Alembic-to-head split/merge route tests with FKs on + fresh-session read-back, seven-state store + invalid refusal, model-vs-migrated parity.
- `backend/tests/test_sg279_rehearsal.py` (new, `noqa: C901`) — populated old-head rehearsal: upgrade/downgrade, schema/data/counts/FTS/integrity/FK checks, refusal branches, PG-EV-01 deliberate-alteration proof. This is the rehearsal script (a test file, stated here).

Evidence (`docs/worklogs/SG-279*` only):

- `docs/worklogs/SG-279_fail_routes.log` — route tests FAIL before change, naming `ck_candidate_state`.
- `docs/worklogs/SG-279_pass_routes.log` — same route tests PASS after change.
- `docs/worklogs/SG-279_rehearsal.log` — rehearsal output with actual text diff.
- `docs/worklogs/SG-279_backend_gate.log` — `make backend-test` (host + image).
- `docs/worklogs/SG-279_image_proof.log` — new migration present in `storagegenie-backend:prover`.
- This report `docs/worklogs/SG-279_report.md`.

Test counts (PG-IC-08, exact):

- Targeted: `test_sg279_candidate_state.py + test_sg279_rehearsal.py` — `5 passed`.
- New file twice (PG-DP-04): `test_sg279_candidate_state.py` run 1 `4 passed`, run 2 `4 passed`.
- Host gate: `786 passed, 2 deselected` (`SG-279_backend_gate.log:36`; prior baseline 777 passed + 5 new + 4 drift from head move = 786).
- Image proof: `2 passed, 6 deselected` (`tests/test_signals.py`, requires_native_libs).
- `make frontend-test` not run: no frontend file changed, none should.

Logs: all above committed beside this report. Contract echo above. G3 rider lines (one line each):

- New revision id: `20261102_sg279_candidate_state`.
- Alembic transaction: does NOT wrap the rebuild in a transaction on this SQLite — established from log `Will assume non-transactional DDL` (rehearsal + route logs), not remembered; `env.py:35-44` `begin_transaction` is overridden by SQLite impl.
- Alembic invocation that reached the temp file: `command.upgrade(_alembic_config(url), "head")` with `settings.database_url` monkeypatched to the temp `sqlite:///...` file (tests); rehearsal also uses `command.upgrade(config, "20261023_sg233_reminder")` to populate old head then `command.upgrade(config, "head")`.

Every UNCLEAR / REMAINING:

- UNCLEAR: process-argument model/effort unavailable within permitted reads — stated as unknown above, not guessed.
- REMAINING: none new. Live deploy is rider SG-280; this slice deploys nothing (PG-PR-05).

## G0 — Preflight

`DOCKER_CONFIG=/tmp/opencode/SG-279-docker-cfg` (writable; `/tmp` denied on lane so pre-approved `/tmp/opencode` used for docker config only; packet scratch used `output/SG-279-scratch`, removed by exact path, never `output/` or `output/dispatch`), `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-279/docker.sock`, `docker version` shows Server (29.9.2), `docker run --rm busybox true` rc 0. `PATH=$PWD/backend/venv/bin:$PATH` for every make/test. Health `curl -s http://127.0.0.1:8003/v1/health` 200 at start (`{"status":"ok","db":"ok","storage":"ok"}`) and 200 at end (same). Installed versions read, not remembered: SQLAlchemy 2.0.52, Alembic 1.19.1.

## G1 — The migration and the model

Enumerated states the code assigns (criterion, not list): `proposed` (`candidates.py:746` build, `:1366` split children, `dedup.py:205`, `enrich.py:256`), `accepted` (`api/v1/candidates.py:157`), `edited` (`:155`), `held` (`:138`), `rejected` (`:138`), `split` (`SPLIT_ORIGIN_STATE="split"`, `:1373`), `merged` (`MERGED_STATE="merged"`, `:1514`). Expected seven confirmed; no other assignment found. Existing tests store only `proposed`/`accepted`/`split`/`merged` (subset); no test stores a state outside the seven once the model declares it — no STOP.

- SQLite cannot alter CHECK in place: table rebuild via `op.batch_alter_table(..., copy_from=..., recreate="always")`, precedent `20260916_sg048_name_optional.py:117,138`. `fts.py:46-82` hangs view + three triggers on `asset`, not `candidate` — verified no view/trigger mentions `candidate`; workaround NOT imported.
- Batch CHECK handling (UNKNOWN established): SQLAlchemy 2.0.52 `inspect.get_check_constraints("candidate")` on old head returns the named CHECK, so batch keeps it on reflection unless explicitly dropped/recreated. Migration does explicit `drop_constraint(..., type_="check")` + `create_check_constraint(...)` both ways.
- No FK targets `candidate`: enumerated from migrated old-head `sqlite_master` + `PRAGMA foreign_key_list` of every table — zero incoming; `ReviewTask.subject_ref` is plain string (`models/review_task.py:14-18`). Dropping the table with FK enforcement on would not cascade to a child; still rebuilt via batch (copy, not drop), preserving rows.
- Alembic URL + FK enforcement: test points Alembic by monkeypatching `settings.database_url` to temp file + `config.set_main_option("sqlalchemy.url", url)`; `env.py:22-23` overwrites from `settings`, so the monkeypatch is the effective path (verified: head recorded as new revision in test output). Migration connection does NOT enforce FKs (no `app/db.py` listener; its engine is `engine_from_config` in `env.py:35-44`); app/test route engine DOES (`PRAGMA foreign_keys=1` asserted in fixture, `SG279_FK_PRAGMA=1`).
- Survivors: two `DateTime` `server_default (CURRENT_TIMESTAMP)` and indexes `ix_candidate_job_id`, `ix_candidate_household_id` (`20260908_sg014_candidate.py:29-37`) — verified unchanged via `PRAGMA table_info` + index SQL in rehearsal.

Downgrade restores five-state CHECK; with any `split`/`merged` row it raises `RuntimeError` before any DDL (online only; offline skipped like sg048) — revision/data/schema compared equal after refusal.

PG-SC-11 hits (`backend/` excluding `venv`, `__pycache__`): literal `20261023_sg233_reminder` in `test_sg279_rehearsal.py:20` (OLD_HEAD), `test_sg233_reminders.py:47` (shipped path), `20261023_sg233_reminder.py:3,14`, new migration `:4,15`; `"head"` in `test_sg048_name_optional.py:55,66,76,124`, `test_sg114_relations.py:54,77`, `test_search.py:242,255`, `test_signals.py:262,268`, `test_foundations.py:65,85`, `test_sg148_offline_sql.py:39`, `test_sg235_daily_caller.py:69`, `test_sg279_rehearsal.py:80,116,235,275`, `test_sg233_reminders.py:74,164,241`, `test_saved_searches.py:263,275`, `test_sg113_locations.py:49,68`, `test_sg279_candidate_state.py:66`, `test_sg100_snapshot_persistence.py:122,132`, `test_candidates.py:161,165`, plus dynamic `get_current_head` in `exports.py:23`, `test_export.py:114`, and `ALEMBIC_UPGRADE="... upgrade head"` in `test_runbook_commands.py:20`; `[-1]` only in list-indexing (`signals.py:197,202`, `scoring.py:76`, etc., none migration-relative); `latest` only in `expiry_engine` `_latest_*` (none migration-relative). No assertion made false by the append: all `"head"` upgrades now reach the new head by design (verified green); `test_sg148_offline_sql` still passes (chain still contains `-> 20260924_sg114_relation`); `test_export` uses dynamic head; none pin old head as latest.

## G2 — Tests on a migrated schema

File `backend/tests/test_sg279_candidate_state.py` on one temp file built by Alembic to head, path + `ALEMBIC_HEAD` + `ALEMBIC_VERSION` printed (`-s` logs). Other tests keep `create_all`.

- Split + merge through routes with FKs on, read back in fresh sessions: origin `split`, children `proposed`×2; loser `merged` (+`merged_into`), survivor `proposed`. Routes commit at `candidates.py:207,229`; seed session closed before routes, read-back via new `factory()` session.
- Seven states stored + `bogus` refused, each in own transaction (`commit` per state; `pytest.raises(IntegrityError, match="ck_candidate_state")` then `rollback`).
- Parity: `Candidate.__table__` `ck_candidate_state` vs `sqlite_master` CHECK, both parsed to seven sets, asserted equal.

FAIL before (no migration/model): both route tests error `sqlite3.IntegrityError: CHECK constraint failed: ck_candidate_state` (`SG-279_fail_routes.log`). Any other failure would have meant wrong test — not observed. PASS after: `2 passed` (`SG-279_pass_routes.log`).

## G3 — Rehearsal

Script: `backend/tests/test_sg279_rehearsal.py` (stated here); output `docs/worklogs/SG-279_rehearsal.log`. Temp DB populated at old head via migrations to `20261023_sg233_reminder` (never `create_all`); five candidates (all old states) + real asset `RehearsalBrush Toothbrush` found by FTS.

Compared before/after from raw `sqlite_master` + raw column values:

- Every candidate column of every row (ordered `SELECT ... ORDER BY id`), timestamps as stored — identical.
- Indexes (`ix_candidate_*` SQL identical), FKs (semantic set identical; PRAGMA id order swap noted as non-semantic), `table_info` (columns/defaults identical).
- Every other object's definition identical except `candidate` table; all table row counts identical; FTS view + three triggers identical and present both sides.
- FTS search `asset_fts MATCH '"RehearsalBrush"'` returns seeded asset both sides.
- `integrity_check=[ok]`, `foreign_key_check=[]` after upgrade.

Actual text diff (`candidate` table only):

```diff
-CREATE TABLE candidate (
+CREATE TABLE "candidate" (
-	CONSTRAINT ck_candidate_state CHECK (state IN ('proposed', 'accepted', 'edited', 'held', 'rejected')),
-	FOREIGN KEY(job_id) REFERENCES job (id) ON DELETE CASCADE,
-	FOREIGN KEY(household_id) REFERENCES household (id) ON DELETE CASCADE
+	CONSTRAINT ck_candidate_state CHECK (state IN ('proposed', 'accepted', 'edited', 'held', 'rejected', 'split', 'merged')),
+	FOREIGN KEY(household_id) REFERENCES household (id) ON DELETE CASCADE,
+	FOREIGN KEY(job_id) REFERENCES job (id) ON DELETE CASCADE
```

Beyond the accepted set: quoting (`candidate` → `"candidate"`) and FK clause order swap only. Why only that: FK semantic set proven identical via PRAGMA set comparison; quoting is SQLite batch-rendering, no semantic change; remainder after removing CHECK + FKs is byte-identical after whitespace normalisation (logged `SG279_NO_CHECK_*`). No semantic STOP.

Downgrade success (no new-state rows): back to `20261023_sg233_reminder`, five-state CHECK restored, data intact. Refusal with `split` row and again with `merged` row: `RuntimeError` before DDL, revision/data/schema compared equal (not assumed).

PG-EV-01: same row comparison fails on deliberately altered state (`held` → `bogus-altered`) and same object comparison fails on altered trigger — both shown once in log.

## G4 — Gate

Targeted first: `5 passed`. Then `make backend-test` once: host `786 passed, 2 deselected` + image `2 passed` (green). `make frontend-test` not run: no frontend file changed. Image proof: `/app/alembic/versions/20261102_sg279_candidate_state.py` present in `storagegenie-backend:prover` (`SG-279_image_proof.log`). New file run twice: `4 passed` + `4 passed`. `ruff check` on all changed files clean (`All checks passed!`); repo-wide mypy reds out of scope.

## Acceptance

- A1 — Split + merge through routes commit on Alembic schema, read back fresh: PASS (`SG279_SPLIT_OK`, `SG279_MERGE_OK`).
- A2 — FAIL names `ck_candidate_state`, PASS after; both logs committed: PASS.
- A3 — Enumerated seven equals constraint set; invalid refused; model/migrated agree: PASS.
- A4 — Rehearsal shows values/counts/FTS/integrity/FK clean; deliberate alteration fails once: PASS.
- A5 — Downgrade succeeds clean, refuses with either new state leaving everything unchanged: PASS.
- A6 — PG-SC-11 hits listed; host green; new file twice; counts quoted; ruff clean: PASS.
- A7 — Scope only listed files; zero live-DB/host/container/deploy/Dockerfile/compose/lockfile/dependency/provider bytes; no deploy, no migration vs non-temp file; rows only in temp files: PASS.
- A8 — Preflight proven before gate; health 200 start + end: PASS.
- A9 — PB-3 vacuity: route error naming constraint (checked in FAIL log), missing index (checked `cand_idx`), changed value (checked `cand_rows`), lost row (checked counts) — none observed: PASS.
- A10 — Ends `Verification: PASS`: see last line.

Constraints: PB-1–PB-6 bind (CODER.md §14); DATABASE temp only — obeyed; restart none — obeyed (live stays as-is per PG-PR-05); provider none — obeyed; contract chain 0.56.0 — echoed; approval D16 — recorded; no second copies; sensitive areas untouched (no photos/files/DB/key/host); health probe at start/end; second-opinion rule N/A (no 🟠/🔴 to owner); artifacts rule N/A; coder scratch in `output/SG-279-scratch` removed by exact path; upload cap untouched; autonomy L3 respected (builder retry inside slice only; STOP would have been reported as success).

Next steps: rider SG-280 (non-mutating lane-rights check + live inventory first; denial STOPs; then backup/quiesced migration/recovery per D16).

Verification: PASS
