SG-131 — Live ledger purge: backup, census, run the SG-125 vehicle, prove counts

**Dispatch-ID:** SG-131 · **Verdict:** NO-OP PURGE (vehicle ran LIVE, `deleted= 0 []`) — NOT blocked: the month-box is live in the served image and the G0 zero-precondition held (old-row set EMPTY). The SG-125 instrument served the request; it had nothing old to remove.

**Contract:** 0.37.0. Source path `/home/andrei/storagegenie-contract/VERSION` (`0.37.0`); contract HEAD `1acd7730e5fa6de5b7403aacce71207e9946461d`; `RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` (matches installed). Recorded == published.
**BASE** (`origin/automation` requested; resolved at start): `777c293edf80a5a575cd7a2aa95a1ff7f266d6df` · **WORK_HEAD:** `ac9288074408f5f3c6543418c9e81971b30b4c25` (log + verify log). Report added at the final tip.
**Model/effort (CO-78, from process args/provider metadata):** providerID `opencode-go`, modelID `deepseek-v4.1-flash` (metadata: `output/dispatch/SG-131.log` `> build · deepseek-v4.1-flash`; `opencode.log` providerID=opencode-go modelID=deepseek-v4.1-flash); **effort `high`** from process argv, pid `1686971`, `/proc/1686971/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --variant high`.
**Spend:** real **$0.000000** — zero metered calls; no path in this slice constructs one.
**Money posture:** $0.000000 actual vs $0 bound (units: USD).
**Authoring date (metadata only):** 2026-09-25.

(Note: the packet carries no `coder:`/`model:`/`effort:` line; settings travelled on the trigger `SG-131 coder=opencode effort=high` per D2/D302. Confirmed — the packet `/home/andrei/StorageGenie/docs/packets/SG-131-live-purge.md` opens with the trigger line, not packet settings.)

## G0 — live-readiness, capability, backup, before-census

**Is the SG-125 instrument the code actually serving?** Yes — verified in-image, not inherited (`PG-IC-09`):

    $ docker compose exec -T backend python -c "from app.services.providers import reader; import inspect; ..."
    LEDGER_RETENTION_MONTHS= 12
    purge_old_provider_calls_callable= True
    _recorded_spend_month_boxed= True
    purge_predicate= ['.filter(ProviderCall.created_at < cutoff)']

All three SG-125 symbols are importable from the running container; `_recorded_spend` contains `_current_month_start_utc` (month-box live); the vehicle predicate is exactly `ProviderCall.created_at < cutoff`. Had any symbol been absent this would have been BLOCKED (no rebuild is in scope).

**Capability census** (`PG-PR-01`, read-only forms): the container exec identity is `uid=0(root)` and CAN write `/data/db`; host `andrei` owns the bind-mounted DB (`-rw------- andrei:andrei`) and can read it. Only read-only SELECTs were issued for the census; the single potential write was the G1-gated vehicle DELETE.

**Backup-first (SG-086 runbook, read-only copy + byte-equality):** executed `backend/scripts/backup_restore_drill.py` with the volume mountpoint, `--work-dir /tmp/opencode/sg131-backup` (kept). Results:
- Before/after per-table counts identical (`provider_call 17`, `guardrail_event 2`, `audit_event 68`, `job 8`, `evidence 13`), `integrity_check=ok` both; production-untouched proven.
- DB consistent copy `sha256=8a20713603f645be1d7cccfcbaa2fee1f8356f72b0e9f38166afa9ad8c7bac46 bytes=606208`; **backup == restored byte-equal**; restored `integrity_check=ok`; corrupted-copy gate seen-to-fail (quoted).
- Storage copied read-only (29 files / 5296705 bytes, byte-identical) — precaution; the vehicle cannot touch storage.
- **Reversal path named:** `/tmp/opencode/sg131-backup/backup/storagegenie.db` (restore copy proven byte-equal).

**Before-census (live clock):**

    clock_local       = 2026-09-25T19:58:03.032685+00:00
    retention_months  = 12
    cutoff_naive_utc  = 2025-09-25 19:58:03.032702
    month_start_utc   = 2026-09-01 00:00:00
    provider_call_total = 17
      2026-09	17	0.010368          # per-month histogram (only month present)
    old_rows_count    = 0
    current_month_count = 17 ; current_month_sum = 0.010368
    guardrail_event 2 | audit_event 68 | job 8 | evidence 13 | asset 6 | job_step 56 | observation 16 | candidate 7 | enrich_snapshot 2

The old-row set is **EMPTY** — the G0 zero-precondition HOLDS. The whole 17-row ledger sits in 2026-09, weeks old, nowhere near the 2025-09-25 cutoff. Any nonzero pre-count in either direction would have been a STOP-and-report with nothing written (`PG-IC-08`); none occurred.

## G1 — the live run and after-census

**The vehicle, word-for-word** (source `docs/worklogs/SG-125_verify.log:298`; identical command, no improvisation):

    $ docker compose exec -T backend python -c "from app.db import SessionLocal; from app.services.providers.reader import purge_old_provider_calls; s=SessionLocal(); ids=purge_old_provider_calls(s); print('deleted=', len(ids), ids)"
    deleted= 0 []
    vehicle_exit=0

Returned ids: the empty list. Nothing deleted.

**After-census (same code path, live clock advanced):**

    cutoff_naive_utc  = 2025-09-25 19:58:13.287155
    2026-09	17	0.010368
    provider_call_total = 17 ; old_rows_count = 0
    current_month_count = 17 ; current_month_sum = 0.010368
    guardrail_event 2 | audit_event 68 | job 8 | evidence 13 | asset 6 | job_step 56 | observation 16 | candidate 7 | enrich_snapshot 2

**BEFORE == AFTER exactly.** `deleted == 0`; `provider_call` 17 == 17; per-month histogram `2026-09 17 / 0.010368` **unmoved**; current-month total **0.010368 unmoved**; non-spend tables `guardrail_event`/`audit_event`/`job`/`evidence` untouched (`2/68/8/13`). `PG-IC-08` did not trip in either direction. The cutoff moved with the live clock (19:58:03 → 19:58:13) per `PG-IC-07`.

**What proves only those rows could go** (`PG-PR-06` containment): one predicated `DELETE` whose predicate is exactly `.filter(ProviderCall.created_at < cutoff)`, with the cutoff quoted from the live code (`2025-09-25 19:58:13`) and the enumerated old set quoted empty over a non-empty table. `PG-EV-06`: rows deleted — NONE; identifiers — none; reversal path named above. No vacuous pass: the empty deleted set is meaningful because the table is non-empty (17 rows) and the pre/post SELECTs are independent of the return value (`PG-EV-02`, `PG-EV-08`).

## G2 — served sanity and empty product diff

    $ curl -s -w '\nHTTP_CODE=%{http_code}\n' http://127.0.0.1:8003/v1/health
    {"status":"ok","db":"ok","storage":"ok"}
    HTTP_CODE=200

Gate probe: exact shape, DB and storage both `ok` post-run, GET-only.

    $ git status --porcelain      # product files clean; only docs/worklogs/*.log changed
    $ git diff --stat             # (empty)
    $ git diff -- . ':(exclude)docs/worklogs'   # (empty)

**Zero product hunks** — this slice shipped no product code, schema, config or storage artifact.

## Findings / disagreements

- **F-SG131-1 (defect in the SG-125 recorded backup command):** `SG-125_verify.log:292-294` records `--prod-storage "$(docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}')/_data"`. `{{.Mountpoint}}` already returns the `_data` directory (measured: `/home/andrei/.local/share/docker/volumes/storagegenie_storage_data/_data`), so the recorded form resolves to `.../_data/_data` and would STOP with "production storage not found". I used the SG-086 runbook form (`SG-086_verify.log:70`, mountpoint alone). The DB half of the record is correct; the shipped drill script is correct.
- **F-SG131-2 (informational drift):** live `provider_call` is 17 (SG-086 measured 14 on 2026-09-21). All rows are 2026-09; nothing approaches the cutoff. No premise broken.
- **F-SG131-3 (write-scope disclosure):** the packet's write ceiling is the vehicle run + three `docs/worklogs` files. Backup-first per the SG-086 runbook necessarily writes a read-only copy under `/tmp/opencode/sg131-backup` (outside the worktree, not a repo/product write); it is the named reversal path required by G1, so it is disclosed rather than hidden.

## Acceptance criteria

- Readiness import check quoted (in-image, all three symbols) — answered: yes, the instrument being served is SG-125.
- Backup byte-equality quoted (`8a2071…`, backup==restored, integrity ok, corrupted gate seen-to-fail); before/after census quoted with live cutoff; deleted set quoted empty; month total unmoved and quoted; health exact (`{"status":"ok","db":"ok","storage":"ok"}` 200); empty product diff quoted.
- Write-fate answered: the vehicle deleted nothing; only `created_at < cutoff` could have been touched, and the enumerated set was empty. Live-safety answered: the G0 zero-precondition plus the exact predicate.
- `$0.000000`; no vacuous pass.

## Budget — actual vs budget (units: seconds of wall time)

| Leg | Actual | Budget |
|---|---|---|
| G0 readiness import | ~1 s | 120 s |
| G0 capability census | ~1 s | 120 s |
| G0 backup drill (DB+storage+restore) | ~8 s | 120 s |
| G0 before-census | ~3 s | 120 s |
| G1 vehicle run | ~1 s | 120 s |
| G1 after-census | ~2 s | 120 s |
| G2 health + diff | ~1 s | 120 s |
| Overall | ~<1 min | 600 s |

No command was killed or hung; all ran under the stated bounds. Real metered spend: **$0.000000** (0 calls).

## Receipt — executed and pasted verbatim from the FETCHED mapped ref

Executed, in order. The `show` output below is the **executed** output against the **fetched** notes ref (mapped local name `refs/notes/sg131-verify`, not a bare `FETCH_HEAD`):

    $ git notes --ref=refs/notes/storagegenie-coder-reports show ac9288074408f5f3c6543418c9e81971b30b4c25
    error: no note found for object ac9288074408f5f3c6543418c9e81971b30b4c25.
    pre_show_exit=1

    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-131 | Report: docs/worklogs/SG-131_report.md | Work-HEAD: ac9288074408f5f3c6543418c9e81971b30b4c25" ac9288074408f5f3c6543418c9e81971b30b4c25
    add_exit=0

    $ git push origin refs/notes/storagegenie-coder-reports
    To github.com:Andovol/StorageGenie.git
       091facd..b8bbfa2  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    push_exit=0

    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg131-verify
    From github.com:Andovol/StorageGenie
     * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg131-verify
    fetch_exit=0

    $ git notes --ref=refs/notes/sg131-verify show ac9288074408f5f3c6543418c9e81971b30b4c25
    Dispatch-ID: SG-131 | Report: docs/worklogs/SG-131_report.md | Work-HEAD: ac9288074408f5f3c6543418c9e81971b30b4c25
    show_exit=0

The work was pushed to `automation`; no push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. The final tip is dual-annotated with the same message (note-anchor inoculation, SG-092 precedent). Final line: `note=yes`.

## UNCLEAR

- **FIRST READ:** whether "PURGED (vehicle run live, before/after census quoted, month-math unmoved)" in the verdict menu intended a delete-count of zero to still read as PURGED (no-op purge) rather than a distinct NO-OP label; I reported NO-OP PURGE and stated the counts, since `deleted=0` is not a BLOCKED condition per the packet's own BLOCKED definition (month-box live, zero pre-count).
- **DURING EXECUTION:** the SG-125 recorded backup command's extra `/_data` would have STOPPED the backup leg; I resolved it to the SG-086 runbook form rather than treating it as a slice blocker (F-SG131-1). No confirmation was possible mid-run.
- **REMAINING:** the mere existence of the retention vehicle (`LEDGER_RETENTION_MONTHS` UNCALIBRATED per `G-A9`) is a standing scheduler-less capability; whether the 12-month window should be calibrated or the vehicle retired is an Architect decision outside this slice.
