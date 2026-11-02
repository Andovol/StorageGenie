# SG-281 — Publish SG-279's two finished commits, which reached the host's branch but never the remote

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only**, through the new test file. No live database read or write.
**Restart: none.** No deploy; rider SG-280 does that.
**Provider: none.**

**Contract chain:** recorded `0.56.0` (`AGENTS.md`) == published `contract-v0.56.0` == the host's contract, echoed by this report. A different echo is a finding.

## Why this exists

SG-279 ended `exit=0`, published its receipt and reports `Verification: PASS`, but `origin/automation` never got its commits. From `SG-279.dbg --status`, verbatim: `DISPATCH_RESULT id=SG-279 coder=opencode exit=0 head=a6bab9aec41822408c3c866ba3c8f21d30a7ba97 note=yes moved=yes rewrite=no dirty=no elapsed=818s budget=2100s stragglers=0 permission_denied=bash`, and `## automation...origin/automation [ahead 2]`. Commits: `3179eac` (work) and `a6bab9a` (report).

**Part of the fault is the Architect's:** the SG-279 packet carried the notes commands but not the branch push, which `PACKET.md` §4 requires in full. That is `UNVERIFIED — my inference` as the cause; G2 settles it.

## G1 — Publish them unchanged

Expected, each a hypothesis to falsify: `dispatch` (engine, the ISS-122 block) saved the old host `HEAD` as `refs/quarantine/preserve-<UTC>` before resetting to `origin/automation` for this run, and printed `preserved=<ref>`. Enumerate `git for-each-ref refs/quarantine/` and take the one ref whose tip is `a6bab9aec41822408c3c866ba3c8f21d30a7ba97`. **If no ref has that tip, or the commits between it and `be8e209` are not exactly `3179eac` and `a6bab9a`, STOP as BLOCKED** and report what you found. Stopping is a success. Older quarantine refs are not this slice's: leave every ref as it is.

Apply the two commits onto your start base in order, with `git cherry-pick`. They are unpublished, so `CO-54` does not forbid this. `origin/automation` moved by this packet's commit alone (expected), so no conflict is expected. **A conflict is a STOP.** No other edit to their content.

Prove equality: `git diff a6bab9a HEAD --name-only` lists only this packet file, before your own report commit. Run `backend/tests/test_sg279_candidate_state.py` once from that tree and quote the count. Run no other suite: SG-279's report holds those, and the Architect audits them.

## G2 — Say why the push did not happen

Read SG-279's run log (`output/dispatch/SG-279.log` and the print-logs file beside it, read-only). Answer, quoting verbatim: which bash command `permission_denied=bash` refers to; whether `git push origin automation` was attempted in SG-279, and what it returned; and how SG-279 satisfied `CODER.md`'s `CO-48` "Confirm the remote head moved", if it did. "Not in the log" is a valid answer, stated as what you searched.

## Publish

After your report commit, literally, in this order:

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-281 | Report: docs/worklogs/SG-281_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The last line's two hashes must be equal. Quote them in the final message. **A refused or failed push is a STOP (`PB-2`), quoted verbatim.** A push of the receipt without the branch is the fault this slice repairs.

## Acceptance criteria

- **A1** — `origin/automation` holds the two commits' content; the two hashes above are equal after the push.
- **A2** — The diff against `a6bab9a` is only this packet and your report.
- **A3** — The new test file passes once on that tree; count quoted.
- **A4** — G2 answered from the log.
- **A5** — `PB-3` vacuity: a failure would look like a missing quarantine ref, a conflict, or a mismatch of the two hashes. Say which you checked.
- **A6** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed files:** exactly what the two commits carry, plus `docs/worklogs/SG-281_report.md`. No `git push --force`. No quarantine ref moved or deleted, and none pushed.
- **Reads of any file are allowed**, and `output/dispatch` is read-only. The only runtime authorised is that one test file.
- **No changes** to the live database, stored files, running containers, images, host packages, or any provider. Scratch, if needed: `output/SG-281-scratch/`, removed by exact path.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

One test file **300 s**; ordinary commands, each push included, **120 s**.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. Expected ≈200 s (`UNVERIFIED — my estimate`).

## Report

Destination: `docs/worklogs/SG-281_report.md`. The first line states the slice ID, model and effort from the process arguments, working directory, remote, BASE ref and resolved commit, and WORK_HEAD. Include the quarantine ref found, the new hashes of the two commits, the A2 diff, the test count, G2's answers, and the contract echo. Its last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
