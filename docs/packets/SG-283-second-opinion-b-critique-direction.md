# SG-283 — Second opinion Phase B (critique): direction after stage C

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. This lane's snapshot has no `.git`: state `unknown` once and carry on.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A is done (`docs/worklogs/SG-282_report.md`). This is **Phase B — the critique.** Attack the picks below. **R1 to R3 were approved by the owner before this review, on the owner's own request that the review follow** (*"D17-D19 - approved."*, *"Get a 2nd opinion from Sol 6.1 for all important topics."*). The review is advisory; a strong objection goes back to the owner. **R4 to R7 are the Architect's recommendations, not decisions.**

**New owner statements since Phase A, verbatim:** *"The Outfits suggestion and saved Outfits seems important features."* · *"Lets try to enrich other modules like "Pantry" with similar features, including AI and "intelligence" features."*

## The picks, verbatim

> **R1 (D17), approved.** Add to the roadmap: stage D: V1, V2, V3, V5, W1, W2, W3, W4, W5. Stage E: V4, V6, V7, W6, W7, W8, W9, W10, W11, W12. Not worth copying: family feed, partner links, XP and streaks, credits and billing, local AI, eight languages.
>
> **R2 (D18), approved.** The new theme's colours, font and shapes everywhere, with the full design on the catalog, item panel and Pantry view. Keep dark mode; enlarge the 9–11 px type.
>
> **R3 (D19), approved.** Finish Pantry (stage C), then shared images (stage D), then Wardrobe (stage E).
>
> **R4, recommended.** W13 suggest an outfit (weather and a hint, occasion, optional build around a piece, weather override) and W14 saved outfits (list and calendar, build your own, filters) become the first things built in stage E. They need W11, V4, W6 and a weather source, which is new. They can start on normal photos; only flat-lay collages need cutouts.
>
> **R5, recommended.** Product images per the roadmap's stage D: a cloud cut-out of the owner's photo with a fixed backdrop and non-AI shadow, the original kept; no regeneration by default. Provider remains the owner's choice.
>
> **R6, recommended.** Deploy SG-279 as built through rider SG-280. SG-280 adds: compare the live `candidate` schema text with the expected text before any change, and stop on any difference; treat a leftover `_alembic_tmp_candidate` as the during-migration state. The rest of its design is D16's recovery states, already approved. It does not add an isolated restore rehearsal beyond restoring the backup to a scratch path and proving `integrity_check`, `foreign_key_check`, schema head and table counts.
>
> **R7, recommended: the same pattern for Pantry, and later other modules.** Built after the owner's real-shelf trial, in this order, each only if that trial supports it:
> - **P1 Use log:** counts from "used" and "thrown away" (stage C adds the reasons), used and never-used lists, a simple waste view.
> - **P2 Check before you buy:** barcode or photo, answering "you have 2, the nearer one expires in May", on the existing barcode reader and duplicate check.
> - **P3 What can I make:** servings and time, build around an ingredient, nearest dates first, with a stated reason, extending the manual use-up run (`backend/app/services/planning/service.py`) and category chat (`backend/app/services/chat/service.py`).
> - **P4 Saved meals and a calendar.**
> - **P5 Running low and a shopping list:** from the use log, suggestions only (Q27).
> - **P6 Shelf check:** one item at a time, keep, correct or gone.
> - **P7 Add by typing:** "2 milk, 500 ml".
> - **P8 Household food settings:** dislikes, diet and allergies entered by people, plus learning from accept and skip.
> - **P9 Label fields:** brand, storage and allergens, read from the label only, never guessed.
> - **P10 A daily "use this today" push.**
>
> **Limits on AI, always:** it never says food is safe past its date, never guesses an allergen or a date, and gives no dosing or interaction advice for medicine; medicine gets dates and check-before-buy only. Other modules take the same shape (suggest, saved, log, check before buy, review) when the owner picks them (Q6). Every AI call keeps the existing consent gate and cost log.

## G1 — Read

`AGENTS.md`'s top section, `docs/reviews/2026-11-02-direction-after-stage-c-context.md`, `docs/worklogs/SG-282_report.md`, `docs/worklogs/SG-279_audit.md`, and the code they name, plus `backend/app/services/planning/service.py`, `backend/app/services/chat/service.py` and `backend/app/services/providers/prompts/planning-v1.md`. **List every file read beyond those.**

## G2 — Per pick R1 to R7

- the strongest case against it, with evidence (`file:line`, a quote, a measurement);
- a premise of it that is unverified;
- the observation that would settle any disagreement.

An objection without evidence is labelled `opinion`. Where your Phase A pick differed, say whether seeing the Architect's reasoning changes it. Check especially: R3 against your Phase A sequence, including restore; R1's placement of W1, W3 and W7 before any use data exists; R6 against your restore-rehearsal step; whether planning and chat can really carry P3 given the one-operation provider seam at `planning/service.py:3-13`; and whether R7's safety limits are enough.

## G3 — Report

Your final message **is** the report (read back with `SG-283 --status`; the Architect copies it unedited to `docs/worklogs/SG-283_report.md`). **Keep the whole report under 200 lines: the engine keeps only 200 lines of a read-only run's report.** The most serious objection first, about 25 lines per pick. Shape: `SG-283` as the first token; the contract-version line (`PB-4`); the extra-files list; R1–R7; a closing line of what you read.

## Constraints

Read-only; reads confined to the repository at BASE; no host changes, credentials, browser, network or database. Hang bound: file reads 120 s each. A denial is a STOP (`PB-2`).

## Acceptance criteria

Each of R1–R7 answered; each objection evidenced or labelled `opinion`; extra-files list complete; report under 200 lines. `PB-3` vacuity: "no objection" needs one sentence on what was checked.

## Report

Destination: final message (engine-published). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.
