# SG-097 — Parked Enrich remainder: Jina settings field + .env.example + docs + example (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D130-approved parked Enrich remainder (the config/docs leg of SG-082's REMAINING; endpoint+trigger, synthesis prompt+caller, and persistence model+migration are OUT OF SCOPE — later slices). SG-081 shipped the OFF library and SG-082 the Jina fallback + review mapping as unwired code; F-SG082-2 left `app/config.py` and `.env.example` untouched by ceiling (`Settings` declares no Jina field, `extra="ignore"`, key lives only in host `.env`). `jina.py` `resolve_api_key` already probes `settings.jina_api_key` via `getattr` with env fallback (verified by the Architect 2026-09-23 — re-verify on target, expected not certain). THIS slice declares the field, documents the seam, and commits a worked example. **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** config + docs ONLY. No endpoint, no trigger wiring, no synthesis prompt/caller, no persistence model/migration (prove by diff: `models/` + `alembic/` untouched), no deploy, no restart, no container action — the running service is untouched (`PG-PR-04`). No live Jina call ($0 — a metered call is a STOP-and-report, never a disclosure). Key VALUES never in logs or commits — names only; tests use dummy `"test-"` literals, never real key material.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-04` · `PG-EV-05` · `PG-EV-09` · `PG-SC-05` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 1200s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (declared honestly — under 0.32 rules this keeps engine-relaunch-on-transient eligibility; a slice that writes data or restarts is never relaunched).

## G1 — Jina settings field (one field, precedence proven)

- `backend/app/services/enrich/jina.py` `resolve_api_key` resolves explicit-arg → `settings.jina_api_key` (when declared) → `JINA_API_KEY` env (enumerate the seam on target — the function that turns configuration into the send-time key — with the criterion stated; a list is a fact too). Declare `jina_api_key: str | None = None` in `Settings` beside `opencode_api_key` (`config.py:29` expected). No other settings change; `jina.py` logic change ONLY if the seam differs from this premise (disclosed, minimal).
- Prove the no-migration claim by diff: `backend/app/models/` + `backend/alembic/` byte-untouched — or report the migration this slice would need and STOP before writing it.

## G2 — precedence tests (fail-then-pass through the real seam)

- Extend `backend/tests/test_sg082_enrich_jina.py`: settings-field beats env (monkeypatched field + env both set), explicit-arg beats field, absent-field falls through to env. FAIL-then-pass raw BOTH runs committed (`PG-EV-09`): pre-change the settings leg cannot resolve (field absent — quote the failure mode per test, never one shared paraphrase). Dummy `"test-"` key literals only; assert no test interpolates a real value.
- `PG-SC-12`: assertions drive the REAL `resolve_api_key` over the REAL `Settings` — no re-implemented seam. Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real.

## G3 — .env.example + docs + worked Jina example

- `.env.example`: add the `JINA_API_KEY=` names-only line (file convention line 1: NAMES only, values never committed). End-relative grep over `.env.example` committed raw (append-discipline, `PG-SC-11` family).
- Document the seam where an operator looks (enumerate on target: README env section or the Enrich docs home — criterion: the file a key-rotating operator opens): field → env → explicit precedence, Bearer added at send time only, names-only logging. One worked example committed: the request the driver builds (EU-default base, header NAMES, `site:` query shape) derived from the REAL driver constants (`PG-SC-12` — assert the example's shape against them, never a re-typed copy). No live call.
- `PG-SC-05`: exclude key material BY RULE — `JINA_API_KEY` may appear only in names-only contexts (code identifier, example placeholder, docs prose); grep-gate the literal tree-wide over the diff and quote the hits.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-097.log`, `SG-097_report.md`, `SG-097_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate). First token `SG-097`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `config.py` (one field) + `test_sg082_enrich_jina.py` + `.env.example` (one line) + the documented seam file + the example artifact + `docs/worklogs` — NOTHING else. **Suite-green binds on collision** (minimal root-cause repair + disclosure, M45); anything else is a STOP.
- Cross-product (`PG-IC-01`): no criterion demands an endpoint, synthesis call, migration write, live call, deploy, or container act — no cell collides; stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- `jina_api_key` declared nullable beside `opencode_api_key`; precedence explicit > field > env proven through the REAL seam; pre-change failure modes quoted per test.
- `.env.example` carries the names-only line; seam documented where the operator looks; worked example committed with shape asserted against the REAL driver constants.
- Diff touches no `models/`/`alembic/` path; literal-gate shows names-only contexts; end-relative grep clean.
- Tests fail-pre/post-pass both committed raw; suite + ruff + mypy + secret gates green; $0; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — does configuration reach the sender through the declared field? G2 — does the precedence hold against the real seam? G3 — can the next operator rotate the key from docs alone?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-097 | Report: docs/worklogs/SG-097_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1200s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
