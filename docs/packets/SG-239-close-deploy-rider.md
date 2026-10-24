# SG-239 — Standing close-deploy rider: serve the SG-238 daily-pass success line (no migration; the same-day pass creates nothing)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: production SQLite — NO schema change, NO data write.** The `reminder` table and every other table already exist; the head stays `20261023_sg233_reminder` and **no alembic command may run**. The only production effect of this slice is the **startup pass** the new container runs: it computes the day again and finds today's row already present, so it creates **nothing** — `reminder` stays at 1 (the Miso Soup row, **unread**, and it must stay unread).
**Restart: one backend rebuild plus one recreate through the lane socket, each exactly once.**
**Autonomy: L2.** Settings ride the trigger, never this packet. No product repair is implemented here.

**Context and standing lines.** SG-238 (rated 97) added one INFO line to the daily pass so a pass can be observed. **That line is not live yet** — the served container still runs the old module. This rider serves it, and it is the first slice that can prove the pass in production by reading the container's own log. Expected premises, all re-verified in-slice per `PB-1` (a difference is a finding, not an obstacle): (a) the merged-vs-served **runtime** diff is EXPECTED to be exactly `backend/app/services/reminders/daily.py` (one INFO line) — `Makefile` and the two test modules are not runtime (not in the image's import path), and any other runtime change is named exactly, or STOP; (b) pre-state: container `ee4e165a` (created 2026-10-24T11:30:45Z by SG-236, **restarted** at 13:59:05Z by SG-237), image `sha256:2bd3599f…`, `Cmd ["uvicorn","app.server:app",…]`, restarts 0, health green; served bundle `index.html` `9850538a…`, JS `index-B0lDq5dE.js` `b6e26a8e…` (323000 B), CSS `index-C07VbG0m.css` `c3b58cda…` (4535 B); (c) production SQLite: 29 tables, alembic head `20261023_sg233_reminder`, `reminder` = **1** (as_of_day 2026-10-24, tier urgent, bucket this-week, days_remaining 3, status **unread**), `assertion` 40, `audit_event` 104, `review_task` 9, `asset` 7, `household` 1 — quote your own counts; (d) the new container's startup pass must log exactly one line of the form `Daily reminder pass completed as_of=<today UTC> households_visited=1 reminders_created=0 errors=0` — **0 is the correct count** (today's row exists; `record_due` is idempotent per `(asset_id, as_of_day)`), and 0 is the proof that the same-day pass creates nothing; (e) the served JS/CSS are EXPECTED unchanged (no frontend byte changed) — record what you read and **never claim byte-identical if it is not**; (f) contract recorded `0.52.0` == published payload `0.52.0` == host copy `0.52.0` (SG-235/236/237/238 echoes) — echo verbatim what your copy says and name the source path.

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

The standing close-out rule deploys the live app before every close, and unrated or blocked work stops the deploy instead of shipping silently. SG-238 is rated 97 with nothing open, so its delta ships now. **What this serve buys beyond the bytes:** the daily pass becomes *observable* for the first time. SG-236 could only infer the pass (no success line existed); SG-237 proved the row from the table. After this recreate the container's own log states the pass — the day, the households visited, the reminders created, the errors — and the expected `reminders_created=0` is the live proof that a same-day pass creates nothing (idempotence, observed in production rather than asserted in a test).

Waste cut: the SG-238 audit named `slowest_waste = 66s candidate-suite-raw`. The full backend suite stays **WAIVED** per `PG-DP-02` (restart-gated: any end-to-end sweep would exercise the previous build), and this slice changes one runtime line — the suite would prove nothing new. The substitute is the post-recreate read-only verification plus the live pass-line observation.

## G0 — Socket first (lane socket before anything Docker)

Print the lane socket from YOUR unit's own process environment, `export DOCKER_HOST` to it (and `DOCKER_CONFIG` to a writable temp path if the client needs one), then prove the server line with `docker version` — the **server** section must answer; a client-only block is NOT proof. **No `docker` invocation of any kind before the export**: a default-endpoint call is a STOP for this slice (`PB-2`).

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: the running container's identity (id, created, started, `Cmd`, restarts), the health status and body, the served bundle hashes, the alembic head, and the per-table row counts of the live SQLite file — **including `reminder` = 1 and that row's status (`unread`)** (`PG-EV-08`: the production observable before AND after).

Then, through the lane socket only and in this order: **no migration**, build the backend image exactly once, recreate the backend container exactly once (`PG-PR-04`). No host config changes. A second build/recreate issuance is STOP. `PG-EV-06`: the rows this slice's run creates are **zero** — the startup pass must create none, because today's row already exists; quote the per-table counts before and after and name every table that moved (the expected answer: none).

## G2 — Verify the serve, and read the pass line

Observe the new container identity and start time (ID/Created, not RestartCount) and its `Cmd` showing `app.server:app`. Health ok for DB/storage; six health GETs as the standing precedent. Re-read the served bundle hashes, the schema head (**unchanged**) and the table counts; require no application row change.

**The pass line — the point of this slice.** Read the new container's log and paste it verbatim. It must contain exactly one pass line, and the line's numbers must be the pass's real numbers: `as_of` = today's UTC date, `households_visited` = the number of households in the table, `reminders_created` = **0** (today's row exists — a non-zero number here is a finding, not a pass), `errors` = 0. Then read the endpoint and the table: `GET /v1/reminders?household_id=…` → `unread_count` 1 and the same row, still **unread**; the row's `as_of_day`, tier, bucket and days unchanged. **Do not POST `/read` or `/dismiss`** — the owner clicks those.

Also required: the old container's stop must be prompt (the lifespan cancels the daily task with a 5 s bound — a stop that hangs past that is a finding; the old container's own shutdown log may be unreadable once it is removed, so record the recreate's wall time and the new `StartedAt` as the evidence), the new container must be `running`/`healthy`, and the shell routes must still answer (`/`, `/expiry`, `/inbox`, `/planning`).

Suite stays waived per `PG-DP-02`; the substitute is the post-recreate read-only identity/health/schema/counts/pages verification plus the live pass-line observation.

## Constraints

- Scope: `docs/worklogs/SG-239*` only. No product/config/schema/migration/test edits. No production INSERT/UPDATE/DELETE of any kind by this slice. No imports or evidence-store mutation. Reads are git / lane-socket docker / curl GETs / read-only SQLite; only executed runtimes are the G0-verified build and recreate (`PG-IC-01`). Reads/verification ≤120s per command, build ≤600s (inherited precedent); visible timeout finding; idle kill 900s never approached. No prompt or polling loop — the pass-line read is a **bounded** wait (state the bound, e.g. at most 60 s in ≤5 s steps, then report what you saw). No sudo/alternate identity/mount/host config. No secret in any artifact. Runtime-vs-lane budget in seconds from the lane's own stamps (`PG-PR-06`).
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks share no condition with any remediation step — stops win. Reads MAY use the already-built local images only; pulling or running any image the packet does not name counts as a runtime launch — NOT authorized here.
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`).

## Acceptance and report

- A1: G0 proven (export + server line) BEFORE any other docker call; one build + one recreate THROUGH THE LANE SOCKET; new running-instance proof with `Cmd` = `app.server:app`; health green; explicit deltas (runtime diff = `daily.py` only; bundle hashes recorded; schema head unchanged; **every table count identical**, `reminder` still 1).
- A2: **the pass line pasted from the container log**, exactly once, with `as_of` = today, `households_visited` = the household count, `reminders_created` = 0, `errors` = 0; `GET /v1/reminders` shows `unread_count` 1 with the same unread row; the row's fields unchanged; **no `/read` or `/dismiss` POST was made**.
- A3: base/hash echoed separately; merged-vs-served runtime diff checked against the EXPECTED set; work diff only SG-239 namespace.
- A4: command logs + report `docs/worklogs/SG-239_report.md`; elapsed per leg vs lane bound; constraints answered; FIRST/DURING/REMAINING dispositioned. First token SG-239. The report's LAST line is exactly one of: `Verification: PASS` — or `Verification: FAIL — <check>` naming the check that failed (`CO-104`).
- A5: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-239 | Report: docs/worklogs/SG-239_report.md`, Work-HEAD recorded, push + mapped read-back. Bound lane receipt only.

## Budget

120s ordinary · 600s build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
