# SG-055 — enablement probe: key + consent + restart check, read-only (opencode, low)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: low

**Context and standing lines.** D76 verification-first probe (owner quote "What I wanted is for you to run a separate, very small slice, just to ask the Coder to check."): the owner placed the provider key + `SG_CONSENT=true` in the host backend `.env` and restarted the backend; THIS slice only checks that, read-only, before the SG-049 live-leg re-dispatch. SG-049 returned the designed STOP (G0: key present len 67, `consent=false` → zero calls, $0) with the full offline slice shipped and rated 98; NOTHING about SG-049 is re-done here. D74 L3 spent except the live leg; SG-055 takes this number so the untabled consistency batch shifts to SG-056+. **Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-049 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no code hunks anywhere (read-only slice — a diff outside `docs/worklogs` is a STOP); no migration; no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback only, nothing else.
**Money posture (F2):** spend UNCAPPED-but-ledgered with re-evaluation owed; this slice makes zero provider calls so the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-SC-03` read-before-stop · `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-SC-05` exclude-by-rule · `PG-SC-09` name-the-world · `PG-PR-03` denied-is-stop · `PG-PR-04` code-becomes-live · `PG-DP-02` no-sweep-waiver · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 300s for the note push+verify. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** Every check below is a read of the running service or the container runtime; the production SQLite is touched by nothing, not even arithmetically.

## Why this exists

The SG-049 live leg is gated on three establishments the owner just put in place by hand (key + `SG_CONSENT=true` + restart). The Architect has no host shell path (forced-command rejects non-verb traffic — verified `result=reject reason=bad_id`), so the only proof vehicle is a Coder slice. A full live-leg re-dispatch on an unverified gate risks a wasted metered run or a second designed STOP; this probe establishes the gate at ~2 minutes of Coder compute first. Expected premises (re-verify per `PG-IC-09`, all from `docs/worklogs/SG-049_report.md:17-28`): settings read is `GET /v1/settings/ai` (bare `/settings/ai` serves the SPA, never JSON); key existence is probed from INSIDE the backend container (`docker exec storagegenie-backend-1 python -c`, booleans + length only); `ai_status()` is read the same way (`reader.ai_status`); health is `GET /v1/health`; SG-049 observed `provider_id=fake`, key len 67, `consent=false`.

## G1 — the four establishments, read-only (`PG-SC-03` goal with both outcomes)

- Establish, read-only: (a) `GET /v1/settings/ai` (loopback) reports `consent=true` — quote the full JSON body; (b) the provider key EXISTS — existence-only probe from inside the backend container (boolean + length integer, e.g. the SG-049 shape) — **never print, log, quote, or commit a single key byte**; `docker compose config` output is FORBIDDEN here — it prints secrets (`PG-SC-05` exclude-by-rule); (c) `ai_status()`-equivalent reports enabled for the configured provider — quote the tuple; (d) the backend container is post-restart — quote `StartedAt` + image ID (read-only `docker inspect`); note the load-bearing reasoning: live settings come from env at process start (SG-031: a restart drops overrides), so `consent=true` served live PROVES the restart — while `consent=false` means STOP no matter what `StartedAt` says.
- GO (all of a+b+c true) → verdict GO for the SG-049 live leg. STOP (any false) → **STOP-as-SUCCESS**: commit the three worklogs + `BLOCKED: <exact failing leg>` first line, push, receipt, clean tree. **Stopping here is the successful outcome** — say so in the report, never treat it as failure. What does NOT count as grounds to stop: the `provider_id` label value alone, the key length differing from 67, frontend container state (exited since SG-049 — the backend serves the SPA), the runner's `report_missing` classifier (desk-side, Launcher#42 — verify receipts via mapped notes-ref fetch, never the status verb).
- `PG-SC-09`: name the world where this probe reports GO yet the live leg still STOPs (key present but invalid at call time; env rotated between probe and leg) and why the slice still ships (the live leg re-runs G0 itself — this probe prices the surprise down, never removes the gate).

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-055.log`, `{{WORKLOG_DIR}}/SG-055_report.md`, `{{WORKLOG_DIR}}/SG-055_verify.log` (raw outputs of every command in G1, quoted). First token `SG-055`; elapsed-versus-budget with units; MODEL + effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); three UNCLEAR lines. Pre-commit secret gate: grep the three worklogs for any line carrying a long token (exclude the `key_len=` integer line) — 0 hits required, quote the grep.

## Constraints

- **Scope ceiling:** `docs/worklogs/SG-055.log` + `docs/worklogs/SG-055_report.md` + `docs/worklogs/SG-055_verify.log`. **Anything else is a STOP** — including any backend/frontend file, prompts, eval, tests, `.env`, compose files, and any new dependency. Reads MAY run the already-built local containers only (`curl` loopback, `docker exec`/`inspect` read-only); launching any other runtime counts as execution, not reading (`PG-IC-01`).
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G1's STOP shares no condition with any remediation step — stops win (`PG-IC-03`).
- Test scope: no code changes, so no suite run — full sweep WAIVED explicitly per `PG-DP-02` (substitute = the four quoted live reads named in G1). A gate emitting no tool output is a FAIL, not a PASS (`PG-EV-01` — every check pastes its raw output).
- Budget (uncalibrated per `G-A9`): 120s ordinary · 300s note push+verify · **600s early-close** · **900s overall** — actual-versus-budget with units.
- Simplicity (`G-A7`): four reads, one verdict; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- G1 quoted read-only FIRST with both outcomes handled; GO verdict only with all three establishments quoted, else STOP-as-SUCCESS via the `BLOCKED:` commit path.
- Starting tree quoted (clean expected; dirt = STOP first); SG-049-report premises re-verified in-slice with quoted reads (endpoint path, container name, notes ref).
- The four properties hold as PROPERTIES (`PG-EV-02`, `PG-EV-05`): served consent JSON, key boolean+length (zero key bytes), `ai_status()` tuple, `StartedAt`+image — never bare exit codes.
- Secret gate 0 hits quoted; `docker compose config` never run; zero provider calls; no migration; nothing pushed to `storagegenie-evidence`; no ignored file staged; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Verdict line GO/STOP with the three establishments quoted; spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-055 | Report: docs/worklogs/SG-055_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 300s note push+verify · 600s early-close · 900s overall; REAL metered $0.000000 (zero calls); actual-versus-budget with units.
