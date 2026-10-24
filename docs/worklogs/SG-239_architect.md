# SG-239 architect note — close-deploy rider for the SG-238 success line (L2; launch record)

Planned envelope: `SG-239 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (same as SG-235/236/237/238). Settings ride the trigger, never the packet (`D302`).

Packet: `docs/packets/SG-239-close-deploy-rider.md` (committed and pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s). Same SSH client, key, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`.

Expected duration: ~400 s (SG-236's rider used 397 s for the same shape: G0, pre-state, build 29 s, recreate 1.4 s, post verification, report — bracketed, not summed `D369`).

Version chain: recorded `0.52.0` == published payload `contract-v0.52.0` == host copy `0.52.0` (SG-235/236/237/238 echoes) == the echo the next report must carry.

Checklist (`DISPATCH.md` §2): scope = the standing close-deploy directive plus the owner's close instruction this session · packet committed + pushed before trigger · worktree clean verified · no dispatch in flight · nothing pushed while running · `PB-1` cited · receipt = notes-ref + Work-HEAD, read back on remote.

Production basis (`G-K2`/`G-K3`): the app database and the host are declared sensitive surfaces. One rebuild + one recreate through the lane socket, read-only verification, and **zero** production rows written by the slice: the startup pass finds today's row already present and creates nothing (`reminders_created=0` is the live idempotence proof). The Miso Soup reminder is left **unread** for the owner. No migration, no host config change, no provider call, $0.

Why this rider is also the close's deploy: SG-238 changed product code (one runtime line), so the project's standing rule — deploy the live app and record a release before every close — requires this slice before the session can close. After it: the release record + tag for the served bytes, the END report on Launcher issue 62, and the close.

Waste: the SG-238 audit named `66s candidate-suite-raw`; the rider waives the full suite per `PG-DP-02` (restart-gated, one runtime line changed) → the waste is removed by construction.
