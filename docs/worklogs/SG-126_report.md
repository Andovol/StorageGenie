SG-126 — Backup re-drill: prove the manual runbook still holds (read-only, restore-to-temp)

**Work dir:** `/home/andrei/StorageGenie` · **remote:** `git@github.com:Andovol/StorageGenie.git`
**BASE** (packet ref `origin/automation`, resolved commit): `e9b2ffd49962bbd1d09eb79185fc15ff90170875`
**WORK_HEAD:** _(filled in the receipt-fill commit)_
**Contract:** recorded `0.37.0` == published `0.37.0` · source `/home/andrei/storagegenie-contract/VERSION`;
installed `RULES.md` sha256 `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`.
**MODEL / effort (CO-78, from process args + provider metadata, never the system-prompt identity):**
model `deepseek-v4.1-flash` (provider metadata banner `> build · deepseek-v4.1-flash` in
`output/dispatch/SG-126.log`; argv carries no `--model` = contract-legal omitted-model subset) ·
effort `high` (argv: `opencode run --auto --dir /home/andrei/StorageGenie --variant high`).
**Spend:** real `$0.000000` vs `$0` bound — zero provider calls, no metered call exists on any path.
**DB:** `/data/db/storagegenie.db` (= host `/home/andrei/StorageGenie/data/db/storagegenie.db`), grant D17
**READ-ONLY**; restore lands on TEMP only; production never written. Restart: none. Deploy: none.

## G0 — capability enumeration (non-mutating) — GREEN
- Live DB readable: `-rw------- andrei`; `PRAGMA journal_mode` → `wal`; `PRAGMA integrity_check` → `ok`.
- Storage volume resolvable read-only: `docker volume inspect storagegenie_storage_data` →
  `/home/andrei/.local/share/docker/volumes/storagegenie_storage_data/_data` (local), readable, 29 files / 6035868 B.
- `sqlite3` 3.45.1; `docker` 29.6.2; temp writable (`/tmp`, 122G avail).
- Runbook freshness: script `--help` exit 0; test file present; `backend/venv/` present; README command paths —
  **DRIFT** (F-SG126-1, below).
- Premise difference (not an obstacle): the packet's `/data/db/... NOT directly readable under
  `ProtectSystem=strict`` does not reproduce — `docker-compose.yml` has no such directive and no systemd unit
  carries it; `/data/db` is the RW bind mount of `./data/db` (`docker inspect` mounts quoted in the verify log).
  No container exec was performed (constraint); host readability is the operative leg.

## G1 — consistent read-only copy — GREEN
- **BEFORE** (read-only, live): 28 tables; quoted per-table counts + `integrity_check=ok` (verify log). Named rows
  quoted (`Toothpaste`, `CEAFĂ DE PORC`, `UHT Lapte 3,5% grăsime`).
- DB copied via **SQLite-native backup API over `mode=ro`** (no raw `cp` of WAL files): backup
  `sha256=8a20713603f645be1d7cccfcbaa2fee1f8356f72b0e9f38166afa9ad8c7bac46`, 606208 B, `integrity_check=ok`.
- Storage copied recursively: source == backup, **29 files / 6035868 B**, sampled hashes quoted.
- **AFTER**: counts **identical** to BEFORE, `integrity_check=ok`; live file size + mtime unmoved
  (`606208`, `2026-09-24 11:42:31Z`). No `UPDATE/DELETE/INSERT`, no forced checkpoint, no restart.

## G2 — restore-to-temp proof — GREEN
- Restored into fresh temp `restore-dir` (the script's own `/tmp/sg086-drill-6w7lc7cl/restore`); DB
  **backup == restored** at `8a20713603f645be1d7cccfcbaa2fee1f8356f72b0e9f38166afa9ad8c7bac46`;
  restored `integrity_check=ok`; counts + named rows match BEFORE; storage hashes identical. Temp dir **removed
  post-proof**; hashes/counts retained in the committed verify log (`PG-EV-06`).
- **Seen-to-fail (`PG-EV-01`)** — corrupted temp copy quoted: equality gate `FAILED as expected: byte inequality:
  ...storagegenie.db=8a207136... vs ...corrupted.db=b36300ada1cfaa3c3fdefed8bde55968cf44c682c20ab04513bd07575b8eef70`;
  artifact discarded. (Not vacuous: a real bad input drove the gate.)

## Runbook verdict — DRIFT-REPAIRED (F-SG126-1)
At BASE, the README runbook command (README.md:130) ended:

```
  --prod-storage "$(docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}')/_data"
```

`{{.Mountpoint}}` **already** ends in `/_data`, so the command resolved to
`.../storagegenie_storage_data/_data/_data` → `STOP: production storage not found` (raw in verify log). SG-086's
own verify log ran the undoubled path and green; only the README hunk (commit `6eb805b`) diverged. Surgical
1-line repair (quoted hunk):

```
-  --prod-storage "$(docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}')/_data"
+  --prod-storage "$(docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}')"
```

No script/test change; both remain unchanged SG-086 artifacts. `git diff -- README.md` = 1 insertion / 1 deletion.

## G3 — worklog + report — this file
- `docs/worklogs/SG-126.log`, `SG-126_report.md`, `SG-126_verify.log` (raw outputs + hashes/counts + `CO-42`).
- Drill test re-run green: `3 passed in 0.03s` (temp fixtures only).
- `PG-SC-11` grep verdicts: `test_backup_drill.py:4,7` = docstrings (no assertion); `:22` `DRILL_PATH` anchored to
  `__file__` (robust); `:26` consumes it. **No test asserts over the README path** — no vacuous pass; this absence
  is why F-SG126-1 stayed invisible to CI, reported rather than silently fixed beyond the ceiling.
- `CO-42` verbatim (`/home/andrei/storagegenie-contract/CODER_PRODUCTION.md:26`):
  **"Restoring production from backup is an incident, never silent cleanup."**

## Budget — actual vs bound (units; live clock)
- G0 enumeration: ~45 s / 120 s ordinary — UNDER.
- G1+G2 drill (first abort on F-SG126-1 + green re-run): ~30 s / 600 s copy — UNDER.
- G3 test re-run: 0.03 s / 600 s — UNDER.
- Overall: ~3 min / 1800 s (lane `RUN_BUDGET_S=2100`; expected ~900 s) — UNDER. No command killed;
  no interactive command.

## Findings
- **F-SG126-1 — README runbook drift (doubled `/_data`), REPAIRED** surgically per the ceiling; quoted above.
- **F-SG126-2 — packet premise `ProtectSystem=strict` does not reproduce** on this host (no such directive);
  container `/data/db` is the same RW bind mount. Not an obstacle; host read leg used.
- **F-SG126-3 (carried, outside scope):** no automated guard ties the README command to the live volume path, so
  the SG-086 drift survived 40+ slices. A runbook command test (or removing the shell substitution) would prevent
  recurrence; noted for the Architect, not changed here.

## Receipt
- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push; no `{{RECEIPT_CMD}}`.
- Note added on WORK_HEAD then `refs/notes/storagegenie-coder-reports` pushed and verified from a **mapped** fetch;
  executed `show` output pasted below in the receipt-fill commit. Final tip dual-annotated (SG-092 precedent).
- `note=yes` (final line below, in the receipt-fill commit).

## UNCLEAR
- **FIRST READ:** whether the README path actually resolved — it did not; the doubled `/_data` was caught only by
  executing the runbook command, not by reading it.
- **DURING EXECUTION:** whether the `ProtectSystem=strict` premise existed (no) and whether any test guarded the
  runbook command (no).
- **REMAINING:** no automated runbook-command guard exists; F-SG126-3 is open.
