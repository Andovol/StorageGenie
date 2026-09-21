# SG-088 — derived table registry: remove the EXPECTED_TABLES static copy, keep the tripwires (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D107-approved slice 4 of the Phase 5 hardening stage (plan `docs/superpowers/plans/2026-09-21-phase-5-hardening.md` Slice 4). The trap: `EXPECTED_TABLES`, a static 18-name set hand-maintained in `backend/tests/test_postgres_dialect.py:35-54`, is imported by `backend/tests/test_plugin_taxonomy.py:25` — every table-adding slice trips two pins it did not touch, and the set is a second copy of what `Base.metadata` + the model imports already define. THIS slice removes the static copy: derive, don't list. Product code (`app/`, models, migrations) gets NO hunks — tests only. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** test files ONLY (enumerated ceiling below). No schema change, no new tables, no behaviour change, no migration, no secrets in logs, no deploy, no restart (`PG-PR-04` — nothing becomes live). No provider calls, $0.
**Money posture:** $0.00 by construction — no metered call exists on any path. No bound to multiply out (`PG-IC-04` stated as not firing).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-05` · `PG-SC-09` · `PG-SC-11` (grep + verdict, see G2) · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NOTHING live stated).

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

## G1 — remove the static copy, keep both tripwires (tests only)

- Re-read both files fully before touching (`PG-IC-09`): I hold the static set at `test_postgres_dialect.py:35-54` (18 names), consumed at `:59,63,65` and imported at `test_plugin_taxonomy.py:25` for the `:62,83` pins. Reconcile the count (18?) and every consumer against the tree — an unlisted third consumer is a finding.
- Load-bearing fact the shape turns on: the two pins protect DIFFERENT properties — (a) dialect test: EVERY metadata table compiles for PostgreSQL (needs completeness over whatever exists, never a fixed list); (b) taxonomy exit test: registration ADDS NO tables (needs `before == after`, never equality with a fixed set). A derivation that re-lists the names anywhere (helper, constant, second file) is the same trap moved, not removed — grep-gate the literals after the change (`PG-SC-05`: exclude by rule, gate the literal; the FTS5 exclusion stays rule-based per the file docstring).
- Preserved, not weakened: the FTS5 exclusion remains a RULE (SQLite FTS5 has no PG equivalent — stated in place); the taxonomy exit property still fires on a table-adding registration; the dialect check still covers every table present.
- Seen-to-fail (`PG-EV-01`), each quoted: (a) a test-space table-adding registration MUST trip the exit pin loudly (plant, quote the failure, remove the plant); (b) a planted PG-uncompilable construct MUST fail the dialect compile loudly (plant, quote, remove). Gates never fed a bad input are decoration.
- `PG-SC-12`: assertions run against the REAL `Base.metadata` + REAL registry import — no fixture metadata re-implements the table set (a fake metadata proves the fake).

## G2 — gates + no other movement (green, honest)

- New/changed tests FAIL-then-PASS raw, both runs committed to `SG-088_verify.log` (`PG-EV-09`) — FAIL-PRE is the new mechanism asserted against the old static files (or the plants above against BASE; state the composition explicitly, never silently).
- `PG-SC-11`: grep the test tree for end-relative assertions over tables/metadata/registry (`latest`, `[-1]`, `HEAD~1`, tail globs, count literals like `== 18`); list every hit with a verdict (updated with reason or position-independent). The old `== EXPECTED_TABLES` legs are replaced, not left dangling — grep proves no leg still names the removed set.
- Full backend suite green modulo the 2 known decoder env reds (base-proved premise — re-verify on bare BASE with stash, do not inherit); `ruff` clean; `mypy` delta 0 quoted (test files included); secret grep-gate over the diff (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken` identifiers, SG-037 shape) with 0 real secret shapes.
- A table-adding product change in this slice is a STOP (out of scope — no migration, no model). A second static copy anywhere is a STOP the Coder reports rather than ships.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-088.log`, `SG-088_report.md`, `SG-088_verify.log` (raw outputs + BOTH fail-then-pass runs + every enumeration). First token `SG-088`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **$0.000000 actual**; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** SURGICAL edits to `backend/tests/test_postgres_dialect.py` + `backend/tests/test_plugin_taxonomy.py` (every hunk quoted; no new test files unless the derivation needs a home — decided and reported) · `docs/worklogs` (3 files). **Anything else is a STOP** — `app/`, models, migrations, prompts, compose/`.env`, README, STATE/AGENTS/packet dirs.
- Cross-product (`PG-IC-01`): no criterion changes product code or touches the network beyond pushes; reads include the suite only — no container image pull/run; G3's suite run is covered by the same offline rule.
- A count or absence premise carries the RAW command output, never a paraphrase.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition — reachability form only.
- Simplicity (`G-A7`): derive + pin + prove; no helper framework, no registry refactor, no Enrich.

## Acceptance criteria

- No static table-name copy remains (literal grep-gate empty, quoted); FTS exclusion still rule-based and still excluding.
- Exit pin fires on a planted table-adding registration (quoted); dialect compile covers every metadata table + fails a planted uncompilable construct (quoted); plants removed.
- New/changed tests FAIL-then-PASS raw both committed; end-relative grep listed with verdicts; no leg names the removed set; suite/ruff/mypy/secrets per G2; $0.000000; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — is the list gone with both tripwires intact? G2 — is the suite green for the right reason? G3 — is the evidence committed, not merely reported?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **$0.000000 actual** (zero provider calls — containment per `PG-PR-04` stated: nothing live exists to contain).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-088 | Report: docs/worklogs/SG-088_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1800s overall; **$0.00** — no metered call exists on any path in this slice.
