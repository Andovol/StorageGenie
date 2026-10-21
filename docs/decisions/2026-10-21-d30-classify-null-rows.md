# D-30 — DECIDED: classify the 5 stale null-cost rows (cost NULL → 0.0, per-row evidence) — 2026-10-21

**Owner message, byte-identical (2026-10-21, chat):**

> D30 - approved.

(Read as approval of the D-30 recommendation from the SG-223 audit turn: classify —
the rows are provably $0, fixing the accounting beats working around it. The other
two options, wider-grant and park, are not approved.)

## D-30 — DECIDED: classify, with per-row proof

- Exactly **5 `provider_call` rows**: the 2×404 + 2×429 pre-pilot rows and the SG-219
  CEAFĂ 400 row — each re-verified live before writing (error body carries no usage
  object, key spend unchanged across the call — quoted per row). UPDATE `cost`
  NULL → `0.0` on exactly those rows; error/state columns untouched.
- Expected effect: `scene_spend_so_far` unknown-cost 5 → 0; next-render projection
  ≈ `0.012437125 + 0 + 0.17028` ≈ 0.18 vs pilot-remainder cap — the wall clears
  without touching the guard formula.
- Slice: **SG-224** under project **L2** (one retry, root-cause only). Any row outside
  the 5 (different error, has usage, billed) STOPS the slice — classify nothing by
  assumption. No billed sends in this slice ($0).
- Afterwards: the Miso cutout probe re-dispatches first (the missing verdict), then
  the D-29 bulk run packets against real headroom.
