# SG-086 — backup/restore drill: read-only production copy, restore-to-temp proof, runbook

**Dispatch:** SG-086 · Phase 5 hardening slice 2 (plan `docs/superpowers/plans/2026-09-21-phase-5-hardening.md` §Slice 2) · **Coder:** opencode / effort medium (argv, not identity line) · **Autonomy:** L3 per D107 grant
**BASE ref:** `origin/automation` → resolved `60d9a70044a57233c40e1bda984f4acbf4111194` (two fields, never one)
**WORK_HEAD:** `6eb805b24909431b67ab1ad8426c291523198bae` (slice tip; the follow-up docs-only commit carries this paste)
**Spend:** **$0.000000 actual** — zero provider calls; no metered call exists on any path in this slice
**Authoring date metadata:** 2026-09-21 (not a gate)

## Contract echo + source path

`AGENTS.md` records **`0.28.2`** ("D82 adoption 2026-09-17: tag `contract-v0.28.2` checkout `b495b59`"), and the published contract source reads the same:

```
$ cat /home/andrei/storagegenie-contract/VERSION
0.28.2
$ git -C /home/andrei/storagegenie-contract rev-parse HEAD
b495b59b3426af66772a87939473ac558f8f72d2
```

**Recorded `0.28.2` == published `0.28.2`.** Source path: `/home/andrei/storagegenie-contract/VERSION` + git HEAD `b495b59` (the `.rules-cache/` directory does **not** exist in this worktree — gitignored, Launcher-only; same as SG-062/SG-078 recorded).

## What shipped (scope ceiling only)

| File | Status | Note |
|---|---|---|
| `backend/scripts/backup_restore_drill.py` | NEW | operator tooling: the G1/G2 sequence, parameterized by paths, read-only guards inline |
| `backend/tests/test_backup_drill.py` | NEW | 3 tests, temp fixtures only |
| `README.md` | +22 lines | "Backup and restore drill" runbook hunk (surgical) |
| `docs/worklogs/SG-086.{log,report.md,verify.log}` | NEW | this worklog set |

No app code, prompt, migration/model, compose/`.env`, STATE/AGENTS/packet-dir or production-write path was touched. `backend/scripts/` did not exist on `automation` (confirmed); the ignore-check is quoted below.

## G0 — capability enumeration (non-mutating; stopping here is SUCCESS)

All four legs green, raw in `SG-086_verify.log`:

1. **Live DB** `/home/andrei/StorageGenie/data/db/storagegenie.db` — `test -r` READABLE, `ls -l` 372736 B; `PRAGMA journal_mode` → **`wal`** (the -wal/-shm sidecars are present). The container path `/data/db` is the same bind mount (`docker-compose.yml:11`).
2. **Storage volume** — **corrected premise:** the real name is `storagegenie_storage_data` (Compose project prefix). `docker volume inspect storage_data` → `Error response from daemon: get storage_data: no such volume`. `docker volume inspect storagegenie_storage_data` → `Mountpoint /home/andrei/.local/share/docker/volumes/storagegenie_storage_data/_data`, READABLE, 29 files / 6035868 B (`F-SG086-1`).
3. **`sqlite3`** present: `/usr/bin/sqlite3`, version `3.45.1`.
4. **Temp space** writable: `mktemp -d` → `/tmp/tmp.xKSnIFeFOt`, removed.

A red leg is the **only** stop-ground (slowness/size are never grounds, `PG-SC-03` negative case); none was red. Load-bearing fact acted on: because the DB is WAL, the copy uses SQLite-native means (native backup API), **never** raw `cp` of the live DB files.

## G1 — consistent read-only copy (production untouched)

**BEFORE** (read-only query path): per-table counts for all 24 tables (e.g. `asset 6`, `evidence 13`, `audit_event 68`, `job_step 56`) + live `PRAGMA integrity_check` = `ok`. Raw in the verify log.

**Copy:** DB via the SQLite native backup API over a `mode=ro` connection → `sha256 150a39919620f2ad0176334d833e8ffbbfa22cf4e4437e882e46e521acad3d5c`, 503808 B, copy integrity `ok`; storage recursive read copy `5.9M / 29 files / 6035868 B`, sampled hashes quoted. A raw `cp` of the live WAL database is explicitly NOT an acceptable backup — stated, not silent.

**AFTER** (post-drill, read-only): all 24 counts **identical**, integrity `ok`, live DB mtime unchanged. Compared LOGICAL state (counts + integrity), not mtime/size; no mtime move occurred, so no WAL-checkpoint disclosure is owed. Writes to production-adjacent state: **none** — no `UPDATE/DELETE/INSERT`, no forced checkpoint, no restart.

## G2 — restore-to-temp proof (byte-equality on real artifacts)

Restored the G1 copy into a **fresh temp dir** (script-logged `backup-dir` and `restore-dir` under `/tmp/sg086-drill-*`, never the live paths). Proof:

- `sha256sum` backup vs restored **identical** (`150a3991…3d5c`);
- restored `PRAGMA integrity_check` = `ok`;
- restored per-table counts == G1 BEFORE counts;
- named rows read back (table + id): `evidence` `01a0a467-eacf-7e13-bbd0-078b1bc93860`, `01a0afaa-…`, `01a0c445-…`; `asset` `01a0a467-eb0e-…` (Toothpaste), `01a0c446-…` (CEAFĂ DE PORC), `01a0c47f-…`;
- storage: file-count 29, bytes 6035868, sampled hashes equal source == backup == restored.

**Seen-to-fail (`PG-EV-01`):** a deliberately corrupted temp copy flipped one byte; the equality gate failed exactly as required — `byte inequality: …backup…=150a3991… vs …corrupted.db=5fdffd6d…` — and the artifact was discarded. (During development a corruption at a **free** page passed `integrity_check` while the sha256 gate still failed; corruption at a live page additionally reported `row 3 missing from index sqlite_autoindex_job_1` — disclosed in the log: byte-equality is the gate, integrity_check is corroboration.) A second gate, the work-dir-inside-production guard, was also fed a wrong input and STOPped: `STOP: work-dir …/data/db is inside production DB …/storagegenie.db` (exit 1).

**Temp state (`PG-EV-06`):** temp rows/files were reported with identifiers; the script-created temp dir was **removed** post-proof; hashes/counts stay in the committed logs. No production rows were created by this slice.

## G3 — committed test + runbook (the drill outlives the slice)

- **Test** `backend/tests/test_backup_drill.py` (3 tests) loads the drill module and proves, on `tmp_path` fixtures only: consistent-backup restore byte-equality + counts + named rows, storage copy byte-equality, and a corrupted-copy seen-to-fail. **FAIL-then-PASS raw, both committed** to `SG-086_verify.log`: fail-pre = collection `FileNotFoundError` (script absent, exit 2); pass-post = `3 passed in 0.03s`.
- **Drill script** `backend/scripts/backup_restore_drill.py` = the exact G1/G2 sequence, parameterized by `--prod-db/--prod-storage/--work-dir`, with inline read-only/path guards. The production evidence above was produced by running **this committed script**, not by ad-hoc commands.
- **Ignore-check (`PG-SC-10`)** quoted: `git check-ignore -v backend/scripts/backup_restore_drill.py` → exit **1** (not ignored).
- **README runbook** — surgical hunk (`git diff README.md` quoted in the verify log), inserted after the Data-locations section: what to copy, how to resolve the volume path, where temp lands (and is removed), how equality is proved, and the incident line — **`CO-42`: "Restoring production from backup is an incident, never silent cleanup."** (verbatim).
- **`PG-SC-11` grep** (raw in verify log), test tree for end-relative assertions over README/scripts/drill paths: the only qualifying hit is the new test's own structural path constant `DRILL_PATH = BACKEND_DIR / "scripts" / "backup_restore_drill.py"`; it is a fixed, committed deliverable path, **not** an append/tail-relative assertion ("latest"/`[-1]`/`HEAD~1`). Remaining hits are incidental data strings (`orange-drill.jpg`, `Cordless drill`). No existing test asserts relative to a README/script sequence end.
- **Gates:** suite `2 failed, 365 passed` (the 2 reds are the base-proved decoder env reds — re-verified on clean BASE, not inherited); `ruff check .` → `All checks passed!`; `mypy app` → `Found 41 errors in 9 files` (delta **0** vs base 41-in-9); secret grep over the diff (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken`) → **0 hits**, plus a literal-token scan → 0.

## Acceptance criteria — the question each answers (`PG-SC-09`)

| Criterion | Question it answers | Verdict |
|---|---|---|
| G0 four legs quoted | CAN this identity copy without changing anything? | green, all four raw |
| BEFORE/AFTER counts + integrity | Is the copy consistent and production untouched? | green; counts identical, integrity ok |
| Restored sha256 + rows + corrupted gate | Does the backup actually restore, byte-equal? | green; gate seen-to-fail |
| Test/script/README/ignore-check | Is the drill repeatable from the repo? | green; fail→pass committed |
| G4 logs + receipt | Is the evidence committed, not merely reported? | green; see Receipt |

No criterion passed vacuously: the equality gate was fed a corrupted input and failed; the test file was red before the script existed; counts are non-empty (24 tables, 365 passing tests); the grep lists its hits rather than assuming none.

## Findings / disagreements

- **F-SG086-1 — storage volume name premise wrong.** The packet holds `storage_data`; the real Compose-prefixed name is `storagegenie_storage_data` (`docker volume inspect storage_data` → no such volume). Also, host `data/storage` is an **empty** directory — the live evidence is only in the named volume. Resolved by reading `docker volume inspect` (read-only) as the packet directed; no workaround used.
- **F-SG086-2 — `.rules-cache/` absent** in this worktree; contract source is `/home/andrei/storagegenie-contract/`, matching the SG-062/SG-078 precedent recorded in AGENTS.md.
- **F-SG086-3 — free-page corruption.** A single-byte corruption inside free space passes `PRAGMA integrity_check` while changing the artifact's sha256. The drill therefore keys the gate on **byte equality**, with integrity_check as corroboration; this is stated in the logs rather than hidden.
- No disagreement with the packet's authority or scope; the read-only constraint was honoured on every path.

## Guards invoked (for the rating row)

`PG-EV-01` (corruption + guard gates seen-to-fail) · `PG-EV-02` (artifacts verified at their paths) · `PG-EV-05` (properties stated) · `PG-EV-06` (temp-only, reported, removed) · `PG-EV-09` (both runs committed) · `PG-SC-03` (G0 stop is success; negative case stated) · `PG-SC-05` · `PG-SC-09` (questions above) · `PG-SC-11` (grep + verdicts) · `PG-SC-12` (proof run against the real live DB/volume, not a stand-in) · `PG-IC-01` (reads only; no container exec/image pull/run/network beyond push) · `PG-IC-03` (read-only-violation STOP precedence stated; none fired) · `PG-IC-07` (live clock) · `PG-IC-09` · `PG-PR-01` (G0 enumeration first) · `PG-PR-03` (no denied read) · `PG-PR-04` (nothing live: operator tooling only; no code becomes live; proof scoped to this host run) · `PG-PR-10` (database cited + D107 grant quoted) · `PG-IC-04` stated not firing ($0, no bound to multiply).

## Receipt

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on the work HEAD and the notes ref pushed, then verified against the **fetched** ref mapped to a local name:

```
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-086 | Report: docs/worklogs/SG-086_report.md | Work-HEAD: <hash>" <WORK_HEAD>
git push origin refs/notes/storagegenie-coder-reports
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-remote
git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>
```

Verbatim executed output against the fetched mapped ref (exit 0):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-086 | Report: docs/worklogs/SG-086_report.md | Work-HEAD: 6eb805b24909431b67ab1ad8426c291523198bae" 6eb805b24909431b67ab1ad8426c291523198bae
add exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports show 6eb805b24909431b67ab1ad8426c291523198bae
Dispatch-ID: SG-086 | Report: docs/worklogs/SG-086_report.md | Work-HEAD: 6eb805b24909431b67ab1ad8426c291523198bae
$ git push origin refs/notes/storagegenie-coder-reports
   e5b6821..04d5500  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes push exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-remote
   372e770..04d5500  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-remote
fetch exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-remote show 6eb805b24909431b67ab1ad8426c291523198bae
Dispatch-ID: SG-086 | Report: docs/worklogs/SG-086_report.md | Work-HEAD: 6eb805b24909431b67ab1ad8426c291523198bae
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`). No existing note refused; final line `note=yes`.

## UNCLEAR

- **FIRST READ:** whether the "storage volume" leg was resolvable without elevated privilege — it was, but only after the packet's name premise (`storage_data`) was corrected to `storagegenie_storage_data`.
- **DURING EXECUTION:** whether a single-byte corruption should count as a valid failure when `integrity_check` still says `ok` (free-page corruption) — resolved by keying the gate on sha256 byte-equality and disclosing the integrity limitation.
- **REMAINING:** whether the human-readable DB artifact (492K snapshot) should ever be retained off-box / on a schedule; scheduling and off-box copies are explicitly out of scope, so the runbook leaves backup cadence to the owner.
