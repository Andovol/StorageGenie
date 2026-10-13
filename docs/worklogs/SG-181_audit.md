# SG-181 — Custody valid; rollback correction proven, key-replay defect confirmed, 94 no flag

## Receipt and independence

Trigger `SG-181 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` via background SSH (`job 707475cb`); wake carried `result=done exit=0`. Status verb read once after: `result=done id=SG-181 inactive`. Mapped notes receipt on `refs/notes/storagegenie-coder-reports` (explicit refspec fetch): first line `Dispatch-ID: SG-181 | Report: docs/worklogs/SG-181_report.md`, Work-HEAD `b0dd968d2a6771b5d5a8eded98baf714ee5f8e53`, Base `785fe7d5b70de414591c61bfbcf3609ccc6b06c7` (D1 adoption commit, clean at dispatch), Settings envelope-sourced `coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max`. Pulled `--ff-only` to `b0dd968`. Base→candidate diff is ten `docs/worklogs/SG-181*` artifacts only (probes, four run logs incl. one preserved failed path-probe log, report) — no product/config/test/lockfile/schema/migration/dependency edit. Custody is not acceptance of open defects.

## Independent verification (bodies read, not pass lines)

| Claim | Check | Result |
|---|---|---|
| F-SG181-1 asset key replay | `backend/app/api/v1/assets.py:82` `filter_by(key=...)` global, returns stored row `:83-87` with no household check | CONFIRMED defect; counter-controls (fresh-key own row, foreign GET/PATCH 403s) differ |
| F-SG181-2 C1 rollback | `SG-181_probe_g1.py:192-204` wrapper calls the REAL `candidates._create_asset_for_candidate`, flushes, asserts in-txn counts (3/3/1/3), raises AFTER the landed write; `:226-250` fresh independent engine2/session reads 2 assets (rolled back) with job FAILED; `:252-263` normal retry persists exactly +1 with assertions/links/audits | PROVEN correction; SG-180's fail-before-create claim stays retracted; SG-180 artifacts untouched |
| F-SG181-3 bare Resolve | `review_tasks.py:71-97` resolves any task with no type/data guard | CONFIRMED gap |
| F-SG181-4 foreign backing ref | `planning/service.py:337-347` — foreign `lot` misses the household catalog index, falls through to the label fallback storing the raw foreign id with no ownership check | CONFIRMED as bounded (opaque label value, no cross-household write), as reported |
| F-SG181-5 guardrail reader gap | `grep -rc GuardrailEvent backend/app/api/` → 0 in every route file | CONFIRMED at source level; intent stays UNVERIFIED |
| G1/G2/G3 0 FAIL | `grep -c FAIL` → G1 4 hits all inside `[PASS]`/FAILED-state captures, G2/G3 zero | 0 check failures; no placebo found in C1/If-Match/cursor bodies spot-read |
| Contract/host | Coder-measured host `VERSION=0.47.0`, payload `49338e39a574…`, HEAD `bdbbaa7`, tag present, tag-object peel explicitly NOT done | Stated, limitation honest; matches pre-dispatch recorded uncertainty |
| Isolation/spend | Per-probe temp `DATABASE_URL`/`STORAGE_ROOT` asserted pre-import; keys popped; production interaction = health GET only | No breach; no denial encountered (exclusion honoured, nothing routed around) |

## Accepted, rejected, deducted

Accepted: F-1 (OPEN defect), F-2 (correction PROVEN, SG-180-C1 discharged), F-3/4/5 (OPEN, bounded as stated), F-6/7/8 (OBSERVE, decision-owed), scenario inventory A1 distinctions, FIRST READ packet corrections (expiry prefix, 405-vs-404 shape). Rejected: nothing material — no false proof, no vacuous promotion (the one `or True` was removed pre-run and disclosed). Deducted: START health never captured (packet requires start/end + delta; delta underivable — admitted slice gap) and G2/G3 intermediate reruns overwrote same-path logs so raw-failure preservation is limited to the path-probe crash log plus embedded negative controls (disclosed). Both are process imperfections in an otherwise genuine evidence set: no flag, score below 95.

Architect judgement **94, no flag**. Failure class: model execution (baseline step skipped; log paths reused). Deduction attribution: coder; packet sound, environment clean. Owner impact: Coder worker ~640s of lane 2100s (Coder-reported; engine exact per runner record); trigger cap 2400s unused; cost and context-size readings unavailable. Recurrence lever (folded into SG-182, whose constraints already bind both): capture START health before the first probe import and never overwrite a run log — suffix reruns; this slice's omission + overwritten intermediates are the instance. No standalone slice: safety/product correctness do not require one.

## Dispositions (every REMAINING resolved)

R1 audit/rating/register-publish → this turn (this file + ratings row + STATE). R2 F-SG181-1 scoped repair → canonical register + NEW owner repair grant (SG-176/177/178 grants do not cover it; no implementation implied). R3 F-3/4/6/7/8 decisions → SG-182 consolidation, then owner. R4 per-field enrichment accept/conflict + true-concurrency If-Match → register as deferred executable scope, future owner-granted slice. R5 deployed effective flags/settings → SG-182 granted-surface proof. R6 frontend journey execution SC-04/05/06/08/09/12 → SG-182 consolidation against SG-175/179 UI evidence. R7 START-health/process gap → closed by the SG-182-bound lever above. R8 SG-175 hold + close obligations → standing; CLOSE_BLOCKED unchanged. Register merge itself is SG-182 G3's chartered consolidation (this audit delegates the merge there rather than risking a partial hand-edit now — Architect judgement).
