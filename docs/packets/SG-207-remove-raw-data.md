# SG-207 — D-12: remove the Raw Data panel from the asset drawer

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none** (frontend-only removal; no lane serve needed beyond the test run).
**Autonomy: L2.** Authority: owner D-12 (`docs/decisions/2026-10-17-q1-q2-q3-directives.md` — "I don't need it" → full removal, reversible via git). One retry max, root-cause only.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

The drawer carries a collapsed dev-verification panel dumping the stored record as JSON. The owner does not need it. Server-side `assertions` readback stays; only the drawer panel (section + memo + its test) goes. Precedent class: small reversible presentation removal, statically verifiable.

## Handed-over facts (expected — re-verify on target, `PB-1`; correct openly)

- Panel (expected): `frontend/src/components/shell/ItemInspectorDrawer.tsx:440-460` (toggle button `Raw data`, `rawOpen` state, `<pre data-testid="raw-json">`); memo `rawJson = JSON.stringify({asset: current, assertions}, null, 2)` at `:171-174`.
- Test (expected): `frontend/src/components/shell/drawer.test.tsx:196-206` (raw-panel test; `:198` asserts `raw-json` absent before expansion). Other `rawJson`/`raw-json` references: none expected — enumerate on target.
- Chevron imports (`ChevronDown`/`ChevronRight` at the button) may serve other sections — check before removing.

## G1 — remove the panel

- Delete the Raw Data section (button + conditional `<pre>`), the now-unused `rawJson` memo + `rawOpen` state, and any import left unused by exactly this removal. Nothing else in the drawer changes: metadata editing, tabs, empty states, AI-action buttons all stay byte-identical in behaviour.
- Update the test file: remove/replace the raw-panel test so the suite asserts the panel is GONE (a test silently passing because it never looks is `PB-3` vacuity — the new assertion must name `raw-json`/`Raw data` absence explicitly).

## G2 — prove nothing else moved

- Full frontend suite ONCE on the candidate (`vitest run`); on the base, nothing (no new unit rows — the removal's FAIL-then-PASS is the deleted test failing pre-change... state precisely: the removed test's pre-change green + post-change absence is recorded, and the new absence-assertion passes post-change; `PG-EV-09`: both runs committed to `SG-207_verify.log`).
- Diff file-list proof: product bytes ONLY `ItemInspectorDrawer.tsx` + `drawer.test.tsx` (grep-gated, `PG-SC-05`); served Catalog + drawer smoke on the lane (open drawer, confirm no Raw Data affordance; one screenshot committed).

## Constraints

- **Scope ceiling (rule, grep-gated):** product+test bytes ONLY the two named files; evidence ONLY `docs/worklogs/SG-207_*`. No backend/config/schema; no other route/component touched. `git status` clean apart from the named commits.
- No interactive prompt/polling; no sudo; no host change; no secret in logs. `PB-2`: any denial STOPS. `PB-3`: suite green with zero mention of raw-json anywhere (test + code grep empty) or FAIL.
- Hang bounds: reads 120 s; suite per its bound; idle kill never approached. Expected duration ≈450 s (Architect record, `G-A9` uncalibrated; derived from SG-205's 399 s minus the CDP-measurement legs this slice has no use for).
- Simplicity (`G-A7`): deletion + test update; no new machinery. No waste cut owed (SG-205: `none`).

## Acceptance criteria

- **A1:** no `Raw data` affordance and no `raw-json`/`rawJson` string anywhere in `frontend/src` (tree grep empty, committed); drawer behaviour otherwise unchanged (edit/save, tabs, empty states exercised by the suite).
- **A2:** suite green once on candidate with counts; pre/post test transcript committed; one lane screenshot of the drawer without the panel committed and opened by the Coder.
- **A3:** report `docs/worklogs/SG-207_report.md`; elapsed vs ≈450 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-207`.
- **A4:** notes-ref receipt, first line `Dispatch-ID: SG-207 | Report: docs/worklogs/SG-207_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/05/09; PG-SC-05/09/12; PG-IC-01/07/09; PG-PR-03. Stop follows `PB-6`.
