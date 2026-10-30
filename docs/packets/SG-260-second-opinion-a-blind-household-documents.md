# SG-260 — Second opinion Phase A (blind): the household-and-document implementation choices

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

`SECOND_OPINION.md` (contract 0.56.0; `T3`, `D555`) requires a blind pass before the Architect commits a packet that introduces a design choice no earlier review covered. The owner approved the household-and-document stage on 2026-10-30 (`"d6 - approved"`, D6). The stage's implementation has four choices no earlier review covered: how Documents/other gets a date, how the app lets a user classify an item, how reclassification keeps an existing date, and how the expiry-date form behaves.

This is **Phase A — the blind phase.** You pick independently from the context pack, before the Architect's own pick exists anywhere you can read. A different model reviews because self-critique shares blind spots.

**Standing lane condition** (`docs/reviews/review-ledger.md`): a host session launched with `agent=plan` cannot read outside the repository — every file you need is inside it and named below.

## G1 — Blind read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section (project identity and configuration);
2. the context pack `docs/reviews/2026-10-30-household-documents-context.md`;
3. every file the context pack names in its "Where it lives" table.

**LIST every file you read beyond those.** Do not treat this list as optional: it is how the Architect detects inputs you were not meant to have, and inputs that were needed but missing.

## G2 — Per decision, a pick

For **D-A**, **D-B**, **D-C** and **D-D**, as framed in the context pack, produce:

- (a) a **PICK** — one of the listed options (if you believe the right answer is outside the list, say so explicitly and name it);
- (b) **WHY**, with evidence — a quote or a `file:line` from what you read; a claim you cannot evidence is labelled `opinion`;
- (c) **one option the context pack's list misses** — or the explicit statement that you find none, with one sentence on what you checked;
- (d) the **riskiest unverified premise** in the decision as framed — what, if false, would make the framing itself wrong.

Then one short statement of **what would make the whole approach wrong**.

## G3 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-260 --status`; the Architect copies it unedited to `docs/worklogs/SG-260_report.md`). Required shape:

- `SG-260` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- one section for each of **D-A**, **D-B**, **D-C**, **D-D** with (a)–(d);
- the whole-approach statement;
- a short closing statement of what you read and deliberately did not use.

Do not restate the context pack at length — your value is the picks, the evidence, the missed options and the premises, not a summary.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the lane's `RUN_BUDGET_S`.
- Simplicity: the context pack is the input; go beyond it only into the named files (and declare every extra file read).
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live clock at execution (`PG-IC-07`).

## Acceptance criteria

- One pick per decision with (a)–(d) complete; each "why" carries at least one evidence item (quote or `file:line`) or is self-labelled `opinion`.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: a pick that merely restates a context-pack option label without independent reasoning does not satisfy G2; "missed option: none" without the one sentence of what you checked does not satisfy G2(c).
- The whole-approach statement names a world in which the approach would be wrong, or says none can be named and why.

## Report

Destination: final message (engine-published; the Architect copies it unedited to `docs/worklogs/SG-260_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote nothing.
