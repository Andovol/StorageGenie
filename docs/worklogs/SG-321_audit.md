# SG-321 audit — SG-304's screenshots found the duplicate card unreachable; the same-name warning works but its dark buttons fail contrast

**Score 85/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (report, process arguments). Ran 1167 s by the engine (1037 s by its stamps). **Its push was refused because the Architect pushed D36 mid-run** (my fault, not the coder's); the report and shots were rescued by SG-322 (`83a5eb5`). Own verdict `FAIL — A3`, which is correct.

## Holds — I opened every shot

| Shot | What I saw | Agrees with its DOM read |
|---|---|---|
| 01 warning, one match (light) | *You already have **Rice** (use by 12 Aug 2030).* with *Add another pack*, *Open it*, *Cancel* | yes |
| 02 warning, two matches (dark) | both *Olive Oil* packs listed with dates and an *Open it* each; **the *Add another pack* and *Cancel* buttons are near-white with pale pink text and look disabled** | yes (`rgb(213,156,154)` on `rgb(239,239,239)`) |
| 03 / 04 duplicate card | *In your catalog* — the card is absent | yes — the product bug (I6), fixed by SG-322 |
| 05 three olive oils | still six items, two *Olive Oil*; the click found no button | yes, a consequence of I6 |

## Findings

**I6 (the slice's real value): the F10 card was unreachable in the real app.** Found by driving the app, diagnosed to `committed_asset_id`. Fixed by SG-322.

**I9. The warning's buttons are unstyled browser defaults** (`rgb(239,239,239)` is Chrome's default button grey). In dark mode their contrast is **2.02:1** (I computed it with the WCAG formula from the quoted colours; the floor for 13 px text is 4.5:1). In light mode it is 8.59:1 but they still look like default form controls next to the maroon *Create asset*. **Disposition: polish P10 — give the warning's and the duplicate card's choices the theme's control style, light and dark.**

**I10. Developer words on the capture form**, seen in shots 01/02: the heading *Capture — Manual Create*, *Kind of item: unknown*, the button *Create asset*, and the 11 px hint *Left blank, we use the photo's filename* (under the 13 px floor). **Disposition: polish P11.**

**I11. A design note that contradicts its own image (model issue, Muse):** for shot 04 it says the phone header *"wrapped to two rows (`Menu` under logo)"*; the image shows one row (*StorageGenie · Menu · theme · upload*). The same weakness was seen in SG-273 (a claim not checked against its own evidence), now a third time.

**I12. Required reads missing:** the per-button contrast ratios the packet asked for are written as *"computed in driver per-button below"* and never appear, and the shot-02 *body* ratio pairs a dark-mode text colour with the light paper. Shot 05's search did not narrow the list (the driver's input never reached React).

## Rating below 95 — what went wrong (`RATING_ISSUE.md`)

- **Failure class:** model execution (I11, I12) and protocol (the refused push, mine).
- **Root cause:** Muse writes design notes from memory of the DOM rather than from the image; it skipped a required read without saying so.
- **Correction and recurrence guard:** the retake packet (SG-321r1) asks for each button's contrast **as a number per button, or the shot fails**, and says that any layout claim (wrap, crowding) quotes the element's measured `getBoundingClientRect` **and** names what the image shows. The Architect never pushes while a dispatch is in flight (STATE).
- **Owner impact:** 1167 s; cost `unavailable`.

## Rating

85 — the run found a real product bug that green tests had passed. Deducted for a false layout claim, missing per-button reads, and a non-working search step. slowest_waste: none.
