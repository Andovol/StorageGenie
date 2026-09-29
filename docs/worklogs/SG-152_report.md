MERGED: #33's `backend/tests/test_schemas_common.py` landed byte-exact (blob `9ec30b77` == PR head blob);
#37's unique cases (loads_json list/int/bool/string, unicode dumps_json) folded in; the duplicate #37 file
DROPPED (single adopted file, no add/add collision). FULL suite delta exactly +10 green = the one new file,
base-reds identical. Test-only: no served-code change, no live proof owed.

# SG-152 — merge Batch C: schemas-common tests (#33 + folded #37, test-only) — report

**Dispatch-ID:** SG-152
**Role:** Coder (never Architect — no dispatch verb run for any ID, no unit started or polled).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved commit):** `b26139c2a735e62fa688e0b567484be83da3ea7d`
(the ref and the resolved commit are stated separately — two fields, never one; ref == commit this run).
**WORK_HEAD:** `e8f20a30c3313df4117e3396bb9df3bb0cef054a` (the one new test file, folded, committed; the
land commit is its parent `dd22af343f0160d265629514f952f54e5e35d0ec`).
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` =
`f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c` (subject `Contract payload 0.40.0`); payload `RULES.sha256` =
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`. (`.rules-cache/` is absent on the
host — SG-145 F-SG145-1; the live checkout above is the contract path.)
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort
`high` — source `/proc/<pid>/cmdline` (parent `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high # SG-152 …`). No system-prompt identity used.
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (local fetch/land, `TestClient`-
free pure-unit test, temp-isolated mutation copy, full temp-SQLite suite, lint/type). No USD-metered call
exists on any path.
**Live clock (`PG-IC-07`):** first capture `2026-09-29T14:44Z`; as-of-report-writing `2026-09-29T14:48Z`.
**Autonomy:** `L2` (merge-batch arc, D-0929-3 2nd word). **DATABASE none, restart none, deploy none**
(test-only slice — `PG-PR-04` not invoked; stated).

## Verdict: **MERGED** (test-only slice, no rider, no rebuild/recreate/deploy)

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| `test_schemas_common.py` absent at BASE | `ls` → ENOENT (exit 2); `git cat-file -e origin/automation:…` → exit 128. | confirmed |
| zero test refs to `decode_cursor`/`loads_json` | `grep -rn "decode_cursor\|loads_json\|encode_cursor\|dumps_json" backend/tests/` → no line (exit 1). | confirmed |
| `common.py:15-36` carries both cursor branches | Read: spec `f"{id}:{created_at.isoformat()}"` + decode `:` branch; legacy `ts\|id`; `return None` no-separator; `except Exception: return None`; `dumps_json ensure_ascii=False`; `loads_json` None/success/except. | confirmed |
| suite 2/638 with 2 known base-reds (`test_signals` env pair, SG-151) | Full suite after +1 file → `2 failed, 648 passed`; reds are the same two `test_signals` cases. BASE count `2/638` taken from the SG-151 record (not re-run at BASE, see UNCLEAR). | confirmed (delta) |
| alembic single head `sg114` (untouched) | No migration file touched; diff ceiling is one test file. | confirmed (by diff) |
| #33 file asserts the real branches; #37 collides on the exact path with unique list/int/bool + unicode | Both heads add only `backend/tests/test_schemas_common.py` (87/78 lines); blobs `9ec30b77`/`ed852cdd`; `common.py` blob identical to BASE on both heads (`8ef2b672`). | confirmed |

## G0 — absence proof at BASE (`PG-EV-08`)

- The coverage gap is the fail-pre (there is no red run for unborn coverage). `ls` ENOENT + grep empty +
  `cat-file` exit 128 — all three committed to `SG-152_verify.log`. No conflicting file landed since the
  audit; if one had, that would have been a STOP (never overwrite, never duplicate) — it did not.
- Non-vacuity for unborn coverage cannot come from a red run; it is discharged at G1 by **mutation** —
  every assertion is shown to fail when its real `common.py` branch is broken.

## G1 — union file from the real heads (`PG-SC-12`, `PG-EV-09`)

**Blob identity.** `git show origin/pr/33:backend/tests/test_schemas_common.py > backend/tests/test_schemas_common.py`,
then `git hash-object` = `9ec30b77e2924fd7f8d99c1915f48f05b29bb5a8` == `origin/pr/33` blob. Landed blob at
`dd22af3` re-verified equal. #37 was **not** applied as a file (add/add); only its unique cases were
folded, so the `dd22af3 → worktree` diff is **additions at EOF only** (`87a88,106`).

**Both heads' case enumeration — kept / folded / dropped.** (`kept` = landed from #33; `folded` = unique
#37 added into the single file; `dup` = dropped because #33 already pins the same branch.)

| # | Case (input class) | Real `common.py` branch pinned | Disposition |
|---|---|---|---|
| 33.1 | spec `id:iso` round-trip | `encode_cursor` spec + decode `":"` split→`fromisoformat` | kept |
| 33.2 | legacy `ts\|id` | decode `"\|"` branch | kept |
| 33.3 | invalid base64 | decode `except Exception → None` | kept |
| 33.4 | no `:`/`\|` separator | decode trailing `return None` | kept |
| 33.5 | bad ISO with `:` and with `\|` | decode `except Exception → None` | kept |
| 33.6 | empty string | decode `except Exception → None` | kept |
| 33.7 | dict round-trip / `None` / invalid string | `dumps_json`; `loads_json` None branch, success, except-fallback | kept |
| 33.8 | `ProblemDetail` fields + default `type` | model default `"about:blank"` | kept |
| 37.1 | `loads_json` list `[1,2,3]` | `loads_json` success (`json.loads`) | **folded** |
| 37.2 | `loads_json` int `123` | `loads_json` success | **folded** |
| 37.3 | `loads_json` bool `true` | `loads_json` success | **folded** |
| 37.4 | `loads_json` string `"string"` | `loads_json` success | **folded** (unique; packet named list/int/bool; string is the same batch of non-mapping cases — folded rather than silently dropped) |
| 37.5 | `dumps_json` unicode `こんにちは` round-trip | `dumps_json` `ensure_ascii=False` | **folded** |
| 37.6 | `loads_json` dict / `None` / invalid | duplicates of 33.7 | dup |
| 37.7 | `loads_json` `{bad_json:}` / `not a json string` | same except-fallback as 33.7 | dup (extra invalid inputs; same branch) |
| 37.8 | spec round-trip / legacy / invalid trio / `ProblemDetail` | duplicates of 33.1,33.2,33.3-33.5,33.8 | dup |

**Mutation matrix (non-vacuity, `PG-EV-09`).** Isolated copy under `/tmp/opencode/sg152/mut` (product
tree never touched). Nine single-branch mutations, each caught by the named case; the harness first
asserted the imported module path and disabled bytecode writing:

| Mutation of `common.py` | Caught by |
|---|---|
| `encode_cursor` spec order swapped | `test_encode_and_decode_cursor_valid` |
| decode `":"` split order swapped | `test_encode_and_decode_cursor_valid` |
| legacy `"\|"` branch disabled (`if False:`) | `test_decode_cursor_legacy_format` |
| no-separator `return None` → tuple | `test_decode_cursor_missing_separator`, `test_decode_cursor_empty_string` |
| decode `except Exception` re-raises | `test_decode_cursor_invalid_base64`, `test_decode_cursor_invalid_timestamp_format` |
| `dumps_json` `ensure_ascii=True` | `test_dumps_json_unicode_not_escaped` (unique #37) |
| `loads_json` `None` branch changed | `test_json_dumps_and_loads` |
| `loads_json` except-fallback re-raises | `test_json_dumps_and_loads` |
| `ProblemDetail.type` default changed | `test_problem_detail_model` |

## G2 — gates (`PG-EV-01`, `PG-IC-08`)

- New file: `10 passed`.
- FULL backend suite: `2 failed, 648 passed, 32 warnings in 33.39s`; failures are exactly
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` — the SG-151 base-reds. **Blast radius:**
  delta is exactly `+10` green tests = the ONE new file; **no other delta** → not a STOP.
- `ruff check .` → `All checks passed!`
- `mypy app` → `Found 41 errors in 9 files (checked 90 source files)` — **delta 0** vs the recorded
  BASE `41/9`.
- Secret scan over added diff lines (`api key|secret|password|token|private key|AKIA…|ghp_|sk-…`) → no
  match. `CO-100` clean.
- Diff ceiling: `backend/tests/test_schemas_common.py | 106 +++++`, **1 file changed, 106 insertions** —
  exactly the ceiling (one new test file; no product/config, no second test file, no overwrite).
- Worktree clean (`git status --porcelain` empty, `CO-55`).

## Acceptance criteria (`PG-SC-09`) — answered

- **covered:** every `common.py` branch under test is pinned by a case that FAILS when the branch breaks —
  mutation-stated in the G1 table (9 mutations, 9 caught), not merely asserted. No assertion is true of a
  stub.
- **united:** every unique #37 case is present in the single adopted file (rows 37.1-37.5 folded); no
  duplicated file; every duplicate #37 case is enumerated and marked `dup`, none dropped silently.
- **clean:** diff is exactly the ceiling file — one new `backend/tests/test_schemas_common.py`; worklogs
  are the only other writes. No vacuous pass: the absence proof is a real ENOENT+grep-empty, and the
  mutation matrix rules out placebo assertions.
- **PG-PR-03 (stated):** this slice changes no served code; there is nothing to prove live and no deploy
  is owed.

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| Orientation + premise verification (fetch, diffs, blob hashes, contract) | ordinary | 120 s | ~60 s |
| G0 absence proof + case enumeration | ordinary | 120 s | < 10 s |
| G1 land (blob identity) + fold + new-file run | ordinary | 120 s | < 10 s |
| G1 mutation harness (9 mutations, isolated) | ordinary | 120 s | ~15 s |
| G2 full suite | suite class | 600 s | 33.39 s |
| G2 ruff + mypy + secret + ceiling | ordinary | 120 s | ~40 s |
| Worklogs + commit + push | ordinary | 120 s | < 20 s |
| Receipt notes (add/push/fetch-mapped/show, dual) | ordinary / notes-push | 120 s / 300 s | < 30 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | ~ well inside cap (14:44Z→ report) |

Actual-versus-budget per goal: every leg well inside its class; overall well inside the 2400 s cap. No
command was killed by its bound; no interactive command ran. **Real metered spend $0.000000 USD, zero
metered calls.**

## Receipt note on the notes ref

> Filled by executing the packet's note path and pasting the output verbatim. If this subsection carried
> no pasted `git notes … show` output, the step was not executed — it is executed, and pasted below.

Existing-note check before adding (must be empty): `git notes … show e8f20a3…` → `error: no note found`
(exit 1); `git notes … show 29f488d…` → `error: no note found` (exit 1). No refusal encountered.

Executed output, verbatim (`receipt1.txt`):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-152 | Report: docs/worklogs/SG-152_report.md | Work-HEAD: e8f20a30c3313df4117e3396bb9df3bb0cef054a" e8f20a30c3313df4117e3396bb9df3bb0cef054a
add_wh_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-152 | Report: docs/worklogs/SG-152_report.md | Work-HEAD: e8f20a30c3313df4117e3396bb9df3bb0cef054a" 29f488d494d1a87102ad825bbf669761a49be3ed
add_tip_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   7c4d37f..bd7bcb3  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg152-fetched-e1
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg152-fetched-e1
fetch_exit=0
$ git notes --ref=refs/notes/sg152-fetched-e1 show e8f20a30c3313df4117e3396bb9df3bb0cef054a
Dispatch-ID: SG-152 | Report: docs/worklogs/SG-152_report.md | Work-HEAD: e8f20a30c3313df4117e3396bb9df3bb0cef054a
show_wh_exit=0
$ git notes --ref=refs/notes/sg152-fetched-e1 show 29f488d494d1a87102ad825bbf669761a49be3ed
Dispatch-ID: SG-152 | Report: docs/worklogs/SG-152_report.md | Work-HEAD: e8f20a30c3313df4117e3396bb9df3bb0cef054a
show_tip_exit=0
```

The doubly-annotated tip `29f488d494d1a87102ad825bbf669761a49be3ed` (this report commit) and the work HEAD
`e8f20a30c3313df4117e3396bb9df3bb0cef054a` both carry the note; first line carries BOTH `Dispatch-ID:`
and `Report:` (`CO-97`). The final-tip dual-annotation is completed in the subsection below.

The record commit `92482822e069132ac9ad4d661031b1de62a941de` (the final tip at annotation time) was
dual-annotated; mapped-fetch `show`, verbatim (`receipt2.txt`):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-152 | Report: docs/worklogs/SG-152_report.md | Work-HEAD: e8f20a30c3313df4117e3396bb9df3bb0cef054a" 92482822e069132ac9ad4d661031b1de62a941de
add_tip2_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   bd7bcb3..fe5d3e4  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg152-fetched-e2
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg152-fetched-e2
fetch_exit=0
$ git notes --ref=refs/notes/sg152-fetched-e2 show 92482822e069132ac9ad4d661031b1de62a941de
Dispatch-ID: SG-152 | Report: docs/worklogs/SG-152_report.md | Work-HEAD: e8f20a30c3313df4117e3396bb9df3bb0cef054a
show_tip2_exit=0
```

## UNCLEAR

- **FIRST READ:** the packet named #37's unique cases as "`loads_json` list/int/bool, unicode `dumps_json`".
  #37 additionally carries `loads_json('"string"')`, which is equally unique against #33's dict-only case.
  Dropping it silently would be the finding the packet warns about, so I folded it too and marked it in
  the enumeration (37.4); the packet's list reads as illustrative of the non-mapping batch.
- **DURING EXECUTION:** my first mutation harness reused a copied `__pycache__` and reported the two cursor
  mutations as "passed" — a harness artifact (stale bytecode), not test behavior. Re-running with the
  imported module path asserted and `PYTHONDONTWRITEBYTECODE=1` caught all nine. Also: the repo-root
  `venv/` cannot collect the suite (`ModuleNotFoundError: pillow_heif`); the complete interpreter is
  `backend/venv` (pillow_heif 1.8.0). Both recorded rather than worked around.
- **REMAINING:** the BASE suite count `2/638` is taken from the SG-151 record; I measured only the
  post-change `2/648` (delta exactly the new file). No product or config surface was touched; nothing is
  live on this slice's account. The `venv/` vs `backend/venv` split and the `pillow_heif` gap are host
  environment findings outside this slice — offered for reconciliation.

## RECOMMENDED-NEXT

- **Batch D per SG-149 order:** #32, #35, #38, #41.

**note=yes**
