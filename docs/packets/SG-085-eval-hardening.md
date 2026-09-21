# SG-085 — eval runner outgrows its single-corpus hardwire: manifest selector + frozen baselines (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D107-approved slice 1 of the Phase 5 hardening stage (plan `docs/superpowers/plans/2026-09-21-phase-5-hardening.md` Slice 1). F-SG079-1 carried: `eval/run.py` is hardwired to sg029 (`MANIFEST_PATH = CORPUS_DIR / "sg029" / "manifest.json"` — re-verify on target per `PG-IC-09`, do not inherit my line number). THIS slice adds a manifest selector (sg029 + sg079 required; sg049 decided-and-reported, see G1), records frozen offline baselines for the scored corpora, and guards the refactor with a v1-metrics-identical check — scoring logic itself is untouched. NO live leg, $0, no network. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** eval-selector + baseline records ONLY (enumerated ceiling below). No `--live`, no provider call, no fixture/manifest content edits, no scoring-logic hunks, no migration, no secrets in logs, no deploy, no restart (`PG-PR-04` — nothing becomes live; proof is scoped to the offline runner + suite).
**Money posture:** $0 offline by construction. Prove it by result, not by command exit: zero `provider_call` rows in the sandbox after the offline runs (`PG-EV-02`). No bound to multiply out — there is no metered call (`PG-IC-04` stated as not firing: nothing to bound).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-07` · `PG-EV-09` · `PG-SC-05` · `PG-SC-08` (satisfied in-slice: metrics + baselines recorded together) · `PG-SC-09` · `PG-SC-11` (grep + verdict, see G3) · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NOTHING live stated).

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (temp-SQLite sandbox inside the runner only, nothing persists). Restart: none. Deploy: none.**

## G1 — manifest selector (plumbing only, scoring untouched)

- Re-read `run.py` manifest block + all three corpus manifests before touching (`PG-IC-09`): I hold `MANIFEST_PATH` hardwired to sg029; `corpus/sg029` = 10 fixtures + manifest + images + `generate.py`; `corpus/sg049` = 3 fixtures + manifest; `corpus/sg079` = 6 fixtures + manifest; `corpus/sg026_*.json` = 5 loose files, NO manifest. Reconcile every count against disk and report drift as a finding.
- Add the selector (flag shape yours): names at least `sg029` + `sg079`; unknown name fails LOUDLY with usage (seen-to-fail gate, `PG-EV-01` — feed a bogus name and quote the failure). `sg049` is a design call inside constraints: include or defer with the reason quoted (its manifest exists; the plan requires sg029+sg079). `sg026` stays out (no manifest — stated, not silent).
- Default invocation (no flag) scores sg029 with per-fixture scores IDENTICAL to the pre-change code's run on the same committed cache (v1-identical guard). Scoring/grading code gets NO hunks — selector + path plumbing only; quote the diff to prove it.
- `PG-SC-12`: the BEFORE run is derived at the BASE commit — record which code each run (before/after) actually loaded.

## G2 — frozen baselines recorded (numbers, not prose)

- Score the committed caches OFFLINE for every selected corpus and RECORD frozen baseline files: field_accuracy / unknown_rate / correction_rate + `$0.000000` spend, per-fixture table. New record files are ADDITIVE — `baseline_sg029.md` + `baseline_sg026.md` stay byte-identical (history; empty diffs quoted).
- Reconcile loudly: `baseline_sg029.md` documents **7** fixtures while `corpus/sg029` holds **10** — name the extra three, state which record covers them, never average across the drift silently.
- Drift gate (`PG-EV-01`): the reproduction check fails loudly on altered numbers — prove it seen-to-fail once (feed one doctored expectation, quote the failure, revert). Re-runs reproduce the recorded numbers exactly or the gate is red.

## G3 — tests + gates (extend, don't fork)

- Extend `backend/tests/test_eval_corpus.py` (it EXISTS — 168 lines, sg029 integrity + discrimination; verify on target): selector accepts known / rejects unknown loudly; default invocation == sg029; frozen-baseline reproduction per recorded corpus. FAIL-then-PASS raw for every new test, BOTH runs committed to `SG-085_verify.log` (`PG-EV-09`).
- `PG-SC-11`: grep the test tree for end-relative assertions over corpora/manifests/baselines (`latest`, `[-1]`, `HEAD~1`, tail globs); list every hit with the verdict (updated with reason, or reported as position-independent).
- Full backend suite green modulo the 2 known decoder env reds (base-proved premise — re-verify on bare BASE with stash, do not inherit); `ruff` clean; `mypy` delta 0 quoted against the measured file/error baseline (SG-080 measured 41-in-9 — re-measure, do not inherit); secret grep-gate over the diff (`api_key|OPENCODE_API_KEY|Bearer|token` identifiers, SG-037 shape) with 0 real secret shapes; zero `provider_call` rows post-run.
- Exclusions by RULE with literal grep-gates (`PG-SC-05`): state each rule (e.g. scoring functions, fixture contents, manifests) and gate the literal.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-085.log`, `SG-085_report.md`, `SG-085_verify.log` (raw outputs + BOTH fail-then-pass runs). First token `SG-085`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **$0.000000 actual** (zero provider calls, sandbox state quoted); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/eval/run.py` (selector + path plumbing ONLY — scoring/grading hunks are a STOP) · NEW `backend/eval/baseline_*.md` record files (existing baselines byte-untouched) · SURGICAL edits to `backend/tests/test_eval_corpus.py` (quoted) · `docs/worklogs` (3 files). **Anything else is a STOP** — fixture/manifest contents, prompts, reader/schemas/router, API/frontend, migrations/models, compose/`.env`, STATE/AGENTS/packet dirs.
- Cross-product (`PG-IC-01`): no criterion touches production, the network, or the running service (no restart; reads include the suite + offline runner only — no container image pull/run; a criterion with no forbidding constraint is written down as such: G4's suite run is covered by the same offline-only rule).
- A count or absence premise carries the RAW command output, never a paraphrase.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition — reachability form only.
- Simplicity (`G-A7`): selector + records + pins; no `--live`, no new corpora, no scorer redesign, no Enrich.

## Acceptance criteria

- Selector names sg029+sg079 (sg049 decided + reported); unknown name fails loudly (quoted); default == sg029 with per-fixture scores identical to the base-commit run (which code loaded, quoted both sides).
- Frozen records exist for every scored corpus; old baselines byte-identical; 7-vs-10 drift reconciled by name; re-run reproduces exactly; drift gate seen-to-fail once (quoted).
- New tests FAIL-then-PASS raw, both runs committed; end-relative assertion grep listed with verdicts; suite/ruff/mypy/secrets per G3; zero `provider_call` rows; $0.000000; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — does the runner address any corpus without changing how it scores? G2 — are the frozen numbers recorded, reconciled, and self-checking? G3 — do the extended tests + gates prove the refactor changed nothing but the address? G4 — is the evidence committed, not merely reported?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **$0.000000 actual** (zero provider calls; sandbox state quoted — containment per `PG-PR-04` stated: nothing live exists to contain).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-085 | Report: docs/worklogs/SG-085_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1800s overall; **$0.00** — no metered call exists on any path in this slice.
