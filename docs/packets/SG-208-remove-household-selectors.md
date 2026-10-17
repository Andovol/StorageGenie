# SG-208 — D-13: remove household switching UI (one user = one household)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none (no migration, no seed change, no row writes). Restart: none.**
**Autonomy: L2.** Authority: owner D-13 (`docs/decisions/2026-10-17-q1-q2-q3-directives.md` — single-household requirement + "Remove the selectors"). Server `?household_id=` scoping untouched. One retry max, root-cause only.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

A user belongs to exactly one household and cannot hold several (D-13 requirement), so household-switching UI selects nothing. Remove every switching affordance; keep resolution (stored id else first household) and all server scoping byte-identical.

## Handed-over facts (expected — re-verify on target, `PB-1`; a handed list is a fact too — enumerate, don't trust)

- Known selectors (expected, non-exhaustive): nav selector in `frontend/src/App.tsx` (uses `householdId`/`setHouseholdId` from context at `:40-45`); toolbar selector `frontend/src/components/shell/CatalogToolbar.tsx:123-137` (`aria-label="Household"`, `value`/`onHouseholdChange` at `:48-50,:84`); context `frontend/src/hooks/HouseholdContext.tsx` (localStorage-first else `households[0]` auto-persist rail); props `householdId`/`onHouseholdChange` threaded through `CatalogPage` (expected — verify).
- Possible further affordances (expected unchecked): household management/creation in Settings or elsewhere; `components/HouseholdSelector.test.tsx` exists (a component file under `components/shell/` does NOT — verify the live set). Criterion: every element that lets the user pick, change, or create a household.
- Resolution rail to keep: stored `household_id` else first household, auto-persisted. `setHouseholdId` loses all UI callers; keep or remove the context setter per the Coder's call — report either way (dead-export vs kept-API), never silently.

## G1 — remove every household-switch affordance

- Delete all switching/creation UI found by the enumeration (selects, menus, management entries). Every route keeps working with zero household UI: Catalog, Capture, Inbox, Planning, Chat, Analytics, Expiry, Settings, detail/drawer — the household id flows from the existing rail, no route takes it from a control anymore.
- Update every test that renders or asserts a selector (expected: `HouseholdSelector.test.tsx`, `catalog.test.tsx`, shell tests — enumerate on target): selectors assert ABSENT where they were present; no test silently passes by never looking (`PB-3`).
- Server scoping, seed data, export, and the context provider's resolution logic stay unchanged. Any remaining multi-household path found (API, creation flow) is a reported REMAINING finding — NOT fixed here (D-13 scoped the UI; enforcement beyond the UI needs its own requirement).

## G2 — prove it

- Full frontend suite ONCE on the candidate; tree grep `aria-label="Household"` + `onHouseholdChange` + `setHouseholdId` call-sites committed empty-or-justified (`PG-SC-05`); diff file-list proof (product files + their tests only).
- Lane smoke: Catalog + one non-Catalog route served, household-scoped reads working with no selector on screen; two screenshots committed, opened, dispositioned (UI/layout/data).

## Constraints

- **Scope ceiling (rule, grep-gated):** no backend/api/seed/migration/config bytes; no file outside the enumerated UI + test set gains product bytes. Evidence ONLY `docs/worklogs/SG-208_*`.
- Reads: lane CDP + loopback GETs only; zero credential forwarding; no production/evidence writes; no restart; health start+end identical expected. No prompt/polling/sudo/host change/secrets. `PB-2` denial STOPS; `PB-3` vacuity as in G1.
- Hang bounds: reads 120 s; suite per its bound; smoke 600 s; idle kill never approached. Expected duration ≈500 s (Architect record, `G-A9` uncalibrated; SG-205 399 s + cross-route smoke).
- Simplicity: deletion + test updates; no new machinery. Excluded (stated): server-side single-household ENFORCEMENT (reported, not built); Option C/D; AI stages.

## Acceptance criteria

- **A1:** zero household-switch affordance in the served UI on any route (grep + smoke); scoped reads still carry the resolved household (Catalog loads, Inbox count, capture upload attribute to the same household as before — readback, not code-reading).
- **A2:** suite green once on candidate with counts; enumeration (criterion + found set + delta vs the two known selectors in EITHER direction — `PG-IC-08`) in the report; screenshots committed + opened.
- **A3:** report `docs/worklogs/SG-208_report.md`; elapsed vs ≈500 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-208`.
- **A4:** notes-ref receipt, first line `Dispatch-ID: SG-208 | Report: docs/worklogs/SG-208_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/05/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-01/03/04. Stop follows `PB-6`.
