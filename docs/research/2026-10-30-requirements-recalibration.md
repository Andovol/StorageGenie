# Requirements recalibration — 2026-10-30 (owner D8 steering)

The owner's words and answers are recorded verbatim in `docs/decisions/2026-10-30-session-approvals.md` (second-session sections). This file holds the Architect's research and the **open** round-3 questions, so the next session can continue without re-searching.

Source caveat: almost every source below is a vendor site, app-store listing or affiliate roundup — feature claims are self-reported, not tested.

## Q8 — expiry design (Architect's recommendation, NOT yet approved: Q21)

| | A: one "Expiry Tracker" module (today's code) | **B: expiry as a shared feature any module switches on (recommended)** |
|---|---|---|
| Shape | All dated categories inside one module; clothes outside it | Pantry, Medicine, Cosmetics, Documents switch expiry on; Wardrobe does not |
| Fits "different categories, different focus" | Poorly | Well |
| Rework | None | Split the current plugin into an expiry feature + a Pantry module (UNVERIFIED — size not scoped) |
| Reminders | One rule set | One engine; each module sets its own windows |

## Q15 — AI imagery uses found in similar apps

| ID | Use | Seen in |
|---|---|---|
| A1 | One house style for every product photo (cut out, same backdrop, same shadow); original kept as evidence | Indyx (background removal), Photoroom (batch AI backgrounds) |
| A2 | Clean image taken from the web when the owner's photo is poor | Common in catalogs |
| A3 | Flat-lay outfit collage (owner's Q13 pick) | Most wardrobe apps |
| A4 | User avatar wearing an outfit (owner: later) | Acloset, Alta |
| A5 | "What you could cook" dish pictures from the pantry | Architect's idea, on top of KitchenPal-style recipe matching |
| A6 | A styled picture of the whole pantry shelf from owned items | Architect's idea, not found in the searched apps |
| A7 | A mood board from a prompt, filled with owned items | Adobe Firefly Boards (prompt boards) |
| A8 | "This piece would complete N outfits" — suggestion only, never a purchase | Implied by AI-stylist apps |

## Q19 — design references (names only; looks not yet judged)

Whering ("stylish and elegant"; one reviewer: "too visually busy") · Indyx ("sleek", clean via background removal) · Alta (compared to the Clueless closet) · Acloset (strongest AI) · pantry: KitchenPal is the strongest all-in-one, but no source rated pantry apps on looks.

## Q20 — creativity patterns

| ID | Pattern | Seen in |
|---|---|---|
| C1 | Daily pick from weather and wear frequency | Cladwell |
| C2 | Shuffle / "Dress Me" | Whering |
| C3 | Seasonal prompt sets | Pause Creative |
| C4 | Bounded challenges ("10 pieces, 20 outfits"; "cook with these 3 near-expiry items") | Design-prompt newsletters |
| C5 | Learning taste: skip what was just worn, remember liked combinations | AI closet apps |
| C6 | Style games ("Outfit Battle") | One wardrobe app |

Recommended set: C1 + C2 + C5 for Wardrobe, C4 for Pantry; no social feed.

## Round 3 — OPEN questions (asked 2026-10-30, unanswered at the reply-deadline close)

| ID | Question | Recommendation |
|---|---|---|
| Q21 | Approve design B for expiry | Yes |
| Q22 | Quantity precision | Count or amount + unit; one-tap −1 and "gone" (moves to history, not deleted) |
| Q23 | Photo house style | Open — lead option warm neutral (linen/soft beige) + soft shadow |
| Q24 | Send a photo of a person to a cloud AI for the avatar | Open — owner's privacy call; if yes, opt-in per person, deletable |
| Q25 | Outfit suggestion drivers | Weather + occasion + wear history + colour harmony |
| Q26 | Two people: shared or separate wardrobe | Separate wardrobes, shared pantry |
| Q27 | May the app suggest things to buy | Yes, suggestions only, never a purchase |
| Q28 | Interface language | English unless Romanian is needed |
| Q29 | Make a design mood-board page next | Yes |

## Sources

getwardrobe.com/compare · acloset.app · goodonyou.eco/wardrobe-organising-apps · myindyx.com/versus/whering-vs-indyx · joinelara.com/blog/best-virtual-try-on-apps · pantryfy.ai/blog/best-pantry-inventory-apps · pantrypersona.com/blog/best-pantry-inventory-apps-2026 · photoroom.com/batch/ai-backgrounds · apps.apple.com (Pause Creative id1553820487, Cladwell id1140550878) · adobe.com/products/firefly/features/moodboard.html · contra.com/p/RlbPNvbv-pantry-buddy-mobile-app
