# SG-088 — derived table registry: remove the EXPECTED_TABLES static copy, keep the tripwires

**Dispatch-ID:** SG-088
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` resolved):** `2d6c6b1bd9ec86bfb3ea33d884ff21a901cccbae` (`SG-091 receipt: paste verified notes-ref show output (docs-only)`)
**WORK_HEAD:** `e710a80c0e9168f4db49308cbd50997e838decc9` (the slice tip; the receipt note lives on this commit and this docs-only descendant carries the paste).
**Contract:** recorded `0.28.2` == published `b495b59` — source path `/home/andrei/storagegenie-contract/VERSION`; `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `b495b59b3426af66772a87939473ac558f8f72d2`.
**Model / effort (`CO-78`, from process arguments):** model `unknown` (argv carries no `--model`; the CLI default is the model per policy); effort `medium` (argv `--variant medium`). Source: `/proc/598312/cmdline` via `pgrep -af "opencode run"` → `opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-088 …`.
**Spend:** **$0.000000 actual** — zero provider calls; containment per `PG-PR-04` stated: nothing live exists to contain.
**Live clock at open:** `2026-09-21T17:53:59Z`.
**Autonomy:** `L2` slice (no retry used).

## Verdict: **GREEN** — the static copy is gone, both tripwires intact and seen-to-fail

`EXPECTED_TABLES` (18-name static set) and its cross-file import are removed. The dialect pin now derives
from the REAL `Base.metadata`; the taxonomy exit pin now asserts `before == after`. Product code
(`app/`, models, migrations) has **zero hunks**. The identical planted table that trips the old static
pins passes the derived pins (FAIL→PASS); both new pins were fed bad input and failed loudly. Suite,
lint, types and secret gates are unchanged from bare BASE.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on disk 2026-09-21 | Verdict |
|---|---|---|
| static set at `test_postgres_dialect.py:35-54`, 18 names | BASE parsed from HEAD: static count = 18; live `Base.metadata` count = 18; `derived == static: True`; `static-only: set()`; `metadata-only: set()` | **confirmed** |
| consumed at `:59,:63,:65` | `git grep -n EXPECTED_TABLES HEAD` shows exactly `:35,:59,:63,:65` in that file | **confirmed** |
| imported at `test_plugin_taxonomy.py:25` for pins `:62,:83` | grep shows `:25` import, `:62`, `:83` | **confirmed** |
| an unlisted third consumer is a finding | no third Python consumer: every other HEAD hit is docs (packets/history/ratings/worklogs), not code | **no third consumer** |
| `EXPECTED_TABLES` is a second copy of `Base.metadata` + model imports | `derived == static` on BASE, exact both directions | **confirmed** (the dead set was pure duplication) |
| 2 known decoder env reds on bare BASE | re-run on bare BASE with the slice stashed: `2 failed, 376 passed` (`test_signals.py`) | **confirmed** (not inherited) |

## G1 — remove the static copy, keep both tripwires (tests only)

**Property separation is load-bearing and preserved.** The two pins protect different things, and the
derivation reflects that:

- **Dialect pin (completeness over whatever exists):** `metadata_tables = Base.metadata.tables`; every
  table in that mapping is compiled with the PostgreSQL dialect. There is no fixed list. A non-empty
  guard (`assert metadata_tables, "no tables registered — the app import did not run"`) prevents a
  vacuous pass on empty metadata.
- **Taxonomy exit pin (registration ADDS NO tables):** `before = set(Base.metadata.tables)` (guarded
  non-empty); after the real `register_plugin`, `assert after == before, f"registration changed the
  table set: {after ^ before}"`. There is no equality with a fixed set.

**Derivation is not a re-listed list.** The old per-model import block was itself a second list (a new
model needed a new import or the test silently under-covered). It is replaced by importing the app's
composition root (`import app.main`), which registers every served model — validated at 18/18. The
only remaining table-name literals in the test tree are two pre-existing 3-name SUBSETS for unrelated
properties (`FOUNDATION_TABLES`, `STAT_SOURCE_TABLES`); neither is the registry and neither was touched.

**FTS5 exclusion remains a RULE.** The docstring still states SQLite FTS5 has no PostgreSQL equivalent
and the objects are excluded by rule; `asset_fts` is raw SQL and never enters `Base.metadata`
(measured `asset_fts in metadata: False`). No name list is needed to exclude it.

**Seen-to-fail, each quoted (transient probes, removed; `SG-088_verify.log`):**

- **FAIL-PRE (the trap, `PG-EV-09`):** BASE files + a planted `Table("planted_extra", …)` in
  `Base.metadata` → the OLD pins fail loudly: `assert metadata_tables == EXPECTED_TABLES` →
  `AssertionError … Extra items in the left set: 'planted_extra'` (and the same on the taxonomy pin).
- **PASS-POST (same plant):** the DERIVED pins pass with the identical planted table (`4 passed`),
  because the dialect test compiles whatever exists and the exit pin only needs `before == after`.
- **Tripwire (a) exit pin:** a test-space registration that adds a table →
  `AssertionError: registration changed the table set: {'planted_registration_table'}`.
- **Tripwire (b) dialect compile:** a planted `Column("x", NullType)` →
  `sqlalchemy.exc.CompileError: (in table 'planted_uncompilable', column 'x'): Can't generate DDL for NullType()`.

Both plant probes were removed; `git status --porcelain` lists only the two intended test files
(verified in the raw log).

**`PG-SC-12` (real thing, not a fake):** both pins read the REAL `Base.metadata.tables` and the REAL
`register_plugin` import; no fixture metadata re-implements the table set.

## G2 — gates + no other movement (green, honest)

- **FAIL-then-PASS both committed raw** to `SG-088_verify.log` (`PG-EV-09`). Composition stated
  explicitly: this is a tests-only, no-behaviour-change slice, so the *new* tests pass on BASE by
  construction; the FAIL half is the planted table tripping the *old* pins (and the two tripwire plants
  against the new mechanism) — never silently claimed as a pre/post regression.
- **`PG-SC-11` end-relative grep + verdicts (raw in the log):**
  - `test_signals.py:125,126` — `ean_value[-1]`, the EAN-13 checksum digit; **position-independent, not a table assertion**.
  - `test_chat.py:454` — `provider.texts[-1]`, the last provider text; **position-independent, not a table assertion**.
  - `== 18` count literals: `test_ai_pipeline.py:750,836` — `usage_json["total_tokens"] == 18`; **token count, not a table count; position-independent**.
  - `latest` / `HEAD~1` / tail globs over tables/metadata/registry: **0 hits**.
  - The old `== EXPECTED_TABLES` legs: `EXPECTED_TABLES` grep = **0 hits** — no leg still names the removed set.
- **Full backend suite:** bare BASE `2 failed, 376 passed, 22 warnings in 19.02s`; POST `2 failed, 376 passed, 22 warnings in 19.50s` — same two known decoder env reds (`test_signals.py`), **delta 0**.
- **ruff:** `All checks passed!` (exit 0).
- **mypy delta 0:** `mypy app` = `Found 41 errors in 9 files` on both BASE and POST (no `app/` hunk). Changed test files (`--follow-imports=skip`) = `4 errors in 1 file` on both BASE (taxonomy lines 39,49,88) and POST (same errors at 38,48,87, shifted by the removed import) — **delta 0, test files included**.
- **Secret grep-gate over the diff** (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken`, SG-037 shape): **0 hits**.
- **No table-adding product change** in this slice; **no second static registry copy** found (the two 3-name subsets are unrelated, pre-existing, unmodified).
- **Cross-product (`PG-IC-01`):** writes = the two test files + `docs/worklogs` (3 files); reads = the suite only; network = `git push` only; no container image pull/run; no provider call.

## G3 — worklog and report (unconditional per `CO-57`)

Evidence committed, not merely reported: `docs/worklogs/SG-088.log` (narrative + leg timings),
`docs/worklogs/SG-088_report.md` (this), `docs/worklogs/SG-088_verify.log` (raw commands + verbatim
outputs + BOTH fail-then-pass runs + every enumeration). First token `SG-088`; spend `$0.000000 actual`;
contract echo + source path above; three UNCLEAR lines below.

## Findings / corrections (reported, not bent)

- **F-SG088-1 (packet premise nuance).** The packet called the model imports part of "what
  `Base.metadata` + the model imports already define". True, but the per-model import block in the
  dialect test was *itself* a hand-maintained list with the same failure mode (a new model not imported
  there would be silently uncovered). The derivation therefore imports the app composition root instead
  of re-listing models. This is a strengthening of the packet's intent, not a divergence.
- **F-SG088-2 (report only; out of scope).** `FOUNDATION_TABLES` (`test_foundations.py:24`, 3 names)
  and `STAT_SOURCE_TABLES` (`test_analytics.py:36`, 3 names) are static table-name tuples. They are
  pre-existing, scoped to unrelated properties (foundation indexes, analytics source tables), and are
  **not** a copy of the removed registry; left untouched per the scope ceiling. Named so the Architect
  can judge whether a future slice wants the same derivation treatment for them.
- **F-SG088-3 (tooling artifact).** At BASE, `mypy app tests` aborts with a duplicate-module error
  (`tests/test_postgres_dialect.py` imported both as `tests.…` and top-level) and reports `1 error …
  errors prevented further checking`; removing the cross-test import lifts the abort. This is a
  side-benefit, not a gate: the documented gate is `mypy app` (41-in-9, unchanged).
- **F-SG088-4 (transient-probe policy).** Two transient probe files were created and removed
  (`tests/_sg088_trapprobe.py`, `tests/_sg088_plantprobe.py`); neither is committed. The derivation did
  **not** need a new test home, so no new test file is added.

## Receipt

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. The note was added on the slice-tip WORK_HEAD, the notes ref pushed (300s bound),
then fetched explicitly into a **mapped** local name and shown. No existing note was refused
(`show_before_exit=1`, "no note found").

Commands executed (raw):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show e710a80c0e9168f4db49308cbd50997e838decc9   # existing-note check
error: no note found for object e710a80c0e9168f4db49308cbd50997e838decc9.
show_before_exit=1
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-088 | Report: docs/worklogs/SG-088_report.md | Work-HEAD: e710a80c0e9168f4db49308cbd50997e838decc9" e710a80c0e9168f4db49308cbd50997e838decc9
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   ab0aa59..3391108  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes_push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg088-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg088-verify
fetch_exit=0
$ git rev-parse refs/notes/storagegenie-coder-reports-sg088-verify
339110833ee01a25f837178667783af5eae5abc9
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg088-verify show e710a80c0e9168f4db49308cbd50997e838decc9
```

Pasted `show` output (verbatim, from the FETCHED mapped ref):

```
Dispatch-ID: SG-088 | Report: docs/worklogs/SG-088_report.md | Work-HEAD: e710a80c0e9168f4db49308cbd50997e838decc9
```

note=yes

## Acceptance criteria → question each answers (`PG-SC-09`)

- **G1 — is the list gone with both tripwires intact?** Yes. `EXPECTED_TABLES` 0 hits; dialect pin
  derives + compiles every metadata table and fails a planted uncompilable construct; exit pin asserts
  `before == after` and fires on a planted table-adding registration; FTS5 still rule-excluded.
- **G2 — is the suite green for the right reason?** Yes. Same 2 decoder env reds on bare BASE and POST,
  376 passed both; ruff clean; mypy delta 0; secrets 0; end-relative hits listed with verdicts; no leg
  names the removed set. The FAIL half is real bad input, not a vacuous pass.
- **G3 — is the evidence committed, not merely reported?** Yes — the three worklog files are committed
  with the slice; both fail-then-pass runs and every enumeration are in `SG-088_verify.log`.
- **No vacuous pass:** each pin carries a non-empty guard; both tripwires were fed bad input and quoted;
  the trap removal is proven by the same plant failing old pins and passing derived pins.

## UNCLEAR

- **FIRST READ:** whether removing the explicit model imports could let the dialect test silently
  under-cover. It could — which is exactly why the derivation imports the composition root
  (`app.main`) rather than a new model list; still, a model never wired into the app would be invisible
  to this test. Reported as F-SG088-1.
- **DURING EXECUTION:** whether `FOUNDATION_TABLES` / `STAT_SOURCE_TABLES` count as "a second static
  copy anywhere" (a STOP). Judged no — they are 3-name subsets for unrelated properties, pre-existing
  and unmodified — and reported as F-SG088-2 rather than silently shipped or silently stopped.
- **REMAINING:** whether the anatomy of the EAN/OCR decoder env reds (`test_signals.py`) should be
  turned into a slice; out of this scope and red on bare BASE, so nothing here fixes or hides it.
