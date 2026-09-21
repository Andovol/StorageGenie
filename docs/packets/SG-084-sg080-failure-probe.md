# SG-084 — SG-080 failure probe: why did the unit exit-code with no receipt (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D104-approved read-only probe (the SG-071/D91 verification-first precedent). SG-080's dispatch died BEFORE any Coder work: trigger `result=no_receipt`, unit `dispatch-storagegenie@SG-080.service` exit-code, status verb `failed`, notes ref has no SG-080 note (Architect-verified on a mapped fetch), `origin/automation` tip untouched at the packet commit. Blind re-fire is rule-forbidden until the root is established. THIS slice establishes it, read-only, and returns a GO / NO-GO for re-firing `SG-080 --force`. **No launch change is made here; no unit is started, polled, or retried.** **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path (`/home/andrei/storagegenie-contract/VERSION` per SG-062 precedent, or report unanswered).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** read-only EVERYTHING — no builds, no container actions, no migrations, no writes of any kind outside `docs/worklogs`, no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: local reads only. Secrets: never print, log, quote, or commit a key byte; `docker compose config` output is FORBIDDEN (`PG-SC-05` exclude-by-rule — it prints secrets); no credential file fetched.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` (authority: NONE) · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03`.

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

- Work dir `/home/andrei/StorageGenie`: `git status --porcelain` (quote it — dirt is a finding), `git rev-parse HEAD` vs `origin/automation` (equal expected; a gap is a finding), and whether `docs/packets/SG-080-ingest-pipeline-v3.md` exists at the checked-out tip with the dispatched content (a missing or different packet explains a `packet_missing`-class failure — quote what you find).
- `git log --oneline -3` quoted (any commit AFTER the packet commit `15f7dd4` — e.g. a bot merge mid-window — is a finding with its hash and subject).

## G2 — launch preconditions + unit failure evidence (read-only, non-mutating forms)

- Disk: `df` on the work filesystem + `/tmp` (quote free space — a full disk fails builds and units alike).
- Docker: daemon reachable read-only (`docker info` summary lines or `docker images` count — quote the outcome; a denial is unanswered, not an obstacle). Do NOT build, pull, run, exec, or inspect containers.
- Unit evidence: `systemctl status dispatch-storagegenie@SG-080.service` and `journalctl -xeu dispatch-storagegenie@SG-080.service` output tail (quote what you get — a denial is reported as `unanswered`, never routed around, `PG-PR-01`/`PG-PR-03`). Name the earliest error line and what it attributes the failure to (packet fetch, worktree dirt, runner, lane tooling, upstream).
- Dispatch residue: enumerate — don't assume paths — any per-ID state the engine leaves readable (claimed-ID markers, lock files, prior unit droppings under the runtime dir). State the enumeration criterion and report the difference either way (a list is a fact too: give yours as expectation — none expected — and report what is actually there).

## G3 — verdict

- GO / NO-GO for re-firing `SG-080 --force`, with the one-line reason. GO requires: tree clean, tip == packet commit, packet file present with dispatched content, disk non-full, daemon reachable, and the root named as transient/external or fixed-without-packet-change. Anything else names the blocker and whether it is Architect-fixable (a follow-up slice outline — NOT implemented here), desk-side (unit/journal machinery), or owner-side.
- A count or absence premise carries the RAW command output, never a paraphrase.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-084.log`, `SG-084_report.md`, `SG-084_verify.log` (raw command outputs). First token `SG-084`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for WRITES. READS: work tree, packet dir, disk/daemon/unit status, runtime residue dirs — all read-only. **Any write outside `docs/worklogs` is a STOP** — code, tests, prompts, corpus, compose, `.env`, migrations, STATE/AGENTS.
- Cross-product (`PG-IC-01`): G1–G3 need reads + 3 worklog files; nothing else. No criterion touches the network, the DB, or the running service.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): enumerate, quote, verdict. No fix is implemented here, however small.

## Acceptance criteria

- Tree state quoted (porcelain + HEAD vs origin + log -3); packet presence/content verdict quoted.
- Disk + daemon outcomes quoted; unit status/journal tail quoted or `unanswered` with the denial quoted; residue enumeration with criterion + difference reported.
- GO/NO-GO with the one-line reason and the blocker class (Architect-follow-up outline vs desk-side vs owner-side); no auto-retry performed here.
- $0; no writes outside `docs/worklogs`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-084 | Report: docs/worklogs/SG-084_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 300s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
