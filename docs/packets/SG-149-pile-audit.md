# SG-149 — outside-PR audit (11-PR pile #32–42, read-only, verdicts only)

**Settings travel on the trigger** (`SG-149 coder=opencode effort=high`, PR-pile audit arc, owner triage word "Okay to both" 2026-09-29 with audits-first order) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** 11 open PRs (#32–42, outside agents, author `Andovol`, `bolt/`/`fix/`/`test-`/`perf/`/`clean-models-` heads, all created 2026-09-29) aim at `automation`. Per `G-L7` each gets exactly one outcome — audit-and-merge, rewrite-as-slice, or close-with-reason — and a PR this project's own dispatch did not create is NEVER merged as it stands. **NOTHING merges, rewrites, or closes in this slice: verdicts only; any merge takes a SECOND owner word on the verdict table.** Precedent: SG-133 (14 diffs) / SG-134 (10) / SG-135 (merge batch on its own word). Expectation (gh list 2026-09-29, verify on target — a list is a fact too: enumerate open PRs at runtime and report the difference either way): #32 bolt/batch-fetch-expiry · #33 test-decode-cursor · #34 asset-service-exception-logging · #35 clean-models-exports · #36 bulk-insert-asset-evidence · #37 loads-json-error-handling · #38 synthesis-empty-except-logging · #39 bulk-insert-3013 · #40 restrict-cors-allow-headers · #41 fix-n1-query-loser-merge · #42 restrict-cors-methods. Host `gh` is unauthenticated (SG-145) — fetch diffs via `git refs/pull/<n>/head` substitution (SG-133 precedent), never print a token (`CO-100`). **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** READ-ONLY audit slice. Writes: `docs/worklogs` (3 files) — and NOTHING else. No merge, no close, no branch push, no product/test/config write however trivial. Pull-ref fetches touch local git objects only (transient; worktree stays clean — prove it). No secret in any capture (`CO-100`).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-10` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (diff reads + local greps only). Restart: none. Deploy: none.**

## G0 — fetch every open-PR diff as bytes (`PG-SC-03` goal)

- Enumerate open PRs aimed at `automation` on the target NOW; reconcile against the 11 above (new arrivals and disappearances both reported with numbers).
- Fetch each diff read-only (`git fetch origin refs/pull/<n>/head` + byte diff vs merge-base; quote the refspec scope). Host `gh` stays unused for reads.
- STOP conditions (stopping is a SUCCESS): a diff is unreachable read-only (report UNREADABLE with the attempted scope + defer its verdict, never route around). What does NOT count as grounds to stop: a slow first fetch, an unfamiliar head name.

## G1 — verdicts, overlap, secrets, lessons

- Per PR exactly one verdict — MERGE (as-is) / REWRITE (idea sound, diff not) / CLOSE (one-line reason) — with the evidence quoted, never the report alone.
- Overlap matrix: do any two PRs touch the same lines/symbols (notably the bulk-insert pair #36/#39 and the CORS pair #40/#42)? State the merge order the verdicts imply.
- Secret scan over all 11 diffs (quote scope + result).
- Lesson per defect-fixing PR (`G-L7` D336 shape): name the defect and why this project's own packets, tests and audit let it through.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-149.log`, `SG-149_report.md`, `SG-149_verify.log` (fetch scopes, byte counts/hashes per diff, verdict table, overlap matrix, secret scan). First token `SG-149`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines. End with RECOMMENDED-NEXT: the merge-batch proposal the verdicts imply (IDs + order + expected gates — for the SECOND owner word, never executed here).

## Constraints

- **Scope ceiling:** WRITES — the 3 worklog files. **Any merge, close, branch push, or product/test/config write is a STOP.** Reads: the tree, pull-ref fetches, local greps, `gh` list/pr-view ONLY if authenticated non-interactively (presence-only; a login prompt is a STOP for that leg). `PG-PR-03` stated.
- Cross-product (`PG-IC-01`): G0 needs pull-ref fetches (120s class); G1 needs diff reads + greps (120s class); G2 needs the worklog commit + notes receipt. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): verdicts, not fixes — however small the fix looks.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): fetched — is every open PR's diff captured as bytes (or UNREADABLE with scope quoted)? judged — does every PR carry exactly one verdict with quoted evidence? scanned — is the secret scan quoted over all diffs? clean — is the diff exactly worklogs?
- No vacuous pass (an unfetched PR reported as judged, a verdict without quoted evidence, or a merge smuggled past the ceiling evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-149 | Report: docs/worklogs/SG-149_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 2400s overall; expected ~1200s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
