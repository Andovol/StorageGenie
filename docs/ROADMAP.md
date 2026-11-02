# StorageGenie — product roadmap

Rewritten 2026-11-02 around the owner's direction (D8). **Stage A approved by the owner 2026-11-02 (D11), which closes D8; each later stage needs its own approval.** Reviewed blind by SG-266 (`docs/reviews/review-ledger.md`). Owner words: `docs/decisions/2026-10-30-session-approvals.md`. Research and answered questions (Q21–Q29): `docs/research/2026-10-30-requirements-recalibration.md`. Waiting items: `docs/backlog.md`. Where the blueprint (`inception/generic_asset_catalog_expiry_tracker_blueprint.md`) disagrees with this file, this file wins until the blueprint is amended.

## The product

A beautiful, easy catalog of everything a household owns, built to inspire creativity. One item belongs to one **module**, and each module has its own focus and actions over a shared core. AI imagery, AI suggestions and web enrichment play a key role. Capture is on the phone; review is on phone and desktop. English unless Romanian is needed (Q28). Spending is frugal, with no fixed cap (Q16).

## Stages

Each stage needs the owner's approval. Pantry first and Wardrobe second are the owner's order (Q6); the order of the other stages is the Architect's proposal. Sizes are the Architect's judgement, not measured: S a day or two, M several days, L a project of its own.

| Stage | Outcome | Size | Needs first |
|---|---|---|---|
| **A. Clear the deck** | The three approved D7 fixes are live | S | Owner approval of the stage |
| **B. The look** | One agreed visual direction and photo style | S | Design mood-board page (Q29), owner's reaction |
| **C. First real Pantry** | One styled Pantry you can use end to end: see it, use it up, quantities quick to change | M | B; second opinion (app database) |
| **D. Pantry presentation** | Every photo shares one style; enrichment per module; restore from backup proven | M | C used on real items; the owner's image-provider choice |
| **E. Wardrobe** | Garments catalogued, outfits composed and suggested | L | C, B |
| **F. Later ideas** | Buying suggestions, recipes, the next module | M each | Owner picks, one at a time |
| **G. Avatar try-on** | A person's AI avatar wears an outfit | L | Owner's final go-ahead (Q24) |

### A. Clear the deck

- **Done and live 2026-11-02:** SG-262, SG-263; `docs/releases/2026-11-02-sg262.md`.
- The D7 fixes as approved: hide the review form when it has no asset data (E2); the reverse move resolves the open date task (F1 scoped); "No date" wording (G2); one work slice plus one deploy rider (H1).
- The packet checks each fix against the expiry split (Q21). `UNVERIFIED — my inference`: none depends on it.

### B. The look

- **Done 2026-11-02:** the owner chose direction A, Linen Shelf (D13): beige ground, large photos, Fraunces and DM Sans, olive accent. Board: claude.ai/artifact/XR8roXa3Hv749RofRxgNTH. Its products are stand-in drawings. Real references (Q19) have not been looked at.
- The result becomes the design rules every later screen follows, in `frontend/src/theme/tokens.css`.

### C. First real Pantry

Build one thin Pantry end to end, then widen from what real use shows (SG-266 picked this over building the module framework first). The owner tries it on real items: capture, find, use up. The live census holds only 7 assets, and why is not known.

Approved by the owner 2026-11-02 (D14), after critique (SG-267, SG-268). In progress.

- **First slice, a read-only walk of the real flow, on a throwaway copy with test data:** both capture paths (by hand and by import), inbox, review, category, date, find the item. Record wrong turns and repeated entry as well as dead ends. Known suspects: no link from the review page to the item (`docs/worklogs/SG-262_audit.md`, I1), inbox date tasks that link to the wrong page (I6), and two controls that look like "category" but write different things (`frontend/src/components/shell/ItemInspectorDrawer.tsx:90-107`).
- **Then the fixes the walk shows are needed.**
- **What enters Pantry:** accepted category `food_beverages`. Accepting an item does not classify it today (`backend/app/services/candidates.py:850-905`), so anything captured from Pantry counts as food, and unsorted items get a clear "Not sorted yet" prompt rather than vanishing. Shelf-stable food stays food with no date needed; the Non-perishable wording changes so it does not attract groceries.
- **Pantry view:** what you have and what to use soon, in Linen Shelf, on this view only. Each pack is its own tile, with no grouping by name yet, because names are not reliable product identity. Household pantry is shared (Q26). Photos stay as captured until stage D, so the first version will look less even than the mood board. The menu link appears only when the journey works end to end.
- **Quantities (Q22):** a count, or an amount with a unit. `asset.quantity` and `asset.unit` already exist. One tap takes off 1 where the item is counted; an amount such as 500 ml opens a quick edit, because taking off "1" means nothing there.
- **"Gone" (Q22):** the ARCHIVED status plus a reason (used, thrown away, given away), with a "put back" undo, both through one dedicated all-or-nothing action; no schema migration expected. Tests compare the catalog, expiry, reminders, tasks and summaries across a gone-and-back cycle.
- **Modules, for now:** a small category-to-module map read by the Pantry view, named as temporary. Wardrobe's stage registers the first real second plugin. Expiry is a capability modules use (Q21), and the stored paths stay as they are (`plugin:expiry-tracker/…`, `backend/app/plugins/expiry_tracker.py:29`). Other dated categories keep working.
- **End of the stage:** the owner uses it on one real shelf, then checks it again after ordinary household use: can missing or wrong stock be corrected without much effort (SG-268)? A special "shelf check" mode gets built only if that shows the need.

### D. Pantry presentation

- **House-style photos:** every product photo cut out on one backdrop, the original kept as evidence (Q9, Q23). Recommended mechanism: a cloud cut-out with a fixed backdrop and shadow added without AI, tried first on real samples (provider is the owner's choice). A clean web image where the owner's photo is poor. The screens have cut-out and scene tabs, but those images are mock-only today (`frontend/src/components/catalog/ProductCard.tsx:9`).
- **Web enrichment per module** (Q17): built on the existing web lookup (row 7).
- **Restore from backup (row 16), proven:** export exists but restore does not, and this should work before much more of the owner's data goes in (SG-266).
- **What a photo may carry to the cloud:** the send boundary, retention and deletion, and what happens to people or labels caught in a shot.
- **Blocker:** image generation is parked on owner answers about the provider (`docs/backlog.md`, Context Scene row). Provider and model are the owner's choice (D-1024-16), and no local models run on the server (D-1024-15).

### E. Wardrobe

- **Capture:** garments by photo and by web lookup (Q12). No expiry (Q8).
- **The module rule:** Non-perishable covers clothing and tools alike (blueprint line 385), so clothing needs its own category.
- **Separate wardrobes per person (Q26):** needs a "whose item" field. There is no sign-in by design (row 17), so this is a person picker, remembered per device, with an unassigned state. It organises; it does not keep anything private from the other person.
- **Outfits:** flat-lay collages from owned pieces (Q13).
- **Suggestions (Q25):** weather, occasion, recent wear, colour harmony.
- `backend/app` and the screens hold no wardrobe or outfit feature today (searched for outfit, wardrobe, garment, clothing; the one hit is a drawer's label).

### F. Later ideas

- Buying suggestions, never a purchase (Q27).
- Recipes (Q10), with "what you could cook" pictures.
- The next module, chosen with the owner one at a time (Q6).

### G. Avatar try-on

- Each person opts in, and the avatar can be deleted. The final go-ahead comes when this is scheduled and the provider's terms have been read (Q24). That item gets the second opinion.

### AI imagery and creativity picks (D12)

Owner chose the focused set: A1 + A2 in stage D, A3 in stage E, A4 in stage G, A5 + A8 in stage F, A6 + A7 not planned; C4 in stage D, C1 + C2 + C5 in stage E; no social feed. IDs are in the research file.

## What is already built

Row numbers are kept because older records cite them.

| Row | Feature | Status | Evidence |
|---|---|---|---|
| 1 | Create items by hand, attach photos, search, export a backup | Built | `backend/app/api/v1/assets.py`, `evidence.py`, `frontend/src/routes/CatalogPage.tsx`, `AssetDetailPage.tsx` |
| 2 | Import box with retry | Built | `backend/app/api/v1/jobs.py`, `frontend/src/routes/InboxPage.tsx` |
| 3 | Read labels automatically (text, barcodes, photo dates, duplicates) | Built | `backend/app/services/signals.py`, `dedup.py` |
| 4 | Review desk (accept, edit, merge, split, hold, reject) | Built | `frontend/src/routes/ReviewPage.tsx`, `backend/app/api/v1/candidates.py` |
| 5 | Expiry dates by hand, never guessed | Built | `frontend/src/routes/ExpiryPage.tsx`, `backend/app/plugins/expiry_tracker.py` |
| 6 | Photo reading for food and medicine | Built | `backend/app/services/providers/router.py`, `candidates.py` |
| 7 | Web lookup with sources shown | Built | `backend/app/services/enrich/`, `frontend/src/components/WebAlternates.tsx` |
| 8 | Use-up suggestions by manual run | Partly built | `backend/app/services/planning/service.py`; no schedule |
| 9 | Expiry reminders | Partly built | In-app, daily, live (`backend/app/services/reminders/daily.py`). No email (D-1024-2), no user-set schedule, no actor on a transition (backlog W4) |
| 10 | Category chat from owned items | Built | `backend/app/services/chat/service.py` |
| 11 | Opened-date countdown; household and document dates | Built | `backend/app/services/opened_countdown.py`; release `docs/releases/2026-10-30-sg258.md`; findings are stage A |
| 12 | Home summaries | Built | `backend/app/services/analytics/service.py` |
| 13 | Places, links, saved searches, filters | Built | `backend/app/api/v1/locations.py`, `relations.py` |
| 14 | One cloud photo reader with actual-cost logging | Partly built | `backend/app/services/providers/`. Fallback deferred (W6), no local provider (W7), per D-1024-17, -18, -19 |
| 15 | Category editor in settings | Missing | Unscheduled; may be replaced by the modules |
| 16 | Restore from backup | Missing | Export only (`backend/app/api/v1/exports.py`); stage D |
| 17 | Sign-in | Intentionally out | No passwords by design; stage E needs a person picker |
| 18 | Move database and storage | Intentionally later | Only when this computer is no longer enough |
