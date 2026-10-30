# SG-264 — Second opinion Phase A (blind): the three SG-258 fixes

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

The SG-258 audit (93) left three live-code findings: the review workspace's date form shows the default `needs_evidence` and an empty date because the caller passes no active assertion/category; a move to Non-perishable clears the date but leaves its open `expiry.manual_entry` task; and after a clear the form says `accepted` with no date. The next stage (SG-262 fix + SG-263 rider) is proposed. Because it is a new stage and its rider touches the live host, the project's second-opinion rule (T1/T3; the live host) requires this blind pass before the D7 decision.

This is **Phase A — the blind phase.** You pick independently from the context pack, before the Architect's own pick exists anywhere you can read.

## G1 — Blind read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section (project identity and configuration);
2. the context pack `docs/reviews/2026-10-30-three-fixes-context.md`;
3. every file the context pack names in its "Where it lives" table.

**LIST every file you read beyond those.** Do not treat this list as optional: it is how the Architect detects inputs you were not meant to have, and inputs that were needed but missing.

## G2 — Per decision, a pick

For **D-E**, **D-F**, **D-G** and **D-H**, as framed in the context pack, produce:

- (a) a **PICK** — one of the listed options (if you believe the right answer is outside the list, say so explicitly and name it);
- (b) **WHY**, with evidence — a quote or a `file:line` from what you read; a claim you cannot evidence is labelled `opinion`;
- (c) **one option the context pack's list misses** — or the explicit statement that you find none, with one sentence on what you checked;
- (d) the **riskiest unverified premise** in the decision as framed — what, if false, would make the framing itself wrong.

## G3 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-264 --status`; the Architect copies it unedited to `docs/worklogs/SG-264_report.md`). Required shape:

- `SG-264` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- one section per decision with (a)–(d);
- a short closing statement of what you read and deliberately did not use.

Do not restate the context pack at length — your value is the pick, the evidence, the missed option and the premise.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the lane's `RUN_BUDGET_S`.
- Simplicity: the context pack is the input; go beyond it only into the named files (and declare every extra file read).
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live clock at execution (`PG-IC-07`).

## Acceptance criteria

- One pick present per decision with (a)–(d) complete; each "why" carries at least one evidence item (quote or `file:line`) or is self-labelled `opinion`.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: a pick that merely restates a context-pack option label without independent reasoning does not satisfy G2; "missed option: none" without the one sentence of what you checked does not satisfy G2(c).

## Report

Destination: final message (engine-published; the Architect copies it unedited to `docs/worklogs/SG-264_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote nothing.
