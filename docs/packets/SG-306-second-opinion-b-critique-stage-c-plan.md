# SG-306 — Second opinion Phase B (critique): the order and slicing of the rest of stage C

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. This lane's snapshot has no `.git`: state `unknown` once and carry on.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A is done (`docs/worklogs/SG-305_report.md`, committed unedited). This is **Phase B — the critique.** Attack the pick below. It is the Architect's **recommendation**; under L3 the Architect acts on it after this review and reports to the owner.

## The pick, verbatim

> **P1 — Order:** rider SG-303 now (SG-273 + SG-300 + SG-302 live), then SG-301, its rider, SG-307, its rider, SG-304, its rider, then the owner's formal shelf trial. The owner may take an informal first look as soon as SG-303 is live; that look is not the stage's end check.
>
> **P2 — SG-301 split by screen group, not by concern** (Phase A's missed option (c)), so no surface is worked twice:
> - **SG-301 (Muse, the next rotation slot after SG-303 on Haiku):** the pinned Instrument Sans package (D31); the shared chrome — the app header and navigation (`frontend/src/App.tsx` ~`:65-75`, `frontend/src/components/shell/AppHeader.tsx`) — in the paper/ink tokens with square corners; plain words on the Inbox, Expiry page and asset page (the developer copy found by criterion, a shared label map); the Pantry EXPIRED label to ≥ 13 px; **and one behaviour fix:** drawer saves, gone, put back and quantity changes made from the Pantry refresh the Pantry (`ItemInspectorDrawer.tsx` ~`:143-210` invalidate only `["assets"]` and `["asset", id]`; the Pantry reads `["pantry-assets", hh]` and `["pantry-expiry", hh]`, `PantryPage.tsx` ~`:256-266`; confirmed by the Architect's read, not yet observed at runtime), with a FAIL-then-PASS test.
> - **SG-307 (Haiku):** the catalog and the item panel together — plain words and the full tandpfun look, one pass over each surface.
> - Each finishes a coherent, usable state, gets its own rider, and keeps the 1300 s stop for Muse.
>
> **P3 — Trial entry, a bounded envelope, nothing added to stage C beyond the above:** SG-303 verifies the existing Pantry menu link and `/pantry` route live; the owner's first look checks real-photo legibility (original photos stay through C); the trial is one small shelf, with the exposure that restore is unproven until stage D (roadmap §D) stated to the owner before real data goes in; SG-304's packet requires that an "update existing" offer never merges quantities or overwrites another pack's date, and that a second physical pack stays creatable.

## G1 — Read

`AGENTS.md`'s top section, `docs/reviews/2026-11-12-stage-c-remaining-plan-context.md`, `docs/worklogs/SG-305_report.md`, `docs/worklogs/SG-302_audit.md`, and the source files named in the pick. **Do not read `STATE.md` or `docs/decisions/`; file-targeted reads only.** List every file read beyond those.

## G2 — Per part of the pick (P1–P3)

- the strongest case against it, with evidence (`file:line`, a quote, a measurement);
- a premise of it that is unverified;
- the observation that would settle any disagreement.

An objection without evidence is labelled `opinion`. Check especially: whether SG-301 as now scoped still fits Muse's 1300 s stop given the shared chrome and the behaviour fix; whether the invalidation fix belongs in a design slice or its own; and whether deploying SG-303 with the known Pantry refresh defect is acceptable before SG-301 fixes it.

## G3 — Report

Your final message **is** the report (read back with `SG-306 --status`; the Architect copies it unedited to `docs/worklogs/SG-306_report.md`). **Keep the whole report under 100 lines.** The most serious objection first. Shape: `SG-306` as the first token; the contract-version line (`PB-4`); the extra-files list; P1–P3; one closing line stating you wrote nothing.

## Constraints

Read-only; reads confined to the repository at BASE; no host commands, Docker, credentials, browser, network or database. Hang bound: file reads 120 s each. A denial is a STOP (`PB-2`).

## Scope ceiling

No write of any kind. Reads only as in G1.

## Acceptance criteria

Each part of the pick answered; each objection evidenced or labelled `opinion`; extra-files list complete; report under 100 lines. `PB-3` vacuity: "no objection" needs one sentence on what was checked.

## Report

Destination: final message (engine-published). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.
