# SG-319 audit — SG-318's six screenshots; every W-fix holds on screen; a list of remaining rough edges

**Score 88/100; no flag. SG-318's deploy is released to its rider (SG-320).** Model `opencode-go/claude-haiku-5-5`, effort `high` (receipt note). Diff `e16fbaa..91efe72`: 6 PNGs, `docs/worklogs/SG-318_shots/INDEX.md`, the report. Elapsed 587 s. Its own verdict is `FAIL — A3` for DOM reads it could not make (contrast and heading font where a page has no `h1`, one font size) — honest, and none hides a defect. **I opened all six shots myself.**

## Holds — image and DOM read agree

| Shot | What I saw |
|---|---|
| 01 Catalog (light) | chips *Food & beverages*, *Non-perishable*; *Unnamed item*; no raw keys — **taken in the table view, not the grid the packet asked for** (the grid's chip is SG-318's same `labelAssetType` change) |
| 02 Asset Juice (light) | Details: *Kind of item*, *Expiry date 7 Nov 2026*, *Status Live*, *Unit ml*; History *Added — Today, 19:57*; no `[object Object]`, no ISO |
| 03 Asset Ketchup (dark) | *No evidence attached*; Details plain |
| 04 Panel, photo fails | *No photo yet.* in the photo box, no broken icon |
| 05 Expiry | *7 Nov 2026 · Expiry date*; pills only *Use first* / *Use soon*; Oats and Rice under *Safe* with no pill |
| 06 Inbox | *Checking your upload*, *Reading the photo*, *Making items*, *Saving: Not started* |

## Rough edges still on screen (my look plus the Coder's notes; none from SG-318)

| ID | Where | What |
|---|---|---|
| P1 | Asset page (light) | *Edit* and *Clear expiry date* still white on paper (inline `--card`, outside SG-307's rule) |
| P2 | Asset page | the native date field reads *11/07/2026* (US order) beside *7 Nov 2026* |
| P3 | Asset page | Details shows *Shelf life* = *Food & beverages* (repeats *Kind of item*) and keeps the *Replaced* row; *Amount 300* and *Unit ml* as two rows |
| P4 | Catalog table | header *DIMENSIONS/SPECS* (always —); row actions *…* with no label |
| P5 | Expiry | an *Opened countdown* block about cosmetics on a food page |
| P6 | Inbox | *6/8 complete* counts the two skipped steps; both jobs named *Import job*; *AI off* |
| P7 | Item panel | *Re-isolate Asset*, *Generate Context Scene* buttons in developer words |
| P8 | Catalog | the status column says *Photo only* for every item — true, but says nothing an owner needs |
| I29 | several | *Untitled item* literals and the backend's `noname` remain (not on these screens) |

## Findings

I30. Shot 01 used the table view, not the grid; not called out. Minor. **Coder.**
I31. Some DOM reads missing (contrast on pages without `h1`; one font size). Reported as FAIL, honestly. **Coder, minor.**

## Model note

Haiku: thorough notes that each name their read or image — none contradicted by its own shot (the SG-316 failure did not appear); one view swap unflagged.
