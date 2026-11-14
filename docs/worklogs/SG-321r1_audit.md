# SG-321r1 audit — SG-304's screens hold on the fixed code; the duplicate card works; one false layout note repeated

**Score 88/100; no flag. SG-304 + SG-322 are released to their rider (SG-323).** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (report, process arguments). Diff `38d7586..923719d`: five PNGs, `docs/worklogs/SG-304_shots_r1/INDEX.md`, the report. Own verdict `PASS`.

## Holds — I opened every shot

| Shot | What I saw | Agrees with its DOM read |
|---|---|---|
| 01 warning, one match (light) | as SG-321: *You already have **Rice** (use by 12 Aug 2030).* | yes |
| 02 warning, two matches (dark) | both packs with dates; *Add another pack* / *Cancel* washed out | yes — 2.02:1 now written as a number |
| 03 duplicate card (light) | *This photo matches Olive Oil (use by 6 May 2030).*; maroon *It's another pack*, paper *It's the same pack*, *Decide later*; no *Accept* / *Hold*; *Save edits* at the bottom (G-1) | yes |
| 04 duplicate card (dark, 390) | same card; choices fit, *Decide later* on its own line; no sideways scroll | yes |
| 05 catalog searched *Olive Oil* | *Showing: 3 items*, three *Olive Oil* rows | yes — count 6 → 7 |

**The fix (SG-322) is proven on screen:** the three choices show for an open duplicate, and *It's another pack* makes a third pack without touching the other two.

## Findings

**I17. False layout note, again (model issue, Muse — for the owner and the desk):** the note for 04 says *"the header occupies two rows (wordmark above; `Menu`/theme/import below)"*. The image shows one row: *StorageGenie · Menu · theme · upload*. This is the same false claim as SG-321 (I11), **made despite this packet's explicit rule** that a layout claim must match the image. Fourth instance of the weakness (SG-273 ×2, SG-321, SG-321r1). It touches a note, not a proof; every proof I checked holds.

**I18. The review page is still developer-facing** (seen in 03 and 04): heading *Candidate 01a1dbaf-…* (a raw id), *State: proposed · Job: …*, *Candidate review*, *Possible duplicates or collisions*, raw field keys (`display_name`, `expiry_date`, `status` = `ACTIVE`), the date field shows **`2032-06-18`** (ISO, inside an input, so the `innerText` check could not see it), an evidence id under the photo, and *This match is advisory; review it before accepting.* although no *Accept* button shows. **Disposition: polish P12.**

**I19. Same-name packs cannot be told apart in the catalog** (05): the rows show no date, only *Added*. **Disposition: polish P13 — show each item's use-by date in the catalog row.**

## Rating

88 — every required read present, the search fixed, the bug's fix proven on screen. Deducted for repeating a false layout claim against an explicit rule. slowest_waste: none.
