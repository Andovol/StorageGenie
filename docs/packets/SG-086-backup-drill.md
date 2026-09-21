# SG-086 — backup/restore drill: read-only production copy, restore-to-temp proof, runbook (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D107-approved slice 2 of the Phase 5 hardening stage (plan `docs/superpowers/plans/2026-09-21-phase-5-hardening.md` Slice 2). THIS slice proves the backup story: consistent read-only copy of the live SQLite + storage, restore-to-temp with byte-equality, runbook in README. **Authority (G-K2, D107 owner quote "D107 approved."): production READ authority ONLY — read-only DB + storage copy, restore lands on TEMP paths only, never the live paths; no `UPDATE/DELETE/INSERT` against production in any form.** Restoring production from backup is an incident, never silent cleanup (`CO-42` — quote it verbatim in the report). **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** drill ONLY (enumerated ceiling below). No migration, no schema change, no secrets in logs, no deploy, no restart (`PG-PR-04` — no code becomes live; the drill script is operator tooling, proof is scoped to this host run). No provider calls, $0.
**Money posture:** $0.00 by construction — no metered call exists on any path. No bound to multiply out (`PG-IC-04` stated as not firing).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` (temp rows/files ONLY — reported, temp dir removed post-proof, hashes stay in logs) · `PG-EV-09` · `PG-SC-03` (G0 stop) · `PG-SC-05` · `PG-SC-09` · `PG-SC-11` (grep + verdict, see G3) · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` (precedence: read-only-violation STOP wins over continue — stated) · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (G0 enumeration) · `PG-PR-03` · `PG-PR-04` (NOTHING live stated) · `PG-PR-10` (database cited + D107 grant quoted above).

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

**DATABASE: the host's live SQLite (READ-ONLY under the D107 grant above) + temp copies; production is never written. Restart: none. Deploy: none.**

## G0 — capability enumeration, non-mutating only (stopping here is SUCCESS)

- Establish BEFORE any copy, using forms that change nothing if they succeed (`PG-PR-01`): (1) resolve the live DB file — I hold the host path `/home/andrei/StorageGenie/data/db/storagegenie.db` (SG-001 measured; container path `/data/db/storagegenie.db` is NOT directly readable under `ProtectSystem=strict` — re-verify with `test -r` + `ls -l`, never assume); (2) resolve the storage volume — I hold named volume `storage_data` mounted at `/data/storage` in-container (`docker-compose.yml:10,43`; resolve the host-visible path with `docker volume inspect`, read-only); (3) `sqlite3` present; (4) temp space writable (`mktemp -d`).
- A red leg (unreadable file, unresolvable volume, missing sqlite3, no temp space) is the ONLY ground to stop — slowness or size is never grounds (`PG-SC-03` negative case stated). Stopping here reports `unanswered` for G1–G3 and still ships the enumeration raw.
- Load-bearing fact for every choice below: the DB runs in WAL mode (`db.py` FK + WAL listener — verify on target), so a naive file copy of the live DB can capture an inconsistent snapshot. Consistent copies use SQLite-native means (`.backup` or `VACUUM INTO` — decided and reported); raw `cp` of the live DB files is NOT an acceptable backup (stated, not silent).

## G1 — consistent read-only copy (production untouched, proved)

- BEFORE state first (`PG-SC-12` BEFORE leg): per-table row counts via a read-only query path + `PRAGMA integrity_check` on a consistent copy + `sha256sum` of what you copied. AFTER the drill, re-take the counts: identical is the production-untouched proof. Compare LOGICAL state (counts + integrity), never mtime/size alone — a WAL checkpoint can move bytes with identical logic (F-SG072-1 family; a mtime move with identical counts is disclosed, not a failure).
- Copy: DB via the G0-chosen SQLite-native consistent copy to temp; storage via recursive copy to temp (measure with `du -sh` first, report size; if the copy cannot complete in-bound, STOP with sizes quoted — a sizing finding, not a drill failure). Quote `sha256sum` for the DB artifact + file-count/byte-total + sampled hashes for storage.
- The ONLY writes this slice ever makes to production-adjacent state are none: no `UPDATE/DELETE/INSERT`, no WAL checkpoint forcing, no container restart. A denied read is a STOP (`PG-PR-03`), never a workaround.

## G2 — restore-to-temp proof (byte-equality on real artifacts)

- Restore the G1 copies into a FRESH temp dir (never the live paths — name both temp paths). Prove: `sha256sum` backup-vs-restored identical for the DB file; open the restored copy (`PRAGMA integrity_check=ok`); per-table counts equal the G1 BEFORE counts; read back named rows (table + id quoted); storage file-count/bytes/sampled-hashes equal.
- Seen-to-fail (`PG-EV-01`): a deliberately corrupted temp copy MUST fail the equality gate — quote the failure, then discard it. A gate never fed a bad input is decoration.
- Temp rows/files: REPORTED with identifiers, temp dir REMOVED post-proof; hashes/counts stay in the committed logs (`PG-EV-06` — temp-only, stated).

## G3 — committed test + runbook (the drill outlives the slice)

- ONE new test file (`backend/tests/test_backup_drill.py`): fixture-DB restore-to-temp byte-equality (temp fixtures only — never the production paths; the production proof stays in G1/G2 logs, asserted by existence of the quoted hashes, not re-run). FAIL-then-PASS raw, both runs committed to `SG-086_verify.log` (`PG-EV-09`).
- Drill script: new `backend/scripts/` entry (the dir does NOT exist on `automation` — verify; check the path against ignore rules BEFORE committing anything under it, `PG-SC-10`, quote the check). Script = the exact G1/G2 command sequence, parameterized by paths, with the read-only guards inline.
- README runbook: SURGICAL section (quote the hunk) beside the existing data-location notes (`README.md:99-102,189-192` — re-verify on target): what to copy, where temp lands, how equality is proved, and the incident line (restore-to-production is never silent, `CO-42` quoted).
- `PG-SC-11`: grep the test tree for end-relative assertions over README/scripts/drill paths; list hits with verdicts (expectation: none — state the empty result raw).
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify on bare BASE with stash, do not inherit); `ruff` clean; `mypy` delta 0 quoted; secret grep-gate over the diff (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken` identifiers, SG-037 shape) with 0 real secret shapes.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-086.log`, `SG-086_report.md`, `SG-086_verify.log` (raw outputs + BOTH fail-then-pass runs + every hash/count quoted). First token `SG-086`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **$0.000000 actual**; `CO-42` quoted verbatim; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** NEW `backend/scripts/*` (ignore-checked, quoted) · ONE new test file · SURGICAL README hunk (quoted) · `docs/worklogs` (3 files). **Anything else is a STOP** — app code, prompts, migrations/models, compose/`.env`, STATE/AGENTS/packet dirs, any production write path.
- Cross-product (`PG-IC-01`): no criterion writes to production, restarts anything, or touches the network beyond pushes; reads include suite + sqlite3 + docker-inspect (read-only) — no container exec into the backend, no image pull/run; G4's suite run is covered by the same offline rule.
- A count or absence premise carries the RAW command output, never a paraphrase.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition — reachability form only.
- Simplicity (`G-A7`): enumerate → copy → restore → prove → record; no scheduling, no off-box copies, no encryption changes, no Enrich.

## Acceptance criteria

- G0 green (all four legs quoted) or honest STOP with the exact red leg (G1–G3 `unanswered`, still shipped).
- BEFORE counts + integrity quoted; AFTER counts identical; mtime-only moves disclosed per the WAL rule, never counted as writes.
- Restored-temp `sha256` identical, `integrity_check=ok`, counts + named rows match; corrupted-copy gate seen-to-fail (quoted).
- New test FAIL-then-PASS raw both committed; script + README hunk committed; ignore-check quoted; suite/ruff/mypy/secrets per G3; $0.000000; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G0 — CAN this identity copy without changing anything? G1 — is the copy consistent and production untouched? G2 — does the backup actually restore, byte-equal? G3 — is the drill repeatable from the repo? G4 — is the evidence committed, not merely reported?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **$0.000000 actual** (zero provider calls; temp state quoted — containment per `PG-PR-04` stated: nothing live exists to contain).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-086 | Report: docs/worklogs/SG-086_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/copy · 1800s overall; **$0.00** — no metered call exists on any path in this slice.
