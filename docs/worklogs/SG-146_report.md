BLOCKED: acceptance criterion unreachable within the write ceiling — `upgrade head --sql` exit 0 requires a write to `20260916_sg048_name_optional.py` (not in the ceiling), which carries a *second* `exec_driver_sql` offender plus an offline-incompatible `batch_alter_table`; the packet's acceptance substring `CREATE VIRTUAL TABLE asset_fts` also has zero matches in the emitted SQL.

# SG-146 — offline `--sql` FTS fix (repo slice, unserved) — BLOCKED report

**Dispatch-ID:** SG-146
**Role:** Coder (never Architect — no dispatch verb run for any ID, no unit started or polled).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved commit):** `6edd1be775ed79f69819f50b7784dc09040beed4`
(packet's `BASE REF` is the ref; the resolved commit is stated separately — two fields, never one).
**WORK_HEAD:** `__WORK_HEAD__`
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c`
(subject `Contract payload 0.40.0`); payload `RULES.sha256` =
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`. (`.rules-cache/` is absent on the host —
SG-145 F-SG145-1; the live checkout is the path above.)
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort `high`
— source `/proc/878997/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie --model
opencode-go/deepseek-v4.1-flash --variant high # SG-146 …`. No system-prompt identity used.
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (local greps/reads, offline CLI
runs that open no database, one Alembic offline generation, one temp-DB suite).
**Live clock:** first capture `2026-09-29T10:56:17Z`; G0 drive ~10:53Z.
**Autonomy:** `L3` finish chain (slice P1, D1). No retry. **DATABASE none, restart none, deploy none.**

## Verdict: **BLOCKED** — the slice as packetized is impossible

The within-ceiling fix (sg017 + `fts.py` helper split) is correct and ships as partial progress: the FTS
DDL (view + `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts USING fts5` + 3 triggers) now renders offline,
online DDL bytes are untouched, and the suite shows no delta. **But the packet's acceptance criterion
cannot pass**, for two independent reasons found by executing:

1. **A second offender outside the ceiling.** `20260916_sg048_name_optional.py:36-40` `_drop_fts` also
   calls `connection.exec_driver_sql`. With sg017 fixed, `upgrade head --sql` advances to sg048 and
   aborts there with the identical `AttributeError`. The packet named only sg017 (SG-145 only ever saw
   the *first* abort). Fixing it means writing a file the ceiling forbids → per the ceiling,
   "Any other write is a STOP."
2. **sg048 is not a one-line fix.** Even with its `exec_driver_sql` made mock-safe, `op.batch_alter_table("asset")`
   (`:55`, `:73`) raises offline: `CommandError: … batch mode with dialect sqlite requires a live database
   connection … to reflect the table "asset" … copy_from`. A `--sql`-capable sg048 needs a substantive
   rewrite (e.g. `copy_from=`), far beyond "size S".
3. **The acceptance substring is wrong as written.** The emitted statement is
   `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts USING fts5(`; the packet's literal
   `CREATE VIRTUAL TABLE asset_fts` occurs **0** times. The G2 assertion, quoted verbatim from the packet,
   would fail even if both files were fixed.

Because criterion "fixed" (exit 0 + all 7 post-FTS markers) is unreachable while the write ceiling holds,
this is a STOP. The stop is recorded via this `BLOCKED:` commit path (`PG-EV-03`), not disclosure alone.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| `fts.py` calls `exec_driver_sql` at 35/42/53/63/75 | Confirmed (before edit). | confirmed |
| `sg017_fts.py:22` calls `install_asset_fts(op.get_bind(), rebuild=True)` | Confirmed. | confirmed |
| alembic single head `sg114` | `alembic heads` → `20260924_sg114_relation (head)`. | confirmed |
| suite 2/635 with 2 known base-reds | `2 failed, 635 passed` — the two `test_signals.py` env reds. | confirmed |
| the defect is the sg017 `_ddl` call only | **False.** `sg048` `_drop_fts` has the same defect, plus an offline-incompatible `batch_alter_table`. | **CORRECTED** |
| the replacement call renders under `MockConnection` | **Partially.** `op.execute` renders (proved); but sg048's `batch_alter_table` cannot render offline at all. | **CORRECTED** |
| packet substring `CREATE VIRTUAL TABLE asset_fts` appears | 0 matches; emitted text has `IF NOT EXISTS`. | **CORRECTED** |
| `.rules-cache/` is the contract cache | Absent on host (SG-145 F-SG145-1); live checkout is `/home/andrei/storagegenie-contract`. | finding (inherited) |
| BASE REF `origin/automation` | `= 6edd1be…` = start HEAD. | confirmed |

## G0 — fail-pre reproduced at BASE (`PG-EV-08`, `PG-SC-12`)

Real CLI from `backend/venv`, offline (opens/writes no DB, 300s class):

```
$ cd backend && timeout 300 venv/bin/alembic upgrade head --sql > …G0_offline_base.txt 2>&1
EXIT=1 · LINES=259 · SHA=827323e3df69b7122a889fae36f8d3310162c668dab0aff4252ef7b8aba9d686
AttributeError: 'MockConnection' object has no attribute 'exec_driver_sql'
  at 20260908_sg017_fts.py:22 → fts.py:104 → _ddl at fts.py:35
```
Byte-identical to SG-145's committed drive (same line count and sha256). Only 3 of 11 revisions emit.
STOP condition checked: exit is **not** already 0 at BASE, so the fail-pre is genuine; no live-DB write
was needed to observe it.

## G1 — offline-safe FTS path, online byte-equivalent (`PG-SC-01`)

- **Write path read first:** `fts.py` in full + `20260908_sg017_fts.py`; then read path: `env.py:24-32,47-48`
  (offline branch) and the FTS query at `assets.py` (no change needed). The write path *did* constrain the
  shape: `install_asset_fts` is shared by the route (online) and the migration, so the fix must be a
  helper split that leaves the online call untouched.
- **Mechanism established, not assumed:** `op.get_bind()` offline is `sqlalchemy.engine.mock.MockConnection`
  (`alembic/runtime/migration.py:23,36,672`, `MockEngineStrategy.MockConnection = MockConnection`), which
  has `.execute` but not `.exec_driver_sql`. `op.execute(str)` → `DefaultImpl._exec` with `as_sql=True` →
  `static_output` (`alembic/ddl/impl.py:209-237`). So `op.execute` renders offline. **Both** turning facts
  were established before choosing (rendering under the mock; online bytes unchanged).
- **Change (helper split — stated as required by the ceiling):**
  - `backend/app/services/fts.py`: new public `ddl_statements() -> tuple[str, ...]` holds the five strings;
    `_ddl` becomes `for statement in ddl_statements(): connection.exec_driver_sql(statement)`. The online
    path therefore emits the *identical* strings through the *identical* API — byte-equivalent by
    construction.
  - `backend/alembic/versions/20260908_sg017_fts.py`: `upgrade()` emits SQL through `op.execute` when
    `op.get_context().as_sql` (offline) and otherwise calls `install_asset_fts(op.get_bind(), rebuild=True)`
    — the `rebuild=True` backfill is gated online-only (it needs live rows).
- **Online-equivalence rail:** full suite `2 failed, 635 passed` == BASE (base-reds identical); targeted
  `test_search.py`+`test_sg048_name_optional.py`+`test_export.py` → `25 passed`; `alembic heads` single
  `sg114` before == after. `PG-SC-11` sweep listed in the verify log (`test_export.py:114-116`,
  `test_sg048_name_optional.py:21,101`, `test_sg100_snapshot_persistence.py:33`, `test_sg113_locations.py:29`,
  `test_sg114_relations.py:29`) — all head-relative/pinned, unchanged because no revision is added.

## G2 — offline test + gates (`PG-EV-01`, `CO-101`)

- **New test withheld — stated loudly.** The packet's test must assert exit 0 + the FTS DDL + all 7
  post-FTS markers. That cannot pass (sg048 aborts; substring mismatch). Adding it would either redden the
  suite (violating the blast-radius gate, `PG-IC-08`) or, as `xfail`, verify nothing. I therefore did not
  add a test and did not manufacture a vacuous one. The exact test shape is preserved for the re-packet in
  RECOMMENDED-NEXT. This is a deliberate non-delivery, not an oversight.
- **Seen-to-fail / seen-to-pass:** see below — the real CLI is the seen-to-fail (G0, exit 1) and the
  partial seen-to-pass (FTS DDL emits). Neither reaches exit 0.
- **Gates run:** ruff `All checks passed!`; mypy `41 errors` before == after (touched files absent from the
  error list → delta 0); credential-pattern scan clean (only the English word "token" in a docstring);
  `alembic heads` unchanged. Gate scope is quoted in the verify log.
- **Blast-radius (`PG-IC-08`):** full-suite delta == 0 files (2 reds identical to BASE, 635 green). No
  hidden delta. No unrated write.

## Findings (all reported; ceiling honored)

- **F-SG146-1 (blocking, premise defect)** — `20260916_sg048_name_optional.py` is a second
  `exec_driver_sql` offender. The packet scoped one migration; the offline chain has two. Ceiling forbids
  writing it → STOP.
- **F-SG146-2 (blocking, scope underestimate)** — sg048's `op.batch_alter_table("asset")` cannot run in
  `--sql` mode with SQLite without `copy_from=`; the fix is not a one-liner and the slice is not "size S"
  for end-to-end offline support.
- **F-SG146-3 (acceptance wording)** — the packet's literal substring `CREATE VIRTUAL TABLE asset_fts`
  never appears (emitted text is `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts`). Any re-packet should
  assert the actual emitted text.
- **F-SG146-4 (carry-over)** — `.rules-cache/` absent on host (SG-145 F-SG145-1); contract checkout is
  `/home/andrei/storagegenie-contract`.
- **F-SG146-5 (scope note)** — only two files in the whole tree use `exec_driver_sql` (sg017 downgrade,
  sg048). sg017's `downgrade()` still uses it; presumably the downgrade should be made offline-safe too in
  a re-packet (not exercised by `upgrade head --sql`, so out of this run's failure path).

## Acceptance criteria — assessed

- **fixed:** FAIL. `upgrade head --sql` exits 1 (aborts at sg048); FTS DDL now present but only 3 of 7
  post-FTS markers.
- **equivalent:** PASS for the partial change. Suite delta == +0 files with base-reds identical
  (`2 failed, 635 passed`), heads unchanged. (Note: expected was "+1 green file"; no test was addable —
  see G2.)
- **clean:** PASS. Diff is exactly the ceiling files: `fts.py`, `sg017_fts.py`, 3 worklogs.
- **No vacuous pass:** the drive was run (twice), the suite was not skipped, the marker checks are against
  real CLI stdout.

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}` (this is a Coder report; the Architect publishes receipts).
- Note on WORK_HEAD (this commit), then `refs/notes/storagegenie-coder-reports` pushed and verified from a
  **mapped** fetch (`refs/notes/sg146-fetched`); executed output, verbatim:

```
__NOTE_SHOW__
```

- Final tip dual-annotated (note-anchor inoculation, SG-092 precedent); mapped fetch `show`, verbatim:

```
__FINAL_SHOW__
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| G0 read-only `--sql` drive | offline CLI (300s class) | 300 s | < 3 s |
| G1 code reads + edits + re-drive | ordinary | 120 s | < 3 s |
| G2 probe (mock monkeypatch) | ordinary | 120 s | < 3 s |
| G2 full suite | suite class | 600 s | 33.5 s |
| G2 ruff / mypy / heads / secret | ordinary | 120 s | < 20 s |
| G2 worklogs + commit + push | ordinary | 120 s | < 5 s |
| Receipt notes (add/push/fetch/show) | ordinary / notes-push | 120 s / 300 s | < 10 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | **~15 min wall** |

Actual-versus-budget per goal: well under every class; overall well under the 2400 s cap.
**Real metered spend $0.000000 USD, zero metered calls.**

## UNCLEAR

- **FIRST READ:** the packet treated the offline defect as a single point (`fts.py:35` via sg017) and the
  slice as size S. First contact with the tree showed the defect is a *class* with a second instance in
  sg048, and that sg048's `batch_alter_table` is a structural offline blocker — so the accepted scope
  cannot reach the accepted outcome.
- **DURING EXECUTION:** after the within-ceiling fix, the run advanced to sg048 and died there; a
  read-only monkeypatch probe then proved sg048 fails even with `exec_driver_sql` neutralized. Separately,
  the packet's literal assertion substring `CREATE VIRTUAL TABLE asset_fts` has zero matches in the real
  emitted SQL. I reported my numbers rather than bending to the packet.
- **REMAINING:** the end-to-end offline `--sql` fix needs (a) sg048 added to the write ceiling and made
  offline-capable (exec_driver_sql → `op.execute`, and a `copy_from=` for the batch alter), and (b) a G2
  assertion using the actual substring `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts`. sg017 is already
  fixed in this commit.

## RECOMMENDED-NEXT

- **R1 (re-packet SG-147):** extend the ceiling to `backend/alembic/versions/20260916_sg048_name_optional.py`.
  Make `_drop_fts`/`_reinstall_fts` offline-safe: emit DROP statements via `op.execute` in offline mode
  (analogous helper), gate the rebuild online-only, and provide `copy_from` on the `batch_alter_table`
  calls so SQLite offline mode can render them (or otherwise restructure the alter for offline). Consider
  also sg017 `downgrade()` for symmetry (F-SG146-5). Acceptance: `alembic upgrade head --sql` exits 0;
  stdout contains `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` + the 3 triggers + all 7 post-FTS markers;
  the new test fails against BASE (either side) and passes after.
- **R2 (test wording):** assert the actual emitted text (`CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts`),
  not the packet's `CREATE VIRTUAL TABLE asset_fts` (0 matches today).
- **Chain position:** SG-146 is blocked, so the finish chain (`docs/superpowers/plans/2026-09-29-roadmap-finish.md`)
  cannot continue to the hue verdict / close-out deploy on this slice's account. The partial sg017 fix is
  benign and online-equivalent; no live deploy is owed for it (no served-code path changed — only a
  migration's offline branch and a service helper), and the packet bound Deploy: none.

**note=yes**
