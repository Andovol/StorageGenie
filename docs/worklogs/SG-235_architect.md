# SG-235 architect note — daily reminder caller plus Expiry Read/Dismiss actions (L2; launch record)

Planned envelope: `SG-235 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (same as SG-233/SG-234). Settings ride the trigger, never the packet (`D302`).

Packet: `docs/packets/SG-235-daily-reminder-caller-and-expiry-actions.md` (committed and pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client `C:\WINDOWS\System32\OpenSSH\ssh.exe`, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`.

Expected duration: ~900 s (bracketed between SG-233's 745 s product slice and SG-234's 429 s deploy rider; no migration this time, plus a frontend suite run — uncalibrated `G-A9`, bracketed not summed `D369`).

Version chain: recorded `0.52.0` (`AGENTS.md:4`, `STATE.md:6`) == published payload `contract-v0.52.0` (cache `VERSION` = 0.52.0) — the controlled axis, equal. Host link **STATED, not equal**: SG-234's report echoes `0.51.0` from `/home/andrei/storagegenie-contract/CODER.md` (last slice on this host); the desk states the engine went live at 0.52.0 on 2026-10-24 10:24Z. The 0.51.0 → 0.52.0 contract-text delta is NAMED in the packet (RULES.md reworked `8048dd35…` → `795851b0…`; RATIONALE.md +18; CO-104 `Verification:` line; LNR-183 restart refusal; G-O1/D493, G-M11/D501, G-L1/D502).

Checklist (`DISPATCH.md` §2): scope = owner-approved 2026-10-24 (D-1024-2 daily caller + the Read/Dismiss buttons) · packet committed + pushed before trigger · worktree clean verified · no dispatch in flight (`job_list` empty) · nothing pushed while running · `PB-1` cited · receipt = notes-ref + Work-HEAD, read back on remote.

Retry basis (`ARCHITECT.md` §6): L2 — the owner approves the slice once, the Architect owns ONE retry inside it, and the retry must fix the root cause. A second failure stops the arc and returns to the owner.

Production basis (`G-K2`/`G-K3`): the app database is a declared sensitive surface. This slice's own runs are scratch temp SQLite only (`DATABASE: none`); no deploy, no restart, no image build, no host timer. The production write the feature will make (reminder rows for the household) is the owner-approved behaviour of 2026-10-24 (D-1024-2) and it lands only at the close-deploy rider, which is a separate owner-visible step.

Owner's step list this session: steps 1–3 done (contract 0.52.0 adopted; `release-2026-10-23` tag + release record; PRs #43–#49 and Launcher #89 closed, Launcher #84 deferred to this slice's result). This is step 4. Step 5 (STATE.md RESUME line + startup record naming #84 and #89) and step 6 (close-out: deploy, release record, END report, close) follow.
