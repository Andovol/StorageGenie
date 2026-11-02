# StorageGenie — State

## RESUME — closed 2026-11-02 (rules 0.56.0, `AGENTS.md:4`)

**The product goals are reset and the plan is `docs/ROADMAP.md`:** a beautiful catalog of everything owned, in modules, Pantry first, Wardrobe second. Owner words: `docs/decisions/2026-10-30-session-approvals.md`. **Stage A is live** (the three date fixes). **The look changed:** the tandpfun Wardrobe theme replaces Linen Shelf (D18: colours, font and shapes everywhere; the full design on catalog, item panel and Pantry view; keep dark mode, enlarge the small type, check with real photos, measure contrast). **Design quality is a first-class requirement of every theme and screen slice (owner).** D17–D22 are decided and in the roadmap; order stays C, D, E. **Stage C, the first real Pantry, is approved and in progress** (*"d14 ok"*, L3).

**The next step, the first item to put to the owner: the recovery image.** SG-280 stopped safely before touching the live app: its own tag probe, ordered by the packet, appears to have removed the old image (`docs/worklogs/SG-280_audit.md`). Run a two-phase review (SG-284, SG-285), then bring **D23: recommended, make the recovery image with `docker commit --pause=false d972bc75 storagegenie-backend:recovery-sg270`, prove it by export comparison, then rerun the rider as SG-286** with the real-object tag probe removed and `--user` dropped. The alternative, a rebuild from `release-2026-11-02-sg270`, is not the same bytes. Why: a stop rule fired on a sensitive surface, so it returns to the owner. No new provider or image spend in stage C.

**Packets carry, literally:** `git push origin automation` and a hash-equality criterion; a rider also tags the image it serves `storagegenie-backend:release-<slice>`, and never probes rights on a real object.

**Ordered work for stage C, from the walk (`docs/worklogs/SG-269_findings.md`, disposition in `SG-269_audit.md`):**

1. **SG-270, flow fixes: rated 91; SG-275, its repair: 97; rider SG-276: 97. Live** (`docs/releases/2026-11-02-sg270.md`). **Split and merge cannot work live:** the live `candidate` table refuses those states (`SG-276_audit.md` I1). **Fix, before SG-271: SG-279 is built and on `automation` (rated 90; SG-281 97); the rider reruns per the next step.** Base its packet on `docs/packets/SG-280-deploy-rider-candidate-state-migration.md`, which already holds the owner's recovery states and D20's rehearsal. On the copy, SG-280 proved the upgrade, the interrupted state, the restore and the refusal; **the old image reading a restored file is still unproved.** Builds run on Muse 1.3 Contributor, xhigh (`AGENTS.md`).
2. **SG-271, carry the AI's work through, then its rider:** `needs_evidence` can open a false date task (SG-270 report); a candidate already committed links to its item, including on reload, and stops offering decisions (SG-275 audit I1); F4 keep the proposed date on classify and offer Accept; F5, F12 use the proposed category; F7 rename one "category" control; F8 stop a deliberately dateless item nagging; F11 if cheap.
3. **SG-272, gone, put back, quantities, then its rider:** per the roadmap's stage C, with F3 and F13.
4. **SG-273, the Pantry view, then its rider:** per the roadmap, with F9 and F10. Say in the packet how screens get seen (Chrome exists on the box, no driver).
5. **The owner tries it on one real shelf**, then again after ordinary household use.

**Owed:** read the Launcher desk's reply on trimming cold-start context (issue 62; none by 2026-11-02 18:15 UTC); amend the blueprint to the new direction (`inception/generic_asset_catalog_expiry_tracker_blueprint.md`; only its §1.4 non-goal is marked so far); a read-only review run keeps only 200 lines of its report, so keep review reports short.

**Live:** container `d972bc75`, image `96a66241`, schema head `20261023_sg233_reminder`; `docs/releases/2026-11-02-sg270.md` owns the detail. The classify move and the flow fixes have not been used live; the first real use is the owner's. Actual-cost logging and the consent gate are live.

**Owner decisions:** D9, D10–D14 and all requirement answers: `docs/decisions/2026-10-30-session-approvals.md`. Earlier: `docs/decisions/`. **D7 is done.** Row 14 of the roadmap stays narrowed by the owner (D-1024-17, -18, -19): no fallback yet, cloud only, log costs, predict none. The app's local barcode-and-text reader stays (D-1024-18 is about what we build).

**Parked:** email until the owner binds SMTP credentials (D-1024-2) · the full `mypy app` reds and the one pre-existing `eslint` error in `App.household-nav.test.tsx` · `docs/backlog.md` W3–W6.

**Rules for reports:** every report ends with next steps and starts step 1; the parked list is never shown. **Every rated slice sends the owner one report as soon as it is rated** (D-1024-14), and that report also states the roadmap position.

**Standing:** every app-changing slice is deployed as its own slice, right after it is rated; before every close, deploy the live app and record a release. Unrated or blocked work stops the deploy instead of shipping silently. **Every 🟠 or 🔴 decision item, and a 🟡 on the live host, dispatch key, app database or owner's data, goes through the two-phase second opinion before the owner sees it** (D-1024-10; reviewer in `AGENTS.md`). **No local models on the live server** (D-1024-15). **Model and provider choices are the owner's** (D-1024-16). **Ask before creating any artifact** (`AGENTS.md`).

**Where things live:** product plan `docs/ROADMAP.md`; waiting items `docs/backlog.md`; past work git history and `docs/ratings.md`; decisions `docs/decisions/`; reviews `docs/reviews/`; packets and worklogs under `docs/`. Session reports: Launcher issue 62. Context size: the desktop app's `get_usage` tool.
