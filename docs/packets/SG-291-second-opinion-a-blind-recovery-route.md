# SG-291 — Second opinion Phase A (blind): the recovery image, after commit failed

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. This lane's snapshot has no `.git`: state `unknown` once and carry on.
**DATABASE: none.**
**Restart: none.**

## Why this exists

`docker commit` of the live container failed twice; a new route for the recovery image is needed. This is **Phase A — the blind phase.** You pick independently from the context pack.

## G1 — Blind read

Read, in this order:

1. the repository root file `AGENTS.md`, its top section;
2. the context pack `docs/reviews/2026-11-07-recovery-image-route-context.md`;
3. the files its "Where it lives" table names, as far as each question needs.

**Do not read `STATE.md` or `docs/decisions/`.** They carry the Architect's view. Search with file-targeted reads, never repository-wide greps. **LIST every file you read beyond steps 1–3.**

## G2 — Per question, a pick

For **Q1** to **Q3**, as framed in the pack:

- (a) a **PICK**, one of the listed options, or name the right answer outside the list;
- (b) **WHY**, with evidence: a quote or a `file:line`; a claim you cannot evidence is labelled `opinion`;
- (c) **one option the list misses**, or say you find none, with one sentence on what you checked;
- (d) the **riskiest unverified premise**, and the read-only observation on the host that would settle it.


## G3 — Whole-approach check

Answer the pack's closing section. Evidence, or labelled `opinion`.

## G4 — Report

Your final message **is** the report (read back with `SG-291 --status`; the Architect copies it unedited to `docs/worklogs/SG-291_report.md`). **Keep the whole report under 120 lines: the engine keeps only 200 lines of a read-only run's report.** Picks first. Shape: `SG-291` as the first token; the contract-version line (`PB-4`); the extra-files list; Q1–Q3 with (a)–(d); G3; one closing line of what you read and deliberately did not use.

## Constraints

- Read-only: no write of any kind, no commit, no push; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host commands, Docker, credentials, browser, external network or database.
- Hang bound: file reads 120 s each; no interactive prompt.
- Decisions the pack lists as binding are not reopened; an objection is labelled as such and reported under G3.

## Acceptance criteria

- A pick for each question with (a)–(d); each "why" carries evidence or is labelled `opinion`.
- The extra-files list is complete. The report is under 120 lines.
- `PB-3` vacuity: a pick that merely restates an option label does not satisfy G2; "missed option: none" without the sentence on what you checked does not satisfy G2(c).

## Report

Destination: final message (engine-published). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.
