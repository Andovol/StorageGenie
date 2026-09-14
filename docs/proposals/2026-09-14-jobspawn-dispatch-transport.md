---
status: proposed
applied: NO
from: StorageGenie
raised: 2026-09-14
target: per-project AGENTS.md Harness row (configuration value, Class-1 transport); no shared-file change
---

## Proposed rule

OpenCode-harness Architect lanes record `job_spawn` as their Class-1 dispatch transport instead of per-lane Start-Process + blocking-wait chunking. The shared wake rule stays tool-free; only each lane's configuration value names the transport.

## Evidence

StorageGenie dispatches background runs via `job_spawn` (wake on exit) per owner directive 2026-09-12 (`AGENTS.md` Harness row), replacing Start-Process + blocking-wait chunking. Instances, all on the StorageGenie lane: background wake proven 2026-09-11 by probe `3b96fc80` (exit 0 with harness resume); the SG-023 and SG-024 dispatch watches rode the wake (2 runs); SG-027 attempt-2 (`b84df0d6`, exit 1 on the local cap) bounds the claim — even a `job_spawn` run can hit the cap, so the status-verb re-attach path stays mandatory and §2 failure semantics are unchanged (status verb + receipt decide failure, never the trigger log). Cost of the old shape: the blocked session stays open polling while the run proceeds (per-session context burn; not separately metered — stated as mechanism, not a number).

## Generalisation test

1. Different stack? Yes — the defect class (blocked-session polling; lost result lines on local-cap timeouts) is harness-level and stack-independent; any OpenCode-harness lane meets it.
2. Without naming things? Partly — the shared rule (`DISPATCH.md` §2c) already states the wake tool-free, so no shared change names anything. The value being standardized IS a harness primitive name, so per-lane configuration lines necessarily name `job_spawn`; that naming lives in project config, never in the shared rule (`G-O2`). What has to be generalised: nothing further — the filing standardizes a config value, not a rule.

## Cost

Adds one configuration line per OpenCode lane (`AGENTS.md` Harness row — always-loaded project config, not shared bytes). Replaces per-lane Start-Process + blocking-wait chunking notes where they exist (StorageGenie: superseded 2026-09-12; other lanes: at their next between-slice safe point). Requires the `job_spawn` primitive; lanes on other harnesses keep their own §2c class. Not sure of: whether every OpenCode lane's wrapper/probe history matches ours — stated plainly, the desk can narrow or park with a reopen condition.
