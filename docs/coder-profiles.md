# Coder model profiles

Built from audits, one row per rated slice (owner, D25, 2026-11-07). Strengths and weaknesses are drawn from the rows below, never from one slice alone. Issues with a model are flagged to the owner and the Launcher desk in the report that finds them.

**Rotation pointer:** `STATE.md`.

## Rows

| Slice | Model, effort | Kind of work | Engine elapsed | Rating | Stop rules kept? | Defects the audit found | Attribution |
|---|---|---|---|---|---|---|---|
| SG-286 | haiku-5-5, high | ops, live host read-only | ~70 s | 96 | yes, first sign | none (packet rule wrong) | packet |
| SG-290 | muse-1.3, xhigh | ops, live host, one write attempted | ~100 s | 96 | yes; one allowed retry | none (route closed by daemon) | packet |
| SG-293 | haiku-5-5, high | ops, live host, exports | 162 s | 96 | yes, literally | none (packet rule too broad) | packet |
| SG-294 | muse-1.3, xhigh | ops, live host, image created | ~355 s | 98 | yes | none | — |
| SG-295 | haiku-5-5, high | deploy rider, live migration | 382 s | 97 | yes, every state | none | packet (small) |
| SG-271 run 1 | muse-1.3, xhigh | build, backend + 4 screens | 2100 s (killed) | unrated, retried | **no** — passed the 1500 s publish point and started an optional goal | nothing pushed; work stranded on host | Coder (publish rule) and packet (slice too big, a droppable goal after the gate) |
| SG-271 run 2 | muse-1.3, xhigh | build, backend + 4 screens (retry) | ~420 s | 90 | yes, a 1300 s stop rule; but changed an out-of-scope eval file instead of stopping | cleared perishable dates hidden from Unresolved; new notes at 12 px | mixed |

## Haiku 5.5 at `high` — profile

**Strengths so far (3 slices):** carried a live migration through every recovery state exactly; keeps a hard stop rule at the first sign; reports evidence and options without acting on them; respects a permission denial. **Weaknesses so far:** report gaps (an output cut; phase timings not captured). Applies hard rules literally, which is right for stop rules but means the packet must be exact.

## Muse 1.3 Contributor at `xhigh` — profile

Earlier slices (before D25) are in `docs/ratings.md`; recent ratings: SG-279 90, SG-281 97, SG-280 96. **Strengths so far (2 rotated slices):** keeps stop rules; uses exactly the allowed retry; substitutes a "nothing changed" proof when a step no longer applies, and says so; executes a long multi-gate proof cleanly with counts at every gate. **Weaknesses so far:** SG-271 run 1 ran past a written publish point into an optional goal and lost the whole run (first stop-rule breach by either rotation model); run 2 drew a wrong inference from a fact it had found (a cleared date read as deliberate) and disclosed an out-of-scope edit instead of stopping. **Packets for Muse:** make time points stop rules, put no optional goal after the gate.
