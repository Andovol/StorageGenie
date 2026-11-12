# SG-320 audit — SG-318 served live as `release-sg320`; JS-only diff, census identical, S1 without rollback

**Score 95/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (receipt note). Diff `7a24601..74aeb7c`: `docs/worklogs/SG-320*` only. Engine elapsed 200 s (expected ≈150 s).

## Holds — checked against the evidence files

- **Runtime diff:** the JS and `index.html` only; the removed JS `12083486…` is the one SG-317 added (chain consistent); CSS and both `.woff2` unchanged (SG-318 changed no CSS — consistent with its diff). Backend set empty.
- **Census** before and after: `diff` empty here.
- **Served strings:** the seven new wordings present (e.g. *Not started* 0 → 5); `Untitled asset` 1 → 0.
- Health ×6, routes 200, startup log clean, tag created, none moved; contract line "none received".

## Findings

I32. **`Thumbnail unavailable` 2 → 1, not 0:** one instance remains in the review card (`CandidateCard`), outside SG-318's scope. Reported as it is, not passed. **Disposition: the D35 polish slice.**
