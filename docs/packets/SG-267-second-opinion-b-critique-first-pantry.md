# SG-267 — Second opinion Phase B (critique): the first real Pantry

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. Your tree may carry no git metadata: if so, say that and go on; the review is still useful.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Stage C of `docs/ROADMAP.md` is the next stage to go to the owner. It touches the app database, a declared sensitive surface, so the project requires a critique before the owner sees it. Phase A was SG-266 (`docs/worklogs/SG-266_report.md`); its evidence is unchanged except for the serve in `docs/releases/2026-11-02-sg262.md`.

## Read

`AGENTS.md` top section; `docs/reviews/2026-11-02-roadmap-modules-context.md`; `docs/worklogs/SG-266_report.md`; `docs/ROADMAP.md`; `docs/worklogs/SG-262_audit.md`; and the code each decision needs. **List every other file you read.**

## The Architect's picks, verbatim

All are recommendations. The owner has not seen them.

- **C-1, stage shape:** one read-only walk of the real flow first (capture, inbox, review, date entry, find the item), reporting every step that cannot complete. Then the fixes the walk shows are needed, then the Pantry slices. The owner uses it on real items at the end of the stage.
- **C-2, what enters Pantry:** an item whose accepted category is `food_beverages`. Only that. Any other item, including an unclassified one, stays in the general catalog.
- **C-3, module mechanism for now:** no second registered plugin yet. A small data map from category to module, read by the Pantry view. Wardrobe's stage registers the first real second plugin. Stored `plugin:expiry-tracker/…` paths stay as they are.
- **C-4, repeat purchases:** each pack is its own item, because it has its own date. The Pantry view groups items of the same name into one row, and "take one off" acts on the earliest-dated pack.
- **C-5, "gone":** the existing ARCHIVED status, with a new legal edge ARCHIVED→ACTIVE for "put back", and the reason (used, thrown away, given away) stored as an assertion, so no schema migration. Reaching zero quantity asks "gone?" and does not archive by itself.
- **C-6, the look:** the owner's chosen Linen Shelf direction, applied to the Pantry view only, leaving other screens alone this stage. Until stage D, photos are shown as captured, on the same beige card. Fonts are self-hosted or from the existing build, whichever the walk finds simpler.
- **C-7, rider:** one deploy rider per app-changing slice, as the project already requires.

## G1 — Per pick

For **C-1** to **C-7**:

- (a) the **strongest case against** the pick, with evidence (`file:line`, a quote, a measurement). An objection without evidence is labelled `opinion`;
- (b) a **premise** of the pick that is unverified;
- (c) the **observation that would settle** any disagreement.

Check these specifically: the premise that an ARCHIVED→ACTIVE edge and a reason assertion need no migration; what else reads ARCHIVED and would misbehave on the way back; whether grouping by name is safe given how names are captured; whether C-2 leaves pantry goods out because of how categories are assigned; what happens to items with no classification, given that classification is a separate step.

## G2 — Missing

One thing the plan misses that would most change whether the owner uses this, with evidence or labelled `opinion`.

## Report

Your final message **is** the report (the engine publishes it; read back with `SG-267 --status`; the Architect copies it unedited to `docs/worklogs/SG-267_report.md`). `SG-267` is its first token, followed by the contract-version line (`PB-4`), the extra-files list, one section per pick, and G2. You publish nothing else; state that you wrote nothing.

## Constraints

- Read-only; a denial anywhere is a STOP (`PB-2`). Reads confined to the repository; no host changes; no credentials; no browser; no external network.
- Decisions the context pack lists as already taken are not reopened.
- Hang bound: ordinary file reads 120 s each; no interactive prompt.
- No fixed dates beyond those quoted from sources (`PG-IC-07`).

## Acceptance criteria

- (a)–(c) present for each pick; each objection evidenced or labelled `opinion`.
- `PB-3` vacuity: "no objection" needs a sentence saying what you checked.
