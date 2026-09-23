# SG-105 — UI centering + control consistency repair, Inbox/Capture/Catalog (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D1-approved (owner quote "D1 - approved"). Owner screenshots 2026-09-23 (3: Inbox, Capture — Manual Create, Catalog) + Architect audit UI-1…UI-10 recorded in chat the same day — the audit table is evidence, not ground truth: every premise below is a hypothesis under the frame, re-verify against the tree. SG-104's open threads (F-SG104-3 Jina EU, F-SG103-5 brand) are out of scope and not inherited. **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** presentation ONLY. No backend change (`backend/` untouched — prove by diff), no models/migration, no deploy, no restart, no container action — the running service is untouched (`PG-PR-04`); the served bundle still shows the old UI until a later rider, and the proof here is build + suite, said in as many words. $0, no network, no secrets anywhere. Key/secret material never in any file, log, or assertion; `docker compose config` FORBIDDEN (`PG-SC-05` — it prints secrets).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-11` · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (no privilege needed — enumerate nothing, touch nothing) · `PG-PR-03` · `PG-PR-04`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 1200s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none** (no backend file in the ceiling — prove by diff). **Restart: none. Deploy: none. Container actions: none.**

## Why this exists

Owner screenshots show three pages with three different layout treatments and browser-default controls leaking through the dark theme. Code reads 2026-09-23 confirm the structure (visual rendering itself is inferred from the screenshots — CONFIRMED: code shapes below; INFERRED: exact pixels): page containers differ — `InboxPage.tsx:22` (`padding: 24, maxWidth: 1100`, no centering) vs `CapturePage.tsx:22` (padding only) + `AssetForm.tsx:112` (`maxWidth: 520`) vs `AppShell.tsx:77` (`main` padding only); selects differ — bare (`InboxPage.tsx:23`), inline-only (`CapturePage.tsx:27-33`, `AssetForm.tsx:126`), themed only in the toolbar (`CatalogToolbar.tsx:120`); file inputs raw (`AssetForm.tsx:169-186`); `JobCard` button sets background with no text color (`JobCard.tsx:9` — black-on-dark titles); review `Link`s unclassed (`InboxPage.tsx:28` — purple on dark); brand rendered twice on Catalog (`App.tsx:32-38` + `AppHeader.tsx:49-55`); cards fixed `aspectRatio: 3/4` (`ProductCard.tsx:113` — dead space); pills speak raw `asset_type` (`CatalogPage.tsx:77-87`) while cards speak the display map (`types/product.ts:89` `unknown` → `Uncategorized`).

## G1 — one centered page container on all three pages

- Introduce ONE shared container (new small component or shared style — decide and report) with a single page max-width and centering; apply it to Inbox, Capture, and the Catalog `main` (`AppShell.tsx:77`). Narrow form width (today's `520`) becomes the container's form variant, not a per-file constant. No page keeps a hand-rolled `maxWidth`/padding pair.
- `PG-SC-07`: empty states stay correct — no jobs, no review tasks, empty catalog all still render their status messages, never a blank page.

## G2 — one themed control treatment (selects + file pickers)

- ONE select treatment carrying the theme (`bg-background text-foreground border-border`-equivalent — reuse the toolbar's classes or a shared class, decide and report); apply to the Inbox household select, the Capture household select, and the asset-type select. ONE household-selector reuse (shared component preferred over three copies — decide and report).
- File pickers stop rendering raw native buttons: style via label-triggered hidden inputs or equivalent (decide and report); keyboard + screen-reader behaviour preserved (real `<input type="file">` still in the DOM and asserted).

## G3 — readable Inbox (cards, links, queue)

- `JobCard`: titles and status read on the dark card — theme text color on the button, status toned by state (decide the exact tones and report; no browser-default text anywhere in the card).
- Review-queue `Link`s carry the theme link treatment (no default purple); queue hides `resolved` rows by default (filter or default-scope — decide and report; Planning's status filter is the in-tree precedent).

## G4 — coherent Catalog (chrome, grid, vocabulary)

- Single brand chrome on the Catalog route: drop ONE of the two brand rows (global nav vs `AppHeader` — decide and report; the other seven routes keep the global nav untouched).
- Grid contained by the G1 container; no card clipped at the viewport edge at any breakpoint in `ProductGrid.tsx:15-18` (keep the breakpoint counts or move to auto-fill — decide and report). Cards size to content (no fixed `3/4` dead space); media well uniform across aspects with the badge legible on white photos (badge keeps its semantic token classes — the dead Tailwind utility strings stay untouched, out of scope, said in as many words).
- ONE category vocabulary: pills and cards agree — pills display the same names cards show (`toProductCategory` is the existing map; a pill for `Uncategorized` selects `asset_type=unknown` through the REAL server filter — writer and reader both in acceptance, `PG-SC-02`). `types/product.ts` changes only if the mapping itself needs it (disclosed).

## G5 — tests + gates

- New or extended vitest file(s) (decide and report — colocated with the touched components): container centers content (assert the shared style/class on the rendered page, not a screenshot); every select + file input carries the theme treatment (assert DOM classes, never pixels); `JobCard` title/status carry theme text classes (assert classes/tokens present in the DOM, not a screenshot); resolved tasks hidden by default with a real resolved fixture; pills↔cards vocabulary round-trips through the real filter path (`PG-SC-12` — real components, real `toProductCategory`, real filter state; no re-implemented seam). FAIL-then-pass raw BOTH runs committed (`PG-EV-09`); every new gate seen to fail pre-change (`PG-EV-01`).
- Full frontend suite green (`npm test`), `tsc` clean (via `npm run build` — build doubles as the type gate), `eslint src` clean; backend suite explicitly WAIVED (no backend file in the ceiling — collision repair only per M45, disclosed). `PG-SC-11` end-relative grep over touched test files committed raw. Secret gate 0 with the literal grep quoted.
- Visual proof BAN: you cannot screenshot — NEVER claim a visual result; assert DOM/token-level properties only (`PG-EV-05`). The owner signs off pixels post-deploy.

## G6 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-105.log`, `SG-105_report.md`, `SG-105_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate). First token `SG-105`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** G1 container (new shared file(s) + `InboxPage.tsx` + `CapturePage.tsx` + `AppShell.tsx`) + G2 (`AssetForm.tsx` + household selects) + G3 (`JobCard.tsx` + `InboxPage.tsx` queue) + G4 (`AppHeader.tsx` or `App.tsx` nav — ONE of them + `ProductGrid.tsx` + `ProductCard.tsx` + `CatalogToolbar.tsx`/`CatalogPage.tsx` pills + `types/product.ts` only if the map needs it) + frontend test files + `docs/worklogs` — NOTHING else. **Suite-green binds on collision** (minimal root-cause repair + disclosure, M45); anything else is a STOP. No criterion demands backend, migration, deploy, or a live call — no cell collides (`PG-IC-01`); stated so the check exists on paper. Reads include repo files + `npm`/`npx` only; pulling/running images or launching unnamed runtimes counts as execution — not authorised.
- Privacy: no key material in any file, log, or assertion (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- All three pages share the centered container; no hand-rolled page `maxWidth` remains.
- Every select + file picker carries the theme treatment; no native white control on any of the three pages.
- Job titles/status legible classes on dark cards; review links themed; resolved rows hidden by default.
- One brand row on Catalog; grid unclipped at every breakpoint; cards content-sized; pills and cards share vocabulary through the real filter.
- Tests fail-pre/post-pass both committed raw; full frontend suite + build + lint green; backend waived by ceiling; secret 0; no vacuous pass; no visual claim anywhere.
- Question each criterion answers (`PG-SC-09`): G1 — does every page share one centered layout? G2 — is every control themed? G3 — is the Inbox readable and honest about resolved work? G4 — is the Catalog one coherent surface? G5 — does the suite prove it through the real components?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-105 | Report: docs/worklogs/SG-105_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1200s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
