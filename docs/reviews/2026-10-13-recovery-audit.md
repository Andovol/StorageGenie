# StorageGenie recovery audit — initial inventory, not a completion verdict

Authorization: `docs/decisions/2026-10-13-recovery-audit-approval.md` (RECOVERY-D1). Scope: AUD-P1–AUD-P3 only. Author: Architect; self-reviewed preliminary source investigation, not a Coder receipt or product release rating.

## Baseline and evidence rules

Initial local source baseline: immutable `803cf522723158c65f9c4a6ba1ac3679da57f53a`, branch automation, clean before the local audit records were added. This baseline includes the SG-175 packet but predates its product repair. SG-175 source-sensitive facts MUST be revisited after its actual receipt/diff audit. Prior deployed image d5da5684 comes from SG-174's audited report; it is historical until a new runtime observation. No live image claim is derived from local HEAD.

At the first check following approval, forced-command `SG-175 --status` returned `result=activating id=SG-175 receipt=absent elapsed_s=838 budget_s=2100 stop_s=60 ends_by=2026-10-13T13:11:11Z`. This is an immutable observation, not a current status counter. Owner-facing deadline is 2026-10-13 16:11:11 Europe/Bucharest. No shared-branch push or second dispatch occurred during this observation.

Evidence levels: CURRENT SOURCE (observed at a named immutable commit); EXECUTED LOCAL (command and actual result); EXECUTED DEPLOYED (running build identity plus observations); HISTORICAL (prior evidence, needs refresh); UNVERIFIED INFERENCE (hypothesis awaiting discriminating observation). A source implementation or green mocked test is not enough to mark a user story WORKING. Finding statuses use OPEN / FIX QUEUED / RESOLVED / NEEDS DECISION / NOT FIXABLE; coverage uses working / partial / broken / absent / intentionally deferred / unverified, explicitly scoped.

Scope inventories are recomputed from `git ls-files`/`git ls-tree -r --name-only <base>` rather than a case-insensitive filesystem tree. Snapshot at baseline has backend application, backend tests, frontend routes/components/tests, blueprint, ADRs, accepted decisions, prior reviews, backlog, deployment and runbooks. No saved volatile count is a completion metric. Audit process must inventory every tracked product/config/test path and either review it or name an explicit exclusion; generated assets and historical dispatch logs need not be read indiscriminately. Requirements/decision history is followed by reference when it bears on scope.

## Product identity and scope reconciliation

Blueprint source: `inception/generic_asset_catalog_expiry_tracker_blueprint.md` §§1–14. A generic, evidence-backed household asset catalog with an Expiry Tracker plugin; camera-first responsive web; preserve original evidence; AI values remain proposals until accepted; unknown is valid. Existing journeys A–H are real prior art, not absent documentation.

Scope-changing decisions reviewed: `docs/decisions/2026-08-28-phase-0-approvals.md`, `2026-09-03-accepted-optimizations.md`, `2026-09-16-feedback-approvals.md`, `2026-09-16-l3-feedback-stage.md`; approved Phase 3 and ingest/enrichment specs; STATE current decision entries and backlog. Full priority reconciliation remains OPEN: historical phase grants are not blanket authority for new repair or deployment work.

| Scope identity | Source | Audit treatment |
|---|---|---|
| Responsive web rather than native app | Blueprint §1.4 | Preserve; audit mobile capture and all routes |
| Household scoping is not authentication | Phase 0 decisions; BM-8 accepted optimization; README trust boundary | Trace ingress and every route; do not call a household query param security |
| Manual planning trigger first | Approved Phase 3 spec, Settled decisions | Scheduled planning is intentionally deferred unless later decision reopens it |
| In-app expiry reminders before push infrastructure | UV-4 accepted optimization | Audit in-app behavior; external push is a separate scope decision |
| FTS5 brought forward | UV-2 accepted optimization | Audit search end-to-end, not an obsolete blueprint phase marker |
| Web enrich uses versioned proposals, provenance and human acceptance | Approved ingest/enrichment spec §§1–5 | Trace fetch → proposal → acceptance → readback; do not infer completion from Enrich button |
| Per-field acceptance and chat persistence are trigger-waiting | Current backlog | Classify as deferred/unfinished with original source; do not silently count as delivered or auto-authorize them |
| asset_type fallback for grounded chat rejected | STATE D-1012-10 | Preserve trusted classification boundary; trace usability of classification instead |
| Context Scene adapter work reopened, UI wiring separately parked | STATE D-1009-* / D-1012-6 | Inventory existing behavior, distinguish reopened transport from unapproved UI wiring |
| Provider/threshold/cap and privacy choices | Owner decisions, config and ADRs | Identify controlling decision before labeling a historical tradeoff a defect |

## Story register — outcomes and required proof

Priority below is Architect judgement, provisional pending the consolidated recovery scope decision. Core capture/review/catalog and truthful expiry state precede optional agent/presentation work. Every story requires usable UI + real API + persistence/readback + failure/recovery where applicable; a route existing is only inventory evidence.

| Story ID | User story / observable completion | Source / implementation inventory | Current evidence state and next proof |
|---|---|---|---|
| REC-ST01 | As a household member, select the correct catalog and begin without developer commands | Blueprint §1.2; App/Catalog/Capture/HouseholdSelector | UNVERIFIED overall; Capture renders “seed the database first” if household absent; audit initial/returning user path |
| REC-ST02 | Photograph/upload an item, see accepted/rejected files and processing progress, reach review | Blueprint journey A/§11; Capture, AssetForm, AssetImportModal, Inbox, evidence/jobs routes | PARTIAL SOURCE inventory; run isolated new/error/retry/cancel scenarios; deployed navigation read-only |
| REC-ST03 | Create an import without running it, then start it from the promised Inbox action | Import modal's unchecked help and process branch; jobs run route; Inbox/JobCard | UNVERIFIED INFERENCE gap, REC-ISS02; real render/route proof owed |
| REC-ST04 | Review source evidence and uncertain fields; accept/edit/hold/reject/merge/split with clear blockers | Blueprint A/§11.3; CandidateCard, ReviewPage, candidate services/routes | HISTORICAL BROKEN diagnostic in SG-173; SG-175 checkpoint pending; later classification/Resolve repair scope already recorded |
| REC-ST05 | Find an item with search/filter/sort and reopen a saved search without losing context | Blueprint B; Catalog, hooks, API assets/FTS/saved-searches | PARTIAL SOURCE inventory; audit multi-page populations, saved-search lifecycle, empty/error states |
| REC-ST06 | Inspect/correct details, attach evidence, see provenance and superseded history | Blueprint C/D; AssetDetail, AssetForm, EvidenceGallery, assertion/assets/evidence services | PARTIAL SOURCE inventory; real writes/readback in disposable fixtures, no live mutation |
| REC-ST07 | Record lifecycle/location/relationships without losing history or permissions | Blueprint C; lifecycle, location/relation routes; AssetDetail sections | PARTIAL SOURCE inventory; config flags default off, runtime effective state unknown; no new migration grant |
| REC-ST08 | Classify expiry-relevant items, enter unknown dates and see correct resolved/unresolved/non-applicable states | Blueprint E/§9.3; expiry plugin/API/ExpiryEntryForm | HISTORICAL BROKEN SG-173 diagnosis; classification UI and data-required Resolve still pending |
| REC-ST09 | See urgency/reminders and take an action that actually completes the underlying task | Blueprint F; UV-4; ExpiryPage/Inbox/expiry engine | PARTIAL SOURCE; SG-173 established correct ordering but missing unclassified visibility; audit task-type links and populations |
| REC-ST10 | Obtain proposed, grounded plans and explicitly confirm/dismiss them | Blueprint G; Phase 3 spec; PlanningPage/services/ledger | PARTIAL SOURCE inventory; zero paid calls; deterministic scripted-provider contract proof |
| REC-ST11 | Ask category questions, understand grounding/uncertainty and correct an answer | Blueprint H; Phase 3 spec; ChatPage/services | PARTIAL SOURCE; classification dependency and deferred persistence kept explicit |
| REC-ST12 | Enrich from sources and accept supported proposed fields with conflicts/history preserved | Approved ingest/enrichment spec; enrich route/services/WebAlternates | PARTIAL SOURCE; compare per-field expected flow with actual review implementation |
| REC-ST13 | Understand analytics and distinguish measured data from generated summaries | Blueprint §11.2; AnalyticsPage/service | PARTIAL SOURCE; empty/missing classification and fake-provider behavior need proof |
| REC-ST14 | Manage configuration/privacy/export/backup and recover the catalog/evidence together | Blueprint §§11.1/12/14; Settings/export/backup scripts | PARTIAL SOURCE; Settings UI only exposes model + reset; restore proof must use disposable storage |
| REC-ST15 | Complete the same journeys on narrow and wide screens with keyboard and understandable states | Blueprint responsive UX; existing DQ answers/theme/shell | UNVERIFIED deployed browser; audit every route, overlays, focus, reflow, errors and navigation |

## Initial findings — scoped evidence, not an implementation queue

| Finding ID | Observation and provenance | Status / confidence / destination |
|---|---|---|
| REC-ISS01 | App renders shared Nav for all routes while Catalog adds its own AppShell/AppHeader; Nav has eight route links, theme toggle and Phase 0 label. CURRENT SOURCE App.tsx + AppShell.tsx. | OPEN, design/viewport impact UNVERIFIED; journey/UI audit |
| REC-ISS02 | Import help promises unchecked jobs can be run from Inbox; modal only calls run when checked. Jobs POST creates CREATED job; explicit /run exists. Search frontend/src excluding tests found that import run call only in modal; Inbox offers Retry for FAILED, JobCard only selects. | OPEN, source mismatch observed; actual CREATED-job UI/route control required before defect verdict |
| REC-ISS03 | Settings route renders model selection and clear-household button; description calls itself household/connection settings. Blueprint §11.1 names privacy/storage/taxonomy/plugins/export/backup too. | OPEN, scope gap to reconcile, not claim whole backend lacks these capabilities |
| REC-ISS04 | Browser navigation to https://storagegenie.dynv6.net/ failed net::ERR_INVALID_AUTH_CREDENTIALS. No credential was entered or auth changed. | OPEN verification limitation; granted-lane deployed browser/readback investigation, no auth bypass |
| REC-ISS05 | Three selected local frontend suites initially hit missing local lucide-react; frozen npm ci restored it without package/lock changes. Post-restore import-modal/shell/ReviewPage: 41 tests passed in 3 files; actual captures in 2026-10-13-recovery-local-tests*.log. React Router future warnings remain. | RESOLVED local dependency failure; no product repair or deployed-journey pass inferred |
| REC-ISS06 | CURRENT SOURCE asset POST idempotency replay queries key globally and returns asset without household check; import POST replay explicitly checks household and rejects mismatches. | OPEN, UNVERIFIED INFERENCE of cross-household replay exposure; disposable real-route two-household probe + normal same-household control required |
| REC-ISS07 | CURRENT SOURCE catalog sort is explicitly over loaded page; backend owns q/category filtering. | OPEN audit question: global sort/pagination/empty behavior against product expectations; not yet a defect |
| REC-ISS08 | git ls-files '*.yml' '*.yaml' finds docker-compose.yml only at baseline. gh workflow list returns active Dependency Graph; check-runs at baseline total_count=0. | OPEN, observed verification coverage gap; inspect workflow definition/run provenance and external checks before concluding no CI capability |
| REC-ISS09 | SG-173 diagnosed blocked state/classification/Resolve/visibility faults; SG-175 addresses first fault. | FIX QUEUED under original scope; actual SG-175 receipt/diff audit/rating first; do not count proposed fix as delivered |
| REC-ISS10 | Location/relation routes and UI sections exist; settings defaults off. | OPEN deployment-state question; effective flags/schema readback required, never label absent from defaults |
| REC-ISS11 | SG-175's valid report discloses continued work after denied docker ps, inventing an optional-read exception; mandatory PB-2/packet have none. | OPEN; SG-175 rated 90 FLAG:SAFETY, acceptance/deploy held. Audit record SG-175_audit.md; approved read-only recovery audit continues without accepting this candidate |
| REC-ISS12 | SG-175 initial failed probe setup has no committed capture; final corrected fake-provider command is auditable. | OPEN evidence limitation; SG-180 isolation/privacy audit; do not infer initial run spend/safety from final script |
| REC-ISS13 | SG-175 evidence fingerprints cover names/sizes of empty/absent host paths, not actual production-volume contents. | OPEN measurement limitation; SG-180; temp-root/dependency isolation remains separate accepted evidence |
| REC-ISS14 | SG-175 benchmark script is ephemeral; worker-clock budget end differs from engine status deadline. | OPEN reproducibility/clock limitation; SG-182; stored fixture measurement is not a general performance rate |

## Audit execution boundaries

One stage register replaces another competing roadmap. The audit adds documents and focused isolated proof only; no new application gates, schemas, UI, services or persistent production state. A read-only finding may be reported immediately but repairs need their own already-existing or future scope authorization. Coder is the implementation/runtime audit executor on the granted VPS lane; Architect owns scope reconciliation and independent diff/evidence judgement.

Proposed sequential audit split (Architect judgement; IDs reserved locally only, no dispatch has occurred):

| Audit slice | Purpose | Required output |
|---|---|---|
| SG-179 | Deployed journey/UI audit across all routes; isolated writable story controls; mobile/desktop/keyboard state audit | Route/story coverage + actual-build browser provenance + responsive observations + non-vacuous disconnected-action controls |
| SG-180 | Ingestion/evidence/jobs/provider boundary audit | Input validation, original/derived integrity, idempotency, retry/cancel/failure behavior, lineage, privacy/spend contracts |
| SG-181 | Catalog/API/domain integrity audit | Household boundary controls, assertions/classification/lifecycle/search/pagination/concurrency/expiry/planning/chat/analytics reader-writer proof |
| SG-182 | Operations/test-trust audit and consolidation | Build/migration/backup-restore in disposable environments; CI/test coverage/control failures; prioritized recovery backlog and dependency plan |

After each slice: mapped receipt, immutable base→work diff, claims versus stored captures, independent audit, rating, every UNCLEAR/REMAINING destination. Scope boundaries may be made smaller when execution evidence warrants; no undocumented broadening. The existing project L2 checkpoint remains; audit-stage approval covers the named audit purposes, not product implementation.

Each packet must enumerate its actual targeted tests and isolated database/storage dependency path. No blanket full-suite launch implied by this approval. Metered application providers, production writes, service recreate, credential/config changes and backup restore into live storage are excluded. Existing opaque production IDs/customer content must be sanitized from committed evidence. Browser layout proof must identify actual viewport and rendered state; source-equivalent temporary Vite is not deployed frontend proof.

## Current next action

Complete independent local audit preparation while SG-175 is active; do not push shared branch. On the next authoritative activation, check its status/notes once, fetch/pull the actual receipt candidate, audit/rate and record remaining work. Then publish this approval/register with STATE pointer and prepare/dispatch the first bounded audit slice. Comprehensive audit and modern UI recovery are NOT complete at this initial inventory.

UPDATE: next authoritative check at 2026-10-13 15:59:47 Europe/Bucharest returned SG-175 done/inactive; mapped receipt fetched, checkout fast-forwarded to b789c148dc36336a88a8972e8d71db83645e445b. Immutable diff audited, product unchanged after tested work, 18 frontend checks independently passed. SG-175 is rated 90 with a safety flag for ignored privileged-denial STOP; see SG-175_audit.md. The checkpoint is recorded, not release acceptance. The already-approved read-only audit may inspect the held code; future repairs/deployment await consolidated disposition. No cancellation/re-trigger of SG-175.

SG-179 audit packet has now been drafted locally at `docs/packets/SG-179-recovery-journey-audit.md`, including the declared source gaps, actual-browser authentication limitation, real-route/component controls, data/evidence isolation and scope exclusions. Draft is not committed/pushed or dispatched; re-review it against SG-175's audited outcome before publishing. No SG-180..182 packet written yet; their assumptions must follow the prior audit evidence.
