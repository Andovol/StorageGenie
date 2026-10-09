# Context Scene — design (OpenRouter-routed image rendering)

Date: 2026-10-09 · Decisions: D4 (Q1–Q4) · D5 (P1 adapter) · D6 (T0+T1b) · D7 (pick, was parked) · D-1009-3 (resume) · D-1009-4 (six answers) · D-1009-5 (OpenRouter router)
Sources: OpenRouter docs fetched 2026-10-09 (`/docs/guides/features/server-tools/image-generation`, `/docs/guides/features/server-tools`, `/docs/cookbook/image-generation/preset-enhanced-images`) · prior art: Phase-4 provider seam (D83), Enrich proof discipline (SG-099→104), Jina cost pattern (SG-124/132)

## 1. Goal

Give the shell-only **Generate Context Scene** button (D64, `ItemInspectorDrawer.tsx`) a real backend: restage an asset's Evidence photo as a contextual scene image through OpenRouter, with provenance, ledgered spend, and review-gating. **This arc ends at the D7 model pick with render evidence — UI wiring is the next arc.** §1.4 non-goal is reopened for scene rendering only (D-1009-4).

Non-goals: cutout/isolation pipeline (separate DQ4 producer) · text-to-image from scratch (input is always the real asset photo) · auto-accepting renders (standing: proposed, never auto-accepts) · multi-render batches (T1b cap is 3, one per request).

## 2. Architecture — one OpenRouter client, model by name

Single integration: `POST https://openrouter.ai/api/v1/chat/completions` (OpenAI-compatible), one owner-placed `OPENROUTER_API_KEY` in env (lanes never mint credentials, Jina D109 precedent). No per-vendor clients — the D5 "adapter" is the router plus a frozen request envelope:

- **Orchestrator** (cheap vision-capable model; exact slug fixed in the T0 packet after the live catalogue read): receives the asset photo as message image content plus the frozen scene brief; rewrites into a detailed render prompt (subject preserved, shape/label/material pinned; scene, lighting, framing variable).
- **Tool** `openrouter:image_generation` with `tool_choice: "required"` (no model-decides vagueness — one call, one render) and `parameters: {model, quality, size, aspect_ratio, output_format}` frozen per run; image model is **config, never code**, so D7 swaps a name, not an architecture.
- **Budgets enforced on the request**: `max_tool_calls: 1` and `stop_server_tools_when` spend cap; arc cap ≤$1 total across T1b (D-1009-4).
- **Persistence**: returned `imageUrl` is temporary (per docs) — the slice downloads immediately and stores bytes as an Evidence row carrying provider=`openrouter`, image model, orchestrator, prompt, cost from the `usage` object, and timestamp (Q3 provenance as locked). Every billed call writes its ledger row even on empty/error content (SG-099 lesson, applied from the start).
- **Privacy**: key is name-only in reports (Jina precedent); prompts carry the asset photo — disclosed, consent-gated like synthesis.

## 3. T0 leg — read-only, $0

`GET /api/v1/models` filtered to image-output models: confirm both shortlist slugs exist and record their per-call prices (today's documented candidates: `openai/gpt-5-image*` family, `google/gemini-3.1-flash-image`; prices re-read live, never inherited from this doc). **T0 also verifies the load-bearing unknown**: whether the image tool accepts a source/reference image or is text-prompt-only — the orchestrator-sees-photo design holds either way, but the prompt template differs, so T1b waits on this answer. No render, no spend, no production write.

## 4. T1b leg — max 3 renders, ≤$1, consent-gated

Inputs: 2–3 existing asset Evidence photos (D-1009-4, real data). Runs: render 1 via the OpenAI-family shortlist slug, render 2 via the Google shortlist slug (same photo, same frozen brief — controlled comparison), render 3 confirming the winner on a second photo. Each run: consent check → one request (`max_tool_calls: 1`) → download → Evidence row + ledger row with ids quoted → judgment (faithfulness to asset vs scene quality, stated per render, no aggregate scores — D30). D7 pick lands on these three rows.

## 5. Errors — loud classes, no silent fallthrough

`{status: "error"}` maps to named refusals (auth / content-filter / timeout / empty-content / beta-shape-drift), each with its own refusal path and report line; a refused call never spends, a billed failure still ledgered. Server tools are **beta** (docs, 2026-10-09): the spec pins this date, and T0 re-verifies the envelope — shape drift is a finding, not a surprise.

## 6. Testing

Fail-pre→pass-post on the seam (frozen envelope byte-asserted, `tool_choice` required asserted, cap fields asserted); non-vacuous proofs (refusal paths tripped for real, one forced-error run); suite-green binds (M45); live legs quote row ids (SG-132 precedent). No production writes beyond the ledgered proof rows, left by design (PG-EV-06).

## 7. Exit

D7 model pick with three stored renders as evidence + this spec + T0/T1b receipts. UI wiring (button → endpoint → review surface) scopes as the next arc on owner word.
