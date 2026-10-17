# Second-opinion context pack — D-5 / D-6 / D-7 (Phase A input, blind)

Scope: all three open decision items of one owner message (`SECOND_OPINION.md`, contract 0.50.0 / `D451` — all such decisions of one message go in ONE review). Committed before Phase A. **This pack deliberately contains no picks** — the Architect's picks exist in no file this pack names. Read-only slice; authoring date is metadata, not a gate.

Order: D-5 (serve timing), D-6 (density scope), D-7 (reviewer mode).

---

## D-5 — Serve the unserved frontend delta (SG-196 + SG-198) now, or carry it to the next close?

**The problem in plain words.** The live deployment on the shared VPS was last refreshed 2026-10-16 by SG-197, which served the SG-194+SG-195 delta. Since then two rated frontend slices have landed on `automation` and are NOT live: SG-196 and SG-198. A standing owner directive (2026-09-28) requires a live deploy before every session close; it was executed for the prior delta and is due again for the current one. The open question is timing: serve the delta now as its own rider, or carry it into the next close deploy.

**Evidence (verbatim or file:line where it fits).**

- SG-196: done at G1 commit `faea4d6` ("SG-196 G1+G2+G3: shared household context (one fetch), nav selector+household alert, Inbox open-task badge, catalog facets/saved-search alerts"), 21 files +565/−161; suite 296/296; audit line: "Holistic rating: **98/100**, no flag. No slice-side deduction (attribution empty). ... `slowest_waste` = `none`" (`docs/worklogs/SG-196_audit.md:7`).
- SG-198: done at G1 commit `144190c` ("SG-198 G1: AppHeader onto household context, ReviewPage onto shared useReviewTasks"), 4 files +57/−9; zero behaviour change (re-proof only); suite 298/298; audit: "**98/100**, no flag" (`docs/worklogs/SG-198_audit.md:7`).
- Unserved product delta measured by the Architect 2026-10-17: `git diff --stat f757ebd..HEAD -- backend frontend` = **24 files, +622/−170, frontend-only** (f757ebd = SG-195 G1, inside the SG-197-served tree).
- Rider precedent (the shape "serve now" would take): SG-197 — "RESULT: CHANGED ... Exactly ONE backend rebuild (exit 0, 27 s) and ONE recreate (exit 0, 2 s), both through this unit's own lane socket; zero denials anywhere. New container a77e3f2ff0dd ... image sha256:e3b7c0aa...; Health green: start and end 200 ok/ok/ok; six post-recreate GETs all 200; Production SQLite byte-identical end-to-end (no migration ...)" (`docs/worklogs/SG-197_report.md:3`), rated "**97/100**, no flag" (`SG-197_audit.md:5`).
- Standing directive: "Live deploy (rebuild + one recreate + verify) before every session close"; standing owner directive 2026-09-28, quoted "Always do a live deploy before session close" (`AGENTS.md` Configuration, Close-out row).
- The prior deploy decision recorded: "The standing close-deploy stays due at session close (covers the post-serve delta: SG-196 + followers)" (`docs/decisions/2026-10-16-close-out-deploy-d3.md:9`).
- Carrying cost if delayed: the delta grows with work landed before the close; one serve then carries a larger change set in one hop.
- Deploy rails: sensitive surfaces are declared (dispatch host, SQLite DB, evidence store — `AGENTS.md` Sensitive-surfaces narrowing); the rider packet shape and its rails exist in `docs/packets/SG-197-close-out-deploy-rider.md` and `docs/packets/SG-193-close-out-deploy-rider.md`.

**Where it lives.** `docs/worklogs/SG-196_report.md`, `SG-196_audit.md`, `SG-198_report.md`, `SG-198_audit.md`, `SG-197_report.md`, `SG-197_audit.md`; `docs/decisions/2026-10-16-close-out-deploy-d3.md`; `docs/packets/SG-197-close-out-deploy-rider.md`; `docs/packets/SG-193-close-out-deploy-rider.md`.

**What binds it.** `G-K2` (production-facing actions reach the owner however routine); `PRODUCTION.md` guards (the last rider carried them); the 2026-09-28 standing close-deploy directive; `D16` stage flow (post-D-5/D-6/D-7, the rider and then density work are the queued arc); the declared sensitive surfaces.

**Options as they stand.** (A) Serve now — dispatch a rider next, serving the current product tree. (B) Carry the delta to this session's close — one serve covering this delta plus anything landed before then.

---

## D-6 — Density scope after the measurement

**The problem in plain words.** The R8 design review left "consistent card/table density" only partially addressed: the catalog's grid/table density toggle was kept as-is, and "no compact/comfortable, persistence, or per-surface rule ever requested" is on record (`docs/decisions/2026-10-16-density-scope-d4.md:5`). Under the owner-approved measure-first decision (D-4, 2026-10-16), the read-only measurement slice SG-199 ran touch/zoom/dark across six routes — and found zero failures on every axis. D-4's recorded effect: "A density proposal with renders and real options follows the measurement" (`:9`). The open question is what to do with that promise now that the measurement found nothing broken.

**Evidence (verbatim or file:line where it fits).**

- SG-199 audit: "Holistic rating: **98/100**, no flag. ... The clock-field classifier adaptation is accepted: narrowly allowlisted (JSON + every differing leaf ISO-parseable under `generated_at`), controlled 4/4 both directions, flagged not folded" (`docs/worklogs/SG-199_audit.md:7`).
- Touch axis: "document overflow 0/6 ... Nav selector tap-focus 6/6 routes ... badve tap ... navigated to /inbox — end-to-end touch operability proven. ... 0 FAIL ... smallest by height: brand link 19px → PASS-SPACING" (`docs/worklogs/SG-199_report.md:40`).
- Zoom axis: "overflow 0/6 at BOTH levels ... no shell element (nav menu, selector, badge, cards, tables) breaks the reflow; **the ordering is an empty set, stated plainly**. ... No horizontal scrollbar in any of the 12 shots." (`SG-199_report.md:41`).
- Dark axis: "285 text samples across the 6 routes, 0 below AA; min ratios per route 9.4611 / 9.4611 / 9.1759 / 9.4611 / 9.4611 / 8.3120." (`SG-199_report.md:42`).
- Controls: "Final controls: 22/22, every must-fail arm green" (`SG-199_report.md:8`); "28 committed JPEGs ... EVERY ONE opened by the Coder" (`:43`).
- Density-relevant numbers collected for any proposal (`SG-199_report.md:45-50`): "catalog cards: 1440/1280 light+dark 4 x 248.0 px (gap 20) → zoom200 2 x 280.5 px (gap 16) → touch 390 2 x 163.0 px (gap 16)." · "inbox two-pane: 1280 3 x 516.0 (gap 20) → 640 1 x 577.0; at 390 1 x 342.0 (gap 20)." · "analytics summary: 1280 3 x 340.0 (gap 16) → 640 2 x 280.5 → 390 1 x 342.0." · "planning block: 1280 1 x 1052.0, 640 1 x 592.0, 390 1 x 342.0." · "asset detail assertions table: 6 columns; row height 39.0 px at 1280 light and dark-1440, 78.0 px at zoom200, 117.0 px at touch-390; table never overflows its parent at any measured world".
- One off-token observation recorded for a proposal: "native default button faces (`Choose files`, `Take a photo`, `Run planning`, `Generate summary`, `Choose Files`) render light-on-dark in dark theme — consistent, legible, but visually off-token" (`SG-199_report.md:14`).
- REMAINING: "the optional density system itself is out of scope (facts only — D-4's proposal slice owns it); the native-button dark-theme token consistency is recorded for that proposal ...; no product defect found on any measured axis, so no repair is proposed here." (`SG-199_report.md:60`).
- SG-190 line: "'Consistent card/table density' is only partially addressed (grid/table density toggle preserved; no ne..." (`docs/worklogs/SG-190_report.md:72`).

**Where it lives.** `docs/decisions/2026-10-16-density-scope-d4.md`; `docs/worklogs/SG-199_report.md` (density observations 45–50; (a)9 at :14; REMAINING at :60); `docs/worklogs/SG-199_audit.md`; `docs/worklogs/SG-190_report.md:72`; `docs/packets/SG-199-measure-touch-zoom-dark.md`.

**What binds it.** D-4 (measure-first approved; the proposal promise); "no density requirement exists on record" (D-4 file, :5); `G-A7` (smaller mechanism; no advisory machinery for no live reason); `G-A10` (ask what exists / what a gap is for before closing it); `G-A9` (uncalibrated numbers declared, never gates); auth-live observation stays blocked on owner-provided access; container/image identity is Launcher-only (D-4 file, :9).

**Options as they stand.** (P1) Extend — build the density proposal: renders + real options beyond the current toggle (the thing D-4's effect promises). (P2) Card-size — a narrow catalog card-size change only. (P3) Leave-it — no density work; the existing grid/table toggle stands.

---

## D-7 — Second-opinion reviewer mode

**The problem in plain words.** The project's `second_opinion:` value was declared with the 0.50.0 adoption as the explicit triple `coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max`, because "the Architect's own model (muse-spark-1.3 family) is ambiguously inside/outside the rule's 'Muse 1.3' condition, and the explicit pick satisfies 'never the Architect's own model' under both readings". The contract also allows `default` (resolved by the rule at dispatch time) and `off` (owner-only). The open question: does the explicit value stay, or does the owner set `default` / `off`?

**Evidence (verbatim or file:line where it fits).**

- Adoption record: "Reviewer value declared in AGENTS.md: `second_opinion: coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` — explicit rather than `default` because the Architect's own model (muse-spark-1.3 family) is ambiguously inside/outside the rule's 'Muse 1.3' condition, and the explicit pick satisfies 'never the Architect's own model' under both readings (`G-A2`). Reversible config; owner may set `default`/`off` (`G-K1`: decided, done, reported here)." (`docs/decisions/2026-10-15-contract-050-adoption.md:35`).
- Contract rule: "**`default` resolves to the default below, or to the Muse-1.3-Architect value when the project's Architect runs on Muse 1.3** — the Architect applies that condition from its own model. **Default:** `coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh`. **An Architect that itself runs on Muse 1.3 uses** `coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` — **the reviewer is never the Architect's own model** (owner, `D451`). **`off`** only by the owner's choice ..." (`SECOND_OPINION.md` §The reviewer — one setting per project).
- The review duty descends from: "D-3 was a 🟠 decision brought without the `SECOND_OPINION.md` two-phase review ... **Future 🟡+ decisions go via `agent=plan` Phase A/B before the owner question.**" (`docs/decisions/2026-10-16-close-out-deploy-d3.md:17`).
- `AGENTS.md` Configuration row "Second opinion": "`coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` ... Explicit per D-2 (reviewer never own model under either reading of the Muse-1.3 condition); owner may set `default`/`off` (`SECOND_OPINION.md`, `D451`)."
- The setting governs this very review mechanism (all 🟡/🟠/🔴 decisions of one message go through one two-phase review before the owner question).

**Where it lives.** `docs/decisions/2026-10-15-contract-050-adoption.md:35`; `AGENTS.md` Configuration table ("Second opinion" row); `.rules-cache/SECOND_OPINION.md`; `docs/decisions/2026-10-16-close-out-deploy-d3.md:17`.

**What binds it.** `D451` ("never the Architect's own model"); `G-O2` (never design around a specific model's characteristics); `G-K1` (reversible config — decided, reported); the D-3 miss note and its counter-rule.

**Options as they stand.** (1) Keep-explicit — the config value stays written as it is. (2) `default` — the rule resolves the value at dispatch time from the Architect's own model reading. (3) `off` — no second-opinion reviews (owner-only choice).
