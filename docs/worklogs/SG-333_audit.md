# SG-333 audit — screenshots of the catalog redesign (Muse 1.3 Contributor, xhigh)

**Verdict: 90, no flag. Six shots, every DOM proof present; per-row 5/5/3/4/3/4 proven; two visible defects the report's design notes missed.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-333 exit=0 published_head=yes`; ≈970 s by its stamps (expected ≈700) | ok, slow (one failed shoot retaken) |
| Settings | receipt note: `model=opencode-go/muse-spark-1.3-contributor model_source=command effort=xhigh` | ok |
| Scope | `git show --stat cf3afd9b`: `SG-333_report.md` + `SG-333_shots/` (6 PNG + INDEX) only | ok |
| All six shots (opened by me) | titles, attention line, sort label, per-row tracks match the report | matches report |
| No provider | evidence upload of Pillow PNGs, no import path, `provider_call` 0 | ok |
| Honesty | first shoot (0 cards, connection refused) stated and retaken once, as the packet allows | good |

## Issues

| ID | Issue | Evidence | Status |
|---|---|---|---|
| I23 | **Date chip overflows its card at 4 per row on the phone:** *Past · 16 Nov* runs into Milk's column and touches *19 Nov* | image 04 and 06 (opened by me); `ProductCard.tsx:190,205` `whiteSpace: "nowrap"`; tile width 79.5 px (INDEX) | FIX QUEUED → SG-337 G4 |
| I24 | **Desktop: the grid sits inset from the title and toolbar** — title at x≈24, attention line and grid at x≈114 to ≈1166 | image 01 and 02 (opened by me); cause UNVERIFIED (a max-width wrapper) | FIX QUEUED → SG-337 G5 |
| I25 | Report's design notes said 4-per-row is "tight-but-readable" with every date one-line — true of the text, but missed the chip collision; and missed I24 | report §Design notes | profile (Muse: design notes vs. own image, 4th time) |
| I26 | Phone *Add item* is an upload icon with no label | image 03–06 | OPEN — owner call; noted for the trial |
| I27 | Photo tiles are solid scratch colours: the look with real photos is still unseen | report UNCLEAR | OPEN — first real look is the owner's shelf trial |
| I28 | Font load not proven (`document.fonts`), computed style only | report UNCLEAR | no action — same caveat as SG-326 |

Deduction: −5 for design notes that missed two defects visible in its own images (I25), −5 slow (≈970 s vs ≈700 s, a shoot run lost to a preview server that exited).

`slowest_waste`: first shoot run against a dead preview server (≈340 s).
