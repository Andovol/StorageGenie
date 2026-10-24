# SG-251 — Close-deploy rider: serve SG-250 live, prove the served bytes, and report which providers the served registry holds

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It serves the SG-250 delta and writes its own evidence files. Nothing outside `{{WORKLOG_DIR}}` is committed.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE:** read-only only — the table census below, no write, no migration.
**Restart: one recreate of the backend container, as the standing rider does.**
**Provider: none.** No provider is called, no key is read or printed, **no spend**. Target: **$0**.

## Why this exists

The owner closed the session after SG-250 was audited, and the project's close-out rule is that every
app-changing slice is deployed as its own slice, right after it is rated, and the live app is deployed before
every close. SG-250 changed the app's cost behaviour, so it must be served — and the serve is where the change
becomes observable.

## G0 — Socket first, and the pre-state

**Before any docker command:** export the lane's socket and prove it answers — `docker version` must print a
**Server** section. A docker command before that is a protocol slip; report it if it happens.

Then record the pre-serve state: the running container's id and image id, its command, restart count and
health, the schema head, and the **census of all tables** (read-only). The `provider_call` count matters: this
slice changes what the app records about a call, and the count before and after must not move.

## G1 — ONE build, ONE recreate

- One `docker compose build backend` (rc=0). **If the build is cache-satisfied, do not assume the image is
  current — compare the image's Python tree against the worktree** (the SG-240/SG-241 precedent) and report the
  result.
- One recreate of the backend container (rc=0): the new container's id, its image id, `Cmd`, restart count and
  health.
- **No migration.** The alembic head must stay `20261023_sg233_reminder`; report the head before and after.
- Health: `{{HEALTH_CMD}}` at the start, at least six times after the recreate, and at the end — each answer
  quoted.

## G2 — The served bytes are SG-250's, and nothing else

- **The runtime diff** between the pre-serve image and the worktree, measured over the served Python tree: it
  must be **exactly SG-250's product files** — `backend/app/api/v1/enrich.py`, `backend/app/api/v1/settings.py`,
  `backend/app/config.py`, `backend/app/services/analytics/service.py`, `backend/app/services/chat/service.py`,
  `backend/app/services/enrich/snapshots.py`, `backend/app/services/enrich/synthesize.py`,
  `backend/app/services/planning/service.py`, `backend/app/services/providers/fake.py`,
  `backend/app/services/providers/opencode_go.py`, `backend/app/services/providers/protocols.py`,
  `backend/app/services/providers/reader.py`, `backend/app/services/providers/router.py` — and **nothing else**
  (`backend/eval/run.py` is not runtime). Any extra or missing file is a finding, not a detail.
- **The frontend bundle** must be **byte-identical** to the pre-serve bundle (SG-250 changed no frontend byte):
  `index.html`, the JS and the CSS, with their hashes and sizes quoted.
- The served tree must equal the worktree after the build (`diff` rc=0).

## G3 — What the app now does about cost, in the served bytes

Prove, from the **served image's own files** (not the worktree's):

1. **The prediction is gone from the served code** — the served `providers/opencode_go.py` contains no
   `estimate_call_cost` and no `estimate_cost`; the served `providers/router.py` has no `cost_budget` and its
   `execute` takes no cost argument; the served `providers/reader.py` has no `_estimate_call` and no
   `_recorded_spend`; the served `config.py` declares no `sg_per_job_cap` and no `sg_monthly_cap`. Quote the
   greps.
2. **The cost line is in the served code** — the served `providers/opencode_go.py` contains the log call and its
   format string, and the served `providers/opencode_go.py` still computes the **post-call** cost from the
   response's real usage. Quote the lines.
3. **The app boots on the new configuration** — the startup log must contain no configuration error and no
   traceback. `extra: "ignore"` means a leftover `SG_PER_JOB_CAP` in the host's environment cannot break
   startup; **state that** rather than reading the environment.

## G4 — Which providers the served app holds (ids only — never a key, never a value)

Report the **provider ids the served app's registry holds** and nothing else: the ids, the count, and whether
the real provider is among them. This is a set of **names**, read from the running app's own settings — **no key
value is read, printed, hashed or transmitted**, and no `.env` file is opened.

**Why it matters:** the cost line is emitted by the `opencode-go` adapter, so the line appears in the served
app's log only when a real provider is in use; a keyless app uses the `fake` double and logs nothing. The owner
must be told which case the served app is in — **as a measured fact, not an assumption**.

## G5 — The honest limit: the cost line's live appearance is NOT claimed

The line can appear in the served container's log only when a **real provider call** happens, and this slice may
not make one (no consent, no key, no spend authority). So:

- **Do not** claim the line appears in the served log. Claim only what G3 proves: the code that emits it is live.
- **Do not** trigger a provider call, and do not simulate one by pointing the app at a fake provider — that
  would make the log say something the production path would not.
- State plainly in the report what would produce the line live, and that it awaits an authorised call.

## Acceptance criteria

- **A1** — socket-first proven before any docker command, with the `docker version` Server section quoted.
- **A2** — one build and one recreate, both rc=0, with the container id, image id, `Cmd`, restart count and
  health quoted; **no migration** (head unchanged); health green at the start, six times after and at the end.
- **A3** — the runtime diff is **exactly** SG-250's fourteen product files and nothing else; the frontend bundle
  is byte-identical; the served tree equals the worktree (`diff` rc=0).
- **A4** — G3's three proofs, each quoted from the served image's own files.
- **A5** — G4's provider ids, with an explicit statement that **no key value was read or printed**.
- **A6** — the pre-serve and post-serve census: all table counts identical, including `provider_call`.
- **A7** — the report states, in one paragraph, **what changed for the owner in production**: the app no longer
  estimates a call's cost and no cost check can stop a call; each real call's actual cost is recorded in the
  ledger and logged once as an INFO line; the consent switch and the scene feature's cap still work.
- **A8** — `PB-3` vacuity: each check could have failed — say what the opposite would have looked like (a
  runtime diff with an extra file; a bundle hash that moved; a startup traceback; a `provider_call` count that
  moved).
- **A9** — the report's last line is `Verification: PASS` or the honest failure reason.

## Scope ceiling

- `{{WORKLOG_DIR}}/SG-251*` only. **No product, config, schema, migration, dependency or test byte.**
- The backend container is recreated **once**; no other service is touched; no migration command; no browser;
  no provider call; no key value read; no `.env` file opened.
- The dispatch key opens no shell and runs nothing but this slice.

## Budget

The lane's `RUN_BUDGET_S` is the ceiling; **publish before the bound** at 1200 s. Expected ≈600 s, derived from
SG-241's actual elapsed time (257 s for one build, one recreate and a full verify) — this rider adds a census
and a content comparison.

## Report

Destination: `{{WORKLOG_DIR}}/SG-251_report.md`, with the evidence logs beside it; the receipt to the notes ref
`refs/notes/storagegenie-coder-reports` with the first line `Dispatch-ID: SG-251 | Report: docs/worklogs/SG-251_report.md | Work-HEAD: <work commit>` (fetch the ref explicitly: `git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`).
The report states the base ref and the resolved base commit as two fields, the model and effort read from the
process arguments (never a system-prompt label), the elapsed time measured from the lane's own clock, the
container and image ids before and after, the census before and after, and the files changed.
