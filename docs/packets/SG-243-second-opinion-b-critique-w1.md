# SG-243 — Second opinion Phase B (critique): attack the Architect's pick on W1, the two host test libraries

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A (`SG-242`, blind) has reported. Its report is committed, **unedited**, at `docs/worklogs/SG-242_report.md`.
Phase A picked **A**. The Architect's own pick differs — it is **D**, the option Phase A named but declined.
This phase exists to attack the Architect's pick with evidence, not to agree with either side.

## The Architect's pick — carried VERBATIM

> **D — keep the image route as the home for those two tests and make the host's suite state them as loud, presence-gated skips.** No host privilege change (B is out: D-1024-6's fallback trigger is unmet — the image route is green — and B needs a unit-property change plus a scoped sudoers rule on the live serving host). No whole-suite move into the image (A's trial): the other 740 host tests need no native library, so moving them changes the team's whole test loop for two tests, and the loop's duration inside `--network none` is unmeasured. Instead, `backend/tests/test_signals.py` gains a presence guard — the guard must check the `tesseract` **binary** (`shutil.which`), not just the `pytesseract` module, which imports fine on the host while the binary is missing, and `libzbar`'s loadability, since `pyzbar` imports but fails on the missing shared library (`backend/app/services/signals.py:102-109`, `:207-214`) — so a missing library yields a skip naming the reason and the exact command that proves the test in the image (`make backend-test-image`), not a silent pass. `make backend-test-image` stays the executing prover, and a slice that touches the signals code must run it and say so.

The Architect's own note on why it differs, and the one weakness it already sees in its own pick, are in
`docs/worklogs/SG-242_architect.md` (read it — it is an input, and it is the Architect's reasoning, not
evidence).

## What Phase A found (read the report itself; this is a pointer, not a substitute)

`docs/worklogs/SG-242_report.md` — pick **A** (image route as the home, whole-suite extension gated by one
measured trial); its **missed option D**; its riskiest unverified premise: *that the full backend suite runs
and passes inside the image under `--network none`* — "if that premise is false, option A as written is
unexecutable and the framing itself collapses".

## G1 — Read

1. `AGENTS.md` — the top section (project identity and configuration);
2. the context pack `docs/reviews/2026-10-24-second-opinion-w1-host-test-libraries-context.md`;
3. the Phase A report `docs/worklogs/SG-242_report.md`;
4. the Architect's record `docs/worklogs/SG-242_architect.md`;
5. every file the context pack names in its "Where it lives" table;
6. the code the Architect's pick cites: `backend/app/services/signals.py` (the two import blocks around
   `:102-109` and `:207-214`), `backend/tests/test_signals.py:117-149`, `Makefile:11-12`.

**LIST every file you read beyond those.** Not optional: it is how the Architect detects inputs you were not
meant to have.

## G2 — The critique

Against the Architect's pick **D**, produce:

- **(a) THE STRONGEST CASE AGAINST IT, with evidence** — a quote or a `file:line` or a measurement. A claim
  you cannot evidence is labelled `opinion`. The strongest case is already partly on the table: Phase A
  refused D because it "relabels rather than removes the per-slice proof tax (the image run is still
  required)". Say whether that objection holds against D as the Architect wrote it, and find the strongest
  objection the Architect did **not** raise.
- **(b) THE STRONGEST CASE FOR D**, with the same evidence standard — the Architect's pick deserves a fair
  hearing too, and the owner will see both.
- **(c) A PREMISE OF THE ARCHITECT'S PICK THAT IS UNVERIFIED** — say what would be true if it were false.
  The Architect names two candidates (the guard's exact form; the image target's staleness), but you are not
  bound by that list.
- **(d) THE OBSERVATION THAT WOULD SETTLE ANY DISAGREEMENT** — the single measurement or read that decides
  D versus A. Name what it is, where it would run, and what result would mean which pick.

**Also required:** state whether Phase A's pick **A** survives this critique, and what the owner should be
told. If you believe the Architect's pick and Phase A's pick are both wrong, say so and name the option
that beats them — including any option neither of them listed.

## G3 — Report

Your final message **is** the report (the engine publishes it; read it back with `SG-243 --status`; the
Architect copies it unedited to `docs/worklogs/SG-243_report.md`). Required shape:

- `SG-243` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- the four answers (a)–(d) for **D**;
- your judgement on **A**, and the line the owner should get;
- a short closing statement of what you read and deliberately did not use.

Do not restate the context pack, Phase A's report, or the Architect's record at length — your value is the
evidence against and for, the unverified premise, and the settling observation.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial
  anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
  (No live re-measurement: if the settling observation needs a run, **name** it — do not perform it.)
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the
  lane's `RUN_BUDGET_S`.
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live
  clock at execution (`PG-IC-07`).
- **Do not simply choose between A and D because one of them is the Architect's.** If the honest answer is
  "neither, and here is what beats both", that is the most useful report this phase can produce.

## Acceptance criteria

- (a)–(d) present for D, with at least one evidence item (quote or `file:line` or measurement) in (a) and
  (b), or an explicit `opinion` label; (c) names a premise with what-would-be-true-if-false; (d) names one
  concrete observation and its decision rule.
- The extra-files list is present and complete for your run.
- A judgement on A and the line the owner should get.
- `PB-3` vacuity: an objection without evidence, labelled `opinion`, does not satisfy (a); "both picks are
  fine" does not satisfy the phase — the phase's whole purpose is a disagreement with evidence.

## Report

Destination: final message (engine-published; the Architect copies it unedited to
`docs/worklogs/SG-243_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You
publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote
nothing.
