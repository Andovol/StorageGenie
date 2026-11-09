# SG-272 — An item can be used up: quantities quick to change, "gone" with a reason, "put back", and gone items findable

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary test databases only.** No live database read or write.
**Restart: none.** This slice does not deploy; its rider SG-297 does. Until then the live app stays as it is (`PG-PR-05`). **No schema change: a need for a migration is a STOP and report** (the roadmap expects none).
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.58.0` (`AGENTS.md`). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line as you received it. A denial on that folder is expected and is not a STOP.

**Approval:** owner, stage C (*"d14 ok"*, L3); roadmap stage C, *Quantities (Q22)* and *"Gone" (Q22)*; `STATE.md` ordered work item 3. Owner's Q22, verbatim summary in `docs/decisions/2026-10-30-session-approvals.md:99`: *"a count, or an amount with a unit; one tap takes off 1; "gone" moves the item to history, not deleted."*

**Previous report's open items that are this slice:** `docs/worklogs/SG-271_audit.md` I1 and I2 (fix first, G0b); SG-269 findings F3 and F13 (`docs/worklogs/SG-269_findings.md`, table rows; line numbers there are from `343ba8b` — locate by symbol).

## Why this exists

Stage C's outcome is *"see it, use it up, quantities quick to change"* (`docs/ROADMAP.md`). Today no screen can retire an item: the edit forms send only name, quantity, unit and condition, and nothing sends a status (SG-269 F3, confirmed by a direct `PATCH {"status":"ARCHIVED"}` returning 200). An archived item is then unreachable, because the catalog hides it with no way to ask (F13). Quantity changes need the full edit form. And SG-271 left a cleared perishable date hidden from the Expiry page (its audit I1).

## THE PUBLISH POINT IS 1300 s ELAPSED, AND IT IS A STOP RULE

At 1300 s, **whatever goal you are in, stop it where it stands**: commit what passes, write the report (unfinished goals as `REMAINING`), push, publish the receipt. Check the elapsed time **before starting each goal and before each suite run**, and write it in the report. A partial slice with a receipt is a success; a complete slice with no receipt is a failure (SG-271 run 1 lost 2100 s this way). There is no optional goal in this packet.

## Design is a requirement, not polish

The owner: design quality is *"a first-class requirement of every theme and screen slice"*; *"design, look and feel are very important, so hold every screen to that."* Every screen this slice touches:

- uses only the theme's tokens and shared control classes (`frontend/src/theme/tokens.css`, `THEMED_CONTROL_CLASS` / `CONTROL_STYLE`); no new literal colours or one-off shapes;
- **no text smaller than the page's body text** — D18 asks to enlarge the small type, and SG-271 was marked down for new 12 px notes. Existing 12 px text you touch moves up; text you do not touch stays;
- works in light and dark; any new text/link colour pair goes into the contrast test in `frontend/src/theme/theme.test.tsx` (≥ 4.5:1);
- plain household words, never a raw state name (`ARCHIVED`, `DISPOSED`, `ACTIVE`) shown to the user — say *Gone*, *Put back*, *Used up*, *Thrown away*, *Given away*;
- one clear primary control per action, the result visible right after it (what changed, how to undo).

The report's **design section** names, per screen, what changed and why it looks that way.

## G0 — Preflight

`DOCKER_CONFIG` to a writable temp directory, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-272/docker.sock`, `docker version` shows a **Server** section, `docker run --rm busybox true` rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. Scratch goes in `output/SG-272-scratch/`, removed by exact path; never touch `output/` itself or `output/dispatch`.

## G0b — Fix first, from SG-271's audit

- **I1:** `compute_status` (`backend/app/services/expiry_engine.py`, SG-271's `dateless_count` hunk) counts **any** accepted null expiry as deliberately dateless. `clear_expiry_date` (`backend/app/plugins/expiry_tracker.py:~771`) writes that same accepted null for **perishable** items (it refuses Non-perishable ones, `:~794`). So a cleared milk date vanishes from Unresolved. **Key the quiet count to the Non-perishable classification only**; a perishable item with an accepted null shows on Unresolved as *No date* again (reason `dateless`, as SG-262 had it). Test: clear a food date → listed as *No date*; classify Non-perishable → counted quietly. FAIL-then-PASS.
- **I2:** SG-271's new notes are 12 px (`ExpiryPage.tsx` dateless count; `AssetDetailPage.tsx` shelf-life suggestion notes; `ReviewPage.tsx` messages if any). Raise them to the page's body size.

## G1 — "Gone" and "Put back": one all-or-nothing action each (backend)

A user marks an item **gone** with one reason — *used up*, *thrown away*, *given away* — and can **put it back**. Gone = the `ARCHIVED` status plus the reason; history, never deletion. Each is **one dedicated action** that commits everything or nothing.

Facts the design turns on, each a hypothesis to falsify:
- The transition table is `TRANSITIONS` in `backend/app/services/lifecycle.py` (~`:43-50`): `ACTIVE → {ARCHIVED, MERGED}`, `ARCHIVED → {DISPOSED}`. **Put back needs a new `ARCHIVED → ACTIVE` edge**; that is the owner's approved undo (Q22). Add only that edge; `DISPOSED` and `MERGED` stay terminal. Update the module docstring's flow line to match.
- `PATCH /v1/assets/{id}` (`backend/app/api/v1/assets.py:~408`) accepts `{"status": "ARCHIVED"}` today (SG-269 F3, by direct request). **Establish** whether the new actions should be dedicated routes or that PATCH; the roadmap says *dedicated*; decide and say why.
- **Where the reason lives, without a migration:** establish what can hold it — the assertion store (as plugin values are held), an audit event, or another existing column — and how a screen reads it back. `PG-SC-02`: trace the reason from its writer to the gone list on screen and list every hop. A reason that cannot be read back is not stored.
- **What else moves when an item goes, today:** the expiry engine admits `ACTIVE` only (`expiry_engine.py`, SG-111 comment), and reminders read the engine (`backend/app/services/reminders/service.py:51`). **Enumerate** every reader that filters by status (`lifecycle` imports; analytics, chat, planning, search/FTS, summaries) and every open row tied to the item (review tasks, reminders). Report the list. **Decide** what a gone item's open tasks do and say why; the rule is that a gone-and-back cycle restores the same visible state.
- **Idempotency:** `POST /v1/assets` honours an `Idempotency-Key` header (`assets.py:~75-86`). Say whether the new actions use it, and what a double tap does.
- Only a household member's own item; the household check as on the other asset routes.

## G2 — "Gone" and "Put back" on screen; gone items findable (F3, F13)

- The item page (`frontend/src/routes/AssetDetailPage.tsx`) and the item panel (`frontend/src/components/shell/ItemInspectorDrawer.tsx`) offer **Mark gone** with the three reasons; after it, the item reads *Gone — used up* (etc.) with **Put back**.
- **F13:** the catalog hides `ARCHIVED` by default (`assets.py:~296-298`; `CatalogPage.tsx` calls `useAssets` without a status). Add a way to see **Gone** items in the catalog (your design call: a filter, a tab, a toggle in `CatalogToolbar`), each showing its reason and **Put back**.
- A gone item does not appear on the Expiry page or in reminders; put back, it does again.

## G3 — Quantities quick to change (Q22)

`asset.quantity` and `asset.unit` (`backend/app/models/asset.py:30`, `unit` a free string up to 50 chars) already exist.

- **Counted** items get a one-tap **−1** (and a way back up) on the item page and the item panel. **Amount** items (a unit such as ml, g, kg, l) get a quick edit instead, because taking off "1" means nothing there. **Establish the rule for "counted"** from the code and test data (empty unit? `pcs`? the units the forms offer) and state it; the rule is your design call, written down.
- At **0**, never auto-archive: show *None left* with **Mark gone** offered. Below 0 is refused.
- **Fact the design turns on:** the existing edit sends an **absolute** `quantity` in a PATCH (`AssetDetailPage.tsx:~551`, drawer ~`:69`). Two quick taps from a stale view can lose one. Decide whether −1 is a server-side decrement or an absolute write with a guard, and say why.

## Tests and the gate

- **Backend** (new `backend/tests/test_sg272_*.py`; shared fixtures as the nearest existing asset tests use them, named in the report):
  - **The cycle test the roadmap asks for:** snapshot the catalog list, the expiry status, reminders, open tasks and the summaries (`assets.py` counts/facets ~`:244-270`); mark gone; assert the item left each; put back; assert **each equals the first snapshot**, with only the history record added. **Feed it once with a deliberately broken put-back (e.g. one reader not restored) and show it fails** (`PG-EV-01`), in the log.
  - all-or-nothing: a failure injected mid-action leaves status, reason and every other row unchanged;
  - the three reasons stored and read back; an unknown reason refused; `DISPOSED`/`MERGED` still terminal; put back only from gone; household check;
  - −1 on a counted item, refused below 0; amount items take an edit, not −1; G0b I1.
- **Frontend** (vitest beside the existing route tests): Mark gone with reason and Put back on the item page and panel; the Gone view in the catalog with reason and Put back; −1 for counted, quick edit for amounts, *None left* at 0; G0b I2 sizes.
- **FAIL-then-PASS:** each new test fails on the base and passes on the candidate. Commit both runs as `docs/worklogs/SG-272_fail_*.log` and `SG-272_pass_*.log` (`PG-EV-09`). Full suites on the candidate only; on the base only the new tests.
- `PG-SC-11`: grep for assertions on the transition table's shape (edge counts, `allowed_next(ARCHIVED)`, the docstring flow) and update any this change makes false; list the hits.
- Then `make backend-test` once (host suite green, the two marked tests **deselected**, image proof) and `make frontend-test` once. Quote exact counts (`PG-IC-08`). Affected test files run **twice consecutively** (`PG-DP-04`). `ruff check` and `eslint` on **every changed file** (`PG-EV-15`); the repo-wide mypy reds and the one `eslint` error in `App.household-nav.test.tsx` are out of scope. `tsc` clean and the deploy's frontend build step rc 0 (`PG-SC-12`).

## Acceptance criteria

- **A1** — G0b: a cleared perishable date lists as *No date*; Non-perishable counts quietly; SG-271's notes at body size.
- **A2** — Gone with each reason and Put back work through one all-or-nothing action each; only `ARCHIVED → ACTIVE` added to `TRANSITIONS`; `PG-SC-02` hops for the reason listed.
- **A3** — The cycle test passes, and fails on the planted break, both in the log; the readers-by-status enumeration is in the report.
- **A4** — Gone items are findable in the catalog with their reason and Put back (F13); Mark gone exists on the item page and panel (F3).
- **A5** — −1 on counted items, quick edit on amounts, *None left* at 0, never below 0; the "counted" rule and the decrement choice stated.
- **A6** — Design: tokens only, both themes, no text below body size on touched screens, plain words, contrast test extended if a new pair exists; design section per screen.
- **A7** — FAIL-then-PASS logs committed; suites green; affected files twice; `tsc`, lint and build clean; counts quoted; `PG-SC-11` hits listed.
- **A8** — Scope is only the files below; zero schema, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, running-container or deploy bytes.
- **A9** — Preflight proven before the gate; health 200 at start and end.
- **A10** — `PB-3` vacuity: a failure would look like a gone item still on the Expiry page or in reminders, a put-back item missing from a reader, a reason lost on reload, a half-applied action, a quantity below 0, or a cleared food date hidden. Say which you checked and that none was observed.
- **A11** — The report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Product files:** `backend/app/services/lifecycle.py`, `backend/app/services/asset_service.py`, `backend/app/api/v1/assets.py`, `backend/app/services/expiry_engine.py`, the module that stores the reason if another, `frontend/src/routes/{AssetDetailPage,CatalogPage,ExpiryPage,ReviewPage}.tsx`, `frontend/src/components/shell/{ItemInspectorDrawer,CatalogToolbar}.tsx`, the frontend API types/client and hooks, `frontend/src/theme/{tokens.css,theme.test.tsx}` (additions only), and their tests. Another file under `backend/app`, `backend/tests` or `frontend/src` that you find necessary: change it and name why. **A file anywhere else, including `backend/eval/`, is a STOP and report — do not change it and disclose; stop** (`PG-EV-03`). Evidence paths below are not product files.
- **Reads of any file are allowed.** Authorised runtimes: the preflight, the `make` gates, the tests, `tsc`, lint and the frontend build. **No browser, no local app server, no other container image.**
- Evidence: `docs/worklogs/SG-272*` only.
- **No deploy, no restart, no touch of the running container or its image tag, the live database or the stored files.** Test rows live only in temporary files (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`). "STOP and report" is not satisfied by disclosing and carrying on (`PG-EV-03`). Stopping on a false premise is a success.

## Hang bounds

Preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling; the 1300 s stop rule above binds. Order: G0, G0b, G1, G2, G3, gate. Report elapsed at each transition. Expected ≈1100 s (`UNVERIFIED — my estimate`; SG-271 run 1 reached its last goal near 1500 s with a similar spread, run 2 took ~420 s from a head start).

## Report

Destination: `docs/worklogs/SG-272_report.md`, evidence beside it (`docs/worklogs/SG-272_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then: the **design section** per screen; elapsed against ≈1100 s with every phase over 60 s named; the readers-by-status list; the reason's hops; changed files; test counts; logs; the contract version line; every `UNCLEAR` / `REMAINING` line; one line per constraint.

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-272`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-272 | Report: docs/worklogs/SG-272_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
