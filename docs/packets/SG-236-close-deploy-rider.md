# SG-236 — Standing close-deploy rider: serve the SG-235 daily-caller + Read/Dismiss delta (no migration; the startup pass writes today's reminder rows)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: production SQLite — NO schema change; the deploy itself causes ONE production write, and it is the owner-approved feature.** The `reminder` table already exists (head `20261023_sg233_reminder`); no migration runs in this slice. **The single production write:** the new container starts the daily pass once at startup, and that pass inserts the engine-shaped `unread` reminder rows for the live household for **today's UTC day** (D-1024-2, owner, 2026-10-24: *"a background task inside the app. It runs once at startup, then every 24 hours (UTC), and calls `record_due` for every household"*). The authorising grant for that write is the standing owner directive 2026-09-28 (`AGENTS.md` Close-out row) **plus** the owner's close instruction this chat **plus** D-1024-2. No other table is written; no INSERT/UPDATE/DELETE of application rows by this slice itself.
**Restart: one backend rebuild plus one recreate through the lane socket, each exactly once.**
**Autonomy: L2.** Settings ride the trigger, never this packet. No product repair is implemented here.

**Context and standing lines.** SG-235 (the in-app daily caller + the Expiry Read/Dismiss buttons) is rated 97 with nothing open, and its delta has never been served — the live service still serves the pre-SG-235 build. This rider serves it. Expected premises, all re-verified in-slice per `PB-1` (a difference is a finding, not an obstacle): (a) the merged-vs-served runtime diff is EXPECTED to be exactly the SG-235 product set — `backend/app/services/reminders/daily.py` (new), `backend/app/server.py` (new), `backend/app/main.py` (one top-level import plus the registration line), `backend/Dockerfile` (one CMD token: `uvicorn app.server:app` instead of `app.main:app`), `frontend/src/routes/ExpiryPage.tsx` (the two buttons) — report the actual diff; any runtime product change beyond that set is named exactly, and any diff outside the served paths is STOP; (b) non-runtime delta since the last serve = packets, worklogs, ratings, STATE, decisions, AGENTS version record, the SG-235 audit; (c) the alembic head stays `20261023_sg233_reminder` — **no migration is pending and none may run**; (d) contract recorded `0.52.0` == published payload `0.52.0` == the host copy the last slice echoed (`/home/andrei/storagegenie-contract/CODER.md`, SG-235 report I1) — the host link is now **equal, not merely stated**; echo verbatim what your copy says and name the source path; (e) the served container's command line must show `app.server:app` after the recreate, and the app must still answer every route it answered before (the lifespan attaches to the SAME app object). Never assert HEAD equals any hash (`PG-IC-07`).

**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback plus container-runtime only, nothing else.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked:** `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-06` rows-your-run-creates · `PG-EV-08` before-and-after observable · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-08` a bound is a stop condition · `PG-IC-09` premises-live · `PG-DP-01` delivered-by-the-path · `PG-DP-02` no-sweep-waiver · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-06` runtime-vs-budget · `PG-PR-10` which-database + authorising grant.

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

The standing close-out rule deploys the live app before every close, and unrated or blocked work stops the deploy instead of shipping silently. SG-235 is rated 97 with nothing open, so its delta ships now: one daily-caller module, one served entrypoint, one import normalization, one CMD token, two buttons. **The point of this rider is not only that the bytes arrive — it is that the daily pass becomes LIVE:** today the live database still holds `reminder` = 0 rows because nothing calls `record_due`; after this recreate the served app runs the pass once at startup and the household's due items become unread reminders the owner can act on.

Waste cut: the SG-235 audit names `slowest_waste = 58s full-suite-raw` — handed over here, not re-derived: the full backend suite stays **WAIVED** per `PG-DP-02` (restart-gated: any end-to-end sweep would exercise the previous build), and the substitute is the post-recreate read-only verification of the served tree. This slice changes zero product bytes itself, so the suite would prove nothing new.

## G0 — Socket first (lane socket before anything Docker)

Print the lane socket from YOUR unit's own process environment, `export DOCKER_HOST` to it, then prove the server line with `docker version` (the server section must answer — a client-only block is NOT proof). No `docker` invocation of any kind before the export. A default-endpoint call STOPS the slice (`PB-2`).

## G1 — Pre-state, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, the container's `Cmd`, health status/body, served JS/CSS/index hashes, alembic head, and authoritative table counts (`PG-EV-08`: the production observable before AND after — **counts per table now, counts per table after**, with `reminder` quoted separately because this slice's startup pass changes it).

Then, through the lane socket only and in this order: **no migration**, build the backend image exactly once, recreate the backend container exactly once (`PG-PR-04`). No host config changes. A second migrate/build/recreate issuance is STOP. `PG-EV-06`: the rows this slice's run creates are exactly the `reminder` rows the startup pass inserts (plus zero rows anywhere else) — quote the per-table counts before and after and name every table that moved.

## G2 — Verify the serve, without claiming more

Observe a new container identity and start time (ID/Created, not RestartCount) and its `Cmd` showing `app.server:app`. Health ok for DB/storage; six health GETs as the standing precedent. Re-read bundle hashes (EXPECTED changed: the two buttons ship new JS — record the new hashes, never claim byte-identical; CSS is expected unchanged — if it changed, name it), schema head (**unchanged**), and table counts; require no application row change other than `reminder`.

**The daily pass must be observed LIVE, not assumed.** After the recreate, the startup pass runs in the background: read the container's own log for its pass line (households visited, reminders created, errors) and read `GET /v1/reminders?household_id=<the live household id>` to see the rows. Then check the property, not a count: **every unread row the endpoint returns is engine-shaped for today** (tier/bucket/days match `GET /v1/plugins/expiry-tracker/status` for the same household and day) and the endpoint's `unread_count` equals the number of unread rows it returns. **The created row count is NOT a pass/fail number** — it depends on the live expiry data, and no bound is asserted against it (`PG-IC-08`); report it, name the assets it names, and say so plainly. If the pass did not run, or ran with errors, say so loudly — the deploy succeeded but the feature did not go live, and that is a finding, not a pass.

Also required: the old container's stop must be prompt (the lifespan cancels the daily task with a 5 s bound — a stop that hangs past that is a finding), the new container must be `running`/`healthy`, and the shell routes must still answer (`/`, `/expiry`, `/inbox`, `/planning`) — on `/expiry` confirm the Reminders section renders. No writes; no paid calls. Application provider spend prohibited.

Suite stays waived per `PG-DP-02`; substitute is post-recreate read-only identity/health/schema/counts/pages verification plus the live pass observation.

## Constraints

- Scope: `docs/worklogs/SG-236*` only. No product/config/schema/migration/test edits. No production INSERT/UPDATE/DELETE **by this slice** (the startup pass's own inserts are the feature's authorised write, named above). No imports or evidence-store mutation. Reads are git / lane-socket docker / curl GETs / read-only SQLite; only executed runtimes are the G0-verified build and recreate (`PG-IC-01`). Reads/verification ≤120s per command, build ≤600s (inherited precedent); visible timeout finding; idle kill 900s never approached. No prompt or polling loop — the pass observation is a **bounded** wait (state the bound you used, e.g. at most 60 s in ≤5 s steps, then report what you saw). No sudo/alternate identity/mount/host config. No secret in any artifact. Runtime-vs-lane budget in seconds from the lane's own stamps (`PG-PR-06`).
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks share no condition with any remediation step — stops win. Reads MAY use the already-built local images only.
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`).

## Acceptance and report

- A1: G0 proven (export + server line) BEFORE any other docker call; one build + one recreate THROUGH THE LANE SOCKET; new running-instance proof with `Cmd` = `app.server:app`; health green; explicit deltas (EXPECTED: the SG-235 product set served, bundle JS hash changed, CSS unchanged, schema head unchanged, `reminder` rows created by the startup pass and **no other table moved** — quote both count sets).
- A2: base/hash echoed separately; merged-vs-served diff checked against the EXPECTED SG-235 product set; work diff only SG-236 namespace; **the live daily pass observed** (log line + endpoint read + the engine-shape property), with the created-row count reported as a count, never as a bound.
- A3: command logs + report `docs/worklogs/SG-236_report.md`; elapsed per leg vs lane bound; constraints answered; FIRST/DURING/REMAINING dispositioned. First token SG-236. The report's LAST line is exactly one of: `Verification: PASS` — or `Verification: FAIL — <check>` naming the check that failed (`CO-104`).
- A4: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-236 | Report: docs/worklogs/SG-236_report.md`, Work-HEAD recorded, push + mapped read-back. Bound lane receipt only.

## Budget

120s ordinary · 600s build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
