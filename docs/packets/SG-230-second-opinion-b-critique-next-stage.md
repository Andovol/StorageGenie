# SG-230 — Second opinion Phase B (critique): the strongest case against the Architect's pick on N-1

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: automation.**
**DATABASE: none.**
**Restart: none.**

## Why this exists
Phase B of the mandatory second-opinion review (`SECOND_OPINION.md`, contract 0.50.0; `D451`) — one review, never a debate. Phase A (blind) is already committed at `docs/worklogs/SG-229_report.md`. This phase sees the Architect's pick and must argue the strongest case against it, with evidence, so the owner sees the disagreement rather than a smoothed recommendation.

## The Architect's pick (verbatim)
- **N-1:** "A — render-review + reject pass, with the acceptance-standard question put first: the owner states the bar (primary-label-exact is enough vs any garbled printed text rejects) before giving per-render verdicts; each rejection becomes its own SG-223-shaped unlink slice; if all four are accepted, the stage terminates in the (D) end state (close light, no deploy/release owed)."

## G1 — Reads
Read: the repository root `AGENTS.md` top section; the context pack `docs/reviews/2026-10-23-second-opinion-next-stage-context.md`; Phase A's report `docs/worklogs/SG-229_report.md`; and every file either names. All of them live inside the repository — a host session launched with `agent=plan` cannot read outside it (standing condition, `docs/reviews/review-ledger.md:11`), so confine all reads to the repo. **LIST every file you read beyond those.**

## G2 — The case against
For N-1, produce:
- (a) the **STRONGEST CASE AGAINST** the Architect's pick — with evidence: a file:line, a quote, or a measurement; an objection you cannot evidence is labelled `opinion`;
- (b) a **premise of the Architect's pick you believe is UNVERIFIED** — name what would verify or falsify it;
- (c) the **OBSERVATION that would settle** any remaining disagreement between your Phase A pick and the Architect's pick.

## G3 — Report
Your final message IS the report (read back with `SG-230 --status`; the Architect commits it unedited). Shape: `SG-230` as the first token; the contract-version line (`PB-4`); the extra-files list (G1); one section with (a)–(c); a closing line on what you read and deliberately did not use.

## Constraints
- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces it; a denial anywhere is a STOP (`PB-2`).
- Reads: repository files at BASE only; no host change; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; finish well inside the lane's `RUN_BUDGET_S`.
- Do not re-argue options that are not the Architect's pick — (a) is about the pick as stated.

## Acceptance criteria
- One case-against present with (a)–(c) complete; (a) carries at least one evidence item or is self-labelled `opinion`.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: an (a) that merely restates the context-pack option text, or a (c) that names no observation, does not satisfy G2.

## Report
Destination: final message (engine-published; Architect copies it unedited to `docs/worklogs/SG-230_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else; state that you wrote nothing.
