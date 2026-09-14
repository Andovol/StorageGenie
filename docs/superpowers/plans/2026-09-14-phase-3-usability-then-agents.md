# Phase 3 — usability block, then agents (slice plan)

**Basis:** design `docs/superpowers/specs/2026-09-14-phase-3-design.md` (S1/S2/S3 owner-approved 2026-09-14);
blueprint v3 §14 Phase 3 (p. 524–531, exit:531), §10 guardrails, §11 UX, §12 threats. **Execution rides
packets and dispatches** (`PACKET.md`/`DISPATCH.md`, `job_spawn` transport per `AGENTS.md`), not subagents —
each slice below is one packet, one dispatch, one rating. **IDs:** SG-031 is the queued picker;
SG-032 is spent (lane probe); Phase 3 runs SG-031 then SG-033…SG-039 in order.

**Exit condition (blueprint:531 + this stage's bar):** daily planning suggestions and category chat are
functional; guardrail rollout tracking (§10) is active; the usability block is shippable on screen;
Cosmetics is tracked with opened-date.

## Global constraints (every slice)

AI OFF by default (`SG_PROVIDER_ID=fake`, `SG_CONSENT=false`); cloud calls consent-gated and
cost-ledgered per call; caps uncapped per F2 with re-evaluation owed (mechanisms must still refuse
pre-call when a cap is set); prompt files versioned, never edited in place; no live web fetching;
no automatic scheduling; human confirmation mandatory on every health-adjacent proposal (Stage 0);
`Unknown` stays valid and easy, never a guessed date; packet carries the coder-role line (SG-027 lesson);
proof per the standing bar (fix-driven tests FAIL-then-PASS raw; pre-existing-flow proof by source
mutation, SG-030 pattern); packet ceiling built FROM the requirement list (M4); every acceptance
requirement covered by the scope ceiling (M6); pre-existing-claim premises cite base proof; 128 KiB
packet ceiling; effort medium default (proven across the Phase 2 arc); no model id sent.

## Slice 1 — SG-031: model-picker UI + frontend build proof

**Outcome:** switching AI models is configuration on the Settings screen, tested-models-only (D42);
the long-queued `npm run build` proof lands here and stands for every later UI slice.
**Files:** modify `frontend/src/routes/SettingsPage.tsx`, `frontend/src/api/client.ts`
(+ `frontend/src/api/types.ts` if the settings shape grows); modify `backend/app/config.py` and
`backend/app/api/v1/` settings surface ONLY if `SG_MODEL_ID` is not already readable — else UI only;
create `frontend/src/routes/SettingsPage.test.tsx`; `README.md` one-line picker note if behavior changes.
**Out of scope:** new providers, prompt changes, any other screen.
**Tests:** frontend test (picker lists tested models, persists selection); backend settings test only if
touched; `npm run build` green with output quoted; backend suite + ruff quoted.

## Slice 2 — SG-033: multi-item split review UI

**Outcome:** a photo with several items splits into separate asset drafts on screen, each keeping its
photo link and source record (pipeline already preserves multi-item per SG-028).
**Files:** modify `frontend/src/routes/ReviewPage.tsx`, `frontend/src/components/CandidateCard.tsx`
(+ test files beside them); modify `backend/app/api/v1/review_tasks.py`, `backend/app/api/v1/candidates.py`,
`backend/app/api/v1/assets.py` only as the split action requires; modify `backend/app/services/candidates.py`
and/or `backend/app/services/asset_service.py` for the split operation; extend `backend/tests/test_candidates.py`
(or new `test_review_split.py` if the seam deserves it).
**Out of scope:** extraction changes, auto-split heuristics, new categories.
**Tests:** split preserves per-candidate provenance + evidence links (negative: no field becomes
a guessed value); frontend test for the split action; `npm run build` green.

## Slice 3 — SG-034: manual entry per field + on-screen corrections

**Outcome:** every review field is hand-typeable with Unknown one tap away; accepted fields are
editable on screen with the old value kept superseded and visible in asset history (chain exists
per SG-028/030 — today API-only).
**Files:** modify `frontend/src/components/ExpiryEntryForm.tsx`, `frontend/src/components/AssetForm.tsx`,
`frontend/src/routes/AssetDetailPage.tsx` (+ beside tests); modify `backend/app/services/assertion_service.py`
(supersede path) and `backend/app/api/v1/review_tasks.py` / `assets.py` only as the flows require;
extend `backend/tests/test_assertions.py` and/or `test_candidate_read.py`.
**Out of scope:** new AI behavior, schema changes, prompt changes.
**Tests:** hand-entered values commit as user assertions with prior superseded + audit row; Unknown needs
no date; frontend tests for entry + correction flows; `npm run build` green.

## Slice 4 — SG-035: data foundations (attribution + planning records + guardrail log)

**Outcome:** additive schema only — source-attribution fields, planning suggestion records
(pending/confirmed/dismissed linked to backing label data), guardrail log tables; no routes, no agents.
**Files:** create/modify `backend/app/models/` (new model files), one alembic migration in
`backend/alembic/versions/` (upgrade + head-relative downgrade per the standing migration line);
model/migration tests in `backend/tests/` (apply/rollback on temp DB).
**Out of scope:** API routes, agent logic, UI, web fetching.
**Tests:** migration upgrade/downgrade/upgrade; record lifecycle unit tests; suite + ruff + mypy quoted.

## Slice 5 — SG-036: Cosmetics category + opened-date

**Outcome:** third category live on the same proven rails — taxonomy entry, versioned prompt file,
opened-date field with unknown-valid discipline, eval fixtures.
**Files:** create `backend/app/services/providers/prompts/extract-cosmetics-v1.*`; modify
`backend/app/plugins/expiry_tracker.py` (taxonomy + behavior profile) and `registry.py` only as needed;
extend `backend/eval/corpus/` (cosmetics fixtures + ground truth) and `backend/eval/run.py` only as needed;
`backend/tests/test_plugin_expiry.py` + `test_extraction_contract.py` extensions.
**Out of scope:** prompt tuning of frozen v1 files, agents, UI (uses existing review screens).
**Tests:** cosmetics fixtures extract with opened-date honored or unknown (never guessed); corpus
integrity green; offline scoring quoted.

## Slice 6 — SG-037: Daily Planning Agent on a button

**Outcome:** manual trigger reads catalog + confirmed label data and writes pending suggestions
(use-first, restock, days-math on confirmed labels); nothing executes; confirmation mandatory (Stage 0).
**Files:** create `backend/app/services/planning/` (agent logic on the provider seam) and
`backend/app/api/v1/planning.py` (trigger + list/confirm/dismiss wired to SG-035 records); create the
planning-suggestions screen (new route + component under `frontend/src/routes/`,
`frontend/src/components/`); consent + ledger wiring per the reader pattern; tests offline on the
scripted provider (zero network) + ONE metered live run under a stated ceiling with cost quoted.
**Out of scope:** scheduling, web enrichment, dosage guardrails beyond Stage 0 (none — F4).
**Tests:** suggestions link backing label data; unconfirmed suggestions change nothing; refusal paths
(no consent → no calls); frontend tests; `npm run build` green.

## Slice 7 — SG-038: category chat (Food, then Medicine)

**Outcome:** one conversational screen per category, scoped to its data, grounded in catalog entries +
sources; chat corrections flow into the guardrail log; suggestions only, never autonomous actions.
**Files:** create `backend/app/services/chat/` and `backend/app/api/v1/chat.py`; create the chat screen
(route + component); grounding tests offline scripted + ONE metered live run under a stated ceiling.
**Out of scope:** cross-category chat, web lookup, planning changes.
**Tests:** out-of-category questions refused or redirected; answers cite backing records; untrusted
chat input never becomes instruction (per §12 posture, negative tests); frontend tests; build green.

## Slice 8 — SG-039: Phase 3 exit E2E + runbook + close-out

**Outcome:** blueprint:531 proved in one fixture; docs match the tree; stage closes cleanly.
**Files:** create `backend/tests/test_phase3_e2e.py` (usability acceptance on the HTTP path: split,
manual entry, correction chain; planning button → pending suggestion → confirm; chat grounded answer;
guardrail log rows; default-off unchanged); extend `README.md` (Phase 3 runbook) and `backend/eval/`
guard (Cosmetics included, frozen prompts named); explicit non-goals ledger for the next door.
**Also:** full suite + ruff + mypy quoted; stage spend tallied from the ledger.
**Close-out:** stage exit verdict against the exit condition above; L3 ends; the next proposal goes to
the owner — never auto-chained.

## Slice order and IDs

SG-031 → SG-033 → SG-034 → SG-035 → SG-036 → SG-037 → SG-038 → **SG-040** → SG-039. Eight slices as approved (D45), plus **SG-040** added by owner decision `D47` (2026-09-14): opened-date persistence, closing SG-037 finding `F-SG037-3` — the exit bar "Cosmetics tracked with opened-date" was otherwise unmet. SG-040 runs BEFORE the exit; SG-039 stays last. Each slice is one dispatch. Reordering past a hard stop is forbidden. SG-035 (migration) and SG-037/038 (first metered
runs) carry their bounds in-packet; a metered run fires only under its stated ceiling with consent on.

## Owner forks (answered before they bind — none auto-decided)

- **F1 — L3 grant for this arc**, bounds as tabled: opencode, effort medium default, one retry per
slice fixing the root cause, hard stops: BLOCKED/STOP, score <95, any new provider/privacy/money
fork, any declared-sensitive-surface touch beyond the packet's stated migration/ledger scope.
- **F2 — spend posture:** unchanged (uncapped, re-evaluation owed) — confirm, not re-decide; each
metered slice still states its ceiling in-packet and quotes cost.
- **F3 — effort:** medium default for all eight slices (proven 96–98 across Phase 2) — confirm.
- **F4 — SG-031 packet:** does not exist yet (queued only) — first packet written after the grant.
