# SG-143 — DRAFT (do not dispatch: finalize at chain time) — Port the 3 blocked HouseholdSelector pages

**DRAFT status:** written alongside SG-142 under the L3 finish chain (P1). Premises below come from `docs/worklogs/SG-138_report.md:33-77,134-139` (Architect-read 2026-09-29) and MUST be re-verified against the tree at finalization (`PG-IC-09`) — SG-142's diff may move lines. Finalization: refresh line numbers, confirm the className-prop API word, paste the §3 blocks verbatim, then commit as the final packet.

**Settings travel on the trigger** (`SG-143 coder=opencode effort=high`) — no `coder:` / `model:` / `effort:` line in the first 40 lines (`packet_settings_retired`, D302, 0.40.0).

**Context (to verify at finalization).** SG-138 shipped the selector subset (component + test verbatim, Chat/Planning hunks) and STOPped on 3 pages: `CapturePage.tsx` + `InboxPage.tsx` hunks would drop `className={THEMED_CONTROL_CLASS}` that `theme-adoption.test.tsx:219-228` and `InboxPage.test.tsx:75-81` assert (F-3); `CatalogPage.tsx` renders no household select — it delegates to `AppShell` → `CatalogToolbar.tsx:123-136` (F-2). The SG-138 (g) recommendation: extend `HouseholdSelector` with a `className` passthrough (an API change the SG-138 ceiling forbade) and/or move the Catalog select out of the toolbar. The L3 chain carries the className-prop word — the packet states the choice, the Coder does NOT re-ask it.

**Standing lines (finalize verbatim):** PORT slice. Expected writes: `HouseholdSelector.tsx` (className passthrough ONLY) + the 3 page call-sites + tests + `docs/worklogs` (3 files). Served code changes → owns its refresh per D145 (rebuild + exactly ONE recreate + verify). Money $0.000000 USD. Guards (expected): `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

## G0 — equivalence map on BASE (committed)

- For each of the 3 pages, quote the CURRENT select markup + the themed-class test assertion that guards it. Any page whose markup no longer matches the F-2/F-3 description is a finding, not an obstacle — re-map, never force-apply.

## G1 — port through the shared selector (fail-post, both runs committed)

- `HouseholdSelector` gains the passthrough prop (stated API delta, old props byte-compatible); all 3 pages render through it with output identical to BASE markup (mapping table per page); the two themed-class tests stay green UNCHANGED; full frontend suite green-except-base-proved-reds; `tsc --noEmit` exit 0; eslint exit 0.

## G2 — serve + worklog/report

- Rebuild + exactly ONE recreate + verify (bundle marker moves, counts delta zero, `/expiry` + household pages 200). `{{WORKLOG_DIR}}/SG-143.log`, `SG-143_report.md`, `SG-143_verify.log`; receipt per the M20-corrected block; three UNCLEAR lines.

## Constraints (finalize with cross-product)

- Scope ceiling: selector prop + 3 call-sites + tests + worklogs. Any other product hunk is a STOP. Per-command-class bounds. No fixed dates. Simplicity: port the markup, add the prop — no toolbar redesign beyond what the call-site needs.

## Acceptance criteria (finalize with PG-SC-09 questions)

- mapped — is every page's output identical to its BASE block through the shared component? guarded — are both themed-class tests green unchanged? served — new bundle live with zero count drift? clean — diff exactly prop + call-sites + tests + worklogs?
