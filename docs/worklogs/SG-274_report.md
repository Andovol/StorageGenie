result=done id=SG-274 inactive
debug-report-begin
SG-274 — Q1 PICK: O2, accept and atomically transfer the unresolved date obligation to the committed asset. Do not mark the date task satisfied merely because acceptance succeeded.

**Contract version: 0.56.0**
Identity (`PB-4`): model=unknown; reasoning effort=unknown. Process arguments/provider metadata were not available through the supplied tools.
Working directory: `/tmp/dispatch-review.tvwQgi`.
Requested BASE ref: `origin/automation`.
Resolved BASE commit: unknown. The supplied directory has no visible Git metadata, and no shell tool was available to resolve the ref. Repository identity is declared in `AGENTS.md:13`, not independently verified.
Verification limitation: this is an advisory source review, not a verified review of a named BASE commit. That provenance requirement remains blocked (`PB-6`); no commit hash is inferred.

**Extra Files**
Files read beyond G1 steps 1–3:
- `.contract/CODER.md`: required contract, including `PB-1`–`PB-6`.
- `.contract/SOURCE`: cached contract provenance and version.

Directory listings, not file-content reads: repository root and `.contract/`.
Filename searches returned paths under `docs/decisions/`; none of those files was opened or used.

**Q1**
**(a) PICK: O2.** Keep the candidate's date task open until commit; exempt only that transferable obligation from acceptance blocking. In the asset-creation transaction, re-point it to the asset, update its actionable payload, and preserve task identity/history. An asset date task already present must be coalesced without pretending a date was supplied. Other candidate tasks continue to block.

This is a design recommendation, not measured implementation behaviour.

**(b) WHY**
- The obligation belongs to an item's expiry data, not permission to create the item. The existing completion path requires an asset and classification: `backend/app/plugins/expiry_tracker.py:705-715`. Opinion: acceptance should acknowledge the item while leaving its unknown date visible and actionable.
- Both backend gates currently reject every open candidate task: `backend/app/api/v1/candidates.py:50-51` and `backend/app/services/candidates.py:969-979`. The UI separately blocks all task IDs, including keyboard acceptance: `frontend/src/components/CandidateCard.tsx:48,91-99`; `frontend/src/routes/ReviewPage.tsx:49`. Changing only one gate would not remove the dead end.
- Re-pointing preserves the distinction between “still unknown” and “completed.” It respects the decided prohibition on bare resolution (`backend/app/api/v1/review_tasks.py:15-20`) without adding a second date-writing path.
- O1 duplicates expiry entry before the asset/classification prerequisites exist. O3 turns “AI could not read it” into a user declaration the evidence does not establish. O4's mapping is not sufficient alone: `apply_extraction_result` uses global `needs_evidence`, writes unknown, and has no classification or existing-date guard (`backend/app/plugins/expiry_tracker.py:400-425`).
- The item page already offers classification before date entry (`frontend/src/routes/AssetDetailPage.tsx:447-475,540-550`). Opinion: connect acceptance directly to that existing sequence rather than introducing another review-page form.

**(c) Missed Option**
Classification-driven deferral: stop producing candidate date tasks, preserve extraction uncertainty, and let confirmed expiry-bearing classification create any necessary asset task. Unlike O4, this does not unconditionally call `apply_extraction_result` on commit.

Evidence: classification already creates the unknown assertion/task only when the category has expiry and lacks an accepted date (`backend/app/plugins/expiry_tracker.py:450-498`). I prefer O2 for this slice because classification-driven deferral could otherwise silently lose the reminder: unclassified assets are omitted from Expiry (`backend/app/services/expiry_engine.py:263-266`).

**(d) Riskiest Unverified Premise**
That `needs_evidence` reliably means “this item's expiry date requires attention.” The candidate producer tests only that global boolean (`backend/app/services/candidates.py:757-764`); split children derive it from any item-prefixed unknown (`:1136-1157`). If the flag also covers unrelated missing facts or another item, carrying a mandatory date task forward perpetuates a false obligation. Its schema/provider semantics were not independently inspected in this pass.

**Q2**
Recommendations below are opinion informed by the cited source behaviour. Paths abbreviated here: `C` = `backend/app/services/candidates.py`; `E` = `backend/app/plugins/expiry_tracker.py`; `A` = `backend/app/api/v1/candidates.py`.

| Edge | What Should Happen Under O2 | Behaviour Shown by the Source |
|---|---|---|
| Also holds `candidate.multi_item` | Multi-item ambiguity still blocks accept/edit-to-commit. Split first; only expiry work is deferrable. | Both tasks can be created together, `C:742-770`; both gates currently block any open task, `A:50-51`, `C:969-979`. |
| Split children and origins | Transfer the origin's obligation into item-specific child obligations without claiming a date was entered. Only relevant children inherit it; retire the origin task with explicit successor links. Asset commit transfers each child's obligation independently. | Children share evidence, carry item-specific unknowns and empty task lists, `C:1131-1173`; split resolves only `candidate.multi_item`, `C:1176-1202`. Manual entry can later resolve origin tasks merely through shared evidence, `E:660-702,736-755`. |
| Merge | Permit an expiry-only loser obligation to follow the survivor; coalesce it without discarding uncertainty. Do not weaken unrelated loser-task checks or auto-accept the survivor. | Any loser task outside `identifier_collision` blocks merge, `C:534,1274-1285`; survivor keeps fields and unions evidence, `C:1228-1237,1288-1305`. |
| Hold | Keep the candidate and obligation pending; create no asset or asset task. A later decision must still use the same narrow exemption. | Hold returns before task gating and leaves tasks untouched, `A:45-48`. |
| Reject | Create no asset. Remove the date obligation from actionable work with an audited “candidate rejected” disposition, not a “date supplied” resolution. Preserve its history. | Reject is terminal but does not update tasks, `A:42-48`; open task queries do not join candidate state, `backend/app/api/v1/review_tasks.py:37-55`. |
| Edit decision | Apply the same expiry-only exemption as Accept because Edit currently commits too. Editing a generic date field must not count as validated completion of the plugin's expiry assertion. | Edit updates proposal fields, sets `edited`, then resumes the job, `A:53-78`; manual entry uses parsing and the plugin write path, `backend/app/api/v1/plugins.py:194-209`. |
| `duplicate_of_asset` | Use the existing target, not an invented new asset. If its date remains genuinely unresolved, transfer/coalesce there. Never overwrite an accepted date or explicit no-date decision with extraction uncertainty; record why the candidate obligation is superseded. | Duplicate commit returns the target without creating or updating an asset, `C:981-986`; expiry classification preserves a valid accepted date, `E:460-462`. |
| Candidates already open | Derive eligibility from live tasks, not only new producer output or stored task-ID snapshots. Apply transfer on decision/commit to existing candidates; separately account for terminal split/rejected origins. No schema migration appears necessary from the reviewed code, but this is inference, not a database finding. | Live projection queries task subject, household and status, `C:946-963`; decision and commit query the same class of rows, `A:50-51`, `C:969-976`. Live affected-row count remains unknown. |
| Still unclassified | Accept, retain the obligation, and open the item with an explicit “choose category, then enter date if applicable” next action. No-expiry classification legitimately discharges it. Do not present a date-only link that leads to a hidden form. | Manual entry refuses unclassified assets, `E:708-713`; date form is classification-gated, `frontend/src/routes/AssetDetailPage.tsx:540-550`; no-expiry classification resolves asset date tasks, `E:482-498`. |
| Added: accepted date / explicit no date | Preserve either accepted state; do not manufacture a replacement unknown assertion. Distinguish absent, unknown, accepted date and intentional null. | `E:614-657` explicitly supports user-chosen no date; `E:400-425` unconditionally writes unknown when its flag is true. |
| Added: retries and partial failure | Asset creation, obligation transfer and commit result must be atomic and idempotent. Retry must return the same asset, never leave a moved task attached to a rolled-back asset or create another asset. | Decision state is committed before job execution, `A:65-75`; `C:966-990` itself contains no already-committed-asset guard. Caller-level idempotency remains unverified. |
| Added: selecting a split child | Prove that deciding each child commits that child, not the retired origin; otherwise task transfer cannot rescue the split journey. | `commit_job_candidate` selects the first candidate by job creation order rather than the decided candidate, `C:993-998`; children share the job, `C:1165-1170`. Actual job-runner handling was not inspected. |
| Added: household isolation | Transfer/coalescing must stay within the candidate's household and verify the target asset's household, particularly for duplicates. | Candidate task queries are household-scoped, `C:953-959,969-975`; the duplicate return itself checks only that the target ID is a string, `C:981-986`. |
| Added: every UI acceptance path | Use blocking-task semantics consistently for buttons, keyboard and both backend gates; keep unresolved expiry tasks visible after acceptance and refresh the queue. | Button blocking uses all IDs, `CandidateCard.tsx:48`; keyboard repeats that condition, `ReviewPage.tsx:49`; decision success currently invalidates only the candidate query, `ReviewPage.tsx:42`. |

**Whole-Design Check**
The wrong abstraction would be “every unreadable extraction requires an expiry date before capture can finish.” Capture identity, classification and date completeness are distinct: asset creation does not classify (`C:850-905`), classification may legitimately require no date (`E:482-498`), and the asset already supports explicit no date (`E:614-657`). Opinion: Pantry must allow an honest unknown without demanding fabricated data.

O2 fails as an end-to-end design if deferred work becomes invisible. Unclassified assets disappear from Expiry (`backend/app/services/expiry_engine.py:263-266`), and Review currently ignores the acceptance result except for candidate invalidation (`frontend/src/routes/ReviewPage.tsx:42`). The same-slice review-to-item link and corrected Inbox routing are therefore essential, not decorative.

Intentional no-date also remains misleading downstream: an accepted null becomes `dateless` in unresolved results (`backend/app/services/expiry_engine.py:269-275`). That does not justify blocking capture, but means task transfer alone cannot establish a coherent “nothing left to do” Pantry experience.

A further integrity finding: the generic resolve endpoint rejects empty payloads but accepts an arbitrary nonempty payload without writing expiry data (`backend/app/api/v1/review_tasks.py:107-131`). This is a data-integrity bypass of the stated rule, not an alternative solution. Introducing a reason-only resolve as the fix would exploit that weakness.

No objection is raised to the already-decided bare-resolve prohibition or asset-page date path. F4/F5/F12 ownership is not reopened. The observations above identify integration conditions, not permission to widen this build slice.

The supplied dated-food log is not isolated evidence for the selected item's Expiry visibility: its candidate read reports an asset ID different from the acceptance result (`docs/worklogs/SG-269_j3j4.log:63,113`), and its Expiry output contains another same-name dated row (`:219`). I used the explicit classification skip in source, not the aggregate product-name output, for that conclusion.

**Closing**
Read the project configuration, blind context pack, every file in its “Where it lives” table, and the two disclosed contract files. Deliberately did not read `STATE.md`, decision-file contents, `docs/backlog.md`, Phase B material, live data, credentials or external sources.

I wrote nothing: no files, database access, tests, health probes, restart, provider call, commit, push or receipt note. The final message is the only report; publication is the engine's responsibility.

UNCLEAR FIRST READ: whether global extraction uncertainty is specifically expiry uncertainty.
UNCLEAR DURING EXECUTION: source confirms the dead end but reveals split-child routing and nonempty-resolve risks.
UNCLEAR REMAINING: resolved BASE commit, runtime identity metadata, live affected rows, caller-level idempotency and extraction-flag semantics.
debug-report-end
