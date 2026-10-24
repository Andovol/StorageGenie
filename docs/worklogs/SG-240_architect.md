# SG-240 architect note — roadmap row 11 (opened-date countdown) + the app's logging configuration (L3; launch record)

Stage: roadmap row 11 and its close-deploy rider, approved by the owner on 2026-10-24 (`docs/decisions/2026-10-24-l3-stage-row11-approval.md`, D-1024-8).

Planned envelope: `SG-240 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (same as SG-235…SG-239). Settings ride the trigger, never the packet (`D302`).

Packet: `docs/packets/SG-240-opened-countdown-and-logging.md` (commit `8e22760`, pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). Same SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`.

**The remote command carries the VERB only — no `dispatch` prefix.** The wrapper `/usr/local/bin/dispatch` is the forced command; its own header states `VERB: <ID> [coder=<c>] [model=<m>] [effort=<e>] [agent=<a>] [--status|--attach|--force|--quarantine]`, and it takes the FIRST word as the ID. Sending `dispatch SG-240 …` made the ID `dispatch` and the real ID an unknown word: `result=reject reason=bad_word:SG-240 id=dispatch` — refused at the door, **nothing ran, no slice started**. The correct remote command is `SG-240 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max`. (Recorded so the next session does not repeat it; `AGENTS.md`'s "Dispatch verb" row already said the verb is `SG-<number>` — the error was mine, not the project's.)

Expected duration: ~1200 s (bracketed from this lane's recent actuals — 700, 397, 268, 700, 324 s — not summed per-goal guesses, `D369`).

Version chain: recorded `0.52.0` == published payload `contract-v0.52.0` == host copy `0.52.0` (the SG-235…SG-239 echoes) == the echo the next report must carry. `rules_check.sh` this session: all three installed harness copies CLEAN, VERSION CURRENT 0.52.0.

Checklist (`DISPATCH.md` §2): scope = the owner-approved stage (row 11 + its rider) · packet committed + pushed before the trigger · worktree clean verified at `8e22760` · no dispatch in flight · nothing pushed while running · `PB-1`–`PB-6` cited · receipt = notes-ref + Work-HEAD, read back from the fetched remote ref.

Production basis (`G-K2`/`G-K3`): the app database and the host are declared sensitive surfaces. **This slice touches neither**: no production read beyond G5's read-only census, no production write, no migration, no change to the running container, no host configuration change, no provider call, $0. The G1 container proof builds a **new tag** (`storagegenie-backend:sg240-proof`) and runs a **throwaway** container with a SQLite inside it; `storagegenie-backend:latest` — the tag the running production container was built from — is not overwritten.

Design calls SG-240 makes (so the next session does not re-derive them): the countdown's end is the category's after-opening window, cosmetics declaring **12 months**, **declared uncalibrated** at the site and sourced to the EU period-after-opening symbol (Regulation 1223/2009 Art. 19), the printed figure varying per product; the window and its source are named in the response so the number is visible and correctable; a **per-item PAO override is parked**. Storage is one accepted `opened_date` assertion with a bare JSON string value — the shape the planning and chat services already read.

The next slice after this one is the standing close-deploy rider: build the image, recreate the container, and the **first live observation of the daily pass's success line** — which is only possible because SG-240 configures the app's logging.
