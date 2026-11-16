# SG-324r1 audit — polish A gate (Muse 1.3 Contributor, xhigh, `--quarantine`)

**Verdict: 96, no flag. Polish A (SG-324, `33cd2dc..d45aaf4`) is gated green and may ship in the next rider.**

| Item | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-324r1 exit=0 published_head=yes`; SG-324 scratch moved to `refs/quarantine/SG-324-20261116T165907Z` | ok |
| Provider | OpenCode Go answered (2026-11-16); the 2026-11-14 quota kill has cleared | ok |
| Scope | `git diff --stat 78cf9dc d0812ce`: 5 frontend test files + `docs/worklogs/SG-324r1_*` only; no product, backend, migration or dependency file | ok |
| Gate | report: eslint 1 known error (parked) · tsc 0 · build RC 0 · backend 817 passed · frontend 67 files / 510 tests green after fixes · named 19 files twice green | ok (counts from the report; not re-run here) |
| Test fixes | read every changed line: each swaps old SG-324-replaced wording for the new (Actions → More actions, Re-isolate → Cut out the item again, Skipped (AI off) → photo reading is off, Import job → `Import ·`, 7 → 6 columns, empty countdown region) | faithful |
| Old wording gone | `grep` for `Untitled item|Thumbnail unavailable|Re-isolate Asset|Generate Context Scene` over `frontend/src` minus tests: no hits; control `grep "Unnamed item"` hits 5 product files, so the search can match | ok |

## Issues

| ID | Issue | Status |
|---|---|---|
| I3 | SG-324 (Muse) left 8 older tests asserting the wording it replaced; its own gate never ran (provider kill), r1 caught and aligned them | RESOLVED (r1 fix commits `1c5f48e..950c64a`) |
| I4 | P3 hides every `Replaced` (superseded) value from the Details table, even one holding a real older value; History lists audit events, not old values — an older value is not visible anywhere on the page | OPEN — intended by the polish A packet ("current record only"); owner may want old values in History later |
| I5 | Fix in `catalog.test.tsx` "absent specs" adds a tautological line (asserts the fixture's own metadata is null) | OPEN, minor — harmless; the two `queryByText` lines carry the check |
| I6 | Report says model/effort "not visible"; honest (`unknown` rather than a guess). Envelope: Muse xhigh | no action |

`slowest_waste`: none — every phase's output was used in this audit.
