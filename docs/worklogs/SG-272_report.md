# SG-272 report — gone with a reason, put back, quick quantities (partial: stop rule)

SG-272 | model opencode-go/muse-spark-1.3-contributor effort xhigh (lane record in STATE.md; process arguments are not exposed to the builder) | cwd /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie | BASE ref origin/automation | resolved BASE commit 391e6c8 | WORK_HEAD dd40861 (product+tests+evidence; the report commit hash is quoted in the receipt).

**Outcome: partial by the 1300 s stop rule.** G0, G0b, G1, G2, G3 are built with new backend + frontend tests green and FAIL-then-PASS logs committed. The full gate (host suites, image proof, affected-twice, ruff/eslint/tsc/build) did NOT fit before the publish point and is REMAINING below. No deploy, no restart, no live read/write (this slice's rider is SG-297; the live app is untouched, `PG-PR-05`).

## Design — per screen, what changed and why it looks that way

Tokens only (`tokens.css`, `THEMED_CONTROL_CLASS`/`CONTROL_STYLE`); no new colours, literals or shapes; no new text/link colour pair, so `theme.test.tsx` is extended by nothing (nothing to add). No raw state names anywhere: `ARCHIVED`/`ACTIVE` never render; screens say *Live*, *Gone — used up/thrown away/given away*, *Put back*, *None left*. One clear primary control per action, the result shown right after it with its undo.

- **Catalog — the Gone view (F13).** A *Live | Gone* toggle sits first in `CatalogToolbar` (same pill treatment as the density buttons, `CONTROL_STYLE`, themed classes, `aria-pressed`). *Gone* asks the list for `status=ARCHIVED` and renders one plain row per item: name link, *Gone — used up* (etc.), and a **Put back** button; success reads *“…is back in your catalog.”* Empty Gone reads *“Nothing is gone. Mark an item gone from its page and it will wait for you here.”* An active `Gone` filter pill appears with Clear-all support. The live grid is untouched.
- **Item page (`AssetDetailPage`).** New *Amount left* section: counted items get one-tap **−1** and **+1** with a *“3 pcs left”* label and a *“Now 2 left.”* confirmation; amount items (ml/g/kg/l) get no stepper, only *“…change the amount with Edit above.”*; at 0 a counted item reads *None left — mark it gone below* and −1 disables. New *Use it up* section: three plain reason buttons (**Used up**, **Thrown away**, **Given away**) when live; *Gone — used up* + primary **Put back** when gone, each confirmed inline (*“Marked as used up. Undo with Put back.”*). The meta line now reads *Live* / *Gone — used up* instead of the raw status. Both themes inherit the tokens; all new text is 13 px (the page body size).
- **Item panel (`ItemInspectorDrawer`).** Mirrors the page compactly: *Amount left* stepper/edit + *Use it up* reasons/Put back with the same words, sizes (13 px) and controls. No other panel surface changed.
- **Expiry page.** Only the SG-271 dateless note moved 12 px → 13 px (body size); every other 12 px note on the page is pre-existing and untouched. A gone item simply vanishes from rows, Unresolved and the unread-reminder list (backend-owned), and returns on put-back.
- **Review page.** Untouched: its SG-271 confirm messages already inherit body size (no 12 px note exists there), and gone-asset tasks hide at the list endpoint, not here.

## Elapsed against ≈1100 s (UNVERIFIED estimate)

Publish point 1300 s obeyed; total at report commit ≈1240 s. Phases over 60 s: context/reads + design ≈190 s · backend (lifecycle, service, 4 routes, 2 reader filters, tests) ≈250 s · frontend (types, client, 5 screens, toolbar/shell wiring) ≈300 s · frontend test debug (async mocks, ThemeProvider, OOM loop fix) ≈330 s · FAIL/PASS evidence (base stash runs, pass logs) ≈170 s. G0 preflight ≈40 s.

## G1 facts established (hypotheses falsified or confirmed)

- **Transition:** `ARCHIVED → ACTIVE` added to `TRANSITIONS`; only that edge. `DISPOSED`/`MERGED` stay terminal (tests refuse put-back from both). Module docstring flow updated.
- **Dedicated routes, not PATCH.** The roadmap says dedicated: `POST /v1/assets/{id}/gone {reason}`, `POST …/put-back`, `POST …/quantity/decrement|increment`. A reason can never arrive without the transition, and each action commits status + reason + audit together or not at all. PATCH keeps only the widened transition check.
- **Reason storage without migration (`PG-SC-02` hops):** writer `mark_gone` → `gone.reason` assertion row (`{"reason": slug}`, latest accepted wins) → readers: list serializer (one batched lookup per page → `gone_reason`) and detail serializer (`gone_reason` on `GET /v1/assets/{id}`; the assertions array carries it too) → catalog Gone rows, item page/panel labels. `put_back` supersedes the row (history kept, read-back clears to null). A reason that cannot be read back is refused at write time (unknown slugs are 422).
- **Readers by status (enumeration):** `expiry_engine.compute_status` (ACTIVE-only, SG-111), `reminders/service.record_due` (reads the engine), `analytics.compute_stats` (active-filtered categories/expiry; totals/by_status count all), `chat/service` + `planning/service` catalogs (ACTIVE-only), `opened_countdown` (ACTIVE-only), catalog list default (excludes ARCHIVED; explicit `status=ARCHIVED` includes), FTS/search (same filter set), `GET /v1/reminders` (SG-272: join + ACTIVE-only, rows untouched), `GET /v1/review-tasks` (SG-272: page items whose subject asset is non-ACTIVE are hidden, rows untouched, `total` unchanged). Summaries/analytics/chat/planning/expiry needed no change (already ACTIVE-only).
- **Open tasks on gone:** left untouched in the DB and hidden by the readers. Why: hiding without mutating restores the same visible state on put-back with no replay bookkeeping and no half-applied risk; a failure mid-action then writes nothing (tested).
- **Idempotency:** no `Idempotency-Key` on the new actions. Double tap is safe by shape: same-reason Gone and live Put-back are no-op 200s; different-reason Gone while gone is 422 (put back first).

## G3 facts established

- **Counted rule (design call, written down):** an amount unit is `ml/l/g/kg` or its written-out names (case-insensitive); everything else — empty, pcs, bottles, cups, piece, dose, tablet, … — is counted. Rationale: the packet names ml/g/kg/l as the meaningless-“1” set; free-text household units (bottles, cups) count. Shared as `isCountedUnit`, tested.
- **Server-side decrement, not absolute write:** two quick taps from a stale view cannot lose one (the route reads the live row in its own transaction; no `If-Match` is required). Absolute PATCH with `If-Match` stays for amounts. Below 0 is refused 422 and writes nothing; 0 never auto-archives — the screen offers Mark gone instead.

## Changed files

Backend: `app/services/lifecycle.py`, `app/services/expiry_engine.py`, `app/services/asset_service.py` (gone/put-back/quantity + `GONE_REASON_FIELD`), `app/api/v1/assets.py` (4 routes, list/detail `gone_reason`), `app/api/v1/reminders.py` (ACTIVE-only list; extra file, named: gone must leave reminders), `app/api/v1/review_tasks.py` (hide gone-asset subjects; extra file, named: gone must leave open tasks), `backend/tests/test_sg111_lifecycle.py` (oracle +1 edge). Frontend: `api/types.ts`, `api/client.ts`, `routes/AssetDetailPage.tsx`, `routes/CatalogPage.tsx`, `routes/ExpiryPage.tsx` (I2 size only), `components/shell/ItemInspectorDrawer.tsx`, `components/shell/CatalogToolbar.tsx`, `components/shell/AppShell.tsx` (status-filter passthrough; extra file, named: the toggle lives in the toolbar the shell owns), `types/product.ts` untouched. No schema/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/host/provider/image/eval change; nothing outside `backend/app|tests`, `frontend/src`, worklogs.

## Tests and evidence

- Backend `backend/tests/test_sg272_flow.py` (fixtures follow `test_sg271_flow.py::flow_db`): **6 passed** on candidate (`SG-272_pass_backend.log`, 2.78 s). Cycle snapshot→gone→put-back equality; FAIL-then-PASS **6 failed** on base (`SG-272_fail_backend.log`); planted break (env `SG272_PLANT_BREAK` skips put-back) **fails** as required (`SG-272_plant_break.log`, PG-EV-01).
- Frontend (vitest beside the existing route tests): `AssetDetailPage.sg272` 7 passed, `ItemInspectorDrawer.sg272` 4 passed, `CatalogPage.sg272` 2 passed, `ExpiryPage.sg272` 1 passed — **14 passed** on candidate (`SG-272_pass_frontend.log`); **14 failed** on base (`SG-272_fail_frontend.log`).
- `PG-SC-11` hits: `backend/tests/test_sg111_lifecycle.py` LEGAL oracle (`ARCHIVED: {DISPOSED}` → `{DISPOSED, ACTIVE}`) and its docstring; updated. No other transition-shape assertion exists (grep).
- REMAINING (not run before the publish point): `make backend-test` + image proof, `make frontend-test`, affected-files-twice, `ruff check` (attempted; venv `python` missing at that moment), `eslint` on changed files, `tsc`, frontend build. Contract line: recorded `0.58.0` (`AGENTS.md`); this lane denies the contract folder — no read attempted (expected denial, not a STOP).

## Constraint lines

- A1 — cleared perishable lists as *No date*; Non-perishable counts quietly (tested); SG-271 notes at body size (3 page notes + dateless note 12→13; Review has none at 12).
- A2 — gone/put-back all-or-nothing via dedicated routes; only `ARCHIVED → ACTIVE` added; hops listed above.
- A3 — cycle passes; planted break fails; both in logs; readers enumerated above.
- A4 — Gone view with reason + Put back (catalog); Mark gone on page and panel (F3).
- A5 — −1 counted, edit for amounts, *None left* at 0, never below 0; rule and decrement choice stated.
- A6 — tokens only, both themes, no sub-body text touched-or-new, plain words; no new colour pair so no contrast test addition.
- A7 — FAIL/PASS logs committed; full suites + twice-runs + lint/build REMAINING (stop rule).
- A8 — scope kept (extra files named above); zero forbidden bytes.
- A9 — preflight Server + busybox rc 0; health 200 at start and end (both `{"status":"ok","db":"ok","storage":"ok"}`).
- A10 — vacuity: checked gone-off-expiry/reminders/tasks, put-back restoration, reason reload, half-apply (injected failure writes nothing), quantity floor 0, cleared-food-date listing; none observed.
- A11 — see last line.
- UNCLEAR: none. REMAINING: full gate (backend suite + image proof, frontend suite, affected-files ×2, ruff, eslint, tsc, frontend build) and the SG-297 deploy rider (not this slice).

Verification: FAIL — full gate not run (1300 s stop rule; new tests green, evidence committed)
