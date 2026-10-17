# Q1/Q2/Q3 directives (D-12/D-13/D-14), D-10 superseded — 2026-10-17

**Owner messages, byte-identical (2026-10-17, chat; Q-numbers mirror the Architect's Q&A they answer — Q1 = Raw Data, Q2 = Cutout/Scene availability, Q3 = Household selector):**

> Q1 - I don't need it.

> Q2 - Push me to get this implemented, tell me what is needed, with details.

> Q3 - One user is assigned to one household, he cannot have multiple households. Remove the selectors.

## D-12 — APPROVED: remove the Raw Data section

- Q1 removes the dev-verification panel from the asset drawer (`ItemInspectorDrawer.tsx:440-460`, `rawJson` memo `:171-174`, test `drawer.test.tsx:196-206`). Interpretation recorded: full removal of section + memo + its test (not a hide-behind-flag), reversible via git. Server-side `assertions` readback is untouched — only the drawer panel goes.
- Slice: **SG-207** (packet drafted with this decision; dispatched after the SG-206 serve lands).

## D-13 — APPROVED: one user = one household; remove the household selectors

- Requirement on record: a user belongs to exactly one household and cannot hold several. Server-side `?household_id=` scoping is untouched; only the switching UI goes: the nav selector (`App.tsx` household select) and the toolbar selector (`CatalogToolbar.tsx:123-137`, `aria-label="Household"`), plus any further household-switch affordance the slice's enumeration finds (e.g. Settings management, if any). Household resolution keeps the existing rail (stored id else first household — `HouseholdContext.tsx`); the slice reports any remaining multi-household path it finds.
- D-10 (auto-hide on single-household, proposed one turn earlier) is **SUPERSEDED** by this removal — marked, not deleted.
- Slice: **SG-208** (packet drafted with this decision; dispatched after SG-206/207 in order).

## D-14 — D7 push: what the owner owes for Cutout + Scene (Q2)

- The AI image stages stay parked on owner-side answers (backlog `Context Scene resume` row; SG-159 proved both legs blocked live). The detail the owner asked for is answered in chat this turn, not here: (a) Google AI Studio quota/billing for `google/gemini-3.1-flash-image` (measured upstream 429, unbilled) or a narrowed substitute image-model pick — Google-only stands per D-1009-10, no slug is substituted without a pick (`PG-IC-03`); (b) Muse has no artifact-yielding transport (chat 200 text-only, Image-API endpoints `[]`) — confirm Google-only or name a transport; (c) per-render + monthly spend caps for live calls (measured ~$0.0008/render; real money, owner-owned).
- No slice dispatches on the AI stages until (a)/(b)/(c) land. D-11 (D7 answers) is carried, not closed.

## Ordering this turn

SG-205 audit + rate (done, 98) → SG-206 serve rider (D-5 due on the SG-205 product commit; pre-approved, dispatched this turn) → SG-207 → SG-208 in slice order. No product slice runs concurrently with another.
