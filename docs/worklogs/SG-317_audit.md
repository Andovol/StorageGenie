# SG-317 audit — SG-307 served live as `release-sg317`; static-only diff, census identical, S1 without rollback

**Score 97/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high` (receipt note, `model_source=command`). Diff `b9b5f3e..884bf4d`: `docs/worklogs/SG-317*` only. Engine elapsed 123 s (expected ≈200 s).

## Holds — checked against the evidence files

- **Runtime diff** (`SG-317_runtime-diff.txt`): JS, CSS, `index.html` only; the removed JS `26ce556e…` is the one SG-314 added (chain consistent); both `.woff2` same sha256. Backend, alembic and dependency diffs empty.
- **Census** before and after: `diff` empty here.
- **Served strings** before → after: *Photo only* 0 → 1; `Source Only`, `Isolated Cutout`, `Bounding-box overlay omitted` 1 → 0; `.sg-paper-control` 0 → 1; the 480 px media rule quoted.
- Health ×6, routes 200, startup log clean by named lines, restart count 0, tag created, none moved.
- **Contract line:** *"none received"* — the SG-314 slip (I6) did not recur.

## Findings

I27. Effort still not visible in the process arguments (as SG-314, SG-315). Lane, minor — to the desk. No other finding.
