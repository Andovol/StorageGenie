# SG-328 audit — catalog opens in Standard Grid (Muse 1.3 Contributor, xhigh, MINOR tier)

**Verdict: 96, no flag.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-328 exit=0 published_head=yes`; 456 s (est. ≈450 s) | ok |
| Change | `CatalogPage.tsx`: `CATALOG_TABLE_FIT_MIN_PX`, `measureContentColumnWidth`, `resolveInitialDensity`, the mount `useLayoutEffect` and the ref removed; state still starts `"grid"` (read in diff) | ok |
| Tests | new `sg328-grid-default.sg328.test.tsx`; `sg325-p8` now reaches the table by clicking *Compact Table* and asserts *Standard Grid* pressed first — not loosened (read in diff); `catalog.test.tsx` width-rule tests updated | ok |
| Gate | report: frontend 73 files / 529 tests, backend 817, tsc 0 | ok (counts from the report) |

`slowest_waste`: none.
