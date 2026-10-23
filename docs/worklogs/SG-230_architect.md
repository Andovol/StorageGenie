# SG-230 architect note — Phase B critique on N-1 (launch record; pick inside the packet only)

Planned envelope: `SG-230 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max agent=plan` — same reviewer as Phase A, never the Architect's own model (`D451`). Model + effort ride the dispatch command, never the packet (`D302`).

Trigger class: OpenCode `job_spawn`, wake on exit (`DISPATCH.md` §2c). ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). Same SSH client, key, and `-o BatchMode=yes` as SG-229.

Expected duration: ~389 s ceiling (rule-stated 127–389 s review window; uncalibrated `G-A9`) plus local packet/commit legs.

Version chain (unchanged since SG-229): recorded `0.50.0 CURRENT` (cache at tag `contract-v0.50.0`) == adopted payload; host link STATED (`SG-226_report.md:4` echo). Read-only review needs no contract text beyond the pack.

Checklist (`DISPATCH.md` §2): scope = `D451` Phase B (read-only, no production surface) · Phase A report committed unedited at `docs/worklogs/SG-229_report.md` before this packet · packet + note committed and pushed before trigger · worktree clean verified · SG-229 finished (no dispatch in flight) · nothing will be pushed while it runs · `PB-1` cited · receipt = engine-published final message read back via `SG-230 --status`, copied unedited to `docs/worklogs/SG-230_report.md`; no Coder-side receipt note.

The Architect's N-1 pick lives verbatim in the SG-230 packet (as `D451` requires) and nowhere else new — it was in no committed file before Phase A ran.
