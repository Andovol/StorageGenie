# SG-271 — The AI's proposals carry through review, classification and the Expiry page, and a committed candidate leads to its item

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** This slice does not deploy; its rider SG-296 does. Until then the live app stays as it is (`PG-PR-05`); nothing here needs a schema change.
**Provider: none.** No key, no `.env`, no spend. Scripted provider only.

**Contract chain:** recorded `0.58.0` (`AGENTS.md`) == published `contract-v0.58.0` == the host's contract, echoed by this report from `/home/andrei/storagegenie-contract/CODER.md` line 3. A different echo is a finding.

**Approval:** owner, stage C (*"d14 ok"*, L3); this slice is `STATE.md` ordered work item 2, re-stated by the owner on 2026-11-09.

**RETRY — the one retry this slice gets.** The first run (2026-11-09) was killed at the 2100 s budget past its publish point, still in the optional screenshot goal, with nothing pushed (`SG-271.dbg`: *"NEXT ACTION: change the packet"*). Root-cause fixes here: the screenshot goal is removed, and the publish point is earlier and a stop rule. **Its unfinished work is on this host at `refs/wip/SG-271/20261109T201913Z`** (37 paths, tracked and untracked) and `refs/wip-tracked/SG-271/20261109T201913Z`. **Read it as a reference, never as verified work:** you may bring its changes across, but every test and gate in this packet runs again from the base, and the report says what you took and what you changed. Do not push, delete or move any `refs/wip/*` or `refs/quarantine/*` ref.

**Previous reports' open items that are this slice:** `docs/worklogs/SG-270_report.md` (`needs_evidence` false date task; accepted-candidate reload has no `asset_id`), `docs/worklogs/SG-275_audit.md` I1, and SG-269 findings F4, F5, F7, F8, F11, F12 (`docs/worklogs/SG-269_findings.md`, table rows, read them). F3, F9, F10, F13 are **not** this slice.

## Design is a requirement, not polish

The owner, verbatim: design quality is *"a first-class requirement of every theme and screen slice"*, and for this session *"design, look and feel are very important, so hold every screen to that."* Every screen this slice touches:

- uses only the theme's tokens and shared control classes (`frontend/src/theme/tokens.css`, `THEMED_CONTROL_CLASS` / `CONTROL_STYLE` as `InboxPage.tsx` uses them); **no new literal colours, font sizes below the page's body size, or one-off shapes**;
- works in light and dark (`ThemeProvider.tsx`); any new text/link colour pair is added to the contrast test in `frontend/src/theme/theme.test.tsx` (≥ 4.5:1, its existing bar);
- says things in plain words a household user understands — never an internal state name (`needs_evidence`, `consent_disabled`, `COMPLETED`, `asset_type`) shown raw;
- gives each new action one clear primary control, with the state after it visible (what changed, where to go next).

**Name, per screen, what you changed and why it looks the way it does** in the report's design section. A design call inside these limits is yours; decide and report.

## Why this exists

The AI does work the screens then throw away, and finished work keeps asking for decisions. Each item below is a finding with evidence; line numbers in `SG-269_findings.md` are **from `343ba8b`, before SG-270, SG-275 and SG-279 moved code** — locate by symbol, and treat every premise as a hypothesis to falsify first (`PB-1`).

## G0 — Preflight

`DOCKER_CONFIG` to a writable temp directory, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-271/docker.sock`, `docker version` shows a **Server** section, `docker run --rm busybox true` rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch goes in `output/SG-271-scratch/`, removed by exact path; never touch `output/` itself or `output/dispatch`.

## G1 — No false date task (backend, load-bearing)

An `expiry.manual_entry` task opens for a candidate **only when a date the category needs is actually unknown**, not whenever `needs_evidence` is true.

Facts the design turns on, each a hypothesis:
- `needs_evidence` is provider-global: food prompt v4 rule 20 sets it for a null `expiry_date`; cosmetics prompt v4 rule 21 sets it for an unknown **opened** date; the schema (`schemas.py`, the extraction model, ~`:140-145`) only requires a non-empty `unknowns` list (SG-270 report line 12).
- The candidate producer is `build_candidate_from_extraction` in `backend/app/services/candidates.py` (`if extraction.needs_evidence:` ~`:773`); split children carry their own flag (~`:1270`, ~`:1360`). The asset-subject producer is `expiry_tracker._manual_task` (`backend/app/plugins/expiry_tracker.py:381`), called by `apply_extraction_result` and `classify_asset`.
- **Establish before choosing:** what `unknowns` holds for each case (field names), and whether an unknown opened date should open a different task or none. **Do not invent a new task kind**; if the opened-date case needs one, say so under `REMAINING` and open none.

## G2 — A committed candidate leads to its item (backend + Review/Inbox)

A candidate that already has an item says so **on first load and on reload**: the candidate read carries the item's id, the Review page shows *"In your catalog"* with an **Open item** link and offers **no** Accept / Edit / Hold / Reject; the Inbox candidate list links such a candidate to its item, not to Review.

- The id already exists server-side: `committed_assets` in the review step output and `_created_asset_from_commit_step` (`backend/app/api/v1/candidates.py:69-110`, SG-275). Derive it on read; **store nothing new — any schema or migration need is a STOP and report.**
- `PG-SC-02`: trace the new field from where it is computed through the candidate serializer, the API response, the frontend type and both screens; report each hop. Check the household before returning the id, as the existing branch does.
- This also closes SG-275 I1: a repeat edit on a committed row no longer has a screen that offers it. The API's repeat edit stays as SG-275 left it (returns the item, `created` false).

## G3 — The AI's date and category survive (F4, F5, F12)

- **F4:** classifying an item that holds an active **proposed** expiry date keeps it, opens no manual-entry task for it, and the asset page shows the proposed date with **Accept date** (and the existing edit form as the alternative). Expected path: `classify_asset` (`expiry_tracker.py:457`) currently treats the unaccepted date as absent and writes `{"status":"unknown"}` with a manual task. `expiry_engine.py` treats `proposed` as absent; say where the item appears until the date is accepted, and make that place say *"Date proposed"*, not *"No date"*.
- **F5 / F12:** a candidate's `category_proposed` (promoted at `candidates.py:~704`, stored as a `category_proposed` assertion with `review_state=proposed`) **preselects** the Classification control on the asset page and is shown on the Review page after accept, with one **Confirm** action. **Never classify without the user's confirmation** — the proposal is a suggestion, as the date is. An item with no proposal behaves as today.

## G4 — One word per concept (F7)

Two controls both read as "category": `asset_type` at capture (`frontend/src/components/AssetForm.tsx`, ~`:104`) and in the drawer (`frontend/src/components/shell/ItemInspectorDrawer.tsx`), and the expiry classification on the asset page (`AssetDetailPage.tsx`, `classificationChoice` ~`:306`). Rename so each concept has one name everywhere it appears (labels, headings, help text, tests). My suggestion, yours to improve: *"Kind of item"* for `asset_type`, *"Shelf life"* for the classification. **Labels only — no field, value or API rename.** List every place each name now appears.

## G5 — A deliberately dateless item stops nagging (F8)

An item classified Non-perishable (accepted null expiry, reason `dateless`, `expiry_engine.py:~273`) is **not** listed under Unresolved on the Expiry page (`frontend/src/routes/ExpiryPage.tsx:~270`). **Establish what distinguishes deliberate from missing** (the classification, the accepted null, both) and key the rule to that, not to the label. Keep such items findable: a quiet count or note is your design call. An item with no date and no such decision still shows as unresolved.

## G6 — Skipped steps say so (F11, droppable)

In the Inbox's Selected job (`InboxPage.tsx:~52`, `step.state` rendered raw), a step whose output is `{"status":"skipped", ...}` reads as skipped with its reason in plain words (for `consent_disabled`: the AI is turned off). No backend state change. **Drop this goal first if time is short**, and say so.

## G7 — retired in the retry

Screenshots moved to SG-273 (the Pantry view), which owns how screens get seen. **Do not run Chrome or start a local app server in this slice.**

## Tests and the gate

- **Backend** (fixture module `backend/tests/test_sg270_flow.py`, in scope, or a new `backend/tests/test_sg271_*.py`): G1 food null date opens a task, cosmetics unknown opened date opens no date task; G2 the read carries the item id for a committed candidate on a fresh session and none for an uncommitted one, and none across households; G3 classify keeps a proposed date and opens no task, and a candidate's proposed category reaches the asset unconfirmed; G5 the engine/route output the Expiry page reads.
- **Frontend** (vitest, beside the existing route tests): Review page hides decisions and shows Open item for a committed candidate; Inbox links it to the item; asset page shows Accept date and the preselected shelf life; new labels; Expiry page excludes the deliberate dateless item and still lists a missing one; G6 if done.
- **FAIL-then-PASS:** each new test fails on the base and passes on the candidate. Commit both runs as `docs/worklogs/SG-271_fail_*.log` and `SG-271_pass_*.log` (`PG-EV-09`). Full suites run on the candidate only; on the base only the new tests (`D443`).
- Then `make backend-test` once (host suite green, the two marked tests **deselected**, image proof) and `make frontend-test` once. Quote exact counts (`PG-IC-08`).
- Affected test files run **twice consecutively** (`PG-DP-04`). `ruff check` and `eslint` on **every changed file** (`PG-EV-15`); the repo-wide mypy reds and the one `eslint` error in `App.household-nav.test.tsx` are out of scope. `tsc` clean and the deploy's frontend build step rc 0 (`PG-SC-12`).

## Acceptance criteria

- **A1** — G1: a non-date unknown opens no date task; a missing required date still does; both shown FAIL-then-PASS.
- **A2** — G2: the committed candidate's item id survives a reload (fresh session read), the Review page offers no decision on it, the Inbox links to the item; `PG-SC-02` hops listed.
- **A3** — G3: a proposed date survives classification with Accept date; a proposed category preselects and is never applied without Confirm.
- **A4** — G4: one name per concept, every occurrence listed; no API or value renamed.
- **A5** — G5: the deliberate dateless item is off Unresolved; a truly missing date is still on it.
- **A6** — Design: every touched screen uses tokens only, works in both themes, new colour pairs are in the contrast test, and the report's design section names each change and why.
- **A7** — FAIL-then-PASS logs committed; suites green; affected files twice; `tsc`, lint and build clean; counts quoted.
- **A8** — Scope is only the files below; zero schema, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes.
- **A9** — Preflight proven before the gate; health 200 at start and end.
- **A10** — `PB-3` vacuity: a failure would look like a date task on a cosmetics candidate with a known expiry, a Review page offering Accept on a committed candidate after reload, a proposed date replaced by "unknown", or a Non-perishable item under Unresolved. Say which you checked for and that none was observed.
- **A11** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Product files:** `backend/app/services/candidates.py`, `backend/app/api/v1/candidates.py`, `backend/app/plugins/expiry_tracker.py`, `backend/app/services/expiry_engine.py`, the candidate schema/serializer module they use, `frontend/src/routes/{ReviewPage,InboxPage,AssetDetailPage,ExpiryPage}.tsx`, `frontend/src/components/{CandidateCard,AssetForm}.tsx`, `frontend/src/components/shell/ItemInspectorDrawer.tsx`, the frontend API types/client, `frontend/src/theme/{tokens.css,theme.test.tsx}` (additions only), and their tests. Another file you find necessary: change it and name why; a product file outside `backend/app`, `backend/tests`, `frontend/src` is a STOP (the evidence paths below are not product files).
- **Reads of any file are allowed.** Authorised runtimes: the preflight, the `make` gates, the tests, `tsc`, lint, and the frontend build. **No browser, no local app server, no other container image is pulled or run.**
- Evidence: `docs/worklogs/SG-271*` only.
- **No deploy, no restart, no touch of the running container or its image tag, the live database or the stored files.** Test rows live only in temporary files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`). "STOP and report" is not satisfied by disclosing and carrying on (`PG-EV-03`). Stopping on a false premise is a success.

## Hang bounds

Preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **THE PUBLISH POINT IS 1300 s ELAPSED, AND IT IS A STOP RULE, NOT A TARGET.** The first run passed its publish point, kept working on a droppable goal, and was killed at 2100 s with nothing pushed — a total loss. At 1300 s, **whatever goal you are in, stop it where it stands**: commit what passes, write the report (unfinished goals as `REMAINING`), push, publish the receipt. Check the elapsed time **before starting each goal and before each suite run**, and write it in the report. A partial slice with a receipt is a success; a complete slice with no receipt is a failure. Order: G0, G1, G2, G3, G5, G4, gate, G6. Expected ≈1100 s with the first run's work as a reference (`UNVERIFIED — my estimate`).

## Report

Destination: `docs/worklogs/SG-271_report.md`, evidence beside it (`docs/worklogs/SG-271_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: a **design section** per screen; elapsed against ≈1100 s with every phase over 60 s named; changed files; test counts; logs; the contract echo; every `UNCLEAR` / `REMAINING` line; one line per constraint.

Commit with the trailer `Dispatch-ID: SG-271`, then `git push origin automation`. **Hash equality:** after the push, `git rev-parse HEAD` equals `git rev-parse origin/automation`; quote both.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-271 | Report: docs/worklogs/SG-271_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-271 | Report: docs/worklogs/SG-271_report.md | Work-HEAD: <work commit>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
