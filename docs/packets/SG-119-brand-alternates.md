# SG-119 — Brand alternates: OFF `brands` into the merge vocabulary + visible render (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D10-chain slice (F-SG103-5: "brand alternate unrepresentable until a web path emits brand"). Architect path-trace 2026-09-25 (`PG-SC-01`, reads only — stated, not solved): WRITE — `map_off_decision_fields` (`backend/app/services/candidates.py:282-311`) emits `display_name`/`identifier`/`category_proposed` from the OFF product but drops `brands` although the payload carries it (`client.py:26` `OFF_FIELDS` includes `brands`; `scoring.py:141` reads `product.get("brands")`); the Jina mapper (`:314-344`) emits no brand either; `enrich.py:112-113` already records the gap citing `PG-SC-07`. READ — `merge_web_fields` (`:347-380`, label-wins → alternates) → enrich route attaches `web_alternates` (`enrich.py:216,226,252`) → candidates route serves (`candidates.py:173-187`) → frontend renders NO alternates anywhere (Architect grep 2026-09-25 over `frontend/src` for `web_alternates|alternates`: review/CandidateCard display only — zero render hits). So a brand alternate needs the mapper AND the render, or it stays invisible. THIS slice ships both. **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.36.0` == published (`a9324d5`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** served-code change (API shape + UI) → rebuild + exactly ONE recreate + verify as this slice's final goal (D145); the recreate is the D10-authorized production mutation (`G-K2`). Behavioural proofs on temp DBs/fixture transports only — NO live OFF/Jina search ($0 — a metered call is a STOP-and-report; correctness price per `PG-EV-04`: request-shape + fixture-shape tests on the real builder/mapper, live press belongs to the next Enrich slice). Secrets: none involved; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.36.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-01` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-DP-02` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 60s ordinary, 1200s overall (suites + rebuild need it). A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none touched (temp DBs/fixtures). Restart: exactly ONE recreate (D10-authorized). Deploy: rebuild + recreate + verify, this slice.**

## G1 — OFF `brands` into the merge vocabulary (both populations, `PG-SC-07`)

- BEFORE capture (`PG-EV-08`): quote an OFF-brand-holding fixture producing NO brand field/alternate pre-change.
- Map `product.get("brands")` in `map_off_decision_fields` with `_web_provenance` (`OFF_WEB_SOURCE`) exactly like the sibling fields — then it flows through the existing `merge_web_fields` rule untouched (no merge change: label-visible brand present → alternate; brand-absent → gap-fill per the standing rule — DECIDE the brand-absent behavior explicitly against the `synthesize.py` brand-absent refusal discipline and report which wins and why; never invent a brand the payload did not carry).
- Populations (`PG-SC-07`, each with a named outcome): brand-present asset + OFF brands → alternate (or stated variant); brand-absent asset + OFF brands → decided behavior; OFF-miss/empty brands → no brand emitted, gap stays, no alternate. A silent fallback or substitution is reported as the defect it is.

## G2 — render the brand alternate (trace to the screen, `PG-SC-02`)

- Enumerate on the target every surface showing asset brand today (criterion, not my list — mine found none rendering alternates) and render the brand alternate there (asset detail + review/CandidateCard at minimum if they show brand); the full `asset_id` discipline from SG-118 holds (ids in hrefs, never visible text).
- If a surface cannot honestly show it, name the follow-up instead of widening silently. Frontend fail-then-pass with a brand-alternate fixture (alternate visible, source shown).

## G3 — pins + suites (both runs committed, `PG-EV-09`)

- Backend: new mapper tests (brands→provenance, both populations, miss→absent) fail-pre→pass-post; full backend suite after, reds stash-proved by precedent. Frontend: render tests fail-pre→pass-post; full vitest after. `tsc` + vite build + eslint clean.

## G4 — rebuild + exactly ONE recreate + served proof

- Rebuild, exactly ONE recreate (container-id change; `RestartCount+1` never asserted — M42). Verify: bundle differs with marker, health 6× exact, gate 301/401, alembic head unchanged, all counts delta 0 (no press ran — any delta is a STOP). Served proof: brand-alternate fixture driven through the LIVE route read path is NOT a press — instead prove the served shape by asserting the live OpenAPI/route table exposes the unchanged contract plus the new field through a GET-only read (decide the narrowest live read, report it); no POST, no rows created.
- Containment (`PG-PR-06`): lane `RUN_BUDGET_S` + 1200s overall; actual-versus-budget per leg with units. How the code becomes live is this goal (`PG-PR-04`).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-119.log`, `SG-119_report.md`, `SG-119_verify.log` (BEFORE/AFTER pair, both test runs raw, served proofs). First token `SG-119`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — `backend/app/services/candidates.py` (mapper only — merge rule untouched unless the brand-absent decision forces it, stated), backend enrich/candidate tests, frontend brand surfaces + tests, `docs/worklogs` (3 files). READS — enrich route, candidates route, suite, daemon (read-only). **Anything else written is a STOP** — merge-rule redesign, compose, `.env` (rule-excluded), migrations, STATE/AGENTS, synthesis prompts.
- Cross-product (`PG-IC-01`): G1–G2 need mapper + surface edits + tests; G4 needs rebuild + one recreate + GET-only live read. No criterion writes the DB, runs a metered call, or touches secrets. No criterion demands what the ceiling forbids.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): map, render, serve. No vocabulary redesign is attempted here, however small.

## Acceptance criteria

- BEFORE/AFTER brand pair quoted (absent pre, present post); brand-absent decision explicit with its discipline cited; miss→absent with no alternate.
- Brand alternate visible on every brand-showing surface (enumerated) with source, or a named follow-up; ids never visible text.
- Fail-pre red + pass-post green quoted, both committed, backend and frontend; suites green modulo stash-proved base reds; build+lint clean.
- Exactly ONE recreate (container-id change); bundle/health/gate/alembic/counts as stated; GET-only served read quoted.
- $0; no press; no writes outside the ceiling; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-119 | Report: docs/worklogs/SG-119_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 1200s overall; expected ~1200s (Architect's record; the lane enforces `RUN_BUDGET_S`); $0; actual-versus-budget per leg with units.
