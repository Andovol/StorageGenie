# SG-121 — Non-empty activation probe: do the G3+G4 surfaces answer against real rows

**Settings travel on the trigger** (`SG-121 coder=opencode effort=high`, D16) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D16-approved read-only probe under L2 (the SG-084/SG-116 verification-first precedent). SG-115 (work `7b4ca92`) flipped `SG_LOCATIONS_ENABLED` + `SG_RELATIONS_ENABLED` live and proved activation as a 404→200 transition — against EMPTY lists, disclosed as vacuous in the report. THIS slice closes that REMAINING: it asks whether the G3+G4 surfaces answer against NON-EMPTY data, reading only. Verdicts: ACTIVATED-NONEMPTY (bodies carry rows through the real routes — the SG-115 gap closes) / ACTIVATED-EMPTY (200s, zero rows — a seeding word is owed, recommended as follow-up, NOT implemented here) / DORMANT (404s — regression vs SG-115, STOP-and-report) / INCONCLUSIVE-transient (recommend re-probe). **No write of any kind is made here; no seeding, no migration, no flag, no recreate, no code change.** **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** read-only EVERYTHING except `docs/worklogs` — no POST/PATCH/DELETE/PUT against any route, no `INSERT`/`UPDATE`/`DELETE`/DDL against any database, no builds, no container actions beyond read-only `docker exec` probes, no `.env` reads or writes, no compose commands. Live reads allowed: service GETs on the routes below + read-only `SELECT`/`COUNT` probes via `docker exec` on the backend container. Any leg that needs a write to proceed is a STOP returning for its own word (D16) — seeding is never improvised here. Secrets: no credential file fetched; identifiers TEXT only.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path (a metered call is a STOP-and-report).
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-SC-03` · `PG-SC-07` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04` (no new code — proof scoped to already-running code) · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 60s ordinary, 600s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: live, READ-ONLY — nothing is created, so no grant is cited and `PG-PR-10` needs no row.** A leg needing a write is a STOP for its own word, never an improvised write. **Restart: none. Deploy: none. Container actions: none** (`docker exec` read-only probes are reads, stated here — `PG-IC-01`; any denial is reported as unanswered, never routed around).

## G0 — capability + census BEFORE (nothing moves until this is quoted; `PG-PR-01` with non-mutating forms; `PG-SC-03`: live ids are the unread condition)

- `docker ps` (backend healthy?), health exact, gate 301/401, `alembic current` (hypothesis `20260924_sg114_relation` — VERIFY), table set incl `location` + `asset_location` + `asset_relation` (hypothesis: present from SG-115 — VERIFY).
- Read-only census: row counts for the three G3+G4 tables + live `household_id` / asset-id discovery via `SELECT` (quote the queries AND the counts). No usable id is a finding that re-scopes G1/G2 to what exists — it is NOT grounds to stop. What does NOT count as grounds to stop: zero rows (that is the ACTIVATED-EMPTY evidence, not a stop), slow responses (quoted findings of degradation). What STOPS: a 404 on any activated route (DORMANT — regression vs SG-115, STOP-and-report), a denial on any probe step (reported as unanswered per leg, slice continues).

## G1 — locations legs (real routes, real bodies — `PG-EV-02`, `PG-EV-05`)

- `GET /v1/locations?household_id=<live-id>` (path hypothesis from SG-115 — VERIFY): quote status AND body. If rows exist, GET one location by id and quote it (non-empty proof through the real boundary).
- Asset detail for a live asset: quote the `locations` key as found — rows, empty list, or absent each discriminate the verdict differently (absent key after SG-115's 200s is a finding, never bent to match).

## G2 — relations legs (same discipline)

- `GET /v1/assets/<live-asset>/relations?household_id=<live-id>` (path hypothesis from SG-115 — VERIFY): quote status AND body. If rows exist, the body itself is the non-empty proof; quote the narrowest row-bearing fragment that still shows provenance.
- Asset detail for the same asset: quote the `relations` key as found, same three-way discrimination as G1.

## G3 — one verdict line, exactly one

- ACTIVATED-NONEMPTY (bodies carry rows through the real routes — SG-115's REMAINING closes, recommend nothing) / ACTIVATED-EMPTY (200s, zero rows everywhere counted — recommend the seeding follow-up with the one-line reason non-empty proof is still owed, implemented nowhere here) / DORMANT (any 404 — regression, STOP-and-report, no verdict beyond it) / INCONCLUSIVE (transients on every leg — recommend re-probe, never a write).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-121.log`, `SG-121_report.md`, `SG-121_verify.log` (raw statuses + raw bodies, key bytes never — none are touched). First token `SG-121`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for WRITES. READS: live service GETs on the named routes + read-only `docker exec` SELECTs — all read-only, each named above. **Any write anywhere else is a STOP** — routes, DB, code, tests, prompts, compose, `.env`, migrations, STATE/AGENTS.
- Cross-product (`PG-IC-01`): G0–G2 need container-listing + health/gate GETs + ≤6 route GETs + read-only SELECTs + 3 worklog files; nothing else. No criterion demands a write, a second probe shape, a press, or any metered call — no cell collides; stated so the check exists on paper. Reads explicitly INCLUDE `docker exec <container> <read-only query>`; launching any other runtime or pulling any image is NOT included and is a STOP.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): census, legs, verdict. No seeding is implemented here, however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): census — what does the live tree hold to probe against? legs — do the activated surfaces return rows or only statuses? verdict — is SG-115's activation real against data?
- Capability + census quoted (health, gate, alembic version, table counts, live ids with the queries that found them); any hypothesis miss from §G0 stated, never bent.
- Every executed GET quoted (status + body or body fragment); every `locations`/`relations` detail key quoted as found (rows / empty / absent).
- Exactly one verdict line with the one-line reason; ACTIVATED-EMPTY carries the seeding follow-up outline, implemented nowhere here.
- No writes of any kind; no vacuous pass (a 200 against an empty table evidences ACTIVATED-EMPTY — it never evidences non-empty activation).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-121 | Report: docs/worklogs/SG-121_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 600s overall; expected ~300s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
