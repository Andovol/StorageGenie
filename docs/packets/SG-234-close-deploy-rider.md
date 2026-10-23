# SG-234 — Standing close-deploy rider: serve the SG-233 reminders delta (migration plus API plus badge)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: production SQLite migrates, never data-writes.** The deploy applies the one pending migration (empty `reminder` table); no INSERT/UPDATE/DELETE of application rows, no imports, no evidence-store mutation.
**Restart: one backend rebuild plus one recreate through the lane socket, each exactly once.**
**Autonomy: L2.** Production authorization basis: standing owner directive 2026-09-28 (`G-O4`; `AGENTS.md` Close-out row) plus the owner's close instruction this chat (deploy-at-close of the rated SG-233 delta). Settings ride the trigger, never this packet. No product repair is implemented here.

**Context and standing lines.** SG-233 (reminder store, daily compute, in-app sender) is rated 98 and committed; its product delta has never been served — the live service still serves the pre-SG-233 build. This rider serves it. Expected premises, all re-verified in-slice per `PB-1` (a difference is a finding, not an obstacle): (a) the merged-vs-served runtime diff is EXPECTED to be exactly the SG-233 product set — `backend/alembic/versions/20261023_sg233_reminder.py`, `backend/app/models/reminder.py`, `backend/app/services/reminders/`, `backend/app/api/v1/reminders.py`, `backend/app/main.py` (one line), `frontend/src/routes/ExpiryPage.tsx`, `frontend/src/api/client.ts`, `frontend/src/api/types.ts` — report the actual diff; any runtime product change beyond that set is named exactly, and any diff outside the served paths is STOP; (b) non-runtime delta since the last serve = packets, worklogs, ratings, STATE, decisions, AGENTS version record; (c) contract recorded/published/host/installed now `0.51.0` (D3 adoption this session; previous host echo `0.51.0` from the SG-233 report). Never assert HEAD equals any hash (`PG-IC-07`).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback plus container-runtime only, nothing else.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked:** `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-06` rows-your-run-creates · `PG-EV-08` before-and-after observable · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-DP-01` delivered-by-the-path · `PG-DP-02` no-sweep-waiver · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-06` runtime-vs-budget · `PG-PR-10` which-database.

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

The standing close-out rule deploys the live app before every close, and unrated or blocked work stops the deploy instead of shipping silently. SG-233 is rated 98 with nothing open, so its delta ships now: one migration, one model, one writer, three routes, one registration line, one badge.

Waste cut: the SG-233 audit names `slowest_waste = 59s full-suite-raw` — handed over here, not re-derived: candidate suite `730 passed + 2 base-proved environment reds` (pyzbar/tesseract absent, proven on base `7d0cc91`, same family as the standing decoder reds). Full suite stays WAIVED per `PG-DP-02` (restart-gated; substitute below is post-recreate read-only verification of the served tree, and this slice changes zero product bytes itself).

## G0 — Socket first (lane socket before anything Docker)

Print the lane socket from YOUR unit's own process environment, `export DOCKER_HOST` to it, then prove the server line with `docker version` (the server section must answer — a client-only block is NOT proof). No `docker` invocation of any kind before the export. A default-endpoint call STOPS the slice (`PB-2`).

## G1 — Pre-state, migrate, one rebuild, one recreate — lane socket only

Establish read-only pre-state: actual ref/hash, clean tree, running image/container ID/Created/RestartCount, health status/body, served JS/CSS/index hashes, alembic head plus authoritative table counts (`PG-EV-08`: the production observable before AND after — counts per table now, counts per table after, plus the new empty `reminder` table at 0 rows).

Then, through the lane socket only and in this order: apply the pending migration (head must become `20261023_sg233_reminder`), build the backend image exactly once, recreate the backend container exactly once (`PG-PR-04`). No host config changes. Second migrate/build/recreate issuance is STOP. `PG-EV-06`: the only rows this slice's run creates are schema plus zero data rows in `reminder`; application row counts must be identical before and after — quote both.

## G2 — Verify the serve, without claiming more

Observe a new container identity and start time (ID/Created, not RestartCount). Health ok for DB/storage; six health GETs as the standing precedent. Re-read bundle hashes (EXPECTED changed: the Expiry badge ships new JS — record the new hashes, never claim byte-identical), schema head, and table counts; require no slice-caused application row change. Owner-activity deltas get direct discriminating evidence, never hidden.

Suite stays waived per `PG-DP-02`; substitute is post-recreate read-only identity/health/schema/counts/pages verification. Walk the shell routes read-only (`/`, `/expiry` — confirm the Unread reminders section renders — `/inbox`, `/planning`). No writes; no paid calls. Application provider spend prohibited.

## Constraints

- Scope: `docs/worklogs/SG-234*` only. No product/config/schema/migration/test edits. No production INSERT/UPDATE/DELETE, imports or evidence-store mutation. Reads are git / lane-socket docker / curl GETs / read-only SQLite; only executed runtimes are the G0-verified migrate, build and recreate (`PG-IC-01`). Reads/verification ≤120s per command, build ≤600s (inherited precedent); visible timeout finding; idle kill 900s never approached. No prompt or polling loop. No sudo/alternate identity/mount/host config. No secret in any artifact. Runtime-vs-lane budget in seconds from the lane's own stamps (`PG-PR-06`).
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks share no condition with any remediation step — stops win. Reads MAY use the already-built local images only.
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`).

## Acceptance and report

- A1: G0 proven (export + server line) BEFORE any other docker call; one migrate + one rebuild + one recreate THROUGH THE LANE SOCKET; new running-instance proof; health green; explicit deltas (EXPECTED: SG-233 product set served, bundle hashes changed, `reminder` table at 0 rows, all other counts identical); bundle hashes recorded.
- A2: base/hash echoed separately; merged-vs-served diff checked against the EXPECTED SG-233 product set; work diff only SG-234 namespace.
- A3: command logs + report `docs/worklogs/SG-234_report.md`; elapsed per leg vs lane bound; constraints answered; FIRST/DURING/REMAINING dispositioned. First token SG-234.
- A4: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-234 | Report: docs/worklogs/SG-234_report.md`, Work-HEAD recorded, push + mapped read-back. Bound lane receipt only.

## Budget

120s ordinary · 600s build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
