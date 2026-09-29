BLOCKED: acceptance criterion unreachable within the write ceiling — after the sg048 fix (which this slice does land), `upgrade head --sql` advances past sg048 but aborts at `20260917_sg068_saved_search.py:21` on `sa.inspect(op.get_bind()).has_table(...)` (`NoInspectionAvailable` for `MockConnection`); three further post-FTS revisions (`sg100:21`, `sg113:21`, `sg114:21`) carry the same offline-incompatible guard, none in the ceiling. "Any other write is a STOP."

# SG-147 — offline `--sql` end-to-end fix (sg048 in ceiling, unserved) — BLOCKED report

**Dispatch-ID:** SG-147
**Role:** Coder (never Architect — no dispatch verb run for any ID, no unit started or polled).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved commit):** `843e3d220daf4f339289d4f38337a5cbba40c5da`
(the ref and the resolved commit are stated separately — two fields, never one).
**WORK_HEAD:** `__WORK_HEAD__`
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` =
`f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c` (subject `Contract payload 0.40.0`); payload `RULES.sha256` =
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`. (`.rules-cache/` is absent on the
host — SG-145 F-SG145-1; the live checkout above is the contract path.)
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort
`high` — source `/proc/<opencode-run-pid>/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high # SG-147 …`. No system-prompt identity used.
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (local reads/greps, offline CLI
runs that open no database, one temp-DB online migration, one temp-DB suite).
**Live clock:** first capture `2026-09-29T11:19:52Z`; G0 drive ~11:05Z.
**Autonomy:** `L3` finish chain (slice P1, owner word "D1 - D2 both ok"). **DATABASE none, restart none,
deploy none.**

## Verdict: **BLOCKED** — the end-to-end criterion is unreachable while the ceiling holds

The sg048 fix the packet asked for **is implemented and correct** (detailed in G1): `_drop_fts` /
`_reinstall_fts` are offline-safe, the FTS rebuild is gated online-only, and both `batch_alter_table`
calls carry a complete `copy_from`, so the SQLite batch recreate now renders in `--sql` mode. The online
migrated schema is **byte-identical** to BASE and the full suite shows **no delta**.

**But `upgrade head --sql` still does not exit 0.** With sg048 fixed, the run now fails one revision
later, at `20260917_sg068_saved_search.py:21`:

```
File ".../20260917_sg068_saved_search.py", line 25, in upgrade
    if _has_table("saved_search"):
File ".../20260917_sg068_saved_search.py", line 21, in _has_table
    return sa.inspect(op.get_bind()).has_table(name)
...
sqlalchemy.exc.NoInspectionAvailable: No inspection system is available for object of type
<class 'sqlalchemy.engine.mock.MockConnection'>
```

The identical `_has_table` guard exists in **three more** post-FTS revisions:
`20260923_sg100_enrich_snapshot.py:21`, `20260924_sg113_location.py:21`,
`20260924_sg114_relation.py:21`. None of these files is in the write ceiling; per the packet, "**Any other
write is a STOP.**" Therefore the G2 criterion — exit 0 **and** all 7 post-FTS revision markers — cannot be
satisfied within the granted scope. This is a STOP recorded through the `BLOCKED:` commit path
(`PG-EV-03`), not disclosure alone.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| BASE already carries the SG-146 partial fix; remaining failure is sg048 | Confirmed: `fts.py:ddl_statements()` + sg017 offline branch present; sg048 aborts. | confirmed |
| sg048 `_drop_fts` `exec_driver_sql` at :36-40 | Confirmed. | confirmed |
| sg048 `batch_alter_table("asset")` at :55/:73 cannot render offline without `copy_from` | Confirmed (fixed in G1; batch now renders). | confirmed |
| BASE abort is the `copy_from` `CommandError` | **False at BASE.** The real CLI aborts *earlier*, at sg048:36 `exec_driver_sql` (`AttributeError: 'MockConnection'…`). The `copy_from` `CommandError` is SG-146's monkeypatch probe, i.e. the *next* failure after that line. | **CORRECTED** |
| emitted DDL is `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` | Confirmed (G0 stdout line 225). | confirmed |
| alembic single head `sg114` | `alembic heads` → `20260924_sg114_relation (head)`. | confirmed |
| suite 2/635 with 2 known base-reds | `2 failed, 635 passed` — the two `test_signals.py` env reds. | confirmed |
| fixing sg048 (+sg017) reaches exit 0 | **False.** A second class of offline offenders (4 post-FTS `_has_table` guards) blocks the chain; all outside the ceiling. | **CORRECTED** |
| packet's G2 expects all 7 post-FTS markers | Only 3 of 7 (sg025/sg035/sg048) emit; sg068 aborts before its marker. | **CORRECTED** |

## G0 — fail-pre reproduced at BASE (`PG-EV-08`, `PG-SC-12`)

Real CLI from `backend/venv`, offline (opens/writes no DB, 300s class):

```
$ cd backend && timeout 300 venv/bin/alembic upgrade head --sql
EXIT=1 · LINES=384 · SHA256=4f2615ab661e565165ba0007f5dc65b8ee8c2ad5dc233b10db1e1e4c467ef06c
AttributeError: 'MockConnection' object has no attribute 'exec_driver_sql'
  at 20260916_sg048_name_optional.py:36 → _drop_fts → upgrade:54
```

sg017's FTS DDL already emits (`CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts USING fts5(`, line 225).
STOP conditions checked: exit is **not** already 0, and observing it needed no live-DB write. G0 proceeds.

## G1 — sg048 offline-safe; online schema byte-identical (`PG-SC-01`)

Write path read first (sg048 in full, `fts.py`, sg017 offline branch); read path read (`env.py:28-32,47-48`).
The write path constrained the shape: `install_asset_fts` is shared by the online route, so the fix must
leave the online call untouched.

- **`backend/app/services/fts.py` (extended — stated):** added public `drop_statements()` returning the
  five teardown statements (triggers → table → view). `ddl_statements()` and `_ddl()` are **byte-identical**.
- **`20260908_sg017_fts.py` (adjusted — stated):** `downgrade()` now renders `drop_statements()` through
  `op.execute` when `op.get_context().as_sql`, else `exec_driver_sql` (F-SG146-5 symmetry; SG-147 asked to
  decide and report). `upgrade()` untouched.
- **`20260916_sg048_name_optional.py` (fixed):**
  - `_exec(statement)` — `op.execute` offline, `exec_driver_sql` online.
  - `_drop_fts()` loops `drop_statements()` through `_exec`.
  - `_reinstall_fts()` — offline renders `ddl_statements()` via `op.execute`; online keeps
    `install_asset_fts(bind, rebuild=True)` (the rebuild re-reads live rows and stays online-only).
  - `_asset_table(display_name_nullable)` builds the complete pre-state `asset` `Table` (all 11 columns,
    cascade FK, PK, `(CURRENT_TIMESTAMP)` server defaults, `ix_asset_household_id`) for
    `batch_alter_table(copy_from=…)`; both the upgrade and downgrade batch calls use it.
  - `downgrade()`'s live nameless-row guard is skipped in `--sql` mode (no connection to read rows); it
    remains active online.
- **Turn-on-two-facts established, not assumed:**
  1. *Rendering*: `op.get_bind()` offline is `MockConnection`; `op.execute` renders the batch + DDL. Proof
     (G2 stdout, sg048 block): `CREATE TABLE _alembic_tmp_asset (… display_name VARCHAR(300) … FK … )` →
     `INSERT … SELECT` → `DROP TABLE asset` → `ALTER TABLE _alembic_tmp_asset RENAME TO asset` →
     `CREATE INDEX ix_asset_household_id`.
  2. *Online byte-identity*: online `upgrade head` on a temp SQLite exits 0; the `sqlite_master` dump for
     `asset` (table DDL + indexes + triggers) diffs **empty** BASE vs fixed → `ONLINE SCHEMA IDENTICAL`.
     Because `copy_from` is used on both branches, the batch DDL is rendered by one code path, so online
     and offline renders are identical by construction (verified online-result-identical).
- **Online-equivalence rail:** targeted `test_sg048_name_optional.py` → `9 passed`; full suite
  `2 failed, 635 passed` == BASE (base-reds identical); `alembic heads` single `sg114` before == after.
  `PG-SC-11` sweep — every end-relative assertion over the chain, all head/rev-pinned and unchanged
  because no revision is added: `test_export.py:114-116` (`exports.ALEMBIC_HEAD` vs
  `ScriptDirectory.get_current_head()`), `test_sg048_name_optional.py:21,101`, `test_sg114_relations.py:29`,
  `test_sg113_locations.py:29`, `test_sg100_snapshot_persistence.py:33`; plus the `command.upgrade(…,"head")`
  call sites in `test_search.py`, `test_signals.py`, `test_foundations.py`, `test_saved_searches.py`,
  `test_candidates.py` (all resolve the live head, which is unchanged).
- **Symmetry render proof:** offline downgrades now render — `sg048:sg035` EXIT=0, `sg017:sg014` EXIT=0
  (both in the verify log).

## G2 — end-to-end offline test + gates (`PG-EV-01`, `CO-101`) — BLOCKED

- **Re-drive after the fix:** `alembic upgrade head --sql` → still **EXIT=1**, 462 lines, sha
  `ea0e8ebe7fd5ecb42e49292c1f5cc26d84ba084a4361466e52cb4290457948f1`. sg048 renders fully; abort moves to
  `sg068:21` (`NoInspectionAvailable`). Only 3 of the 7 post-FTS markers emit.
- **New test withheld — stated loudly.** The packet's test must assert exit 0 + the FTS DDL + all 7
  post-FTS markers. That cannot pass (4 out-of-ceiling offenders). Adding it would redden the suite
  (violating the blast-radius gate, `PG-IC-08`) or, as `xfail`, verify nothing. I therefore did not add a
  test and did not manufacture a vacuous one. The exact test shape is preserved for the re-packet in
  RECOMMENDED-NEXT. This is a deliberate non-delivery, not an oversight.
- **Seen-to-fail / seen-to-pass:** G0 is the seen-to-fail (exit 1). The within-ceiling fix has a
  seen-to-pass component — the sg048 block now renders (quoted above) — but no exit-0 pass exists.
- **Gates run:** ruff `All checks passed!`; mypy `41 errors in 9 files`, **none in the touched files**
  (SG-146 baseline 41 → delta 0); secret scan over the diff clean (no password/key/token pattern);
  `alembic heads` unchanged.
- **Blast-radius (`PG-IC-08`):** full-suite delta == +0 files (`2 failed, 635 passed`, base-reds
  identical). No hidden delta. No unrated write.

## Findings (all reported; ceiling honored)

- **F-SG147-1 (blocking, scope underestimate — the headline).** Four post-FTS revisions carry an
  offline-incompatible `sa.inspect(op.get_bind()).has_table(...)` idempotency guard:
  `20260917_sg068_saved_search.py:20-21`, `20260923_sg100_enrich_snapshot.py:20-21`,
  `20260924_sg113_location.py:20-21`, `20260924_sg114_relation.py:20-21`. `--sql` mode has no inspection
  system for `MockConnection`. None is in the ceiling → STOP. End-to-end exit 0 is unreachable until all
  four are made offline-safe (idiomatic fix: skip the guard when `op.get_context().as_sql`, or render
  through the migration context).
- **F-SG147-2 (premise correction).** At BASE the real CLI aborts at sg048:36 `exec_driver_sql`, **not** at
  the `copy_from` `CommandError` the packet quotes; that CommandError is SG-146's monkeypatch probe (the
  next failure after the raw-connection line). Both facts are real; the ordering matters for a re-packet.
- **F-SG147-3 (packet premise).** "fixing sg048 reaches exit 0" is false — the offline defect is a *class*
  with instances at sg068/sg100/sg113/sg114 in addition to sg017/sg048.
- **F-SG147-4 (carry-over).** `.rules-cache/` absent on host (SG-145 F-SG145-1); contract checkout is
  `/home/andrei/storagegenie-contract`.
- **F-SG146-5 (closed).** sg017 `downgrade()` is now offline-safe in the same shape as sg048; render proof
  in the verify log.

## Acceptance criteria — assessed

- **fixed:** FAIL. `upgrade head --sql` exits 1 (aborts at sg068); FTS DDL + sg048 batch now present, but
  only 3 of 7 post-FTS markers. Unreachable within the ceiling (F-SG147-1).
- **equivalent:** PASS for the landed change. Suite delta == +0 files with base-reds identical
  (`2 failed, 635 passed`); online `asset` schema byte-identical; heads unchanged. (Packet expected
  "+1 green file"; no test was addable — see G2.)
- **clean:** PASS. Diff is exactly the ceiling files: `fts.py`, `sg017_fts.py`, `sg048_name_optional.py`,
  plus the three `SG-147` worklogs.
- **No vacuous pass:** the drive was run twice against real CLI stdout; the suite was not skipped; the
  marker check is against real emitted SQL.

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}` (Coder report; the Architect publishes receipts).
- Note on WORK_HEAD, then `refs/notes/storagegenie-coder-reports` pushed and verified from a **mapped**
  fetch (`refs/notes/sg147-fetched`); executed output, verbatim:

```
__NOTE_SHOW__
```

- Final tip dual-annotated (note-anchor inoculation, SG-092 precedent); mapped fetch `show`, verbatim:

```
__NOTE_SHOW_FINAL__
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| G0 read-only `--sql` drive | offline CLI (300s class) | 300 s | < 3 s |
| G1 code reads + edits + re-drives | ordinary | 120 s | < 15 s |
| G1 online temp-DB migration + schema diff | ordinary | 120 s | < 3 s |
| G2 offline re-drive + downgrade renders | offline CLI (300s class) | 300 s | < 6 s |
| G2 full suite | suite class | 600 s | 32.1 s |
| G2 ruff / mypy / heads / secret / PG-SC-11 | ordinary | 120 s | < 20 s |
| G2 worklogs + commit + push | ordinary | 120 s | < 10 s |
| Receipt notes (add/push/fetch/show) | ordinary / notes-push | 120 s / 300 s | < 15 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | **~20 min wall** |

Actual-versus-budget per goal: well under every class; overall well under the 2400 s cap.
**Real metered spend $0.000000 USD, zero metered calls.**

## UNCLEAR

- **FIRST READ:** the packet (and SG-146's REMAINING) treated sg048 as the last offline blocker and the
  work as complete on fixing it. First contact with the tree after the sg048 fix showed a *second class* of
  offline offenders — the `sa.inspect(...).has_table` guards in four later revisions — so the accepted
  scope still cannot reach the accepted outcome.
- **DURING EXECUTION:** sg048 now renders end to end (its batch recreate included), but the run dies at
  sg068:21. All four `_has_table` offenders are one idiom (`sa.inspect(MockConnection)`), none fixable
  inside the ceiling.
- **REMAINING:** the end-to-end offline `--sql` fix needs (a) the write ceiling widened to
  `20260917_sg068_saved_search.py`, `20260923_sg100_enrich_snapshot.py`, `20260924_sg113_location.py`,
  `20260924_sg114_relation.py`, each `_has_table` made offline-safe (skip when `op.get_context().as_sql` or
  use the migration context), and (b) the G2 test asserting exit 0 + `CREATE VIRTUAL TABLE IF NOT EXISTS
  asset_fts` + the 3 `asset_fts_after_*` triggers + all 7 post-FTS markers. sg017 + `fts.py` + sg048 are
  already fixed in this commit.

## RECOMMENDED-NEXT

- **R1 (re-packet SG-148):** widen the ceiling to the four `_has_table` migrations above and make each
  offline-safe. Their guard exists only to make the revision idempotent against a hand-created DB; in
  `--sql` mode there is no DB, so skip it (`if not op.get_context().as_sql: if _has_table(...): return`).
  Acceptance unchanged: `alembic upgrade head --sql` exits 0; stdout contains
  `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` + the 3 triggers + all 7 post-FTS markers; the new test
  fails against the current BASE and passes after.
- **R2 (expectation):** the expected blast-radius for R1 is +1 green test file with base-reds identical
  (`2 failed, 635 passed` → `2 failed, 636 passed`).
- **Chain position:** SG-147 is blocked, so the finish chain
  (`docs/superpowers/plans/2026-09-29-roadmap-finish.md`) cannot continue to the hue verdict / close-out
  deploy on this slice's account. The landed change is benign and online-equivalent; no live deploy is owed
  (no served-code path changed — a migration's offline branches and a service helper only), and the packet
  bound Deploy: none.

**note=yes**
