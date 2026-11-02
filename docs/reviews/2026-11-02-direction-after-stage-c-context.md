# Second-opinion context pack — direction after stage C

**Prepared by:** the Architect, 2026-11-02. **Committed before Phase A runs** (`SECOND_OPINION.md`, T1 and T3).
**Requested by the owner, verbatim:** *"Get a 2nd opinion from Sol 6.1 for all important topics."*
**Your snapshot has no network and no `.git`.** The two outside projects are described here; you cannot open them. A missing `.git` is a known limit of this lane: state it once and carry on. It is not a blocker for this review.

## The problem in plain words

StorageGenie is a household catalog: Pantry first, Wardrobe second. The owner has now named two outside projects as references and wants the look of one of them. The Architect must decide how the look lands, what to build after stage C, which outside features are worth adding, how to make product images, and whether the migration just built is fit to deploy.

## Evidence

**Owner, 2026-11-02, verbatim:** *"The inspiration for our project was this github repo "https://github.com/tandpfun/wardrobe"."* · *"I also want to use the theme and design of the tandpfun project, as I think its clean and visually attractive."*

**Measured state of this project:** the live catalog holds 7 assets, and why is not known (`docs/ROADMAP.md`, stage C). The owner has not yet used the Pantry flow on real items; the flow fixes *"have not been used live"* (`docs/releases/2026-11-02-sg270.md`). Split and merge fail on the live database until the Q5 migration deploys.

### tandpfun/wardrobe, read from its source at its default branch, not run

MIT, 45 files, JavaScript, a JSON file as its database, one person. Last pushed 2026-07-16.

- **Look (`src/styles.css`):** `--paper: #f4f0e8`, `--ink: #191919`, `--muted: #66625d`, `--line: #cfc8bc`, `--accent: #6e302e`; font Instrument Sans Variable; `border-radius: 0` on the filter nav; uppercase labels with `letter-spacing` .04–.12em; grid `repeat(auto-fill, minmax(165px, 1fr))`; 0 matches for `prefers-color-scheme`, `.dark` or `data-theme`; 16 rules with `font-size` 9, 10 or 11 px.
- **Owner's screenshot:** an "80 PIECES" count, joined square filter tabs, borderless transparent garment cutouts on paper, a right-hand panel with a modeled photo, name, category, colours from the image, detail tags, Delete, Cancel and Save, and a round add button. It shows an Outfits tab that the published `App.jsx` does not contain (0 matches for "outfit").
- **Images (`scripts/import-job-api.mjs`, `.agents/skills/`):** a vision model finds up to 8 garments in a photo with bounding boxes; an image model regenerates each garment on a solid chroma colour; a non-AI step removes that colour, with a tolerance slider and a spill check; the owner approves or regenerates with a written direction at each step; an optional second model call makes a modeled photo from a reference photo of the person. Its skill says to prefer omitting a detail over inventing logos, text or seams, and to hold items that cannot be recovered.

### wardrowbe, read from its README, marketing site, source file names and a walk of its sample-data demo

MIT, Python and Next.js, about 818 stars, self-hosted or paid cloud. No suggestion, scan or try-on was run. Not opened: review screen, notification, family and billing settings. The site's own marketing figures are unverified and not used.

Features seen: daily outfit suggestions from weather, occasion and notes, with scheduled notifications (ntfy, Mattermost, email); scan before you buy, by photo or link; a gap report counting outfits per occasion; build an outfit around one piece; pairings; wear log with calendar; never-worn and most-worn lists; colour distribution; review items one at a time, archive with undo; wash tracking; add an item by typing; learned colour and occasion preferences from accept, skip and ratings; style settings; a family feed where household members rate each other's outfits; XP and streaks; partner shop links with commission; credits and billing for try-on; optional `rembg` background removal.

### Our own constraints

`docs/ROADMAP.md` holds the stages. Row 16: restore from backup is missing and belongs to stage D. Stage D's *"Blocker: image generation is parked on owner answers about the provider"*. `backend/app` and the screens hold no wardrobe or outfit feature (the roadmap's search). `frontend/src/theme/tokens.css` is the theme: `--primary: 2 41% 30.6%`, which converts to `#6e302e` (derived by hand); `--font-sans` is the system font; it has a `.dark` theme. A search of `frontend` found neither Fraunces nor DM Sans.

## What binds it

Not reopened: no local models on the live server (D-1024-15) · provider and model are the owner's choice (D-1024-16) · never a purchase (Q27) · no sign-in by design (roadmap row 17) · sending a person's photo to a cloud AI is the owner's privacy call (Q24) · spending is frugal with no fixed cap (Q16) · the 20 MB upload cap · English unless Romanian is needed (Q28). The tandpfun theme itself is the owner's choice; **how far and when** is the question.

## Questions and options, without a pick

**Q1 — How the theme lands.** (a) whole app in one slice; (b) tokens, font and shapes everywhere, full design on the catalog, item panel and Pantry view; (c) Pantry view only. Also say: what happens to the dark theme, the small type, and how an uneven phone photo should look in a grid designed for cutouts, before any cutouts exist.

**Q2 — What comes after stage C.** (a) shared images (stage D), then Wardrobe (E); (b) straight to Wardrobe, with images inside it; (c) pause Pantry now and start Wardrobe.

**Q3 — Which features to add.** Candidates, with the first stage each could join:
V1 one photo becomes many items (D) · V2 install on the phone (D) · V3 no invented details (D) · V5 approve or regenerate each image (D) · W1 check before you buy (D, E) · W2 review one item at a time (C or D) · W3 used and unused lists (D or E) · W4 phone push by ntfy (D) · W5 add by typing (D) · V4 colour as data (E) · V6 free-form tags (E) · V7 outfit rules with a stated reason, no duplicates, varied pieces (E) · W6 wear log (E) · W7 gap report (E or F) · W8 build around one piece (E) · W9 learning from answers (E) · W10 style settings (E) · W11 richer garment fields (E) · W12 wash tracking (E).
Not adopted so far: family feed, partner links, XP and streaks, credits and billing, local AI, eight languages.
Say which are mis-placed, over-valued or missing, and what the smallest first set is. **Which of these does real use need to justify first?**

**Q4 — How product images get made.** (a) a cloud cut-out of the owner's photo with a fixed backdrop and non-AI shadow (`docs/ROADMAP.md`, stage D); (b) regenerate each item with an image model, then remove a chroma colour (tandpfun); (c) cut-out first, and regeneration only where the photo is poor, with approval. Name which risks each carries for accuracy: a pantry label or a garment's real detail being changed. Name no provider or model as a decision.

**Q5 — Is SG-279 fit to deploy?** One migration widening `ck_candidate_state`, already built and approved in principle after an earlier review (`docs/worklogs/SG-278_report.md`). Read the built code and its evidence. Its report says Alembic *"Will assume non-transactional DDL"* on this SQLite. The rider's approved recovery states: before the migration, the old image restarts; during it with the app stopped, the backup is restored; after the new image starts, back to the owner before any restore; a failed recovery leaves the app stopped and goes to the owner. Options: (a) deploy as built; (b) fix something first, naming it; (c) add a rider step, naming it.

## Where it lives

| Question | Read |
|---|---|
| Q1 | `frontend/src/theme/tokens.css`, `frontend/src/routes/theme-adoption.test.tsx`, `frontend/src/components/catalog/ProductCard.tsx`, `frontend/src/components/shell/ItemInspectorDrawer.tsx`, `frontend/src/routes/CatalogPage.tsx` |
| Q2, Q3 | `docs/ROADMAP.md`, `docs/research/2026-10-30-requirements-recalibration.md`, `docs/backlog.md` |
| Q4 | `docs/ROADMAP.md` stage D, `backend/app/services/scene/openrouter.py`, `docs/backlog.md` Context Scene row |
| Q5 | `backend/alembic/versions/20261102_sg279_candidate_state.py`, `backend/app/services/candidates.py` (`Candidate`), `backend/tests/test_sg279_candidate_state.py`, `backend/tests/test_sg279_rehearsal.py`, `docs/worklogs/SG-279_report.md`, `docs/worklogs/SG-279_rehearsal.log`, `docs/worklogs/SG-278_report.md`, `docker-compose.yml`, `backend/app/server.py` |

## What would make the whole approach wrong

Name the observation, if any, under which this whole direction is a mistake: for example, building more features and a new look before anyone has used the product on real items.
