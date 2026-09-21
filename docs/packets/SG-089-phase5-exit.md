# SG-089 — Phase 5 exit: re-prove the bounded condition, carry verdicts unmodified, state limits (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D107-approved slice 5 (LAST) of the Phase 5 hardening stage (plan `docs/superpowers/plans/2026-09-21-phase-5-hardening.md` Slice 5). The bounded exit condition: eval runner scores every frozen corpus with recorded baselines; backup restores to temp byte-equal with a runbook; privacy audit proves redaction + identifiers-only; the registry is derived, not listed. THIS slice re-proves that condition on the current tree, carries the slice verdicts unmodified, states the limits, and closes the stage — it builds no new machinery and fixes nothing. Anything red here is a STOP, not a repair-in-slice. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** exit verification ONLY (enumerated ceiling below). No product-code change, no migration, no schema change, no secrets in logs, no deploy, no restart (`PG-PR-04` — nothing becomes live). No provider calls, $0.
**Money posture:** $0.00 by construction — no metered call exists on any path. No bound to multiply out (`PG-IC-04` stated as not firing).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-05` · `PG-SC-09` · `PG-SC-11` (grep + verdict, see G3) · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NOTHING live stated).

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

**DATABASE: none (temp fixtures only). Restart: none. Deploy: none.**

## G1 — re-prove the bounded condition on this tree (numbers, not inheritance)

- Re-run, do not quote old logs: all three frozen corpora reproduce their records through the REAL selector (`--corpus sg029/sg049/sg079`) — I hold sg029 `0.833/0.571/0.000`, sg049 `1.000`, sg079 `1.000` (re-verify each figure against the record files on target, never inherit my numbers). Any drift is a STOP, not a re-baseline.
- Full backend suite green modulo the 2 known decoder env reds (base-proved premise — re-verify on bare BASE with stash, do not inherit); `ruff` clean; `mypy` delta 0 quoted; secret grep-gate over the diff (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken` identifiers, SG-037 shape) with 0 real secret shapes; `provider_call` rows 0.
- Read-back the stage artifacts exist where claimed (`PG-EV-02`): the three `baseline_*_frozen.md` records, `backend/scripts/backup_restore_drill.py` + its test, `backend/tests/test_privacy_audit.py`, the SG-086 README runbook hunk, `EXPECTED_TABLES` still 0 hits. A missing artifact is a STOP, not an inference.

## G2 — carry verdicts unmodified + state limits (the exit record)

- Quote (never paraphrase) the per-slice verdict lines: SG-085 frozen numbers, SG-086 byte-equality hashes, SG-087 no-hole verdict, SG-088 derivation proof — with the report paths they came from. Carrying means quoting; re-proving means G1.
- Limits, each stated in one line: Enrich queued after Phase 5 (D108, Jina key placed, Vision deferred); PG/S3 declined until scale demands; UX tracks (per-field accept UI, chat persistence) queued; sg026 unfrozen (no manifest); ledger-row retention deferred to the production-datastore slice; backups manual (D118); CLI drift open (host `1.17.19` vs recorded `1.18.31`); pilot tiers uncalibrated. A limit you cannot verify on target is marked unverified, never dropped.
- Ratings completeness read-back: rows for SG-085, SG-086, SG-087, SG-088, SG-090, SG-091 present in `docs/ratings.md` with scores/flags — report present-or-missing per row (filling gaps is NOT in this slice; a gap is a finding with the Architect as destination).

## G3 — surgical README delta if owed, else nothing (restraint is the deliverable)

- If and only if the README misstates Phase 5 status after G1/G2, ONE surgical hunk (quoted) correcting it. Otherwise no README diff — state "no delta owed" explicitly.
- `PG-SC-11`: grep the test tree for end-relative assertions touching anything this slice reads; list hits with verdicts (expectation: none — state the empty result raw).
- Exclusions by RULE with literal grep-gates (`PG-SC-05`): no `app/` hunks (`git status --porcelain backend/app` empty), no migration, no prompt diff, no `EXPECTED_TABLES` resurrection (grep 0 hits).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-089.log`, `SG-089_report.md`, `SG-089_verify.log` (raw outputs + every re-run + every read-back). First token `SG-089`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **$0.000000 actual**; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** SURGICAL README hunk ONLY if G3 owes one (quoted, else no README diff) · `docs/worklogs` (3 files). **Anything else is a STOP** — app code, tests, prompts, migrations/models, compose/`.env`, scripts, STATE/AGENTS/packet dirs, ratings.md (read-back only; the Architect owns the ledger).
- Cross-product (`PG-IC-01`): no criterion changes product code or touches the network beyond pushes; reads include the suite + read-backs only — no container image pull/run; a red leg stops the exit, it never becomes a repair.
- A count or absence premise carries the RAW command output, never a paraphrase.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition — reachability form only.
- Simplicity (`G-A7`): re-run + read back + state limits; no new proofs, no new machinery, no Enrich.

## Acceptance criteria

- All three corpora reproduce records exactly on this tree (figures quoted, not inherited); suite/ruff/mypy/secrets per G1; provider_call 0; any drift is a STOP with the differing figure quoted.
- Every stage artifact read back present; verdicts quoted unmodified with paths; limits each stated in one line, unverified ones marked.
- Ratings rows present-or-missing reported per row; README delta owed-or-not with the hunk or the explicit no-delta statement; exclusion gates quoted; $0.000000; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — does the condition still hold on this tree? G2 — is the exit record complete and honest about limits? G3 — did the slice change only what the exit owed? G4 — is the evidence committed, not merely reported?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **$0.000000 actual** (zero provider calls — containment per `PG-PR-04` stated: nothing live exists to contain).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-089 | Report: docs/worklogs/SG-089_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1800s overall; **$0.00** — no metered call exists on any path in this slice.
