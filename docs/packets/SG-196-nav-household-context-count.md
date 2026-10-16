# SG-196 — Nav household context + count: shared context, nav selector, household error branches, Inbox badge

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none.**
**Autonomy: L3.** D16 stage flow (per-slice gos ended; checkpoints only on G-K2 surfaces, assumption-changing results, stage end). This slice is disposable-DB + read-only GETs + jsdom tests, no restart, no prod write — same class as SG-185–SG-190. Dispatch settings ride the trigger, never this packet.

Authoring date (metadata, never a gate): 2026-10-16.

## Why this exists

SG-190 REMAINING + SG-195 out-of-set census, both re-verified by the Architect on the current tree 2026-10-16 (read `frontend/src/App.tsx` in full plus route grep; zero product diff since SG-195, so the SG-195 census is current):
- Nav (`App.tsx` `Nav`, lines 29-133) calls `useHouseholds()` (line 33) only to derive the import-modal id (lines 34-37, localStorage-first). It renders NO household selector, NO household error branch, NO Inbox/task count.
- Seven route-level selectors own their state (`CatalogPage:34`, `CapturePage:11`, `InboxPage:14`, `PlanningPage:24`, `ChatPage:19`, `AnalyticsPage:28`, `ExpiryPage:86` — each `useState(householdId)` + own `useHouseholds()` + localStorage key `household_id` with first-household fallback and auto-persist effect). That is EIGHT `useHouseholds` queries for one list; every one except the SG-195 named set fails silently.
- `isError` grep on current tree: branched = Catalog useAssets, Inbox jobs/detail/tasks, Analytics summary, Planning suggestions, Capture households, Planning households. UNBRANCHED = Catalog useHouseholds/useFacets/useSavedSearches, Inbox useHouseholds, Analytics useHouseholds, nav useHouseholds. EXPECTED enumeration: exactly these 4 route sites + nav (criterion below requires the Coder to enumerate the household-query set on target and report any difference either way — a handed list is a labeled expectation, never the set).

## G1 — Shared household context + nav selector (cheapest load-bearing first)

New `HouseholdContext`: provider mounted in `App` above `Nav`+`Routes`; single `useHouseholds()` fetch; value = `{ households, isError, error, householdId, setHouseholdId }` with `household_id` localStorage persistence. Selection semantics (behavior-preservation rail, every route today): localStorage-first, else first-household fallback, auto-persist on fallback. Nav renders the existing `HouseholdSelector` (`components/HouseholdSelector.tsx`, props `value/onChange/households/selectStyle/selectClassName`) bound to context, narrow-safe (SG-190 wrap/menu rules; no hidden focusables). Nav household error branch: `{householdsIsError && <div role="alert">Could not load households: …}` (SG-195 text-only convention: no refetch control invented; per-route text).
Migrate the 7 route selectors to consume the context (delete their `useState`+`useHouseholds`+fallback effects; keep their `effectiveHousehold` derivation shape). Designs inside these constraints are the Coder's; a constraint found wrong or impossible is a STOP (`PB-2`): second issuance of any destructive rewrite is STOP — migrate selector state only, no route logic changes.

## G2 — Household error branches on the remaining queries

Named `role="alert"` text-only branches (SG-195 sibling shape, duplication rule: same text on <3 routes stays per-route): Catalog `useFacets` + `useSavedSearches` failures. Households failures now surface once at the provider/nav branch (G1) — routes seeing `households === undefined` keep today's disabled-query empty states, now beside a named alert instead of silence. Enumerate the household-query set on target per the criterion above; any EXPECTED site already branched is reported-not-rebuilt; any site outside EXPECTED found needing a branch is reported-not-widened.

## G3 — Discoverable Inbox/task count in nav

Nav badge on the Inbox `NavLink`: open (non-resolved) review-task count for the effective household, reusing queryKey `["review-tasks", household]` (shared react-query cache with InboxPage — no new endpoint, no new fetch shape). `aria-label="Inbox, N open review tasks"`; error/loading/empty-household renders NO badge (absent, never a `0` — a zero shown for a failed fetch is a false completion). Wording follows the honest loaded-vs-whole rule (count of loaded open tasks).

## Constraints

Scope ceiling: `frontend/src/App.tsx`, `frontend/src/components/HouseholdSelector.tsx` (only if its props must change — prefer unchanged), the 7 route files, `frontend/src/hooks/*` (only for the context module + query reuse), one new test module (+ edits to existing route tests ONLY where the hook-shape migration requires it — each such edit names the preserved behavior). No backend, no router structure, no new routes, no screenshots/driver (jsdom only — zoom/touch/dark/auth-live stand, stated not silent). Secrets: none. Denial path `PB-2`. Hang bounds: reads 120 s, focused tests 600 s, full suite its own 900 s bound; visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo/host change. Simplicity: no shared helper component for <3 duplicated texts (SG-195 precedent); context module is the one shared unit and is the goal, not a helper.
Test scope per `D443`: full frontend suite ONCE on the candidate; on the base ONLY the new rows' FAIL half; old rows failing on candidate run alone on base; no carried counts. tsc + eslint gates. No waste cut owed (`slowest_waste = none` from SG-197; every SG-197 leg used).

## Acceptance criteria

- A1 (context): one `useHouseholds` fetch at App level; nav selector changes propagate to every route's effective household in the same session (no reload); selection persists across reload via `household_id`; first-household fallback + auto-persist preserved per route; existing suite green (behavior-preservation rail).
- A2 (branches): every EXPECTED unbranched household query now alerts with a named `role="alert"`; FAIL genuine (structurally absent on base) committed per `PG-EV-09` (both runs in committed logs); controls assert unchanged paths + alert absence; census enumerated on target with differences reported either way.
- A3 (count): badge shows the loaded open-task count; absent on error/loading/empty-household (each asserted — never a false zero); accessible name carries the count.
- A4 (report/receipt): first token SG-196; notes-ref receipt published + mapped-fetch/read-back verified, `Work-HEAD` recorded, branch/report push complete; elapsed per leg vs ~900 s uncalibrated Architect expectation (SG-195 branch-shape 442 s + unmeasured migration increment, stated per `G-A9`; lane enforces `RUN_BUDGET_S`); constraints each answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned.

Guards invoked: PG-EV-01/02/03/09; PG-IC-01/07/09; PG-PR-03/06. Stop follows `PB-6`.
