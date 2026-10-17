# D-15 — muse-image ONLY for now, via OpenRouter directly (Q2 pick) — 2026-10-17

**Owner message, byte-identical (2026-10-17, chat):**

> Q2 - use only muse-image for now. Muse-iamge should be available from OpenRouter directly, make sure you know how to call an Image API.

## D-15 — APPROVED: muse-image-only; Google leg parked, not retired

- The AI image stages (isolated cutout P1 + context scene T1b) narrow to **`meta/muse-image` via OpenRouter directly** — "for now" bounds the pick, it does not retire the Google leg. D-1009-10 (Google-only) is SUSPENDED while D-15 holds, not contradicted: no Google quota answer is owed anymore unless muse-image fails the probe.
- Relation to SG-159's measurement (`endpoints: []`, chat text-only): that reading was taken on the lane's Image-API path in October; the owner asserts direct OpenRouter availability. It is a new premise, not a contradiction — and it is verified by probe, never assumed: **SG-209 first re-runs discovery against OpenRouter directly** (`GET /api/v1/images/models` → `meta/muse-image` record → per-endpoint `supported_parameters` incl. `input_references`, plus pricing lines). If the slug is still absent, the probe REPORTS it — no substitution without a new pick (`PG-IC-03` stands).

## What the probe was briefed with (docs read 2026-10-17, OpenRouter current)

- Discovery: `GET https://openrouter.ai/api/v1/images/models` (Bearer) → per-model `/api/v1/images/models/{id}/endpoints` (definitive parameters, passthrough keys, per-endpoint `pricing[]` with `billable`/`unit`/`cost_usd`).
- Generation: `POST https://openrouter.ai/api/v1/images`, body `{model, prompt, ...}` (`resolution`/`aspect_ratio`/`quality`/`output_format`/`n`/`input_references[]` as data-URLs or URLs); buffered result at `data[0].b64_json` (+ `media_type`), cost at `usage.cost`; all-or-nothing billing (fail = not billed).
- Scene/cutout relevance: `input_references` carries the product photo for image-to-image; support and max count vary per endpoint — the probe confirms `input_references` in the muse-image record before any implementation slice depends on it.

## Still owed by the owner (D-14 carried, narrowed)

- (c) spend caps: per-render + monthly caps for live muse-image calls (real money; the probe slice itself needs a worst-case cap — proposed with SG-209, decided in chat). (a)/(b) are discharged by this pick: no Google quota work, no Muse transport question — OpenRouter direct IS the transport.
- No secret ever travels in chat, packets, logs or the repo (approved tooling only).

## Order

SG-206 (in flight) → SG-207 → SG-208 → **SG-209 muse-image probe** (packet drafted after SG-206 lands; needs the spend-cap approval). Implementation slices (cutout/scene) only after the probe proves slug + `input_references` + price.
