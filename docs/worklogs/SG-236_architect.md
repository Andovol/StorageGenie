# SG-236 architect note — close-deploy rider for the SG-235 delta (L2; launch record)

Planned envelope: `SG-236 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (same as SG-235/SG-234). Settings ride the trigger, never the packet (`D302`).

Packet: `docs/packets/SG-236-close-deploy-rider.md` (committed and pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). Same SSH client, key, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`.

Expected duration: ~500 s (SG-234's rider used 429 s of 2100; the extra is the live startup-pass observation wait — uncalibrated `G-A9`, bracketed not summed `D369`).

Version chain: recorded `0.52.0` == published payload `contract-v0.52.0` == host copy `0.52.0` (SG-235's report read `/home/andrei/storagegenie-contract/CODER.md` and echoed 0.52.0) == the echo the next report must carry. All four links equal for the first time this session.

Checklist (`DISPATCH.md` §2): scope = owner close instruction (step 6 of this session) + the standing close-deploy directive in `AGENTS.md` · packet committed + pushed before trigger · worktree clean verified · no dispatch in flight · nothing pushed while running · `PB-1` cited · receipt = notes-ref + Work-HEAD, read back on remote.

Production basis (`G-K2`/`G-K3`): the app database and the host are declared sensitive surfaces. One rebuild + one recreate through the lane socket, read-only verification, and the **one** production write the feature itself causes — the startup pass inserting today's engine-shaped `reminder` rows for the live household (D-1024-2). No schema change, no other row written, no provider call, $0. The rows are the owner-approved behaviour, not a side effect to be cleaned up.

Waste: the SG-235 audit named `58s full-suite-raw`; the rider waives the full suite per `PG-DP-02` (restart-gated), so the waste is removed by construction rather than by instruction.

After this rider: the release record for the shipped bytes, then the END report on Launcher issue 62 and the session close.
