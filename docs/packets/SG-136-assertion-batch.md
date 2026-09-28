# SG-136 — Make #16's idea real: batch-load asset assertions, prove the N+1 gone

**Settings travel on the trigger** (`SG-136 coder=opencode effort=high`, D8) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** D8-authorized rewrite (owner quote "D8 - approved"; SG-133 verdict REWRITE-AS-SLICE on PR #16, head `f6a467a`): #16 adds `Asset.assertions` (lazy `relationship`, `order_by="Assertion.field_path"`) + back-populating `Assertion.asset` and rewrites `_asset_to_dict` (`backend/app/api/v1/assets.py`, near `:72`) to iterate `asset.assertions` — which issues the SAME per-asset SELECT (N+1 moved, not removed) and carries a stale import hunk (its base `c849088` predates SG-113 locations + lifecycle imports). THIS slice ships the idea properly: assertions batch-loaded (expected shape: `selectinload` at the asset-query sites, or the relationship dropped for an explicit batched prefetch — DECIDE and report), `_asset_to_dict` output byte-identical per asset, and the N+1 measurably gone. Facts in hand (re-verify — every premise below is a hypothesis): relationship hunks `asset.py:30-36` + `assertion.py:24-28` (from the PR diff, measured this session); current `assets.py` imports carry `relations/location/lifecycle` (measured this session); `_asset_to_dict(asset, db)` signature keeps `db` (callers unchanged). **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-139's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** REWRITE slice. Writes: `asset.py` + `assertion.py` (relationship shape as decided), `assets.py` (query sites + `_asset_to_dict`), new or extended tests proving query-count + output-equality, `docs/worklogs` (3 files) — and NOTHING else. Relationships create no tables — prove empty diff over `backend/alembic/versions/` (a needed migration is a STOP). No rebuild/recreate (unserved until a rider word; `PG-PR-04` stated). No secret within ten lines of any hunk (`CO-100` — assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-07` · `PG-EV-09` · `PG-SC-02` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (relationships are schema-neutral — empty `versions/` diff quoted; temp-DB query-count proof only, `PG-EV-06`: no production rows touched, temp rows reported and left for the scratch DB's own lifecycle). Restart: none. Deploy: none.**

## G0 — enumerate the N+1 + fail-pre (committed — `PG-EV-09`)

- Enumerate EVERY code path calling `_asset_to_dict` on the target (criterion: any caller of the function; expectation: asset list + asset detail routes — differenced either way, a handed list is a fact too — DISPATCH.md §2a).
- Fail-pre, committed BEFORE any edit: on a TEMP database with K≥3 assets carrying assertions, count SELECT statements on the list path (statement listener or query log — real seam, `PG-SC-12`) and quote the N+1 (expected: 1 + K assertion SELECTs); capture `_asset_to_dict` output per asset as the equality baseline. A count that cannot observe the property (e.g. cached session) is not a criterion (`PG-EV-05`).

## G1 — batch-load + prove it (fail-post, both runs committed)

- Ship the decided shape (selectinload at the enumerated sites, or relationship dropped for explicit prefetch). `field_path` ordering preserved (the relationship's `order_by` or an explicit `order_by` — decide, and the equality proof covers it).
- Fail-post: SAME temp scenario — SELECT count constant in K (quote both counts), `_asset_to_dict` output per asset byte-identical to the G0 baseline (behaviour-preservation rail: identical output per site across every input shape present — divergence is a STOP). Empty-asset world named: zero assertions → zero assertion SELECTs beyond the base query (`PG-SC-07`).
- `PG-IC-08` blast radius: expected SELECT counts written down BEFORE measuring (1 + K pre, constant post) — a measured count differing either way stops the run.
- Full backend suite green-except-base-proved-reds (600s bound; reds stash-reproved on bare BASE); ruff clean; mypy delta stated with file list (new errors = STOP-and-report, never fixed by widening ignores); empty `versions/` diff quoted.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-136.log`, `SG-136_report.md`, `SG-136_verify.log` (fail-pre + fail-post captures, equality proof, suite/mypy/ruff, empty-versions proof). First token `SG-136`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the relationship/query-site hunks, their tests, the 3 worklog files. **Any other write — versions/, served-route behaviour beyond identical output, frontend, scheduler — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs temp-DB counting + baseline capture (reads INCLUDE temp-DB writes on scratch paths only — production DB is NOT included and any touch is a STOP); G1 needs the hunks + equality + suites (modify-versus-call: tests CALL the real routes/seam, fixtures never bypass it); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): batch the load, prove the count, prove equality. No query-builder abstraction, no caching layer, no pagination rework — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): batched — is the assertion SELECT count constant in K on the list path? identical — is `_asset_to_dict` output per asset byte-equal to baseline? safe — do suites hold with reds proved base-side and the migration surface empty?
- Fail-pre N+1 count quoted from the commit + fail-post constant count quoted + per-asset equality quoted + suite/mypy/ruff quotes + empty `versions/` diff + $0.000000 USD; no vacuous pass (a count without K≥3, an equality without the baseline, or a suite skipped for speed evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-136 | Report: docs/worklogs/SG-136_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~1200s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
