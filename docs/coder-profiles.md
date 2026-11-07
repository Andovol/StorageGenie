# Coder model profiles

Built from audits, one row per rated slice (owner, D25, 2026-11-07). Strengths and weaknesses are drawn from the rows below, never from one slice alone. Issues with a model are flagged to the owner and the Launcher desk in the report that finds them.

**Rotation pointer:** `STATE.md`.

## Rows

| Slice | Model, effort | Kind of work | Engine elapsed | Rating | Stop rules kept? | Defects the audit found | Attribution |
|---|---|---|---|---|---|---|---|
| SG-286 | haiku-5-5, high | ops, live host read-only | ~70 s | 96 | yes, first sign | none (packet rule wrong) | packet |
| SG-290 | muse-1.3, xhigh | ops, live host, one write attempted | ~100 s | 96 | yes; one allowed retry | none (route closed by daemon) | packet |
| SG-293 | haiku-5-5, high | ops, live host, exports | 162 s | 96 | yes, literally | none (packet rule too broad) | packet |

## Haiku 5.5 at `high` — profile

**Strengths so far (2 slices):** keeps a hard stop rule at the first sign; reports evidence and options without acting on them; respects a permission denial. **Weaknesses so far:** report gaps (an output cut; phase timings not captured). Applies hard rules literally, which is right for stop rules but means the packet must be exact.

## Muse 1.3 Contributor at `xhigh` — profile

Earlier slices (before D25) are in `docs/ratings.md`; recent ratings: SG-279 90, SG-281 97, SG-280 96. **Strengths so far (1 rotated slice):** keeps stop rules; uses exactly the allowed retry; substitutes a "nothing changed" proof when a step no longer applies, and says so. **Weaknesses so far:** none attributable.
