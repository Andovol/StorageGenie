# SG-106 — presentation rider: rebuild + one recreate + verify, serves the SG-105 UI (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D146-approved presentation rider (production restart, G-K2; owner quote "D1 - approved"): SG-105 (UI centering + consistency, work `3b18e93`) is committed but the running service still serves the SG-104 image with the old bundle. THIS slice rebuilds + recreates + verifies, nothing else. NO code changes — any diff outside `docs/worklogs` is a STOP. NO migration: SG-105 touched no `models/`/`alembic/` (prove by empty diff — the migration vehicle stays parked; if `alembic current` shows any head you did not expect, STOP, do not upgrade). Last separate rider by D145 (slices own their refresh from now on). **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-23); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** rider ONLY. One rebuild + exactly ONE recreate + verify. No migration, no backup (no DB write of any kind — the volume persists across the recreate; a write you did not intend is a STOP), no live press, no synthesis call, no container action beyond the single recreate. $0, no network beyond loopback probes, no secrets anywhere; `docker compose config` FORBIDDEN (`PG-SC-05` by family — it prints secrets; no compose config read is needed for this slice).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-SC-09` · `PG-SC-12` · `PG-DP-01` · `PG-DP-02` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04` (THIS DEPLOY stated) · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s build, 600s recreate+verify, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (read-only counts/health probes only — a write of any kind is a STOP). **Restart: ONE backend recreate (D146). Deploy: THIS slice.**

## G1 — capture BEFORE (every observable the proof moves)

- Image id + container id, served frontend bundle name + size + sha256 (EXPECTED to DIFFER after — SG-105 touched frontend; byte-identical would be the STOP-and-report finding here, the inverse of the SG-104 premise), SG-105 marker ABSENCE in the served bundle (`page-container`, `THEMED_CONTROL_CLASS`, `Uncategorized (` — grep the served assets, raw), `alembic current` (expected `sg100` — verify, don't inherit), 24-table counts + DB bytes, gate (http 301 / https 401 without login), health exact. Quote all raw — a production-change claim without a before-capture is not a claim (`PG-EV-08`).

## G2 — rebuild + ONE recreate (no migration)

- Rebuild the image from the committed tree (build log quoted; it must show the SG-105 frontend hunks entering the build context — `PageContainer.tsx` + the SG-105 edited screens, raw). Exactly ONE `up -d` recreate of the backend service. No `run --rm` migration of any kind (nothing to migrate — the upgraded table already exists with its rows from SG-104).
- `BUILDX_CONFIG` relocation to a writable tmp is allowed if confinement denies it (SG-067 precedent); anything else denied is `unanswered`, never routed around.

## G3 — verify AFTER (the UI is served)

- Image id DIFFERS, fresh container from the NEW image id (`docker ps` + `docker images` quoted), loopback-only preserved, health exact, gate 301/401, counts = BEFORE exactly, DB bytes unmoved (no write happened — any movement is a finding).
- Served proof (`PG-SC-12` — decode what the consumer runs): the served bundle name/sha DIFFERS from G1 BEFORE, and the G1-absent SG-105 markers are now PRESENT in the served assets (quoted hits); `GET /v1/health` exact through the fresh container; one catalog-list shape probe (read-only, existing route) proving the fresh server answers.
- `PG-DP-01`: the delivery path (image) is changed BY the delivery path (rebuild) — the going-live behaviour deltas are the disclosed SG-105 set (centered pages, themed controls, one brand row, content-sized cards, `Uncategorized` pills) — no surprise behaviour, said in as many words.
- Full-suite sweep WAIVED (`PG-DP-02` — restart-gated; externally-driven tests would exercise the previous build); substitute: the build itself + the container-side probes above; name the post-restart run as the authority.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-106.log`, `SG-106_report.md`, `SG-106_verify.log` (raw outputs + before/after captures + every gate). First token `SG-106`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for WRITES. Everything else is commands (build/up/probes), never edits. **Any file edit outside `docs/worklogs` is a STOP.**
- Cross-product (`PG-IC-01`): G1–G3 need image/container/bundle reads + `docker` build/run + gate/health/count probes; nothing else. No second recreate, no migration, no press, no config dump.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): rebuild, one recreate, verify. Nothing else.

## Acceptance criteria

- G1 before-captures quoted for every observable, markers absent before.
- One rebuild (SG-105 bytes in-image) + exactly ONE recreate; image differs, health/gate/counts as stated, DB bytes unmoved, `alembic current` still `sg100`.
- Served bundle DIFFERS with all three SG-105 markers present; fresh server answers health + one read-only list probe.
- $0 as stated; full sweep waived with substitute named; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — what did production serve before? G2 — was exactly the authorised sequence performed with the UI bytes in the image? G3 — is the new UI actually served?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units (`PG-PR-06` stated against the build/recreate bounds).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-106 | Report: docs/worklogs/SG-106_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s build · 600s recreate+verify · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
