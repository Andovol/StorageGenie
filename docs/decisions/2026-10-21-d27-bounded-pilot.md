# D-27 — DECIDED: bounded pilot for cutout/scene, ≤10 renders — 2026-10-21

**Owner message, byte-identical (2026-10-21, chat):**

> D3 - approved.

(Read as the answer to the standing D-3/D-27 choice from the SG-216 audit turn: the bounded-pilot recommendation accepted whole. The turn-local label "D3" maps to the durable ID D-27 per `G-P4` — no ID is reused. The recommendation's "e.g. ≤10 renders" is pinned here as the bound: **at most ten billed image renders under this authority.**)

## D-27 — DECIDED: bounded pilot, ≤10 billed renders

- Authority covers at most **10 billed image renders** total (BYOK upstream ~$0.0459/render measured SG-216 → worst-case pilot exposure ≈ $0.46 upstream, $0 OpenRouter credits). D-20 ($2.00/day) and D-14 ($10.00/month) continue to bind every billed leg fail-closed alongside this bound — the tightest of the three stops the slice.
- Scope: prove the cutout/scene path end to end (isolated cutout P1 + context scene T1b shape per the parked backlog row) inside the pilot bound. Implementation slices carry their own packets; each counts its renders against the 10.
- Exhausting the 10 without a finished path returns to the owner — never an 11th render on this authority.
- Slice: **SG-217** first under project **L2** (one retry, root-cause only). Coder/model/effort ride the dispatch envelope, never the packet (D302).
