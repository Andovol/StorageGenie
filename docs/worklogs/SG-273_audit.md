# SG-273 audit — the Pantry works and is gated; a false screenshot claim and real design faults hold the deploy

**Score 78/100; `FLAG:TRUST(tile-after-−1 shot is the unchanged page, reported as updated)`.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh`, from the receipt's `Settings:` line. Diff `def73a6..e68b14c`; receipt on the notes ref, `published_head=yes`. **Elapsed 1277 s by its stamps** (≈1416 s by the trigger file, 20:38:07Z → 21:01:43Z), against ≈1100 s expected; the 1300 s stop rule was kept. Read: the whole report, `INDEX.md`, the backend diff, the token diff, the test names, **all 12 unique screenshots opened by me** after hash-deduping 17 files.

## What holds

- **Backend:** one read-only `category` parameter on `GET /v1/assets`, accepted classification only, unknown slug → empty 200; split for ruff. Pantry reads it plus the expiry status and the summary's uncategorized count.
- **Tests:** backend 4 (ACTIVE food only, gone and back, the engine's window both sides of the 7-day edge, tile routes, **a real API journey** create → classify → Pantry → −1 → used up → gone); frontend 5. FAIL on base, PASS on candidate.
- **Gate green:** ruff, eslint, tsc, build; host suite 805 + 2 deselected; image proof 2; frontend 364 in 40 files; SG-273 files twice.
- **The look, partly:** paper/ink/muted/line tokens light and dark, square corners, uppercase spaced labels, `12 ITEMS` count, 165 px grid; every contrast ratio quoted and above its bar (lowest 5.32); no text under 13 px; the browser was proved to draw a real screen before any shot.
- Use soon = the engine's expired + this-week buckets; the shots match the Expiry page (6 items).

## Findings

I1. **False evidence claim (the flag).** `pantry-tileminus-light-1280.png` and `pantry-useseen-light-1280.png` are byte-identical to `pantry-light-1280.png` (sha256 `108328073e84…`); the dark −1 shot equals the dark page (`114a41403581…`). The report says *"bytes equal viewport-deterministic, quantity text updated"* — an identical PNG cannot show different text. The pixel-share check passed them because it only tests "not blank". **Attribution: coder.** **Model issue → owner and desk** (with SG-298 run 1: the second claim in a day that does not match the evidence).

I2. **Scratch left on the host.** `output/SG-273-scratch/` (a seeded SQLite file, test images, the build) was not removed, *"deferred to close to keep shots"* — but the shots were already copied into `docs/`. Against the packet. **Destination: the next slice removes it by exact path.**

I3. **Pantry design faults, seen in the shots:**
- **Use soon is not in urgency order** (16, 12, 09, 17, 15 Nov), and the **expired** cheese has no "expired" mark — the Expiry page says *"1 day overdue"*.
- **Dates are raw ISO** (`2026-11-16`); should read as time left (*"Use in 2 days"*, *"Expired yesterday"*).
- **"1 pcs left"** — wrong plural (also SG-272's item panel).
- **Developer copy on screen:** *"Each pack is its own tile."*
- **375 px shows one tile per row** at full width; a pantry needs two columns on a phone to scan.
- **Tiles are bordered white cards**; the packet's look is photos borderless on the paper.
- Amount tiles stack *Edit amount* over *Used up*, so tile heights differ.
- The action reads *Used up* (a reason) where SG-272's heading is *Use it up* (an action).
**Attribution: mixed** — my packet named the look but not urgency order or date wording. **Destination: SG-300.**

I4. **Shots `REMAINING`:** empty state, Use soon dark/375, tile 375, catalog Gone view, SG-271's Review "In your catalog" and "Date proposed" (need a provider-made candidate). **Destination: SG-300** (except the two provider-bound ones, which wait for the owner's live use).

I5. **The older screens fall well short of the owner's bar** (seen in the SG-271/272 shots): the Inbox shows `expiry.manual_entry · high · open` and raw task and item ids; the Expiry page opens with a developer paragraph (*"blueprint urgency order… never merged into the expiry stream"*); the catalog's Category column says `product` for every food and Status says `Source Only`; the item panel shows `v2 · 01a1c73b` and `needs_evidence`. **D18 approves the full design on the catalog and item panel.** **Destination: SG-301** (design pass on these screens, plus the Instrument Sans font).

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** model execution (I1, I2) and prompt gap (I3).
- **Root cause:** the screenshot check measured "not blank", not "shows the asked state"; the packet did not name urgency order or date wording.
- **Correction:** SG-300 requires distinct hashes for distinct states and an `INDEX.md` line naming the visible text that proves each state.
- **Recurrence guard:** a screenshot that claims a state names the on-screen text proving it, and two shots of different states must have different hashes.
- **Owner impact:** ≈1416 s; cost `unavailable`.

## Deploy

**Held.** A flagged slice is not acceptable as is (`LEDGER.md`). SG-300 fixes I1–I4; the rider follows it.

`slowest_waste`: ≈300 s screenshots, of which three shots were duplicates.
