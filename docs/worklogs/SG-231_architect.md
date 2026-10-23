# SG-231 architect note — standing close-deploy rider (re-proof; launch record)

Planned envelope: `SG-231 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (standing model policy, owner D-1012-15; no `agent=` — full Coder slice, not a review). Settings ride the trigger, never the packet (`D302`).

Trigger class: OpenCode `job_spawn`, wake on exit (`DISPATCH.md` §2c). ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). Same SSH client, key, and `-o BatchMode=yes` as SG-229/230.

Expected duration: ~500 s (bracketed by lane actuals SG-202 ≈ 380 s and SG-197 ≈ 514 s of `RUN_BUDGET_S=2100`; uncalibrated `G-A9`, no summed guesses `D369`).

Version chain (pre-dispatch): recorded `0.50.0 CURRENT` (cache at tag `contract-v0.50.0`) == adopted payload; host link STATED (`SG-226_report.md:4` echo). Read-only-plus build/recreate slice; contract text beyond the packet not needed.

Checklist (`DISPATCH.md` §2): scope = standing 2026-09-28 close-deploy directive after D-33 (all accepted, zero product delta) — standing-authorized, no new scope word owed · packet committed and pushed before trigger · worktree clean verified · SG-230 finished (no dispatch in flight) · nothing will be pushed while it runs · `PB-1` cited · receipt = notes-ref + Work-HEAD, read back on remote (`{{RECEIPT_CMD}}` bound).

Production basis (`G-K2`/`G-K3`): declared sensitive surfaces (SQLite DB, evidence store, dispatch host) touched only as the standing directive authorizes — one rebuild + one recreate + read-only verification; no data writes; reported either way.
