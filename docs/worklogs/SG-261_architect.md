# SG-261 architect note — second opinion Phase B (critique) on the household-and-document picks (L3; launch record)

Stage: the household-and-document stage, approved by the owner on 2026-10-30 (`"d6 - approved"`, D6; `docs/decisions/2026-10-30-session-approvals.md`). This slice is the **Phase B critique** (`SECOND_OPINION.md` 0.56.0, `T3`, `D555`) of the Architect's picks for the stage's implementation. It is not a product slice.

Planned envelope: `SG-261 coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh agent=plan` — the project's second-opinion lane (the Architect runs on `opencode-go/deepseek-v4.1-flash`, so the reviewer is not the Architect's model; `agent=plan` is read-only).

Packet: `docs/packets/SG-261-second-opinion-b-critique-household-documents.md` (commit `99b505d`, pushed before the trigger). Inputs: the context pack `docs/reviews/2026-10-30-household-documents-context.md` and the Phase A report `docs/worklogs/SG-260_report.md` (commit `58ad31e`).

The picks under critique, verbatim from the packet:

- **D-A — A1**, with the `_observed_date` proposal suppressed for documents; reuse the existing `expiry_date` field and date-type list; no new `DateType` this slice.
- **D-B — B1**, a classification control on the asset detail page, using the served taxonomy and the existing classification route; no `If-Match`.
- **D-C — C1**, skip both the placeholder and the observed-date proposal when an active expiry exists; the reverse move into `non_perishable` keeps the date active (today's behaviour), tested and reported.
- **D-D — D1**, show the date form for a classified category with windows, read the active plugin assertion, pre-fill accepted/proposed, Save writes accepted; no clear action this slice.

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ≈127–389 s, the project's measured review range (`SECOND_OPINION.md`).

Version chain: recorded `0.56.0` == published payload `contract-v0.56.0`; the host copy last echoed `0.53.0` at SG-257. The 0.53.0 → 0.56.0 delta is named in `docs/decisions/2026-10-30-session-approvals.md`; the reviewer must echo its own copy's version and state it. Read-only review; the pre-migration host-link rule is stated, not equal.

Checklist (`DISPATCH.md` §2): scope = the owner-approved D6 stage and the T3 trigger · packet committed + pushed before the trigger (`99b505d`) · worktree clean · no dispatch in flight (`SG-260` exited; `SG-261` is the only call) · nothing pushed while running · `PB-1`–`PB-6` cited · the report is engine-published and read back with `SG-261 --status`; a read-only review publishes no receipt note.

Production basis (`G-K2`/`G-K3`): none. No host action, no database, no container, no provider, no credential, no browser, no external network; $0. The review reads only the repository at `origin/automation`.

Design calls: the Phase B findings inform the SG-258 packet; a material objection is reported to the owner before the work is dispatched. The stage's work slice (SG-258) and its rider (SG-259) follow this review.
