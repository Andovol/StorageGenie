# SG-277 — Second opinion Phase A (blind): the live candidate state constraint

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

A schema change on the app database may be needed. It goes through a two-phase second opinion before the owner sees it (`AGENTS.md`). This is **Phase A — the blind phase.** You pick independently from the context pack.

## G1 — Blind read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section (project identity and configuration);
2. the context pack `docs/reviews/2026-11-02-candidate-state-constraint-context.md`;
3. every file the context pack names in its "Where it lives" table, as far as each question needs.

**Do not read `STATE.md`, `docs/decisions/` or `docs/worklogs/SG-276_audit.md`.** **LIST every file you read beyond those in steps 1–3.**

## G2 — Per question, a pick

For **Q1**, **Q2** and **Q3**, as framed in the context pack, produce:

- (a) a **PICK** — one of the listed options where the question lists them (if the right answer is outside the list, say so and name it);
- (b) **WHY**, with evidence — a quote or a `file:line`; a claim you cannot evidence is labelled `opinion`;
- (c) **one option the list misses** — or the explicit statement that you find none, with one sentence on what you checked;
- (d) the **riskiest unverified premise**.

## G3 — Whole-approach check

Answer the pack's closing section, "What would make the whole approach wrong". Evidence, or labelled `opinion`.

## G4 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-277 --status`; the Architect copies it unedited to `docs/worklogs/SG-277_report.md`). **Keep the whole report under 200 lines: the engine keeps only 200 lines of a read-only run's report.** Put the picks first. Required shape: `SG-277` as the first token; the contract-version line (`PB-4`); the extra-files list; each question with (a)–(d); G3; a short closing statement of what you read and deliberately did not use.

## Constraints

- Read-only: no write of any kind, no commit, no push; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network; no database.
- Hang bound: ordinary file reads 120 s each; no interactive prompt.
- Decisions the pack lists as already taken are not reopened; an objection is labelled as such and reported under G3.

## Acceptance criteria

- A pick for each question with (a)–(d) complete; each "why" carries evidence or is labelled `opinion`.
- The extra-files list is complete. The report is under 200 lines.
- `PB-3` vacuity: a pick that merely restates an option label does not satisfy G2; "missed option: none" without the sentence on what you checked does not satisfy G2(c).

## Report

Destination: final message (engine-published; the Architect copies it unedited to `docs/worklogs/SG-277_report.md`). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.
