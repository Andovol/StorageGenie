# SG-313 audit — SG-312's four screenshots, every proof from the DOM; SG-312's change holds on screen

**Score 92/100; no flag. SG-312's deploy is released to its rider (SG-314).** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh` (trigger; receipt note `Settings: … model_source=command effort_source=command`). Diff `5e23b07..c2e18b0`: 4 PNGs, `docs/worklogs/SG-312_shots/INDEX.md`, the report — nothing else (`git diff --stat`). Elapsed 640 s by stamps (expected ≈450 s). **I opened all four shots myself.**

## Holds — each checked against the image and the DOM read

| Shot | What I saw | DOM read that agrees |
|---|---|---|
| 01 Inbox light 1280 | Paper ground; plain step names; skipped steps read *Skipped (AI off)*; date *Today, 17:59*; no *Menu* | body `rgb(244,240,232)`; `.nav-menu-toggle` `display:none` |
| 02 Expiry light 1280 | Paper cards with a line border; tier words beside each row | tier pills `Use first, Use soon, Upcoming×2, Long lead, Safe` |
| 03 Asset dark 1280 | Dark paper; *1000 ml left*, *Date confirmed*; no developer wording | body `rgb(32,27,23)`; nine strings absent |
| 04 Pantry light 375 | Header on two rows; white tile buttons on paper; EXPIRED 13 px | `nav` 93 px, Import top 52; buttons `rgb(255,255,255)` |

Fonts: heading, body and every named button compute to Instrument Sans (the Arial controls SG-311 found are gone). Smallest text 13 px on all four. Servers started in the background, both calls returned at once — the SG-312 failure did not recur. Distinct hashes 4/4.

## Findings (session IDs)

I1. **Identity line inferred, not read** — the first line says model and effort were inferred from `STATE.md`, process arguments not exposed. Honestly labelled; the receipt note confirms the values. `PB-4`. **Coder, minor. Disposition: noted in the profile.**
I2. **Design notes missed three things visible in the shots** (found by my own look): Expiry rows show **ISO dates** (*2026-11-07 · Expiry date*) while Inbox says *Today, 17:59*; the Inbox **Saving** step reads *In progress* while the job only waits for review (`frontend/src/lib/labels.ts:17` maps `PENDING` to *In progress*); the *Long lead* item sits under the **Safe** heading (bucket and tier names collide). **Coder, design-note depth. Disposition: a small wording slice after SG-307 (queued in `STATE.md`); SG-307 is already a full build slice.**
I3. **White controls measured, not guessed:** Pantry tile *Edit* / *Use it up* / *−1*, the theme toggle, the Inbox *Review status* select; on the dark asset page the native *Choose Files* control is white and *Attach evidence* floats far right. **Disposition: SG-307** (catalog and item panel own these surfaces).
I4. **Header wraps at 375 px** — *Import Asset* drops under the logo row (93 px tall). Settles SG-312's open question. **Disposition: SG-307's design scope.**
I5. **Fallback step names** *Validating input*, *Analyzing with ai*, *Building candidates* (lowercase *ai*, no map entry). Found by the Coder. **Disposition: the same small wording slice.**

## Below 95

- **Failure class:** evidence complete, design review shallow on dates and status words. **Root cause:** the packet asked for "anything that looks wrong" without naming dates and status words as things to check. **Guard:** screen packets list date format and status wording explicitly among design-note checks.
- **Owner impact:** none; the Architect's own look caught I2.

## Model note

Muse's sixth rotated slice: on time with a wide margin, every DOM read delivered, servers handled as told, no claim contradicted by its own evidence (its SG-273 weakness did not recur). Gaps: the identity line inferred, and design notes thinner than the shots warranted.
