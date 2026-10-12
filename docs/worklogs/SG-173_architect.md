# SG-173 — Architect preparation and dispatch constraint

2026-10-12, Europe/Bucharest. Owner request: "packetize + dispatch D-1012-14 end-to-end review-to-catalog story repair as SG-173 (story walk first per PG-DP-03, then chain repair ...; D-1012-13 folded in)."

## Session-start reconciliation

Git Bash `.rules-cache/rules_check.sh` completed exit 0 before investigation. Output:

```text
G-L1 claude CLEAN installed=487841b151a5 /c/Users/popes/.claude/CLAUDE.md
G-L1 codex CLEAN installed=487841b151a5 /c/Users/popes/.codex/AGENTS.md
G-L1 opencode CLEAN installed=487841b151a5 /c/Users/popes/.config/opencode/AGENTS.md
G-L1 VERSION CURRENT adopted=0.46.0 shared=0.46.0
R15 codex combined=33862 cap=131072 spare=97210 ~/.codex/config.toml
R15 grok agents_md=9264 cap=10000 spare=736
G-L5 FILED #62 Session reports: StorageGenie last=filer age=17d
G-L7 PR #49 author=Andovol base=automation age=7d
G-L7 PR #48 author=Andovol base=automation age=8d
G-L7 PR #47 author=Andovol base=automation age=9d
G-L7 PR #46 author=Andovol base=automation age=10d
G-L7 PR #45 author=Andovol base=automation age=11d
G-L7 PR #44 author=Andovol base=automation age=12d
G-L7 PR #43 author=Andovol base=automation age=13d
G-L6 BYTES /c/Users/popes/.claude/CLAUDE.md 24487
G-L6 BYTES /c/Users/popes/.codex/AGENTS.md 24487
G-L6 BYTES /c/Users/popes/.config/opencode/AGENTS.md 24487
G-L6 BYTES /c/Coding/OpenCode/StorageGenie/AGENTS.md 9375
G-L6 BYTES /c/Coding/OpenCode/StorageGenie/CLAUDE.md 11
G-L6 BYTES total[codex]=33873 unseen=architect-layer,state-file,other-ritual-files
```

Hashes are abbreviated by the project's check; SG-172's prior report records full adopted SHA256 `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef`. Cache exact tag contract-v0.46.0, clean. Initial local/remote automation equals dcc12cd05f339a0c48eca5f570027e96f6f4a87c; local tree clean. RESUME read first after the check. Previous report host contract echo 0.46.0 is historical evidence, not a fresh host measurement. Live image 9064d2ce is likewise prior SG-172 evidence, pending SG-173 observation.

## Sequencing and envelope

L2 remains the project setting. SG-173 is the story diagnosis, preceding the approved repair chain; PACKET.md §5 separates diagnosis from implementation. No production mutations needed/authorized by this packet. Planned envelope: `SG-173 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max`; cap 2400s covering recorded lane RUN_BUDGET_S=2100 plus stop window, subject to current lane readback. Model/effort apply per D-1012-15; max is uncalibrated.

Expected duration: UNVERIFIED — no comparable recent complete story diagnostic was found in the bounded reads of SG-171/172 reports and ratings headings; do not derive a duration by adding goal estimates. Actual to be compared once a defensible baseline exists. Exact Codex usage unavailable; expected preparation cost MEDIUM is author judgement.

## Dispatch blocker and next action

At 2026-10-12 23:22 Europe/Bucharest, forced-command `SG-172 --status` returned `result=done id=SG-172 inactive`. No new dispatch was launched.

Tool inventory was inspected for job_spawn/background/wake. This Codex session has exec_command session tools, but no job_spawn. STATE RESUME explicitly says job_spawn-only; AGENTS Harness row and docs/proposals/2026-09-14-jobspawn-dispatch-transport.md preserve the owner directive. This is a transport/configuration mismatch, not a failed SG-173 run. No detached shell substitute or watcher was installed.

Next action: launch the committed SG-173 packet from an OpenCode Architect session exposing job_spawn; alternatively owner explicitly authorizes this Codex session to use DISPATCH §2c Class 4 (one detached trigger, end turn, one status check on the next turn). No code repair, rating or deploy has happened here.
