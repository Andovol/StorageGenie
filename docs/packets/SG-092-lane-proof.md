# SG-092 — lane proof: opencode/high full-loop test before product work (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D124-approved lane test (owner: small test on the restored lane before any product work). Two consecutive SG-081 launches failed — attempt 1 refused pre-Coder (`effort_unsupported_value_opencode_medium`, exit 2), attempt 2 died 4s in on transient upstream invalid-JSON (exit 1, `SG-081.dbg` certified, zero commits) — and the 0.29.0 engine now refuses `medium`/`xhigh` for opencode by name. THIS slice proves the lane end-to-end at the surviving rung: trigger accepted at `effort: high`, Coder boots, work commits, receipt publishes. Product work (SG-081 `--force`, D123) waits on its GO. **Authoring date (metadata, never a gate):** 2026-09-22. Transport: the standard job_spawn lane. Contract: recorded `0.29.1` == published (`454589c`; D119 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** read-only EVERYTHING — no builds, no container actions, no migrations, no writes of any kind, no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: local reads only. Secrets: never print, log, quote, or commit a key byte; `docker compose config` output is FORBIDDEN (`PG-SC-05` exclude-by-rule — it prints secrets); no credential file fetched.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.29.1 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` (authority: NONE) · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 60s ordinary, 300s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (not even `ps` against the daemon counts as free — `docker` CLI queries are allowed read-only; any denial is reported as unanswered, never routed around).

## G1 — host tree + packet presence

- Work dir `/home/andrei/StorageGenie`: `git status --porcelain` (quote it — dirt is a finding), `git rev-parse HEAD` vs `origin/automation` (equal expected; a gap is a finding), and whether `docs/packets/SG-092-lane-proof.md` exists at the checked-out tip with the dispatched content (a missing or different packet explains a `packet_missing`-class failure — quote what you find).
- SG-081 readiness sighting: whether `docs/packets/SG-081-off-fetch.md` at the tip carries `effort: high` and the `0.29.1` contract echo (quote both lines — the re-fire's packet must be this one).
- `git log --oneline -3` quoted (any commit AFTER the packet commit — e.g. a bot merge mid-window — is a finding with its hash and subject).

## G2 — launch preconditions + effort-rung proof (read-only, non-mutating forms)

- Disk: `df` on the work filesystem + `/tmp` (quote free space — a full disk fails builds and units alike).
- Docker: daemon reachable read-only (`docker info` summary lines or `docker images` count — quote the outcome; a denial is unanswered, not an obstacle). Do NOT build, pull, run, exec, or inspect containers.
- Effort-rung proof: YOUR OWN launch — quote the exact `opencode` argv the lane used for THIS slice (launcher artifact — enumerate, don't assume the path: state the criterion used to find it) and the provider/model banner plus `effort_source` if the lane log names it. If the lane refused this slice's `high` effort, that refusal IS the headline finding (quote it verbatim) and the remaining goals report `unanswered` where they depend on a boot that never happened.
- Dispatch residue: enumerate — don't assume paths — any per-ID state the engine leaves readable (claimed-ID markers, lock files, prior unit droppings under the runtime dir, including any `SG-081` residue from the two failed launches). State the enumeration criterion and report the difference either way (a list is a fact too: give yours as expectation — none expected beyond the two documented SG-081 failures — and report what is actually there).

## G3 — verdict

- GO / NO-GO for the queued `SG-081 --force` re-fire (D123), with the one-line reason. GO requires: THIS slice booted at `high` and published its receipt, tree clean, tip == packet commit, SG-081 packet present with `high`/`0.29.1` content, disk non-full. Anything else names the blocker and whether it is Architect-fixable (a follow-up slice), desk-side (unit/journal machinery), or owner-side.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-092.log`, `SG-092_report.md`, `SG-092_verify.log` (raw command outputs). First token `SG-092`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) — NOTHING else in the repository. **Anything else is a STOP.**
- Cross-product (`PG-IC-01`): every criterion is a read; no criterion writes anywhere.
- Budget (uncalibrated per `G-A9`): 60s ordinary · 300s overall — actual-vs-budget per leg with units.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Tree status + HEAD-vs-origin + both packet sightings quoted; last-3 log quoted.
- Disk + daemon reachability quoted (or denial quoted as unanswered).
- Own-launch argv quoted with `effort_source` where the lane names it (or the refusal quoted verbatim as the headline).
- Residue enumeration performed with criterion stated and difference reported.
- Explicit GO / NO-GO on the SG-081 re-fire with reason; no vacuous pass; nothing written outside `docs/worklogs`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-092 | Report: docs/worklogs/SG-092_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 300s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
