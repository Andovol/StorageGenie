# SG-301 audit (run 1, SG-301r1, screenshots SG-311) — the font and plain words are in; three screens still miss the paper look

**Score 80/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (both runs, from the launcher line). Diff `a15b76d..db8c719`; shots by SG-311 (Haiku) at `032fe07`. Elapsed run 1 ≈933 s, r1 ≈1031 s, both inside their stop lines. Read: both reports in full for state, enumeration, gate and reasons; SG-311's report; **opened all 7 shots** in `docs/worklogs/SG-301_shots/`.

## Checked independently

- **Shots:** 7 PNGs, 7 distinct 12-char prefixes (my `sha256sum | sort | uniq -c` shows no duplicate; the failed attempt is a separate eighth file, labelled).
- **DOM proofs** (SG-311): heading and body text in the Instrument Sans stack on every shot; EXPIRED 13 px; none of `optimistic concurrency`, `blueprint`, `Phase 0`, `AWAITING_REVIEW`, `consent_disabled`, `If-Match`, `Import <hex>` in `innerText` on Inbox, Expiry, asset; the skipped step reads *Skipped (AI off)*.
- **Gate** (r1): frontend 47 files / 423 tests; host 805; image proof 2 with `npm ci` on the new lockfile.
- **Dependency:** `package.json` gains exactly `@fontsource-variable/instrument-sans` `5.3.0`; the lock adds one node.

## What holds, seen in the shots

The header sits on the paper with a ruled line, square tabs and an inverted selected tab, in light and dark; Instrument Sans everywhere text is text; the Pantry unchanged apart from the 13 px EXPIRED; the Expiry page opens with *"Food and other dated things, soonest first."*; Inbox states read *Waiting for you*, *Done*, *Skipped (AI off)*; the asset page lost the If-Match line, ids and cap codes.

## Findings (all → SG-312 unless stated)

I1. **Page ground not paper on Inbox, Expiry and the asset page** — near-black (dark) and near-white (light) where the Pantry is cream or brown; the *Manual expiry entry* card is white on the page. G3 asked for these screens *"in the look"*. Packet (named tokens and corners, not the page ground) and Coder.
I2. **Buttons, selects and the file control render in Arial** — browsers do not inherit fonts into form controls. G1's proof read only text nodes. Packet.
I3. **Inbox step names** still uppercase internal names (*EXTRACTING DETERMINISTIC SIGNALS*, *COMMITTING*); the job card shows the raw timestamp `2026-11-12T14:42:10`; review rows say *"item"* with no item name.
I4. **The *Menu* button shows on desktop** beside the full navigation; the header wraps to two rows at 375 px.
I5. **Asset page wording:** *"Expiry evidence state: accepted"*, *"per-press cap $0.05"*, *"Live · qty 500 ml"*.
I6. **Expiry tiers** *No tier* / *Critical* / *Urgent* are engine words, pinned to the row's edge.
I7. **Catalog body** (monospace *"2m ago"* and `item` chips, *Source Only*, rounded thumbnails, white toolbar) — **SG-307's scope, as planned.**
I8. **Scope vs stop:** run 1 could not finish; the retry and a separate shots slice were needed (≈2600 s of runs for one slice). Packet (my scoping).
I9. **Untracked `.vite/` left on the host** caused SG-311's first refusal (`dirty_unattributable`); quarantined by the engine. Coder.

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** scope too large for one run; design requirement under-specified.
- **Root cause:** *"tokens, square corners"* named pieces of the look but not the page ground or form controls; the proof read text nodes only.
- **Correction:** SG-312 (I1–I6).
- **Recurrence guard:** screen packets require the computed page background and a button's font family in the DOM proof, and one screen group per slice.
- **Owner impact:** ≈2600 s of runs; no live harm.

## Model note

Muse kept both stop lines and was honest about every gap; it under-ran the gate in run 1 and left `.vite/` behind.
