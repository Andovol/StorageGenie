# SG-208 audit — D-13: household switching UI removed (9 affordances), rated 98

Immutable audit: base `31982f8` → work `e81147f` (19 product files, +83/−362) → evidence `f71df61` (12 files) → report `aa737b0` → receipt `264d30a`. Local `--ff-only` to the exact tip (`264d30a` == origin/automation at pull); tree clean. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-208 | Report: docs/worklogs/SG-208_report.md | Work-HEAD: f71df61...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Eleventh ISS-4 instance.** No re-trigger; no debug slice (the retry itself followed the earlier `--debug`).

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Product diff** (`31982f8..f71df61 -- frontend/`, 19 files): all 9 switching affordances gone (nav, CatalogToolbar, Chat, Planning, Inbox, Capture, Analytics inline, Expiry inline, Settings clear) + shared `HouseholdSelector.tsx` + its test deleted + context setter retired + prop threading removed (AppShell, CatalogPage) + asserting tests updated. Zero backend/api/seed/migration/config bytes; `frontend/dist/` gitignored transient. Exactly the D-13 scope (UI only).
- **Counts reconcile:** deleted `HouseholdSelector.test.tsx` held 4 tests (re-counted here) + 1 retired nav row = the 30/298 → 29/293 delta. Candidate suite `29 passed (29) / 293 passed (293)`, rc=0 (`SG-208_suite.log`).
- **FAIL-then-PASS (both committed, `SG-208_verify.log`):** fail-half = 5 candidate test files vs base tree in a throwaway worktree → 5 files / 10 tests failed, 58 passed, rc=1, every failure an absence row (quoted names + one body); pass-half = the 29/293 above. `PG-EV-09` holds. `useMemo`-class check N/A here; no dead-export silence — the setter retirement is reported either-way per packet.
- **Grep gates (`SG-208_scope.txt`, committed):** `aria-label="Household"` / `onHouseholdChange` / `setHouseholdId` / `HouseholdSelector` / copy variants — every gate rc=1 EMPTY; justified remainder named (kept resolution rail `HouseholdContext.tsx:34`; fixture line; `removeItem` rc=1 — Settings clear was its only caller). File-list: all staged paths under `frontend/src/`.
- **Served smoke:** `/` and `/inbox` on loopback candidate + real API — all gates true both routes (0 household selects, combobox scans live on remaining selects, 7 cards, scoped reads 11/11 and 2/2 × 200, served bytes == rebuilt dist 3/3). Both screenshots opened by this audit (D425): Catalog nav carries no household control (theme toggle + Import Asset only), toolbar intact with no gap; Inbox header bare with jobs + review queue; masking holds; no clipping/overlap/data anomaly. Light theme both — acceptable (deletion is theme-independent).
- **Contract:** 0.50.0 echoed with live proof. Health identical (3 reads). Elapsed 363 s vs ≈500 s (under, stated). No command over 60 s.
- **Reuse provenance ( Retry path):** candidate 19/19 reused from the preserved local ref via `cherry-pick -n`, byte-identical to the preserved commit; driver byte-identical (sha match); residue reconciled by hash reproduction (own build 3/3 hashes == debris bytes); debris shots cross-checked (inbox byte-identical, catalog 6-byte PNG noise, disclosed). REDONE: suite, build, smokes, fail-half, logs — correctly, since the dead run preserved none of those.

## The one packet-side finding (mine): quarantine refs are NOT on origin

The amended packet said "fetchable origin refs" — `ls-remote` carries no `refs/quarantine/*` (rc=128 both); the refs were lane-local. The Coder verified content independently (build reproduction + suite + greps) instead of trusting provenance, exactly per `PB-1`. Outcome unaffected. Recorded, attribution `packet`.

## Rating

**Holistic: 98/100, no flag.** Nine-affordance enumeration (7 beyond the packet's two) with both-direction delta, fail-half + pass-half committed, served proof on two routes with opened screenshots, exemplary disclosure throughout. `deduction_attribution`: packet (quarantine-refs premise). `slowest_waste`: `none`. Guards: PG-EV-02/03/05/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-01/03/04.

## Dispositions

| Item | Destination |
|---|---|
| D-13 UI removal complete in tree | Serve rider after SG-209 (live!=tree now SG-207+SG-208) |
| Server-side multi-household paths (`POST/PATCH /v1/households`, list-all) | **NEW decision for the owner** (D-13 scoped UI only): enforce single-household server-side, or leave the API as-is — added to the outstanding list |
| Runner `report_unreadable`, **11th instance** | Desk #84 (no re-trigger) |
| SG-209 (D-17, $2.00 cap) | **Dispatched this turn after push** (L3 flow) |
| npx absent from lane PATH (rc=127, 2nd slice) | Lane shape, no denial; recorded for provisioning awareness |

Harness context-size reading unavailable; no conclusion made.
