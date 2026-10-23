# SG-229 architect note — Phase A blind review on N-1 next stage (launch record, NO PICKS)

Planned envelope: `SG-229 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max agent=plan` — reviewer is never the Architect's own model (`D451`; Architect runs muse-spark-1.3; matches the SG-200/201 precedent reviewer). Model + effort ride the dispatch command, never the packet (`D302`).

Trigger class: OpenCode `job_spawn`, wake on exit (`DISPATCH.md` §2c). ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client `C:\WINDOWS\System32\OpenSSH\ssh.exe`, key `~/.ssh/storagegenie-architect-dispatch`, `-o BatchMode=yes` so an auth failure fails loudly instead of hanging on a prompt.

Expected duration: ~389 s ceiling per phase (rule-stated 127–389 s review window, `SECOND_OPINION.md` §Where; uncalibrated `G-A9`) plus local pack/packet/commit legs. No guessed per-goal sum (`D369`).

Version chain (pre-dispatch): recorded `0.50.0 CURRENT` (`rules_check.sh` CLEAN ×3, cache at tag `contract-v0.50.0`) == adopted payload; host link STATED: host contract copy echoed `0.50.0` on the last receipt (`SG-226_report.md:4`; host `.rules-cache/` absent as designed). Read-only review needs no contract text beyond the pack (standing lane condition `review-ledger.md:11`).

Checklist (`DISPATCH.md` §2): scope = the `D451` standing duty triggered by the owner's next-stage request (read-only, no production surface) · packet + pack committed and pushed before trigger · worktree clean verified · no other dispatch in flight (`job_list` all exited) · nothing will be pushed while it runs · packet states hypotheses as hypotheses · `PB-1` cited · receipt = engine-published final message read back via `SG-229 --status`, copied unedited to `docs/worklogs/SG-229_report.md`; no Coder-side receipt note (SG-200 shape).

Packet/line audit for blindness: neither the packet nor the pack nor this note contains a pick for N-1. Phase B packet (with the pick verbatim) is written ONLY after Phase A's report is committed.
