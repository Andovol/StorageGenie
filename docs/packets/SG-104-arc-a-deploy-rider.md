# SG-104 — Arc A deploy rider: rebuild + migrate + one recreate + verify, one live press (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D142-approved Arc A deploy rider (production restart + production writes, G-K2) closing Arc A: SG-099 (synthesis caller) + SG-100 (snapshot model/migration, UNAPPLIED in production) + SG-101 (text-path fix) + SG-102 (snapshot wiring) + SG-103 (alternates) are committed but the running service still serves the SG-096 image. THIS slice rebuilds + migrates + recreates + verifies, nothing else. NO code changes — any diff outside `docs/worklogs` is a STOP. Migration is MANUAL on this lane (verified 2026-09-23: image `CMD` is bare uvicorn, `backend/Dockerfile:22`; no startup auto-migrate anywhere in `backend/app` — re-verify, don't inherit): the vehicle is a one-off `run --rm` upgrade, never a second recreate. **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-23); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** rider ONLY. One rebuild + one migration + exactly ONE recreate + verify. Production writes AUTHORISED by D142 (owner quote "D142 - approved."): (a) a timestamped file-level backup copy of the live SQLite BEFORE any write; (b) `alembic upgrade head` (one new table, additive — no existing-table touch); (c) exactly ONE verification Enrich press (Job + Candidate + snapshot rows, reported with ids, left in place — that press IS the Arc A exit proof). `PG-PR-10`: the database is `sqlite:////data/db/storagegenie.db` (compose bind `./data/db`), grant D142, cited here. Anything beyond (a–c) is a STOP. $0 except the press's own Jina spend under the per-press cap.
**Money posture:** REAL metered spend, ONE verification press, Jina actuals under the $0.05 per-press cap (actual-vs-budget with units, `PG-PR-06`); build/recreate $0.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-09` · `PG-SC-11` · `PG-SC-12` · `PG-DP-01` · `PG-DP-02` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (THIS DEPLOY stated) · `PG-PR-06` · `PG-PR-10` (D142 cited).

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s build, 600s migrate+recreate+verify, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: the live SQLite for (a–c) above under D142, read-only otherwise.** **Restart: ONE backend recreate (D142). Deploy: THIS slice.**

## G0 — backup BEFORE any write (restores are incidents, never cleanup)

- File-level copy of the live DB (`storagegenie.db` + `-wal`/`-shm` if present) to a timestamped directory OUTSIDE the live DB dir and OUTSIDE version control (never force-add, `PG-SC-10`): quote bytes + `sqlite3 … "PRAGMA integrity_check"` on the COPY (never the live file). If the copy or the check fails: STOP, no migration, no recreate.

## G1 — capture BEFORE (every observable the proof moves)

- Image id + backend `RestartCount`, served frontend bundle name+size+sha256 (EXPECTED byte-identical AFTER — SG-099→103 touched no frontend; a difference is a STOP-and-report finding), `alembic current` (expected single head `20260917_sg068_saved_search` — verify), 24-table counts + DB bytes, gate (http 301 / https 401 without login), health exact, one Enrich-route shape probe (in-process, no press). Quote all raw — a production-change claim without a before-capture is not a claim (`PG-EV-08`).

## G2 — rebuild + one-off migrate + ONE recreate

- Rebuild the backend image from the committed tree (build log quoted; it must show the SG-099 prompt, `synthesize.py`, `snapshots.py`, `enrich_snapshot` model + SG-100 migration, SG-101 adapter hunks, SG-102/103 endpoint hunks entering the image — grep the build context, raw). Exactly ONE `up -d` recreate of the backend service, and it happens AFTER the migration run below (so the first start already sees the table).
- Migrate via a one-off container of the NEW image (`run --rm` + `alembic upgrade head` against the live DB path — this is the migration vehicle, NOT a second recreate): quote `alembic current` before (`sg068`) and after (`sg100`), plus the new table present with 0 rows. If history shows any head you did not expect: STOP, do not upgrade.
- `BUILDX_CONFIG` relocation to a writable tmp is allowed if confinement denies it (SG-067 precedent); anything else denied is `unanswered`, never routed around.

## G3 — verify AFTER + the ONE live press (Arc A exit proof)

- Image id DIFFERS, fresh container from the NEW image id (`docker ps` + `docker images` quoted), `RestartCount` +1, loopback-only preserved, health exact, gate 301/401, bundle IDENTICAL to G1 BEFORE, `alembic current` = new head, counts = BEFORE + exactly the press rows below, DB bytes moved only by (a–c).
- In-image proof (`PG-SC-12` — decode what the consumer runs): the synthesis prompt + caller + snapshots writer + model importable through the REAL runtime loaders inside the fresh container; `GET /v1/candidates/{candidate_id}` shape live. `docker exec` into the fresh backend container and one `docker run --rm` inspection ARE reads for this packet (`PG-IC-01` decided either way).
- THE press: ONE `POST /v1/enrich/{asset_id}` at loopback (no nginx login needed there; the gate is proven separately) for ONE production asset WITH identifier TEXT — enumerate qualifying assets first (a list is a fact too: name the criterion — brand+name/barcode TEXT in the Popescu household — enumerate on target, pick one, report it). Consent on, spend under the per-press cap, actuals quoted. Assert: 200 + `candidate_id` + `snapshots_recorded: True` + rows readable (Job + Candidate + ≥1 snapshot, ids quoted, LEFT in place per `PG-EV-06` — report them, never delete). No synthesis call rides the press (endpoint path only). No second press for any reason.
- Full-suite sweep WAIVED (`PG-DP-02` — restart-gated; externally-driven tests would exercise the previous build); substitute: targeted in-process enrich legs by node ID against the new build; name the post-restart run as the authority.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-104.log`, `SG-104_report.md`, `SG-104_verify.log` (raw outputs + before/after captures + every gate). First token `SG-104`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** press actuals); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for WRITES. Everything else is commands (backup/migrate/build/up/probes/press), never edits. **Any file edit outside `docs/worklogs` is a STOP.**
- Cross-product (`PG-IC-01`): G0–G3 need DB-file/backup reads+writes + `docker` build/run/exec + gate/health/count probes + the one press; nothing else. No second press, no synthesis call, no frontend change, no second migration.
- `PG-DP-01`: the delivery path (image) is changed BY the delivery path (rebuild) — permissive-additive only (new files + additive hunks; the adapter hunks change text-path behaviour, disclosed as the D140 fix going live, not as a behaviour surprise).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): backup, rebuild, migrate, one recreate, verify, one press. Nothing else.

## Acceptance criteria

- G0 backup quoted + integrity OK before any write; G1 before-captures quoted for every observable.
- One rebuild (Arc bytes in-image) + one-off migrate (`sg068`→`sg100`, table present, 0 rows) + exactly ONE recreate; image differs, RestartCount +1, health/gate/counts as stated, bundle identical to BEFORE.
- ONE press: 200 + gated candidate + `snapshots_recorded: True` + rows reported with ids and left; Jina actuals under cap; no second press.
- $ as stated; full sweep waived with substitute named; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G0 — can we roll back? G1 — what did production look like before? G2 — was exactly the authorised sequence performed with the Arc bytes in the image? G3 — is the new build live, migrated, and serving real Enrich proposals?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** press actuals. Actual-versus-budget per leg with units (`PG-PR-06` stated against the build/migrate/recreate bounds).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-104 | Report: docs/worklogs/SG-104_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s build · 600s migrate+recreate+verify · 1800s overall; REAL metered ONE press under the $0.05 per-press cap; actual-versus-budget per leg with units.
