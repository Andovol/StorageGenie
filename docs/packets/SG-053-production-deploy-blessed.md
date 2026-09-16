# SG-053 — production deploy with blessed row counts (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D70 production deploy (owner-approved 2026-09-16), second attempt after SG-052's correct STOP: the stop's trigger (real rows beyond seed) is reissued here as an EXPLICIT blessed set, because the rows are the owner's own live pass. Same D69 live-write authority carries over (rebuild + restart of the production stack ONLY). No code changes, no migration (verified again in-slice, see G1). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; compose/buildx print exit 0 even on build failure — output TEXT is the verdict source, never the exit code (SG-024); rootless docker is the runtime, project-local `BUILDX_CONFIG` route stands (SG-023/024); **AI stays OFF**: no provider calls, **$0 metered**; frozen prompts read-only. **Live-write authority (D69+D70, owner 2026-09-16):** `docker compose up --build -d` + one idempotent re-`up` against the production stack ONLY. Any database write, any other unit/restart, any host file outside the lane → STOP.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-08` before-observable · `PG-EV-09` both-runs-committed · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-08` expectation-bounds · `PG-IC-09` premises-live · `PG-PR-01` capability-model · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-goes-live · `PG-PR-06` runtime-vs-budget · `PG-PR-10` which-db-and-grant · `PG-DP-01` delivery-by-delivery-path · `PG-DP-04` two-consecutive-runs.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary probes, 1800s build+up leg, 300s migrate-check (read-only). A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: read-only probes + blessed-count comparison — NO migrate, NO seed, NO writes. Restart: the compose stack ONLY (D69+D70). NETWORK: registry pulls for the build + app API only.**

## Why this exists

SG-052 stopped at its own seed-only tripwire although the "unexpected" rows are the owner's directed live pass (Toothpaste import, 2026-09-15). This slice reissues the gate with the blessed set stated, then performs the identical rebuild + restart + prove sequence. The live site still serves the SG-041 image.

## G1 — pre-state quoted, blessed counts compared (`PG-EV-08`, `PG-IC-08` both directions, `PG-PR-10`)

- Stack state: `docker compose ps`, `ss -ltnp` (expect `127.0.0.1:8003` only), `curl -s http://127.0.0.1:8003/v1/health` (quote), `curl -s http://127.0.0.1:8003/` → quote the served asset hash (SG-052 recorded `/assets/index-khM4mS2k.js` — re-verify, never inherit).
- DB read-only (`sqlite3 -readonly` or equivalent, never a writer): `alembic current` MUST equal head `20260914_sg035_foundations` with no pending migration, else STOP (unapproved).
- **Blessed counts (embedded — the F-SG052-5 fix):** households ≥1 incl. the SG-041 seed household · users = 2 (seed) · assets = 1 (`Toothpaste`) · evidence = 1 (upload) · assertions = 3 (`source_type=user`) · audit events = 3 (`evidence.create`, `asset.create`, `asset.accepted`). Compare EXACTLY: equal → proceed; ANY difference in either direction (new owner rows since, or missing rows) → STOP and report the measured counts (`PG-IC-08`: an under-count speaks as loudly as an over-count). Record the running image id.
- Rationale stated in the report: the rebuild is DB-neutral (bind-mounted SQLite, no entrypoint migrate/seed, no lifespan writes per SG-052 F-SG052-3), so blessed rows are never at risk from the restart; the gate exists to catch rogue state, not owner use.

## G2 — build + up (the D69+D70-authorised mutation)

- `docker compose up --build -d` (rootless; BUILDX_CONFIG route; 1800s bound) — build TEXT quoted; a build failure is read from the output text, never exit 0. No `--profile dev`.
- One idempotent second `up -d` proving no restart loop (`PG-DP-04` shape). New image id quoted; `docker stats --no-stream` one memory sample.

## G3 — the new tree proven live, by value

- `curl -s http://127.0.0.1:8003/v1/health` → exactly `{"status":"ok","db":"ok","storage":"ok"}`.
- `curl -s http://127.0.0.1:8003/` → `200 text/html` with `<div id="root">` AND a hashed asset reference DIFFERENT from the G1 hash (before/after pair, both raw committed, `PG-EV-09`).
- Wardrobe markers greppable in the served bundle: `sg-theme`, `Product results`, `Import assets` (quote the matching lines).
- `ss -ltnp` → 8003 on `127.0.0.1` only, no `0.0.0.0`/`::` listener for 8003/8000/5173.
- Gate intact from the outside (no credentials, none used): `https://storagegenie.dynv6.net/v1/health` → `401`; `http://` → `301`. Differ → STOP and report (nginx outside this slice; do not touch it).
- `PG-EV-01`: feed one check a deliberately wrong expectation in the same run (e.g. assert the OLD asset hash post-change) and show it failing.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-053.log`, `{{WORKLOG_DIR}}/SG-053_report.md`, `{{WORKLOG_DIR}}/SG-053_verify.log` (before/after captures raw, gate-failure demonstration raw). First token `SG-053`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); live-state ledger (image ids old→new, zero DB writes, network = build pulls + API checks); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** NO tree files except `docs/worklogs` (3 files). **This slice changes zero product files** — any product diff is a STOP (deploy-only). Worklogs carry all evidence.
- Live-write authority is exactly: the compose build + up + re-up (D69+D70). Nothing else writes.
- Cross-product (`PG-IC-01`): G1 reads state; G2 the stack commands; G3 the served observables; G4 worklogs. No new exclusion issued.
- `PG-IC-03`: no remediation step shares a condition with a stop-gate — stops win, stated not assumed.
- Test scope: no suite re-run is ordered (zero product delta since SG-051's green — stated, not skipped-silently); verification is the live observables vs G1 baselines. Gates name values checked; silent gates FAIL.
- Budget (uncalibrated per `G-A9`): 120s ordinary probes · 300s migrate-check · 1800s build+up leg · **2100s early-close** · **2700s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): build + up + prove; nothing else.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); BASE == the pushed tip carrying SG-051 (verify `HEAD == origin/automation`, else STOP — deploying anything but the audited tip is forbidden).
- Blessed counts compared exactly (equal → proceed; else STOP with measured counts); no-migration-need proven; pre-state health + hash + listeners quoted.
- Post-change health exact JSON; new asset hash different from pre-state; wardrobe markers quoted from served bytes; loopback-only proven; gate 401/301 proven; second `up -d` provokes no restart; memory sample quoted.
- Gate seen failing (wrong-expectation demonstration quoted); artifact checked is the SERVED response, never an exit code (`PG-EV-02`); properties stated as values (`PG-EV-05`).
- No product-file diff; no DB write; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = worklog commit hash. Model/effort per `CO-78` from process arguments. Live-state ledger: image ids old→new, zero DB writes, live spend `$0`, network = build pulls + API checks.
- **Receipt note on the notes ref (M20-corrected block):** push the worklogs to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-053 | Report: docs/worklogs/SG-053_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (`<ref>:<ref>`, M21 — a bare fetch never updates a notes ref), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary probes · 300s migrate-check · 1800s build+up leg · 2100s early-close · 2700s overall; $0 metered; actual-versus-budget per leg with units.
