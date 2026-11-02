result=done id=SG-283 inactive
debug-report-begin
SG-283 model=unknown; effort=unknown (process arguments/provider metadata unavailable within permitted repository reads); directory=/tmp/dispatch-review.Zv4DzB; remote=unverified; WORK_HEAD=unknown.
BASE_REF_REQUESTED: origin/automation
BASE_COMMIT_RESOLVED: unknown; the supplied snapshot has no `.git`, so resolved identity and equivalence to BASE cannot be independently established.
**Contract version: 0.56.0** — **echo this line verbatim in your receipt.** It is the only proof that you
Contract provenance: `.contract/CODER.md:3`, corroborated by `.contract/SOURCE:1`. No external version command was run.
Outcome: advisory critique completed. R1–R3 remain owner-approved; objections below do not rescind them. R4–R7 remain recommendations. Most serious objection first.

**Extra Files**
Beyond the eight files explicitly required by G1, the following files were read, including bounded windows and search excerpts:
- `.contract/CODER.md`
- `.contract/SOURCE`
- `docs/ROADMAP.md`
- `docs/research/2026-10-30-requirements-recalibration.md`
- `docs/backlog.md`
- `docs/worklogs/SG-278_report.md`
- `docs/worklogs/SG-279_report.md`
- `docs/worklogs/SG-279_rehearsal.log`
- `frontend/src/theme/tokens.css`
- `frontend/src/routes/theme-adoption.test.tsx`
- `frontend/src/components/catalog/ProductCard.tsx`
- `frontend/src/components/shell/ItemInspectorDrawer.tsx`
- `frontend/src/routes/CatalogPage.tsx`
- `backend/alembic/versions/20261102_sg279_candidate_state.py`
- `backend/tests/test_sg279_candidate_state.py`
- `backend/tests/test_sg279_rehearsal.py`
- `backend/app/services/candidates.py` (470–539)
- `backend/app/server.py`
- `backend/app/services/scene/openrouter.py`
- `backend/app/services/providers/protocols.py`
- `backend/app/services/providers/router.py`
- `backend/app/services/providers/schemas.py`
- `backend/app/services/providers/prompts/chat-v1.md`
- `backend/app/services/providers/opencode_go.py` (search excerpts and 260–384)
- `backend/app/services/providers/fake.py` (search excerpts only)
- `docker-compose.yml`
Expansion triggers: verify recovery boundaries, actual text-provider capability, structured-output restrictions and AI safety enforcement.
Directory listings: repository root and `.contract/`. Filename searches obtained paths only; no images were opened.
`docs/packets/SG-280.md` was absent; searches found no SG-280 packet. This was not a permission denial. R6's supplied rider description is reviewed as a specification, not as inspected implementation.

**R6: Migration Deployment**
Strongest objection: scratch restoration plus integrity/FK/head/count checks does not establish that the actual interrupted-migration recovery procedure works.
Evidence: the rehearsal runs successful upgrade at `backend/tests/test_sg279_rehearsal.py:115-117`, successful downgrade at `:224-232`, and downgrade refusals at `:238-271`. It never interrupts the rebuild or executes backup replacement.
`docs/worklogs/SG-279_rehearsal.log:2` explicitly says “Will assume non-transactional DDL.” Detecting `_alembic_tmp_candidate` identifies one failure state; it does not demonstrate recovery from it.
The schema-text gate materially improves prevention of drift identified at `docs/worklogs/SG-279_audit.md:17`. However, candidate's table SQL does not itself inventory separately defined indexes, triggers or dependent objects; the rehearsal compares the wider object set at `backend/tests/test_sg279_rehearsal.py:139-145`.
Opinion: retain that wider pre/post inventory rather than treating candidate SQL equality as complete schema equivalence.
Unverified premise: authorised rollback can replace the failed database at the intended destination, handle sidecars correctly, and start the immutable old image with readable application data.
Settling observation: an authorised isolated rehearsal of the exact recovery commands against an interrupted rebuild, with application read-back and data/object comparisons, including a failed-recovery branch that leaves services stopped.
Phase A disposition: unchanged. The Architect's two additions close important gaps but not the restore-rehearsal gap. Opening a restored scratch database proves more than checking an archive, but less than rehearsing operational replacement.
Recommendation: retain SG-279's code and D16's recovery states; add the narrow isolated recovery proof before live DDL. Do not demand general export/import restore as part of this rider.
Starting the new backend remains the write boundary: `backend/app/server.py:27-34` schedules the reminder loop. Do not infer a safe restore window from a subsequent failed health check.
This is the strongest objection to return to the owner if the proposed narrower gate is retained. It is not a discovered defect in the constraint widening or deployment authorisation.

**R7: Pantry Intelligence**
Strongest objection: the proposed safety limits are necessary policy, but the existing services do not enforce the stronger claims a meal recommender would make.
Evidence: chat returns provider text and marks it `grounded=True` without semantic safety validation (`backend/app/services/chat/service.py:448-465`). Its prompt prohibits invented facts and medicine advice, but has no explicit allergen or past-date food-safety rule (`backend/app/services/providers/prompts/chat-v1.md:10-33`).
Planning validates an extraction envelope, not recipe safety or factual date equality (`backend/app/services/planning/service.py:309-318,362-385`). Unresolved item references can fall back to a label rather than being refused (`:322-332`).
P3 is not a small prompt extension: planning overloads extraction fields for single-asset actions; its prompt specifies `lot=asset id`, `date_type=kind` (`planning-v1.md:28-39`). The strict schema forbids undeclared recipe fields (`backend/app/services/providers/schemas.py:31-69`).
Premise correction: the one-operation note at `planning/service.py:3-13` is historical, not the current provider's complete capability. The real adapter implements `extract_text(text, prompt)` (`providers/opencode_go.py:326-370`), and chat uses it (`chat/service.py:423`).
Thus existing consent, accounting and grounding plumbing are reusable; structured meals, quantities, servings, time and multi-ingredient references are new contracts. Both catalog builders omit quantity/unit and allergens (`planning/service.py:175-186`; `chat/service.py:270-281`).
Unverified premise: these sparse records can support useful meal proposals without implying sufficient quantities, allergen suitability or safe consumption.
Opinion: put explicit household allergy entry and verified label handling before any personalised dietary-suitability claim, even if richer P8/P9 features stay later. Never learn a hard allergy from accept/skip; unknown ingredients or cross-contamination information cannot mean “allergen-free.”
Opinion: add deterministic eligibility/reference checks, distinguish use-by from best-before and unknown dates, and reject unsupported medical or food-safety claims. A date before today is not the only food-safety risk.
P1 also needs event semantics: final “gone” reasons alone do not establish every partial consumption or historical non-use. The roadmap distinguishes quantity changes from archive reasons (`docs/ROADMAP.md:45-46`). Label incomplete history “not recorded,” not “never used.”
P2 should say “2 recorded matching packs,” with uncertainty and source dates; do not promise two current packs from a stale catalog.
P4 calendar plans must remain distinct from actual consumption; P5 shortages must not be inferred merely from missing logs. P10 needs separate notification opt-in, timing and deduplication criteria.
Settling observation: a real-shelf trial plus adversarial tests covering absent quantities, stale stock, unknown allergens, expired items, hostile labels, cross-module medicine requests, invalid references, consent refusal and accounting on failed calls.
Phase A disposition: the owner's explicit intelligence request increases product priority, not evidential confidence. Conditional, trial-led R7 is preferable to unconditional adoption; safety and data prerequisites still need explicit gates.

**R3: C → D → E**
Strongest objection: strictly finishing an expanded D before beginning E lets a parked provider decision and speculative enhancements block an explicitly desired outfit workflow.
Evidence: `docs/ROADMAP.md:18-19` makes D depend on real C use and provider choice, but E depends on C and B, not D. `:56` explicitly parks image generation on provider answers.
R1 also expands D beyond shared images. Treating all those additions as prerequisites would strengthen R3 beyond its stated shared-images sequence.
Unverified premise: shared-image work will be sufficiently bounded and available that serialising it ahead of Wardrobe will not delay the owner's principal new use case.
Settling observation: after C's real-shelf return visit, identify a bounded image pilot with an owner-selected provider and achievable acceptance criteria; otherwise return the sequencing consequence to the owner.
Phase A disposition: unchanged on “C real use → restore proof → bounded D pilot → thin E.” The owner's emphasis on suggestions and saved outfits strengthens the argument against making every D feature a prerequisite.
Restore must not wait behind provider selection. The roadmap says it should work “before much more of the owner's data goes in” (`docs/ROADMAP.md:54`).
Distinguish R6's narrow migration rollback proof from D's broader backup-restoration capability; neither substitutes for the other.
Recommendation: preserve approved R3, explicitly bound what “shared images first” means, and carry restore as an independent safety gate. Any change to the approved order returns to the owner.

**R1: Feature Placement**
Strongest objection: stage placement can become a build commitment before the inventory and use history needed to justify the features exist.
Evidence: only seven assets and unknown reasons for low use are recorded at `docs/ROADMAP.md:37`; C explicitly requires a later ordinary-use correction check (`:48`).
W1 does not inherently require wear history: exact duplicate lookup can help early. But absent/incomplete inventory cannot justify “you do not own this” or “you need this.”
W3 needs actual use events and a coverage boundary; no recorded use is not evidence of never-use. R7's use-log-first ordering exposes the same dependency.
W7 is placed in E, not D, but E placement alone does not ensure accumulated wear/occasion evidence. Counting possible combinations is not evidence of a genuine household wardrobe gap.
The original roadmap places buying suggestions in F (`docs/ROADMAP.md:67-70`). Approved R1 can revise this, but implementation must distinguish inventory lookup from purchase/gap advice.
Unverified premise: real use will supply sufficient completeness and history before W1/W3/W7 are built or presented confidently.
Settling observation: the shelf trial demonstrates reliable correction and consultation; later garment trials show trustworthy ownership/person fields and wear logging. Evaluate each feature against the relevant evidence, not an arbitrary asset-count target.
Phase A disposition: not persuaded to build the full list automatically. Accept the owner's approved roadmap additions while retaining evidence-based execution gates.
V3/V5 remain first-image safeguards. V1 batch capture, V2 installation and W4 push need a demonstrated capture/access/delivery problem; existing in-app reminders are documented at `docs/ROADMAP.md:95`.
W5 natural-language capture is not identical to today's manual form, but should first be scoped against existing typed capture (`docs/ROADMAP.md:87`), not assumed wholly new.
Opinion: exclude the listed social, billing and gamification features as proposed; the stated household goals provide no evidence they deserve earlier work.

**R4: Outfits First in E**
Strongest objection: “first things built” bundles the first valuable outcome with prerequisites and secondary UI that need not all block it.
Evidence: E needs a garment category and separate wardrobes with a person picker (`docs/ROADMAP.md:60-62`). R4's listed dependencies omit that ownership boundary, while existing code has no working Wardrobe feature according to `:65`.
Conversely, saved manual outfits do not inherently require weather, colour extraction or prior wear history. Those chiefly improve suggestions, not basic composition and saving.
Unverified premise: implementing W11/V4/W6/weather before any usable saved-outfit flow is the fastest path to value.
Opinion: start with person-scoped garments, manual composition and a saved list; add a thin suggestion path with explicit occasion/weather input and manual override. Let missing wear history mean unknown. Add calendar/filter sophistication when the first loop works.
A calendar assignment is planned wear, not proof of wearing; W6 must preserve that distinction.
Settling observation: the owner can choose the intended person's pieces, build/save/reopen an outfit, and correct or reject a suggestion using ordinary photos. Observe whether automatic weather and the calendar actually remove friction.
Phase A disposition: the new owner statement supports prioritising W13/W14 over speculative wardrobe analytics. It does not justify making every enrichment field or weather integration a prerequisite.
No objection to starting on ordinary photos: current cards support contained source imagery (`frontend/src/components/catalog/ProductCard.tsx:60-64,140-155`).
Opinion: even a collage can technically use rectangular photos; cutouts are a visual-quality dependency, not an absolute composition dependency. No weather provider is selected here.

**R5: Product Images**
Strongest objection: a cloud “cut-out” is not automatically faithful; bad masking can remove packaging, transparent edges, straps or fine garment details.
Evidence: the current scene client's preservation promise is prompt text (`backend/app/services/scene/openrouter.py:79-85`), and its server-tool path explicitly translates the image through text (`:32-38`). Neither demonstrates foreground-preserving segmentation.
The roadmap already calls for trials on real samples and retaining originals (`docs/ROADMAP.md:52`).
Unverified premise: an owner-selected service preserves identifying foreground detail at acceptable review effort, cost and privacy terms on actual household photos.
Settling observation: compare derived results against representative source photos, including transparent/reflective packs, readable labels and fine garment detail; reject materially altered results and retain the original as a successful display outcome.
Phase A disposition: unchanged; R5 substantially matches it. “No regeneration by default” is weaker than “poor evidence prompts recapture, not synthesis,” so any regeneration exception needs a separate explicit purpose and approval.
Opinion: keep derived imagery out of authoritative label/allergen/date extraction, support undo/original fallback, and define retention/deletion at the cloud send boundary before bulk processing.
No provider is recommended as a decision. Owner choice remains binding.

**R2: Theme Adoption**
Strongest objection: global colours/font/shapes do not imply global fidelity, accessibility or satisfactory presentation with raw household photos.
Evidence: card radii are inline (`frontend/src/components/catalog/ProductCard.tsx:108-127`); inspector controls have independent shapes (`ItemInspectorDrawer.tsx:224-243`). A token change alone cannot complete R2.
Existing tests assert token classes and toggle persistence, not rendered readability or narrow-layout quality (`frontend/src/routes/theme-adoption.test.tsx:163-221,271-276`).
The theme has a distinct dark-link tint because the primary colour previously had inadequate dark contrast (`frontend/src/theme/tokens.css:11-14,44-47`); preserving `.dark` alone is insufficient.
Unverified premise: the chosen hierarchy still works with uneven Pantry photos, enlarged text and mobile controls.
Settling observation: owner review with representative real photos, plus measured light/dark contrast, narrow layouts, text zoom and keyboard operation. Do not create a new design artifact without the required approval.
Phase A disposition: unchanged and supportive of R2's bounded scope. I checked shared tokens, component-local geometry, source-photo fallback and existing tests; no source-backed reason to reject the selected theme was found.
Opinion: keep honest neutral photo wells and original-source access rather than using placeholder cutouts to claim visual completion.

**Close**
A failed real-shelf return visit would challenge the whole expansion: if maintaining correct stock remains too burdensome, investigate that burden before adding breadth (`docs/ROADMAP.md:37,48`).
No tests, health probes, database access, network, browser, credentials, host operations, migration, restart, commit or push were performed. I wrote nothing.
The production overlay was absent from the supplied `.contract/` listing; no operational authority is inferred. Publication is delegated to the engine.
UNCLEAR FIRST READ: exact rider contents and provider-seam capability.
UNCLEAR DURING EXECUTION: SG-280 packet absent; current text adapter corrects planning's historical one-operation premise.
UNCLEAR REMAINING: executable recovery proof, household adoption, inventory/history coverage, real-photo fidelity and implemented safety enforcement.
Read: AGENTS.md, the direction context, SG-282, SG-279 audit, planning/chat services and planning prompt, plus every extra file inventoried above.
debug-report-end
