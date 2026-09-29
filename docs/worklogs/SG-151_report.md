MERGED: #36's dedup + bulk `asset_evidence` insert landed byte-exact on `asset_service.py`; #39's unique
`_create_asset_for_candidate` bulk hunk landed byte-exact on `candidates.py`; #34's failure log repathed
onto the bulk path. Backend-suite delta exactly +1 green (the one reconciled test), base-reds identical.

# SG-151 — merge Batch B: asset-evidence bulk insert (#36 + folded #39 + repathed #34, unserved) — report

**Dispatch-ID:** SG-151
**Role:** Coder (never Architect — no dispatch verb run for any ID, no unit started or polled).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved commit):** `aec6af19b7b4aa8aa609e0c089f20b78c878be72`
(the ref and the resolved commit are stated separately — two fields, never one).
**WORK_HEAD:** `88688f50761c76e07a011cc2576adf5eb112924f`
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` =
`f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c` (subject `Contract payload 0.40.0`); payload `RULES.sha256` =
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`. (`.rules-cache/` is absent on the
host — SG-145 F-SG145-1; the live checkout above is the contract path.)
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort
`high` — source `/proc/1137479/cmdline` (parent `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high # SG-151 …`). No system-prompt identity used.
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (local fetch/apply, `TestClient`/
service probes, temp-SQLite suite, lint/type). No USD-metered call exists on any path.
**Live clock (`PG-IC-07`):** first capture `2026-09-29T14:34Z`; as-of-report-writing `2026-09-29T14:37Z`.
**Autonomy:** `L2` (merge-batch arc, D-0929-3 2nd word). **DATABASE none, restart none, deploy none**
(served-code change ships via the standing close-out rider — `PG-PR-04`; stated).

## Verdict: **MERGED** (unserved slice, no rider, no rebuild/recreate/deploy)

SG-149 (98) ordered `#36 MERGE`, `#39 REWRITE` (drop the duplicate `create_asset` region, fold only its
`candidates.py` hunk), `#34 REWRITE` (log-on-failure onto the bulk path). All three heads still applied
3-way onto this BASE (verified before any edit). `#36`'s `asset_service.py` hunks and `#39`'s
`candidates.py` hunk landed byte-exact by `git apply --3way` — landed blobs equal the head blobs. The
final `asset_service.py` differs from `refs/pull/36/head` **only** by the #34 logging repath (the `import
logging` + module logger + `try/except` around the bulk insert, with the per-item fallback carrying
#34's exact `"Failed to attach evidence_id=%s to asset_id=%s: %s"` warning). The final `candidates.py` is
byte-identical to `refs/pull/39/head`.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| Base `create_asset`/`attach_evidence` still per-item loop with swallowed failures | Confirmed at BASE: `create_asset` `for eid in evidence_ids: db.execute(...)` (`asset_service.py:75-76`); `attach_evidence` loop with `except Exception: pass` (`:132-137`). | confirmed |
| `attach_evidence` has ZERO test references (SG-149 grep) | Confirmed: `grep -rn "attach_evidence" backend --include=*.py` → only the definition + the API call site (`app/api/v1/assets.py:528`). No test names it directly. | confirmed |
| Suite 2/637 with 2 known base-reds (`test_signals` env pair) | Confirmed at final: `2 failed, 638 passed`; the two reds are the same `test_signals` cases SG-150 recorded; the +1 vs BASE is exactly the one reconciled test. | confirmed (counts) |
| SQLAlchemy 2.0.52 (`Session.scalars`/`select` available) | `venv/bin/python -c "import sqlalchemy; print(sqlalchemy.__version__)"` → `2.0.52`. | confirmed |
| alembic single head `sg114` (untouched) | `alembic heads` → `20260924_sg114_relation (head)`; no migration touched. | confirmed |
| All three heads still apply 3-way onto this BASE | `git apply --3way --check` on each head's diff (PR36 asset, PR39 asset+candidates, PR34 asset+test) → all applied cleanly, exit 0. | confirmed |
| INFERRED: #36 + (#39 candidates hunk) + (repathed #34 log) yields the N+1 fix with failure visibility | Confirmed: both loops gone; failure logs both ids; suite delta exactly +1. | confirmed |
| Base behavior "duplicate evidence attach leaves duplicates-or-swallow" | Measured: the **swallow** branch. A duplicate raises `IntegrityError` inside the loop, is caught by `except Exception: pass`; the call returns OK with 1 row and **no warning**. A ghost (FK-violating) id is likewise swallowed with no log. | confirmed (mechanism: swallow, not duplicate rows) |

## G0 — land #36 by its real hunks, prove the bulk path (`PG-EV-08`, `PG-SC-12`, `PG-EV-09`)

- **Fail-pre commit `c93cbf1`** — the reconciled test (`test_attach_evidence_bulk_dedups_and_logs_failed_links`)
  was added to the existing `backend/tests/test_assets_crud.py` (no new file) and run at BASE:
  `pytest tests/test_assets_crud.py -q` → **1 failed, 3 passed**; the failure is exactly
  `assert 'Failed to attach evidence_id=ghost-evidence-id to asset_id=' in ''` — at BASE the genuine
  failed attach is swallowed, so nothing is logged. Non-vacuous: the pre-existing three tests pass.
- **Pass-post commit `14b648b`** — `git apply --3way` of `refs/pull/36/head`'s `asset_service.py` diff →
  applied cleanly; landed blob `b37739afa33d741cca83c3cd659e48c8d92084f0` == head blob
  `b37739afa33d741cca83c3cd659e48c8d92084f0`. Duplicate/repeat attach → exactly **1 row, no
  `IntegrityError` escapes**; the swallow is removed (a bad id now raises, which G1 repaths to a log).

Both runs / both blob identities are committed in `docs/worklogs/SG-151_verify.log` (`PG-EV-09`).

## G1 — fold #39's candidates hunk, repath #34's logging (`PG-SC-12`)

- **Commit `88688f5`.** `git apply --3way` of `refs/pull/39/head`'s `candidates.py` diff → applied
  cleanly; landed blob `7c2e9818653e37aa1027b91f5a3689ce88dfd88e` == head blob
  `7c2e9818653e37aa1027b91f5a3689ce88dfd88e`. **Only** the `_create_asset_for_candidate` bulk hunk landed;
  #39's duplicate `create_asset` region and its benchmark script were **dropped** (stated exclusions).
- **Repath of #34.** The bulk insert in `attach_evidence` is now wrapped: on the atomic failure,
  `db.rollback()` then a per-item fallback that logs `evidence_id` + `asset_id` with #34's exact message.
  Faithfulness proven by diff (`git diff refs/sg/pr36:…asset_service.py HEAD:…asset_service.py`) — the
  **only** delta vs `#36`'s head is `import logging`, the module `logger`, and the `try/except`/fallback
  block. No other line moves.
- **Reconciled failure-visibility test through the real service.** One test:
  - duplicate ids within one call and across calls → **1 row**, no warning;
  - a ghost (FK-violating) id → warning logged with **both** ids, row count still 1.

  It **fails at BASE** (no warning) and passes after; it calls the real `attach_evidence` against a real
  session (no mock, no `xfail`). Final run: `pytest tests/test_assets_crud.py -q` → **4 passed**.

## G2 — gates (`PG-EV-01`)

- **Targeted:** `pytest tests/test_assets_crud.py tests/test_candidates.py -q` → **7 passed**.
- **Full suite:** `2 failed, 638 passed, 32 warnings in 34.05s`; base-reds = the two `test_signals` env
  cases, **identical** to BASE. Blast-radius expectation met exactly — the only delta is the one
  reconciled test green.
- **ruff:** `ruff check .` → `All checks passed!`
- **mypy-delta:** `mypy app` → `Found 41 errors in 9 files` — **delta 0** vs the recorded BASE count
  (41/9). The three `asset_service.py` hits (`:19`, `:41`, `:112`) are the pre-existing `payload: dict`
  annotations, not introduced here.
- **Secret scan** over added diff lines (`git diff aec6af1 HEAD | grep '^+'`) → no
  password/key/token/private-key/credential pattern (`CO-100` clean).
- **Blast-radius bound (`PG-IC-08`):** no delta beyond the reconciled test; no stop triggered.
- **Ceiling:** `git diff --stat aec6af1 HEAD` = exactly `backend/app/services/asset_service.py` (+45/−12),
  `backend/app/services/candidates.py` (+5/−2), `backend/tests/test_assets_crud.py` (+38/−0); no other
  product path, no benchmark script.

## Findings

- **F-SG151-1 (base behavior nuance).** The packet offered "leaves duplicates-or-swallow"; measured, the
  answer is **swallow**: the composite PK already prevents duplicate rows, and the `except Exception:
  pass` hides both duplicate-key and FK failures. So BASE's duplicate assertion passes; the genuine
  fail-pre discriminator is the **failure-visibility** assertion (a real failed attach logs nothing at
  BASE). This is recorded rather than bent — the reconciled test keys on the warning.
- **F-SG151-2 (design call, inside the acceptance).** #36 deletes the `try/except` outright, which would
  make a bad id raise uncaught (visible but unlogged and aborting the whole call). Repathing #34's log
  required a decision: keep the bulk fast path, and on its atomic failure `rollback()` + per-item
  fallback so good links still land and every failure logs both ids. The rollback only ever discards the
  failed batch in this function's failure path (the caller's asset is already committed before
  `attach_evidence`); no committed row is undone. Stated because it is a behavior choice, not a
  byte-copy of any one head.
- **F-SG151-3 (carry-over).** `.rules-cache/` absent on host (SG-145 F-SG145-1); the contract checkout is
  `/home/andrei/storagegenie-contract`.
- **F-SG151-4 (out of scope, practice note).** As SG-150 F-SG150-2: work commit messages carry the
  `SG-151` ID (repo practice) although `CO-53` reads otherwise; flagged for reconciliation, not resolved
  here.
- No denied privileged operation occurred; no leg was routed around (`PG-PR-03`). No command was killed by
  its bound.

## Acceptance criteria — assessed (`PG-SC-09`)

- **bulked (N+1 gone on both paths):** PASS. `create_asset` (`asset_service.py:78-83`) and
  `_create_asset_for_candidate` (`candidates.py:906-910`) both do a single
  `db.execute(asset_evidence.insert(), [ … ])`; no per-item loop remains on either path. `attach_evidence`
  bulks too (pre-read + one insert), with a per-item fallback only on the failure path.
- **visible (failed attach logs both ids through the real service):** PASS. Final probe and the
  reconciled test both show `Failed to attach evidence_id=ghost-evidence-id to asset_id=…` logged via the
  real `attach_evidence`; BASE logs nothing (fail-pre committed).
- **faithful (byte-effect):** PASS. Landed `asset_service.py` == `#36` head + only the #34 repath; landed
  `candidates.py` byte-identical to `#39` head; both proven by blob hashes and by `git diff` against the
  head blobs.
- **clean (diff):** PASS. Exactly the three ceiling files; no benchmark scripts, no fourth file.
- **No vacuous pass (stated loudly):** the reconciled test invokes the real service and asserts the real
  log text with both ids (not a mock, not `xfail`); the fail-pre run is red for the asserted reason; the
  full suite ran (not skipped) with base-reds quoted. Nothing here passed by empty diff, empty set or
  skipped gate.

## Guard invocation (as listed in the packet)

`PG-EV-01` (suite/gates) · `PG-EV-02`/`PG-EV-05` (captures committed in the verify log) ·
`PG-EV-08` (BASE probe before edits) · `PG-EV-09` (both fail-pre and pass-post runs committed) ·
`PG-SC-09` (per-criterion questions above) · `PG-SC-12` (real hunks applied + blob-identity; no memory
reimplementation) · `PG-IC-01` (cross-product: G0 fetch/apply 120s, G1 fold/repath 120s, G2 suite 600s +
gates 120s — no criterion demands what the ceiling forbids) · `PG-IC-07` (live clock) · `PG-IC-08`
(blast-radius exactly +1 green; no other delta) · `PG-IC-09` (every given fact re-verified) · `PG-PR-03`
(no denied probe, none routed around) · `PG-PR-04` (no rebuild/recreate/restart/deploy; liveness rides the
close-out rider).

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}`. The receipt is the note on `refs/notes/storagegenie-coder-reports`.
- **WORK_HEAD note** (`88688f50761c76e07a011cc2576adf5eb112924f`), then the notes ref pushed and verified from a **mapped** fetch
  (`refs/notes/sg151-fetched`); executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f" 88688f50761c76e07a011cc2576adf5eb112924f
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   427f5a1..153067b  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg151-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg151-fetched
fetch_exit=0
$ git notes --ref=refs/notes/sg151-fetched show 88688f50761c76e07a011cc2576adf5eb112924f
Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f
show_exit=0
```

- **Final-tip dual-annotation** (note-anchor inoculation, SG-092 precedent); mapped-fetch `show`,
  verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f" 5a750806a73fed32e214ae69644cb20ad37af30e
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   153067b..b6daecb  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg151-fetched-final
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg151-fetched-final
fetch_exit=0
$ git notes --ref=refs/notes/sg151-fetched-final show 5a750806a73fed32e214ae69644cb20ad37af30e
Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f
show_exit=0
```

- The report-recording tip (`f87108a25ac9048d8d1a30ec0a1443831a4197e2`) was itself annotated; mapped-fetch
  `show`, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f" f87108a25ac9048d8d1a30ec0a1443831a4197e2
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   b6daecb..1faeb2c  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg151-fetched-e2
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg151-fetched-e2
fetch_exit=0
$ git notes --ref=refs/notes/sg151-fetched-e2 show f87108a25ac9048d8d1a30ec0a1443831a4197e2
Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f
show_exit=0
```

- The final tip (`61f3a97fa76ce0fa205244e0d373699a5daa96fa`) was also annotated; mapped-fetch `show`,
  verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f" 61f3a97fa76ce0fa205244e0d373699a5daa96fa
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   1faeb2c..48dc344  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg151-fetched-e3
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg151-fetched-e3
fetch_exit=0
$ git notes --ref=refs/notes/sg151-fetched-e3 show 61f3a97fa76ce0fa205244e0d373699a5daa96fa
Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: 88688f50761c76e07a011cc2576adf5eb112924f
show_exit=0
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| Orientation + premise verification (fetch, diff, 3-way checks, BASE probe) | ordinary | 120 s | ~90 s |
| G0 fail-pre (test + pytest) | ordinary | 120 s | < 5 s |
| G0 pass-post (apply #36 + pytest) | ordinary | 120 s | < 5 s |
| G1 fold #39 + repath #34 + reconciled test + probe | ordinary | 120 s | < 30 s |
| G2 full suite | suite class | 600 s | 34.05 s |
| G2 targeted + ruff + mypy + secret scan | ordinary | 120 s | ~50 s |
| Worklogs + commit + push | ordinary | 120 s | < 20 s |
| Receipt notes (add/push/fetch/show, twice) | ordinary / notes-push | 120 s / 300 s | < 20 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | ~ well inside cap (14:34Z→ report) |

Actual-versus-budget per goal: every leg well inside its class; overall well inside the 2400 s cap. No
command was killed by its bound; no interactive command ran. **Real metered spend $0.000000 USD, zero
metered calls.**

## UNCLEAR

- **FIRST READ:** the packet's "duplicate evidence attach leaves duplicates-or-swallow" reads naturally
  as two possible BASE behaviors; the measurement pinned it to **swallow** (PK already blocks duplicates;
  the `except: pass` hides both duplicate-key and FK errors). I keyed the fail-pre test on the real
  discriminator — the missing warning — and recorded the correction rather than bending the test.
- **DURING EXECUTION:** #36 deletes the swallow entirely, so repathing #34's log needed a design call the
  packet left to me: keep the bulk insert, and on its atomic failure `rollback()` + per-item fallback that
  logs both ids. This preserves the N+1 fix, restores failure visibility, and leaves good links landing;
  the rollback touches only the failed batch. The reconciled test asserts both the dedup and the log.
- **REMAINING:** nothing on this slice's account beyond the shipped merge; the served-code change is not
  live until the standing close-out rider rebuilds/recreates (Deploy: none here). F-SG151-4 (the `CO-53`
  work-commit-ID practice) is outside this slice and offered for reconciliation.

## RECOMMENDED-NEXT

- **Batch C per SG-149 order:** #33 + folded #37.

**note=yes**
