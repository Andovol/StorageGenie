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
| SG-272 | muse-1.3, xhigh | build, lifecycle + 4 screens + quantities | ~1240 s (stopped by its rule) | 85 | **yes**, the 1300 s stop rule exactly | task list filtered after paging; a status literal | packet (scope vs budget) |
| SG-296 | haiku-5-5, high | deploy rider, code only (2 runs) | run 1 stopped in S0; run 2 ~150 s | 96 | yes, at the first sign (run 1) | contract version line not echoed | packet (run 1) |
| SG-297 | haiku-5-5, high | gate + small backend fix | ~406 s (trigger file) | 90 | yes, stopped on the two reds exactly as told | none in its own work; report had no timings (second time) | packet (stale oracle not named) |
| SG-298 run 1 | muse-1.3, xhigh | gate + small backend fix | ~85 s | unrated, retried | stopped, but on a fault of its own | **typed the socket path wrong, then reported it as the packet's exact value** | coder |
| SG-298 run 2 | muse-1.3, xhigh | gate + small backend fix (retry) | ~625 s | 92 | yes | none in the work; corrected a wrong packet premise with evidence | mixed |
| SG-299 | haiku-5-5, high | deploy rider, code only (2 runs) | run 1 ~110 s stopped in S0; run 2 128 s | 96 | yes, S0 on a file outside the list (run 1) | publish hashes not quoted | packet (run 1) |
| SG-273 | muse-1.3, xhigh | build, new screen + gate + screenshots | 1277 s (stamps) | 78 FLAG:TRUST | yes, 1300 s stop kept | **identical screenshot reported as showing an updated state**; scratch left on host; design faults | mixed |
| SG-300 | haiku-5-5, high | build, screen design fixes + gate + DOM-proven shots | ~964 s (trigger file) | 92 | yes, finished under the 1300 s stop | none of its own beyond a self-inflicted shell hang; found the live-port API default unasked | packet (dark contrast) |
| SG-302 | muse-1.3, xhigh | build, small screen fix + contrast table + DOM-proven shots | ~973 s (stamps) | 93 | yes, finished under the 1300 s stop | wrong version line echoed; a `/tmp` file left (self-reported); oversized FAIL log | packet (11 px label carried) |
| SG-303 | haiku-5-5, high | deploy rider, live serve | 128 s | 95 | yes, S1 | unlisted probe container (disclosed); two `/tmp` attempts (refused); over-broad log grep exposed a household id to its own output | packet (probe unnamed) |
| SG-308 | muse-1.3, xhigh | build, small behaviour fix + 5-path test + runtime DOM check | ~1450 s (stamps) | 84 | **no** — ran ≈150 s past the 1300 s hard stop, then published | model/effort inferred, not read; a covered screenshot | mixed (estimate ≈800 s too low) |
| SG-309 | haiku-5-5, high | deploy rider, live serve | 170 s | 96 | yes, S1 | none; corrected a wrong packet premise from source | packet (small) |
| SG-301 run 1 | muse-1.3, xhigh | build, font package + copy on 3 screens + shared header | ~933 s (stamps) | unrated, retried | **yes**, stopped before the 1100 s line and reported G4–G6 `REMAINING` honestly | 26 old tests left failing on the branch (named, not updated); FAIL-on-base not run | packet (scope vs a 1100 s stop) |
| SG-301r1 | muse-1.3, xhigh | retry: 26+11 old-test wording updates, FAIL on base, full gate | ~1031 s (stamps) | SG-301 rated 80 overall | yes — stopped before R3 rather than overrun; scratch removed before the report | said the 1200 s line was hit at ≈1031 s (it stopped early, mislabelled); found 11 reds run 1 missed | packet (shots did not fit) |
| SG-311 | haiku-5-5, high | screenshots only, DOM-proven, design notes | (see report) | 96 | yes | none; a failed retake kept and labelled | — |
| SG-310 | muse-1.3, xhigh | deploy rider, live serve | 243 s | 90 | yes, S1 | passed a criterion its own evidence contradicted (font content type) | coder |
| SG-312 | haiku-5-5, high | build, CSS and copy over 3 screens + gate | ~1223 s (stamps) | 82 | **no** — ≈120 s past 1100 s, from a 600 s hung foreground server start | no screenshots | mixed |
| SG-313 | muse-1.3, xhigh | screenshots only, DOM-proven, design notes | 640 s (stamps) | 92 | yes, wide margin | identity line inferred, not read; design notes missed ISO dates, a misleading status word, a tier/heading clash | coder |
| SG-314 | haiku-5-5, high | deploy rider, live serve | 159 s | 93 | yes, S1 | echoed the project file's version line as its own contract line | coder |
| SG-307 run 1 | muse-1.3, xhigh | build, catalog + item panel + shared controls + 375 header | ~1116 s (stamps) | unrated, retried | **no** — 16 s past 1100 s; skipped the full gate the packet said was never skipped | full gate not run; a `!important` band-aid where the packet kept the file out of scope; *Food Beverages* | mixed |
| SG-307r1 | muse-1.3, xhigh | retry: three fixes + full gate | 649 s (stamps) | rated with SG-307 after SG-315 | yes, wide margin | used `/tmp` once against the packet; build path landed under `frontend/` (cleaned, disclosed); reported the reds honestly, did not fix out of scope | coder (minor) |
| SG-315 | haiku-5-5, high | fix: one product line + 8 test assertions + full gate | 314 s (stamps) | 96 | yes, wide margin | none; said "not visible" for model and effort instead of inferring | — |
| SG-316 | muse-1.3, xhigh | screenshots only, 7 shots, DOM-proven, design notes | 1296 s (stamps) | 85 | **no** — ≈196 s past 1100 s in write-up | two design-note claims contradicted by its own shots; found `[object Object]` unasked | coder |
| SG-317 | haiku-5-5, high | deploy rider, live serve | 123 s | 97 | yes, S1 | none; contract line correctly "none received" | — |
| SG-318 | muse-1.3, xhigh | build, ten wording fixes over 9 files + full gate | ~1040 s (stamps) | 88 | yes, inside 1100 s | edited one product file outside the scope ceiling, disclosed instead of stopping | mixed |

## Haiku 5.5 at `high` — profile

**Strengths so far (7 slices):** the most careful screenshot evidence so far — DOM-confirmed proof per state, honest gaps, a live-port hazard found unasked (SG-300); stops in S0 rather than widen an expected list on its own authority (SG-299 run 1); records phase timings when the packet requires stamps (SG-299); a clean in-scope fix with FAIL-then-PASS and unasked base-run attribution of every red (SG-297); stopped at a denial in S0 without trying another route (SG-296 run 1); carried a live migration through every recovery state exactly; keeps a hard stop rule at the first sign; reports evidence and options without acting on them; respects a permission denial. **Weaknesses so far:** report gaps (an output cut; phase timings not captured, twice: SG-296, SG-297). Packets for Haiku require a `date +%s` stamp at each phase. Applies hard rules literally, which is right for stop rules but means the packet must be exact.

## Muse 1.3 Contributor at `xhigh` — profile

Earlier slices (before D25) are in `docs/ratings.md`; recent ratings: SG-279 90, SG-281 97, SG-280 96. **Strengths so far (4 rotated slices):** establishes each premise from code before changing it and corrects a wrong packet premise with evidence (SG-298 run 2); keeps stop rules; uses exactly the allowed retry; substitutes a "nothing changed" proof when a step no longer applies, and says so; executes a long multi-gate proof cleanly with counts at every gate. **Weaknesses so far:** SG-271 run 1 ran past a written publish point into an optional goal and lost the whole run (first stop-rule breach by either rotation model); run 2 drew a wrong inference from a fact it had found (a cleared date read as deliberate) and disclosed an out-of-scope edit instead of stopping; SG-298 run 1 hand-copied a path wrong and claimed it matched the packet; SG-273 reported a duplicate screenshot as showing a new state (**twice in one day: a report claim not checked against its own evidence**). **Packets for Muse:** make time points stop rules, put no optional goal after the gate, give every value it must set as a literal command block.
