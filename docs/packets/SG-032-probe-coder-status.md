# SG-032 — Lane probe: Coder status (opencode, medium) · owner-requested diagnostic

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** NOT a Phase-2 slice. Owner-requested 2026-09-12 after SG-027 attempt-2 failed with no readable evidence (ISS-9). Purpose: prove the lane end-to-end (Coder runs, reads, writes, commits, pushes, receipt lands) and capture environment facts. Dispatched with `--quarantine` so any debris from the failed run is moved to a host-local ref and reported; the flag is inert on a clean tree.
**Standing lines:** the model report uses process-argument/env provenance — write `unknown` rather than a plausible guess (owner standing rule); a step requiring privilege you lack is reported unanswered, never routed around.

> My premises are hypotheses. Verify before building on them; a difference is a finding, not an obstacle.
> If any acceptance criterion could pass vacuously (empty diff, skipped step, grep that could not match),
> say so loudly rather than reporting a pass.

> **DO NOT HANG.** Every command under 120s. Never run an interactive command; a command you had to kill
> is a finding worth reporting. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, leave the worktree clean. End with
> the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation** (state the commit it resolved to). **DATABASE: none. Restart: none.**

## Steps

1. `git status --porcelain` verbatim at start; if non-empty, also `git diff --stat` and `git log --oneline -3` — **do not modify those files**.
2. `git rev-parse HEAD`; current branch; `git for-each-ref refs/quarantine --format="%(refname)"` — report names only (a fresh `flag-SG-032-*` / `preserve-*` is expected evidence); adopt nothing.
3. Environment: working dir; `venv/bin/python --version` (single command); model + effort provenance as above.
4. Write `docs/worklogs/SG-032_report.md`: every quoted output above, elapsed per step, the three UNCLEAR lines.
5. Commit `SG-032 probe: lane status report`; push to automation; worktree clean.
6. Receipt note on the work HEAD LAST (no commit after): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-032 | Report: docs/worklogs/SG-032_report.md | Work-HEAD: <hash>" <WORK_HEAD>`; verify with `show <WORK_HEAD>` and QUOTE it; final line `note=yes`.

## Constraints

- No suite runs, no builds, no installs, no live calls, no DB, no secrets (`.env` presence only, never values). All commands bounded 120s.
- Scope ceiling: `docs/worklogs/SG-032_report.md` + the receipt. Anything else is a STOP.

## Acceptance criteria

- Report committed + pushed; receipt valid (`Dispatch-ID: SG-032` + `Report:`); worktree clean; all quoted outputs present; model provenance quoted (`unknown` allowed). No vacuous pass.

## Budget

120s per command; 600s overall.
