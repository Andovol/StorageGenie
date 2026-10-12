# D-1012-17 — Dispatch transport follows the current Architect harness

Owner directive, 2026-10-12: "We are now in Codex and you should use your own transport, job_spawn is just for OpenCode."

The existing dispatch protocol, forced-command credential, settings, sequential guards and notes-ref receipt remain the same. OpenCode uses job_spawn. Codex uses exec_command's background command session for one SSH trigger. No polling loop, re-trigger or claim of automatic completion wake is authorized by that primitive. If no automatic wake is exposed, DISPATCH.md §2c Class 4 applies: end the turn and perform one authoritative status/receipt check on the next turn.

The prior SG-173 transport blocker in docs/worklogs/SG-173_architect.md is RESOLVED by this owner clarification. Its OpenCode-only reading was an Architect error. SG-173 is approved to launch here with coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max. Coder selection is independent of the Architect harness.

Next: push this clarification and trigger SG-173 once; audit the receipt before preparing repair implementation.
