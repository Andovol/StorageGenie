# SG-274 — Second opinion Phase A (blind): the AI-no-date dead end

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

The next build slice must remove a dead end in the import flow, and no earlier review covered its design, so a blind pass runs before the Architect commits to one (`SECOND_OPINION.md` T3).

This is **Phase A — the blind phase.** You pick independently from the context pack.

## G1 — Blind read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section (project identity and configuration);
2. the context pack `docs/reviews/2026-11-02-f2-date-dead-end-context.md`;
3. every file the context pack names in its "Where it lives" table, as far as each question needs.

**Do not read `STATE.md`, `docs/decisions/` or `docs/backlog.md`.** **LIST every file you read beyond those in steps 1–3.** It is how the Architect detects inputs you were not meant to have, and inputs that were needed but missing.

## G2 — Per question, a pick

For **Q1**, as framed in the context pack, produce:

- (a) a **PICK** — one of the listed options (if the right answer is outside the list, say so and name it);
- (b) **WHY**, with evidence — a quote or a `file:line` from what you read; a claim you cannot evidence is labelled `opinion`;
- (c) **one option the list misses** — or the explicit statement that you find none, with one sentence on what you checked;
- (d) the **riskiest unverified premise** — what, if false, would make the framing itself wrong.

For **Q2**, one row per named edge: what should happen under your pick, and the `file:line` that shows the edge's behaviour today. Add any edge the pack misses.

## G3 — Whole-design check

Answer the pack's closing section, "What would make the whole approach wrong". Evidence, or labelled `opinion`.

## G4 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-274 --status`; the Architect copies it unedited to `docs/worklogs/SG-274_report.md`). **Keep the whole report under 200 lines: the engine keeps only 200 lines of a read-only run's report, and anything past that is lost.** Put the picks first. Required shape:

- `SG-274` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- Q1 with (a)–(d), Q2's table;
- the whole-design check (G3);
- a short closing statement of what you read and deliberately did not use.

Do not restate the context pack; your value is the pick, the evidence, the missed option and the premise.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network; no database.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the lane's `RUN_BUDGET_S`.
- Decisions the pack lists as already taken are not reopened; an objection to one is labelled as such and reported under G3.
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live clock at execution (`PG-IC-07`).

## Acceptance criteria

- A pick for Q1 with (a)–(d) complete, and every Q2 edge answered; each "why" carries at least one evidence item or is self-labelled `opinion`.
- The extra-files list is present and complete for your run.
- The report is under 200 lines.
- `PB-3` vacuity: a pick that merely restates an option label without independent reasoning does not satisfy G2; "missed option: none" without the one sentence of what you checked does not satisfy G2(c).

## Report

Destination: final message (engine-published; the Architect copies it unedited to `docs/worklogs/SG-274_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote nothing.
