# SG-248 — Second opinion round 2, Phase A (blind): an independent pick on the four row-14 decisions as they now stand

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**
**Provider: none.** No provider call, no model download, no key read, no spend. Target: **$0**.

## Why this exists

The owner asked for a second opinion on **all** of the row-14 decisions, and then to be brought the decisions.
Roadmap row 14 ("Second AI provider and local option with fallback and spending limits") carries four owner
decisions. One of them has since been **decided by the owner** (no local models on the server — recorded as
D-1024-15 and quoted in the context pack); the other three are open, and the first review round left each of
them with conditions and amendments rather than with a settled answer.

This is **Phase A — the blind phase.** You pick independently. The Architect's own pick does not exist anywhere
you can read; neither does any prior review's pick. A different model reviews because self-critique shares
blind spots.

**Standing lane condition** (`docs/reviews/review-ledger.md`): a host session launched with `agent=plan`
cannot read outside the repository — every file you need is inside it and named below. If you need a rule's
own text, it is quoted in the context pack.

## G1 — Blind read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section (project identity and configuration) and its
   "Project rules" section;
2. the context pack `docs/reviews/2026-10-24-row-14-round-2-context.md`;
3. every file the context pack names in its tables.

**LIST every file you read beyond those.** Do not treat this list as optional: it is how the Architect detects
inputs you were not meant to have, and inputs that were needed but missing.

**Do not read** the earlier review's reports (`docs/worklogs/SG-245_report.md`, `SG-246_report.md`) or the
Architect's records (`SG-245_architect.md`, `SG-246_architect.md`). They are in the repository, they exist, and
reading them would replace an independent pick with a copy of one. The context pack states the **facts** they
surfaced; every one of those facts is verifiable in the code, and you are expected to verify them.

## G2 — Per decision, a pick

For each of the four decisions **D-R14-a, D-R14-b, D-R14-c, D-R14-d**, as framed in the context pack, produce:

- (a) a **PICK** — one of the options the pack lists (if you believe the right answer is outside the list, say
  so explicitly and name it);
- (b) **WHY**, with evidence — a quote or a `file:line` from what you read; a claim you cannot evidence is
  labelled `opinion`;
- (c) **one option the context pack's list misses** for that decision — or the explicit statement that you find
  none, with one sentence on what you checked;
- (d) the **riskiest unverified premise** in that decision as framed — what, if false, would make the framing
  itself wrong.

**D-R14-b is already decided by the owner** (no local models on the server — the pack quotes it). Do **not**
re-open it and do not treat it as an open choice: pick the **consequent** shape of the local option inside the
owner's ruling (what "local" can mean now, and what the routing must do), and report if you think the ruling
leaves a real gap that the Architect must name to the owner.

## G3 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-248 --status`; the
Architect copies it unedited to `docs/worklogs/SG-248_report.md`). Required shape:

- `SG-248` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- one section per decision (**D-R14-a** … **D-R14-d**) with (a)–(d);
- a short closing statement of what you read and deliberately did not use, and **whether the four decisions can
  be taken as one package or must be split** (the owner should not be handed four answers that contradict each
  other).

Do not restate the context pack at length — your value is the picks, the evidence, the missed options and the
premises, not a summary.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial
  anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- **No provider call, no metered probe, no model download.** If a decision needs a measurement, **name** it with
  its cost and its proof; do not run it.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the
  lane's `RUN_BUDGET_S`.
- Simplicity: the context pack is the input; go beyond it only into the named files (and declare every extra
  file read).
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live
  clock at execution (`PG-IC-07`).

## Acceptance criteria

- Four picks present, each with (a)–(d) complete; every "why" carries at least one evidence item (quote or
  `file:line`) or is self-labelled `opinion`.
- D-R14-b's answer stays inside the owner's ruling and names any gap the ruling leaves.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: a pick that merely restates a context-pack option label without independent reasoning does
  not satisfy G2; "missed option: none" without the one sentence of what you checked does not satisfy G2(c).
- The one-package-or-split judgement is present.

## Report

Destination: final message (engine-published; the Architect copies it unedited to
`docs/worklogs/SG-248_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You
publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote
nothing.
