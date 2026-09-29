# SG-144 — Pin the README runbook commands with a guard test (F-SG126-3)

**Dispatch-ID:** SG-144
**Role:** Coder (never Architect — no dispatch verb run, no unit started or polled for any ID).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` resolved):** `a6644810d7d21e00247e3cfc7be33d6ab318f428`
**WORK_HEAD:** `03b82459b57541586cc3e511b633390d38c73438` (the guard commit; the receipt note lives on it).
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c`.
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort `high`
— source `/proc/792653/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high # SG-144 …`. (No system-prompt identity used.)
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (no provider/USD-metered call is
reachable from a file-read guard; the suite runs offline).
**Live clock at open:** `2026-09-29T10:02:49Z`.
**Autonomy:** `L3` finish chain (slice 3 of 5); no retry used.

## Verdict: **GREEN** — G0 CLEAN, guard added and seen-to-fail, README byte-untouched

The four runbook command strings were CLEAN against the SG-086 form at G0 (the doubled-`/_data` drift was
already repaired by SG-126/F-SG126-1). No product hunk ships. One new guard test
(`backend/tests/test_runbook_commands.py`) reads the **real** `README.md` bytes, derives the drill's required
flag set from the **real** `backend/scripts/backup_restore_drill.py`, and pins compose-up / alembic-upgrade /
seed / drill invocation. It was shown failing on a deliberately drifted string, then green on the real file.
Suite: 2 failed / 635 passed — both reds are environment reds (`test_signals.py`, no tesseract/pyzbar),
re-proved identically on bare BASE. Ruff green; secret gate clean.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on disk 2026-09-29 | Verdict |
|---|---|---|
| `README.md:26` compose-up | line 26 = `docker compose up --build -d` (also line 63) | **confirmed** |
| `:33-34` + `:64-65` alembic + seed | lines 33/64 = `docker compose exec backend python -m alembic upgrade head`; 34/65 = `docker compose exec backend python -m app.seed` (63 is the second compose-up) | **confirmed** |
| `:121-136` drill runbook block | the fenced sh block is lines **127-131**; prose 117-126, proof prose 133-137 | **confirmed** (block at 127-131) |
| `:510-515` drill + test references | lines 510-516 name `backend/scripts/backup_restore_drill.py` + `backend/tests/test_backup_drill.py` and point back to the drill runbook | **confirmed** |
| SG-086 form lives in `backend/scripts/backup_restore_drill.py` | `main()` declares `--prod-db` and `--prod-storage`, both `required=True` (lines 243-244); `--work-dir` optional | **confirmed** |
| drill tests live in `backend/tests/test_backup_drill.py`; guard home beside it | both files exist under `backend/tests/`; new guard placed there | **confirmed** |
| contract recorded `0.40.0` == published `f26dbd3` | `VERSION`=0.40.0, contract HEAD `f26dbd3…` | **confirmed** |
| runbook strings may be DRIFTED | anti-drift probe for `{{.Mountpoint}}')/_data` = absent; all four strings byte-equal to the form | **CLEAN** |

**Finding F-SG144-1 (out of scope, reported):** the "Run the suites" block (`README.md:78-82`) tells the
reader to `cd backend` and run `../venv/bin/python -m pytest`. On this host `/home/andrei/StorageGenie/venv`
(root) is missing `pillow_heif` (50 collection errors); the working interpreter is `backend/venv/bin/python`
— which the drill block at `:128` already uses. This is a real runbook weakness but is **not** one of the
four pinned commands and a repair would exceed this slice's ceiling (runbook rewrite forbidden), so it is
reported, not changed.

## G0 — quote the strings + CLEAN/DRIFTED (committed before any edit)

Committed as `b3fb56596588825af4ab2a2019e5d99fcb4a6925` **before** the guard existed. Verbatim capture (from
`docs/worklogs/SG-144_verify.log`, `README.md` sha256 `1286ecd3446a074e34e7fd835b99a245439b205c7fb2697caf7faa787f6c6859`):

```
README.md:26   'docker compose up --build -d'
README.md:33   'docker compose exec backend python -m alembic upgrade head'
README.md:34   'docker compose exec backend python -m app.seed'
README.md:63   'docker compose up --build -d'
README.md:64   'docker compose exec backend python -m alembic upgrade head'
README.md:65   'docker compose exec backend python -m app.seed'
README.md:127  '```sh'
README.md:128  'backend/venv/bin/python backend/scripts/backup_restore_drill.py \'
README.md:129  '  --prod-db data/db/storagegenie.db \'
README.md:130  '  --prod-storage "$(docker volume inspect storagegenie_storage_data --format '"'"'{{.Mountpoint}}'"'"')"'
```

SG-086 form (from `backend/scripts/backup_restore_drill.py:243-244`):
`add_argument("--prod-db", required=True)` and `add_argument("--prod-storage", required=True)`.
**VERDICT: CLEAN** — so no product edit ships; the diff is test + worklogs only. (CLEAN is a success.)

## G1 — the guard, seen-to-fail then green (`PG-EV-09`, `PG-EV-01`)

**Set the test pins (enumerated on the target):** four strings — compose-up, alembic-upgrade, seed, drill
invocation. The drill's **required flag set is derived** from the script (never hard-coded a second copy);
the README's drill block must use exactly that set, and the `--prod-storage` value must be the raw volume
mountpoint with no `/_data` suffix.

**Seen-to-fail (`PG-EV-09`):** a transient probe (`backend/tests/_sg144_driftprobe.py`, removed, not
committed) re-appended `/_data` and called the **real** pin function; it failed:
`AssertionError: drill-invocation: --prod-storage is not the SG-086 form: '…/_data"' != '…"'` (full capture
in the verify log). **Green on the real file:** `3 passed`.

The guard also holds a permanent seen-to-fail property
(`test_guard_flags_the_doubled_data_suffix_drift`) and a non-vacuity guard (`README` non-empty, required
flags non-empty) and a `CO-100` assertion that the pinned constants carry no credential-shaped literal.

**Suite / lint / secret:** `2 failed, 635 passed` — the two reds
(`test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
`test_signals.py::test_ocr_has_text_boxes_and_mean_confidence`) are OCR/barcode environment reds, re-proved
on bare BASE `a664481` in a temp worktree with the slice absent (`2 failed`). `ruff check app tests` →
`All checks passed!`. Secret grep of the new file → no hits.

## G2 — worklog and report (`CO-57`)

Written: `docs/worklogs/SG-144.log`, `SG-144_report.md`, `SG-144_verify.log` (G0 + fail-then-pass + suite +
lint + diff-ceiling). Budget below; real spend $0.000000 / zero metered calls.

**Diff ceiling (WRITES exactly: ONE guard test + README drift-only + 3 worklogs):**

```
$ git diff --name-only a664481..03b8245
backend/tests/test_runbook_commands.py
docs/worklogs/SG-144_verify.log
$ git diff a664481..03b8245 -- README.md backend/scripts/backup_restore_drill.py   # empty
```

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}`.
- Note added on WORK_HEAD `03b8245`, then `refs/notes/storagegenie-coder-reports` pushed and verified from a
  **mapped** fetch (`refs/notes/sg144-fetched`); executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-144 | Report: docs/worklogs/SG-144_report.md | Work-HEAD: 03b82459b57541586cc3e511b633390d38c73438" 03b82459b57541586cc3e511b633390d38c73438   # add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports            # 36ac758..6b764f5 push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg144-fetched   # fetch_exit=0
$ git notes --ref=refs/notes/sg144-fetched show 03b82459b57541586cc3e511b633390d38c73438
Dispatch-ID: SG-144 | Report: docs/worklogs/SG-144_report.md | Work-HEAD: 03b82459b57541586cc3e511b633390d38c73438
show_exit=0
```

- Final tip dual-annotated (note-anchor inoculation, SG-092 precedent); its fetched `show` is recorded in
  `SG-144.log` and appended below after the final-tip note was pushed:
  `<FINAL_TIP_SHOW_PLACEHOLDER>`
- `note=yes`

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| G0 reads/quote | ordinary | 120 s | < 1 s (file reads only) |
| G1 guard + targeted + probe | ordinary | 120 s | ~1 s (targeted 0.02 s, probe 0.11 s) |
| G1 full suite | suite | 600 s | 33.58 s |
| G1 ruff + secret | ordinary | 120 s | < 1 s |
| G1 base-reprove | ordinary | 120 s | 0.73 s (+ worktree add/remove) |
| G2 worklogs + commit | ordinary | 120 s | < 1 s |
| G2 notes add + push + fetch + show | ordinary / notes-push | 120 s / 300 s | < 3 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | **~4 min wall** |

Actual-versus-budget per goal: G0 well under 120 s; G1 well under 600 s; G2 well under its bounds; overall
well under the 2400 s cap. Real metered spend $0.000000 USD, zero metered calls.

## UNCLEAR

- **FIRST READ:** The packet's line citations (`:33-34`, `:64-65`, `121-136`) matched the tree; the drill
  fenced block is precisely 127-131 and the plan's own citation `63-65` differed by one from the packet's
  `64-65` — both are subsets of the two runbook blocks, so no string was missed.
- **DURING EXECUTION:** The working interpreter is `backend/venv/bin/python`, not the README's
  `../venv/bin/python` (root venv lacks `pillow_heif`) — an out-of-scope runbook weakness (`F-SG144-1`)
  that the four pinned strings do not cover.
- **REMAINING:** The guard pins the four command strings + the drill's derived flag set + the `/_data`
  anti-drift property; it does not pin the prose around them or the `:78-82` test-run block. F-SG126-3's
  named instances are guarded; broader README prose remains unpinned by design.
