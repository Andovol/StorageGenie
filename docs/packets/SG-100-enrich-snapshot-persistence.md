# SG-100 — Enrich snapshot persistence: model + migration + append-only writer ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D139-approved L3 Arc A slice 2 of 4 (SG-099 GREEN-offline/PARTIAL-live → persistence → live re-confirms + reviewer alternatives). SG-099 shipped the synthesis caller with output RETURNED-never-stored (`PG-SC-02`); SG-081/082 fetchers return in-memory snapshots; SG-098's endpoint serves from memory. THIS slice persists snapshots: one new table + migration + append-only writer + a committed brand-absent OFF fixture (F-SG099-2). NO endpoint wiring (the endpoint reads memory until the live re-confirms slice — said explicitly), no live calls of any kind ($0 — scripted transports only; a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-23); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** persistence ONLY. No synthesis-prompt/caller changes (read-only pattern sources), no endpoint/UX reads or writes, no deploy, no restart, no container action. Migration file ONLY — it is NEVER applied to production here (tests run it on temp DBs; production migration rides a later owner-gated rider, `PG-PR-04`). Key NAMES only, never bytes; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-10` · `PG-SC-11` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (ONE new migration file; applied to temp DBs in tests only — production migration rides a later owner-gated rider. No `UPDATE/DELETE/INSERT` against production in any form; temp rows reported and removed, `PG-EV-06`). **Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`).

## G1 — snapshot model + migration (append-only, verbatim)

- New `backend/app/models/enrich_snapshot.py` on the `provider_call.py` pattern (verified 2026-09-23 — re-verify: `TimestampMixin + Base`, `String(36)` PK `default=new_id`): one row per fetch — source name (`off` | `jina`), query text (brand+name, never photos/GPS), request URL, retrieved-at, verbatim raw body (`Text`), raw text (`Text`, nullable), version/correlation id, NO update path (corrections are new rows — the enrichment plan §3 rule, restated not re-decided). Export in `models/__init__.py` (name + `__all__`, same file).
- ONE new alembic migration chaining from the CURRENT head — read `backend/alembic/versions/` in-slice, do NOT inherit my listing (`20260917_sg068_saved_search.py` was last verified 2026-09-23): upgrade creates the table, downgrade drops it, head-relative (`PG-SC-11` — grep every end-relative assertion over the touched files and list the hits in-slice).
- `PG-SC-02` read-back, stated whole: rows are written by G2 and read back in-slice through the writer's own `get_*` loader + test queries; the ENDPOINT does not read this table until the live re-confirms slice (that absence is the design, not a gap).

## G2 — append-only writer (library, unwired)

- New `backend/app/services/enrich/snapshots.py`: `record_off_snapshot(db, OffSearchSnapshot) -> row` + `record_jina_snapshot(db, JinaSearchSnapshot) -> row` (exact snapshot fields verified on target first — `client.py:49-59` OFF shape verified 2026-09-23, `jina.py:62-90` read in-slice; a field-name difference is a finding, never a bend). Verbatim body stored unmodified (byte-compare test against the input); degraded snapshots (`no_result_reason` set) record LOUDLY with the reason, never silently dropped; no overwrite function exists anywhere in the module.
- No existing-file edits expected; a touch elsewhere ships ONLY on failing-test proof, minimal + root-cause + disclosed (suite-green binds on collision, M45) — anything else is a STOP.

## G3 — tests + gates ($0, temp DBs only)

- New `backend/tests/test_sg100_snapshot_persistence.py` (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; new checks fed deliberately wrong inputs and shown failing in the same run, `PG-EV-01`): migration upgrade→downgrade→upgrade on a temp DB (following the SG-035 migration-test precedent — locate it by grep, name it in-report); writer round-trip per source (stored body byte-equal to input; degraded snapshot recorded with reason); second write of the same query creates a SECOND row (append-only, never update); loader `get_*` reads back by id/source; suite sees the new table through derived metadata (no static table list touched — SG-088 rule).
- Committed `backend/tests/fixtures/enrich/off_absent_brand.json` (F-SG099-2 — the SG-099 derivation made a file: committed OFF hit minus `brands`, byte-pinned by a test asserting absence + parity otherwise).
- Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-100.log`, `SG-100_report.md`, `SG-100_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate). First token `SG-100`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** new model file + `models/__init__.py` export hunk + ONE migration + new writer module + new test file + ONE fixture file + `docs/worklogs` (3 files) — NOTHING else (existing-file touch only on M45 terms above). Ordered paths committable per `.gitignore` (verified 2026-09-23: none ignored, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands a live call, endpoint read/write, deploy, restart, or container act — no cell collides; stated so the check exists on paper. Reads include TestClient + host commands only; pulling/running images or launching unnamed runtimes counts as execution — not authorised.
- Privacy: fixture TEXT only; key never in any file, log, or assertion (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture timestamps are sample data; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Migration chains from the live head, upgrades/downgrades/upgrades on temp DB; table holds verbatim bodies byte-equal; re-write appends, never updates; loader reads back; degraded snapshots recorded with reason.
- Brand-absent fixture committed with absence+parity pins.
- Tests fail-pre/pass-post both committed raw; gates green; $0; production untouched; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — does the schema hold verbatim history? G2 — does the writer append without ever overwriting? G3 — is it proven on temp DBs with zero live touch?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-100 | Report: docs/worklogs/SG-100_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
