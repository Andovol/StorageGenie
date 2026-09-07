# SG-010 — Phase 0 exit: end-to-end proof + ADRs + runbook (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

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
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** All verification runs against temp SQLite / `TestClient` with an isolated temp storage root, following the pattern in `backend/tests/test_health.py`. No prod-row writes; no service restart.

## Why this exists

Phase 0's exit condition (`blueprint §14`): *manually catalog an item, attach source photos, search it, export a consistent backup.* Every leg is proved in isolation — SG-007 (CRUD, pagination, filters, provenance), SG-008 (manifest, restore round-trip) — but no single test walks all five legs against one fixture set, and the two ADRs plus the runbook that make the exit durable do not exist: `docs/adr/` is absent and `README.md` has no Phase 0 run instructions. `POST /v1/assets/{id}/evidence` is expected to exist (SG-007 exercised post-creation attach); if it does not, that is a finding with a wiring fix, not a redesign. Prior-slice answers carried forward: run gates with `/home/andrei/StorageGenie/venv/bin` (tools are not on PATH); contract files are absent on the host, so all context is embedded here; a non-fast-forward work-branch push resolves by content-neutral merge per CO-54, never force-push. Baseline: backend suite 23 passed (SG-008, re-proved SG-011), `ruff` clean, `mypy` 43 advisory repo-wide (the `:95` instance closed by SG-011, out of ceiling).

## G1 — Exit E2E, committed test first

- Add `backend/tests/test_phase0_e2e.py::test_phase0_exit_condition`: on one temp fixture household — (1) create asset manually → 201; (2) upload JPEG evidence and attach via `POST /v1/assets/{id}/evidence` → 200; (3) `GET /v1/assets?q=<name>` returns the asset; (4) `GET /v1/export` manifest contains the asset id AND the evidence id; (5) asset detail shows the evidence item and a `display_name` assertion with provenance. Each leg asserts against the ids created in leg 1–2 — replaying fixed ids from another run is vacuous.
- Fail-first against the unmodified tree (quote the run); pass after wiring. If all five legs pass unmodified, the result is "already passed, hardened" — still a success, still committed.

## G2 — ADRs (durability, not decoration)

- `docs/adr/ADR-001-local-first-storage.md`: SQLite WAL + local FS outside web root now, Postgres+S3 later via the same SQLAlchemy/Alembic path; what was decided, what was deferred, and the migration-path test that keeps it honest.
- `docs/adr/ADR-002-evidence-provenance.md`: immutable evidence, assertion review-state chain, audit on every write; plus the deferred-table recipe (`observation`, `identifier`, `classification`, `location`, `lifecycle_event`, `asset_relation`) documented as future tables, never Phase 0 columns.
- Each ADR states its decision, its deferred alternatives, and the file/line that pins it. An ADR describing code that does not exist is a finding, not an ADR.

## G3 — Runbook + trust note

- `README.md` gains Phase 0 run instructions: prerequisites, `docker compose up`, migration + seed, health check with expected output, how to run backend and frontend suites, where data lives and why it is gitignored.
- The runbook carries the `BM-8` trust-boundary note verbatim in meaning: LAN-only, single household, no auth in Phase 0 — household scoping is namespacing, never security.
- Verify the runbook by reading it against the tree (every command named exists, every path named exists) — a runbook that was never checked against reality is documentation debt, reported as such.

## G4 — Duration measurability (`UV-5`, no new code)

- From the E2E fixture's own `audit_event` rows, compute `asset-accepted minus asset-created` durations and assert they are present, ordered, and non-negative — proving the §2.3 time-to-first-asset target is measurable on existing timestamps. No new columns, no new endpoints; a duration that cannot be computed is a finding about the audit writes, fixed only inside the audit path if a test proves it broken.

## G5 — Full suite + lint gates

- `pytest` full backend suite non-vacuous (exit 5 is a FAIL); `ruff check` on app + tests clean with output quoted and match counts named; `mypy` advisory count reported, not gated. Fail-then-pass runs for any repair committed in the log (`PG-EV-09`).

## G6 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-010.log` and `{{WORKLOG_DIR}}/SG-010_report.md`, first token `SG-010`, every output path named in the report committed, three UNCLEAR lines at the end.

## G7 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-010 | Report: docs/worklogs/SG-010_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/tests/test_phase0_e2e.py`; `docs/adr/ADR-001*`, `ADR-002*`; `README.md`; audit-path lines only where G4 proves breakage; `docs/worklogs` files; the G7 note mechanism. No other product file changes, no migrations, no frontend, no expiry/LLM/OCR, no `.env`/restart/secrets. Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a migration, the evidence service, or a restart.
- No datastore writes outside temp space; accidental prod rows reported with identifiers and left in place (`PG-EV-06`).
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs; every gate names the files it checked and its match counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 600s for the suite, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run — host paths and the note return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- One committed E2E test walks create → attach → search → export → provenance on a single fixture set, fail-then-pass quoted (or "already passed, hardened" with the passing run quoted).
- ADR-001 and ADR-002 committed, each tracing its claims to existing files/lines, deferred tables documented as recipe.
- README run instructions + BM-8 note committed and checked against the tree.
- Audit durations computable from the E2E rows, ordered and non-negative, with no new schema.
- `pytest` full suite green and non-vacuous; `ruff` clean quoted; `mypy` count reported advisory.
- `docs/worklogs/SG-010.log` and `docs/worklogs/SG-010_report.md` committed; every output path in the report committed.
- the notes ref carries the `Dispatch-ID: SG-010` + `Report:` note on the work HEAD; note quoted; dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
