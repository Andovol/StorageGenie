# StorageGenie — Coder ratings

Schema: shared `LEDGER.md` — nine columns, `guards_invoked` + `deduction_attribution` included. Below-95 investigations per shared `RATING_ISSUE.md` sit under their row. No pooled ledger (D30): rows live here, nothing aggregates them.

| slice_id | phase | model | effort | score | flag | lever | guards_invoked | deduction_attribution |
|---|---|---|---|---|---|---|---|---|
| SG-003 | Phase 0 | codex (audit: gpt-5.6-luna) | medium | 82 |  | G5-prefill: every future SG packet orders push-WORK_HEAD-to-evidence-ref + verify equality BEFORE invoking RECEIPT_CMD (verbatim block carried in SG-004) | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-10, PG-EV-06, PG-PR-03, PG-PR-04 | packet |
| SG-004 | Phase 0 | codex (audit: unknown per identity line) | medium | 96 |  |  | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-10, PG-EV-06, PG-PR-03, PG-PR-04 | coder |
| SG-005 | Phase 0 | codex (audit: unknown per identity line) | high | 97 |  |  | PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09 |  |
| SG-006 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09 |  |
| SG-007 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09 |  |

## SG-003 investigation (score 82 < 95)

1. **Failure class:** prompt gap.
2. **Root cause:** packet G5 ordered "publish with RECEIPT_CMD" but never the evidence-prefill push that `finalize_dispatch_report.sh` gates on (`candidate_not_remote`: `origin/storagegenie-evidence` must equal CANDIDATE first). The precondition lived only in the host script, which packet authoring never read (G-A10 miss).
3. **Exact correction:** G5 gains: push `<WORK_HEAD>:refs/heads/storagegenie-evidence`, fetch, verify equality, then invoke RECEIPT_CMD; a post-prefill `candidate_not_remote` is a STOP.
4. **Recurrence guard:** the lever above — pasted into every future SG packet G5.
5. **Owner impact:** run completed inside one 15 min client window (bound, not estimate); cost unavailable (platform exposes none).
6. **Attribution note:** coder execution was contract-correct throughout (CO-54 refusal to hand-move the ref, CO-57 unconditional report, non-vacuous gates, honest BLOCKED first line). No flag: no false completion, no breach.