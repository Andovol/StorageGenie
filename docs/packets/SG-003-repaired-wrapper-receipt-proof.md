# SG-003 — Prove auto-receipt with the repaired wrapper (no product change)

> Facts below are what I believe from the tree that carries this packet. **They are EXPECTED conditions,
> not established truth. Verify each before building on it; a difference is a finding, not an obstacle.**
> For any number, path or quoted line I hand you: if your figures differ from mine, investigate and
> explain — **do not bend your answer to match mine. Correcting me is worth more than agreeing with me.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** Nothing in this slice becomes live; all proof is scoped to already-running code plus the wrapper files themselves.

## Why this exists

SG-001 proved the host runnable (work `2abf9f1`, report `8c8997f` on `automation`) but its receipt never auto-published: `finalize_dispatch_report.sh` shipped with `HL-` / `healthylaws-evidence` / `worklogs` instead of `SG-` / `storagegenie-evidence` / `docs/worklogs`, failing `receipt_diff_not_exact` and `candidate_not_remote`. The script was patched on the host (`finalize_dispatch_report.sh:4-8`) and the receipt manually repaired as `637302e` (`Dispatch-ID: SG-001`) on `storagegenie-evidence`. **This slice proves the repair by publishing a real receipt through the unmodified pipeline — no product change, no new mechanism.

Coder changed by envelope: SG-002 ran twice under grok and produced zero artifacts across two full budgets; the owner confirms an external grok outage (owner statement m0052). This slice runs the identical goal under codex. The packet is coder-neutral by design — selection lives only in the dispatch envelope, never in this file.**

Expected conditions (verify, do not trust):
- `finalize_dispatch_report.sh` header reads `SG-` + `storagegenie-evidence` + `docs/worklogs`
- Workstation checkout `AGENTS.md` → `0.17.2`; host payload `/home/andrei/launcher/VERSION` → `0.17.2`
- `storagegenie-evidence` ref exists on `git@github.com:Andovol/StorageGenie.git` (created by the SG-001 repair)
- Prior finding, do not re-derive: no `CODER.md` lives under `/opt/storagegenie-dispatch/`; the shared contract is read via the wrapper's `CONTRACT_DIR` (observed as `/home/andrei/launcher/CODER.md` at SG-001) — state the actual path you used

If any differ, investigate and explain — correcting me is worth more than agreeing.

## G1 — Prove the wrapper repair (read-only)

- Print the `finalize_dispatch_report.sh` header block and state the three values with line numbers: the ID prefix, the evidence ref, the worklog dir. The property is the strings `SG-`, `storagegenie-evidence`, `docs/worklogs` — not the exit code of the print.
- Grep `/opt/storagegenie-dispatch/*` for remaining foreign-project strings (`HL-`, `healthylaws`, `HealthyLaws`) and report every hit with filename + line number. A mismatch inside the finalize script is a STOP; a hit in `dispatch_coder.sh` is a reported finding and the slice still ships (that file was never patched).
- Run the receipt command unmodified. A repair need is a finding, never a local patch to the wrapper.

## G2 — Version chain, all four links with observed values

- State with observed values: the workstation checkout's recorded version, the host payload `VERSION`, the header this run echoes (`contract_sync=refresh version=0.17.2` expected). A mismatch on any link is a STOP.

## G3 — Contract and health re-proof (cheap, kills stale-payload risk)

- Quote `CO-42` exactly from the host contract copy, never from the repo: *"Restoring production from backup is an incident, never silent cleanup."*
- State model/effort from process arguments or provider metadata (`unknown` per the identity line above if unreadable).
- Run `{{HEALTH_CMD}}` at start and end per `CO-92` and report the delta. Attempt both the `curl` leg and the `TestClient` fallback and quote both verbatim; on this shared host `curl :8000` is expected to hit a foreign 404, so green comes from `TestClient` against this checkout's own app.

## G4 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-003.log` and `{{WORKLOG_DIR}}/SG-003_report.md`, first token `SG-003`, every output path named in the report committed, three UNCLEAR lines at the end.

## G5 — Auto-publish the receipt through the repaired pipeline

- Publish with `{{RECEIPT_CMD}}` to `refs/heads/storagegenie-evidence` with header `contract_sync=refresh version=0.17.2` per `AGENTS.md`.
- Verify the artifact, not the command: the evidence ref carries a commit with the `Dispatch-ID: SG-003` trailer — quote its hash. A zero-exit publish with no such commit is a FAIL.

## Constraints

- Scope ceiling: verification only — no product behaviour change, no migration, no `.env` modification, no service restart, no LLM/OCR. No writes outside `docs/worklogs`.
- No datastore writes; any rows this run creates accidentally are reported with identifiers and left in place.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: no suite ordered — the gates above (string properties, version values, health delta) are the verification. Every gate names the files it checked and its match counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 2100s overall — report actual-versus-budget with units.
- Simplicity: follow the SG-001 shape; write no new checklist (`G-A7`).

## Acceptance criteria

- Finalize header reads `SG-` / `storagegenie-evidence` / `docs/worklogs`, with exact strings and line numbers stated.
- Version chain stated with observed values on all links, or STOP taken with a published receipt.
- `CO-42` quoted exactly; model/effort stated from process args or `unknown`.
- `{{HEALTH_CMD}}` start-vs-end delta reported with both legs quoted verbatim.
- `docs/worklogs/SG-003.log` and `docs/worklogs/SG-003_report.md` committed; every output path in the report committed.
- `storagegenie-evidence` carries the `Dispatch-ID: SG-003` receipt commit; hash quoted.
- No criterion passed vacuously — an empty grep, an empty log, or a skipped leg is declared loudly, never a pass.

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash (expected `CHANGED`: worklog + report).
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 2100s overall (`TIMEOUT_S=2100` in wrapper).