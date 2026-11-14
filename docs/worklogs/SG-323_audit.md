# SG-323 audit — SG-304 and SG-322 served live as `release-sg323`; expected runtime diff, census identical, S1 without rollback

**Score 94/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high`. Diff `fba17fb..1cf0299`: `docs/worklogs/SG-323*` only. Engine elapsed 167 s (expected ≈200 s).

## Holds — checked against the evidence files

- **Runtime diff:** the two backend app files, the two test files the image ships, the JS and `index.html`; CSS and both `.woff2` byte-identical. This matches the set derived from `git diff 7a24601..HEAD`. The 107 removed `.pyc` files are runtime cache, not source.
- **Served strings:** *You already have* 0 → 2, *It's another pack* 0 → 1, `Exact duplicate of asset` 1 → 0; `DECIDED_CANDIDATE_STATES` 0 → 3 in the served `candidates.py`.
- Census 29 tables identical; head unchanged; health and routes 200; startup log clean (named lines only); `release-sg323` created, no tag moved; contract line "none received".

## Findings

**I20.** The first G3 pass read from the old container id after the recreate, got errors, and was redone against the new one. Disclosed and discarded, not reported as a result. Deducted.

**W11** still holds: `.woff2` is served as `application/octet-stream` (backlog).

## Rating

94 — clean serve; one self-corrected step. slowest_waste: none.
