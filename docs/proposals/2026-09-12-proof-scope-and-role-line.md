# Two packet-contract proposals from the StorageGenie Phase-2 arc

**Date:** 2026-09-12 · **Source:** StorageGenie (SG-025…SG-030 arc) · **Status:** proposed (project-internal; relay to Launcher when the batch is next sent)

## P1 — `PG-EV-01`/`PG-EV-09` scope: FAIL-then-PASS binds fix-driven tests only

**Incident.** SG-030's packet demanded FAIL-then-PASS for every new test, including the Phase-2 exit E2E — a file that proves an already-landed flow (SG-028's). Those tests pass on the unmodified base tree by construction; demanding a pre-fix failure invites a fabricated or contrived one.

**Proposal.** State the rule as: a test is fail-then-pass when it is written against a fix (red on base, green after). A file proving a pre-existing flow is instead held to a **source-mutation sensitivity proof** — break the behaviour under test, show the test catches it, revert clean, and record all three in the verify log. SG-030 did exactly that (three mutations: gated-field routing, rollback, supersession; each caught; `SG-030_verify.log` §3).

**Rationale.** The mutation proof is strictly stronger evidence of non-vacuity than a manufactured pre-fix failure, and it removes an incentive to deform tests to fit a rule.

## P2 — every packet carries the coder-role line

**Incident.** SG-027 run-1 (headless opencode) executed its own dispatch verb — `/usr/local/bin/dispatch SG-027 --force`, refused `lock_held` (its own unit held the lock) — then polled its own unit until the 35-minute timeout killed it. Zero commits, zero files, zero calls; the whole run was lost to a role misread. Evidence: host journal + `~/.local/share/opencode/log/opencode.log`; root cause recorded in StorageGenie `STATE.md` (ISS-9, corrected) and `Andovol/Launcher#30`.

**Proposal.** Every packet carries one verbatim standing line:

> You are the Coder, never the Architect — never run the dispatch verb for any ID, never start or poll your own unit. If you believe a dispatch is needed, STOP and report it.

**Rationale.** One line, cites a real 35-minute loss, no new machinery (`G-A7`). StorageGenie's packets from SG-028 on carry it; no recurrence since.

## Evidence pointers

- `docs/worklogs/SG-030_verify.log` §3 (mutation proofs, reverted clean) and the SG-030 report finding 1 (premise difference disclosed).
- `docs/ratings.md` rows SG-027 (run-1 failure, run-2 completion) and SG-030.
- `Andovol/Launcher#30` — root-cause comment (self-dispatch, lock_held, evidence locations).
