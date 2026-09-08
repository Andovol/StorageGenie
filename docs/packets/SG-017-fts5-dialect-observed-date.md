# SG-017 — FTS5 search + Postgres-dialect CI check + observed-date kind scope (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 slice 6 of 7 (plan `docs/superpowers/plans/2026-09-08-phase-1-deterministic-import.md`, D9, D10 resume). SG-016 landed (rated 97): UI complete, backend suites green except ISS-1. This slice is backend-only: ranked search structure, migration-path honesty, and one audit-queued correctness repair.
**Carries (verify, do not re-derive):** ISS-2 — `_observed_date` (`backend/app/plugins/expiry_tracker.py:244-264`) regex-scans ALL observation kinds, so an EXIF capture date reads as an expiry candidate. ISS-1 decoder legs stay carried to the manual compose pass (no test here imports pyzbar/pytesseract or depends on real decoders). A "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination (standing SG-014 lever line).

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
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (Effort is proven readable from process arguments — do the same.)

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

**DATABASE: none live. Restart: none.** One Alembic revision is authorised (the FTS5 table + triggers + backfill below); exercised `upgrade head` + `downgrade -1` + `upgrade head` against temp SQLite only (`PG-PR-04`: the running service is not touched; all proof in-process via `TestClient` + temp DBs). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): finish inside 2100s, report elapsed against it. Coder-side `python`/`pytest` are absent on the host PATH — name `venv/bin/` binaries explicitly.

## Why this exists

Catalog search is an ILIKE full-scan (`assets.py:130-131`, verified this session) with household/type/status/evidence filters and a `(created_at, id)` cursor envelope (`assets.py:129-178`). That will not hold the §2.3 <300 ms target at ~10k assets, and UV-2 moved deterministic FTS into Phase 1. Separately, ADR-001 promises a Postgres migration path that nothing checks (BM-4, unlanded since Task 1), and the SG-015 audit caught EXIF timestamps feeding expiry candidacy (ISS-2). Three small backend legs, one slice, no UI.

## G1 — FTS5 narrows, existing ordering/pagination unchanged (`PG-EV-01`, `PG-SC-02`)

- Exactly one migration: FTS5 external-content table over `asset` (`asset_id`, `display_name`, `household_id`) + insert/update/delete sync triggers + backfill of existing rows via a named, re-runnable function (also callable post-migration — name it in the report).
- `q` path: sanitize the user string for FTS5 MATCH syntax FIRST (quotes, `OR`/`AND`/`NOT`/`NEAR`, asterisks, unbalanced quotes must become literals, never operators — prove with hostile inputs incl. `" OR "1"="1` and an unterminated quote), then MATCH-narrowed asset ids ANDed with the existing household/type/status/evidence filters. Ordering and cursor pagination stay EXACTLY `(created_at desc, id desc)` — relevance ranking is explicitly NOT introduced (reason recorded: rank cursors break the envelope; revisit only on evidence with Phase 4 facets).
- ILIKE fallback: keep the ILIKE path for the empty-`q` case only (no `q` ⇒ no MATCH); `q` present ⇒ FTS. If any existing both-polarity filter test cannot be satisfied through FTS, report it as a finding with the exact test id — do not silently dual-run both.
- Read-back trace (`PG-SC-02`): the `q` result rows flow through the unchanged serializer; extend `test_search.py` (both polarities stay green) with FTS-specific legs: multi-token match, hostile-syntax literal treatment, household isolation THROUGH the FTS path (a same-named asset in another household must not leak — identity assertion, `PG-SC-09`), and rebuild-function verification (delete FTS rows → rebuild → matches return).
- Fail-first with both runs in the committed log (`PG-EV-09`).

## G2 — 10k-fixture latency check (`G-A3` honesty, `PG-EV-05`)

- Seed 10,000 assets (+ evidence links on a subset) in a temp database and measure `GET /v1/assets?q=` wall time distribution; report p50/p95 with the machine named (it is one run on shared hardware — say so, do not present it as a rate). Target: p95 < 300 ms per §2.3. A miss is a finding with the measured numbers and the query plan (`EXPLAIN QUERY PLAN` quoted), not a re-design inside this slice.

## G3 — BM-4 Postgres-dialect compile check, offline

- New `backend/tests/test_postgres_dialect.py`: compile every metadata table (`Base.metadata.tables`, enumerated in the test — a handed list is not allowed to drift silently, so the test asserts its own table inventory against `metadata.tables` first) with the Postgres dialect to DDL strings, no server, no driver, no network. The SQLite-only FTS migration is EXCLUDED by rule with the reason in the module docstring (FTS5 has no Postgres equivalent; ADR-008 records this) — exclusion by rule with the uncovered file named, never a silent skip.
- `Makefile`: add a `check-postgres-dialect` target running exactly that file; ALSO drop the stale `|| true` on the frontend lint line (`Makefile:16` — TS-5 follow-through: frontend lint is green since SG-009, the mask is decoration). Both Makefile lines proved by running them.
- Deliverable: ADR-008 (deterministic FTS first; semantic/vector criterion; FTS↔Postgres divergence recorded).

## G4 — ISS-2 observed-date kind scope (bounded repair leg)

- `expiry_tracker.py::_observed_date` ONLY: restrict candidate scanning to `kind IN ('ocr', 'barcode_qr')` (visible content per blueprint §5.2-3); EXIF (and any future non-visible kind) never feeds expiry candidacy. Nothing else in the file changes.
- Regression test: an asset whose ONLY date-bearing observation is EXIF-kind with a valid date classifies to `needs_evidence` (not `proposed`); an OCR-kind observation with a date still proposes with evidence linkage. Both legs fail-then-pass quoted.
- SG-015 suite stays green (no behavior change for OCR/barcode paths — prove, don't assert).

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-017.log` and `{{WORKLOG_DIR}}/SG-017_report.md`, first token `SG-017`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units. State model/effort provenance from process arguments.

## G6 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-017 | Report: docs/worklogs/SG-017_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/api/v1/assets.py` (`q` path only — filters/envelope/serializer untouched) + FTS helper module iff the split earns it (else inline, record why) + `backend/tests/test_search.py` (extend) + `backend/tests/test_postgres_dialect.py` (new) + `backend/tests/test_plugin_expiry.py` (ISS-2 regression leg only) + `backend/app/plugins/expiry_tracker.py` (`_observed_date` ONLY) + one migration file + `Makefile` (two lines: new target + lint unmask) + `docs/adr/ADR-008-search.md` + `docs/worklogs` files + the G6 note mechanism. No frontend, no new runtime dependency, no `.env`/restart/secrets/infra, no AI/LLM/provider code, no semantic search, no facets/saved searches (Phase 4). Anything else is a STOP ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a second migration, a worker, a frontend change, or a production write. Recorded here once, not per criterion.
- Exclusions by rule: no route decorator outside the existing `/v1/assets` GET is added or modified (`PG-SC-05`); grep-gate and report. No new `source_type` or `review_state` value is minted anywhere.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs (quote file + test counts); every gate names the files it checked and its counts; a gate emitting no output is a FAIL. mypy stays advisory — quote the count, fix nothing outside the ceiling. Decoder-dependent tests FORBIDDEN (ISS-1 — the two node IDs named if excluded).
- Budget: 120s per ordinary command, 600s per suite leg (the 10k seed leg may approach this — report actuals), 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`). New constants are named settings, never silent (`m0019`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- FTS migration with temp-DB upgrade/downgrade/rebuild quoted; `test_export.py` head test green.
- `q` matches multi-token queries, treats hostile MATCH syntax as literals (quoted hostile inputs), isolates households through the FTS path (identity assertion), keeps all existing filter/cursor tests green with ordering unchanged.
- 10k-fixture p50/p95 quoted with machine named; miss handled as measured finding with query plan, not a redesign.
- Dialect test inventories its own tables, compiles all non-FTS DDL offline with zero server; FTS exclusion rule documented; Makefile target + lint unmask both run green.
- ISS-2: EXIF-only-dated asset → `needs_evidence`; OCR-dated asset → `proposed` with linkage; SG-015 suite green; diff to `expiry_tracker.py` confined to `_observed_date` (prove by diff).
- ADR-008 committed with traces; worklog + report committed; notes ref carries the `Dispatch-ID: SG-017` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — from process arguments (proven readable), never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
