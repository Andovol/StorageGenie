# SG-340 audit — screenshots of redesign C (Muse 1.3 Contributor, xhigh)

**Verdict: 94, no flag. Nine shots, first try, every DOM proof present; ≈550 s. The grouped cards and the item page hold; three design gaps its notes missed or underplayed.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-340 exit=0 published_head=yes` | ok |
| Scope | `git show --stat f48d1013`: report, INDEX, 9 PNG only | ok |
| All nine shots (opened by me) | 1 *Olive Oil* card *3 packs*; title, attention line and first card at x 24 (01, 03); past chip wraps inside its card at 4/row (02); item page rows in date order, *Add another pack* the one dark button (04–06); notice *Olive Oil used up · Undo*, rows 3→2 (08); History and More open (09) | matches report |
| Undo | report: rows 3→2→3, API read `status ACTIVE` for the restored pack | proved |
| No provider | stand-in PNGs via evidence upload, no import path | ok |

## Issues (design — for the post-trial polish slice, D39)

| ID | Issue | Evidence | Status |
|---|---|---|---|
| I39 | A pack's *Edit* opens the old *Manual expiry entry* card — *Date confirmed*, a *Date type* menu, browser-order date `11/23/2026`, *Save date* 32 px and *Clear expiry date* 26 px, then an amount block reading *No count yet* with empty *Quantity* / *Unit* fields. Works, but heavy and unlike the mockup's quiet rows | image 07 (opened by me); report note 07 names the button heights only | OPEN → post-trial polish |
| I40 | *More about this item* repeats *Use it up* (Used up / Thrown away / Given away) for the opened pack beside each row's own *Used up*; *Evidence* uses the browser's raw *Choose Files* control; *Details* keeps *Source / State / Confidence / Evidence* columns (*Kept*, *—*) | image 09 (opened by me) | OPEN → post-trial polish |
| I41 | *Undo* in the notice reads as plain text, not a control (no underline or button look) | image 08 (opened by me) | OPEN → post-trial polish |
| I42 | *Food & beverages* under every card — the same words twelve times | image 01, 03 | OPEN → post-trial polish |
| I37 | Title says *13 things* while the grid shows 10 cards (counts packs) | image 01 | OPEN — owner sees it in the trial |
| I38 | At 1920 the tiles are ≈350 px — large and sparse, not broken | image 03; report note 03 | OPEN — owner call (6 per row exists) |

Deduction: −6 — the design notes call 07's editor and 09's More section fine apart from button heights; I39–I41 are plain in its own images.

`slowest_waste`: none.
