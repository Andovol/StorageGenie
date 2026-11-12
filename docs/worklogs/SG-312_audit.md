# SG-312 audit — SG-301's design fixes built and gated; screenshots not taken (a hung server launch ran past the stop)

**Score 82/100; no flag. Deploy held until its screens are seen** (owner: *"open every screenshot yourself"*). Model `opencode-go/claude-haiku-5-5`, effort `high` (trigger). Diff `80011d0..58ba0ef`, 17 frontend files. Read: report sections Elapsed, Premises, G1, gate, REMAINING.

## Holds

- **Gate green:** frontend 50 files / 450 tests; host 805 + 2 deselected; image proof 2; eslint 0 errors; FAIL on base 26 of 27 (the one pass is an existing CSS guard, named).
- **G1:** `body` on `--paper` from one place, the shell's `bg-background` replaced, the Pantry's redundant ground removed; a control-font rule; step names in `labels.ts` (*Checking the file*, *Tidying the details*, *Looking for duplicates*, *Your review*, *Saving*); *Menu* given the existing `nav-menu-toggle` class (hidden at ≥ 768 px); asset and tier wording through the label map; item names from existing reads, no backend byte.
- **Premises checked, one falsified with evidence:** `labelStepName` was local to `InboxPage.tsx`, not in `labels.ts`.

## Findings

I1. **No screenshots.** The scratch-server launch blocked the tool call for its 600 s timeout and the run passed the 1100 s line by ≈120 s. **Attribution: mixed** — Coder (a server started in the foreground, against the 60 s start bound); packet (screens again at the end of a full build slice). **Destination: SG-313**, screenshots only, as SG-311 did.
I2. **Left on white `--card`:** buttons on the asset page, the expiry form's *Clear*, the Pantry tiles' controls — reported, not changed. **Destination: SG-313's design notes decide; then SG-307 or a small follow-up.**
I3. **Expiry tier names** *Upcoming*, *Long lead*, *Safe* left for the owner. Minor; noted for SG-307's packet.

## Below 95

- **Failure class:** evidence phase lost to a hang. **Root cause:** a foreground server start in a slice that ends with a scratch app. **Recurrence guard:** screen slices start servers with `nohup … &` and poll health within the 60 s bound; screenshots run as their own slice when the build slice is full.
- **Owner impact:** ≈1250 s; deploy waits for SG-313.

## Model note

Haiku's eleventh rotated slice: clean premises and a full gate, then its first stop-line overrun, caused by a hung command, not by choosing to continue.
