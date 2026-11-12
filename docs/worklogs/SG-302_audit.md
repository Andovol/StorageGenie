# SG-302 audit — the Pantry's warning text now reads in dark (7.36:1); one design rule still broken: the EXPIRED label is 11 px

**Score 93/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (process args quoted in the report; receipt `result=done exit=0 published_head=yes`). Diff `cc1ec92..0645b25`: product `frontend/src/routes/PantryPage.tsx` (+11/−3) and a new test file; nothing else outside `docs/`. **Elapsed ≈973 s** by its stamps against ≈900 s expected and the 1300 s stop. Read: the whole report, `SG-302_contrast.md`, `INDEX.md`, the product diff, `proof_full.json` (label colours), gate log tails. **Opened all 7 shots myself.**

## Checked independently

- **Hashes:** `sha256sum SG-302_shots/*.png | cut -c1-12 | sort -u | wc -l` → 7 of 7 distinct.
- **Colours from the DOM** (`proof_full.json`): EXPIRED dark `rgb(213, 156, 154)` on `rgb(32, 27, 23)`; light `rgb(110, 48, 46)` — the base's light value.
- **Ratios recomputed:** link on dark paper 7.36; muted on light paper 5.32; ink on light paper 15.47 — all match the table.
- **Gate:** backend log `2 passed, 6 deselected` (image proof) after the host suite; frontend `44 passed (44)`, `396 passed (396)`.
- **Scope:** `git diff --stat cc1ec92..0645b25 -- ':!docs'` → the two frontend files only.

## What holds

- **G1.1:** both `--primary` text uses found by grep and switched to `--link`; dark 7.36:1, light unchanged by token equality and by DOM read.
- **It corrected the audit's premise:** the text sits on dark `--paper` `rgb(32,27,23)`, not the body `rgb(15,14,13)` that SG-300's audit measured against — established from the DOM, not assumed.
- **G1.2:** *Capture* is a real link, underlined, focus ring, visible in both empty shots.
- **G1.3:** 16 pairs plus one honestly `REMAINING` (the tile error text, never rendered).
- **Shots, by eye:** dark Use soon at 1280 and 375 — EXPIRED and *Expired 3 days ago* clearly readable in rose; light 375 unchanged from SG-300; the notice *"Juice used up · Put back"*; both empty states; the catalog's Gone view (*Old Soup*, *Juice*, *Gone — used up*, *Put back*). Each shows what `INDEX.md` says it shows.
- **Stop rules:** kills by PID only, no `pkill -f`; scratch removed by exact path; `VITE_API_BASE` set and the bundle checked for `18302` and no `8003`.

## Findings

I1. **The EXPIRED label is 11 px** (`PantryPage.tsx` ~`:196`, `fontSize: 11`; the contrast table's row says *"normal 11px bold"*). D18 says *no text under 13 px*. Introduced by SG-300 (its packet asked for *"a small uppercase EXPIRED label"*); my SG-300 audit missed it and so did SG-302's packet. **Attribution: packet / audit.** **Destination: SG-301** (one line added to its scope).

I2. **Contract echo is the project file's line, not the Coder's own** (`Rule-set version recorded here: 0.58.0 (AGENTS.md:4)`). Second time on this lane (SG-296). Coder, minor; the desk's lane copy is also behind 0.59.0 (D30).

I3. **A stray `/tmp/sg302_pass_raw.txt` on the host** from an early `tee`, though the packet said `/tmp` is denied; the Coder reported it rather than hiding it. Test output only. **Destination:** the next host-cleanup step, with the SG-300 quarantine ref.

I4. **Some light ratios are approximate** (`~15.0*`, and *No photo yet* carried from an identical token pair rather than read on its own node). Every such pair is far above its bar (ink on paper 15.47 by my recomputation), so no verdict changes.

I5. **`SG-302_fail_full.log`, 1422 lines**, kept although FAIL logs were to hold names and the first assertion only. Disclosed as superseded. Evidence bloat, minor.

**Design notes for SG-301, seen in the shots (not this slice's scope):** the catalog's Gone view still has rounded cards, the enum chip `product (14)`, *Loaded: 2 items* and *None yet*, and the *Gone* / *All (14)* toggles both look selected; the light-mode app header is white over the beige paper. The header (app shell) is outside SG-301's drafted scope — raised to the plan review.

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** prompt gap (I1), carried from SG-300.
- **Root cause:** the 13 px floor is in D18 and the SG-273 packet but was not repeated in SG-300's or SG-302's packets, and the contrast table recorded sizes without checking them against it.
- **Correction:** SG-301 raises the label to ≥ 13 px.
- **Recurrence guard:** every screen packet's contrast table also checks the 13 px floor per row.
- **Owner impact:** none live (not deployed); ≈973 s.

## Model note

Muse's sixth rotated slice: finished under the stop with no overrun, falsified the Architect's surface premise with DOM evidence, and reported its own `/tmp` slip. Weaknesses: an echo of the wrong version line (second time on this lane, first for Muse) and an oversized evidence log.

`slowest_waste`: none notable; G4 scratch ≈511 s, of which a backend restart (three PIDs) was the largest share.
