# SG-232 architect note — close-deploy retry (L2 retry; launch record)

Planned envelope: `SG-232 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (same as SG-231; full Coder slice). Settings ride the trigger, never the packet (`D302`).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s). Same SSH client, key, `-o BatchMode=yes`.

Expected duration: ~400 s (SG-231 used 282 s to the STOP; full build legs add ~100-200 s per SG-202/SG-197 precedent; uncalibrated `G-A9`, bracketed not summed `D369`).

Retry basis (`ARCHITECT.md` §6): L2 owns one retry; this one fixes the ROOT cause (G0 ordered export-first step — SG-231 failed on the Coder's first call, packet already correct otherwise). A second failure stops the arc and returns to the owner — never a third.

Version chain: recorded `0.50.0 CURRENT` == adopted payload; host link STATED (`SG-231_report.md:7` echo 0.50.0).

Checklist (`DISPATCH.md` §2): scope = standing close-deploy + SG-231 audit retry (standing-authorized) · packet committed + pushed before trigger · worktree clean verified · SG-231 finished (no dispatch in flight) · nothing pushed while running · `PB-1` cited · receipt = notes-ref + Work-HEAD, read back on remote.

Production basis (`G-K2`/`G-K3`): declared surfaces touched only as authorized — one rebuild + one recreate + read-only verification; no data writes; reported either way.
