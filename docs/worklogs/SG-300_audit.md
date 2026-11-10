# SG-300 audit — the Pantry now meets the brief in light mode; the dark-mode warning colour fails contrast

**Score 92/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high`, from the receipt's `Settings:` line (the report could not read effort; the engine is the authority). Diff `36be113..a2b8a2d`, frontend only; receipt on the notes ref, `published_head=yes`. **Dispatch:** the first trigger was refused `dirty_unattributable` (SG-273's leftover scratch, its audit I2; `output/` is not git-ignored); re-triggered with `--quarantine`, which moved it to the host-local `refs/quarantine/flag-SG-300-20261110T212535Z`. **Elapsed ≈964 s** by the trigger file (21:25:34Z → 21:41:38Z) against ≈1000 s; ≈900 s by its stamps. Read: the whole report, `INDEX.md`, the diff stat; **opened 7 of 12 shots** (Use soon light 1280 and 375, dark 375, notice, empty, catalog Gone, item panel); hash check run myself: 12 files, 12 distinct.

## What holds

- **All nine G1 lines visible in the shots:** urgency order (Juice −3, Cheese −1, Milk 1, Yogurt 2…), *EXPIRED* label, time-left wording, *"1 left"* / *"500 ml left"*, the new subtitle, **two columns at 375 px**, photos straight on the paper with no card, one even action row, *Use it up* with the *"Juice used up · Put back"* notice, empty state.
- **One shared formatter** (`frontend/src/lib/quantityText.ts`) in the Pantry, the item panel and the asset page; SG-272/SG-273 tests updated and named.
- **Evidence honest this time:** distinct hashes per state (my check agrees), the proving text read from the DOM through DevTools, missing dark shots listed as `REMAINING` rather than claimed.
- **Gate green:** eslint, tsc, build; host suite 805 + 2 deselected; image proof 2; frontend 393 in 43 files; the 8 SG-27x/300 files twice.
- **I2 closed:** the SG-273 scratch was already moved by the quarantine; this run's own scratch removed by exact path.
- **A hazard found unasked:** `frontend/src/api/client.ts` defaults the API base to `http://localhost:8003` — the live port — when `VITE_API_BASE` is unset. It rebuilt the scratch bundle against the scratch port. Every packet running a scratch app must set it.

## Findings

I1. **Dark-mode accent fails contrast.** *EXPIRED*, *"Expired 3 days ago"*, *"Use by tomorrow"* use `--primary` (`#6e302e`) on the dark paper (`rgb(15,14,13)`): **≈1.95:1** by my calculation (relative luminance 0.056 vs 0.0045), against 4.5:1. `tokens.css` (SG-118's comment) already records ≈1.8:1 for primary on the dark card and gives `--link` a lighter tint for exactly this. Visible in `pantry-useseen-dark-375.png`. **Attribution: packet** — G1 line 2 named `--primary` and SG-300 did not repeat SG-273's every-pair contrast requirement. **Destination: SG-302** (before the rider).

I2. **The item panel still shows developer text** (*"Bounding-box overlay omitted…"*, *"Uses If-Match: 2 for optimistic concurrency"*, *Kind of item: product*, the cut-out tabs) — SG-301's scope (D27). Noted, not this slice's.

I3. **Three dark shots not taken** (Use soon 1280, notice, catalog Gone), listed honestly. **Destination: SG-302** takes the dark Pantry shots again after its fix.

I4. **≈200 s lost** to a `pkill -f` that matched its own command line. Coder; `slowest_waste`.

I5. **Empty state text says "Add an item from Capture"** without a link. Minor. **Destination: SG-302.**

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** prompt gap (I1).
- **Root cause:** a colour named in the packet without its dark-mode contrast; the measurement requirement was in SG-273's packet but not repeated here.
- **Correction:** SG-302 gives the accent a dark-mode value at ≥ 4.5:1 and measures every pair again.
- **Recurrence guard:** every screen packet carries the every-pair contrast requirement, light and dark, whatever colours it names.
- **Owner impact:** ≈964 s; cost `unavailable`.

## Model note

Haiku's seventh rotated slice: the most careful evidence of the session — DOM-confirmed proof per shot, honest gaps, and a live-port hazard found unasked. Weakness: one self-inflicted shell hang.

`slowest_waste`: ≈200 s shell hang on a self-matching `pkill`.
