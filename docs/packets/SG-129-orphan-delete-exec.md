# SG-129 — Orphan delete via the container (writable context): probe, delete the 14, prove serving

**Settings travel on the trigger** (`SG-129 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved slice (eighth of the L3 residual-completion stage; SG-128 BLOCKED 98). SG-128 completed the enumeration (14 orphan `_thumb*.png`, 904,254 bytes, suffix distribution `{'png': 14, 'jpg': 2}`, per-file verdicts in `SG-128_verify.log`) but the delete was denied EROFS — the Coder sandbox mounts `/` read-only and only the worktree is `rw`. The container is the writable context: the backend mounts the same volume `rw` at `/data/storage` (SG-128: host `/home/andrei/.local/share/docker/volumes/storagegenie_storage_data/_data`; `docker exec` SELECTs/ps already proven from this lane). THIS slice deletes through `docker exec` on EXACT paths — explicitly authorized here, never a workaround: the mechanism is planned, quoted, and bounded below. **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** probe-then-delete ONLY. No code change, no migration, no rebuild, no recreate, no key, no metered call ($0 — a metered call is a STOP-and-report). Originals never candidates; `.tmp` files never candidates; host-path writes never attempted (known EROFS — do not re-prove it). A delete outside the enumerated set is a STOP.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-SC-03` · `PG-SC-07` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-01` · `PG-PR-03` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none written; live reads only for the served check. STORAGE: the live volume THROUGH `docker exec storagegenie-backend-1` ONLY (host path never written — known EROFS). DELETE of the enumerated set only, grant D17 (`PG-PR-10`: volume `storagegenie_storage_data` at in-container `/data/storage`, grant D17, stated here). Restart: none. Deploy: none. Container actions: exec for delete + probe ONLY (no restart, no image pull, no shell beyond the quoted commands).**

## G0 — re-verify enumeration + writability probe (no delete until both are quoted — `PG-SC-03`)

- Re-list `*_thumb*` through the container (`docker exec storagegenie-backend-1 ls .../storage/...` — derive the in-container thumb dir from `/data/storage`, quote the mapping host→container). Diff against SG-128's 14-path list: identical expected — ANY delta (new thumbs, missing files, a new suffix class) is a STOP before any delete (`PG-IC-08`: expectation is that exact list, either direction stops).
- Re-verify the reader premise (`.jpg`-only resolution) — one read; if changed, STOP.
- Writability probe: `docker exec ... touch /data/storage/<household>/.__sg129_wtest && rm ...` — create AND remove in the same leg, quoted. Denied → STOP (ship the re-verified enumeration). Zero orphans present → clean verdict, ship it (`PG-SC-07`).
- What does NOT count as grounds to stop: volume size drift from new uploads (only thumb-set membership matters), slow exec (quoted finding).

## G1 — delete exactly the enumerated set via container exec

- Delete the 14 paths (or the re-verified set if G0 re-scoped by STOP — no: any delta STOPS; the set is SG-128's 14 or nothing) by EXACT in-container path, no globs at delete time. Quote every command + output. Before/after `*_thumb*` listing quoted; bytes-reclaimed quoted.
- `PG-EV-06` spirit: every deleted path + size reported; the probe file's create+remove quoted (it is not an orphan, it is the probe — never counted).

## G2 — served regression check (no status may flip 200→404 — `PG-EV-02`)

- Per-evidence thumb GETs BEFORE (G0) and AFTER: identical tables required. A 200→404 flip is a STOP-and-report (no re-upload, no restore — report it). Pre-existing 404s staying 404 is unchanged, quoted as such.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-129.log`, `SG-129_report.md`, `SG-129_verify.log` (enumeration + probe + deletes + status tables). First token `SG-129`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for FILE writes; the enumerated live-volume deletes + one probe create/remove for STORAGE writes. **Any other write — code, tests, originals, `.tmp` files, host paths, DB, config — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs exec listing + reader read + probe; G1 needs exact-path exec deletes; G2 needs route GETs; nothing else. No criterion demands a rebuild, a DB touch, a key, or any metered call — no cell collides; stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): re-list, probe, delete the list, prove the serving. No re-uploads, no writer changes — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): enumerate — does SG-128's list still match the volume exactly? probe — can this context delete? serve — did any served status move?
- Enumeration diff quoted (identical or STOP); probe create+remove quoted; every deleted path + size quoted; volume before/after quoted.
- Status BEFORE == AFTER with no 200→404 flip; $0.000000; no code diff of any kind (prove by empty product diff or STOP); no vacuous pass (a delete proved only by `rm` exit codes evidences nothing — the before/after listings are the proof).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-129 | Report: docs/worklogs/SG-129_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s overall; expected ~300s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
