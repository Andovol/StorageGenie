# SG-131 — Live ledger purge: backup, census, run the SG-125 vehicle, prove counts

**Settings travel on the trigger** (`SG-131 coder=opencode effort=high`, D2) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D2-authorized production word (owner quote "D2 - approved", ISS-1): run the SG-125 live purge that SG-125 recorded and deliberately never ran. SG-125 (rated 98) shipped the instrument — month-boxed `_recorded_spend` + `purge_old_provider_calls` + `LEDGER_RETENTION_MONTHS = 12` (UNCALIBRATED, `G-A9`) — temp-proven with before/after SELECTs, suite green. Four images rebuilt + recreated since (SG-126/127/129/130), so the vehicle is EXPECTED live in the served image — expected, not certain (`PG-IC-09`: verify, never inherit). Verdicts: PURGED (vehicle run live, before/after census quoted, month-math unmoved) / BLOCKED (month-box not live in-image, or a nonzero old-row pre-count — commit, receipt, clean tree; the delete decision returns to the Architect). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** purge ONLY. Writes: the live-DB vehicle run under the G0 zero-precondition + `docs/worklogs` (3 files) — and NOTHING else. No product-code hunk of any kind (prove by empty product diff), no migration, no rebuild, no recreate, no key, no metered call ($0 — a metered call is a STOP-and-report). **Authorising grant (`PG-PR-10`):** D2, live SQLite at in-container `/data/db/storagegenie.db` (expectation — resolve on target). Backup-first per the SG-086 runbook before any write.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path. `PG-PR-06` containment, stated upfront: exactly one predicated `DELETE` (`created_at < cutoff`, cutoff = live clock back 12 calendar months, day-clamped) inside a container exec, bounded by the G0 precondition (zero old rows expected — the project's oldest data is weeks old, so any nonzero pre-count is a STOP, never a delete). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-EV-08` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-01` · `PG-PR-03` · `PG-PR-06` · `PG-PR-10`.

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

**DATABASE: live SQLite WRITE under grant D2 — exactly the predicated vehicle run, and ONLY after the G0 zero-precondition holds (else STOP, nothing written). Reads: census SELECTs (provider_call counts + cutoff enumeration). STORAGE: untouched. Restart: none. Deploy: none. Container actions: exec for census + vehicle ONLY (no restart, no pull, no recreate; EROFS sandbox — container-exec is the writable path, SG-129 precedent).**

## G0 — live-readiness + backup + before-census (nothing is written until all three are quoted)

- Verify the instrument is LIVE in the served image: `LEDGER_RETENTION_MONTHS` + `purge_old_provider_calls` + month-boxed `_recorded_spend` importable via container python (SG-130 G0 precedent). If any symbol is absent → BLOCKED (no rebuild here — the rebuild decision returns to the Architect; purging under a lifetime-summing cap is the exact fail-open SG-125 forbids).
- Backup-first per the SG-086 runbook (read-only copy, byte-equality quoted), then BEFORE-census quoted: `provider_call` total + per-month histogram + the cutoff value computed from the live clock + the enumerated set of rows with `created_at < cutoff`. EXPECTATION: the old-row set is EMPTY (project data is weeks old; `PG-IC-08` — a nonzero pre-count in EITHER direction is a STOP-and-report before any delete, never a delete).
- Capability census (`PG-PR-01`, read-only forms only): state what the exec identity can touch before the run.

## G1 — the live run + after-census

- Run the SG-125 recorded vehicle word-for-word (source: `docs/worklogs/SG-125_verify.log` in-tree — quote the command you run; if it differs, stop and report rather than improvising). Quote the run output including returned ids.
- AFTER-census quoted: `provider_call` total + per-month histogram + non-spend tables (`guardrail_event`, `audit_event`, `job`, `evidence`) untouched. EXPECTATION: deleted == 0, every count identical (`PG-IC-08` either-direction STOP). Month-math re-proof: the current-month total quoted before and after (unmoved).
- `PG-EV-06`: every row the run deletes (expected: none) reported with identifiers; the backup path that reverses the run named.

## G2 — served sanity (GET-only) + empty product diff

- `{{HEALTH_CMD}}` exact-shape + gate probes quoted; empty product diff (`git diff` over everything except `docs/worklogs`) quoted — this slice ships zero product hunks.
- No vacuous pass: a purge proven only by its own return value evidences nothing — the before/after SELECTs + quoted cutoff are the proof (`PG-EV-02`, `PG-EV-08`).

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-131.log`, `SG-131_report.md`, `SG-131_verify.log` (readiness check, backup proof, before/after census, run output, health). First token `SG-131`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the single predicated vehicle run (G0-gated) + `docs/worklogs` (3 files). **Any other write — product code, schema, config, storage artifacts, suite files — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs image reads + backup + census SELECTs; G1 needs one exec run + census; G2 needs GETs + diff; nothing else. No criterion demands a rebuild, a model change, a key, or any metered call — no cell collides; stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): prove live, back up, census, run once, census again. No scheduler, no auto-run vehicle, no window calibration (still UNCALIBRATED, `G-A9`) — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): live-readiness — is the SG-125 instrument the code actually serving? write-fate — what did the vehicle delete, and what proves only those rows could go? live-safety — what stops a surprise delete?
- Readiness import check quoted; backup byte-equality quoted; before/after census quoted with cutoff; deleted set quoted (expected empty); month total unmoved and quoted; health exact; empty product diff quoted.
- $0.000000; no vacuous pass (return-value-only proof evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-131 | Report: docs/worklogs/SG-131_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
