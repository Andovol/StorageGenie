# SG-120 — Group C docs sweep: README Phase 4/5, AGENTS pointer, enrich docstring

**Dispatch-ID:** SG-120
**Coder / effort:** `opencode` / effort **`high`** — read from the process arguments
(`pgrep -af "opencode run"` → `opencode run --auto --dir /home/andrei/StorageGenie --variant high # SG-120 …`).
**MODEL:** `deepseek-v4.1-flash` (provider `opencode-go`) — read from provider metadata
`/home/andrei/.local/state/opencode/model.json` `recent[0]`; the argv carries no `--model` flag, so the
CLI default is the model. Not taken from a system-prompt identity line.
**Work dir:** `/home/andrei/StorageGenie` · **branch** `automation` · **remote**
`git@github.com:Andovol/StorageGenie.git`
**BASE REF:** `origin/automation` → **BASE_RESOLVED:** `b62c7e207785f21e2a92ed7554c8e8b8802bf50f`
(== start HEAD; two fields, never one).
**WORK_HEAD:** `44e867e9a9889042907917a235ec0e17341d7e78` (the docs-only worklog commit is the later tip).
**DATABASE:** none · **Restart:** none · **Deploy:** none (no served-behaviour change).
**Autonomy:** L2 slice (packet); 1 retry available, not used.
**Spend (real $):** **$0.000000** actual vs $0 bound — zero metered provider calls.
**Coder process start:** 2026-09-25T10:55:48Z.

**Contract echo (verbatim):** recorded **`0.36.0`** == published **`0.36.0`**.
**Source path:** `/home/andrei/storagegenie-contract/VERSION` (`0.36.0`); contract HEAD
`a9324d5e1782384c036c1411ec8adac6bb2acaa1`; installed `RULES.md` sha256
`18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`.
The repo's `.rules-cache/` directory is **absent** on this host (F-SG120-1), the same standing
observation as SG-062/SG-078/SG-099/SG-104–SG-119.

## G1 — AGENTS pointer ISS-5 (GREEN)

`AGENTS.md:61` `(contract \`contract-v0.25.0\`)` → `(contract \`contract-v0.36.0\`)`. One string, nothing
else in the file. Pre/post quoted in `SG-120_verify.log`.

**Absence, scoped honestly.** In-source: `git grep -n "contract-v0.25.0" -- AGENTS.md` → **0 hits**
(exit 1); `README.md`/`backend/` → 0 hits. Tree-wide the exact old string still occurs **20 times**, every
one historical: `STATE.md:8` (the Architect's own open-thread note naming the stale pointer — not writable
here), the packet `docs/packets/SG-120-docs-sweep.md` quoting it, and prior `docs/history` /
`docs/worklogs` / `output/dispatch` logs. **No live source or pointer carries it.** This is not a
tree-wide-zero claim; it is a source-clean claim with the historical hits named.

**Cache check (packet instruction):** `.rules-cache/` does not exist anywhere on the host
(`find / -name .rules-cache` empty), so the directory's state cannot contradict the pointer. The adopted
version is verified from the host contract checkout (`VERSION` `0.36.0`, HEAD `a9324d5`, hash clean) and
matches `AGENTS.md:4` + `STATE.md:4`. Nothing invented.

## G2 — enrich docstring F-SG119-2 (GREEN)

`backend/app/api/v1/enrich.py` docstring block (was 112–114) corrected: `brand` **IS** in
`LABEL_VISIBLE_FIELDS` and the OFF path emits one under `web:OpenFoodFacts` (so a label brand wins the
proposal and the web value becomes its visible alternate); Jina still emits none; the OFF-miss population
(`PG-SC-07`) still maps to nothing. I also replaced the now-inaccurate "frozen SG-082" descriptor with
"`LABEL_VISIBLE_FIELDS` vocabulary (SG-082, extended by SG-119)" — same docstring block, no code.

**Code untouched — behaviour-identical proof:** `git diff -U1` shows only docstring lines (10 insertions,
7 deletions, zero code lines). enrich test set (9 files:
`test_sg081_enrich_fetch` · `test_sg082_enrich_jina` · `test_sg098_enrich_endpoint` · `test_sg099_synthesis` ·
`test_sg100_snapshot_persistence` · `test_sg101_text_path` · `test_sg102_enrich_wiring` ·
`test_sg103_web_alternates` · `test_sg119_brand_alternates`) **120 passed before, 120 passed after**;
`py_compile` OK; ruff clean. Absence grep in `backend/app` for the false claim → 0 hits (tree-wide hits are
historical worklogs/logs + the packet).

## G3 — README Phase 4 + Phase 5 runbooks (GREEN)

Two `##` sections appended after the Enrich runbook (`README.md:425` and `:488`): "Phase 4 runbook —
photo-ingest v3, 20 MB uploads, plugin domains" and "Phase 5 runbook — hardening". Every claim is grounded
in a path that exists on this tree (existence check in `SG-120_verify.log`): the v3 fields at
`schemas.py:52-67`, the v3 prompt files, `reader.py` map, the plan docs, the slice suites,
`config.py:20` + `evidence_service.py:142` + `evidence.py:53` for the 20 MB/413 story,
`test_plugin_taxonomy.py:58` + `registry.py:34` for the exit proof, `eval/run.py` + the three frozen
baselines + `test_eval_corpus.py`, `backup_restore_drill.py` + `test_backup_drill.py`,
`test_privacy_audit.py`, `test_postgres_dialect.py`. The SG-061 host nginx measurement (25M) is quoted as a
host measurement from `docs/worklogs/SG-061_report.md` and **not** re-measured this slice. Key material
stays names-only; no screenshots prose, no marketing.

**Ungrounded claims omitted (not written):** no Phase 4 section claim was left ungrounded. I explicitly
did **not** write a `test_phase4_e2e.py` (it does not exist) and did **not** claim the live reader serves
v3 — the committed map serves v4 (F-SG120-2), stated in the section.

## Findings (a difference is a finding, not an obstacle)

- **F-SG120-1 — `.rules-cache/` absent on host.** Same standing observation as SG-062/SG-078/SG-099/SG-104–119.
  Contract authority read from `/home/andrei/storagegenie-contract/`. No action owed beyond the record.
- **F-SG120-2 — Phase 4 premise partially stale.** The packet says "photo-ingest v3 … served by SG-083"; the
  committed `reader.py:54-58` now loads **v4** (`extract-{food,medicine,cosmetics}-v4.md`, SG-095). The v3
  delivery is history and the section says so; the current live map is stated accurately. Correcting the
  packet in-text rather than bending the tree.
- **F-SG120-3 — root `venv/` is not the test env.** `README.md` (Phase 0/2) prescribes `../venv/bin/python`
  (the repo-root venv), which lacks `pillow_heif`; the import chain through `reader.py:33` →
  `evidence_service.py:11` (`from pillow_heif import register_heif_opener`) then fails, so no test collects.
  `backend/venv/bin/python` is the working env (SG-119 used `./venv/bin/python` from `backend/`). Out of
  scope to edit; reported with destination README Phase 0 or the environment.
- **F-SG120-4 — full-suite reds are the known decoder environment class.** `2 failed, 593 passed`; both reds
  are `tests/test_signals.py` with `pyzbar/libzbar is not installed` and `tesseract is not installed`. This
  matches the SG-119 baseline class (there `2 failed, 581 passed` with more tests since). Not caused by this
  docstring-only change (which cannot touch `signals.py`).

## No vacuous pass

- The absence greps are quoted raw, including the tree-wide non-zero historical hits — not a narrowly scoped
  pass.
- The enrich-set pre/post counts are from the same 9-file selection; identical 120/120.
- The receipt `show` is pasted from the **fetched mapped ref**, not from the local write ref.

## Scope ceiling

`git status --porcelain` before commit 1 shows exactly `AGENTS.md`, `README.md`,
`backend/app/api/v1/enrich.py`; `docs/worklogs/SG-120.{log,report.md,verify.log}` are the only other writes.
No code/tests/prompts/compose/`.env`/migrations/STATE written. No build, no container action, no DB touch,
no `docker compose config`. Nothing pushed to `storagegenie-evidence`; `{{RECEIPT_CMD}}` not invoked.

## Receipt (notes ref)

Commit 1 (work) pushed `b62c7e2..44e867e` to `automation`. Note anchored on `WORK_HEAD`; worktree clean.

Pasted verbatim from the **fetched mapped ref** (`git fetch origin
refs/notes/storagegenie-coder-reports:refs/notes/sg120-verify`):

```
$ git notes --ref=refs/notes/sg120-verify show 44e867e9a9889042907917a235ec0e17341d7e78
Dispatch-ID: SG-120 | Report: docs/worklogs/SG-120_report.md | Work-HEAD: 44e867e9a9889042907917a235ec0e17341d7e78
```

Pre-add check (`... show <WORK_HEAD>` on the write ref) returned "no note found" (exit 1), so the
existing-note refusal did not fire. Notes push: `1b54aad..1518799  refs/notes/storagegenie-coder-reports`.

note=yes

## Budget

| Leg | Actual | Bound | Units |
|---|---|---|---|
| Recon + premise verification | ~180 | 60/command | s |
| G2 baseline enrich tests | 3.76 | 60 | s |
| Full backend suite | 29.70 | 300 | s |
| Edits + post-checks (grep/compile/ruff/tests) | ~40 | 60/command | s |
| Commit + push + notes + mapped verify | ~90 | 300 | s |
| **Slice total (process start → close)** | **~390** | **300 expected** | **s** |

The slice ran ~90s over the packet's ~300s expected figure; the overrun is the reconnaissance reads of the
Phase 4/5 worklogs and plans needed to ground G3. Every individual command stayed within its stated bound;
no command was killed. Spend $0.000000.

## UNCLEAR

- **FIRST READ:** the packet's Phase 4 premise ("photo-ingest v3 … served by SG-083") is stale against the
  tree — the committed reader loads v4 (SG-095); and the root `venv/` the README prescribes cannot import
  the app (`pillow_heif` missing), so I ran tests with `backend/venv`. Both corrected in place and reported
  (F-SG120-2, F-SG120-3).
- **DURING EXECUTION:** `grep -rn "contract-v0.25.0"` tree-wide is not zero and cannot be — the old string
  survives in the Architect's `STATE.md` open-thread and in the packet/history; I reported source-clean plus
  the historical carriers rather than a false tree-wide zero. The receipt `show` is pasted from the mapped
  fetched ref.
- **REMAINING:** F-SG120-1 (`.rules-cache/` absent — standing), F-SG120-2 (Phase 4 premise now a README
  note), F-SG120-3 (README's root-venv test path vs `backend/venv` — destination: Phase 0 README hunk or
  environment fix), F-SG120-4 (decoder env reds — pre-existing). `STATE.md` still lists ISS-5 in its open
  threads even though this slice fixed the pointer; removing that line is the Architect's write, not mine.
