# SG-327 audit — deploy rider, polish A and B (Muse 1.3 Contributor, xhigh)

**Verdict: 96, no flag. `release-sg327` serves; state S1, no rollback.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-327 exit=0 published_head=yes`; 152 s engine (est. ≈200 s) | ok |
| Scope | `git diff --stat 19469ad e039b9a`: `docs/worklogs/SG-327*` only | ok |
| Runtime diff | `SG-327_runtime_diff.txt`: JS renamed + `index.html` changed; CSS and both `.woff2` UNCHANGED; `backend_like_changed=0`; derived backend, dependency, alembic sets empty | equals the derived set |
| Served strings | `SG-327_strings.txt`: 9 new strings present (6 from 0, 3 rose), 7 old strings 1 → 0 | ok |
| Ids | container `a92d27bb` → `9c7f8b81`, image `e2703987` → `0cf8bdc1`, restart count 0, healthy in 15 s | ok |
| Census | 29 tables identical; `reminder` 4 → 4 | ok |
| Tags | `release-sg327` created on the new image; none removed or moved | ok |

**Limit:** the evidence is the Coder's; this session cannot reach the host except through the dispatch verb. The served strings, ids and census come from its report and evidence files, which agree with each other and with the derived change set.

## Issues

| ID | Issue | Status |
|---|---|---|
| I15 | Packet said all nine new strings would be 0 before; three already existed (*Use by*, *Add an item*, *No photo yet*) — packet premise wrong, the Coder reported it rather than bending | RESOLVED — packet error (mine), no effect |
| W11 | `woff2` served as `application/octet-stream` | OPEN, backlog |

`slowest_waste`: none.
