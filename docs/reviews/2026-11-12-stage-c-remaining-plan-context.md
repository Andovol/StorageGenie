# Second-opinion context pack — the rest of stage C (the first real Pantry)

**Prepared by:** the Architect, 2026-11-12. **Asked for by the owner, 2026-11-12:** *"What is the plan going forward? Can you review the plan using the 2nd decision model?"* Contract 0.59.0 (D30) also requires a blind review of plan-level choices at L3 (dropping, reordering or rescoping planned work).
**Blindness:** **blind by instruction.** The Architect's current plan is already written in `STATE.md`, `docs/decisions/` and the packets `docs/packets/SG-301*` and `docs/packets/SG-303*`. **Do not open those files**, nor `docs/reviews/*` other than this one. Everything you need from them is quoted below.

## The problem in plain words

Stage C's goal (`docs/ROADMAP.md` §C): *"One styled Pantry you can use end to end: see it, use it up, quantities quick to change"*, ending when *"the owner uses it on one real shelf, then checks it again after ordinary household use."* The Pantry screen is built and gated but not live. Four pieces of work remain before the owner's shelf trial. The question is their **order, their slicing, and when each is deployed**, given this lane's measured limits.

## The evidence, verbatim

**Work remaining** (from the Architect's records; each a separate slice unless the options say otherwise):

| ID | What | State |
|---|---|---|
| SG-302 | Pantry dark-mode warning text to ≥ 4.5:1 contrast (today ≈1.95:1), every text pair measured light and dark, the empty state's "Capture" made a link, dark screenshots retaken | **Running now** on Muse 1.3 `xhigh` |
| Rider | Deploy SG-273 (Pantry view, rated 78 with a trust flag on one false screenshot, fixed and re-proven by SG-300), SG-300 (Pantry design fixes, 92) and SG-302 together | Packet drafted |
| SG-301 | Design pass on the older screens: remove developer text from Inbox, Expiry page, Catalog, item panel and asset page (raw ids, enum words like `product` / `Source Only`, `If-Match`, sentences about the code); the tandpfun look on the catalog and item panel; the Instrument Sans font through one new npm package, pinned (owner-approved D31) | Packet drafted |
| SG-304 | F9 and F10 from the capture walk (`docs/worklogs/SG-269_findings.md`): a same-name warning at capture; a duplicate photo offers to update the existing item | Not written |
| Trial | The owner uses the Pantry on one real shelf, then again after ordinary use | After the above |

**Standing rules that bind (not reopened):**
- *"Deploy every app-changing slice as its own slice, right after it is rated, and deploy the live app before every close"* (`AGENTS.md`, Close-out).
- *"Unrated or blocked work stops the deploy instead of shipping silently."*
- Model rotation, owner D25: *"we use the model rotation as suggested by Launcher desk, one slice using Haiku the next with Muse and so on."* SG-302 is Muse; the owner named Haiku 5.5 `high` for the rider. The next slot after the rider is Muse.
- The owner, 2026-11-10 and 2026-11-12: *"design, look and feel are very important, so hold every screen to that."*
- Slices on one project run one at a time; the lane's run budget is 2100 s; Muse packets carry a hard stop at 1300 s.

**Measured slice durations on this lane** (`docs/coder-profiles.md`, rows quoted):

| Slice | Model | Kind | Elapsed | Rating |
|---|---|---|---|---|
| SG-271 run 1 | muse-1.3 xhigh | build, backend + 4 screens | 2100 s (killed) | unrated, retried |
| SG-271 run 2 | muse-1.3 xhigh | same, retry | ~420 s | 90 |
| SG-272 | muse-1.3 xhigh | lifecycle + 4 screens + quantities | ~1240 s (stopped by its rule) | 85 |
| SG-273 | muse-1.3 xhigh | new screen + gate + screenshots | 1277 s | 78 FLAG:TRUST |
| SG-300 | haiku-5-5 high | screen design fixes + gate + shots | ~964 s | 92 |
| SG-299 | haiku-5-5 high | deploy rider | 128 s | 96 |

The Architect's estimate for SG-301 as drafted: ≈1250 s (`UNVERIFIED`), against Muse's 1300 s stop.

**The live state:** release `release-sg299` (2026-11-10) serves stage C's lifecycle work (gone, put back, quantities); none of it has been used live yet. The Pantry route `/pantry` exists only in the gated, undeployed code.

## Where it lives

- `docs/ROADMAP.md` §C and §D — the stage's definition and what follows.
- `docs/worklogs/SG-269_findings.md` — F9, F10 and the older-screen faults.
- `docs/worklogs/SG-300_audit.md` — the latest Pantry audit.
- `docs/coder-profiles.md` — model rows (the profile prose is fine to read).
- `frontend/src/routes/{PantryPage,InboxPage,ExpiryPage,CatalogPage,AssetDetailPage}.tsx`, `frontend/src/components/shell/ItemInspectorDrawer.tsx` — for sizing SG-301.

## What binds it

`G-A7` (simplicity), `G-K1` (forks to the owner), the standing deploy rule, D25 (rotation), D31 (the font package), D18 (the tandpfun look everywhere, the full design on catalog, item panel and Pantry).

## The questions and options — without the Architect's pick

**Q1 — Order of the remaining work.**
- **O1a:** SG-302 → rider (Pantry live) → SG-301 → its rider → SG-304 → its rider → trial.
- **O1b:** SG-302 → SG-301 → one rider for everything → SG-304 → rider → trial.
- **O1c:** SG-302 → rider (Pantry live) → the owner's trial starts at once; SG-301 and SG-304 follow, informed by what the trial shows.
- **O1d:** SG-304 before SG-301 (function before polish).

**Q2 — SG-301's size.**
- **O2a:** one slice as drafted (font, developer text on five screens, catalog and item-panel look, contrast table, 8 screenshots).
- **O2b:** two slices: (i) font + developer text, (ii) the catalog and item-panel look.
- **O2c:** one slice, but on the Haiku slot instead of Muse (swap rotation positions; the rotation is the owner's choice, D25).

**Q3 — Anything the plan misses** before the owner's shelf trial (for example: a way for the owner to reach `/pantry` from the menu, real-photo checks, a restore-from-backup proof before real data goes in — roadmap §D lists restore under stage D).

## What to return (Phase A)

Per question: your pick and why, with evidence (file:line, a quote, a measurement); an option the list misses; the riskiest unverified premise. List every file you read beyond those named here. Keep the report under 150 lines.
