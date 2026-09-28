# SG-140 — Close-out deploy rider: serve everything landed (rebuild + one recreate + verify)

**Settings travel on the trigger** (`SG-140 coder=opencode effort=high`, standing close-out directive) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** Standing close-out directive (`AGENTS.md` Close-out row, owner 2026-09-28: live deploy before every session close — this IS the `PG-PR-10` authorising grant for the single recreate below, `G-K2` stated, production restart named plainly). Since the last served image, these product changes landed UNSERVED (all rated, all receipted — re-verify currency on the target, never inherit): SG-135's 11 merges (evidence query batch, asset subqueries, dedup prefetch, memoized ProductCard, chat-init re-exports, taxonomy index+cache, analytics batching, chat+planning batching, health logger + caplog test, 2 vitest files) · SG-139 (non-disabling `fileConfig`, dedup `Row` annotation) · SG-136 (assertion relationship + `selectinload`, cascade) · SG-137 (`client.test.ts` union) · SG-138 (HouseholdSelector + test, Chat/Planning adopters, `*.log` ignore). No slice since added a migration (each proved empty `versions/` — re-verify, and any head you did not expect is a STOP, do not upgrade). THIS slice rebuilds + recreates exactly once + verifies, nothing else. **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-138's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** RIDER slice. Writes: `docs/worklogs` (3 files) — and NOTHING else. NO code changes — any product-file diff vs BASE is a STOP (prove by empty product diff at start AND end). Exactly ONE `recreate` (container-id change quoted — `RestartCount` never the proof, M42); a second recreate, a restart-loop, or any `down -v` is a STOP. No migration run (prove `alembic current` head unchanged before AND after). No secret in any capture (`CO-100` — health bodies carry status strings only; assert no DSN/key/token in any committed artifact).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-PR-10` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 300s build/recreate steps, 120s ordinary, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none read or written beyond `alembic current` (read-only head check). Restart: exactly ONE recreate (grant above). Deploy: that recreate only.**

## G0 — prove nothing to serve but the queue (reads only — stated, not solved)

- Empty product diff vs BASE at start (any product hunk = STOP — the rider carries no code).
- `alembic current` head quoted (expectation: `20260924_sg114_relation` — differenced either way; an unexpected head is a STOP, do not upgrade).
- Pre-rider baseline: image id, container id, health exact-shape ×2, served JS bundle hash (frontend changed since last image — EXPECT the post bundle to differ; a byte-identical bundle is a finding, not a pass — `PG-EV-05`).

## G1 — rebuild + ONE recreate + verify (in this order — `PG-PR-04`)

- Rebuild (quote image id; 300s bound) + exactly ONE recreate (quote container-id change; 300s bound) + verify: health exact-shape ×6 (`GET /v1/health` status/body per `{{HEALTH_CMD}}`), gate 301/401, `alembic current` head UNCHANGED from G0, live counts delta == 0 (no press rows — a rider creates none), served bundle hash DIFFERS from G0 (frontend shipped) with the new `HouseholdSelector`/`client.test.ts`-era bundle quoted by hash (bytes, not rendering).
- Live smoke through the real seam (`PG-EV-07`): one `GET /v1/assets` 200 + one served frontend 200 (loopback or Host-header form per F-SG053-2 — never an external vantage claim without one). Quote statuses + shapes.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-140.log`, `SG-140_report.md`, `SG-140_verify.log` (G0 proofs, image/container ids, health ×6, gate, alembic before/after, bundle hashes, smoke). First token `SG-140`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the 3 worklog files. **Any product-file write, second recreate, migration run, `down -v`, or served-path mutation beyond the single recreate is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs diff + head + baseline reads; G1 needs rebuild + one recreate + served proofs (modify-versus-call: the recreate IS the authorized production mutation — the grant line above is its authority); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 300s build-recreate / 2400s overall), never one blanket timeout. Reads INCLUDE container exec probes + in-image checks; pulling any image besides the slice's own rebuild is NOT included and is a STOP. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): rebuild, recreate once, verify. No config tuning, no migration, no log-level changes — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): served — does the running build carry the landed queue (bundle hash moved, image id new)? safe — is it exactly one recreate with head/counts unmoved and gates holding? clean — is the product diff empty at start and end?
- Empty product diffs quoted (start + end) + image/container ids quoted + health ×6 quoted + gate quoted + alembic before==after quoted + bundle hash moved quoted + smoke quoted + $0.000000 USD; no vacuous pass (a health shape without exact body, a bundle asserted without hash, or a recreate counted by RestartCount evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-140 | Report: docs/worklogs/SG-140_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 300s build/recreate · 2400s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
