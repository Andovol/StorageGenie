# SG-316 audit — SG-307's seven screenshots; SG-307's change holds on screen; my look found five owner-visible defects, two of the model's claims were false

**Score 85/100; no flag. SG-307's deploy is released to its rider (SG-317).** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (read from process arguments). Diff `bcaa2fd..1f184dc`: 7 PNGs, `docs/worklogs/SG-307_shots/INDEX.md`, the report — nothing else. Elapsed 1296 s by stamps (expected ≈750 s): shots done at 1064 s, report written past the 1100 s line. **I opened all seven shots myself.**

## Holds — image and DOM read agree

| Shot | What I saw | DOM read |
|---|---|---|
| 01–02 Catalog light/dark | square paper cards, *Photo only*, *11 ITEMS*, joined square tabs | radius `0px` card/well/button; no `mono` |
| 03–04 Panel light/dark | tabs *Photo / Cut-out / In a scene*; *No cut-out yet.*; *Kind of item: Food & beverages* | five developer strings absent |
| 05 Pantry 375 | header on one row (icon-only import); paper tile buttons | `nav` 57 px, tops 12–16; buttons `rgb(244,240,232)` |
| 06 Inbox | paper *Review status* select | `rgb(244,240,232)` |
| 07 Asset dark | paper file input | bg `rgb(32,27,23)` |

## Findings (session IDs)

I19. **Catalog cards show raw category keys** (`food_beverages`, `documents_other`, `non_perishable`) on the most-used screen, while the toolbar and panel say *Food & beverages*. SG-307's own scope (enums through `labels.ts`). **Disposition: wording slice.**
I20. **Asset page Details table shows `[object Object]`** for *Shelf life* and both *Expiry date* rows, plus raw `food_beverages`, `ACTIVE`, `ml` and rows all named *Detail*; **History shows ISO timestamps** (`2026-11-12T19:06:54.601245`); *Thumbnail unavailable* at 11 px. Pre-existing, owner-visible. **Disposition: wording slice.**
I21. **Item panel shows a broken image** (alt text *Milk* and a broken-image icon) when the photo will not load, where the catalog and Pantry show a *No photo yet* placeholder. **Disposition: wording slice.**
I22. **Nameless items read two ways:** *noname* (a file name stem) and *Untitled asset*; Pantry says *Unnamed item*. **Disposition: wording slice (one word: *Unnamed item*).**
I23. **Panel shows the amount twice** (*Quantity 1000 / Unit ml* fields and *1000 ml left* below). Minor. **Disposition: wording slice notes; change only if trivial.**
I24. **Two design-note claims were false** — Milk's tile *"uses a different thumb path than the catalog card, which does show its color"*: the catalog's Milk card shows the same placeholder (last card, shot 01); *"the evidence file exists"* — stated without a check. **Coder: a report claim not checked against its own evidence (third time: SG-273 twice). Disposition: profile; flag to owner and desk.**
I25. **Stop line passed by ≈196 s** during write-up after three shot attempts. **Coder. Disposition: profile.**
I26. Heading and body contrast not measured (button pair used as proxy, disclosed). Minor.

## Below 95

- **Failure class:** evidence complete; claims in notes not checked; stop line overrun. **Root cause:** three shot attempts ate the margin; notes written from belief. **Guard:** screen packets keep *"every sentence saying a shot shows names the DOM read"* — extend it to design notes.
- **Owner impact:** none on the live app; my own look caught I19–I22.

## Model note

Muse's seventh rotated slice: thorough DOM evidence and a good findings list (I20 is its find), but a false claim again and the stop line passed.
