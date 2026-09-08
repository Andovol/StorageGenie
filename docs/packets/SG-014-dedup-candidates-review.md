# SG-014 — Deduplication, candidates, review decisions, lifecycle events (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 slice 3 of 7 (plan `docs/superpowers/plans/2026-09-08-phase-1-deterministic-import.md`, D9, D10 resume). SG-013 landed (`1dc63ec2`, rated 90): observations are written and readable via `get_observations` (`backend/app/services/signals.py:47-52`); NOTHING consumes them yet. This slice fills the `DEDUPLICATING` and `COMMITTING` bodies in `execute_step` (`backend/app/services/job_service.py:105-116` shape) and makes the review queue real.
**Carries from audit (do not re-derive, do verify):** (a) ADR-003 lines 41 and 51 still say `no-migration-needed` — now stale since SG-013 added the `observation` revision; amend exactly those lines here (smallest diff that tells the truth; the rest of ADR-003 is untouched). (b) Established SG-013 behavior, stated as premise: PDF evidence quarantines at `EXTRACTING` (media gate in `signals.py:82-88`) — candidates never see PDFs; PDF rendering belongs to a future slice, not this one. (c) ISS-1: tesseract/zbar absent in-sandbox — dedup tests MUST hand-insert observation rows (pattern exists in `test_signals.py:210-212`) and must never depend on the real decoders.

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

**DATABASE: none live. Restart: none.** One Alembic revision is authorised (the `candidate` table below); exercised `upgrade head` + `downgrade -1` + `upgrade head` against temp SQLite only (`PG-PR-04`: the running service is not touched; all proof in-process via `TestClient` + temp DBs). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): finish inside 2100s, report elapsed against it. Coder-side `python`/`pytest` are absent on the host PATH — name `venv/bin/` binaries explicitly.

## Why this exists

Imports extract signals and stop at review with no policy and no commit: duplicate bytes, near-duplicate photos, and identifier collisions have no defined outcome, and `GET /v1/review-tasks` still returns `{"items": [], ...}` (`backend/app/api/v1/review_tasks.py:36`). Handed facts that shape the design (verify each): upload already dedups bytes — `evidence_service.py:210-215` returns the existing row on SHA collision, so "exact duplicate" at job level means an import referencing evidence already linked to an asset in this household (via `asset_evidence`, pattern in `assets.py:50-55`), and the correct outcome is a candidate proposing the EXISTING asset, never a second asset for the same bytes. Commit building blocks exist — `create_asset` (`asset_service.py:12-66`, asset + per-field assertions + evidence links + `asset.create`/`asset.accepted` audit, one commit), `attach_evidence` (`:98-115`, INSERT with duplicate tolerance), `audit_service.record` (`audit_service.py:9-31`, explicit kwargs). Assertion columns are `field_path/value_json/source_type/confidence/review_state/source_evidence_ids/model_json` (`models/assertion.py:8-21`); identifier convention (`field_path` = `identifier`?) is UNVERIFIED — check `test_assertions.py`/`test_assets_crud.py` for an existing convention; if none exists, establish `identifier` and record it in ADR-006 rather than assuming.

## G1 — duplicate policy enforced, never auto-merged (`PG-EV-01`, `PG-EV-05`, `PG-EV-09`)

- New `backend/app/services/dedup.py` feeding the `DEDUPLICATING` step body: exact-SHA-linked evidence → candidate marked `duplicate_of_asset` (link proposal, no new asset); dHash distance at or under the named `dhash_near_threshold` setting (`config.py`, SG-013) against this household's existing `phash` observations → `similar` suggestion (advisory); validated `barcode_qr` observation value equal to an existing identifier assertion value in this household → review task, commit blocked. NOTHING auto-merges serialized items — a test asserting "no merge path exists" (grep-gated: no UPDATE of another asset's rows from this module) is the property.
- Semantic similarity is explicitly absent (Phase 2+); multi-object split/merge required by ambiguous scenes returns a review task, not a guess (blueprint §5.2-5).

## G2 — candidates decided, commits atomic, queue real (`PG-SC-02`, `PG-EV-01`)

- Exactly one migration: `candidate` (`job_id` FK, `evidence_ids_json`, `proposed_fields_json`, `state` in {proposed, accepted, edited, held, rejected}, household FK). Assess `review_task` columns (`subject_ref/proposed_change/status/task_type/priority`, `models/review_task.py:8-19`) FIRST — if they cannot carry duplicate/identifier/manual-entry tasks, STOP that leg (`PG-SC-03`); a second migration is not authorised.
- `POST /v1/candidates/{candidate_id}/decision` with actions accept / edit (with corrected fields) / hold / reject: accept/edit runs the `COMMITTING` step body creating asset + assertions (`source_type=deterministic`; `review_state=accepted` for machine-safe fields, `proposed` for identifiers/expiry per blueprint §5.2-7) + evidence links + initial lifecycle event **in one transaction** — a forced mid-commit failure must roll back all four writes and leave the job retryable (quote the rollback proof). Reject/hold set state only. `GET /v1/review-tasks` returns real items through the existing cursor envelope (same repair shape as SG-012's `GET /v1/jobs`; the SG-008 empty-list assertion is updated fail-then-pass); `POST /v1/review-tasks/{task_id}/resolve` closes with audit rows; household 403s throughout; the `/review_tasks` alias keeps working.
- Minimal `POST /v1/assets/{asset_id}/events` (the lifecycle leg deferred since Phase 0): record the event as an `audit_event` row (action `asset.lifecycle.<type>`) — NO new table — read back through the existing asset-detail audit history (`PG-SC-02` trace: write route → detail history). Full event-history UI stays out.
- Fail-first with both runs in the committed log; SG-012/SG-013 suites stay green (no seam regression).

## G3 — ADR-006 + ADR-003 amendment

- `docs/adr/ADR-006-duplicate-policy.md`: exact/perceptual/identifier/semantic rules, merge-never rule, identifier convention established above, every claim to file/line. Plus the carried one-line-class amendment to ADR-003:41,51 (`no-migration-needed` → observation revision named). No other ADR touched.

## G4 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-014.log` and `{{WORKLOG_DIR}}/SG-014_report.md`, first token `SG-014`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units.

## G5 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-014 | Report: docs/worklogs/SG-014_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/dedup.py` + `backend/app/services/candidates.py` (new; one module only if the split earns it) + `backend/app/services/job_service.py` (DEDUPLICATING + COMMITTING bodies only — EXTRACTING body untouched) + `backend/app/api/v1/review_tasks.py` + `backend/app/api/v1/assets.py` (events route only) + new candidates route file or jobs-router extension (your call, record why) + `backend/tests/test_dedup.py` + `backend/tests/test_candidates.py` (new; may extend `test_export.py` only for the stub-assertion leg and `test_import_jobs.py` only for the step-body legs) + one migration file + `docs/adr/ADR-006-duplicate-policy.md` + ADR-003:41,51 amendment lines + `docs/worklogs` files + the G5 note mechanism. No frontend, no new runtime dependency, no `.env`/restart/secrets/infra, no AI/LLM/provider code. Anything else is a STOP ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a second migration, a worker, a frontend change, or a production write. Recorded here once, not per criterion.
- Exclusions by rule: no route decorator outside `/v1/imports*`, `/v1/jobs*`, `/v1/review-tasks*`, `/v1/candidates*`, and the single `/v1/assets/{asset_id}/events` route is added or modified (`PG-SC-05`); grep-gate the decorators and report the match list.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs (quote file + test counts); every gate names the files it checked and its counts; a gate emitting no output is a FAIL. mypy stays advisory — quote the count, fix nothing outside the ceiling. Decoder-dependent tests are FORBIDDEN in this slice (ISS-1) — hand-insert observations; a test importing pyzbar/pytesseract fails review.
- Budget: 120s per ordinary command, 600s per suite leg, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`). New constants (if any) are named settings, never silent (`m0019`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- Re-import referencing asset-linked evidence proposes the existing asset; zero new asset rows; the proposal names the asset id (identity, not counts — `PG-SC-09`).
- Near-duplicate pair (dHash at/under threshold, fixtures generated as in `test_signals.py:170-187`) yields a `similar` suggestion and still permits independent commit; far pair yields none.
- Identifier collision opens a review task and the commit path refuses until resolution (prove the refusal, not just the task).
- Accept-commit creates asset + assertions + evidence links + lifecycle audit atomically (four-way row proof from the database, not the response); forced mid-commit failure rolls back all four and the job retries to completion.
- `GET /v1/review-tasks` returns created tasks through the cursor envelope; old `items==[]` assertion replaced fail-then-pass; resolve closes with audit rows; cross-household 403s; alias intact.
- Events route appends `asset.lifecycle.*` audit rows visible in asset detail history.
- One migration with temp-DB upgrade/downgrade quoted; `test_export.py` head test green; SG-012 + SG-013 suites green (decoder legs excluded per ISS-1 — name the excluded node IDs explicitly so the exclusion is visible, `PG-DP-02` in-spirit for sandbox-blocked legs).
- ADR-006 committed with traces; ADR-003:41,51 amended truthfully; worklog + report committed; notes ref carries the `Dispatch-ID: SG-014` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
