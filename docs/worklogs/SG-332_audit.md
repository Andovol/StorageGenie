# SG-332 audit — deploy rider, catalog redesign (Muse 1.3 Contributor, xhigh)

**Verdict: 95, no flag. `release-sg332` serves; state S1, no rollback.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-332 exit=0 published_head=yes`; 233 s (est. ≈200 s) | ok |
| Runtime diff | `SG-332_runtime_diff.txt`: 5 static paths (JS and CSS renamed, `index.html`); no backend file; both `.woff2` identical | equals the derived set |
| Served = built | report `:68`: served JS `11e4ee1b…` and CSS `d0a1bbde…` equal a local `vite build` of `HEAD` | ok |
| Strings | `SG-332_strings.txt`: 7 new labels present; *Processing Status*, *Recently Added* 0 after; Midnight ground in CSS 0 → 3, old paper 2 → 0 | ok |
| Census | 29 tables identical | ok |

## Issues

| ID | Issue | Status |
|---|---|---|
| I22 | *Import Asset* 4 → 2 in the JS, not 0: the non-catalog nav in `frontend/src/App.tsx:156`, `:176` still says it. My packet assumed 0 (SG-330's scope was the catalog header only) | OPEN — packet premise (mine); small slice next session |
| I19 | Model named from `AGENTS.md` rather than `unknown` (`PB-4`), source stated — second time (SG-329) | OPEN, minor — coder |

**Limit:** evidence is the Coder's; this session reaches the host only through the dispatch verb.

`slowest_waste`: none.
