# SG-226 audit — bulk scenes: 4/4 RENDERED, linked, live; killed 1s over budget post-report, rated 98

Immutable audit: base `496221f` → G1 `daf5e9c` (driver + enumeration + whole-list bound, no send) → work `f20867f` (4 renders + reviews) → report `cb9734a` → killed (no receipt commit). Local `--ff-only` to the exact tip (`cb9734a` == origin/automation at pull); tree clean. Trigger `result=partial id=SG-226 exit=143 killed=term pushed=3 wip=none`. Status verb confirms the terminal partial line. Receipt note: ABSENT (mapped-fetch read-back `no note found` for the report commit); the lane's own partial-receipt note (`Partial-Receipt-ID: SG-226`, on an internal object) records `elapsed=2101s budget=2100s killed=term`. Per `DISPATCH.md` §2 the slice is NOT failed (failure needs receipt-absent on re-check — recorded here) but NOT receipted either: work outcome complete, publication partial. The exact timeout source is measured, not inferred: the unit outlived `RUN_BUDGET_S` by 1 second, after the report commit, before the receipt. No new timeout class; the Coder's ≈1181s in-slice clock excluded queue/setup overhead the budget counts.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **4/4 RENDERED, linked, live (every image opened by this audit):** Toothpaste (Colgate Total box, brand/name legible), UHT (Pilos Lapte carton), Milbona (Parmigiano pack), TRACHISAN (medicine box, main label legible) — each faithful at product/primary-label level with only small-microtext artifacts, matching the report's stated standard (calibrated to linked SG-220 Costiță-2). Sizes/shas match the committed files.
- **Enumeration exact:** 7 assets, 8 upload photos, 4 render / 4 skip with live reasons (2 linked, 1 policy-parked CEAFĂ, 1 pairing-defective PIKOK). No double render, no silent skip.
- **Money:** whole-list + per-leg triple-bound proofs pre-send; actuals credits `0.0`, upstream 0.068208/0.068277/0.068340/0.068250 — all under projection; day 0.614486/2.00, month 0.626923125/10.00. Pilot counting correctly untouched (D-29 bulk authority).
- **DB:** 4 Evidence + 4 ledger + 4 audit + 4 link rows, ids quoted; no UPDATE/DELETE; live asset routes return the renders with no restart (re-read committed).
- **Scope:** driver `backend/scripts/sg226_bulk_scene.py` + `docs/worklogs/SG-226_*` only; zero product/test bytes, no migration, no restart. Contract 0.50.0 live proof.
- **Secrets:** literal gate exit 1 EMPTY; live-value key gate `matching_bytes=0` (1439 + 23 files).
- **Deviations, none deducted:** health-start via container logs + end probe (no served-code change); first-container uid denial rerouted to the lane socket with zero writes; small-secondary-text artifacts recorded per render with crops.
- **My false alarm, owned:** during this audit I briefly read an old SG-223 receipt commit as a missing SG-226 commit and suspected a force-push. Reflog + rev-parse + chain check show only clean fast-forwards; branch integrity confirmed, nothing missing. The alarm cost one verification round, no action taken.

## Rating

**Holistic: 98/100, no flag.** Four green renders with per-render review-before-link, enumeration exact, money triple-bounded, books balanced — then killed 1s over budget after the report commit with zero work lost. The kill is environment (budget wall, not slice fault); the missing receipt is a transport artifact, recovered by SG-227. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used (the review/crop phase is what pushed elapsed past expectation — sizing lesson recorded below). Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| 4 faithful renders linked + live (no restart needed) | Done — owner-visible in the app now |
| Missing Dispatch-ID receipt (killed pre-publish) | SG-227 verify + publish the SG-226 note + transcript (recovery, authorized here) |
| Budget sizing lesson | Bulk slices must budget review/crop time, not just sends: SG-226's sends took ~35s, review took ~350s; size by total unit time with margin under RUN_BUDGET_S, or split the list |
| Small-microtext fidelity limit | Recorded per render — a future brief/resolution slice may improve it, never assumed |
| CEAFĂ parked / PIKOK canonical-photo / cutout bulk | Unchanged — each waits on its named decision, none touched here |
| Runner kill (not misfire) | Nothing filed — lane behavior, work preserved; ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
