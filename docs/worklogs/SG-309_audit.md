# SG-309 audit — the Pantry refresh fix is live (`release-sg309`)

**Score 96/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high` (trigger). Report `9892efb`; receipt `result=done`. **Elapsed 170 s** against ≈150 s. Read: report sections State, G2, notes; runtime diff; both census files.

## Checked independently

- **Census:** `diff SG-309_census_before.txt SG-309_census_after.txt` → identical.
- **Runtime diff:** only `static/index.html` and the JS bundle (`index-gWdOr0um.js` → `index-BL66eLr6.js`); no backend file, as derived.
- **State:** S1, container `0b4742d3…` → `d01a2493…`, image `62e61689…` tagged `release-sg309`, restart 0, healthy ≈10 s.

## What holds

Every step of the way back proven; logs read by named lines only (no household id in its output — the W10 guard worked); no `/tmp`; no unlisted command. **It corrected a wrong packet premise with source evidence:** I asked for `pantry-assets` to appear *"at least as many times"* in the served JS; the count fell from 4 to 2 because SG-308 moved three call sites into the helper, which the report explains from the source.

## Findings

I1. **Packet premise wrong** (the string-count rule). Packet; no harm, corrected by the Coder.

## Model note

Haiku's ninth rotated slice; second clean rider this session; the W10 log guard held.

`slowest_waste`: none.
