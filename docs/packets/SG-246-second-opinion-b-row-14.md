# SG-246 — Second opinion Phase B (critique): attack the Architect's four picks on roadmap row 14

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**
**No provider call, no metered probe, no model download, no key handling** — name what a probe would cost and prove; do not run it.

## Why this exists

Phase A (`SG-245`, blind) has reported. Its report is committed, **unedited**, at `docs/worklogs/SG-245_report.md`.
This phase attacks the **Architect's** picks — which differ from Phase A's in two places (the fallback direction
and the local-landing constraints) and add a concrete first-probe ceiling — with evidence.

## The Architect's picks — carried VERBATIM

**D-R14-a — which second cloud provider. OpenRouter as the second cloud provider, with the model id carried in
configuration; the key's provisioning is a separate owner item.** The pick follows the *shape*, not the price:
the existing reader is one OpenAI-shaped POST (`providers/opencode_go.py:32-33`, `:258-263`), OpenRouter speaks
the same shape, and the repo already carries an OpenRouter client and a key slot (`.env.example:5`,
`config.py:44`, `services/scene/openrouter.py`). The pick is also about the **fallback direction**:
`opencode-go` stays the primary and OpenRouter becomes the fallback — real vendor independence, because a
second *model* on the same gateway would not survive the vendor being down and is therefore not a provider
fallback at all. "Changing providers needs configuration, not code" (blueprint `:533-539`) then means: a
stable seam plus a per-vendor adapter plus a configurable model id — **not zero code per vendor** (the tree
already branches per model family, `opencode_go.py:63-67`). Key provisioning, cap values and probe spend are
**not** part of this pick.

**D-R14-b — what "the local option" means. L1 now, with L3 as the routing destination; L2 (a local model
served on the live host) stays closed.** "Local" = the deterministic no-provider path already in the tree (the
`fake` registry entry `reader.py:96` and `ScriptedProvider` `fake.py:82-130`, plus the local OCR and barcode
observations `signals.py:102-109`, `:205-245`), used as the offline/fallback landing; no always-on runtime, no
host change. Two hard constraints on that landing, which the reviewer's premise (d) forces: **a local landing
must never be presented as a reading** — `fake` fabricates `items: [{"name": "fake-item", …}]`
(`fake.py:63`), so a fallback that lands there must produce **no candidate proposal**, or an explicitly
labelled "no provider" outcome, never a fabricated item (the app's rule: never guessed); and **local must be
the destination only for transport/outage classes, never for `invalid_json`** — that class is in
`RETRYABLE_ERRORS` (`reader.py:61-63`) and stands for a prompt or schema bug, which must surface rather than be
absorbed by a fixture. L2 is **deferred, not rejected**: it needs the owner to change a host rule (VPS.md F4),
a stated memory budget, and a re-measure of the shared host (7.7 GiB, measured 2026-09-17).

**D-R14-c — the caps and the money authority. Set explicit caps before any metered call; grant no standing
money authority; every metered probe is separately authorised with a hard ceiling.** No probe in the review
lane. The caps exist and bind nothing today (`config.py:48-49`, both `None`), and the machinery already refuses
a pre-call estimate over budget (`router.py:71-74`) and checks the monthly ceiling from the durable ledger
(`reader.py:486-497`); consent already defaults to deny (`config.py:50`). The magnitudes are the owner's,
informed by the estimate arithmetic — and the estimate is a deliberate **upper bound**
(`opencode_go.py:151-164`), not a forecast, and it is **per adapter**: the new reader needs its own rate table
before any cap can bind on it (`_estimate_call → 0.0` for a provider with no estimator, `reader.py:233-242`).
The first probe's ceiling I propose as **$0.50 for one image, one model, one call** — a ceiling, not a
forecast; the measured cost is expected far below it, and the probe's job is to measure it against the
estimate. Two things the probe must prove before anyone says the caps held: the **measured cost against the
estimate**, and the **ledger row** for that probe (the monthly check joins through `Job`,
`reader.py:270-284`, and writers with `job_id=None` already under-count).

**D-R14-d — the stage shape. Four ordered slices, $0 first, spend last.** (1) **Fallback plumbing with test
doubles only** — the mechanism made reachable (`fallback_id` is hardcoded `None` at
`providers/reader.py:465`, `services/chat/service.py:425`, `services/planning/service.py:444`,
`services/analytics/service.py:597`) with **no production fallback configured**, so nothing can fabricate a
reading; exit: the fallback path is exercised in the production code path by a double, $0. (2) **The second
cloud adapter** (OpenRouter) with its own rate table, `estimate_call_cost`, registry entry, key seam, and the
**deliberate** update of the two privacy pins (`backend/tests/test_privacy_audit.py:237-248` the send-site
set, `:251-267` the `redact_image` sites); exit: the provider is switchable by configuration, $0. (3) **Caps
calibration plus one authorised metered probe** — exit: measured cost against the estimate, ledger rows read
back. (4) **Local as the fallback destination** (L1/L3) — exit: the blueprint's test demonstrated across
provider, fallback, local fallback and budgets (`:318`, `:533-539`). The stage's exit condition is read as **a
stable seam with per-vendor adapters** (the tree already branches per model family, `opencode_go.py:63-67`),
not "zero code per vendor".

**Structural position: the four decisions are split, not one package** — agreed with Phase A. The vendor and
the slice order can ride together; the local-host branch (L2) and the money authority stay separate items and
never ride inside a vendor-and-caps bundle.

## What Phase A found (read the report itself; this is a pointer, not a substitute)

`docs/worklogs/SG-245_report.md` — its four picks, its missed options, its four riskiest unverified premises,
and its structural judgement that the four decisions **must be split**, not handed over as one package.

## G1 — Read

1. `AGENTS.md` — the top section (project identity and configuration) and its "Project rules" section;
2. the context pack `docs/reviews/2026-10-24-row-14-photo-ai-second-opinion-context.md`;
3. the Phase A report `docs/worklogs/SG-245_report.md`;
4. the Architect's record `docs/worklogs/SG-245_architect.md`;
5. every file the context pack names in its tables.

**LIST every file you read beyond those.** Not optional: it is how the Architect detects inputs you were not
meant to have.

## G2 — The critique

Against the Architect's four picks, produce:

- **(a) THE STRONGEST CASE AGAINST EACH PICK, with evidence** — a quote or a `file:line` or a measurement. A
  claim you cannot evidence is labelled `opinion`. For each pick, name the strongest objection **the Architect
  did not raise** — Phase A's objections are already on the table.
- **(b) THE STRONGEST CASE FOR EACH PICK**, with the same evidence standard.
- **(c) A PREMISE OF EACH PICK THAT IS UNVERIFIED** — say what would be true if it were false. The Architect's
  own residual uncertainty is one of them (whether the owner meant genuine offline photo understanding); you
  are not bound by that list.
- **(d) THE OBSERVATION THAT WOULD SETTLE EACH DISAGREEMENT** — the single measurement or read that decides.
  Name what it is, where it would run, and what result would mean which pick. **Do not perform it.**

**Also required:** judge the **split** itself — is separating the four decisions (and the a→d→c→b-host
sequence) right, or does it fragment a decision the owner should take once? And state what the owner should be
told, in one line per decision, if the picks stand.

## G3 — Report

Your final message **is** the report (the engine publishes it; read it back with `SG-246 --status`; the
Architect copies it unedited to `docs/worklogs/SG-246_report.md`). Required shape:

- `SG-246` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- the answers (a)–(d) for each of the four decisions;
- your judgement on the split, and the owner lines;
- a short closing statement of what you read and deliberately did not use.

Do not restate the context pack, Phase A's report, or the Architect's record at length — your value is the
evidence against and for, the unverified premises, and the settling observations.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial
  anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the
  lane's `RUN_BUDGET_S`.
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live
  clock at execution (`PG-IC-07`).
- **Do not simply choose between the Architect's picks and Phase A's.** If the honest answer is "none of them,
  and here is what beats all of them", that is the most useful report this phase can produce.

## Acceptance criteria

- (a)–(d) present for each of the four decisions, with at least one evidence item (quote or `file:line` or
  measurement) in (a) and (b), or an explicit `opinion` label; (c) names a premise with what-would-be-true-if-
  false; (d) names one concrete observation and its decision rule.
- The extra-files list is present and complete for your run.
- A judgement on the split, and the owner lines.
- `PB-3` vacuity: an objection without evidence, labelled `opinion`, does not satisfy (a); "the picks are fine"
  does not satisfy the phase — the phase's whole purpose is a disagreement with evidence.

## Report

Destination: final message (engine-published; the Architect copies it unedited to
`docs/worklogs/SG-246_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You
publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote
nothing.
