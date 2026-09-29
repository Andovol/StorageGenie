FIXED: `alembic upgrade head --sql` now exits 0 across the full chain — the four post-FTS `_has_table` guards skip in `as_sql` mode; online schema byte-identical; suite delta == +1 green file.

# SG-148 — offline `--sql`: four `_has_table` guards (unserved) — report

**Dispatch-ID:** SG-148
**Role:** Coder (never Architect — no dispatch verb run for any ID, no unit started or polled).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved commit):** `94ba35ed3f7353746ee3c80a1ff328717b1e7779`
(the ref and the resolved commit are stated separately — two fields, never one).
**WORK_HEAD:** `b4d31fa323d86e80f627cc046d8e8d2ae195bf86`
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` =
`f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c` (subject `Contract payload 0.40.0`); payload `RULES.sha256` =
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`. (`.rules-cache/` is absent on the
host — SG-145 F-SG145-1; the live checkout above is the contract path.)
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort
`high` — source `/proc/1085732/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high # SG-148 …`. No system-prompt identity used.
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (local reads/greps, offline CLI
runs that open no database, temp-DB online migration, temp-DB suite).
**Live clock (`PG-IC-07`):** first capture `2026-09-29T13:59:25Z`.
**Autonomy:** `L3` finish chain (word D-0929-1). **DATABASE none, restart none, deploy none.**

## Verdict: **FIXED** (unserved slice, no rider)

SG-147 left four identical offline-incompatible guards after the sg017/sg048 fixes. Each is the same
idiom — `_has_table(name)` calls `sa.inspect(op.get_bind()).has_table(name)`, and `upgrade()` returns
early if the table exists. Under `--sql` there is no connection to inspect (`MockConnection`), so the
guard raises `NoInspectionAvailable` and the run aborts. The idempotency guard exists for hand-created
databases; offline there is no database, so the check is meaningless and the statement is safe to render
unconditionally. All four now skip the guard when `op.get_context().as_sql`:

```python
if not op.get_context().as_sql and _has_table("saved_search"):
    return
```

Online (`as_sql` False) the expression short-circuits to exactly the original `_has_table(name)` call, so
the online idempotency behavior is unchanged. `alembic upgrade head --sql` now exits 0 and renders the
entire chain.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| Four guards at `sg068:20-21`, `sg100:20-21`, `sg113:20-21`, `sg114:21` | Confirmed — one shared idiom, `def _has_table` at exactly those lines, `upgrade()` early-return at the next line. | confirmed |
| sg017 + `fts.py` + sg048 landed; do not revert | Confirmed present in BASE (`fts.py:drop_statements`, sg017 offline downgrade, sg048 offline-safe). Diff touches none of them — byte-identical. | confirmed |
| BASE `upgrade head --sql` aborts at sg068 (`NoInspectionAvailable`) | Confirmed: EXIT=1, sha `ea0e8ebe…`, abort at `20260917_sg068_saved_search.py:21`. | confirmed |
| emitted literal is `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` | Confirmed at G0 stdout line 225 and G2 lines 225/387. | confirmed |
| alembic single head `sg114` | `alembic heads` → `20260924_sg114_relation (head)` before and after. | confirmed |
| suite 2/635 with 2 known base-reds (`test_signals` env pair) | `2 failed, 635 passed` at BASE; `2 failed, 636 passed` after. | confirmed |
| "3 of 7 post-FTS markers emit" (SG-147) | **4 of 7** in the G0 capture (sg025/sg035/sg048/sg068); SG-147's count was from before sg048 rendered. sg068's marker line emits then its body aborts. Non-vacuity intact: sg100/sg113/sg114 absent pre-fix. | **CORRECTED (count)** |
| INFERRED: skipping the guard in `as_sql` renders all four | Confirmed: EXIT=0 with all 7 markers after the four edits. | confirmed |

## G0 — fail-pre at BASE (`PG-EV-08`, `PG-SC-12`)

Real CLI from `backend/venv`, offline (opens/writes no DB, 300s class):

```
$ (cd backend) timeout 300 venv/bin/alembic upgrade head --sql
EXIT=1 · LINES=462 · SHA256=ea0e8ebe7fd5ecb42e49292c1f5cc26d84ba084a4361466e52cb4290457948f1
sqlalchemy.exc.NoInspectionAvailable: No inspection system is available for object of type
  <class 'sqlalchemy.engine.mock.MockConnection'>
  at 20260917_sg068_saved_search.py:21 → upgrade:25
```

STOP conditions checked: exit is **not** already 0 at BASE (no FIXED-ELSEWHERE), and observing it needed
no live-DB write. G0 proceeds. Both G0 and G2 captures committed in `SG-148_verify.log` (`PG-EV-09`).

## G1 — four guards offline-safe; online byte-identical (`PG-SC-01`)

All four files read in full first; the idiom was confirmed identical, not assumed (finding: it is exactly
`def _has_table(...) -> bool: return sa.inspect(op.get_bind()).has_table(name)` plus a one-line early
return — no other differences).

- `20260917_sg068_saved_search.py:25` — `if not op.get_context().as_sql and _has_table("saved_search"):`
- `20260923_sg100_enrich_snapshot.py:25` — `if not op.get_context().as_sql and _has_table("enrich_snapshot"):`
- `20260924_sg113_location.py:25` — `if not op.get_context().as_sql and _has_table("location"):`
- `20260924_sg114_relation.py:25` — `if not op.get_context().as_sql and _has_table("asset_relation"):`

`_has_table` itself is untouched in all four (the online inspection call is byte-for-byte unchanged);
only the call site now guards it. `sg017_fts.py`, `fts.py`, `sg048_name_optional.py` are **byte-identical**
(not in the diff; the shape did not demand otherwise — stated).

- **Online-equivalence rail:** online `upgrade head` on a temp SQLite exits 0 at BASE and fixed; the
  `sqlite_master` dump (tables, indexes, triggers) diffs **empty** → `ONLINE SCHEMA IDENTICAL` (verify
  log). Because the online branch of the boolean is the original expression, online behavior is identical
  by construction and verified result-identical.
- **Suite:** `2 failed, 635 passed` (BASE) → `2 failed, 636 passed` (fixed) — delta exactly the one new
  test file, base-reds (`test_signals` env pair) identical, stash-reproved both directions.
- **Heads:** `alembic heads` single `sg114` before == after; no revision added.
- **`PG-SC-11` sweep** — every end-relative assertion over the migration chain, all head/rev-pinned and
  unchanged because no revision is added: `test_sg048_name_optional.py:21,101`; `test_sg114_relations.py:29,34`;
  `test_sg113_locations.py:29`; `test_sg100_snapshot_persistence.py:33`; `test_export.py:114-115`
  (`ScriptDirectory.get_current_head()` vs `exports.ALEMBIC_HEAD`); `test_saved_searches.py:272`; plus the
  `command.upgrade(..., "head")` call sites in `test_search.py`/`test_signals.py`/`test_foundations.py`/
  `test_candidates.py`, all resolving the unchanged live head.

## G2 — end-to-end offline test + gates (`PG-EV-01`, `CO-101`)

- **Re-drive post-fix:** `alembic upgrade head --sql` → **EXIT=0**, 518 lines, sha
  `a0013d4dbf9f449e42979574f8984dc5b7c03c02e096a4bedcc66fab68f1a655`. Stdout contains
  `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` (lines 225, 387), all three
  `CREATE TRIGGER IF NOT EXISTS asset_fts_after_{insert,update,delete}`, and all 7 post-FTS markers
  (`sg025`, `sg035`, `sg048`, `sg068`, `sg100`, `sg113`, `sg114`); tail sets
  `alembic_version` to `20260924_sg114_relation`.
- **New test:** `backend/tests/test_sg148_offline_sql.py`, named for what it proves. It runs the real CLI
  (`<venv>/bin/alembic upgrade head --sql`, cwd `backend`) and asserts exit 0 **and** the FTS table DDL
  **and** the 3 triggers **and** all 7 markers parsed from `-- Running upgrade` lines. An early-prefix-only
  output fails on the first missing marker, so the criterion cannot pass vacuously.
- **Seen-to-fail / seen-to-pass:** with the four guard edits stashed (BASE shape) and the test present,
  `1 failed` (`assert 1 == 0`, `NoInspectionAvailable`); post-fix `1 passed`. Verified by stash, not by
  argument.
- **Gates run (files checked named):** ruff over `app alembic tests` → `All checks passed!`; mypy `app`
  → `41 errors in 9 files`, **none in any touched file**, delta 0 vs BASE; secret scan over the added diff
  lines and the new test → no password/key/token/private-key pattern; `alembic heads` unchanged.
- **Blast-radius (`PG-IC-08`):** full-suite delta == **+1 green file** (`2 failed, 635 passed` →
  `2 failed, 636 passed`) with base-reds identical. No other delta. No unrated write.

## Findings

- **F-SG148-1 (count correction, minor).** SG-147 reported "3 of 7 post-FTS markers emit"; the BASE
  capture here emits **4** (sg025/sg035/sg048/sg068) — sg068's marker line prints before its body aborts.
  The end-to-end criterion was still genuinely unmet (sg100/sg113/sg114 missing); the count, not the
  verdict, is corrected.
- **F-SG148-2 (carry-over).** `.rules-cache/` absent on host (SG-145 F-SG145-1); contract checkout is
  `/home/andrei/storagegenie-contract`.
- **F-SG147-1 (closed).** All four guards are now offline-safe; the end-to-end blocker is gone.
- No denied privileged operation occurred; no leg was routed around (`PG-PR-03`). No command was killed
  by its bound.

## Acceptance criteria — assessed

- **fixed:** PASS. `upgrade head --sql` exits 0 with `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts`, the
  3 `asset_fts_after_*` triggers, and all 7 post-FTS markers (`SG-148_verify.log`, G2).
- **equivalent:** PASS. Online schema byte-identical (empty diff, BASE vs fixed); suite delta == +1 green
  file with base-reds identical; `alembic heads` single `sg114` before == after; no new revision.
- **clean:** PASS. `git diff --stat` is exactly the four guard migrations (`4 files changed, 4 insertions(+),
  4 deletions(-)`) plus one new untracked test; three SG-148 worklogs. sg017/fts.py/sg048 byte-identical.
- **No vacuous pass:** the drive was run against the real CLI both sides; the suite was run in full, not
  skipped; the marker assertion covers all 7 (the pre-fix capture lacks 3 of them). Stated loudly.

## Guard invocation (as listed in the packet)

`PG-EV-01` (new test) · `PG-EV-02`/`PG-EV-05` (evidence committed in the verify log) · `PG-EV-08`/`PG-SC-12`
(G0 fail-pre) · `PG-EV-09` (both runs committed, sha-pinned) · `PG-SC-01` (online byte-identical) ·
`PG-SC-09` (per-criterion questions, above) · `PG-SC-11` (end-relative assertion sweep) · `PG-IC-01`
(cross-product: G0 offline CLI 300s class, G1 edit no bound, G2 suite 600s + gates 120s) · `PG-IC-07`
(live clock) · `PG-IC-08` (blast-radius exactly +1) · `PG-IC-09` (every given fact re-verified) ·
`PG-PR-03` (no denied probe, none routed around).

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}` (Coder report; the Architect publishes receipts).
- Note on WORK_HEAD, then `refs/notes/storagegenie-coder-reports` pushed and verified from a **mapped**
  fetch; executed output pasted verbatim below.

- Note on WORK_HEAD, then `refs/notes/storagegenie-coder-reports` pushed and verified from a **mapped**
  fetch (`refs/notes/sg148-fetched`); executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-148 | Report: docs/worklogs/SG-148_report.md | Work-HEAD: b4d31fa323d86e80f627cc046d8e8d2ae195bf86" b4d31fa323d86e80f627cc046d8e8d2ae195bf86
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   99426af..2572b8d  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg148-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg148-fetched
fetch_exit=0
$ git notes --ref=refs/notes/sg148-fetched show b4d31fa323d86e80f627cc046d8e8d2ae195bf86
Dispatch-ID: SG-148 | Report: docs/worklogs/SG-148_report.md | Work-HEAD: b4d31fa323d86e80f627cc046d8e8d2ae195bf86
show_exit=0
```

- Branch push `94ba35e..b4d31fa HEAD -> automation` (exit 0) preceded the notes push.

- Final tip `badbafa` dual-annotated (note-anchor inoculation, SG-092 precedent); mapped fetch `show`,
  verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-148 | Report: docs/worklogs/SG-148_report.md | Work-HEAD: b4d31fa323d86e80f627cc046d8e8d2ae195bf86" badbafa8d3948e64bdc952e1b47c1e1345e49e7a
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   2572b8d..f6af98b  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg148-fetched-final
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg148-fetched-final
fetch_exit=0
$ git notes --ref=refs/notes/sg148-fetched-final show badbafa8d3948e64bdc952e1b47c1e1345e49e7a
Dispatch-ID: SG-148 | Report: docs/worklogs/SG-148_report.md | Work-HEAD: b4d31fa323d86e80f627cc046d8e8d2ae195bf86
show_exit=0
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| G0 read-only `--sql` drive | offline CLI (300s class) | 300 s | < 3 s |
| G1 code reads + four edits + re-drive | ordinary | 120 s | < 15 s |
| G1 online temp-DB migration + schema diff + heads | ordinary | 120 s | < 6 s |
| G2 new test fail/pass (stash round-trip) | ordinary | 120 s | < 3 s |
| G2 full suite | suite class | 600 s | 32.8 s |
| G2 ruff / mypy / secret / PG-SC-11 | ordinary | 120 s | < 15 s |
| G2 worklogs + commit + push | ordinary | 120 s | < 10 s |
| Receipt notes (add/push/fetch/show) | ordinary / notes-push | 120 s / 300 s | < 15 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | **< 15 min wall** |

Actual-versus-budget per goal: well under every class; overall well under the 2400 s cap.
**Real metered spend $0.000000 USD, zero metered calls.**

## UNCLEAR

- **FIRST READ:** SG-147's REMAINING was precise — four `sa.inspect(MockConnection).has_table` guards, one
  idiom, fix = skip under `as_sql`. First contact confirmed all four at the stated lines; the only
  difference from the packet was the marker count (4, not 3, emit at BASE).
- **DURING EXECUTION:** the four edits are one-line condition changes; the boolean short-circuit keeps the
  online branch literally identical to BASE, so online equivalence held without any behavior negotiation.
  The re-drive reached exit 0 on the first attempt post-edit.
- **REMAINING:** nothing on this slice. The offline `--sql` chain is now end-to-end green and online
  byte-identical. No follow-up write is owed (no served-code path changed — migration offline branches
  only).

## RECOMMENDED-NEXT

- **Chain position:** this unblocks the finish chain. Proceed to the merge batch per SG-149's verdicts on
  its second word, then the hue verdict, then the close-out live deploy per
  `docs/superpowers/plans/2026-09-29-roadmap-finish.md`. No deploy is owed on this slice's account (Deploy:
  none; a migration's offline guard only).

**note=yes**
