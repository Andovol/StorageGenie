# Second-opinion context pack — N-1 next stage (Phase A input, blind)

Scope: one open decision (which stage, if any, follows D-32). Committed before Phase A. **This pack deliberately contains no picks** — the Architect's picks exist in no file this pack names. Read-only slice.

Order: N-1 only.

---

## N-1 — Which stage, if any, follows the D-32 bulk-fork close?

**The problem in plain words.** D-32 (2026-10-23) closed all three D-31 bulk forks as parks/record: cutouts parked, BARONI canonical with PIKOK staying an upload, CEAFĂ stays parked. The bulk stage is complete-as-narrowed: scenes linked and live for every renderable product; zero product delta since the SG-222 serve rider; `release-2026-10-21` still covers live. No approved executable remains. The question is what, if anything, comes next.

**Evidence (verbatim or file:line where it fits).**

- SG-226 REMAINING (`docs/worklogs/SG-226_report.md:65`): "(1) small secondary text remains a model fidelity limit; a future brief/resolution may improve it; (2) CEAFĂ stays policy-parked; PIKOK needs the canonical-photo decision; (3) bulk cutouts stay parked on a better brief; (4) D-27 pilot remains 5 of 10 billed (bulk renders count against D-20/D-14 only; pilot ledger unchanged); (5) the four new links are live but unlinked/rejected later by owner word if the artifacts are unacceptable; (6) no served-code change, so no deploy was owed." Items (2) and (3) are since decided by D-32 and are not reopened.
- Fidelity calibration (`SG-226_report.md:10`): "All four renders carry a small secondary-text artifact; the primary labels are exact. The review standard is calibrated to the pilot's linked SG-220 Costiță-2 render, whose small ingredient print is garbled while the BARONI brand/name are exact (`SG-226_calib_costita_label.png`)." Per render: "Toothpaste top-face Romanian microtext garbled; UHT circular Lidl-mark microtext garbled; Milbona certification ribbon/producer line garbled; TRACHISAN ECHILIBRU ALIMENTAR logo text garbled. In each, the product identity, brand, product name, variant, quantity and key claims/ingredients are exact and legible."
- Cutout label fail (`SG-225_report.md:10,32`; `SG-225_audit.md:7`): isolation pass on white (border-ring minimum `[250,249,250]`, positive margins, no props); exact-label fail — bottom-left word **FROZEN rendered ERO7EN**, chicken badge changed from source gold `(253,197,66)` line-art head to dark-red `(150,33,42)` full chicken. Decision: unlinked with reason; `asset_evidence` stayed 16.
- Unlink shape precedent (SG-223): one `asset_evidence` DELETE exact, 17→16, render Evidence preserved, re-verified live (`2026-10-21-close-sg216-sg228.md:22`).
- Excluded-from-pilot items (`SG-225_report.md:55`; `SG-226_report.md:53`): Generate-button wiring, resolution pin, drawer cutout tab, provider-routing contest — each excluded, none attempted. Drawer cutout tab still shows the honest copy (SG-225 REMAINING).
- Spend rails (`2026-10-21-d29-bulk-run-all-products.md:18-19`): "at ~$0.068/render upstream, the $2.00/day cap fits ~29 renders/day and the $10.00/month cap fits the whole DB many times over." D-27 pilot: 5 of 10 billed remain (`SG-225_audit.md:9`; unchanged by bulk per `SG-226_report.md:37`).
- Standing close rule (`STATE.md:8`): close-deploy + close-release re-fire only when new product commits land — none have landed since SG-222.

**Where it lives.** `docs/worklogs/SG-226_report.md` (:10, :43-44, :63-65), `SG-226_audit.md`, `SG-225_report.md` (:10, :32, :55, REMAINING), `SG-225_audit.md`, `STATE.md` (:2, :8, :12), `docs/decisions/2026-10-21-d31-l3-bulk-stage.md`, `docs/decisions/2026-10-23-d32-bulk-forks-decided.md`, `AGENTS.md` (Configuration: caps, close-out, second opinion).

**What binds it.** D-32 (parks + canonical — not reopened); D-31 (stage ends at a `G-K2` surface, an unanswered decision, or a STOP); D-20/D-14 caps + D-27 remainder (every billed leg triple-bound fail-closed); `G-K2`/`G-K3` (production writes reach the owner individually); standing close-deploy/close-release (product commits only).

**Options as they stand — WITHOUT pick.**

- (A) Render-review + reject pass. The owner reviews the linked renders live in the app; each rejected render is unlinked by its own slice (DELETE exact, evidence preserved — the SG-223 shape), never edited. Settles: whether the shipped artifacts are acceptable. Costs: $0 billed renders; owner eyeball time; small DB writes under per-slice grant.
- (B) Microtext-fidelity probe, ≤2 billed renders. Tests whether a reworded brief or a higher resolution fixes the small-text garbling class (SG-226 calibration + SG-225 label fail are the baseline). Settles: improvable flaw or hard model limit — which decides whether any future scene/cutout brief can demand exact text. Costs: ≤2 billed sends against D-20/D-14 (D-27 remainder available); spend for a finding either way.
- (C) Generate-button wiring. Product slice: wire the UI Generate button to the render path, with tests, plus a deploy rider to serve it. Settles: owner self-serve renders. Costs: a product slice + suite + serve; and render demand is mostly done or parked, so the button would serve re-renders and rejections only.
- (D) Park everything / close light. No next stage; the session closes with records already pushed and no deploy/release owed (zero product delta since SG-222). Settles: nothing further unless the owner names it later. Costs: none.
