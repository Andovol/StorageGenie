# SG-201 — Second opinion Phase B (critique): the strongest case against the Architect's picks on D-5 / D-6 / D-7

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: automation.**
**DATABASE: none.**
**Restart: none.**

## Why this exists
Phase B of the mandatory second-opinion review (`SECOND_OPINION.md`, contract 0.50.0; `D451`) — one review, never a debate. Phase A (blind) is already committed at `docs/worklogs/SG-200_report.md`. This phase sees the Architect's picks and must argue the strongest case against each, with evidence, so the owner sees the disagreement rather than a smoothed recommendation.

## The Architect's picks (verbatim)
- **D-5:** "A — serve the unserved SG-196+SG-198 frontend delta now."
- **D-6:** "P1 — build the density proposal (renders + real options); proposal step only — no density system implemented before the owner picks an option."
- **D-7:** "`default` — let the rule resolve the reviewer value at dispatch (today: `muse-spark-1.3-contributor xhigh`)."

## G1 — Reads
Read: the repository root `AGENTS.md` top section; the context pack `docs/reviews/2026-10-17-second-opinion-d5-d6-d7-context.md`; Phase A's report `docs/worklogs/SG-200_report.md`; and every file either names. The host contract copy at `/home/andrei/storagegenie-contract/` (e.g. `SECOND_OPINION.md`, `PRODUCTION.md`) may be read read-only where you need a rule's own text — it is outside the repository, and reading it is permitted for this slice only. **LIST every file you read beyond those.**

## G2 — Per decision, the case against
For each of D-5, D-6, D-7, produce:
- (a) the **STRONGEST CASE AGAINST** the Architect's pick — with evidence: a file:line, a quote, or a measurement; an objection you cannot evidence is labelled `opinion`;
- (b) a **premise of the Architect's pick you believe is UNVERIFIED** — name what would verify or falsify it;
- (c) the **OBSERVATION that would settle** any remaining disagreement between your Phase A pick and the Architect's pick.

## G3 — Report
Your final message IS the report (engine-published; read back with `SG-201 --status`; the Architect commits it unedited). Shape: `SG-201` as the first token; the contract-version line (`PB-4`); the extra-files list (G1); one section per decision with (a)–(c); a closing line on what you read and deliberately did not use.

## Constraints
- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces it; a denial anywhere is a STOP (`PB-2`).
- Reads: repository files at BASE plus the named host contract copy (read-only); no other host change; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; finish well inside the lane's `RUN_BUDGET_S`.
- Do not re-argue options that are not the Architect's pick — (a) is about the pick as stated.

## Acceptance criteria
- Three cases-against present, each with (a)–(c) complete; each (a) carries at least one evidence item or is self-labelled `opinion`.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: an (a) that merely restates the context pack's option text, or a (c) that names no observation, does not satisfy G2.

## Report
Destination: final message (engine-published; Architect copies it unedited to `docs/worklogs/SG-201_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else; state that you wrote nothing.
