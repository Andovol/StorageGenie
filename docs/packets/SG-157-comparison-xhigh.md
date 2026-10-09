# SG-157 — Coder comparison: independent T0 re-verification on muse-spark/xhigh, $0

Autonomy: L3 (D-1009-7 Scene arc; D-1009-9 comparison). Same T0 scope as SG-155/156, executed independently on the second selection to compare Coder-model behavior. T1b is SG-158 and waits on nothing here except the sequential rule.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.** No datastore is opened, temp or live.
**Restart: none.**

## Why this exists

D-1009-9 queues a same-scope comparison run: `coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh` (catalogue-valid, re-measured 2026-10-08). CONFIRMED from the pushed tree: the SG-155 seam (`backend/app/services/scene/openrouter.py`), its 12 offline tests, committed `SG-155_t0live.log` + `SG-156_t0recheck.log` (both MATCH), SG-155/156 reports. CAVEAT (stated, not assumed): the project lane note says the lane refuses `medium`/`xhigh` by name — if the trigger was refused you would not be reading this; if any in-slice step reports an effort refusal, quote it and STOP (no silent fallback to `high` — the fallback is the owner's call).

## G1 — independent re-verification

Re-run the SG-155 offline tests + full suite + ruff + mypy on the lane from your own reading of the code (do not copy SG-156's verdicts — derive them). Expect 12/12, suite 2/661 with the same 2 `test_signals` environment reds (stash leg if different), ruff clean, mypy no scene errors. Disclose your own comparison-harness bugs the way SG-156 disclosed its two (found-before-commit counts as process, hidden counts as defect).

## G2 — independent T0a/T0b pass, $0

Fresh public keyless GETs (`/api/v1/models`, `/openapi.json`): re-derive the shortlist slugs + prices, the 5 stop-condition types, and the reference-image answer from the live bytes — then compare against the committed logs (MATCH or drift-with-both-values). No Authorization header, no chat/render call, $0. Missing key is irrelevant, never grounds to stop (PG-SC-03).

## G3 — comparison judgment + reports + receipt, ordered FIRST

Publish-before-bound: reports + receipt before half the elapsed budget (SG-155 lesson, SG-156 proof). Write `docs/worklogs/SG-157_report.md` (echo `SG-157` first token): your verification tables, your T0a/T0b values, and an explicit comparison section — where your approach, errors, and disclosures differed from the SG-155/156 record and what that suggests about model behavior (stated per observation, no aggregate scores — D30). Publish the receipt through the notes-ref mechanism (`refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-157 | Report: <path>` + `Work-HEAD`, read back on remote — the bound `{{RECEIPT_CMD}}` script is retired, F-SG156-1).

## Constraints

Scope ceiling: verify commands + two public GETs + `docs/worklogs/SG-157_*` files; no product-code change expected (fix-small-or-STOP per SG-156 precedence); no migration, no restart, no served-code change → no refresh. Secrets: key name-only; no secret file copied (CO-100). $0 total, production writes 0 (PG-IC-08 both directions). Hang bounds per class: ordinary 120s, suite 600s, HTTP GETs 120s — none near the 900s idle kill. Expected duration 300s (SG-156 actual 355s all-in; lane enforces `RUN_BUDGET_S`). Cross-product (PG-IC-01): no blanket bans; every criterion names its action. Full suite runs (derived-set block not pasted).

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> **No bound reaches the lane's idle kill (`IDLE_KILL_S`, default 900 s):** a run printing nothing for
> that long is killed whole. Run longer work in the background and check it with short calls.
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Acceptance criteria

- A1: G1 green, committed verify log; any fix ships fail-pre (PG-EV-09); stash leg on any unexpected red.
- A2: G2 fresh $0 reads committed (`docs/worklogs/SG-157_t0recheck.log`): MATCH or drift-with-both-values; 0 Authorization headers proven by request dump.
- A3: comparison section with per-observation differences vs SG-155/156 (approach, errors, disclosures).
- A4: SG-157 report + notes-ref receipt read back on remote; production writes == 0; publish-before-bound honored with elapsed quoted.
- A5: suite + ruff + mypy as G1; guards invoked: PG-EV-04, PG-EV-09, PG-SC-03, PG-IC-01, PG-IC-03, PG-IC-07, PG-IC-08, PG-IC-09.

## Report

Echo `SG-157` as the first token. Destinations: `docs/worklogs/SG-157_report.md` + verify + recheck logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
