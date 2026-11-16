# SG-331 audit — redesign B: plain toolbar, use-by sort, attention line, gaps (Muse 1.3 Contributor, xhigh)

**Verdict: 96, no flag. Seven items done; frontend 79 files / 554 tests, host 817 + 2 deselected, image proof 2.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-331 exit=0 published_head=yes`; ≈1060 s by stamps | ok |
| T7 gaps | `ProductGrid.tsx:273` `gap: narrow ? "16px 8px" : "40px 24px"` (read) | fixed (I20 RESOLVED) |
| T2 premise | packet said the sort might run before the use-by join; the Coder found it already runs after and reported it | premise falsified, honestly |
| T6 sources | past = `bucket === "expired"`, this week = `bucket === "this-week"`, counted from `ExpiryStatusResponse.rows` (`api/types.ts:389-406`) | ok |
| Backend count | `817 passed, 2 deselected` given this time (I21 not repeated) | ok |

`slowest_waste`: none.
