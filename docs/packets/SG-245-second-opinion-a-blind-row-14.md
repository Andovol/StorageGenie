# SG-245 — Second opinion Phase A (blind): an independent pick on roadmap row 14, the second photo reader, the local option, the caps

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

`SECOND_OPINION.md` (contract 0.52.0; `D451`) requires a two-phase second-opinion review **before the owner is
brought any 🟠 or 🔴 decision item**, and this project's own rule widens the trigger: every 🟠/🴠 item, plus
any 🟡 item whose subject is the live host, the dispatch key, the app database, or the owner's own data.

The open decision set is **roadmap row 14** — *"Second AI provider and local option with fallback and
spending limits"* — which the owner made the standing priority on 2026-10-24 (D-1024-12): *"I want to
prioritize the remaining missing photo AI features going forward."* Four decisions ride on it: which second
provider, what "the local option" means, the spending caps and the money authority for a metered probe, and
the stage shape. Two of them are 🟠 (a local runtime on the live serving host; money authority for a metered
call), so the review runs **before** the owner sees them.

This is **Phase A — the blind phase.** You pick independently from the context pack, before the Architect's
own pick exists anywhere you can read. A different model reviews because self-critique shares blind spots.

**Standing lane condition** (`docs/reviews/review-ledger.md`): a host session launched with `agent=plan`
cannot read outside the repository — every file you need is inside it and named below. If you need a rule's
own text, it is quoted in the context pack.

## G1 — Blind read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section (project identity and configuration) and its
   "Project rules" section;
2. the context pack `docs/reviews/2026-10-24-row-14-photo-ai-second-opinion-context.md`;
3. every file the context pack names in its tables.

**LIST every file you read beyond those.** Do not treat this list as optional: it is how the Architect detects
inputs you were not meant to have, and inputs that were needed but missing.

## G2 — Per decision, a pick

For each of the four decisions **D-R14-a, D-R14-b, D-R14-c, D-R14-d**, as framed in the context pack, produce:

- (a) a **PICK** — one of the options the pack lists (if you believe the right answer is outside the list, say
  so explicitly and name it);
- (b) **WHY**, with evidence — a quote or a `file:line` from what you read; a claim you cannot evidence is
  labelled `opinion`;
- (c) **one option the context pack's list misses** for that decision — or the explicit statement that you
  find none, with one sentence on what you checked;
- (d) the **riskiest unverified premise** in that decision as framed — what, if false, would make the framing
  itself wrong.

If one decision's answer follows from another's, say so and keep the answers separate anyway.

## G3 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-245 --status`; the
Architect copies it unedited to `docs/worklogs/SG-245_report.md`). Required shape:

- `SG-245` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- one section per decision (**D-R14-a** … **D-R14-d**) with (a)–(d);
- a short closing statement of what you read and deliberately did not use, and **whether the four decisions
  can be taken as one package or must be split** (the owner should not be handed four answers that contradict
  each other).

Do not restate the context pack at length — your value is the picks, the evidence, the missed options and the
premises, not a summary.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial
  anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
  **No provider call, no metered probe, no model download** — name what a probe would cost and what it would
  prove; do not run it.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the
  lane's `RUN_BUDGET_S`.
- Simplicity: the context pack is the input; go beyond it only into the named files (and declare every extra
  file read).
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live
  clock at execution (`PG-IC-07`).

## Acceptance criteria

- Four picks present, each with (a)–(d) complete; every "why" carries at least one evidence item (quote or
  `file:line`) or is self-labelled `opinion`.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: a pick that merely restates a context-pack option label without independent reasoning does
  not satisfy G2; "missed option: none" without the one sentence of what you checked does not satisfy G2(c).
- The one-package-or-split judgement is present.

## Report

Destination: final message (engine-published; the Architect copies it unedited to
`docs/worklogs/SG-245_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You
publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote
nothing.
