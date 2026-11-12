# SG-310 audit — SG-301 is live (`release-sg310`); the font files are served as `application/octet-stream`, which the rider did not flag

**Score 90/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (trigger). Report `60fe632`; receipt `result=done`. **Elapsed 243 s** against ≈250 s. Read: report sections State, G1, G2, A1; census diff.

## Checked independently

- **Census:** `diff SG-310_census_before.txt SG-310_census_after.txt` → identical.
- **Runtime diff:** `static/` only — new JS, new CSS, the two `instrument-sans-*.woff2` (30092 B, 11144 B); no backend path.
- **State:** S1, container `d01a2493…` → `77bcbb51…`, image `969ce264…` tagged `release-sg310`, healthy ≈16 s, restart 0.

## Findings

I1. **G2 asked for the font file to return *"200 with a font content type"*; it returned `application/octet-stream`**, quoted in the report, yet A4 and the verdict say PASS. A criterion missed and not flagged. Coder. Product impact `UNVERIFIED — my inference`: current browsers generally load a same-origin `@font-face` woff2 whatever its type, and SG-311's scratch shots rendered the face, but the live app has not been looked at in a browser. **Destination: backlog W11** — register `font/woff2` in the backend's static serving (one backend line, its own small slice or the next backend slice); the owner's first look confirms the face meanwhile.

I2. `npm ci` was a cache hit (the SG-301r1 image build held the lockfile layer), so this rider did not itself fetch the package; it says so. Not a defect.

## Model note

Muse's ops record stays good (S1, every step proven, 243 s), but it passed a criterion its own evidence contradicted — the same pattern as SG-308's stop: correct work, a rule read loosely.
