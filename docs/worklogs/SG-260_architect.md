# SG-260 architect note — second opinion Phase A (blind) on the household-and-document implementation (L3; launch record)

Stage: the household-and-document stage, approved by the owner on 2026-10-30 (`"d6 - approved"`, D6; `docs/decisions/2026-10-30-session-approvals.md`). This slice is the **T3 blind pass** (`SECOND_OPINION.md` 0.56.0, `D555`) required before the Architect commits the stage's work packet. It is not a product slice.

Planned envelope: `SG-260 coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh agent=plan` — the project's second-opinion lane (the Architect runs on `opencode-go/deepseek-v4.1-flash`, so the reviewer is not the Architect's model; `agent=plan` is read-only).

Packet: `docs/packets/SG-260-second-opinion-a-blind-household-documents.md` (commit `15f8cb9`, pushed before the trigger). Context pack: `docs/reviews/2026-10-30-household-documents-context.md` (same commit).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ≈127–389 s, the project's measured two-phase review range (`SECOND_OPINION.md`), with the context pack already written.

Version chain: recorded `0.56.0` == published payload `contract-v0.56.0`; the host copy last echoed `0.53.0` at SG-257 and has not been re-read since. The 0.53.0 → 0.56.0 delta is named in `docs/decisions/2026-10-30-session-approvals.md`; the reviewer must echo its own copy's version and state it. This is a read-only review, not product work; the pre-migration host-link rule is stated, not equal.

Checklist (`DISPATCH.md` §2): scope = the owner-approved D6 stage and the T3 trigger · packet committed + pushed before the trigger (`15f8cb9`) · worktree clean · no dispatch in flight (`SG-257 --status` returned `result=done id=SG-257 inactive`) · nothing pushed while running · `PB-1`–`PB-6` cited · the report is engine-published and read back with `SG-260 --status`; a read-only review publishes no receipt note.

Production basis (`G-K2`/`G-K3`): none. No host action, no database, no container, no provider, no credential, no browser, no external network; $0. The review reads only the repository at `origin/automation`.

Design calls: the four implementation choices (D-A Documents/other date; D-B classification control; D-C reclassification date preservation; D-D expiry-date form) are listed in the context pack without the Architect's pick, so the pass is blind. The owner's approval is the stage outcome, not the implementation. Phase B (`SG-261`) is written only after this report is committed, and carries the Architect's pick verbatim for critique.
