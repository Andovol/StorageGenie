# D-18(b) — AI transport pick: retry `google/gemini-3.1-flash-image` — 2026-10-17

**Owner message, byte-identical (2026-10-17, chat):**

> D18 - b - lets try it again. (Gemini 3.1 Flash Image)

## D-18 — DECIDED: option (b), retry the Google image leg

- Pick: **`google/gemini-3.1-flash-image`** via OpenRouter direct (Image API primary; the SG-159 server-tool chat path stands as measured: 200 without artifact).
- Effect on prior holds: the D-15 Google suspension is LIFTED for this slug only. D-15's muse verdict stands (refuted, not revived). "Try it again" is read exactly as stated: the October 429/quota wall may or may not still hold — the probe measures which, it does not assume the fix.
- Spend authority: D-20 ($2.00/day total live-AI cap) covers this probe — worst-case projection must fit inside it, fail-closed. No new cap decision needed for the probe; implementation spend still needs no separate word beyond the daily cap (monthly undeclared, not required for a capped probe).
- Slice: **SG-213 Google re-probe** (packet drafted with this decision; dispatched after SG-212 under L3). Success = a billed render returning image bytes end to end (plus an `input_references` render proving the cutout/scene path). Any 429/quota or artifact-less 200 STOPS with bodies committed — a second wall is evidence, not failure.

## What "try again" settles (the probe's three questions)

1. Discovery: is the slug listed with non-empty endpoints + declared `input_references` + pricing lines (SG-209's controls say 3 endpoints, 0..14 references, ~6e-05 token pricing — re-measure, never inherit)?
2. Quota: does a minimal billed render return 200 with image bytes, or the SG-159 429 again (quoted body either way)?
3. Reference path: does an `input_references` render return image bytes (the cutout/scene precondition)?
