# SG-198 — Consolidation micro-slice: AppHeader onto household context, ReviewPage onto useReviewTasks

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none.**
**Autonomy: L3.** D16 stage flow (same class as SG-196: disposable + read-only GETs + jsdom, no restart, no prod write). Dispatch settings ride the trigger, never this packet.

Authoring date (metadata, never a gate): 2026-10-16.

## Why this exists

SG-196 audit left two reported-not-widened outliers, both re-verified by the Architect on the current tree 2026-10-16 (zero product diff since SG-196):
- `frontend/src/components/shell/AppHeader.tsx:16` runs its own `useHouseholds()`; the data serves only the import-modal fallback id (lines 18-21, localStorage-first). The shared context now owns exactly this derivation.
- `frontend/src/routes/ReviewPage.tsx:39` inlines its own `["review-tasks", householdId]` query; `hooks/useAssets.ts` exports the identical shared `useReviewTasks` (same key, same shape, same invalidations). ReviewPage's `householdId` sourcing (URL param + localStorage, line 32) is OUT of scope — swap the query definition only.

## G1 — Migrate both sites, change no behavior

AppHeader: consume `useHouseholdContext().householdId` for the modal id; delete its `useHouseholds` import/call and the local fallback derivation. ReviewPage: replace the line-39 inline `useQuery` with `useReviewTasks(householdId)`; keep every key, enabled flag, consumer and invalidation identical. No branch, wording, route, or selection-semantics change anywhere. Any behavioral difference found mid-slice is STOP and report (`PB-2`), not a quiet fix.

## Constraints

Scope ceiling: `frontend/src/components/shell/AppHeader.tsx`, `frontend/src/routes/ReviewPage.tsx`, plus test edits ONLY where the hook swap requires them (each names the preserved behavior; no assertion text changes). No other product file. No backend, no branches, no screenshots/driver (jsdom only). Secrets: none. Hang bounds: reads 120 s, focused 600 s, full suite 900 s; visible timeout finding; never approach idle kill 900 s. No polling, no sudo, no host change.
Test scope per `D443`: this slice adds no new behavior, so no FAIL half is owed (stating why, not sneaking — `PG-EV-09` attaches to claims, and this report claims re-proof only): full frontend suite ONCE on the candidate + tsc/eslint gates; targeted proof = existing AppHeader/ReviewPage suites green plus one render asserting the modal id and the tasks list load through the swapped wiring. No waste cut owed (`slowest_waste = none`, SG-196).

## Acceptance criteria

- A1: `useHouseholds(` product call sites drop to definition + provider (AppHeader outlier closed); exactly one `review-tasks` query definition exists (`useReviewTasks`; grep-gated).
- A2: full suite green on candidate (own count, not carried); tsc + eslint exit 0; targeted proof green; no assertion text changed in edited tests.
- A3 (report/receipt): first token SG-198; notes-ref receipt + mapped read-back, `Work-HEAD` recorded, pushes complete; elapsed per leg vs ~300 s uncalibrated Architect expectation (SG-184-class re-proof precedent, stated per `G-A9`); constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned.

Guards invoked: PG-EV-01/02/03; PG-IC-01/07/09; PG-PR-03/06. Stop follows `PB-6`.
