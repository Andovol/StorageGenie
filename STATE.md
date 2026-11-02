# StorageGenie — State

## RESUME — closed 2026-11-02 (rules 0.56.0, `AGENTS.md:4`)

**The product goals are reset and the plan is `docs/ROADMAP.md`:** a beautiful catalog of everything owned, in modules, Pantry first, Wardrobe second. Owner words: `docs/decisions/2026-10-30-session-approvals.md`. **Stage A is live** (the three date fixes). **The look is chosen** (Linen Shelf, D13). **Stage C, the first real Pantry, is approved and in progress** (*"d14 ok"*, L3).

**The next step is SG-279, approved by the owner (D16, *"D16 - ok."*):** write its packet and dispatch it. Stage C is about 8 runs plus D16's 2 (`UNVERIFIED — my estimate`), no new provider or image spend.

**Ordered work for stage C, from the walk (`docs/worklogs/SG-269_findings.md`, disposition in `SG-269_audit.md`):**

1. **SG-270, flow fixes: rated 91; SG-275, its repair: 97; rider SG-276: 97. Live** (`docs/releases/2026-11-02-sg270.md`). **Split and merge cannot work live:** the live `candidate` table refuses those states (`SG-276_audit.md` I1). **Fix, before SG-271: build SG-279, then rider SG-280.** The design is R1–R6 in `docs/packets/SG-278-second-opinion-b-critique-state-constraint.md`, plus the accepted corrections in the SG-277/278 row of `docs/reviews/review-ledger.md`; the build packet needs nothing else. SG-280 opens with a non-mutating check of the lane's rights and a live object inventory; a denial stops before anything changes. **The owner's approval names the recovery states:** before the migration, the old image restarts; during it with the app stopped, the backup is restored; after the new image starts, back to the owner before any restore; a failed recovery leaves the app stopped and goes to the owner. Builds run on Muse 1.3 Contributor, xhigh (`AGENTS.md`).
2. **SG-271, carry the AI's work through, then its rider:** `needs_evidence` can open a false date task (SG-270 report); a candidate already committed links to its item, including on reload, and stops offering decisions (SG-275 audit I1); F4 keep the proposed date on classify and offer Accept; F5, F12 use the proposed category; F7 rename one "category" control; F8 stop a deliberately dateless item nagging; F11 if cheap.
3. **SG-272, gone, put back, quantities, then its rider:** per the roadmap's stage C, with F3 and F13.
4. **SG-273, the Pantry view, then its rider:** per the roadmap, with F9 and F10. Say in the packet how screens get seen (Chrome exists on the box, no driver).
5. **The owner tries it on one real shelf**, then again after ordinary household use.

**Owed:** read the Launcher desk's reply on trimming cold-start context (asked in issue 62's last END report, at the owner's request); amend the blueprint to the new direction (`inception/generic_asset_catalog_expiry_tracker_blueprint.md`; only its §1.4 non-goal is marked so far); a read-only review run keeps only 200 lines of its report, so keep review reports short.

**Live:** container `d972bc75`, image `96a66241`, schema head `20261023_sg233_reminder`; `docs/releases/2026-11-02-sg270.md` owns the detail. The classify move and the flow fixes have not been used live; the first real use is the owner's. Actual-cost logging and the consent gate are live.

**Owner decisions:** D9, D10–D14 and all requirement answers: `docs/decisions/2026-10-30-session-approvals.md`. Earlier: `docs/decisions/`. **D7 is done.** Row 14 of the roadmap stays narrowed by the owner (D-1024-17, -18, -19): no fallback yet, cloud only, log costs, predict none. The app's local barcode-and-text reader stays (D-1024-18 is about what we build).

**Parked:** email until the owner binds SMTP credentials (D-1024-2) · the full `mypy app` reds and the one pre-existing `eslint` error in `App.household-nav.test.tsx` · `docs/backlog.md` W3–W6.

**Rules for reports:** every report ends with next steps and starts step 1; the parked list is never shown. **Every rated slice sends the owner one report as soon as it is rated** (D-1024-14), and that report also states the roadmap position.

**Standing:** every app-changing slice is deployed as its own slice, right after it is rated; before every close, deploy the live app and record a release. Unrated or blocked work stops the deploy instead of shipping silently. **Every 🟠 or 🔴 decision item, and a 🟡 on the live host, dispatch key, app database or owner's data, goes through the two-phase second opinion before the owner sees it** (D-1024-10; reviewer in `AGENTS.md`). **No local models on the live server** (D-1024-15). **Model and provider choices are the owner's** (D-1024-16). **Ask before creating any artifact** (`AGENTS.md`).

**Where things live:** product plan `docs/ROADMAP.md`; waiting items `docs/backlog.md`; past work git history and `docs/ratings.md`; decisions `docs/decisions/`; reviews `docs/reviews/`; packets and worklogs under `docs/`. Session reports: Launcher issue 62. Context size: the desktop app's `get_usage` tool.
