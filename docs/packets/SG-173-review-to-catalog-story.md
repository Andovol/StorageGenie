# SG-173 — Live review-to-catalog story walk before the approved repair chain

`PB-1`–`PB-6` bind (`CODER.md` §14). Authoring date: 2026-10-12 (metadata).

**BASE REF: automation.** Report the resolved commit separately.
**DATABASE: production read-only; isolated disposable test database for mutations.**
**Restart: none.** No deploy, rebuild, recreate, production write or provider call.
**Autonomy: L2.** Owner-approved review-to-catalog repair (D-1012-14, quote "Approved."); bare-Resolve issue (D-1012-13) folded in. This first slice diagnoses the story; subsequent repair packets consume its observations. `PACKET.md` §5 requires diagnosis to be its own slice. Do not implement product behavior here.

Expected contract: recorded 0.46.0 == published contract-v0.46.0 == previous host echo 0.46.0 (`docs/worklogs/SG-172_report.md`, source `/home/andrei/storagegenie-contract/VERSION`). Re-read and echo the host contract version/source; explain any delta. Previous host rules_check exit 3 is documented in that report: distinguish unavailable local tag/auth from the independently verified contract bytes, do not silently repair host configuration.

## Why this exists

Expected starting point: SG-171 gating is served by SG-172, image prefix 9064d2ce (previous deploy report; re-observe running image). Owner called the complete flow "a real bad user experience design" and asked whether user stories were reviewed. Approval covers story walk first, then live blocked-derivation, classification in Review, Resolve semantics and expiry ordering. Existing findings are hypotheses, not an inventory:

- `frontend/src/components/CandidateCard.tsx`: Accept and keyboard acceptance currently depend on embedded `review_task_ids`; task resolution may leave those IDs stale.
- `frontend/src/routes/ReviewPage.tsx`: keyboard guard and post-accept `ExpiryEntryForm`; expected missing classification step.
- `backend/app/api/v1/review_tasks.py`: expected bare Resolve accepts no completion data and changes any task to resolved.
- `backend/app/api/v1/plugins.py` + `backend/app/plugins/expiry_tracker.py`: classification and manual expiry entry; expected existing reusable routes.
- `backend/app/services/expiry_engine.py`: accepted classification/date drive urgency; inspect its actual ordering and downstream consumers.
- Existing surfaces/tests: `frontend/src/routes/InboxPage.tsx`, `CatalogPage.tsx`, `frontend/src/components/ExpiryEntryForm.tsx`, `frontend/src/api/client.ts`, `types.ts`; `backend/tests/test_candidate_read.py`, `test_candidates.py`, `test_plugin_expiry.py`, `test_sg107_expiry_engine.py`; frontend Review/Inbox/ExpiryEntryForm tests. Enumerate actual consumers and fixtures on target; report differences from these expectations.

## G1 — Walk the served story and identify the first failed transition

`PG-DP-03` binds. Walk capture/import → candidate Review → task completion → Accept → classification → expiry entry → Catalog/expiry visibility. Start with live observations before diagnosing source. Use already existing rows, read-only UI navigation and GET requests only. Record the current running image, requested/resolved ref, and which version each observation exercised. Capture request status/body shape, contemporaneous server logs and read-only data predicates only where they discriminate between remaining explanations. Use approved credential tooling; never print or commit credentials, customer/domain contents, photos, names or transcripts. Commit sanitized structural observations only.

For each transition, record entry state, visible action, route, prerequisite, observable result and exact stop point. Distinguish OBSERVED LIVE, OBSERVED ISOLATED and UNVERIFIED. A source read cannot substitute for a live reproduction. If a live transition needs a write, stop that live transition and state the limitation; do not claim the entire live story passed.

## G2 — Exercise the complete story in an isolated environment

Use a disposable SQLite DB and synthetic evidence, proving isolation before any write. Reuse existing fixture infrastructure; identify its defining module before using it. No mutation of a shared fixture is authorized here. Exercise real routes/components where available rather than a copied policy function. Reproduce stale task membership, absence/presence of classification UI, data-less Resolve of an expiry reminder, and resulting expiry ordering. Controls: unresolved versus genuinely completed tasks; missing versus accepted classification; missing versus accepted expiry; resolved and unresolved rows together. Do not dismiss/resolve live reminders or seed production for this proof.

No metered inference or image calls. No full suite. Derive targeted existing tests from the actual consumers, run needed node IDs/file tests only, and record exclusions and why. An unavailable browser/runtime is reported as a limitation, never inferred green from source. New product tests/code are outside this diagnostic slice; disposable probes may live in the worklog namespace.

## G3 — Hand off the smallest sequential repair chain

Report which live hypotheses held, which did not, and root causes with defining files/symbols. Order the repair handoff: live blocked-state derivation and server/client consistency; classification action in Review using existing taxonomy semantics; task-type-aware Resolve with data-required expiry completion; expiry ordering with explicit missing/unresolved handling. Reorder only if measured dependencies require it, and explain why. Name callers/readers before recommending any artifact change (`G-T6`). Compare reuse of existing routes/components against one simpler viable alternative in a short table (`G-A7`); state machinery cost and what it replaces. Do not propose a parallel workflow or silently widen into Scene/UI wiring, unrelated PRs or taxonomy redesign.

## Constraints

- Scope ceiling: `docs/worklogs/SG-173*` only. Product, schema, migrations, deployment files, records of production objects and host configuration remain untouched.
- Production/read permissions are observational only. A denied privileged operation is a STOP (`PG-PR-03`), not an invitation to use another identity, mount, Docker route or permission change. Finished diagnostic work follows `PB-6`.
- No production POST/PUT/PATCH/DELETE, direct DB mutation, evidence-store write, host/credential change, paid API call or service restart. Health GET is allowed at start/end (`CO-92`); it does not authorize a datastore mutation.
- Per-command bounds: ordinary reads 120s; isolated test commands 600s (uncalibrated author judgement, visible timeout finding). Kill/report a hung command; no bound approaches the lane's 900s idle kill. No polling watcher or interactive prompt.
- The lane owns the whole-run budget. If time is short, publish observed work and explicit unanswered transitions rather than compressing uncertainty into a pass. No whole-slice budget field in this packet.

## Acceptance criteria

- A1: sanitized served-story observations identify exact transitions and current image; each missing observation has an explicit limitation. Live findings include direct evidence that distinguishes their alternatives.
- A2: isolated route/component story demonstrates relevant failure/control pairs, with DB isolation, actual commands, outputs and nonempty inputs recorded. Each suspected defect receives CONFIRMED / DISPROVED / UNVERIFIED with evidence.
- A3: repair chain names defining symbols, consumers, completion semantics and targeted verification needed; preserves D-1012-13 within D-1012-14. No product change or live write is claimed/performed.
- A4: requested ref + resolved hash, contract echo, start/end health, constraints, elapsed transitions, remaining work and notes-ref receipt are reported. Every UNCLEAR item receives an explicit disposition.

## Report and receipt

First token `SG-173`. Write `docs/worklogs/SG-173_report.md` plus sanitized diagnostic artifacts under `docs/worklogs/SG-173*`. Report actual contract identity, resolved base, WORK_HEAD and all scope limitations. Close with FIRST READ / DURING EXECUTION / REMAINING. State product code unchanged, running service unchanged, production writes none.

Use the lane's bound notes-ref receipt mechanism (`CO-60`): commit with `Dispatch-ID: SG-173` trailer; publish a note on `refs/notes/storagegenie-coder-reports` whose first line is `Dispatch-ID: SG-173 | Report: docs/worklogs/SG-173_report.md` and includes `Work-HEAD`; push automation and that notes ref. Read back the note on remote and report the commit it annotates. The legacy finalize_dispatch_report.sh is retired for this lane; do not use it.
