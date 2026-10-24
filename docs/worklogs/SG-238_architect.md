# SG-238 architect note — durable gates + the daily-pass success line + the signal-test proof (L2; launch record)

Planned envelope: `SG-238 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (same as SG-235/236/237). Settings ride the trigger, never the packet (`D302`).

Packet: `docs/packets/SG-238-gates-log-line-signal-tests.md` (committed and pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s). Same SSH client, key, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`.

Expected duration: ~600 s (two test-file rewrites with seen-to-fail demos, one log line plus its test, one image run, one host suite run — bracketed from SG-237's 268 s and the earlier ~600 s product slices; uncalibrated `G-A9`, bracketed not summed `D369`).

Version chain: recorded `0.52.0` == published payload `contract-v0.52.0` == host copy `0.52.0` (SG-235/236/237 echoes) == the echo the next report must carry.

Checklist (`DISPATCH.md` §2): scope = D-1024-6 (owner-approved) + the two audit-queued fixes (the daily-pass success line, the two stale scope gates) · packet committed + pushed before trigger · worktree clean verified · no dispatch in flight · nothing pushed while running · `PB-1` cited · receipt = notes-ref + Work-HEAD, read back on remote.

Production basis (`G-K2`/`G-K3`): `DATABASE: none` and `Restart: none`. The one executed runtime is a throwaway container from the already-built local image (no bind mount, no write to the running container). The host package install of `libzbar0` + `tesseract` is authorised by D-1024-6 **only** if `sudo -n true` succeeds; otherwise no host change is attempted and the fact is reported (`PG-PR-03`). The G2 log line becomes live at the next close-deploy rider, not in this slice.

Not in this slice: the unread Miso Soup reminder — the owner clicks Read/Dismiss on it; no slice touches it.
