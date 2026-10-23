# SG-233 — expiry reminders that reach the user: store plus daily compute plus in-app sender (no email)

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** Every run uses scratch temp SQLite plus temp storage; the production SQLite is touched by nothing. **Restart: none.** No service, container, nginx, or host timer operation of any kind.

**Settings ride the trigger, never this packet** (retired packet fields are refused at admission): the approved envelope is already on the trigger command. **Authoring date (metadata, never a gate):** 2026-10-23. Transport: the standard job_spawn lane.

**Context and standing lines.** Owner-approved slice D1 (2026-10-23, L2): row 9 of `docs/ROADMAP.md` — sender plus schedule on top of the existing urgency math. Purpose: turn the computed urgency into reminders the user actually sees. Expected premises, all re-verified by the Architect in-tree before writing and to be re-verified in-slice per `PB-1` (a difference is a finding, not an obstacle): (a) `backend/app/services/expiry_engine.py:1-8` is pure computation — header states no scheduler, no sender, no table — with `tier_for`/`bucket_for` over live `CATEGORIES[slug].tier_defaults` (tier windows DECLARED UNCALIBRATED per `G-A9`); (b) the dashboard `frontend/src/routes/ExpiryPage.tsx` renders buckets plus unresolved rows and nothing pushes to the user; (c) `User.email` is nullable (`backend/app/models/user.py:16`), seed uses `example.com` addresses, and no SMTP/queue/scheduler exists anywhere in `backend/app/` (grep `remind|notify|sender|schedule|smtp|push` over `backend/` returns only engine-header, tier-profile, and seed/test hits — no delivery path); (d) the status read is `GET /v1/plugins/expiry-tracker/status` (`backend/app/api/v1/plugins.py:64-95`) over accepted `YYYY-MM-DD` assertions only; (e) routers register in `backend/app/main.py:67-83` (reminders adds one line there); (f) contract recorded `0.50.0` == packet-cache tag `contract-v0.50.0`; installed harness copy echoes `0.51.0` (BEHIND, recorded at session start — echo verbatim whatever your copy says and report WHICH version string and source path you read; a difference is a finding, not an obstacle). **Authoring date (metadata, never a gate):** 2026-10-23. Transport: the standard job_spawn lane. Email is an explicit NON-GOAL this slice (needs owner SMTP creds plus production-secret sign-off, `G-K2` — a second slice, never smuggled in here).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no provider calls ($0 — a metered call is a STOP-and-report); no new dependencies; no auth/household/password shape change (single-household server, no passwords by design); NETWORK: loopback plus container-runtime only, nothing else.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (Architect copies these to the rating row):** `PG-EV-01` seen-to-fail · `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-05` property-not-command · `PG-EV-06` rows-your-run-creates · `PG-EV-09` both-runs-committed · `PG-EV-13` base-settings · `PG-SC-02` new-field-to-readback · `PG-SC-05` rule-not-literal · `PG-SC-09` name-the-world · `PG-SC-12` real-thing · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-10` which-database.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

## Why this exists

Row 9 is Partly built: the engine tiers every accepted date and the Expiry page groups them, but nothing reaches the user before food or medicine expires — the core promise of the tracker. No sender and no schedule exist anywhere in `backend/app/` (confirmed by grep this session; re-verify in-slice and quote your grep). This slice adds the smallest delivery pipe that proves the loop: one durable store, one daily compute over the real engine, one in-app sender (unread list plus badge). Email stays out until the owner binds SMTP creds.

## G1 — reminder store (migration plus model)

- New `reminder` table by migration: `id, household_id (FK household.id, index), asset_id (FK asset.id, index), as_of_day (YYYY-MM-DD string), tier (nullable string), bucket (string), days_remaining (int), status (unread/read/dismissed, index), created_at/updated_at`. Unique on `(asset_id, as_of_day)` — one row per asset per day max.
- Migration naming follows the repo convention (`backend/alembic/versions/<date>_sg233_*.py`); enumerate the current heads in-slice and place the new head correctly — the packet's filename sketch is an expectation, your enumeration is the authority (a list is a fact too: report yours either way).
- Downgrade drops the table. Upgrade plus downgrade plus upgrade runs green on temp SQLite.
- New `backend/app/models/reminder.py` mapped exactly onto the migrated table (one model, no extra tables, no column outside this list — an extra column is a STOP-first finding).

## G2 — daily compute over the real engine (production writer named)

- New `backend/app/services/reminders/service.py` with ONE production writer, `record_due(db, household_id, as_of_day)` (name it this or report why the name differs): loads `expiry_engine.compute_status(db, household_id, as_of_day)` — the REAL engine, never a re-implementation — and inserts one `unread` row per tiered `rows` entry missing for that `(asset_id, as_of_day)`. Unresolved rows NEVER create reminders. Each row records the tier string plus the window days it fired under (from the live category `tier_defaults`) so mistunes stay visible.
- Idempotence is structural: re-running the same `as_of_day` inserts zero rows (unique guard, proven by two consecutive runs, `PG-DP-04` shape applied to the writer).
- `as_of_day` defaults to today UTC read from the live clock at execution; tests pass explicit dates inline, never a fixed production date (`PG-IC-07`).

## G3 — in-app sender (API plus badge, no email)

- New `backend/app/api/v1/reminders.py`: `GET /v1/reminders?household_id=` (unread-first, urgency-sorted, household-scoped 403 on mismatch like the neighboring `_owned` reads) and `POST /v1/reminders/{id}/read` plus `.../dismiss` (legal transitions only; illegal 422). Register with ONE line in `backend/app/main.py` beside the existing `include_router` lines — any other hunk there is a STOP.
- `GET` is the read-back that closes `PG-SC-02`: every stored field (asset, date, tier, bucket, days, status) is readable through it; the acceptance names this route, never "it persists".
- Frontend: `ExpiryPage.tsx` gains an **Unread reminders (N)** section reusing the existing row renderer plus `api/client.ts`/`api/types.ts` thin typed wrappers. No new route, no new dependency, no notification permission prompt, no email form anywhere — an email-shaped string in the diff is a FAIL.

## G4 — proof (FAIL-then-PASS both runs committed, real routes, no live rows)

- New `backend/tests/test_sg233_reminders.py`: (a) due fixture (accepted food date 3 days out) yields exactly the expected unread row with tier `urgent`/bucket `this-week` through the REAL `POST`/`GET` routes on temp SQLite via the committed migration; (b) unresolved fixture (proposed date) yields zero rows; (c) second identical compute inserts zero rows; (d) read plus dismiss transitions verified through the API with an illegal-transition 422 leg. `PG-EV-01`: the discrimination leg is inverted in-slice (wrong-tier expectation shown failing) and quoted.
- FAIL-then-PASS: the new nodes FAIL on the start-base tree and PASS on the candidate; BOTH raw runs are committed into `docs/worklogs/SG-233_verify.log` (`PG-EV-09` — prose quotes do not satisfy this). Base runs need no secret files: temp SQLite plus temp storage only (`PG-EV-13` — state the construction).
- Full backend suite runs ONCE on the candidate; on the base only the new nodes run (their FAIL half). An old row red on the candidate is run alone on the base before any verdict. `ruff` clean; `mypy` delta zero in touched files; frontend `tsc` plus `vite build` green for the badge hunk.
- Secret scan over the diff plus `grep -rniE 'smtp|password|secret|api[_-]?key' backend/app/services/reminders backend/app/api/v1/reminders.py` quoted with hits-or-empty; a hit is a finding with a destination, never silent. `PG-EV-06`: the slice creates rows in temp datastores only, discarded with the temp dir — nothing to leave or remove in production; production rows created: zero by construction.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-233.log`, `{{WORKLOG_DIR}}/SG-233_report.md`, `{{WORKLOG_DIR}}/SG-233_verify.log` (BOTH raw FAIL and PASS runs). First token `SG-233`; elapsed-versus-budget per leg with units; MODEL plus effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); contract version echo plus the source path read; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/models/reminder.py` (new) · `backend/alembic/versions/` (ONE new migration only) · `backend/app/services/reminders/*` (new dir only) · `backend/app/api/v1/reminders.py` (new) · `backend/app/main.py` (registration line only) · `frontend/src/routes/ExpiryPage.tsx` plus `frontend/src/api/client.ts` plus `frontend/src/api/types.ts` (badge plus wrappers only) · `backend/tests/test_sg233_reminders.py` (new) · `docs/worklogs` (3 files). **Anything else is a STOP** — including providers/reader/enrich/chat/planning/export/auth/users/households, compose files, `.env`, nginx, host timers, and any email/SMTP shape.
- **Rule-not-literal (`PG-SC-05`):** exclusion is by the rule "no file outside the expiry-reminder read path (engine → reminder store → reminders API → Expiry badge) plus its migration, tests, and worklogs". Grep-gate the literals as the check, never the rule: the suite asserts `git diff --name-only` output against this ceiling and fails on any other path (quote the gate plus its output).
- Cross-product (`PG-IC-01`): no blanket exclusion is issued; every acceptance criterion names a ceiling file above. G-hunks share no condition with any remediation step — stops win. Reads MAY use the already-built local images only; pulling or running any image the packet does not name counts as a runtime launch — NOT authorized here, STOP and report instead.
- How code becomes live (`PG-PR-04`): it does NOT — no deploy, no restart, no host timer in this slice; proof is temp-route plus suite only, and the report states the running service still serves the previous build.
- Budget (uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`): 120s per command · 600s suite+build · 1800s overall — actual-versus-budget per leg with units. Hang bound `PB-5`: as stated here.
- Simplicity (`G-A7`): one table, one writer, two endpoints, one badge. No scheduler daemon, no email, no new job-type machinery beyond calling the writer from an explicit function the next slice can schedule.
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution with the date passed as an explicit argument in tests (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt is STOP-first); packet premises re-verified in-slice with quoted reads — in particular the engine no-sender header, the tier-defaults block, the grep proving no sender/schedule, the status route, and the `main.py` router block (`PG-IC-09`).
- Q1 (store): migration upgrades/downgrades/upgrades on temp SQLite with the unique `(asset_id, as_of_day)` proven by a refused double-insert; model maps the table exactly.
  Q2 (compute): due fixture creates exactly the expected unread rows via the production writer `record_due()` through the real engine; unresolved fixture creates none; re-run inserts zero.
  Q3 (sender): unread list plus read/dismiss round-trips through the real routes with household-mismatch 403 plus illegal-transition 422 legs; badge renders the count.
  **Worlds named (`PG-SC-09`):** passes-but-wrong = a writer that inserts its own fixture-shaped rows without calling `compute_status` (ruled out by asserting engine-shaped tier/bucket plus a mutation leg that moves the fixture date and changes the row); working-but-fails = a user reading then dismissing the same reminder (ruled out as a delta from the captured unread baseline, not an absolute count).
- Property-not-command (`PG-EV-05`): the claimed properties are "one row per asset per day", "unresolved creates nothing", "unread count equals badge count" — each checkable against the committed temp artifacts, never satisfied by an exit code alone.
- Candidate suite plus `ruff` plus `mypy`-delta-zero plus frontend build green (only base-proved reds, each cited with base commit plus base-run output); secret scan empty and quoted; diff touches ceiling paths only (gate quoted); prod DB untouched by construction (`DATABASE: none` plus temp-dir evidence); no migration beyond the one; no dependency change; no ignored file staged; nothing pushed to any evidence ref; no vacuous pass (`PB-3` — an empty reminder set on a due fixture is a FAIL, not a pass).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref:** push the work to `automation`, worktree clean (`CO-55`). Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-233 | Report: docs/worklogs/SG-233_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s per command · 600s suite+build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
