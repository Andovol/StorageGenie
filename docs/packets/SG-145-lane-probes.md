# SG-145 — Probe the two lane limitations (`--sql` fts + host `gh` auth), fix nothing

**Settings travel on the trigger** (`SG-145 coder=opencode effort=high`, L3 finish chain P1) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** L3 finish-chain slice 4 of 5 (design `docs/superpowers/specs/2026-09-29-roadmap-finish-design.md`, plan `docs/superpowers/plans/2026-09-29-roadmap-finish.md`): two lane limitations with UNVERIFIED locations — the Architect's `--sql` grep over `.rules-cache/dispatch` finds nothing on the workstation clone, and `gh` is reported unauthenticated on the host (standing thread). Per `PG-SC-03` both are probe goals with stop conditions below; per packet hygiene a fix found here folds into the NEXT slice, never smuggled into this one. THIS slice establishes both limitations and recommends the fix shape. **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** PROBE slice. Writes: `docs/worklogs` (3 files) — and NOTHING else. Any product hunk, however trivial, is a STOP (report it as the recommended next slice instead). No rebuild/recreate/restart. No secret in any capture (`CO-100` — a `gh`-adjacent probe must never print a token; if any command emits credential-shaped output, redact before committing and say so).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-SC-03` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03`.

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

**DATABASE: none (read-only probes only). Restart: none. Deploy: none.**

## G0 — locate the `--sql` path + establish the fts limit (`PG-SC-03` goal)

- Enumerate on the target every `--sql` entry point (grep the lane, wrapper, and repo for the flag; the workstation clone has none in `.rules-cache/dispatch` — the host copy may differ, and THAT difference is itself a finding).
- Drive it read-only against the fts surface and quote what the limit does today (rows returned vs rows matched, where the bound lives in code — read the producing code per `PACKET.md` §2b, never the number alone).
- STOP conditions (stopping is a SUCCESS): the flag exists nowhere reachable (report NOT-FOUND with the grep scope quoted); reaching it needs privilege (report UNANSWERED per the denial path, never route around); the fts behavior needs a live write to observe (report UNOBSERVABLE + the exact write it would take). What does NOT count as grounds to stop: an unfamiliar directory layout, a slow first read.

## G1 — establish the host `gh` auth state (read-only)

- Run the narrowest read-only check that discriminates (`gh auth status`, presence-only — never print a token; 120s bound). Quote the exact failure/success signature.
- If auth needs an owner hand (login flow, device code, token placement): do NOT perform it — write the precise relay ask (what the owner must do, where) as the recommended next step and stop that leg. Performing an auth flow is a STOP.
- What does NOT count as grounds to stop: `gh` missing from PATH (report the PATH + candidate locations instead).

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-145.log`, `SG-145_report.md`, `SG-145_verify.log` (probe captures, grep scopes, diff ceiling proof — the diff must be worklogs ONLY). First token `SG-145`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines. End with one RECOMMENDED-NEXT section per limitation (fix shape + slice size, or owner relay ask).

## Constraints

- **Scope ceiling:** WRITES — the 3 worklog files. **Any other write — product, test, config, auth state — is a STOP.** Reads: the tree, lane/wrapper files, read-only probes, `gh auth status` (presence-only). A probe that would write (live DB, auth mutation, network mutation) is reported UNANSWERED/UNOBSERVABLE, never executed.
- Cross-product (`PG-IC-01`): G0 needs greps + read-only drives (120s class); G1 needs the auth-status read (120s class); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper. `PG-PR-03` stated: a denied probe stops that leg, never routes around.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): establish both limitations, recommend the fixes. No fix ships here, however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): located — is every `--sql` entry point enumerated with its grep scope, or NOT-FOUND with scope quoted? limited — is the fts bound quoted from the producing code with a read-only observation? authed — is the `gh` signature quoted exactly, or the precise relay ask written? clean — is the diff exactly worklogs?
- Probe captures quoted from the commit (not prose summaries) + grep scopes + $0.000000 USD; no vacuous pass (an unrun probe reported as absent, a token printed into a capture, or a fix smuggled past the ceiling evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-145 | Report: docs/worklogs/SG-145_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 2400s overall; expected ~300s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
