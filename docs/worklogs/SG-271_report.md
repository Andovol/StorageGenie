SG-271 | model opencode-go/muse-spark-1.3-contributor effort=xhigh (STATE.md ordered work item 2, rotation: SG-295 was Haiku so SG-271 is Muse) | workdir /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation resolved 29df408ec296cdf54a5e6b66eb80efee6e10b689 | WORK-HEAD 23cf917e818b0ed887f0562eaae9a2d2b101a06e (pre-amend; pushed HEAD quoted in push evidence)

## What this slice did
Carried the AI's work through review, classification and the Expiry page: no false date task for non-date unknowns (G1); a committed candidate reads its item id on first load and reload with no decisions offered and Inbox links to the item (G2, closes SG-275 I1); the AI's proposed date survives classification with Accept date and the proposed shelf life preselects with one Confirm that never classifies alone (G3/F4/F5/F12); one name per concept (G4/F7); deliberately dateless items leave Unresolved with a quiet count (G5/F8); skipped steps read as skipped in plain words (G6/F11). No schema, migration, Dockerfile, compose, lockfile, dependency, .env, live DB, stored files, host, provider, running-container or deploy bytes.

## Retry note (the one retry this slice gets)
First run (2026-11-09) was killed at the 2100 s budget past its publish point in the optional screenshot goal with nothing pushed. Root-cause fixes applied here: screenshot goal removed (moved to SG-273), publish point 1300 s treated as a stop rule. Unfinished work refs read as reference only: `refs/wip/SG-271/20261109T201913Z` (37 paths incl. untracked) and `refs/wip-tracked/SG-271/20261109T201913Z`. No `refs/wip/*` or `refs/quarantine/*` ref was pushed, deleted or moved.
Took from the reference: the full product diff (candidates `requires_date_task` gate + split-child gate; `committed_asset_id` derivation; `classify_asset` proposed-date keep via `_resolve_dated_expiry` + bare-date adoption; engine `dateless` quiet count with `needs_evidence` preserved for truly missing; Review/Inbox/AssetDetail/Expiry label and flow changes; `asset_id` on job candidate list; test updates to `test_plugin_expiry.py`, `test_sg107_expiry_engine.py`, `AssetForm.test.tsx`, `drawer.test.tsx`, `AssetDetailPage.test.tsx`, `ExpiryPage.test.tsx`, `ReviewPage.test.tsx`; eval baseline number move) and the six new test files (`test_sg271_flow.py`, `Review/Inbox/AssetDetail/Expiry/CandidateCard .sg271.test.tsx`). Changed vs the reference: re-ran every test and gate from the base (FAIL logs below are fresh, not carried); dropped the packet-file and coder-profile edits present in the wip snapshot as out of scope; kept `backend/eval/baseline_sg029_frozen.md` with justification below; did not run Chrome or any app server.

## G0 preflight — PASS
`DOCKER_CONFIG` writable scratch, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-271/docker.sock`, `docker version` shows Server 29.9.2, `docker run --rm busybox true` rc 0. `PATH` included `backend/venv/bin` for make invocations. Health `curl -s http://127.0.0.1:8003/v1/health` 200 at start (`{"status":"ok","db":"ok","storage":"ok"}`) and 200 at end. Scratch `output/SG-271-scratch/` removed by exact path; `output/` itself untouched.

## G1 — No false date task (backend, load-bearing) — DONE
Hypothesis tested first: `needs_evidence` is provider-global; food prompt sets it for null `expiry_date`, cosmetics prompt for unknown `opened_date`; schema only requires non-empty `unknowns`. Established: the date task collects an expiry date, so only `items.<n>.expiry_date` unknowns open one.
- `requires_date_task(unknowns)` added (`backend/app/plugins/expiry_tracker.py`): true iff some entry's last dotted segment is `expiry_date`.
- `build_candidate_from_extraction` gates on `requires_date_task(extraction.unknowns)`; `_attach_split_child_date_tasks` gates per child on `requires_date_task(child ai_unknowns)`; `apply_extraction_result` maps non-date unknowns to `(None, None)`.
- No new task kind; opened-date case opens none (noted under REMAINING if a kind is ever wanted).
- Eval baseline `backend/eval/baseline_sg029_frozen.md` updated only in its frozen numbers (`correction_created`/`audit_writes` 6→4 for `sg029-09`/`sg029-10` carrying only `opened_date` unknowns) — why: the two dropped bridge tasks are the intended fix, scores unchanged. Justification for touching a file outside `backend/app|tests, frontend/src`: it is the frozen record of this exact behavior; leaving it stale would misreport the suite.

## G2 — A committed candidate leads to its item — DONE (closes SG-275 I1)
Id derived on every read, nothing stored (no schema/migration need encountered).
- Computed: `committed_asset_id(db, candidate)` (`backend/app/services/candidates.py`): proposal `asset_id` if live and same household → review step `committed_assets[candidate.id]` if same household (SG-270 map) → commit step output (`candidate_id` match + `created is True`) if same household; foreign-household ids read back as none.
- PG-SC-02 hops: `committed_asset_id` → `GET /v1/candidates/{id}` serializer (`backend/app/api/v1/candidates.py`, replaces `proposal.get("asset_id")`) → response `asset_id` → frontend `Candidate.asset_id` (pre-existing) → ReviewPage (`candidate.asset_id` branch) and keyboard guard; and `committed_asset_id` → `_candidate_list_item(db, row)` (`backend/app/api/v1/jobs.py`, signature now takes `db`) → `JobCandidateListResponse.items[].asset_id` → frontend `JobCandidate.asset_id` (new optional) → InboxPage candidate row. Household checked at computation, as the commit path does.
- ReviewPage: `candidate.asset_id` renders `In your catalog` + `Open item` link, offers no Accept/Edit/Hold/Reject (buttons and `a`/`r` keys gated). Inbox: `candidate.asset_id` renders `Open item` → `/assets/:id`, else `Review` → `/review/:id`. Repeat edit has no screen (API repeat-edit behavior unchanged from SG-275).

## G3 — The AI's date and category survive — DONE (F4, F5, F12)
- F4: `classify_asset` now resolves via `_resolve_dated_expiry`: accepted date wins, then active proposed (kept, no manual task), then the candidate-committed bare `expiry_date` adopted into the prefixed proposed slot via `_adopt_candidate_committed_date` (valid date only, AI evidence kept), else observed, else `unknown` + manual task. Non-perishable branch still writes the deliberate accepted null when an active signal exists (now counting the committed AI date as a signal). Expiry engine treats `proposed` as its own unresolved reason; the Expiry page label reads `Date proposed` (was `Proposed`), so the item appears under Unresolved as proposed, never as `No date`. Asset page shows the existing `ExpiryEntryForm` Accept date (proposed state) with the AI value prefilled plus the edit form as the alternative.
- F5/F12: `category_proposed` (promoted at `candidates.py:~704`, stored as `review_state=proposed`) preselects the asset Classification control (`effectiveCategory = selected || suggested`) with a `The AI suggests … Confirm below` note (or an unmapped-name note), `Save shelf life` is the user's explicit Confirm; ReviewPage after a fresh accept shows `The AI suggests …` with one `Confirm shelf life` that calls `classifyAsset` and reports success/failure with an item-page fallback. Nothing classifies without the user's confirmation; no-proposal items behave as today.

## G4 — One word per concept — DONE (F7, labels only)
`asset_type` capture concept = `Kind of item`; expiry classification concept = `Shelf life` (+ `Suggested shelf life` for the AI proposal). No field, value or API renamed.
- `Kind of item`: `frontend/src/components/AssetForm.tsx:144` (capture label), `frontend/src/components/shell/ItemInspectorDrawer.tsx:317` (drawer label), `frontend/src/components/CandidateCard.tsx:29` (`asset_type` field label via `FIELD_LABELS`).
- `Shelf life`: `frontend/src/routes/AssetDetailPage.tsx:468` (section `h3`), `:476` (select `aria-label`), `:482` (`Select a shelf life…`), `:494` (`Save shelf life`), `:365` (`Shelf life saved.`), `:471` (`No shelf life options are available.`), `:500/:505/:510` (suggestion/help notes), `frontend/src/routes/ExpiryPage.tsx:155,157` (`Shelf life filter` label + aria), `frontend/src/routes/ReviewPage.tsx:70,76` (`Confirm shelf life` / messages), `frontend/src/components/CandidateCard.tsx:30` (`Suggested shelf life` for `category_proposed`).
- Tests updated to the new names: `AssetForm.test.tsx:140`, `drawer.test.tsx:168,185,315`, `AssetDetailPage.test.tsx` (`Shelf life` label/buttons/messages), `ExpiryPage.test.tsx:296`.

## G5 — A deliberately dateless item stops nagging — DONE (F8)
Distinguisher keyed to the decision, not the label: an accepted null expiry (`_is_null_value`) — written when the user classifies Non-perishable or clears the date — or a Non-perishable classification slug. `compute_status` (`backend/app/services/expiry_engine.py`) counts those as `summary.dateless` and continues them out of `unresolved_rows`; truly missing dates still list (`needs_evidence`/`unparseable`/`proposed`). Expiry page: Unresolved section keeps its list and adds a quiet count note (`N items are set to need no date — nothing to do here`).

## G6 — Skipped steps say so — DONE (F11, kept: time allowed)
No backend state change. `InboxPage.tsx` `stepStatus(step)`: output `status=skipped` reads `Skipped — the AI is turned off` for `consent_disabled`, `Skipped — <reason>` for other reasons, else `Skipped`; non-skipped still renders raw `step.state`. Not dropped.

## G7 — retired in the retry
No Chrome, no local app server, no screenshots in this slice (moved to SG-273).

## Design section (per screen; tokens only, both themes, plain words, one primary action)
No new literal colours, no font sizes below each page's body size, no one-off shapes; every touched screen uses `frontend/src/theme/tokens.css` tokens and `THEMED_CONTROL_CLASS`/`CONTROL_STYLE` (Inbox/Review) or the page's existing themed classes (`bg-card`, `border-border`, `text-foreground`, `text-muted-foreground`, `text-link`, `text-success`, `text-danger`, `bg-primary`, `focus-ring`). No new text/link colour pair was introduced, so `frontend/src/theme/theme.test.tsx` needed no addition (its ≥4.5:1 bar still passes in the 345-test frontend suite, light and dark via `ThemeProvider`).
- ReviewPage: committed state is a `bg-card border-border` panel (radius 10, existing card language), status line `In your catalog` + muted plain-words explainer `This suggestion is already an item. Decisions are finished — nothing left to accept or edit here.` + one primary control `Open item` (`text-link`). Fresh-accept suggestion is `The AI suggests <value> as the shelf life.` + one `Confirm shelf life` (`THEMED_CONTROL_CLASS`), success in `text-success`, error in `text-danger` with item-page fallback. Why: the committed user needs certainty and one exit; the fresh user needs one explicit confirm, never auto-classify.
- InboxPage: candidate row keeps `name · state` and swaps `Review` for `Open item` when `asset_id` is present; skipped steps read `Skipped — the AI is turned off` in the existing step chip (`bg-card-muted`). Why: the link target must match reality; the skip reason must name the switch a household user controls.
- AssetDetailPage: `Classification` → `Shelf life` heading/labels/options/messages; suggestion notes in `text-muted-foreground` 12px (page's existing note size): `The AI suggests X. Confirm below, or pick another shelf life.` / unmapped variant naming the raw suggestion without guessing. One primary `Save shelf life` (`bg-primary`). Proposed date keeps the existing `ExpiryEntryForm` with `Accept date` (AI value prefilled) + edit form alternative. Why: two concepts finally have two names; the AI stays a suggestion until the user presses one button.
- ExpiryPage: `Category filter` → `Shelf life filter`; reason label `Proposed` → `Date proposed`; quiet dateless count in `text-muted-foreground` 12px under Unresolved. Why: `Date proposed` tells the user a date exists awaiting accept; the quiet count keeps deliberate dateless items findable without nagging.
- CandidateCard/AssetForm/Drawer: `asset_type` → `Kind of item`, `category_proposed` → `Suggested shelf life` via `FIELD_LABELS`; no raw `needs_evidence`/`asset_type`/`COMPLETED` strings shown (step states still raw except skipped, per G6).

## Tests and the gate
- New backend `backend/tests/test_sg271_flow.py` (7 tests: G1 cosmetics-opened-none + food-missing-one + split-child gates; G2 committed-carries/fresh-session + uncommitted-none + cross-household-403; G3 proposed-date-kept + category-unconfirmed; G5 dateless-out/missing-in). New frontend: `ReviewPage.sg271` (committed panel + fresh-accept confirm), `InboxPage.sg271` (item link + skipped-consent), `AssetDetailPage.sg271` (Accept date prefilled + preselect + unmapped), `ExpiryPage.sg271` (dateless quiet + proposed label), `CandidateCard.sg271` (G4 labels).
- FAIL-then-PASS: base `5 failed, 2 passed` (backend) / `5 files failed, 8 failed 1 passed of 9` (frontend); candidate `7 passed` / `5 files passed, 9 passed`. Logs: `docs/worklogs/SG-271_fail_backend.log`, `SG-271_fail_frontend.log`, `SG-271_pass_backend.log`, `SG-271_pass_frontend.log`.
- Full suites on candidate: backend `793 passed, 2 deselected` + image proof `2 passed, 6 deselected` (`docs/worklogs/SG-271_backend_suite.log`); frontend `35 files passed, 345 tests passed` (`SG-271_frontend_suite.log`).
- Affected twice: backend `test_sg271_flow + test_plugin_expiry + test_sg107_expiry_engine` → `48 passed` twice; frontend 10 files → `84 passed` twice.
- `ruff check` on all 8 changed backend files: clean. `eslint` on all 19 changed frontend files: clean (repo-wide pre-existing `App.household-nav.test.tsx` error untouched). `tsc --noEmit`: clean. Frontend `npm run build`: rc 0 (`SG-271_frontend_build.log`).

## Acceptance criteria
- A1: non-date unknown opens no date task, missing required date still does — FAIL-then-PASS shown.
- A2: committed item id survives fresh-session reload, Review offers no decision, Inbox links to item — hops listed, tests pass.
- A3: proposed date survives with Accept date; proposed shelf life preselects, never applied without Confirm.
- A4: one name per concept, every occurrence listed, no API/value renamed.
- A5: deliberate dateless off Unresolved with quiet count; truly missing still on it.
- A6: tokens only, both themes, no new colour pairs (contrast test untouched and green); design section above names each change and why.
- A7: FAIL/PASS logs committed; suites green; affected twice; tsc/lint/build clean; counts quoted.
- A8: scope is the listed files only; zero schema/migration/Dockerfile/compose/lockfile/dependency/.env/live-DB/stored/host/provider/container/deploy bytes.
- A9: preflight proven; health 200 start and end.
- A10: vacuity — checked: no date task on cosmetics candidate with known expiry (test asserts 0), no Accept on committed candidate after reload (test asserts no decision buttons/keys), no proposed→unknown replacement (test asserts `proposed` kept + `review_task None`), no Non-perishable under Unresolved (test asserts absent). None observed.
- A11: see last line.

## Changed files
Product: `backend/app/services/candidates.py`, `backend/app/api/v1/candidates.py`, `backend/app/plugins/expiry_tracker.py`, `backend/app/services/expiry_engine.py`, `backend/app/api/v1/jobs.py`, `frontend/src/api/types.ts`, `frontend/src/routes/{ReviewPage,InboxPage,AssetDetailPage,ExpiryPage}.tsx`, `frontend/src/components/{CandidateCard,AssetForm}.tsx`, `frontend/src/components/shell/ItemInspectorDrawer.tsx`, `backend/eval/baseline_sg029_frozen.md` (justified above). Tests: `backend/tests/test_sg271_flow.py` (new), `test_plugin_expiry.py`, `test_sg107_expiry_engine.py`, `frontend/src/routes/{ReviewPage,InboxPage,AssetDetailPage,ExpiryPage}.sg271.test.tsx` (new), `frontend/src/components/CandidateCard.sg271.test.tsx` (new), `AssetForm.test.tsx`, `shell/drawer.test.tsx`, `AssetDetailPage.test.tsx`, `ExpiryPage.test.tsx`, `ReviewPage.test.tsx`. Another file found necessary: none beyond this list. Evidence: `docs/worklogs/SG-271_*` only.

## Elapsed (≈1100 s budget; publish point 1300 s stop rule)
Start 20:29:19 UTC; this report ~20:36 UTC (~420 s total). Phases over 60 s: `make backend-test` incl. image build+proof ~110 s (20:32:14→20:34:03). All other phases under 60 s (preflight+reads ~70 s total but split across calls; FAIL/PASS runs ~3–5 s each; frontend suite ~30 s; affected-twice ~8–15 s each; lint/tsc/build ~3–12 s). Publish point 1300 s (20:50:59) respected with wide margin.

## Prior reports' open items
- `SG-270_report` false date task: fixed by G1 (`requires_date_task`).
- `SG-270_report` accepted-candidate reload missing `asset_id`: fixed by G2 (`committed_asset_id` on read + list).
- `SG-275_audit` I1 (repeat edit on committed row): closed by G2 (no decision screen on committed candidate).
- SG-269 F4/F5/F7/F8/F11/F12: done above. F3/F9/F10/F13 are not this slice.

## Contract chain
Recorded `0.58.0` (`AGENTS.md`) == published `contract-v0.58.0` == host contract echoed here from `/home/andrei/storagegenie-contract/CODER.md` line 3:
**Contract version: 0.58.0** — **echo this line verbatim in your receipt.** It is the only proof that you
read this file rather than assumed its contents.

## Constraints (one line each)
- BASE `origin/automation`; two fields reported (ref + resolved commit).
- Temporary test databases only; no live DB read or write.
- No deploy/restart; rider SG-296 owns it; live app untouched (`PG-PR-05`).
- Scripted provider only; no key/.env/spend.
- Design tokens/themes/plain-words/primary-action rules honored per screen above.
- Scope ceiling honored; one justified eval-baseline touch; no product file outside `backend/app|tests`, `frontend/src` beyond evidence.
- No browser/app server/new image pulled or run; only preflight/`make`/tests/`tsc`/lint/build runtimes.
- Evidence in `docs/worklogs/SG-271*` only; scratch removed by exact path.
- Denied-operation STOP rules honored; no STOP triggered.
- Hang bounds respected (all commands within their bounds).
- Budget/publish-point stop rule respected (finished ~420 s, publish 1300 s).
- Report ends with `Verification: PASS` and goes to `docs/worklogs/SG-271_report.md` with trailer `Dispatch-ID: SG-271`.

## REMAINING
- None in this slice. If the opened-date decision ever needs a task kind, say so in a future slice (G1 deliberately opens none).
- UNCLEAR: none.

Verification: PASS
