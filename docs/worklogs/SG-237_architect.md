# SG-237 architect note — D2 live reminder proof (L2; launch record)

Planned envelope: `SG-237 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (same as SG-235/SG-236). Settings ride the trigger, never the packet (`D302`).

Packet: `docs/packets/SG-237-live-reminder-proof.md` (committed and pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s). Same SSH client, key, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`.

Expected duration: ~300 s (G0 + pre-state + two route writes + one restart + read-only observation; the previous riders used 397 s and 429 s — bracketed, not summed `D369`).

Version chain: recorded `0.52.0` == published payload `contract-v0.52.0` == host copy `0.52.0` (SG-235 and SG-236 echoes) == the echo the next report must carry.

Checklist (`DISPATCH.md` §2): scope = the owner's D2 approval (D-1024-7, 2026-10-24, quoted in the packet) · packet committed + pushed before trigger · worktree clean verified · no dispatch in flight · nothing pushed while running · `PB-1` cited · receipt = notes-ref + Work-HEAD, read back on remote.

Production basis (`G-K2`/`G-K3`): the app database is a declared sensitive surface. This slice writes **three** rows in production — one classification assertion, one expiry assertion, one reminder row created by the daily pass itself — all under the owner's written grant (D-1024-7). One container restart, same image, no build, no recreate, no migration. Zero other row touched; zero provider call; $0. The reminder is left unread so the owner can act on it from the Expiry page.

Note: D1 (the two always-red signal tests) is **not** in this slice — it is SG-238, and its cheapest route is the project's own image, which already installs both libraries, so the authorised host package install stays unused.

After this slice: SG-238 (scope gates + the daily-pass success log line + the image-based proof of the two reds), then roadmap row 11 (opened-date countdown for cosmetics).
