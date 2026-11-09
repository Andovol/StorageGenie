# StorageGenie — State

## RESUME — closed 2026-11-07 (rules 0.58.0, `AGENTS.md:4`)

**The product goals are reset and the plan is `docs/ROADMAP.md`:** a beautiful catalog of everything owned, in modules, Pantry first, Wardrobe second. Owner words: `docs/decisions/2026-10-30-session-approvals.md`. **Stage A is live** (the three date fixes). **The look changed:** the tandpfun Wardrobe theme replaces Linen Shelf (D18: colours, font and shapes everywhere; the full design on catalog, item panel and Pantry view; keep dark mode, enlarge the small type, check with real photos, measure contrast). **Design quality is a first-class requirement of every theme and screen slice (owner).** D17–D22 are decided and in the roadmap; order stays C, D, E. **Stage C, the first real Pantry, is approved and in progress** (*"d14 ok"*, L3).

**The next step: SG-272 on Muse 1.3 Contributor `xhigh`, fix-first items below** (the owner's rotation, D25: builder slices alternate; pointer: SG-296 was Haiku, so SG-272 is Muse). **SG-271 is live** (`docs/releases/2026-11-09-sg296.md`). Packet contract line: copy the last rider's — the lane denies the contract folder (SG-296 I1). **SG-279 is live** (`docs/releases/2026-11-07-sg295.md`): split and merge are storable; their first live use is the owner's. Way back: image `storagegenie-backend:recovery-sg270` plus backup `data/db/SG-295-backup-20261107T214652Z.db`. Each audit adds a row to `docs/coder-profiles.md`; a model issue goes to the owner and the desk (D25). No new provider or image spend in stage C.

**Packets carry, literally:** `git push origin automation` and a hash-equality criterion; a rider also tags the image it serves `storagegenie-backend:release-<slice>`, and never probes rights on a real object.

**Ordered work for stage C, from the walk (`docs/worklogs/SG-269_findings.md`, disposition in `SG-269_audit.md`):**

1. **Done:** SG-270 and SG-275 live (2026-11-02); SG-279's candidate-state migration live (SG-295, 2026-11-07).
2. **Done:** SG-271 rated 90 (Muse, retry after a budget kill), live by SG-296 (96, Haiku) on 2026-11-09.
3. **SG-272, gone, put back, quantities, then its rider:** per the roadmap's stage C, with F3 and F13. **Fix first, from SG-271's audit:** I1 a cleared perishable date (`clear_expiry_date` writes an accepted null) must stay on Unresolved as *No date* — key the quiet dateless count to the Non-perishable classification only, with a test that clears a food date; I2 SG-271's new notes at body size, not 12 px (D18).
4. **SG-273, the Pantry view, then its rider:** per the roadmap, with F9 and F10, **and screenshots of SG-271's screens** (Review committed candidate, asset page proposed date and shelf life, Expiry page, Inbox step row), light and dark. Headless Chrome wrote a 5169-byte PNG on the box in SG-271 run 1 (`SG-271.dbg`) — possibly a blank page; prove a real screen first. Screenshots go after the gate, never as an optional tail goal.
5. **The owner tries it on one real shelf**, then again after ordinary household use.

**Owed:** the lane's `.contract/` lacks `CODERS.md`, `SECOND_OPINION.md` and `coder_models.tsv`, and the Coders are denied `crontab` and the contract folder (filed in the 2026-11-07 END report, issue 62); read-only checks of WAL databases go on copies (SG-295); amend the blueprint to the new direction (`inception/generic_asset_catalog_expiry_tracker_blueprint.md`; only its §1.4 non-goal is marked so far); a read-only review run keeps only 200 lines of its report, so keep review reports short.

**Live:** container `0c4462ee`, image `dcc67781` (`release-sg296`), schema head `20261102_sg279_candidate_state`; `docs/releases/2026-11-09-sg296.md` owns the detail. The classify move and the flow fixes have not been used live; the first real use is the owner's. Actual-cost logging and the consent gate are live.

**Owner decisions:** D9, D10–D14 and all requirement answers: `docs/decisions/2026-10-30-session-approvals.md`. Earlier: `docs/decisions/`. **D7 is done.** Row 14 of the roadmap stays narrowed by the owner (D-1024-17, -18, -19): no fallback yet, cloud only, log costs, predict none. The app's local barcode-and-text reader stays (D-1024-18 is about what we build).

**Parked:** email until the owner binds SMTP credentials (D-1024-2) · the full `mypy app` reds and the one pre-existing `eslint` error in `App.household-nav.test.tsx` · `docs/backlog.md` W3–W6.

**Rules for reports:** every report ends with next steps and starts step 1; the parked list is never shown. **Every rated slice sends the owner one report as soon as it is rated** (D-1024-14), and that report also states the roadmap position.

**Standing:** every app-changing slice is deployed as its own slice, right after it is rated; before every close, deploy the live app and record a release. Unrated or blocked work stops the deploy instead of shipping silently. **Every 🟠 or 🔴 decision item, and a 🟡 on the live host, dispatch key, app database or owner's data, goes through the two-phase second opinion before the owner sees it** (D-1024-10; reviewer in `AGENTS.md`). **No local models on the live server** (D-1024-15). **Model and provider choices are the owner's** (D-1024-16). **Ask before creating any artifact** (`AGENTS.md`).

**Where things live:** product plan `docs/ROADMAP.md`; waiting items `docs/backlog.md`; past work git history and `docs/ratings.md`; decisions `docs/decisions/`; reviews `docs/reviews/`; packets and worklogs under `docs/`. Session reports: Launcher issue 62. Context size: the desktop app's `get_usage` tool.
