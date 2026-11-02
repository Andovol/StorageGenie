# StorageGenie — State

## RESUME — closed 2026-11-02 (rules 0.56.0, `AGENTS.md:4`)

**The product goals are reset and the plan is `docs/ROADMAP.md`:** a beautiful catalog of everything owned, in modules, Pantry first, Wardrobe second. Owner words: `docs/decisions/2026-10-30-session-approvals.md`. **Stage A is live** (the three date fixes). **The look is chosen** (Linen Shelf, D13). **Stage C, the first real Pantry, is approved and in progress** (*"d14 ok"*, L3).

**First thing next session, put to the owner (arose after the close was requested, so not asked yet) — D15, 🟡 Approve: the larger stage C.** I told the owner roughly 3–5 builder runs and that I would come back if the fixes grew beyond small repairs. The walk found three dead ends, so the honest count is four build slices plus their deploys, about 8 runs (`UNVERIFIED — my estimate`), still no new provider or image spend. Recommended: **approve**, because *the dead ends explain more than the look does and the Pantry cannot work on top of them*.

**Ordered work for stage C, from the walk (`docs/worklogs/SG-269_findings.md`, disposition in `SG-269_audit.md`):**

1. **SG-270, flow fixes, then its rider:** F1 list a job's candidates in the inbox with a Review link, and prove whether AI-read items are also unreachable (audit I1); F2 unblock an AI-no-date candidate (recommended: accept the candidate and carry the date task to the new item's page; a blind second-opinion pass first, since no review covered it); F6 link asset date tasks to the item's page and hide Resolve where it is always refused; add the missing link from review to the item (SG-262 audit I1). Pick up `docs/backlog.md` W8.
2. **SG-271, carry the AI's work through, then its rider:** F4 keep the proposed date on classify and offer Accept; F5, F12 use the proposed category; F7 rename one "category" control; F8 stop a deliberately dateless item nagging; F11 if cheap.
3. **SG-272, gone, put back, quantities, then its rider:** per the roadmap's stage C, with F3 and F13.
4. **SG-273, the Pantry view, then its rider:** per the roadmap, with F9 and F10. Say in the packet how screens get seen (Chrome exists on the box, no driver).
5. **The owner tries it on one real shelf**, then again after ordinary household use.

**Owed:** amend the blueprint to the new direction (`inception/generic_asset_catalog_expiry_tracker_blueprint.md`; only its §1.4 non-goal is marked so far); a read-only review run keeps only 200 lines of its report, so keep review reports short.

**Live:** container `c1beebf9`, image `3e0d49de`, schema head `20261023_sg233_reminder`; `docs/releases/2026-11-02-sg262.md` owns the detail. The new classify move has not been used live; the first real use is the owner's. Actual-cost logging and the consent gate are live.

**Owner decisions:** D9, D10–D14 and all requirement answers: `docs/decisions/2026-10-30-session-approvals.md`. Earlier: `docs/decisions/`. **D7 is done.** Row 14 of the roadmap stays narrowed by the owner (D-1024-17, -18, -19): no fallback yet, cloud only, log costs, predict none. The app's local barcode-and-text reader stays (D-1024-18 is about what we build).

**Parked:** email until the owner binds SMTP credentials (D-1024-2) · the full `mypy app` reds and the one pre-existing `eslint` error in `App.household-nav.test.tsx` · `docs/backlog.md` W3–W6.

**Rules for reports:** every report ends with next steps and starts step 1; the parked list is never shown. **Every rated slice sends the owner one report as soon as it is rated** (D-1024-14), and that report also states the roadmap position.

**Standing:** every app-changing slice is deployed as its own slice, right after it is rated; before every close, deploy the live app and record a release. Unrated or blocked work stops the deploy instead of shipping silently. **Every 🟠 or 🔴 decision item, and a 🟡 on the live host, dispatch key, app database or owner's data, goes through the two-phase second opinion before the owner sees it** (D-1024-10; reviewer in `AGENTS.md`). **No local models on the live server** (D-1024-15). **Model and provider choices are the owner's** (D-1024-16). **Ask before creating any artifact** (`AGENTS.md`).

**Where things live:** product plan `docs/ROADMAP.md`; waiting items `docs/backlog.md`; past work git history and `docs/ratings.md`; decisions `docs/decisions/`; reviews `docs/reviews/`; packets and worklogs under `docs/`. Session reports: Launcher issue 62. Context size: the desktop app's `get_usage` tool.
