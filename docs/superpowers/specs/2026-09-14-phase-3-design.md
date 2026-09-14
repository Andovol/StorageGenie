# Phase 3 design — usability first, then agents (A1)

**Date:** 2026-09-14 · **Status:** design approved section by section (S1/S2/S3); awaiting owner review of this file before the implementation plan.
**Sources:** blueprint `inception/generic_asset_catalog_expiry_tracker_blueprint.md` (Phase 3: §14 p. 524–531; exit:531; UX §11; guardrails §10; threats §12); Phase 2 close (`STATE.md`, SG-030 rated 98, `README.md` Phase 3 non-goals); decisions below with owner quotes.

## Settled decisions (provenance)

- `D44` (2026-09-14, owner quote "Of course P1. I want to run the Phase 3 in L3 mode, so lets plan it and after I approved you can take it forward in L3 mode."): P1 plan-first approved; L3 execution intent recorded, grant still owed after stage-plan approval.
- Scope (owner approved with recommendation): Phase 3 covers BOTH halves — usability screens + model-picker first, then blueprint agents.
- Web search (owner approved with recommendation): source-attribution fields now, live search later. Owner 2026-09-14 note: "we will need to enrich the products ingested with web based information too, that would be nice to have" — kept as a named later item, not in this stage's build list.
- Planning trigger (owner approved with recommendation): manual button first, automatic scheduling later.
- Stage shape A1 (owner approved with recommendation): usability block → agents block → exit proof; small independently shippable slices.
- S1, S2, S3 each approved in chat 2026-09-14.

## S1 — Usability block (approved)

Four screens, no new AI behavior, prompt v1 frozen:

1. **Model-picker (SG-031):** Settings gains a model choice limited to lane-tested models (per D42: settings-backed, tested-models-only). Switching models becomes configuration; backend `SG_MODEL_ID` already exists.
2. **Split for multi-item photos:** pipeline preserves multi-item candidates (SG-028); review cannot split them. New Review action: select candidates → split into separate asset drafts, each keeping its photo link and source record (blueprint §11.3 keyboard-centric review).
3. **Manual entry per field:** reviewer types each field by hand when the photo gives nothing, Unknown as an easy choice, never a guessed date (blueprint §11.3; §9.3). Puts a screen on the API manual-entry route SG-030 proved.
4. **On-screen corrections:** edit an accepted field on screen; old value kept superseded with history visible in asset detail (chain exists per SG-028/030; today API-only).

Out: new AI calls, prompt tuning, live search, scheduling.

## S2 — Data foundations (approved)

Additive only — no existing table changes meaning:

1. **Source-attribution fields:** per-field source link + retrieval date + supported field. Live search later becomes a fetcher, not a remodel.
2. **Cosmetics + opened-date:** third category (taxonomy entry, versioned prompt file, behavior profile) + opened-date field with unknown-valid discipline.
3. **Planning suggestion records:** suggestion linked to its backing label data; status pending/confirmed/dismissed; confirmation mandatory on health-adjacent proposals (blueprint §1.3, §10 Stage 0, F4).
4. **Guardrail log:** every suggestion + correction in one reviewable log — the Stage 1 evidence base (blueprint §10).

Out: fetching from the web, running agents, executing suggestions.

## S3 — Agents on trusted data + exit proof (approved)

Label/catalog data only; no web fetching:

1. **Daily planning on a button:** manual trigger reads catalog + confirmed label data, writes pending suggestions (use-first, restock, days-math on confirmed labels). Never executed; confirmation mandatory. Each run cost-ledgered, consent-gated; AI OFF by default stays.
2. **Category chat (Food, then Medicine):** one conversational screen per category, scoped to its data, grounded in catalog entries + sources. Chat corrections flow into the guardrail log. Suggestions only, never autonomous health actions.
3. **Exit proof:** proves blueprint:531 — planning works end to end, both chats answer grounded, guardrail log active. Same pattern as Phase 2 close: offline behavior proof (zero network) + one capped metered live run. Writes the Phase 3 runbook; extends the eval corpus to Cosmetics; new prompt files versioned and frozen.

Carried bounds: F1 GO provider; F2 uncapped with re-evaluation owed; Q2 key handling; L3 grant after stage-plan approval.

## Later, explicitly not this stage

Live web enrichment (wanted, nice-to-have — owner 2026-09-14); automatic planning schedule; second provider / multi-provider routing (blueprint Phase 4); categories beyond Cosmetics; prompt tuning of frozen files.

## Exit criteria (blueprint:531, restated)

Daily planning suggestions and category chat are functional; guardrail rollout tracking (§10) is active — plus this stage's own bar: usability block shippable on screen, Cosmetics tracked with opened-date.
