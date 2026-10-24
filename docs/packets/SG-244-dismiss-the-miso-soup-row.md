# SG-244 — One production status transition: the Miso Soup row `read` → `dismissed`, through the app's own route

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: production SQLite — ONE row's `status` changes. No schema change, no migration, no row created or deleted.** `alembic_version` stays `20261023_sg233_reminder` and **no alembic command may run**.
**Restart: none.** No build, no recreate, no container operation of any kind touches the running app.
**Autonomy: L3.** Settings ride the trigger, never this packet.

**Authority for the one write (owner's own words, 2026-10-24):** *"W2 - dismiss."* — recorded as **D-1024-11** in `docs/decisions/2026-10-24-session-approvals.md`; the owner's answer to *"dismiss it, or move that expiry date"*. This slice performs that answer and nothing else. **The end state the owner named is `dismissed`.**

**Why this slice exists (the SG-241 audit's open item).** SG-241 (rated 96) served SG-240 and observed the daily pass line live for the first time — but its G3 write was **not** issued: the reminder row was already `read` (`updated_at 2026-10-24 15:21:24Z`, before that unit started at `16:14:53Z`), and **my own SG-241 packet said "if the row is already `dismissed` or `read`, make no write and call the end state reached"**. That clause was wrong: `read` is **not** the state the owner named. `dismissed` is. The legal transition exists — `backend/app/api/v1/reminders.py:24-27` allows `dismissed` from `unread` **or** `read` — and it has never been exercised on this row.

**Read the code before you act (premises, all re-verified in-slice — a difference is a finding, not an obstacle):**
- The row is `id 01a16e35-4394-7c11-9798-844754826bcc`, `asset_id 01a0c4aa-8b62-7360-b11e-a476ddaea0f6`, `display_name` **Miso Soup**, `household_id 01a0a029-1477-7ca0-b200-bce78a96c679`, `as_of_day 2026-10-24`, tier `urgent`, bucket `this-week`, `days_remaining 3`, `status` **read** at `2026-10-24 15:21:24Z`. **Quote your own measured values**; if the row's `display_name` is not Miso Soup, or the row is absent, **STOP and report** — do not write.
- The route is `POST /v1/reminders/{reminder_id}/dismiss?household_id={household_id}` (`backend/app/api/v1/reminders.py:116-122`), and it commits (`_transition`, `:93-104`).
- **The app records no actor and no audit row for this transition** (`reminder` has no actor column; `_transition` only sets `status` and commits). So the pre-state you quote **is the only evidence of what the row was before** — capture it first, precisely, and quote it in the report.
- The Expiry page renders **unread reminders only** (`frontend/src/routes/ExpiryPage.tsx:126`), so a `read` or `dismissed` row is invisible there — do **not** offer the owner a "click Dismiss in the browser" as the way to finish this; that button does not exist for this row.

**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies · no provider calls ($0 — a metered call is a STOP-and-report) · NETWORK: loopback only (the app's own address), nothing else · no secret in any artifact.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked:** `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-06` rows-your-run-creates · `PG-EV-08` pre-state-before-claim · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-08` a bound is a stop condition · `PG-IC-09` premises-live · `PG-DP-01` delivered-by-the-path · `PG-DP-02` no-sweep-waiver · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-06` runtime-versus-budget · `PG-PR-10` which-database.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

## G1 — Pre-state, read-only, before anything else

The app is served on the host at `http://127.0.0.1:8003` (the same loopback address as `{{HEALTH_CMD}}`); every URL below is that address, with no scheme other than `http` and no host other than `127.0.0.1`.

Read the live app over its loopback address and the live SQLite file **read-only**: `GET /v1/reminders?household_id=01a0a029-1477-7ca0-b200-bce78a96c679` (200, the row with every field), `GET /v1/health` (200), the `reminder` row itself (every column), the `reminder` row count, the alembic head, and the per-table counts of the live database. Quote all of it. **If the row's status is already `dismissed`, make no write** — report "end state already reached" and skip G2 (that is a pass, not a failure). **If the row is `unread`,** the same single POST in G2 is the authorized action; quote the pre-state as it is.

**No docker command of any kind in this slice** — the app is already running the bytes this slice changes nothing about.

## G2 — The one authorized write

Exactly **one** POST, through the app's own route, on the Miso Soup row:

```
POST /v1/reminders/01a16e35-4394-7c11-9798-844754826bcc/dismiss?household_id=01a0a029-1477-7ca0-b200-bce78a96c679
```

Expect `200` with the serialized row whose `status` is `dismissed`. **One call. Never two.** If the call times out or returns an ambiguous result, **do not retry it blindly**: re-read the state with `GET /v1/reminders` first — if `status` is already `dismissed`, the write landed (report it); if still `read`, the write did not land (report that and stop; do not loop the POST). A `422` on the first attempt is a finding to report, not a reason to try another route.

**Nothing else is written.** No other row is touched. No expiry date is changed. No row is created or deleted. No reminder is re-dated.

## G3 — Post-state, read-only

Re-read: `GET /v1/reminders?household_id=…` → `unread_count` **0**, the Miso Soup row present with `status` **dismissed**, and `asset_id`, `as_of_day`, `tier`, `bucket`, `days_remaining`, `display_name` **unchanged** from the G1 pre-state; the `reminder` row count unchanged (still 1); every other table's count unchanged; the alembic head unchanged; `GET /v1/health` → 200. Quote the before/after side by side.

## Constraints

- Scope: `docs/worklogs/SG-244*` only. No product, config, schema, migration, dependency or test edit. **One** production `UPDATE` of one column on one row, and nothing else. Reads are curl GETs and read-only SQLite; the only mutating call is the single POST in G2 (`PG-IC-01`). No docker invocation. No browser. No prompt or polling loop. No secret in any artifact. Runtime-vs-lane budget in seconds from the lane's own stamps (`PG-PR-06`).
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`).

## Acceptance and report

- A1: G1 pre-state quoted in full before the write — the row's id, asset, display name, `as_of_day`, tier, bucket, days, `status`, `updated_at`, the row count, the head, the table counts, health 200.
- A2: **exactly one** POST to the dismiss route, its status code and its response body pasted; no other mutating call in the slice (quote the access log's POST/PUT/PATCH/DELETE lines — exactly one, the one you made).
- A3: G3 post-state quoted; `status` is `dismissed`; `unread_count` 0; every other field and every table count identical to G1; health 200; head unchanged.
- A4: the **what the owner sees** line for the report: the Expiry page's unread-reminders block stays empty (it was empty before and after — the row was already `read`); the row's stored state changed from `read` to `dismissed`; and the recurrence fact — the daily pass creates a **new** row for each day (`record_due` is keyed by `(asset_id, as_of_day)`, `backend/app/services/reminders/service.py:53-59`), so a fresh unread row for Miso Soup arrives tomorrow (2026-10-25) and on the 26th and 27th, and stops once the expiry date passes. Say this plainly; it is not a defect.
- A5: base/hash echoed separately; work diff only the SG-244 namespace; elapsed per leg vs the lane bound; FIRST/DURING/REMAINING dispositioned. First token `SG-244`. The report's LAST line is exactly one of: `Verification: PASS` — or `Verification: FAIL — <check>` naming the check that failed (`CO-104`).
- A6: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-244 | Report: docs/worklogs/SG-244_report.md`, Work-HEAD recorded, push + mapped read-back. Bound lane receipt only.

## Budget

120s ordinary · 900s overall (the lane's `RUN_BUDGET_S` is 2100 s; this slice is minutes of work — publish before the bound and say so if you stop early). REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
