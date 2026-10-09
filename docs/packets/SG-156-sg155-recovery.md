# SG-156 — SG-155 report+receipt recovery: verify, report, receipt, $0

Autonomy: L3 (D-1009-7 Scene arc). SG-155 work complete at 461c96f but budget-killed in receipt phase — report + full receipt missing (FLAG:TRUST). This slice verifies that tree, writes the missing report, and publishes its own receipt. Comparison shifts to SG-157, T1b to SG-158.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.** No datastore is opened, temp or live.
**Restart: none.**

## Why this exists

SG-155 delivered all T0 substance (audited by the Architect from commit 461c96f) then died at elapsed=budget=2100s while writing logs+report. CONFIRMED from the pushed tree: `backend/app/services/scene/openrouter.py` (188 lines, frozen envelope, T0-PINNED stop types), `backend/tests/test_sg155_scene_t0.py` (fail-pre ModuleNotFoundError committed), `SG-155_t0live.log` (T0a: 10 real image models with prices, both GETs $0 keyless; T0b: 5 stop-condition types verbatim + reference-image answer text-prompt-only), suite 2/649→2/661 same base reds, ruff clean, mypy delta 0. INFERRED: nothing — every load-bearing fact above is committed bytes; re-verify each below rather than trusting this list.

## G1 — re-verify the SG-155 tree

Run the SG-155 tests + full suite on the lane: expect the same 2 `test_signals` environment reds (pyzbar/tesseract absent) and 661+ green; any different red gets the stash leg (base checkout, same command, both outputs committed). ruff clean; mypy with no error in `services/scene`. Small defects found here get fixed in-slice and disclosed; a structural defect is a STOP (precedence: fix-small wins, STOP beats re-verify loops — PG-IC-03).

## G2 — re-establish T0a/T0b fresh, $0

Re-run the two public keyless GETs (`/api/v1/models`, `/openapi.json`): confirm the shortlist slugs, prices, 5 stop types, and reference-image answer unchanged — drift is a finding with both values quoted, never a silent update. No Authorization header, no chat/render call, $0. Missing key is irrelevant here (no keyed call exists) and is NOT grounds to stop (PG-SC-03).

## G3 — reports + receipt, ordered FIRST (lever)

Publish-before-bound: G3 starts no later than half the elapsed budget — report+receipt before further verification, never after (SG-155 lesson). Write `docs/worklogs/SG-155_report.md` (the missing Coder report, first-hand: echo `SG-155` is NOT yours — that report documents the 461c96f work from your re-verified evidence; mark authorship honestly) + `docs/worklogs/SG-156_report.md` (echo `SG-156` first token). Publish the receipt through the bound `{{RECEIPT_CMD}}` wrapper (CO-97 note), referencing the SG-155 verification.

## Constraints

Scope ceiling: verify commands + the two report files + fail/pass logs if fixes were needed; no product-code change expected (fixes only per G1 precedence); no migration, no restart, no served-code change → no refresh. Secrets: key name-only; no secret file copied (CO-100); tests monkeypatch. $0 total: any metered call stops before sending (PG-IC-08, both directions — expected production writes: none). Hang bounds per class: ordinary 120s, suite 600s, HTTP GETs 120s — none near the 900s idle kill. Expected duration 300s (read-only precedent 107s/133s + 34s suite + reports; lane enforces `RUN_BUDGET_S`). Cross-product (PG-IC-01): no blanket bans in this packet — every criterion names its own action; no collisions possible. Full suite runs (derived-set block not pasted).

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

- A1: G1 re-verification green with both runs committed where fixes occurred (no new code expected → no fail-pre owed; any fix ships fail-pre — PG-EV-09).
- A2: G2 fresh $0 reads committed (`docs/worklogs/SG-156_t0recheck.log`): slugs, prices, stop types, reference answer — match or drift-with-both-values.
- A3: `docs/worklogs/SG-155_report.md` exists with identity line, legs, judgments, and UNCLEAR lines, all first-hand from this run's re-verification.
- A4: SG-156 report + receipt published (Dispatch-ID trailer on the notes ref); production writes == 0.
- A5: suite + ruff + mypy as G1; guards invoked: PG-EV-04, PG-EV-09, PG-SC-03, PG-IC-01, PG-IC-03, PG-IC-07, PG-IC-08, PG-IC-09.

## Report

Echo `SG-156` as the first token. Destinations: the two reports + recheck log above. Close with FIRST READ / DURING EXECUTION / REMAINING.
