# SG-123 — Freeze sg026: manifest the 5 loose fixtures so the selector sees them

**Settings travel on the trigger** (`SG-123 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved slice (second of the L3 residual-completion stage; SG-122 SEEDED 98). SG-085's REMAINING (report :140-141): "`sg026`'s loose files still have no manifest, so the selector cannot see them (correctly). If a later slice wants sg026 frozen, it must first give those 5 files a manifest." SG-089's limit 4 says the same. THIS slice is that later slice: move the 5 loose `backend/eval/corpus/sg026_*.json` into `backend/eval/corpus/sg026/` with a manifest, extend the selector test, and record the frozen offline score — nothing else. Verdicts: FROZEN (sg026 selectable, integrity OK, frozen record committed, suite holds) / BLOCKED (a shape mismatch stopped the move — commit, receipt, clean tree). **No scoring-code change is made here; no live call, no key, no network, no rebuild, no recreate.** **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** offline data-only. Writes: the moved fixtures + `corpus/sg026/manifest.json` + `backend/eval/baseline_sg026_frozen.md` + the `test_eval_corpus.py` selector lines + `docs/worklogs` (3 files) — and NOTHING else. `backend/eval/run.py` + scorer get ZERO hunks (prove by empty diff — any scoring hunk is a STOP). History stays byte-identical: `baseline_sg026.md` + `baseline_sg029.md` + the three frozen records (empty diffs quoted — a hunk there is a STOP). No live leg of any kind ($0 — scripted transports only; a metered call is a STOP-and-report). No served-behavior change, so no rebuild and no recreate (SG-085 precedent: eval-data-only).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-04` (no served-code change — proof scoped to offline runs).

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none. Container actions: none.**

## G0 — premises on the corpus (expectations, verify each — `PG-IC-09`)

- `backend/eval/corpus/` holds exactly `sg029/` + `sg049/` + `sg079/` + the 5 loose `sg026_*.json` (SG-085 :24 confirmed; a sixth entry is a finding).
- Selector shape (read, never inherited): `run.py:60-66` (`available_corpora` = parent names of `*/manifest.json`; `manifest_path` = `CORPUS_DIR / corpus / manifest.json`), `:82-84` (fixtures resolve under `manifest["base_dir"]`), `:119-139` (`check_manifest`: count == listed, every listed file present, disk == manifest). Template: `corpus/sg049/manifest.json` (keys `corpus`/`description`/`base_dir`/`count`/`fixtures`).
- Test pins: `tests/test_eval_corpus.py:177` (`SELECTED_CORPORA = ("sg029", "sg049", "sg079")`) and `:236` (`"sg026" not in known`). Both flip in G2 — the flip is EXPECTED here, stated upfront so no tripwire misfires.

## G1 — move + manifest (data only, history preserved)

- `git mv` the 5 loose files into `backend/eval/corpus/sg026/` (move, never copy-and-delete — history follows the files). Filenames byte-identical.
- Write `backend/eval/corpus/sg026/manifest.json` in the sg049 key shape: `corpus: sg026`, `base_dir: sg026`, `count: 5`, the 5 filenames, and an honest description (v1 scoring-only fixtures with offline-authored provider_output, no images, no metered calls — the SG-026 baseline report is the provenance).
- Prove with the REAL `run.py` (never a hand-rolled check): `--corpus sg026` integrity OK with `count 5`, and `available_corpora()` now lists sg026 with the default still sg029. Quote both.

## G2 — selector test + frozen record + suite (fail-then-pass, both runs committed — `PG-EV-09`)

- Extend `:177` with `"sg026"` and flip `:236` to `"sg026" in known` (the flip this slice exists to earn). FAIL-pre: run the updated test BEFORE the move (it fails — quote it); PASS-post: after the move (green — quote it). Non-vacuity (`PG-SC-12`): the test flip rides the data change, and the independent proof is G1's real-`run.py` integrity run, not the test itself.
- Score sg026 OFFLINE through the real scorer and record `backend/eval/baseline_sg026_frozen.md` in the sibling frozen shape (per-fixture table, `$0.000000`, selector invocation quoted).
- Full suite green-except-base-proved-reds (bound 600s); ruff clean; mypy quoted with untouched-file advisories as findings. Old baselines (`baseline_sg026.md`, `baseline_sg029.md`) + three frozen records byte-identical (empty diffs quoted); scoring code zero hunks (empty diff over `run.py` + scorer quoted).

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-123.log`, `SG-123_report.md`, `SG-123_verify.log` (both raw test runs + real-`run.py` outputs + every empty diff). First token `SG-123`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the 5 moved fixtures, `corpus/sg026/manifest.json`, `baseline_sg026_frozen.md`, the two `test_eval_corpus.py` lines, `docs/worklogs` (3 files). **Any other hunk — scoring code, history baselines, suite files beyond the two lines, product code — is a STOP.**
- Cross-product (`PG-IC-01`): G1 needs filesystem moves + one manifest write; G2 needs test runs + suite + frozen record; nothing else. No criterion touches containers, the DB, the network, or the running service. Reads explicitly INCLUDE running `eval/run.py` and the suite in-process; pulling any image or launching any other runtime is NOT included and is a STOP.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): move, manifest, prove, freeze. No scorer refactor, no new corpus features — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): move — are the fixtures addressable without losing history? manifest — does the selector's own authority now list sg026? freeze — is sg026's offline score recorded like its siblings?
- `git status` shows exactly the ceiling set (5 renames + manifest + frozen record + test file + 3 worklogs); `available_corpora()` lists sg026, default still sg029, integrity OK — all quoted from real runs.
- Updated selector test FAIL-pre→PASS-post, both raw runs committed and quoted; frozen record carries the per-fixture table + `$0.000000`.
- History + scorer diffs empty as quoted; suite green-except-base-reds; no vacuous pass (the pre-move failure is the discrimination — a flip without it evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-123 | Report: docs/worklogs/SG-123_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
