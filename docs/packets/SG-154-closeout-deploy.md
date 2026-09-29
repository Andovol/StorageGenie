# SG-154 — close-out deploy rider (standing directive, rebuild + one recreate + verify)

**Settings travel on the trigger** (`SG-154 coder=opencode effort=high`, standing close-out directive "Always do a live deploy before session close", `AGENTS.md` Close-out row) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** Serves everything landed since the last live deploy (image `76917528` at SG-143): SG-148 offline-SQL chain (migration offline branches only), merge batches A–D (CORS lockdown, evidence bulk paths, schemas tests, independents), all rated 98/99 with receipts. This is a DEPLOY rider: production restart authorized by the standing directive (G-K2 production write — covered, not new). **Expect zero product hunks** — rebuild + exactly ONE recreate + verify only; any product edit is a STOP. **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** RIDER slice. Writes: `docs/worklogs` (3 files) — and NOTHING else. One rebuild, exactly one recreate, verify reads only (no production DB write: counts/health read-only; the CORS proof is an OPTIONS preflight — zero writes). No secret in any capture (`CO-100`).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s rebuild class, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: live SQLite, READS ONLY (counts, health, alembic — no write). Restart: exactly one recreate (authorized). Deploy: this rider.**

## Why this exists

Four merge batches + the offline chain sit committed but unserved (live image is SG-143's `76917528`). The standing directive requires a live deploy before session close. CONFIRMED (rated rows SG-142→153). How the code becomes live (`PG-PR-04`): `docker compose build` + exactly one `up -d` recreate of the changed service(s) + verify. Runtime containment (`PG-PR-06`): rebuild ≤600s class, recreate ≤120s, full verify ≤300s — units stated, actuals reported.

Given facts, each re-verified at runtime before acting (`PG-IC-09`): compose services + current image/container IDs · health endpoint shape (`{{HEALTH_CMD}}`) · gate ports (301/401 pattern per SG-140b) · alembic head `sg114` · the 24-count baseline source (re-read, never inherited).

## G0 — rebuild (one) + exactly one recreate (`PG-PR-03`)

- Rebuild the backend image ONCE; record image ID before/after. Recreate exactly ONE container generation (proof: container-ID change, NOT RestartCount — M42); a second recreate for any reason is a STOP with the reason quoted. `PG-EV-08`: capture BEFORE state (IDs, health, counts, alembic) before the change.
- STOP conditions: rebuild failure (report BLOCKED with the log tail — do not retry blindly); a recreate that changes nothing (report UNMOVED, never force it).

## G1 — verify live (`PG-EV-02`, state change by post-state)

- Health ×6 exact through `{{HEALTH_CMD}}` (quote all six bodies); gate 301/401; `alembic current` == `sg114`; the 24 counts BEFORE==AFTER (delta 0 — any moved count is a finding with the table quoted, never averaged away).
- CORS live proof with ZERO writes: `OPTIONS` preflight with `Origin` + `Access-Control-Request-Headers: If-Match` → 200 with `If-Match` in `allow-headers`; `TRACE` → 400. A mutating request (PATCH/POST/PUT/DELETE) is FORBIDDEN in this slice.
- Bundle note: record whether the served bundle hash moved (backend changed → it moves; state the direction, never assume it).

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-154.log`, `SG-154_report.md`, `SG-154_verify.log` (BEFORE/AFTER IDs, six health bodies, gate lines, alembic, counts table, preflight captures). First token `SG-154`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines. RECOMMENDED-NEXT: hue screenshots (Inbox/Capture/Catalog post-deploy) for the owner verdict.

## Constraints

- **Scope ceiling — WRITES:** the 3 worklog files. **Any product/test/config edit, second rebuild, second recreate, or mutating live request is a STOP.** Reads: compose, image/container IDs, health, gate, alembic, counts, OPTIONS preflight. `PG-PR-03` stated.
- Cross-product (`PG-IC-01`): G0 needs rebuild (600s class) + one recreate (120s class); G1 needs health/gate/counts/preflight (120s class); G2 needs worklog commit + notes receipt. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): serve what is committed, prove it live, nothing more.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): rebuilt — is the image ID new (one build)? recreated — is the container ID new with exactly one generation (M42)? live — are health ×6 exact, gate 301/401, alembic `sg114`, counts delta 0, preflight green with zero writes? clean — is the diff exactly worklogs?
- No vacuous pass (an unrun health check reported as green, a moved count averaged away, or a mutating smoke test evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-154 | Report: docs/worklogs/SG-154_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. RECOMMENDED-NEXT: hue screenshots for the owner verdict.

## Budget

120s ordinary · 600s rebuild class · 2400s overall; expected ~300s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
