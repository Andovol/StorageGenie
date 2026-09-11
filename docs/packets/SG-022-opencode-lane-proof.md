# SG-022 — Opencode lane proof: read-only probe via the third Coder (opencode, low)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: low

**Stage:** D27 lane proof (L2 single slice, one retry) — proves the freshly granted opencode lane end-to-end (trigger → work → report → notes-ref receipt) with a read-only probe. Desk `Andovol/Launcher#25` CLOSED 2026-09-11: `CODER_STATE_DIR` now includes the opencode state dir, unit drop-in regenerated + reloaded. This attempt is run 1 of a NEW entry point — first-run provisional per `PG-DP-04`, a second consecutive green still owed by a follow-up. Prior art: SG-011's bare-ID verb shape, SG-021's G6 receipt block (reused verbatim below), SG-021 attempt-3's wedge (`dirty_unattributable` on re-trigger — this fresh ID tests whether the gate blocks the lane or only the replay). Packet size ~7KB, far under the 128 KiB single-argument ceiling the desk named for opencode packets.

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

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none.** This slice touches no service, no port, no container, no database. The running service is never exercised over the network and never restarted (`PG-PR-04`: no new code, so no live proof is owed).

## Why this exists

The opencode lane was granted desk-side but never run: credential dir added to `CODER_STATE_DIR`, drop-in regenerated + reloaded, with two live caveats from the registry — prompt travels on argv (128 KiB ceiling) and the credential dir's `ReadWritePaths` grant is new and unproven (OAuth refresh may still fail under `ProtectHome=read-only`; two API-key providers are the fallback — report which provider actually authenticated). Separately, SG-021 attempt-3's crash left uncommitted dirt the gate calls `dirty_unattributable`: this fresh ID discovers whether the wedge blocks the whole lane or only SG-021 replays. Handed tree facts (verify — `PG-IC-09`): work dir `/home/andrei/StorageGenie`; report dir `docs/worklogs`; notes ref `refs/notes/storagegenie-coder-reports`; backend health module answers `/v1/health` in-process; Coder-side `python`/`pytest` may be absent on the host PATH — resolve `venv/bin/` binaries first and name them, never assume.

## G1 — lane proof, read-only (report only; every leg has a stop)

- Quote the first line of the `CODER.md` contract as read on the host. EXPECTED (hypothesis, not fact): `Contract version: 0.21.1` — the host copy predates the recorded `0.22.0`. A mismatch is a finding, never a stop.
- State how this run was launched and with what provider authenticated (OAuth refresh vs API-key fallback, with the evidence that discriminates — never a credential value).
- `GET /v1/health` via in-process TestClient (bound 120s): quote the JSON. Any network call against a port is OUT OF SCOPE — stop that leg, do not reroute it.
- Read-only `git status --porcelain` of the host tree: quote every line. The SG-021 wedge dirt is EXPECTED — report it, do NOT stage, stash, clean, or amend anything. Any tree write need is a STOP.
- No other shell work. Anything beyond these four legs is a STOP with the reason quoted.

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-022.log` and `{{WORKLOG_DIR}}/SG-022_report.md`, first token `SG-022`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget PER LEG with units. State model/effort provenance from process arguments. The report carries: contract line as read, provider evidence, health JSON, tree-dirt listing verbatim, every stop with its evidence, and the owed run-2 note (`PG-DP-04`).

## G6 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-022 | Report: docs/worklogs/SG-022_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: PROBE-AND-REPORT ONLY. Permitted changes: `docs/worklogs/SG-022.log`, `docs/worklogs/SG-022_report.md`, the G6 note mechanism. Any product/migration/compose/port change need is a STOP with evidence, never a quiet edit. Where a STOP and a retry itch meet, the STOP wins (`PG-IC-03`) — one L2 retry covers transients, never a routed STOP.
- Cross-product (`PG-IC-01`): G1 needs only read access to the contract file, the interpreter, the health module, and git status output. No goal requires what the ceiling forbids. Recorded here once, not per criterion.
- Secrets: never read out, print, or commit credential contents of any kind — names and modes only (`CO-44` pattern).
- Privileged-denial (`PG-PR-03`): any denied operation is reported as unanswered with its exact text, not routed around. No `sudo`, no socket or group changes.
- Test scope: every gate names what it checked with counts and elapsed; a gate emitting no output is a FAIL. No suite runs (no code change — stated, not silently omitted).
- Budget (`PG-PR-06`): 120s per probe leg, 600s overall — actual-versus-budget per leg with units. The transport kill (`RUN_BUDGET_S=2100`) is not reachable inside this budget; finish inside 600s regardless.
- Simplicity: verify before asserting; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- G1 evidence quoted per leg (contract line as read, launch shape + provider evidence, health JSON, full dirt listing), each with its stop obeyed or explicitly passed.
- The world where the lane works and a criterion fails is named where one exists (e.g. a concurrent owner edit moving the dirt listing between read and report — quote both reads).
- Worklog + report committed; notes ref carries the `Dispatch-ID: SG-022` + `Report:` note, quoted, dispatch result line `note=yes`.
- Run-2-owed note present (`PG-DP-04`): this entry point is provisional until a second consecutive green.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — from process arguments, never from a system-prompt identity line.

## Budget

120s per probe leg, 600s overall. Report elapsed per leg with units.
