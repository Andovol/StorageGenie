# SG-001 — Host project setup and Coder boundary proof (grok, shared key)

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

**DATABASE: none.** Phase 0 is SQLite local (`sqlite:////data/db/storagegenie.db`) + `storage_data:/data/storage` — `{{PROD_DB}}` is `not applicable` per `AGENTS.md:30`. Tests use `TestClient` + temp SQLite.

## Why this exists

VPS at `/home/andrei/StorageGenie` was cloned `2026-09-02T11:57` from `origin/automation` (`dd95eec` `automation`) but has **no host-side setup**: no `venv`, no `.env`, no `alembic upgrade`, no `docker compose` config check, and the dispatch wrapper `/opt/storagegenie-dispatch/dispatch_coder.sh` was just provisioned with `grok` selected per `m0083`. **This slice is ONBOARDING.md step 5 — the first real post-cutover slice that proves the VPS Coder boundary on the configured Coder value.** It must run under the forced-command wrapper at `/opt/storagegenie-dispatch/dispatch_coder.sh` with `grok` + `medium` effort, prove the shared contract loaded, and leave the host project runnable for Phase 0 E2E.

Expected conditions (verify, do not trust):
- `git -C /home/andrei/StorageGenie branch --show-current` → `automation`, `git log --oneline -3` → `dd95eec` top, `AGENTS.md:4` → `0.17.2`, `VERSION` on host `/home/andrei/launcher/VERSION` → `0.17.2`
- `ls /opt/storagegenie-dispatch/dispatch_coder.sh` → `root:root 755` outside project tree, `DISPATCH_PATH` includes `/home/andrei/.grok/bin`, `ReadWritePaths` includes `~/.grok` + `~/.codex`

If any differ, investigate and explain — correcting me is worth more than agreeing.

## G1 — Host project becomes runnable (follow `reference/vps-info.md` New Project Checklist, VPS side)

- Create `/home/andrei/StorageGenie/.env` from template if absent (mind 600 perms): `DATABASE_URL=sqlite:////data/db/storagegenie.db`, `STORAGE_ROOT=/data/storage`, `HOUSEHOLD_DEFAULT_NAME=Popescu Household`, `CORS_ORIGINS=http://localhost:5173` — do not commit `.env`
- `python3 -m venv /home/andrei/StorageGenie/venv` if absent; `venv/bin/pip install -e backend` or `pip install -r backend/requirements` as applicable; prove `venv/bin/python -c "import fastapi; print(fastapi.__version__)"`
- `mkdir -p /data/db /data/storage` or `./data/db` per `docker-compose.yml:9-10` volumes — ensure `storage_data` named volume exists via `docker volume ls`
- Run `alembic upgrade head` in `/home/andrei/StorageGenie/backend` and prove `alembic current` → `0201cf10c56c` (single migration) and `sqlite3` tables include `household`, `asset`, `evidence`

## G2 — Coder boundary proof (every `{{NAME}}` from `AGENTS.md` Values table is bound, no placeholder literal per `CO-08`)

- Prove the shared contract loaded by quoting `CO-42` exactly: *"Restoring production from backup is an incident, never silent cleanup."* — this text lives in `global/CODER.md:0.17.2` on the dispatch host, read via the read-only copy at `/opt/storagegenie-dispatch/` (never from repo)
- The dispatch envelope must record `grok` + `medium` (no model id per `CODERS.md:59`); read model/effort from process args per identity line above
- The worklog at `{{WORKLOG_DIR}}/SG-001.log` and report at `{{WORKLOG_DIR}}/SG-001_report.md` are unconditional per `CO-57`
- No unresolved `{{NAME}}` in final prompt/receipt — every binding came from `AGENTS.md` Values table

## G3 — Health and confinement proof (host evidence, not self-report per `ONBOARDING.md:140`)

- Run `{{HEALTH_CMD}}` (`curl -s http://localhost:8000/v1/health` fallback `TestClient`) at start and end per `CO-92` and report delta
- Prove confinement applied: `sudo -n systemd-run` with `ProtectHome=read-only`, `ReadWritePaths` includes project root + `~/.grok` + `~/.codex`, `InaccessiblePaths` enumerated at dispatch time — show `systemd-run` line from wrapper and that `ls /home/andrei/pip` is refused inside confinement per wrapper `negative` test

## Constraints

- Scope ceiling: host setup only + boundary proof — no product behaviour change beyond making the project runnable; no schema change; no new expiry columns; no LLM/OCR
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per block above, not routed around
- Stash: worktree must end clean per `CO-55` — untracked `venv/`, `data/db/*.db`, `data/storage/` are gitignored
- Test scope: `ruff check app` + `mypy app` advisory (report, do not gate), `pytest -q` if tests exist, `npm test` frontend
- Budget: 120s per ordinary command, 300s for `pip install`/`alembic`/`npm ci` — state bound per command per hang bound
- Simplicity: follow `vps-info.md` checklist, do not write a second one (`G-A7`)

## Acceptance criteria

- `git -C /home/andrei/StorageGenie log --oneline -1` shows the packet commit `SG-001` is the base (`automation` head moved 0 or 1 if this slice commits a host-setup doc)
- `ls -l /opt/storagegenie-dispatch/dispatch_coder.sh` → `root:root 755`, `DISPATCH_PATH` contains `/home/andrei/.grok/bin`, `ReadWritePaths` includes `~/.grok` + `~/.codex` per `PROVISIONING.md:137-139`
- `cat /home/andrei/StorageGenie/.env` exists `600` (redacted in report) and `venv/bin/python -c "import fastapi"` succeeds
- `alembic current` → `0201cf10c56c` and `sqlite3 /data/db/storagegenie.db ".tables"` or `TestClient` shows `household` table
- Report quotes `CO-42` exactly and states model/effort from process args (or `unknown` per identity line)
- `{{HEALTH_CMD}}` start vs end delta reported per `CO-92`
- Worklog `docs/worklogs/SG-001.log` and report `docs/worklogs/SG-001_report.md` committed and tracked in published commit per `CO-57` — every output path named in report is committed

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet's start HEAD (hash), `WORK_HEAD` = work commit hash (or `none` if NO-CHANGE per `CO-48` — this slice is expected `CHANGED` if it creates worklog, or `NO-CHANGE` if host already runnable)
- Publish receipt with `{{RECEIPT_CMD}}` (`/opt/storagegenie-dispatch/finalize_dispatch_report.sh`) to `refs/heads/storagegenie-evidence` with header `contract_sync=refresh version=0.17.2` per `AGENTS.md:29`
- State model/effort provenance per `CO-78` — never from system prompt

## Budget

120s ordinary, 300s for `pip install`/`alembic`/`npm ci`, 2100s overall (`TIMEOUT_S=2100` in wrapper)
