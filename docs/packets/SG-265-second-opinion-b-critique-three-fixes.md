# SG-265 — Second opinion Phase B (critique): the three SG-258 fixes

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A (SG-264) picked **E1 / F1 / G1 / H1** — the same as the Architect's pick. This is **Phase B**: the strongest case against each pick, with evidence, an unverified premise, and the observation that would settle any disagreement. The report is advisory; the owner's D7 follows.

## G1 — Read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section;
2. the context pack `docs/reviews/2026-10-30-three-fixes-context.md`;
3. the Phase A report `docs/worklogs/SG-264_report.md`;
4. every file the context pack names in its "Where it lives" table.

**LIST every file you read beyond those.**

## G2 — Per decision, the strongest case against the pick

For **D-E**, **D-F**, **D-G** and **D-H**, with the Architect's pick **E1 / F1 / G1 / H1**:

- (a) the **strongest case AGAINST the pick**, with evidence — a `file:line`, a quote, or a measurement; an objection without evidence is labelled `opinion`;
- (b) **a premise of the pick that is unverified**;
- (c) the **observation that would settle any disagreement** — what to read, run or measure.

Do not restate the case for the pick; your value is the attack, the unverified premise and the settling observation.

## G3 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-265 --status`; the Architect copies it unedited to `docs/worklogs/SG-265_report.md`). Required shape:

- `SG-265` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- one section per decision with (a)–(c);
- a short closing statement of what you read and deliberately did not use.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the lane's `RUN_BUDGET_S`.
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live clock at execution (`PG-IC-07`).

## Acceptance criteria

- One section per decision with (a)–(c) complete; each objection carries evidence or is self-labelled `opinion`.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: a section that restates the pick's rationale does not satisfy G2; an objection without evidence must say `opinion`.

## Report

Destination: final message (engine-published; the Architect copies it unedited to `docs/worklogs/SG-265_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote nothing.
