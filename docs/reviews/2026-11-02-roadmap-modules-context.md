# Second-opinion context pack — the module roadmap

**Prepared by:** the Architect, 2026-11-02. **Committed before Phase A runs** (`SECOND_OPINION.md`, T1/T3, `D555`).
**Decision:** how to build the owner's new product direction: the order of the work, and the design choices inside it.
**Why it matters now:** the owner reset the product goals. The roadmap is being rewritten, and the next large stage touches the app database, a declared sensitive surface.

`docs/ROADMAP.md` at this commit is the OLD roadmap, bannered as under recalibration. Use it only as the record of what is built.

## The evidence, verbatim

**Owner's product direction, 2026-10-30:**

> "No, it is more than just an app that reminds about the expiry. It is also a catalog that you can use to track the items you own, from food items to clothing. For food items you would like to understand which ingredients you have, which you should use as they are closer to expiry, but also just to give you an overview of what you have in a pantry, presented in a very nice way. The presentation is everything, the app should have a beautiful design and be very easy to use. It should inspire the users creativity. For clothes, presentation is extremely important to help create outfits and also see how different items could fit together. AI image generation, AI suggestions and recommendations play a key role. The modules are important, because different categories have a different focus from the app and different actions and handling. Also, the app should enrich the content around a scan product (like retrieve from the web specifications, usage, etc.)."

**Owner's answers:** rounds 2 and 3, D10 and D12, verbatim with their reading, are in `docs/decisions/2026-10-30-session-approvals.md` (second-session sections). The questions and research are in `docs/research/2026-10-30-requirements-recalibration.md`.

**The audit, same file:** "the live census (SG-259 G4) holds 7 assets, 10 candidates, 39 provider calls; about 1 in 5 of SG-200–SG-265 changed the product (derived from the slice titles)".

**Measured in the code on 2026-11-02 (hypotheses; check them):**

- `backend/app/models/asset.py:29-30` has `quantity` and `unit` columns.
- `backend/app/services/lifecycle.py:25-30` has the statuses DRAFT, PENDING_REVIEW, ACTIVE, ARCHIVED, DISPOSED, MERGED.
- `backend/app/plugins/expiry_tracker.py:27-31`: `PLUGIN_ID = "expiry-tracker"`, `FIELD_PREFIX = "plugin:expiry-tracker/"`. Live assertions carry this prefix in their field paths.
- `backend/app/plugins/descriptor.py:1-12`: "Defining a new domain is a registration, never a migration (blueprint §8)."
- A search of `backend/app` and `frontend/src` for outfit, wardrobe, garment and clothing found one hit: a comment naming a "wardrobe-flow" drawer (`frontend/src/components/shell/ItemInspectorDrawer.tsx:51`).
- `frontend/src/components/catalog/ProductCard.tsx:9`: "cutout/scene URLs are mock-only until the S3-era image derivation lands."
- `backend/app/services/scene/openrouter.py` is a scene-render client with no API route using it (search of `backend/app/api` for "scene": no hit). `docs/backlog.md`, the Context Scene row, records it as parked on owner answers.

## Where it lives

| What | Where |
|---|---|
| Owner's words | `docs/decisions/2026-10-30-session-approvals.md` |
| Research and questions | `docs/research/2026-10-30-requirements-recalibration.md` |
| What is built | `docs/ROADMAP.md` (rows 1–18 only) |
| Parked work | `docs/backlog.md` |
| Plugin contract | `backend/app/plugins/descriptor.py`, `registry.py`, `expiry_tracker.py` |
| Consumers of the expiry plugin | `backend/app/services/expiry_engine.py`, `opened_countdown.py`, `reminders/service.py`, `planning/service.py`, `chat/service.py`, `analytics/service.py` |
| Item statuses | `backend/app/services/lifecycle.py`, `backend/app/api/v1/assets.py` |
| Blueprint | `inception/generic_asset_catalog_expiry_tracker_blueprint.md` |
| Theme | `frontend/src/theme/tokens.css` |

## What binds it

**Rules:** `G-A1`, `G-A6`, `G-A7`, `G-A9`, `G-A10`, `G-K2`; the project's sensitive surfaces (stored photos and files, the app database, the dispatch key and host) go to the owner.

**Decisions already taken, not reopened:** Pantry first, Wardrobe second (Q6). Expiry is a shared feature that modules switch on (Q21). Quantity is a count or amount with a unit; one tap takes off 1; "gone" moves to history, not deletion (Q22). Warm-neutral house photo style, original kept (Q23). Separate wardrobes, shared pantry (Q26). Suggestions may include things to buy, never a purchase (Q27). A design mood-board page comes next (Q29). The three D7 fixes go first (D10, D11). The focused imagery and creativity set (D12). No local models on the server (D-1024-15). Provider and model choices are the owner's (D-1024-16). Launcher L3 process stays (D9).

## The options as the Architect sees them (no pick shown)

**R-A — order after the D7 fixes and the mood board:**
- **A1:** Pantry core (modules, expiry split, quantities), then Pantry presentation, then Wardrobe.
- **A2:** Presentation first on the existing catalog, then the module split, then Wardrobe.
- **A3:** One thin end-to-end Pantry slice (one styled view over real items, with quantities), then widen, with the split done only as far as it needs.

**R-B — what a module is in the code:**
- **B1:** Each module is a registered plugin in the existing registry.
- **B2:** A stored module field on each item.
- **B3:** The module is derived from the item's accepted category, through a category-to-module map.

**R-C — the live field paths under the expiry split:**
- **C1:** Keep `plugin:expiry-tracker/…` paths as they are; the shared feature keeps reading them; no data migration.
- **C2:** Migrate paths to a new name in a data migration.
- **C3:** New items use new paths; readers accept both.

**R-D — what "gone" is:**
- **D1:** The existing ARCHIVED status.
- **D2:** The existing DISPOSED status.
- **D3:** A new status.
- **D4:** Quantity reaching zero, with no status change.

**R-E — whose wardrobe, given no sign-in by design (roadmap row 17):**
- **E1:** A person field on the item, chosen by a picker.
- **E2:** A separate household per person.
- **E3:** Add sign-in.

**R-F — how house-style photos get made (vendor and model stay the owner's):**
- **F1:** A cloud image model restyles each photo.
- **F2:** A cloud service cuts the subject out; the backdrop and shadow are a fixed composite made without AI.
- **F3:** A cloud image model only where a photo is poor; other photos are shown as taken.

## What would make the whole approach wrong

If the modules bring no difference the owner would see, a catalog with better screens is enough, and the split is busywork. If the existing plugin contract cannot carry a second domain, stage sizes are wrong. If house-style images cost too much per item for a frugal household, the presentation stage needs another shape. With 7 assets live, the app may be missing something more basic than any of this: why has the owner not put more items in?
