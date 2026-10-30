# SG-258 architect note — household and document dates (L3; launch record)

Stage: the household-and-document stage, approved by the owner on 2026-10-30 (`"d6 - approved"`, D6; `docs/decisions/2026-10-30-session-approvals.md`). This is the stage's work slice; the deploy rider SG-259 follows the rating. The second opinion ran before this packet was committed: SG-260 (Phase A blind) and SG-261 (Phase B critique), `opencode-go/muse-spark-1.3-contributor` effort=xhigh, `agent=plan`; the picks and dispositions are in `docs/reviews/review-ledger.md` and the decision file.

Planned envelope: `SG-258 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` — the project's model policy (the Coder's contract on the server; the Architect runs on `opencode-go/minimax-m3.1-flash`, so the work model is not the review model).

Packet: `docs/packets/SG-258-household-documents.md` (commit `c6bda4b`, pushed before the trigger). Context: the second-opinion reports `docs/worklogs/SG-260_report.md`, `docs/worklogs/SG-261_report.md`; the context pack `docs/reviews/2026-10-30-household-documents-context.md`.

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ≈1500 s, bracketed from this lane's recent actuals (SG-240 1504 s for a comparable backend+frontend slice; SG-256 540 s; SG-257 451 s). The packet's publish-before-the-bound is 1500 s; a partial slice with a receipt is a success.

Version chain: recorded `0.56.0` == published payload `contract-v0.56.0`; the host copy last echoed `0.53.0` at SG-257. The `0.53.0 → 0.56.0` delta is named in `docs/decisions/2026-10-30-session-approvals.md`; the Coder must echo its own copy's version and state it. The packet carries this chain.

Checklist (`DISPATCH.md` §2): scope = the owner-approved D6 stage · Coder/model/effort stated (this note) · packet committed + pushed before the trigger (`c6bda4b`) · worktree clean · no dispatch in flight (SG-261 exited; `SG-261 --status` checked) · nothing pushed while running · packet states expected conditions as hypotheses (`PB-1`) · expected duration recorded here · ONE backgrounded call · the version chain stated · the receipt commands are written out in the packet · the report requirement restated. No requirement pairs a runner action with in-slice proof.

Production basis (`G-K2`/`G-K3`): none for this slice. The work slice touches only the app code and tests; no host action, no database open, no provider, no credential, no live container, no deploy; $0. The rider SG-259 is the only host action, inside the D6-approved plan (one build, one recreate, read-only census, health checks, release record/tag).

Design calls: the packet's G1–G4. The second opinion's refinements are folded in: documents' OCR proposal suppressed; category hint; optional `If-Match` (classification/expiry assertion ids); accepted-only date preservation; reverse-move clear to a null active; classification-profile form gate; exact-field/latest-`created_at` active read; Clear parity with D4; `valid_until` date type. The keepsake scope risk is noted; the owner's D6 outcome stands.

The work slice is rated before the rider; the rider packet is written only after the rating and stays inside the D6 plan.
