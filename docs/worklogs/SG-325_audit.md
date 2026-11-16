# SG-325 audit — polish B (Muse 1.3 Contributor, xhigh)

**Verdict: 96, no flag. All five items done and gated green; screenshots (SG-326) next.**

| Item | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-325 exit=0 published_head=yes`; ~940 s by its stamps | ok |
| Scope | `git diff --stat 8938787 9ae4702`: frontend product + tests + `docs/worklogs/SG-325_*` only | ok |
| P9 | `CandidateCard.tsx`: *Save edits* wrapped in `{!isDuplicate && (` (read in diff) | ok |
| P8+P13 | `CatalogPage.tsx` joins `fetchExpiryStatus(household)` by asset id (read in diff); backend `plugins.py:69-100` `read_status` with no category calls `compute_status(category=None)` = whole household — the no-category premise holds | ok |
| P12 | heading *Check this item*, labels via `plainFieldLabel`, `type="date"` on use-by inputs, *What we read* / *Photo* (read in diff) | ok |
| Gate | report: frontend 72 files / 526 tests, backend 817, tsc 0, build RC 0, eslint known error only | ok (counts from the report; not re-run here) |

## Issues

| ID | Issue | Status |
|---|---|---|
| I8 | Review card still shows a raw status value (`ACTIVE`): `lib/labels.ts` has no label for it (Coder's UNCLEAR, checked by its grep) | OPEN — fold into the next polish touch; SG-326 reports each hit |
| I9 | A use-by input is now `type="date"`: a read value not in `YYYY-MM-DD` would show as an empty field (`UNVERIFIED — my inference`; the pipeline's candidate date format is not checked here) | OPEN — SG-326 reads the input's value on the real duplicate candidate |
| I10 | Muse added a dead-export cleanup in `ProductCard.tsx` (`0df07d6`) — inside the named file, harmless | no action |

`slowest_waste`: none — every phase's output was used.
