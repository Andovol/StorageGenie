# SG-117 — Jina default base EU→global: switch the default, keep EU named, serve it (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D11-approved served-code slice under D10 L3 (SG-116 EU-DEAD follow-up). SG-116 proved `eu.s.jina.ai` NXDOMAIN (getent exit 2 + gaierror, 0 HTTP bytes) while `s.jina.ai` answers HTTP 200/3-results through the real client; verdict EU-DEAD with this switch as the outlined follow-up. The trade-off, decided by D11 and recorded here: the SG-082 EU data-residency posture for the Romania scope is superseded by reachability — queries go to the global endpoint until the EU base resolves again; no geography is claimed for the global endpoint beyond its URL. THIS slice switches the default, updates the pins, and serves the change. **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.36.0` == published (`a9324d5`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** served-code change → rebuild + exactly ONE recreate + verify as this slice's final goal (D145); the recreate is the D11-authorized production mutation (`G-K2`). All behavioural proofs run on temp DBs — NO enrich press, NO production write (`PG-PR-10`: resolution stays in test scope). Secrets: key names only, never bytes; `docker compose config` FORBIDDEN (`PG-SC-05`); `.env` excluded by rule, never by literal. No metered call exists on any path in this slice ($0 — a live Jina search is a STOP-and-report; correctness price paid in the same breath per `PG-EV-04`: the served default is proven by committed tests + deploy health + a read-only served-constant read, and the first live search belongs to the next Enrich slice's press, with a request-shape test on the real builder carried here instead).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.36.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 60s ordinary, 1200s overall (suite + rebuild need it). A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none touched (temp DBs for behavioural proofs). Restart: exactly ONE backend recreate (D11-authorized). Deploy: rebuild + recreate + verify, this slice.**

## G1 — the switch (expectations; enumerate the set on the target, never trust my list)

- BEFORE capture (`PG-EV-08`): quote the current default-base value pre-change (the observable this slice moves).
- Switch the effective default from `JINA_EU_BASE_URL` to `JINA_GLOBAL_BASE_URL` (`backend/app/services/enrich/jina.py:42-43` values verified 2026-09-25; the live route `fetch_with_fallback` → `fetch_jina_search` passes NO explicit base, so the default params at `jina.py:117` (`build_jina_request`) and `jina.py:239` (`fetch_jina_search`) are the switch surface — verify no caller passes an explicit EU base, `backend/app/api/v1/enrich.py:188` first, and report the enumeration criterion + difference either way).
- Two shapes are acceptable, decide and report: (a) repoint the two defaults at the global constant, or (b) introduce one `JINA_DEFAULT_BASE_URL` the two defaults share. Either way the EU constant STAYS as a named non-default (mirror of the SG-082 discipline, direction reversed) and the module docstring (`jina.py:10`, EU-residency claim) is updated to the D11 trade-off with the decision id.
- Residency comment at the constants: one short comment stating the D11 trade-off (reachability over EU-residency until the EU base resolves), never a geography claim about the global endpoint.
- Request-shape test on the real builder: one test asserting the exact global-base request shape (URL + repeated site tuple + header names, SG-082 shape) — the no-network substitute for the deferred live search (`PG-EV-04`).

## G2 — pins flipped fail-first, suite green after (both runs committed, `PG-EV-09`)

- Expected pin surface (Coder re-enumerates: grep the test tree for `eu.s.jina.ai` + `JINA_EU_BASE_URL` and add every hit driving the changed code): `backend/tests/test_sg082_enrich_jina.py` (`:95`, `:119-123` the mirror test, `:136`, `:207`, `:299`, `:401-523`, `:581`) plus `test_sg101_text_path.py:44` + `test_sg099_synthesis.py:48` `JINA_URL` fixtures IFF they assert against the default rather than passing an explicit base (report which).
- Genuine FAIL leg: the old EU pins run against the switched code go red first (quoted), then the updated pins (mirror test now asserting default-is-global-and-EU-named-not-default) go green; BOTH runs committed raw.
- Full backend suite after; the 2 decoder reds are stash-proved base failures by precedent (prove, never assume). Frontend diff empty → frontend suite waived by stated ceiling (diff over `frontend/` empty), named substitute: none needed, no frontend behaviour changes.

## G3 — rebuild + exactly ONE recreate + served proof

- Rebuild, then exactly ONE recreate (container-id change is the proof; `RestartCount+1` never asserted — M42). Verify: image/container ids differ, health 6× exact, gate 301/401, alembic head unchanged, all counts delta 0 (no press ran, so any delta is a STOP).
- Served-default read: read-only `python -c` import of the default base from INSIDE the running backend container (a read of already-running code, decided here per `PG-IC-01` — launching no new runtime, executing no write) quoted == global; plus the pre/post BEFORE pair (`PG-EV-08`).
- Containment (`PG-PR-06`): lane `RUN_BUDGET_S` + the 1200s overall bound above; actual-versus-budget per leg with units in the report. How the code becomes live is this goal (`PG-PR-04`).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-117.log`, `SG-117_report.md`, `SG-117_verify.log` (fail-pre + pass-post raw, BEFORE/AFTER pair, served-constant read, health/gate/counts). First token `SG-117`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — `backend/app/services/enrich/jina.py` (switch + comment + docstring), `backend/tests/test_sg082_enrich_jina.py` (+ `test_sg101_text_path.py` / `test_sg099_synthesis.py` only the `JINA_URL` lines iff they assert the default), `docs/worklogs` (3 files). READS — the caller `backend/app/api/v1/enrich.py` (explicit-base check), suite, daemon (read-only), running container (read-only exec). **Anything else written is a STOP** — compose, `.env` (rule-excluded), migrations, STATE/AGENTS, frontend.
- Cross-product (`PG-IC-01`): G1 needs constant edits + caller read + shape test; G2 needs test edits + suite; G3 needs rebuild + one recreate + read-only served read. No criterion writes the DB, presses enrich, or touches secrets. No criterion demands what the ceiling forbids.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): switch, pin, serve. No live search is run here, however small.

## Acceptance criteria

- BEFORE/AFTER default-base pair quoted (pre EU, post global); no caller passes an explicit EU base (enumeration + difference reported).
- EU constant retained named-non-default; residency comment + docstring carry D11; mirror test asserts default-is-global.
- Fail-pre red quoted + pass-post green quoted, both committed; full backend suite green modulo stash-proved base reds; request-shape test on the real builder green.
- Exactly ONE recreate (container-id change quoted); health/gate/alembic/counts as stated; served-constant exec read == global.
- $0; no enrich press; no writes outside the ceiling; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-117 | Report: docs/worklogs/SG-117_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 1200s overall; expected ~1200s (Architect's record; the lane enforces `RUN_BUDGET_S`); $0 (no metered call on any path — a live search is a STOP); actual-versus-budget per leg with units.
