# SG-200 — Second opinion Phase A (blind): independent picks for three open decisions (D-5 serve timing, D-6 density scope, D-7 reviewer mode)

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: automation.**
**DATABASE: none.**
**Restart: none.**

## Why this exists
`SECOND_OPINION.md` (contract 0.50.0; `D451`) requires a two-phase second-opinion review before the owner is brought any 🟡/🟠/🔴 decision item. Three such items are open (D-5, D-6, D-7). This is Phase A — the blind phase: you pick independently from the context pack, before the Architect's own picks are written into anything you are given to read. A different model reviews because self-critique shares blind spots; at the Launcher desk, 8 of 11 reviews changed a recommendation.

## G1 — Blind read
Read, in this order:
1. the repository root file `AGENTS.md` — its top section (project identity/configuration);
2. the context pack `docs/reviews/2026-10-17-second-opinion-d5-d6-d7-context.md`;
3. every file it names.

**LIST every file you read beyond those.** Do not treat this list as optional: it is how the Architect detects inputs you were not meant to have (and inputs you needed but lacked).

## G2 — Per decision, a pick
For each of D-5, D-6, D-7 as framed in the context pack, produce:
- (a) a **PICK** — one of the listed options (if you believe the right answer is outside the list, say so explicitly and name it);
- (b) **WHY**, with evidence — a quote or a file:line from what you read; a claim you cannot evidence is labelled `opinion`;
- (c) **one option the context pack's list misses** — or the explicit statement that you find none, with one sentence on what you checked;
- (d) the **riskiest unverified premise** in the decision as framed — what, if false, would make the framing itself wrong.

## G3 — Report
Your final message IS the report (the engine publishes it; it is read back with `SG-200 --status`; the Architect commits it unedited). Required shape:
- `SG-200` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- one section per decision with (a)–(d);
- a short closing statement of what you read and deliberately did not use.

Do not restate the context pack at length — your value is the picks, the evidence, the missed options and the premises, not summary.

## Constraints
- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the lane's `RUN_BUDGET_S`.
- Simplicity: the context pack is the input; go beyond it only into the named files (and declare every extra file read).

## Acceptance criteria
- Three picks present, each with (a)–(d) complete; each "why" carries at least one evidence item (quote or file:line) or is self-labelled `opinion`.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: a pick that merely restates a context-pack option label without independent reasoning does not satisfy G2; "missed option: none" without the one sentence of what you checked does not satisfy G2(c).

## Report
Destination: final message (engine-published; Architect copies it unedited to `docs/worklogs/SG-200_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote nothing.
