# SG-329 audit — deploy rider, Standard Grid default (Muse 1.3 Contributor, xhigh)

**Verdict: 95, no flag. `release-sg329` serves; state S1, no rollback.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-329 exit=0 published_head=yes`; 181 s (est. ≈200 s) | ok |
| Runtime diff | `SG-329_runtime_diff.txt`: 3 changed paths, all `static/` (JS renamed, `index.html`); no backend file; CSS and `.woff2` byte-identical | equals the derived set |
| Served = built | served JS `index-y4viF7r0.js f6f6a12e…` equals a local `vite build` of `HEAD` with the Dockerfile's `VITE_API_BASE` | ok |
| Ids | container `9c7f8b81` → `3527c078`, image `0cf8bdc1` → `409bf8a1`, restart count 0, healthy in 13 s | ok |
| Census | 29 tables identical | ok |

## Issues

| ID | Issue | Status |
|---|---|---|
| I19 | Report's first line names the model "per AGENTS.md model policy" instead of `unknown` when the process arguments were unreadable (`PB-4` asks for `unknown`). The source is stated, so it is not passed off as observed, and the envelope confirms Muse | OPEN, minor — coder; noted in the profile |

**Limit:** evidence is the Coder's; this session reaches the host only through the dispatch verb.

`slowest_waste`: none.
