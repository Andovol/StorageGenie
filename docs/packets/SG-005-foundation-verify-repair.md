# SG-005 — Verify/repair Phase 0 foundation: truthful health, non-vacuous pytest, lint (Codex High)

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

**DATABASE: none. Restart: none.** All verification runs against temp SQLite / `TestClient` with an isolated storage root, or read-only against the live checkout. No prod-row writes; no service restart.

## Why this exists

The Phase 0 WIP on disk already implements plan Tasks 2–11 code paths (`backend/app` models/services/routers present per `git ls-files`; all Task 12–14 screens present under `frontend/src`), but `backend/tests` is empty, so `pytest` exits vacuous (5) and the foundation is unproven. The real gates are `ruff` + `TestClient` + a non-vacuous suite. This slice turns the unproven WIP into a green baseline before any CRUD/export slices — verify/repair, never rebuild (`BM-3`).

Prior reports' open UNCLEARs, answered here so they are not re-raised: the dispatch key is absent inside the confined run, so no Coder-side SSH checks exist in this slice (carried as a constraint, not a gap); `dispatch_coder.sh:72` names HealthyLaws inside a negative test — known, outside `finalize`, out of scope; the wrapper effort gate now defaults to medium and accepts `high` — this first `high` dispatch is its functional proof.

Expected conditions (verify, do not trust):
- `backend/app/db.py:18-25` sets `foreign_keys=ON` + `journal_mode=WAL`, with no `busy_timeout`
- `backend/Dockerfile:1,5` pins `python:3.12-slim` (unpinned patch) and installs with `pip install -e .`, no lockfile; only `frontend/package-lock.json` exists
- `frontend/package.json:10` lints with `eslint src --ext ts,tsx || true`
- `frontend/vite.config.ts:8-10` already proxies `/v1` to `:8000`; `backend/app/config.py:11-13` already carries `max_upload_bytes`, `allowed_mime_types`, `thumbnail_sizes`
- Alembic revision `0201cf10c56c` applied on the host DB; `pytest` currently vacuous; `mypy` advisory

## G1 — Truthful health and start/end delta (`CO-92`)

- Run `{{HEALTH_CMD}}` at start and end and report the delta. Attempt both the `curl` leg and the `TestClient` fallback, quoting both verbatim; on this shared host `curl :8000` is expected to hit a foreign 404, so green comes from `TestClient` against this checkout's own app.
- If `/v1/health` reports `"ok"` without actually probing DB + storage, that is a repair: make each leg real (failed leg → `"error"` + non-200 or honest body), verified by failing first (stop the DB path or point storage at a missing dir in a scratch config and show the leg going red, then restore).

## G2 — Non-vacuous pytest, full suite (`BM-3`)

- Add `backend/tests/test_health.py` (at minimum: `TestClient` health 200 + `status == ok`; plus a constraint test that fails pre-change if G1 repaired anything).
- Run the FULL backend suite — no node-ID list is handed over, so the conditional derived-test-set block is correctly absent. Every test uses a temp SQLite DB and an isolated temp storage root; prod paths (`/data/db/storagegenie.db`, `/data/storage`, `./data/`) are never touched. Any row the run creates outside temp space is reported with identifiers and left in place (`PG-EV-06`).
- `pytest` exiting 5 (no tests collected) after this slice is a FAIL, not a pass.

## G3 — Lint gates: `ruff` fatal, `mypy` + `eslint` advisory

- `ruff check .` clean — the gate. Quote the output; empty output with exit 0 is stated as such, never implied.
- `mypy app` reported advisory with its count (43 last seen — verify, do not trust); `eslint` status reported as-is. If `eslint` is already clean, drop the `|| true` in `frontend/package.json:10` (`TS-5`); if not, leave it and report the failure count — removal must be earned, never assumed.

## G4 — Migration state, no new migration unless repair (`BM-5`)

- State with observed values: Alembic head revision(s) in `backend/alembic/versions/` vs revision(s) actually applied to a scratch DB after `alembic upgrade head`. A mismatch is a finding with both hashes quoted.
- No new migration by default. Exactly one repair revision is permitted if and only if head-vs-applied diverges or the FK/WAL listener from `db.py` is not reflected in a fresh `upgrade head`; otherwise a new revision file is a FAIL. Never edit an applied revision.

## G5 — Small hardenings: `busy_timeout`, lockfile, image pin (`TS-1`, `TS-4`)

- `TS-1`: add `PRAGMA busy_timeout` (5000 ms, named in code, not a magic bare number — comment cites lock-wait semantics) to the existing `db.py` pragma listener. One line + comment; verified by observing the pragma on a fresh connection (`PRAGMA busy_timeout;` returns 5000).
- `TS-4`: commit a backend lockfile and pin the Dockerfile base (`python:3.12-slim` → pinned patch). Verify by rebuilding the dependency install from the lockfile in a clean step and quoting the pinned interpreter + base digest/tag observed.
- Nothing else in this goal. Pillow/EXIF work (`TS-2`, `TS-3`) belongs to the evidence slice, not this one.

## G6 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-005.log` and `{{WORKLOG_DIR}}/SG-005_report.md`, first token `SG-005`, every output path named in the report committed, three UNCLEAR lines at the end. The failing runs from G1 (if any repair occurred) are committed in the log, not only quoted in prose (`PG-EV-09`).

## G7 — Prefill the evidence ref, then auto-publish

- After WORK_HEAD is pushed to `automation`: `git push origin <WORK_HEAD>:refs/heads/storagegenie-evidence` (120s bound), then `git fetch origin refs/heads/storagegenie-evidence` and verify `git rev-parse origin/storagegenie-evidence` equals WORK_HEAD — quote both hashes. The publisher gates on this equality (`candidate_not_remote`); the prefill is what establishes it.
- Only then invoke `{{RECEIPT_CMD}}` with (`SG-005`, header `contract_sync=refresh version=0.17.2`, report path, WORK_HEAD), unmodified. A repair need is a finding, never a local patch to the wrapper.
- A `candidate_not_remote` from the unmodified publisher AFTER the verified prefill is a STOP — commit `BLOCKED`, push, report. Never hand-move the ref by other means and never force-push outside the publisher (`CO-54`).
- Verify the artifact, not the command: the evidence ref carries a commit with the `Dispatch-ID: SG-005` trailer — quote its hash. A zero-exit publish with no such commit is a FAIL.

## Constraints

- Scope ceiling: foundation verify/repair only — no asset/evidence/export/UI behaviour change, no expiry/LLM/OCR, no worker infra. Writes permitted: `backend/tests/test_health.py`, the G3–G5 repairs named above (plus at most one G4 repair revision), `docs/worklogs` files, and the G7 prefill/publish mechanism. Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure — say so here explicitly: disclosing an out-of-scope change does not authorize it).
- Cross-product (`PG-IC-01`): the G5 `db.py` one-liner alters connection setup, not product behaviour; the lockfile/Dockerfile pin alters build inputs, not runtime; no acceptance criterion below requires anything the ceiling forbids.
- No datastore writes outside temp space; accidental prod rows reported with identifiers and left in place.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs; no handed node IDs, so no derived-set block. Every gate names the files it checked and its match counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 600s for the suite + migration + rebuild steps, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run (honest and out of scope) — host paths and the prefill/publish return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- `{{HEALTH_CMD}}` start-vs-end delta reported with both legs quoted verbatim; any repaired leg demonstrated red-then-green with both runs committed in the log.
- `pytest` collects and runs `test_health.py` and the full suite is non-vacuous (exit 5 is a FAIL); all tests isolated to temp DB/storage, prod paths untouched (stated with the paths).
- `ruff` clean with output quoted; `mypy` + `eslint` counts reported advisory; `|| true` removed only on an observed-clean `eslint` run.
- Alembic head-vs-applied stated with observed values; zero or (iff diverged) exactly one new revision; no applied revision edited.
- Fresh connection reports `busy_timeout = 5000`; lockfile committed and install reproduced from it with pinned base observed.
- `docs/worklogs/SG-005.log` and `docs/worklogs/SG-005_report.md` committed; every output path in the report committed.
- `storagegenie-evidence` carries the `Dispatch-ID: SG-005` receipt commit; hash quoted; prefill equality quoted before publish.
- No criterion passed vacuously — an empty grep, an empty log, or a skipped leg is declared loudly, never a pass.

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite/migration/rebuild steps, 2100s overall (`TIMEOUT_S=2100` in wrapper).
