# SG-190 — R8: responsive shell/design recovery (DRAFT, next session)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: DRAFT prepared 2026-10-13 from the consolidation UI plan (`SG-182_consolidation.md:72-74`); scope-approved D9 (after correctness slices D4–D6). Presentation-only slice: no behavior change. RE-REVIEW against the tree before dispatch next session.**
**DATABASE: none touched (presentation only; any fixture reads use disposable state or committed captures).**
**Restart: none. Autonomy: L2.** No packages/frameworks added; reuse AppShell/AppHeader/Nav/tokens/components. Correctness slices (R1/R2/R3/R4/R6) are not reopened here — visual follow-ups to their surfaces ride only as styling, never as logic.

## Why this exists

Sampled verdict SC-15 BROKEN: independently recomputed document overflow 10/10 routes at 390px, 9/10 at 834px, 0/10 at 1440px; muted-text sampled contrast 4.3977 < 4.5 (SG-183 audit; rejected claims — phone-clean, size-only, alpha, forced-focus — stay rejected, no third correction). The consolidation UI plan (Architect/Coder judgement, not owner decision) scopes one shared shell: persistent household context, active destination, primary capture action, discoverable Inbox/task status; narrow layouts use an accessible menu (no hidden focusables); Catalog responsive toolbar with honest loaded-vs-whole wording; consistent card/table density; distinct loading/empty/error/retry; Capture accepted-formats/limits + readable errors + durable progress/retry; Review/expiry fields beside evidence where space permits with explicit Unknown/blockers; Detail edit/history/evidence separation; Settings groups only in-scope functions. Acceptance sources (not conformance claims): W3C reflow (320 CSS px non-excepted), target-size-minimum (with spacing/exception semantics), contrast-minimum, focus-not-obscured-minimum.

## G1 — Shared shell + Catalog/Capture (widest surfaces first)

One nav/context system across routes; responsive Catalog toolbar + cards/tables; Capture surface honesty (formats/limits/errors/progress). Cheapest-and-most-load-bearing first per the plan; CSS-only where it suffices, coherent composition where it does not (the plan's comparison already judged pure CSS-only insufficient alone — do not relitigate, execute the reuse-first sequence).

## G2 — Review/expiry/detail/Settings states

Stacked-narrow Review/expiry with the real completing action visible; data-required tasks show their blockers; Detail history/evidence distinguishable; dormant features never presented as data absence; loading/empty/error/retry distinct everywhere touched; form drafts/feedback/focus preserved.

## Constraints and acceptance

- Write ceiling: frontend shell/routes/components/CSS + colocated tests, `docs/worklogs/SG-190*`. No backend logic change; no route/API contract change; no package/framework addition; no production write; no paid call; no infra change; no restart.
- Presentation-only acceptance per `CO-25`: committed real-browser screenshots (390/834/1440 per the SG-183 sampled shape, desktop rendering stated; 320px reflow + normal Tab + zoom/touch where the harness supports, each explicitly stated with its limits) plus an owner checklist. The Architect independently opens EVERY image (`D425`/0.47 AUDIT) — a written screenshot audit alone is not evidence.
- ALL optional environment/Docker probes excluded; ANY privileged denial STOPS the whole slice. No third SG-183 correction by another name: previously rejected claims (alpha compositing, preventScroll focus) are not re-argued — plain correct behavior is implemented and measured.
- Ordinary commands 120s; browser/control runs 600s; no full suite; no watcher.
- Start/end health GET; contract 0.47.0 echo + source; base/Work-HEAD/settings/lane budget/deadline/elapsed.
- A1: sampled SG-183 denominators re-measured on the new shell (overflow counts per viewport, contrast numbers with opaque pairs and exception semantics stated) — improvement shown numerically or the shortfall named.
- A2: keyboard/focus honesty — normal Tab order, no focus loss behind sticky elements, drafts preserved; every claim has a screenshot + checklist line.
- A3: no logic drift — backend/API untouched (diff proves it); no rejected-claim revival.
- A4: first token SG-190; `docs/worklogs/SG-190_report.md`; FIRST READ / DURING EXECUTION / REMAINING with dispositions.

Guards: PG-EV-01/02/03/04/05/06/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10.

Receipt: commits `Dispatch-ID: SG-190`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-190 | Report: docs/worklogs/SG-190_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates (every evidence image opened) before close. No close or deploy in this slice.
