SG-139 report — green the suite: non-disabling fileConfig + dedup Row types, fail-then-pass

Dispatch-ID: SG-139
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git
BASE ref:    origin/automation
BASE commit: 0b1e05af3a73d41bc322fce4cda90e1688de2a58  (start HEAD; tree clean at start)
WORK_HEAD:   04fe4f544733cdf50bdaeb266d286404b2d99831  (worklog commit; receipt note target)
Model:       opencode-go/deepseek-v4.1-flash   (per process args /proc/76241/cmdline `--model`)
Effort:      high                              (per process args /proc/76241/cmdline `--variant high`)
Coder:       opencode  (env CODER=opencode; OPENCODE_PID=76241; RUN_BUDGET_S=2100)
Contract:    echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION` (published tip `f26dbd3`);
             `RULES.md` sha256 `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`
             equals payload `RULES.sha256`. Recorded 0.40.0 == published. (`.rules-cache/` absent on host.)
Spend:       real $0.000000 USD · zero metered calls · no serving · no rebuild/recreate · no migration.
Gates:       DATABASE none · Restart none · Deploy none. Role guard held (Coder only; no dispatch verb).
Guards:      PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-07 · PG-EV-09 · PG-SC-09 · PG-SC-12 · PG-IC-01
             · PG-IC-07 · PG-IC-08 · PG-IC-09 · PG-PR-03 · PG-PR-04 · PG-PR-06.

## 0. Method and evidence

- Two-fix micro-slice. Every premise in the packet was verified against the tree before building
  on it: the 44/10 mypy baseline, the exact 3-red failing set, and the env.py root cause all held.
- Fail-pre was run on the unmodified BASE and **committed before any edit** (`054f689`) per
  `PG-EV-09`. Fail-post was run after the two hunks; both captures live in
  `docs/worklogs/SG-139_verify.log` (pre in `054f689`, post in the WORK_HEAD commit).
- Tests run through the real suite (never a hand-rolled harness). No command was killed; each ran
  under its class bound. No vacuous pass: the pre-run exists, the mypy count carries its file list,
  and the green is an in-suite verbose PASSED line, not an isolation-only claim.
- Decided shape stated: `env.py` gets the one-kwarg call the packet expected; `dedup.py` gets the
  `Row`-aware annotation + import (no boundary conversion — the annotation now matches the value
  the query already returns).

## 1. G0 — fail-pre on BASE (commit `054f689`)

**Full backend suite (600s bound):**
```
FAILED tests/test_health.py::test_health_reports_database_failure - Assertion...
FAILED tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier
FAILED tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence - a...
3 failed, 623 passed, 32 warnings in 30.22s
```
- caplog red quoted: `assert 'Database health check probe failed' in ''` where `''` is
  `caplog.text` — exactly `caplog.text == ''` as predicted.
- `PG-IC-08` blast radius: the failing set is **exactly** the expected three; **no fourth red**.
- The 2 `test_signals` reds are base-proved environment reds (`PG-SC-12`), derived at base:
  `libzbar` shared library absent (`ImportError: Unable to find zbar shared library`) and the
  `tesseract` binary absent (`command -v tesseract` → not found).

**mypy + ruff on BASE:**
```
Found 44 errors in 10 files (checked 90 source files)     <-- packet expectation, exact
  16 app/api/v1/assets.py · 6 review_tasks.py · 6 households.py · 4 evidence.py
   3 app/services/dedup.py · 3 asset_service.py · 2 audit_service.py
   2 app/schemas/asset.py · 2 app/main.py · 1 app/models/base.py
ruff check app -> All checks passed!
git diff --stat HEAD -- backend/alembic/versions/ -> (empty)
```
The 3 `dedup.py` errors are the predicted `assignment` (`:52`), `union-attr` (`:59`) and
`arg-type` (`:159`).

## 2. G1 — fix + fail-post

**Hunk A — `backend/alembic/env.py:20`** (one line):
```diff
-    fileConfig(config.config_file_name)
+    fileConfig(config.config_file_name, disable_existing_loggers=False)
```
`logging.config.fileConfig` defaults to `disable_existing_loggers=True`; on every alembic config
load it set `app.api.v1.health.disabled = True` process-wide, so under full-suite ordering a
migration test earlier in the run killed the health logger before the caplog test asserted.
Passing `False` keeps the ini's own configuration while no longer disabling unrelated loggers.

**Hunk B — `backend/app/services/dedup.py`** (annotation + import only; no statement change):
```diff
+from sqlalchemy import Row
 from sqlalchemy.orm import Session
...
-    phash_rows: list[tuple[Observation, Asset]] | None = None,
+    phash_rows: list[Row[tuple[Observation, Asset]]] | None = None,
```
`db.query(Observation, Asset).all()` returns `list[Row[tuple[Observation, Asset]]]`; the old
annotation was false. `for row, asset in phash_rows` already unpacked a `Row` at runtime — only
the annotation now tells the truth. The `None` branch is unchanged.

**Fail-post — full suite (600s bound):**
```
FAILED tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier
FAILED tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence - a...
2 failed, 624 passed, 32 warnings in 31.49s
```
- Total reds == the 2 base-proved `test_signals` env reds only. `test_health_reports_database_failure`
  is NOT in the failing set.
- **In-suite green quoted** (verbose re-run): `tests/test_health.py::test_health_reports_database_failure
  PASSED [ 27%]`, with the same file's other two health tests PASSED and summary
  `2 failed, 624 passed, 32 warnings in 31.45s`. The test file was **not touched**.
- **Runtime behaviour unchanged:** targeted `test_health.py + test_dedup.py` → `7 passed` (the
  `_similar_matches` callers exercised through `test_dedup.py`).

**mypy back to pre-#20 count, with the file list:**
```
Found 41 errors in 9 files (checked 90 source files)
  16 assets.py · 6 review_tasks.py · 6 households.py · 4 evidence.py · 3 asset_service.py
   2 audit_service.py · 2 schemas/asset.py · 2 main.py · 1 models/base.py
```
delta `-3` (44→41); `dedup.py` carries **zero** errors; the 9-file list is exactly the base list
minus `dedup.py` — **no new file carries errors**. `ruff check app` → `All checks passed!`.

**Migration surface / logging intact:**
```
$ DATABASE_URL=sqlite:////tmp/opencode/sg139/alp.db alembic upgrade head   # temp DB
INFO  [alembic.runtime.migration] Running upgrade ... -> 20260924_sg114_relation ...
$ DATABASE_URL=sqlite:////tmp/opencode/sg139/alp.db alembic current
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
20260924_sg114_relation (head)
```
All 12 migrations apply and alembic migration logging still **emits** after the fix. `versions/`
diff vs BASE is empty (no version change). `alembic current` output is quoted above as required.

## 3. Findings

- **F1 — offline `alembic upgrade head --sql` exits 1 (pre-existing, unrelated).** It prints the
  expected INFO lines + 8 `Running upgrade` blocks, then dies at `app/services/fts.py:35`
  (`'MockConnection' object has no attribute 'exec_driver_sql'`) — an online-only API used in an
  offline run. Proven **not** caused by this slice: with the two hunks temporarily stashed back to
  BASE the identical command exits 1 with the same 8 upgrades and the same AttributeError. The
  packet's alternative proof, `alembic current` (online), works and is quoted. Scope ceiling forbids
  touching `fts.py`, so this is reported, not fixed.
- **F2 — budget units differ.** The packet states `2400s overall`; the lane's actual
  `RUN_BUDGET_S=2100`. The tighter of the two (2100s) is the real cap; the slice used ~360s.
- **F3 — packet premises confirmed, not bent.** 44/10 mypy exactly; the 3-error dedup set exactly
  the predicted codes; the failing set exactly the predicted three. No premise needed correcting.
- **F4 — "byte-identical served routes" is proven by non-membership, not by a byte diff.** The
  changed set is {env.py (alembic config, unserved), dedup.py (import + annotation only),
  verify.log}; no file under `app/api/` or `app/main.py` changed, and the full suite is green, so
  served-route behaviour is unchanged. Stated plainly so this is not read as a deeper proof than it is.
- **F5 — env reds are environment, not code.** `libzbar` shared library + `tesseract` binary are
  absent on this host; both were red on bare BASE and remain red, so they are not introduced or
  masked by this slice.

## 4. Actual vs budget (units = wall-clock seconds, live clock `PG-IC-07`)

| goal | budget | actual | unit |
|---|---|---|---|
| G0 recon + fail-pre suite + mypy/ruff + committed capture | ~600s class | ~148s | elapsed |
| G1 two hunks + fail-post suite (x2) + targeted + mypy/ruff | ~600s class | ~185s | elapsed |
| G2 worklog + report + receipt | ~200s | ~30s + receipt | elapsed |
| overall | packet 2400s / env `RUN_BUDGET_S=2100` | ~360s at report write | elapsed |

Real metered spend **$0.000000 USD**, zero metered calls, zero container execs. No command killed.

## 5. Receipt

- Work commit `WORK_HEAD = 04fe4f544733cdf50bdaeb266d286404b2d99831` (source fixes + the 3 worklog files), pushed to
  `origin/automation`; worktree clean (`CO-55`).
- No push to `storagegenie-evidence`; `{{RECEIPT_CMD}}` not run.
- Note added on WORK_HEAD on `refs/notes/storagegenie-coder-reports`, pushed, then re-fetched into
  the **mapped** local ref `refs/notes/sg139-verify` (a default fetch carries no notes; a bare
  refspec rewrites only FETCH_HEAD — mapped per `M20`). `show` output pasted verbatim below.
- Final tip dual-annotated with the same note (note-anchor inoculation, SG-092 precedent).
- `note=yes`

Executed output, pasted verbatim:
```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   0b1e05a..04fe4f5  automation -> automation
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-139 | Report: docs/worklogs/SG-139_report.md | Work-HEAD: 04fe4f544733cdf50bdaeb266d286404b2d99831" \
    04fe4f544733cdf50bdaeb266d286404b2d99831
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   9bafea1..4bfe2a1  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg139-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg139-verify
$ git notes --ref=refs/notes/sg139-verify show 04fe4f544733cdf50bdaeb266d286404b2d99831
Dispatch-ID: SG-139 | Report: docs/worklogs/SG-139_report.md | Work-HEAD: 04fe4f544733cdf50bdaeb266d286404b2d99831
```

## UNCLEAR

- **FIRST READ:** the slice read as a clean two-fix micro-slice and it was — both premises
  (44/10 mypy, exact 3-red set, env.py `disable_existing_loggers`) held on first contact. The only
  surprise was the offline `--sql` route dying on a pre-existing online-only migration API, which
  the packet had offered as one of two proof options.
- **DURING EXECUTION:** the `--sql` failure (F1) is real but pre-existing and outside the ceiling;
  I proved it by stashing the hunks back to BASE and reproducing it, then used `alembic current`
  (online) as the migration proof. The offline route is not usable end-to-end on this tree for
  reasons unrelated to logging.
- **REMAINING:** (a) the offline `alembic upgrade --sql` limitation (`fts.py:35`) is a standing
  pre-existing defect for whoever owns offline SQL generation; (b) the 2 `test_signals` reds remain
  environment gaps (`libzbar`, `tesseract`) by design; (c) this slice is unserved (no rebuild/
  recreate) per `PG-PR-04` — serving it needs an owner rider word.
