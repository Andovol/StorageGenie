# SG-141 — Fix the 3 TS2739 literals blocking the production build (test-only, then green tsc)

**Settings travel on the trigger** (`SG-141 coder=opencode effort=high`, D9) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** D9-authorized fix (owner quote "D9 - approved"; SG-140 F-SG140-1 BLOCKED the close-out deploy): merged `frontend/src/components/WebAlternates.test.tsx` builds `WebAlternate[]` literals with only `{field, value}` at three sites (Architect-verified 2026-09-28 on `origin/automation`: `:58-63` model literal, `:73-83` brand + category literals) while `frontend/src/api/types.ts:144-150` types `source_type`/`source_url`/`retrieved_at` as REQUIRED (`string | null`) — so `npm run build` (`tsc && vite build`) exits 2 and the queue is unserved. Vitest never typechecks, which is why every suite stayed green. THIS slice completes the literals (expected shape: add the three keys as `null`, or the decided equivalent — DECIDE and report), proves `tsc --noEmit` clean + the file + full frontend suite green, nothing else. **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-140's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** FIX slice. Writes: `WebAlternates.test.tsx` (the 3 literals ONLY — any other product hunk is a STOP), `docs/worklogs` (3 files) — and NOTHING else. No type relaxation in `types.ts` without a STOP-and-report (weakening a required triple to ship a test inverts the dependency — decide against it loudly or stop). No rebuild/recreate (the re-ride owns serving; `PG-PR-04` stated). No secret in fixtures (`CO-100` — assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

**DATABASE: none. Restart: none. Deploy: none.**

## G0 — reproduce the red on BASE (fail-pre, committed — `PG-EV-09`)

- Run `tsc --noEmit` on the unmodified tree and quote the 3 TS2739 errors (expectation: `WebAlternates.test.tsx:59,74,79` — differenced either way). Commit the capture BEFORE any edit — a fix without a committed red proves nothing.
- `PG-IC-08` blast radius: expected tsc error set == exactly those 3 in the one file; any error ANYWHERE else stops the run (report, don't fix around it).

## G1 — complete the literals + prove it (fail-post, both runs committed)

- Edit ONLY the 3 literals (expected: the missing keys as `null`; if the component under test treats explicit-`null` differently from omitted — read `WebAlternates.tsx` first — decide the shape and report). `types.ts` stays byte-identical unless a STOP is declared.
- Fail-post: `tsc --noEmit` exit 0 quoted (full output, not a grep for absence); the file's vitest green; FULL frontend suite green-except-base-proved-reds (reds, if any, stash-reproved on bare BASE); `eslint` on the file exit 0. Both runs committed to the verification log.
- `PG-SC-12`: the green is produced by the repo's own `tsc` + vitest through their real configs — BEFORE derived at base, same commands.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-141.log`, `SG-141_report.md`, `SG-141_verify.log` (fail-pre + fail-post captures, suite/eslint, diff ceiling proof). First token `SG-141`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the 3 literals + the 3 worklog files. **Any other write — `types.ts`, other tests, config, build files — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs the tsc red read (600s class bound for typecheck/suite); G1 needs the literal edit + typecheck + suites (modify-versus-call: vitest CALLS the real component through its real config); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): complete the literals, prove the typecheck. No type redesign, no test rewrite, no build-config change — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): red — was the exact 3-error set captured pre-edit? fixed — is `tsc --noEmit` exit 0 with the file + suite green and no other file touched? clean — is the diff exactly the 3 literals + worklogs?
- Fail-pre 3-error capture quoted from the commit + fail-post exit-0 quoted + file + full-suite greens quoted (or base-proved reds) + diff ceiling proof + $0.000000 USD; no vacuous pass (an exit-0 without the full output, a suite silence read as green, or a `types.ts` softening to make red go away evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-141 | Report: docs/worklogs/SG-141_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
