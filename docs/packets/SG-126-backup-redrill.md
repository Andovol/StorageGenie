# SG-126 — Backup re-drill: prove the manual runbook still holds (read-only, restore-to-temp)

**Settings travel on the trigger** (`SG-126 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved slice (fifth of the L3 residual-completion stage; SG-125 instrument 98). D118 kept backups MANUAL (runbook stays manual until loss-risk justifies scheduling) — SG-086 built the drill (script + test + README runbook) and THIS slice re-proves it still holds after 40+ landed slices, changing nothing unless drift is found. **Authority (G-K2, D17 stage): production READ authority ONLY — read-only DB + storage copy, restore lands on TEMP paths only, never the live paths; no `UPDATE/DELETE/INSERT` against production in any form.** Restoring production from backup is an incident, never silent cleanup (`CO-42` — quote it verbatim in the report). Expected artifacts, all to be re-verified on target (never inherited): drill script `backend/scripts/backup_restore_drill.py` (SG-125 quoted it), test `backend/tests/test_backup_drill.py`, README runbook section. **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** drill ONLY. No migration, no schema change, no secrets in logs, no deploy, no restart, no provider calls, $0. A stale runbook (moved paths, renamed volume) is a FINDING first: fix it only with a surgical quoted README/script hunk inside the ceiling below, else report it unrepaired. `PG-PR-04` — no code becomes live; proof is scoped to this host run.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-SC-03` · `PG-SC-09` · `PG-SC-11` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` · `PG-PR-03` · `PG-PR-04` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite/copy, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: the host's live SQLite (READ-ONLY under the D17 grant above) + temp copies; production is never written (`PG-PR-10`: database `/data/db/storagegenie.db`, grant D17, stated here). Restart: none. Deploy: none.**

## G0 — capability enumeration, non-mutating only (stopping here is SUCCESS — `PG-SC-03`)

- Establish BEFORE any copy, with forms that change nothing (`PG-PR-01`): live DB path readable (SG-086: host `/home/andrei/StorageGenie/data/db/storagegenie.db`; container `/data/db/storagegenie.db` NOT directly readable under `ProtectSystem=strict` — re-verify both, never assume); storage volume resolvable read-only (`docker volume inspect`); sqlite3 present; temp space writable; WAL mode confirmed (naive `cp` of live DB files is NOT acceptable — SQLite-native consistent copy only).
- Runbook freshness: the three SG-086 artifacts exist with the drilled commands still valid (script runs `--help`/dry shape, test file present, README section paths match disk). Drift is a finding (repaired only inside the ceiling, else reported). A red leg is the ONLY ground to stop — slowness or size is never grounds (negative case stated).

## G1 — consistent read-only copy (production untouched, proved — `PG-EV-02`, `PG-SC-12` BEFORE leg)

- BEFORE: per-table counts (read-only) + `PRAGMA integrity_check` on a consistent copy + `sha256sum` of artifacts. AFTER: counts identical (logical state, never mtime/size alone — WAL-checkpoint moves disclosed, not failures). DB via SQLite-native consistent copy to temp; storage recursive copy to temp (`du -sh` first; cannot-complete-in-bound is a STOP with sizes quoted). Quote DB `sha256sum` + storage file-count/bytes/sampled hashes.
- The ONLY production-adjacent writes are none: no `UPDATE/DELETE/INSERT`, no WAL checkpoint forcing, no restart. A denied read is a STOP (`PG-PR-03`), never a workaround. `PG-IC-03` precedence: read-only-violation STOP wins over continue.

## G2 — restore-to-temp proof (byte-equality on real artifacts)

- Restore into a FRESH temp dir (name both temp paths, never live paths): `sha256sum` backup-vs-restored identical; `integrity_check=ok`; counts + named rows match G1 BEFORE.
- Seen-to-fail (`PG-EV-01`): corrupted temp copy MUST fail the equality gate — quote the failure, discard it.
- Temp rows/files REPORTED with identifiers, temp dir REMOVED post-proof; hashes/counts stay in committed logs (`PG-EV-06`).
- `PG-SC-11`: grep the test tree for end-relative assertions over the drill script/README paths; list hits with verdicts.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-126.log`, `SG-126_report.md`, `SG-126_verify.log` (raw outputs + hashes/counts + `CO-42` quoted verbatim). First token `SG-126`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines. NO new test/script/README expected — the proof is the re-drill; any repair hunk is quoted surgically or absent.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for WRITES by default; surgical README/script hunks ONLY for proven runbook drift (each quoted, each justified as drift-repair). **Anything else — app code, prompts, migrations/models, compose/`.env`, STATE/AGENTS/packet dirs, any production write path — is a STOP.**
- Cross-product (`PG-IC-01`): no criterion writes to production, restarts anything, or touches the network beyond pushes; reads include sqlite3 + docker-inspect (read-only) — no container exec into the backend, no image pull/run.
- A count or absence premise carries RAW output, never paraphrase. No fixed dates except authoring metadata; live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition.
- Simplicity (`G-A7`): enumerate → copy → restore → prove → record. No scheduling, no off-box copies, no encryption changes.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): G0 — CAN this identity still copy without changing anything, and is the runbook fresh? G1 — is the copy consistent and production untouched? G2 — does the backup actually restore, byte-equal?
- G0 green quoted or honest STOP with the red leg (G1–G2 `unanswered`, still shipped).
- BEFORE counts + integrity quoted; AFTER identical; restored-temp `sha256` identical, `integrity_check=ok`, counts + named rows match; corrupted-copy gate seen-to-fail quoted.
- Runbook verdict: FRESH (artifacts valid, no hunks) or DRIFT-REPAIRED (surgical hunks quoted) or DRIFT-REPORTED (unrepaired, with destination).
- $0.000000; `CO-42` quoted verbatim; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-126 | Report: docs/worklogs/SG-126_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/copy · 1800s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
