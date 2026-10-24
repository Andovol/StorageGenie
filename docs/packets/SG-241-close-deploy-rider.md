# SG-241 — Standing close-deploy rider: serve SG-240 (opened-date countdown + logging configuration) and dismiss the one owner-named reminder

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: production SQLite — NO schema change, NO migration.** The head stays `20261023_sg233_reminder`; **no alembic command may run** (`PG-PR-10`). This slice writes exactly **one row's status** — the owner-named dismissal in G3 — and creates no rows.
**Restart: one backend rebuild plus one recreate through the lane socket, each exactly once.**
**Autonomy: L3.** Settings ride the trigger, never this packet.

**Owner authority for the one write (quote, 2026-10-24):** *"W2 - dismiss."* — recorded as **D-1024-11** in `docs/decisions/2026-10-24-session-approvals.md`. W2 is the **Miso Soup** row (the only `reminder` row in production; `as_of_day` 2026-10-24, tier urgent, bucket this-week, expiry 2026-10-27). The owner chose **dismiss**, not "move the date" — the expiry date on the asset is **not** touched. If the owner has already clicked Dismiss themselves, the end state is reached: report it as a pass and make no write.

**Context.** SG-240 (row 11 of `docs/ROADMAP.md`) is rated and approved to ship. It adds the opened-date countdown (write path `POST /v1/plugins/expiry-tracker/assets/{asset_id}/opened`, read path `GET /v1/plugins/expiry-tracker/opened`, a UI section on the Expiry page) **and** the logging configuration that makes the daily pass visible — the uvicorn `LOGGING_CONFIG` leaves the root logger at `WARNING`, so the pass line SG-238 added was dropped in production (SG-239 proved it in a container). **This rider is where the pass line first appears live.** Its second job is the dismissal above.

**Premises — hypotheses about the tree and the host, re-verified in-slice per `PB-1` (a difference is a finding, not an obstacle):** (a) the merged-vs-served **runtime** diff is EXPECTED to be the backend files SG-240 touched — read the exact set from the merge commit (`git show --stat`), and it must be a **subset of SG-240's declared scope ceiling** (`backend/app/server.py`, `backend/app/logging_config.py` (new, optional), `backend/app/plugins/expiry_tracker.py`, `backend/app/api/v1/plugins.py`, `backend/app/services/opened_countdown.py` (new)); **any runtime file outside that ceiling is a STOP-and-report** (`PG-PR-04`, scope discipline); test and worklog files are not runtime and do not count; (b) pre-state container `67f668e2`, image `54f520da` — read the live values yourself and report any difference; (c) served bundle before the deploy: `index.html` `9850538a…`, JS `index-B0lDq5dE.js` `b6e26a8e…` (323000 B), CSS `index-C07VbG0m.css` `c3b58cda…` (4535 B) — **the JS and `index.html` hashes are EXPECTED TO CHANGE** (a new UI section), the CSS is expected unchanged; never claim byte-identical if it is not; (d) production SQLite: 29 tables, alembic head `20261023_sg233_reminder`, `reminder` = 1 (status `unread`), `assertion` 40, `audit_event` 104, `review_task` 9, `asset` 7, `household` 1 — quote your own counts; (e) the startup pass must log exactly one line `Daily reminder pass completed as_of=<today UTC> households_visited=1 reminders_created=0 errors=0` — **0 is the correct count** (today's row exists; `record_due` is idempotent per `(asset_id, as_of_day)`), and 0 is the live proof that a same-day pass creates nothing; (f) the new logging configuration must make that INFO line **appear in the container log** (it did not before) — and must not turn on INFO for third-party loggers: **report every distinct logger name that emitted at INFO** during startup; any logger other than `app.services.reminders.daily` (and the uvicorn/app loggers already visible) is a finding to report.

**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback plus container-runtime only, nothing else.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked:** `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-06` rows-your-run-creates · `PG-EV-08` before-and-after observable · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-08` a bound is a stop condition · `PG-IC-09` premises-live · `PG-DP-01` delivered-by-the-path · `PG-DP-02` no-sweep-waiver · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-06` runtime-versus-budget · `PG-PR-10` which-database.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

## Why this exists

The standing close-out rule deploys the live app before every close, and unrated or blocked work stops the deploy instead of shipping silently. SG-240 is rated and approved, so its delta ships now. **What this serve buys beyond the bytes:** (1) the opened-date countdown becomes usable on the live Expiry page; (2) the daily pass becomes *observable in production for the first time* — the container's own log states the day, the households visited, the reminders created and the errors; (3) the one production row the owner named stops sitting unread.

Waste cut: the backend suite stays **WAIVED** per `PG-DP-02` (restart-gated: any end-to-end sweep would exercise the previous build). The substitute is the post-recreate read-only verification plus the live pass-line observation.

## G0 — Socket first (lane socket before anything Docker)

Print the lane socket from YOUR unit's own process environment, `export DOCKER_HOST` to it (and `DOCKER_CONFIG` to a writable temp path if the client needs one), then prove the server line with `docker version` — the **server** section must answer; a client-only block is NOT proof. **No `docker` invocation of any kind before the export**: a default-endpoint call is a STOP for this slice (`PB-2`).

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: the running container's identity (id, created, started, `Cmd`, restarts), the health status and body (`curl -s http://127.0.0.1:8003/v1/health`), the served bundle hashes, the alembic head, and the per-table row counts of the live SQLite file — **including `reminder` = 1 and that row's id, `status` (`unread`), `asset_id`, `display_name`, `as_of_day`, `tier`, `bucket`, `days_remaining`** (`PG-EV-08`: the production observable before AND after). The household id comes from `GET /v1/households` (read-only).

Then, through the lane socket only and in this order: **no migration**, build the backend image exactly once, recreate the backend container exactly once (`PG-PR-04`). No host config changes. A second build/recreate issuance is STOP. `PG-EV-06`: the rows this run creates are **zero** — the startup pass must create none, because today's row already exists; quote the per-table counts before and after and name every table that moved (the expected answer: none).

## G2 — Verify the serve, and read the pass line

Observe the new container identity and start time (ID/Created, not RestartCount) and its `Cmd` showing `app.server:app`. Health ok for DB/storage; six health GETs as the standing precedent. Re-read the served bundle hashes, the schema head (**unchanged**) and the table counts; require no application row change apart from the one named in G3.

**The pass line — the point of this slice.** Read the new container's log and paste it verbatim (bound the read: at most 60 s in ≤5 s steps, then report what you saw; no polling loop). It must contain exactly one pass line, and the line's numbers must be the pass's real numbers: `as_of` = today's UTC date, `households_visited` = the number of households in the table, `reminders_created` = **0** (today's row exists — a non-zero number here is a finding, not a pass), `errors` = 0. Also report the **distinct logger names that emitted at INFO** (premise (f)) and the total number of log lines. Then read the endpoint and the table: `GET /v1/reminders?household_id=…` → `unread_count` 1 and the same row, still **unread**; the row's `as_of_day`, tier, bucket and days unchanged.

Also required: the old container's stop must be prompt (the lifespan cancels the daily task with a 5 s bound — a stop that hangs past that is a finding; the old container's own shutdown log may be unreadable once it is removed, so record the recreate's wall time and the new `StartedAt` as the evidence), the new container must be `running`/`healthy`, and the shell routes must still answer (`/`, `/expiry`, `/inbox`, `/planning`).

**The new route answers (read-only):** `GET /v1/plugins/expiry-tracker/opened` must answer `200` with a body — a `404`/`500` here means SG-240's read path did not reach the served image, and that is a finding to report, not a pass. `GET /v1/plugins/expiry-tracker/status` must still answer. Do **not** POST to the opened-date write path: this rider serves and verifies; it does not create opened-date rows.

## G3 — The one owner-named write: dismiss the Miso Soup reminder

Precondition: the row from G1 is still `unread` and its `display_name` is **Miso Soup** (the `food_beverages` row, expiry 2026-10-27). If the row is already `dismissed` or `read` (the owner clicked it themselves), **make no write**: report "already dismissed/read by the owner — end state reached" and treat G3 as a pass.

Otherwise, exactly **one** call, through the app's own route (never a direct database write):

```
POST /v1/reminders/{reminder_id}/dismiss?household_id={household_id}
```

Expect `200` with the serialized row whose `status` is `dismissed`. Then verify, read-only: `GET /v1/reminders?household_id=…` → `unread_count` **0**, the row still present with `status` `dismissed`, and `asset_id`, `as_of_day`, `tier`, `bucket`, `days_remaining`, `display_name` **unchanged** from the pre-state; the read-only SQLite row shows `status = dismissed`.

**Do not retry the POST blindly.** If it times out or returns an ambiguous result, re-read state first (`GET /v1/reminders`): if the row is already `dismissed`, the write landed — report it; if still `unread`, the write did not land — report that and stop (do not loop the POST). A second POST on a dismissed row returns `422` — a `422` on a *first* attempt is a finding to report.

**Nothing else is written.** No other row is read-marked, dismissed or re-dated; no expiry date is changed; no `reminder` row is deleted.

## Constraints

- Scope: `docs/worklogs/SG-241*` only. No product/config/schema/migration/test edits. Apart from the single named status transition in G3, no production INSERT/UPDATE/DELETE of any kind by this slice. No imports or evidence-store mutation. Reads are git / lane-socket docker / curl GETs / read-only SQLite; only executed runtimes are the G0-verified build and recreate (`PG-IC-01`). Reads/verification ≤120s per command, build ≤600s (inherited precedent); visible timeout finding; idle kill 900s never approached. No prompt or polling loop — the pass-line read is a **bounded** wait (state the bound, e.g. at most 60 s in ≤5 s steps, then report what you saw). No sudo/alternate identity/mount/host config. No secret in any artifact. Runtime-vs-lane budget in seconds from the lane's own stamps (`PG-PR-06`).
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks share no condition with any remediation step — stops win. Reads MAY use the already-built local images only; pulling or running any image the packet does not name counts as a runtime launch — NOT authorized here.
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`).

## Acceptance and report

- A1: G0 proven (export + server line) BEFORE any other docker call; one build + one recreate THROUGH THE LANE SOCKET; new running-instance proof with `Cmd` = `app.server:app`; health green; explicit deltas (runtime diff = the SG-240 subset of the declared ceiling, **or** a STOP-report naming the file outside it; bundle hashes recorded; schema head unchanged; **every table count identical**, `reminder` still 1).
- A2: **the pass line pasted from the container log**, exactly once, with `as_of` = today, `households_visited` = the household count, `reminders_created` = 0, `errors` = 0; the distinct INFO logger names reported; `GET /v1/reminders` shows `unread_count` 1 with the same unread row; the row's fields unchanged.
- A3: the new read route `GET /v1/plugins/expiry-tracker/opened` answers `200` with a body; the shell routes answer; **no POST to the opened-date write path**.
- A4: the dismissal — pre-state quoted, the row named Miso Soup, exactly one `POST …/dismiss` (or an explicit "owner already dismissed it" with the proof), post-state verified (`status` `dismissed`, `unread_count` 0, other fields unchanged), and **no other write** anywhere in the slice.
- A5: base/hash echoed separately; work diff only SG-241 namespace.
- A6: command logs + report `docs/worklogs/SG-241_report.md`; elapsed per leg vs lane bound; constraints answered; FIRST/DURING/REMAINING dispositioned. First token SG-241. The report's LAST line is exactly one of: `Verification: PASS` — or `Verification: FAIL — <check>` naming the check that failed (`CO-104`). The report must also state **what the owner should look at in the browser** (the Expiry page's opened-date section, and that the unread reminder block is now empty).
- A7: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-241 | Report: docs/worklogs/SG-241_report.md`, Work-HEAD recorded, push + mapped read-back. Bound lane receipt only.

## Budget

120s ordinary · 600s build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
