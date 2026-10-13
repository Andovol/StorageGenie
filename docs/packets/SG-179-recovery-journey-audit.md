# SG-179 — Recovery audit: user journeys and the actual deployed UI

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: disposable isolated fixtures; production read-only.**
**Restart: none.** Do not change the running build.
**Autonomy: L2.** Authorization: RECOVERY-D1 in `docs/decisions/2026-10-13-recovery-audit-approval.md`; audit only. SG-175 checkpoint is recorded in SG-175_audit.md: valid receipt, functional proof, 90 FLAG:SAFETY for continued work after denied optional Docker read. Its code remains UNSERVED and held from acceptance/deploy. This independently approved audit may inspect the held candidate read-only and in disposable fixtures; it does not clear the flag, repair product code or change privileges. Do not trigger from an unpushed draft.

## Why this exists — expectations to verify, not completion claims

Owner reports missing functionality, absent user stories and unacceptable UI/design. Existing blueprint journeys and design rules do exist; `docs/reviews/2026-10-13-recovery-audit.md` is the canonical initial register and source map. The approved stage establishes the real coverage before proposing new implementation. The initial map was made at 803cf52, before SG-175 product repair: re-read changed premises at the resolved base and use the final SG-175 audit dispositions. Historical SG-173 observations are diagnostic evidence, not proof of this running frontend.

Expected app routes from `frontend/src/App.tsx`: `/`, `/capture`, `/assets/:id`, `/settings`, `/inbox`, `/planning`, `/chat`, `/analytics`, `/expiry`, `/review/:candidateId`. The source App adds shared Nav to every route; Catalog has an additional shell/header. Treat mobile overflow and hierarchy concerns as hypotheses until rendering/measurements. Blueprint §11 is the intended screen inventory; accepted optimization and Phase 3 decisions narrow it. Context Scene UI is separately parked; no automatic reopening.

Expected known entry limitation: Architect's in-app browser navigation to `https://storagegenie.dynv6.net/` failed `net::ERR_INVALID_AUTH_CREDENTIALS`, without any credential entry. Do not change auth or seek unrelated credential stores. Use only an already-approved authenticated access mechanism/session if available; otherwise explicitly record the missing observation and use granted read-only host observations of the actually running built frontend, with provenance. A temporary Vite build is source-equivalent evidence only, never deployed-URL proof. A limitation is not permission to invent a PASS or modify the host.

SG-175 recurrence correction: its attempted /var/run/docker.sock listing was denied. Do not repeat that known-unavailable optional Docker operation; report container/image identity UNVERIFIED unless already available through an established read grant. No alternate socket, identity, mount or sudo. PB-2 is whole-slice STOP on ANY new privileged denial, including an optional read; “optional” never excuses it. Current SG-175 evidence gaps also belong to SG-180/182: absent initial failed-probe capture, names/sizes fingerprint not content/volume conservation, ephemeral benchmark script and worker-clock versus engine budget distinction. Preserve these limitations.

## G1 — Account for every route and story

Read the canonical register and referenced product/accepted-scope records; preserve intentionally deferred or rejected capabilities. Inventory every listed route and reachable menu/dialog/drawer, URL/household navigation context, main action and all visible states. For every REC-ST01–REC-ST15 record: exact start, consequential action, expected outcome, frontend caller, real API writer/reader, persistence/readback, executed evidence, blocker and missing observation. Coverage state must be working / partial / broken / absent / intentionally deferred / unverified, with scope. Absence of a frontend caller is not absence of a backend capability.

Observe the actual deployed frontend read-only: record current running image/container/start, served bundle identity and current health, then pages/data needed for actual existing-item rendering. No accept/resolve/import/enrich/planning/chat-generation action against live data. Do not expose private item values or opaque IDs in committed screenshot/text evidence; sanitize locally, preserving structural observations and provenance. Fetching a model response is not a GET audit and is prohibited.

The unavailable image/container/start fields above are UNVERIFIED limitations, not reasons to attempt the excluded Docker operation. Independently observed served bytes/health are usable on their own axes and must not be upgraded to container identity proof.

## G2 — Exercise writable and failure paths only in disposable isolation

For mutation-dependent transitions, use real routes/services with a fresh temporary SQLite and fresh evidence/derived-storage root; override all relevant application dependencies and provider clients explicitly BEFORE the first write. No production .env/settings/credentials copied to a checkout or proof. Verify DB and evidence paths point to disposable destinations, capture override inventory and restore resources. Scripted/fake providers may exercise transport shape, consent/error states and user interaction, but do not claim real-provider quality/latency or that the fake proves the provider implementation. No paid network calls.

Focus on small discriminating controls, not another blanket suite:

- Import unchecked branch: source `AssetImportModal.tsx::process` creates the import but calls /run only when checked; its help promises Run from Inbox. `backend/app/api/v1/jobs.py` creates a job in `job_service.create_job`; explicit /run exists. `InboxPage.tsx` and `JobCard.tsx` initially offer select and FAILED Retry, with no other import /run caller found in production frontend source. Assert a real CREATED fixture landed; render the actual Inbox and exercise available actions. Compare a working checked-import/failed-retry control. If no usable Run exists, record the disconnected transition with evidence; do not fix it.
- Review: exercise current SG-175 behavior, busy/keyboard guards, live blocker projection and duplicate reason cleanup; separate repaired UNSERVED source from unchanged deployed build. Classification/Resolve/visibility defects remain whatever the actual evidence shows; no inferred fix from a pending packet.
- Capture/manual create versus import: trace camera/file input options, file-type support and error recovery across both actual surfaces; do not label camera absent from a partial component search.
- Search/filter/saved-search: use a disposable population large enough to span actual pagination, not a single page. Capture loaded-page versus global sort meaning, saved-search lifecycle, empty/error states and household context. A source comment that declares page-local sorting is scope evidence, not proof that global user expectations are met.
- Settings: actual UI exposes model selection and household reset at the initial baseline; compare each promised setting with a real existing control, intentional scope decision, API-only capability or absence. No configuration change in production.
- Links/action destinations: task subjects may reference assets or candidates; verify each current task type reaches its intended existing screen and data-required completion path. Do not manufacture unknown fixtures and call them live rows.

Known fixtures are module-local, not a shared conftest. Reuse backend candidate_read_db/candidate_db/plugin_db and existing frontend query/router fixtures where applicable; audit probes may adapt them in permitted evidence paths without changing the original fixture/tests. Historical production-task population and fixture assertions are distinct.

## G3 — Audit responsive layout, accessibility and state communication

For each route, inspect rendered mobile/narrow, tablet and desktop layouts, keyboard navigation/focus, overlays/scroll, touch controls, evidence readability, empty/loading/error/blocked/success states and whether each action tells the truth. Viewport choices are exploratory Architect judgement: include a narrow phone width, a tablet width and a wide desktop width; record exact dimensions rather than claiming universal coverage. Supplement with zoom/reflow and keyboard checks. Accessibility target in the approved proposal is proposed WCAG 2.2 AA, not an existing conformance claim; use applicable official W3C criteria, do not invent thresholds. Check actual computed geometry/contrast/focus where available, not a styling token's name.

Screenshots receive both UI and displayed-data audit; no diagram/mockup/new design required. Inventory controls not exercised because they would mutate production. Separate visual judgement from measured clipping/overflow/focus failures. Color preference alone is not a product defect. Identify a coherent minimal reuse direction in the report; compare consolidating existing shell/tokens with one simpler viable alternative in a short table, with cost and what it replaces. No component/theme rewrite in this slice.

## Constraints

- Write ceiling: `docs/worklogs/SG-179*` and supporting sanitized captures. Read all project source/config/tests and project contract cache as needed; never another project, owner profile/credential store, unrestricted provisioning key, host config outside declared read grants or another tenant's data. No changes to the canonical register: Architect incorporates audited findings at the checkpoint.
- No product/config/test/lockfile/schema/migration edits, dependency upgrades, new auth, service start/restart/rebuild, production POST/PUT/PATCH/DELETE, direct DB writes, evidence-store writes, imports, resolving, paid API requests or provider calls. Source/test proofs and disposable test processes are allowed inside scratch; no always-on service or watcher.
- Privileged denial is STOP (PG-PR-03); no alternate identity/sudo/mount/socket path. STOP-and-report means stop. Publish finished observations plus limitations through PB-6.
- Start/end health GET per CO-92. Expected contract 0.46.0; echo actual contract version/source and current lane runtime budget. Inherited host cache/tag/auth limitations are not permission to repair them. Ordinary command bound 120s, isolated test/browser command bound 600s (uncalibrated inherited precedent), with timeout visible. Report runtime in seconds versus current lane budget; no sum-of-goal duration promise.
- No full-suite or full end-to-end directory run. Proposed focused regression controls: existing frontend import-modal/shell/ReviewPage tests and backend candidate-read/import-job/plugin expiry nodes actually needed for the demonstrated branches. Before running, identify exact node IDs by their current definitions, name what property each observes and list exclusions. Browser live proof remains separate from component mocks. Proof files go in allowed SG-179 paths, not ignored spaces forced into Git.
- No silent coverage truncation. At the publish boundary, every route/story has an observation or UNVERIFIED with a reason and explicit destination. Stop starting new probes when receipt time is at risk; a partial honest coverage matrix is acceptable, an unexecuted PASS is not.

## Acceptance / report / receipt

- A1: Every actual route and REC-ST story accounted for, with provenance and scope-decision source; no stale phase marker or API presence counted as completed user journey.
- A2: Actual deployed build/read-only page observations identified, plus explicit public-URL/auth and mutation limitations. No temporary-build browser proof mislabeled deployed.
- A3: Discriminating isolated writable/failure controls use real components/routes and demonstrate their fixture/override scope; important checks reject a deliberate wrong outcome and have a known-working control. Commit raw sanitized commands/output under SG-179 paths for every reproduction/measurement claim, including failed controls.
- A4: Responsive/keyboard/state observations identify route, viewport, actual renderer/build and measured property versus visual judgement. Every issue has status, severity as author judgement, root-cause hypothesis, affected story and smallest repair scope proposal; no repairs performed.
- A5: First token `SG-179`; `docs/worklogs/SG-179_report.md` includes requested/resolved base, WORK_HEAD, selected settings identity, contract echo/source, health delta, runtime, all constraint dispositions, and FIRST READ / DURING EXECUTION / REMAINING. Runtime/source gaps remain explicitly UNVERIFIED.

Guards relied on: PG-EV-01/02/03/05/06/09/13; PG-SC-01/02/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/10.

Use bound notes-ref receipt (CO-60): commit with `Dispatch-ID: SG-179` trailer; publish a note on `refs/notes/storagegenie-coder-reports` whose first line is `Dispatch-ID: SG-179 | Report: docs/worklogs/SG-179_report.md` and includes Work-HEAD; push automation and that notes ref; read back the remote note and identify its annotated commit. Legacy finalizer is retired. Runtime audit completion needs this receipt and independent Architect audit/rating before SG-180.
