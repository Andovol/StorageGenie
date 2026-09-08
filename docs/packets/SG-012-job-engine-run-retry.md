# SG-012 — Job engine core: durable steps, run, retry-resume (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 slice 1 of 7 (plan `docs/superpowers/plans/2026-09-08-phase-1-deterministic-import.md`, D9). Previous reports' open items answered: SG-011 REMAINING (43 advisory mypy + one Starlette warning) stays advisory/out-of-scope — mypy is not a gate; SG-010 REMAINING (runner-side push/notes, non-live Docker verification) — Docker/restart verification stays out of scope, no service is touched.

> Facts below are what I believe from the tree that carries this packet. **They are EXPECTED conditions,
> not established truth. Verify each before building on it; a difference is a finding, not an obstacle.**
> For any number, path or quoted line I hand you: if your figures differ from mine, investigate and
> explain — **do not bend your answer to match mine. Correcting me is worth more than agreeing with me.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** No live database, no service touch (`PG-PR-04`: the running service is not touched; all proof is in-process via `TestClient` + temp SQLite). Test-created rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): the whole slice must finish inside 2100s — report elapsed against it. Coder-side `python`/`pytest` are absent on the host PATH — name `venv/bin/` binaries explicitly.

## Why this exists

Phase 1 needs imports that survive failure. Today the `job`/`job_step` tables exist (`backend/app/models/job.py:8-32` — `Job` with `job_type/state/idempotency_key/config_snapshot/household_id`, `JobStep` with `step_name/state/attempts/input_refs/output_refs`) but nothing writes them: `GET /v1/jobs` computes a real query then returns `{"items": [], ...}` (`backend/app/api/v1/jobs.py:36`), and there is no create/run/retry path anywhere. This slice builds the synchronous in-request runner (modular monolith — no worker process; if the slice proves this inadequate, that is a finding with an ADR-003 amendment, not a silent redesign) with deterministic step names from the blueprint pipeline minus the AI legs (`VALIDATING_INPUT → NORMALIZING → EXTRACTING_DETERMINISTIC_SIGNALS → DEDUPLICATING → AWAITING_REVIEW → COMMITTING`, terminals `COMPLETED/FAILED/CANCELLED`, `RETRYING` on retry). Signal/dedup/commit step bodies are stubs returning `not_implemented` outputs — SG-013/SG-014 fill them; the engine, persistence, and resume mechanics are this slice's property.

## G1 — import lifecycle runs, fails safely, resumes (`PG-EV-01`, `PG-EV-05`, `PG-EV-09`)

- `POST /v1/imports` creates a job (state `CREATED`) + links posted evidence ids + writes one step row per deterministic step above; `Idempotency-Key` header honored through the real idempotency table (pattern exists per `test_export.py:186-211` — verify, do not assume).
- `POST /v1/imports/{job_id}/run` executes pending steps inline in order, persisting per-step state/attempts/outputs; the first failing step parks the job in `FAILED` with the step error recorded; the catalog is unchanged by a failed run (commit step is atomic — a forced mid-run failure in tests must leave zero asset/evidence/assertion rows from that job).
- `POST /v1/imports/{job_id}/retry` resets `FAILED` steps to `RETRYING` and re-runs to completion; double-`run` and double-`retry` are idempotent (no duplicate step rows, no duplicate side effects).
- `GET /v1/imports/{job_id}` returns job state + ordered steps + progress counts + errors; cross-household access is 403 on all four routes (pattern exists in `jobs.py:40-48`).
- Fail-first: the new tests run against pre-change code first (expect 404s), both runs quoted in the committed log — a gate never seen to fail is not a gate. Audit rows cover job create + state transitions (verify against `backend/app/services/audit_service.py` — read it, do not assume its interface).

## G2 — migration verdict as a goal, not an assumption (`PG-SC-03`)

- Assess whether `job`/`job_step` as they stand carry everything G1 persists (step error text, terminal timestamps, run outputs). **Stopping is a SUCCESS if the tables suffice: report `no-migration-needed` with the column-by-column mapping and skip the rest of G2.** Stopping because a migration "feels cleaner" or because Alembic tooling is unfamiliar does NOT count as grounds to stop.
- If and only if a column is genuinely missing: add exactly one revision (BM-5), exercised `upgrade head` + `downgrade -1` + `upgrade head` against a temp SQLite database in tests, and keep the SG-011 `db_revision` export mechanism green (run `test_export.py` — the manifest head test is this slice's regression guard for the migration path).

## G3 — `GET /v1/jobs` returns real items (`PG-SC-02`)

- Trace the read-back route already computed in `jobs.py:19-36` and return the serialized items through it (same cursor envelope); the SG-008 stub-shape test asserting `items==[]` must be updated to the real shape, fail-then-pass, with the old assertion quoted as the failing run. Keep the `/review_tasks` underscore alias untouched (not this slice's property).

## G4 — ADR-003 (job orchestration)

- `docs/adr/ADR-003-job-orchestration.md`: durable DB step state, retry/resume semantics, synchronous-runner choice with the future queue path named, every claim traced to file/line (SG-010 ADR discipline — an ADR describing absent code is a finding, not an ADR).

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-012.log` and `{{WORKLOG_DIR}}/SG-012_report.md`, first token `SG-012`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units.

## G6 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-012 | Report: docs/worklogs/SG-012_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/job_service.py` (new) + `backend/app/api/v1/jobs.py` + `backend/tests/test_import_jobs.py` (new; may extend `test_export.py` only for the head-regression leg) + at most one migration file iff G2 requires it + `docs/adr/ADR-003-job-orchestration.md` + `docs/worklogs` files + the G6 note mechanism. No frontend, no `.env`/restart/secrets/infra, no new runtime dependency, no AI/LLM/provider code anywhere. Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a new dependency, a second migration, a frontend change, or a production write. Recorded here once, not per criterion.
- Exclusions by rule, not literal: no route outside `/v1/imports*`, `/v1/jobs*`, and the G4/G5 document paths is created or modified (`PG-SC-05`); grep-gate the route decorators and report the match list.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs (quote file + test counts); every gate names the files it checked and its counts; a gate emitting no output is a FAIL, not a pass. mypy stays advisory — quote the count, fix nothing outside the ceiling.
- Budget: 120s per ordinary command, 600s per suite leg, 2100s overall — report actual-versus-budget with units (`PG-PR-06` containment: the 2100s bound comes from `RUN_BUDGET_S=2100` in the dispatch conf; the kill is real).
- Simplicity: verify before repairing; write no new checklist (`G-A7`). New constants (if any) are named settings, logged when they bind, never silent (`m0019` cap policy).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run — host paths and the note return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- `POST /v1/imports` → 201 with step rows persisted; `run` drives the job to `AWAITING_REVIEW` (stub step outputs) with per-step states/attempts quoted from the database, not the response alone.
- Injected step failure → `FAILED` with the error recorded and zero catalog rows from that job; `retry` → resumes to the pre-failure terminal state; double-run/double-retry create nothing twice.
- Same-key `POST /v1/imports` replays idempotently; cross-household reads/writes 403; audit rows exist for the job lifecycle.
- Migration question resolved by mechanism: either `no-migration-needed` with the column mapping, or one revision with temp-DB upgrade/downgrade quoted and `test_export.py` still green.
- `GET /v1/jobs` returns created jobs through the existing cursor envelope; old `items==[]` assertion replaced, fail-then-pass quoted.
- ADR-003 committed with file/line traces; worklog + report committed; notes ref carries the `Dispatch-ID: SG-012` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
