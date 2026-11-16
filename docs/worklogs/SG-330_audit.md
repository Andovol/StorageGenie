# SG-330 audit — redesign A: Midnight, photo-first cards, per-row setting, header (Muse 1.3 Contributor, xhigh)

**Verdict: 95, no flag. All five items landed and gated (frontend 78 files / 544 tests).**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-330 exit=0 published_head=yes`; ≈1060 s by stamps, inside 1100 s | ok |
| Scope | `git diff --stat a436bef a158aad -- frontend`: tokens, catalog, header, `AppShell.tsx` (title + per-row props threaded through the shell that renders the toolbar — catalog wiring, accepted), `labels.ts`, tests | ok |
| Tokens | every moved token's role named in the report; contrast gate test `sg330-r1` reads the file | ok |
| Gaps | `ProductGrid.tsx:272` `gap: narrow ? "8px 16px" : "24px 40px"` — rows tighter than columns, the reverse of the mockup | packet ambiguity (mine: "40 × 24 px"); fixed in SG-331 T7 |

## Issues

| ID | Issue | Status |
|---|---|---|
| I20 | Grid row and column gaps swapped | FIX QUEUED (SG-331 T7) — packet error |
| I21 | Host backend suite reported as "passed" without its count (A4 asks exact counts) | OPEN, minor — coder; SG-331 A4 names it |

`slowest_waste`: none.
