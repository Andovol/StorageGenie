# SG-237 — D2: accept one near expiry date on the live household and prove the daily reminder path end-to-end (production data write, owner-approved)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: production SQLite — exactly THREE rows are created by this slice, and each one is authorised.** (1) one `plugin:expiry-tracker/classification` assertion, (2) one `plugin:expiry-tracker/expiry_date` assertion, (3) one `reminder` row that the **daily pass itself** creates after the restart. No other table is touched; no existing row is modified or deleted.
**Restart: one backend container restart through the lane socket, exactly once** — no build, no recreate, no migration, no image change.
**Autonomy: L2.** Settings ride the trigger, never this packet. No product code changes in this slice.

**Authorising grant for the production write (PG-PR-10).** The owner, 2026-10-24, verbatim: *"Okay with D1 and D2"* — recorded as **D-1024-7** in `docs/decisions/2026-10-24-session-approvals.md`: *"accept one near expiry date (≈3 days out) for one ACTIVE asset of the live household `01a0a029-…c679`, through the app's own plugin routes; let the daily pass run; observe the reminder row it creates. The reminder is left unread, so the owner can click Read/Dismiss on the Expiry page."* The write is authorised **for one asset and one date**; a second asset or a second date is STOP.

**Context and standing lines.** SG-235's daily caller and the Expiry Read/Dismiss buttons are **live** (served by SG-236: container `ee4e165a`, image `2bd3599f`, `Cmd ["uvicorn","app.server:app",…]`). The pass has never created a row in production because the live household has 7 ACTIVE assets and **0 accepted expiry assertions** — the engine returns 0 rows, so `record_due` inserts nothing (SG-236 audit I2). This slice supplies the missing data and observes the real path. Expected premises, all re-verified in-slice per `PB-1` (a difference is a finding, not an obstacle): (a) the served app answers on `http://127.0.0.1:8003` (the compose mapping `127.0.0.1:8003:8000`; `{{HEALTH_CMD}}` is `curl -s http://127.0.0.1:8003/v1/health`); (b) exactly one household exists, id `01a0a029-1477-7ca0-b200-bce78a96c679`; (c) 7 ACTIVE assets; (d) the two write routes are the ones the committed SG-233 fixture uses — `POST /v1/plugins/expiry-tracker/assets/{asset_id}/classification?household_id=…` with body `{"category": "food_beverages"}` and `POST /v1/plugins/expiry-tracker/assets/{asset_id}/expiry?household_id=…` with body `{"expiry_date": "YYYY-MM-DD", "date_type": "expiry_date"}` (`backend/tests/test_sg233_reminders.py:106-122`); (e) a food expiry 3 days out yields tier `urgent`, bucket `this-week`, `days_remaining` 3, window 7 (the same fixture's expectation — **quote the engine, do not assume**); (f) the daily pass runs once at container startup and then every 24 h, so the startup pass is what a restart triggers; (g) contract recorded `0.52.0` == published payload `0.52.0` == host copy `0.52.0` (SG-235's and SG-236's echoes, both from `/home/andrei/storagegenie-contract/CODER.md`). Never assert HEAD equals any hash (`PG-IC-07`).

**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback plus container-runtime only, nothing else.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked:** `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-06` rows-your-run-creates · `PG-EV-08` before-and-after observable · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-08` a bound is a stop condition · `PG-IC-09` premises-live · `PG-DP-02` no-sweep-waiver · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-06` runtime-versus-budget · `PG-PR-10` which-database + authorising grant.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

## Why this exists

The owner's headline feature — expiry reminders that reach the user — is **live but has never spoken**. The daily pass runs (SG-236 could only infer it: the module logs failures only, so no pass line exists yet), yet the live household holds 7 ACTIVE assets and **zero accepted expiry assertions**, so the engine returns no rows and `reminder` stays at 0. The reminder list on the Expiry page is empty, and the Read/Dismiss buttons have never been exercised against a real row. The owner approved supplying one near expiry date so the whole chain — accepted data → engine → daily pass → stored reminder → live endpoint → the page's two buttons — is observed in production, with the row left unread for the owner to click.

**Waste cut (one, from the last audit).** SG-236's audit named `slowest_waste = 114s contract/product/audit reads` — the Coder re-read the contract, the product tree and the previous audit. This packet hands over everything those reads established: the served container/image/Cmd, the household id, the exact write routes and bodies, the expected engine shape, the pre-state counts and the grant. **Read code only for what this packet does not give.**

## G0 — Socket first (lane socket before anything Docker)

Print the lane socket from YOUR unit's own process environment, `export DOCKER_HOST` to it, then prove the server line with `docker version` (the server section must answer — a client-only block is NOT proof). No `docker` invocation of any kind before the export. A default-endpoint call STOPS the slice (`PB-2`).

## G1 — Pre-state, read-only, before any write

Establish the pre-state read-only: the served container identity (id, created, started, image, `Cmd`, restarts), health status and body, and the per-table row counts of the live SQLite file (`assertion`, `asset`, `reminder`, `household`, plus the alembic head) — plus the **asset inventory**: every ACTIVE asset's id and display name, and the assertion rows the `plugin:expiry-tracker/%` field paths, so the "before" picture of the expiry track is on record. Also read the two route handlers in `backend/app/api/v1/plugins.py` to confirm the route shapes and the request bodies quoted in premise (d) — a route that differs is a finding, and you adjust to the code, not to my quote.

## G2 — The write: one asset, one classification, one near expiry date

Through the app's **own HTTP routes** (never by writing SQLite directly — a direct row insert would bypass the engine's accepted-assertion path and prove nothing):

1. Choose the asset: from the inventory, pick the ACTIVE asset whose display name most plausibly denotes a food or consumable; if none does, pick the first ACTIVE asset by id and say why. **Report the full inventory and the choice.**
2. Post the classification with `{"category": "food_beverages"}` and the expiry with `{"expiry_date": <today UTC + 3 days>, "date_type": "expiry_date"}` — the date is read from the live clock at execution, never hardcoded (`PG-IC-07`). Both responses must be 2xx; quote them.
3. Confirm the data landed the way the engine reads it: `GET /v1/plugins/expiry-tracker/status?household_id=…` now shows that asset with a tier, a bucket and days remaining, and the `assertion` count grew by exactly two. If the engine still shows no row for it, **STOP and report** — do not write a second date or a second asset.

## G3 — Restart once, then observe the pass

One `docker restart` of the backend container through the lane socket, exactly once (the startup pass is what it triggers). No build, no recreate, no image change, no migration, no second restart. Then, read-only:

- the new container identity and start time (id, created, started, `Cmd`, restarts) and health green again;
- the container's log — quote it: the startup lines, any failure line, and **the reminder row appearing**;
- the `reminder` table: exactly **one** new row, `as_of_day` = today's UTC date, status `unread`, tier/bucket/days matching the engine row for the same day;
- `GET /v1/reminders?household_id=…` → `unread_count` 1 and one item whose tier/bucket/days equal the engine's for today;
- the served JS still carries the button strings (`Unread reminders`, `Read reminder`, `Dismiss reminder`);
- per-table counts after, compared with G1's — **only** `assertion` (+2) and `reminder` (+1) may differ. Any other movement is a finding, named exactly.

**Leave the reminder UNREAD.** Do not POST `/read` or `/dismiss` — the owner clicks those. Do not create a second row.

## Constraints

- Scope: `docs/worklogs/SG-237*` only. **No product, config, schema, migration or test edits.** The only production effects are the three authorised rows and the one restart.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued; G-hunks share no condition with any remediation step — stops win. Reads MAY use the already-built local images only; pulling or running any image the packet does not name counts as a runtime launch — the G0-verified restart is the only executed runtime here.
- No full suite and no browser sweep (`PG-DP-02`): this slice changes zero code, and the app restarts mid-slice, so an end-to-end sweep would exercise a mixed build. The substitute is the read-only post-restart verification in G3.
- Runtime-versus-budget (`PG-PR-06`): state the containment limit **with its unit and where the number came from** — the restart's observed downtime in seconds (state the bound you waited for) and the elapsed per leg against the lane budget, in seconds from the lane's own stamps.
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`). No prompt or polling loop — the post-restart observation is a **bounded** wait (state the bound, e.g. at most 60 s in ≤5 s steps, then report what you saw). No secret in any artifact.

## Acceptance and report

- A1: G0 proven (export + server line) BEFORE any other docker call; the pre-state inventory and counts on record before the write.
- A2: exactly one asset, one classification, one near expiry date written **through the app's own routes**, both responses quoted 2xx; the engine shows the asset with a tier/bucket/days; the `assertion` count grew by exactly two.
- A3: exactly one restart; the new identity and green health; the log quoted; exactly one new `reminder` row, unread, engine-shaped, `as_of_day` = today; `GET /v1/reminders` shows `unread_count` 1 and the same shape; per-table counts after differ from before **only** in `assertion` (+2) and `reminder` (+1); the served JS still carries the button strings; **the reminder is left unread**.
- A4: logs + report `docs/worklogs/SG-237_report.md`; elapsed per leg vs the lane bound; constraints answered; FIRST/DURING/REMAINING dispositioned; first token SG-237; the report's LAST line is exactly one of: `Verification: PASS` — or `Verification: FAIL — <check>` naming the check that failed (`CO-104`).
- A5: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-237 | Report: docs/worklogs/SG-237_report.md`, Work-HEAD recorded, push + mapped read-back.

## Budget

120s ordinary · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
