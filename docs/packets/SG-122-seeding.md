# SG-122 — Seed the G3+G4 surfaces through the real write routes, then prove non-empty reads

**Settings travel on the trigger** (`SG-122 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved seeding slice (first of the L3 residual-completion stage; production writes individually covered by D17 — the sensitive-surface word for the live SQLite). SG-121 closed ACTIVATED-EMPTY: five read legs HTTP 200 against globally-zero tables (`location`/`asset_location`/`asset_relation` COUNT 0, `{"items":[]}` ×2, detail keys present-and-`[]` — all committed in `SG-121_verify.log`, which IS this slice's before-capture under `PG-EV-08`). THIS slice creates the minimum rows through the REAL write routes — never raw SQL — then re-runs the SG-121 GETs and quotes row-bearing bodies. Verdicts: SEEDED (all three rows created, all re-run reads row-bearing — the SG-121 REMAINING closes) / PARTIAL (any leg still empty — STOP-and-report, no remediation in-slice) / BLOCKED (a shape mismatch or denial stopped a write — commit, receipt, clean tree). **Exactly THREE mutations exist: one location POST, one assign POST, one relation POST. A fourth mutation of any kind is a STOP.** **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** writes exist ONLY as the three authorized POSTs below + `docs/worklogs` (3 files). No PUT/PATCH/DELETE anywhere — especially no cleanup DELETEs: the created rows are live seed data BY DESIGN (`PG-EV-06`: report them with identifiers, leave them in place; removal is the Architect's decision and this packet does not order it). No builds, no migrations, no flags, no recreate, no `.env` reads or writes, no compose commands. Read-only probes (`docker exec` SELECTs, route GETs) are reads, stated here. A leg needing anything beyond the three POSTs is a STOP for its own word — nothing is improvised here. Secrets: no credential file fetched; identifiers TEXT only.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path (a metered call is a STOP-and-report).
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-EV-08` · `PG-SC-03` · `PG-SC-09` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-01` (reads enumerated with non-mutating forms; the three writes are the authorized mutations) · `PG-PR-03` · `PG-PR-06` · `PG-PR-10`.

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

**DATABASE: LIVE — `/data/db/storagegenie.db`, grant D17, cited here (`PG-PR-10`).** The ONLY live writes are the three POSTs in G1; the before-capture is SG-121's committed empties (`PG-EV-08`). **Restart: none. Deploy: none. Container actions: none** (`docker exec` read-only probes are reads — `PG-IC-01`; any denial is reported as unanswered, never routed around).

## G0 — capability + before-census + shape verification (nothing is written until all three are quoted)

- Capability, non-mutating (`PG-PR-01`): `docker ps` (backend healthy?), health exact, `alembic current` (hypothesis `20260924_sg114_relation (head)` — VERIFY).
- Before-census: `location` / `asset_location` / `asset_relation` COUNT **must read 0/0/0** (`PG-IC-08`: my expectation is exactly zero — a nonzero count in either direction of any table is a STOP-and-report before any write; someone seeded already and the Architect decides). Re-discover live `household_id` + two asset ids via read-only SELECT (SG-121's ids are the expectation, never inherited — `PG-IC-09`).
- Shape verification (`PG-SC-03`: the request schemas are the unread condition — reading them is a GOAL): read the three POST handlers in-tree — `backend/app/api/v1/locations.py:140` (`POST /locations`), `:217` (`POST /assets/{asset_id}/locations`), `backend/app/api/v1/relations.py:113` (`POST /assets/{asset_id}/relations`, 201) — and quote the required body fields as the CODE defines them. Expected (not certain): `{"name": ...}` · `{"location_id": ...}` · `{"to_asset_id": ..., "relation_type": "related_to"}`. A mismatch is a STOP, not an improvisation. What does NOT count as grounds to stop: slow reads, the 422-without-household gate (expected), zero counts (that is the precondition, not a stop).

## G1 — the three POSTs, in order, quoted (on ANY failure here STOP wins over continuing — `PG-IC-03`)

- P1 `POST /v1/locations?household_id=<live-id>` body `{"name":"Kitchen"}` (name from the SG-121 outline; the handler's required fields rule): quote status + body, capture the created location id.
- P2 `POST /v1/assets/<asset-A>/locations` binding that id to asset A: quote status + body.
- P3 `POST /v1/assets/<asset-A>/relations` binding asset A → asset B (`relation_type` `related_to`, the SG-114 vocabulary — VERIFY against the handler): quote status + body, capture the created relation id.
- Report all three created rows WITH their identifiers and LEAVE them (`PG-EV-06` — they are the seed data this slice exists to plant).

## G2 — re-run the SG-121 GETs, quote row-bearing bodies (`PG-EV-02`, `PG-EV-05`)

- `GET /v1/locations?household_id=<live-id>` → must show the Kitchen row (status + body quoted).
- `GET /v1/assets/<asset-A>/relations?household_id=<live-id>` → must show the relation row (status + body quoted).
- Asset detail for asset A → `locations` and `relations` keys must be row-bearing (quoted as found — present-and-empty here is a PARTIAL discriminator, never bent).

## G3 — one verdict line, exactly one

- SEEDED (three rows created with ids quoted, all re-run reads row-bearing — SG-121's REMAINING closes, recommend nothing) / PARTIAL (any re-run read still empty — quote which leg, STOP-and-report, no second attempt in-slice) / BLOCKED (a shape mismatch or denial stopped a write — `BLOCKED:` path taken).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-122.log`, `SG-122_report.md`, `SG-122_verify.log` (raw POST statuses + bodies with created ids, raw GET bodies, before-census counts). First token `SG-122`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for FILE writes; exactly THREE route POSTs for LIVE writes. **Any fourth mutation — a second POST, any PUT/PATCH/DELETE, any SQL write, any code/test/compose/`.env`/migration/STATE/AGENTS touch — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs listings + health + SELECTs + handler reads; G1 needs exactly the three POSTs; G2 needs ≤4 GETs; G4 needs 3 worklog files; nothing else. No criterion demands a rebuild, a recreate, a press, or any metered call — no cell collides; stated so the check exists on paper. Reads explicitly INCLUDE `docker exec <container> <read-only query>`; launching any other runtime or pulling any image is NOT included and is a STOP.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): census, three writes, re-reads, verdict. No second location, no second relation type, no UI proof — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): census — is the tree still in SG-121's empty state, safe to seed? writes — did the real routes accept exactly three rows? re-reads — do the activated surfaces now answer against data?
- Before-census quoted (0/0/0 with the queries, live ids with the SELECTs that found them, handler body fields as the code defines them); any hypothesis miss stated, never bent.
- Three POSTs quoted (status + body + created ids); three created rows reported with identifiers and left in place.
- Re-run GETs quoted (status + row-bearing bodies); exactly one verdict line with the one-line reason.
- No fourth mutation; no vacuous pass (a 201 without a quoted created id evidences nothing — the id is the proof the row exists).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-122 | Report: docs/worklogs/SG-122_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 600s overall; expected ~300s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
