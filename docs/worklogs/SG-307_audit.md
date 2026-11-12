# SG-307 audit — the catalog and item panel in the new look, over three runs (SG-307, SG-307r1, SG-315); gate green, screens not yet seen

**SG-307 overall 78/100; no flag. SG-315 96. Deploy waits for its screenshots (SG-316).** Diff `0dd3fa7..14c1f1f` (product: catalog, item panel, toolbar, import window, header, theme switch, Pantry buttons, `tokens.css`, `labels.ts`). Models: SG-307 and SG-307r1 `opencode-go/muse-spark-1.3-contributor` xhigh; SG-315 `opencode-go/claude-haiku-5-5` high (receipt notes, `model_source=command`).

## Holds — checked against the diffs and logs

- **Gate green at `14c1f1f`** (`SG-315_*.log`): frontend 54 files / 467 tests, 0 failed; host 805 + 2 deselected; image proof 2; eslint only the known `App.household-nav.test.tsx` error; `tsc` 0; build 0; changed files twice 91/91.
- **Catalog:** plain status words (*Photo only*, *Cut-out ready*, *Scene ready*, *Needs attention*), *2 min ago*, no monospace, square cards on paper, the 165 px grid, an *N ITEMS* header; the toolbar as joined square tabs.
- **Item panel:** tabs *Photo / Cut-out / In a scene*; one-line empty states; bounding-box and *If-Match* sentences gone; *Version* off the screen; categories in the taxonomy's words (*Food & beverages*).
- **Controls:** one shared paper control rule (`sg-paper-control`); Pantry buttons fixed at the source (`PantryPage.tsx` `ACTION_STYLE`), no `!important` band-aid left; the drop-zone highlight restored (SG-315).
- **375 header:** a media rule hides the *Import Asset* text and the count (icon keeps an `aria-label`) — proven by rule, **not yet by a render**.

## Findings (session IDs)

I10. **SG-307 run 1 skipped the full gate** the packet said was never skipped, and ran 16 s past the stop line. **Coder (Muse).** Fixed by SG-307r1 and SG-315.
I11. **An `!important` band-aid** on the Pantry buttons. **Packet** (I kept `PantryPage.tsx` out of scope while asking for the fix). Fixed in SG-307r1.
I16. **A lost feature:** SG-307 dropped the drop-zone highlight. **Coder.** Fixed in SG-315.
I17. **8 old styling tests left red,** unseen because run 1 re-ran only its own changed files. **Coder.** Fixed in SG-315 — each moved to the new look, none loosened (diff read).
I14. **Food items read *Uncategorized* in the item panel:** the panel shows `asset_type`, the food kind lives in the expiry classification. Needs a backend change. **OPEN — the owner's wording/trial will show whether it matters; backlog.**
I18. `/tmp/eslint_tail.txt` left on the host by SG-307r1. **OPEN — host cleanup.**

## Below 95

- **Failure class:** a design slice too large for one run, then a lost feature and hidden reds. **Root cause:** catalog + panel + shared controls + header in one build slice; run 1 checked only the tests it touched. **Guard:** a design slice reruns the full frontend suite, not only its own files — already in the gate; the stop-line order (*gate before polish*) must be kept.
- **Owner impact:** ≈2080 s over three runs and one extra slice; nothing live affected.

## Model note

Muse: the design work is broad and good; the stop-rule order was broken again (the gate skipped for polish — its SG-271 pattern). SG-307r1 was clean and honest. Haiku SG-315: fast, exact, every assertion moved rather than weakened.
