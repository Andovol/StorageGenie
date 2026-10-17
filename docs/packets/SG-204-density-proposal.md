# SG-204 — D-6 density proposal: real options + renders off the measured facts (read-only lane; no product change)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none.**
**Autonomy: L4.** Basis: owner D-6 approval 2026-10-17 (P1 density proposal; recorded `docs/decisions/2026-10-17-d5-d6-d7-answers-l4-window.md`) + D-4 measure-first (`docs/decisions/2026-10-16-density-scope-d4.md`). Same class as SG-199/SG-203: lane browser harness for the renders, read-only GETs, committed evidence only. Dispatch settings ride the trigger, never this packet.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

D-6 (owner-approved): **build the density proposal with real options + renders.** Its two binding refinements:

1. **Exercise the existing grid/table toggle first** — DONE by SG-203 `2abe8a7` (rated 96). SG-203's measured behaviour is this proposal's factual base; SG-199 measured only the default grid state.
2. **Name the one measured item — native default button faces render off-token in dark (`SG-199_report.md:14`) — rather than invent requirements; options must include leave-it.**

D-4 recorded the promise (`2026-10-16-density-scope-d4.md:9`): "A density proposal with renders and real options follows the measurement." **No density requirement exists on record** — SG-190 kept the existing toggle; no compact/comfortable, persistence or per-surface rule was ever requested.

**Proposal step only:** NO density system is implemented before the owner picks an option. **This slice writes a document + render images; zero product/config/test/schema/migration change.**

## The measured facts this turns on (handed over; re-verify on target)

From SG-203 (`docs/worklogs/SG-203_measure.json`, report `SG-203_report.md`, driver sha `757f05c8`):

- **Table is ~4.9x denser per item vertically than the grid:** grid cards 248x296 (4-up; 612 px of column height for 7 items) vs table rows 61 px (457 px for 7 items); the table adds Category/Status/Added/Actions columns.
- **Horizontal cost:** the table's 7 columns need 838 px; at 1440/1280 the 1052 px content column fits them (no scroll), at 200%-zoom (577) and touch 390 (342) the table scrolls horizontally by 261 px / 496 px. The grid never scrolls horizontally (`docOverflowX` 0 in every world/state).
- **Both states are AA-clean:** table-cell AA 245/245, 0 below, min 5.2606 light / 10.4918 dark; density control active 9.4611, inactive 5.2606 light / 10.4918 dark.
- **The control defaults to grid and resets to grid on every fresh navigation** (`CatalogPage.tsx:40` `useState<Density>("grid")`; no persistence measured or claimed); operable by mouse and touch in both directions, aria-pressed signalling, 25 px high target (>=24, PASS-SIZE), 4 px gap at touch.
- **DEFECT FOUND (for this proposal, not fixed by SG-203):** dark-theme keyboard focus ring `ringVsSurroundingBgRatio` **1.7559** (light **9.8813**) against its surrounding toolbar — below the 3:1 non-text contrast used for focus indicators. Shared `.focus-ring`, `frontend/src/styles/tokens.css:173`; app-wide, not density-specific.
- **UI observations:** active font-weight 600 widens the active button ~5.75 px (group total 221.17 -> 221.16, internal jitter on every toggle); at 1280 the toolbar wraps "None yet" onto a second row; at narrow/zoom worlds the toolbar wraps to several rows and the sticky header consumes ~150-390 CSS px.
- **The table is the less usable state at narrow widths by measurement** (needs 261-496 px of horizontal scroll; the grid needs none).

From SG-199 (`docs/worklogs/SG-199_report.md`): native default button faces render off-token in dark (`:14`) — consistent and legible, a design input, not a failure.

The control as it stands (re-verify on target): `frontend/src/components/shell/CatalogToolbar.tsx:5` (`export type Density = "grid" | "table"`), `:14` labels, `:44-45` props, `:170` control; `frontend/src/routes/CatalogPage.tsx:40`; `frontend/src/components/catalog/ProductGrid.tsx:15-18` grid breakpoints (2/3/4/5 at 768/1024/1536), `:330` table branch.

## G1 — the proposal document

Path: **`docs/proposals/2026-10-17-density-proposal.md`** (convention: `docs/proposals/YYYY-MM-DD-slug.md`). Fixed structure; the option set is decided by the Coder within the constraints below.

- **Factual base** — the measured numbers, each cited to its source (`SG-199_report.md` / `SG-203_measure.json`). No claim without a measurement behind it.
- **Options** — **at least TWO real options PLUS leave-it.** Each option states, on its own labelled lines: **name**; **what changes** (files/tokens/behaviour); **what it GIVES**; **what it COSTS**; **the measured fact it rests on** (the number, with source); **the render filename**.
- **`options must include`**: (a) **leave-it** (keep the toggle as-is); (b) the **dark focus-ring defect** item (`.focus-ring`, `tokens.css:173`; SG-203 1.7559 dark vs 9.8813 light) presented as a candidate — do not fix it here; (c) the **native default-button off-token-in-dark** item named per refinement 2.
- **No invented requirements:** every option's premise traces to a measurement. An option that would need a requirement not on record is stated as **"owner must specify"** and marked, never invented (`D-6` refinement 2; `SG-190` found no requirement).
- **NO recommendation and no owner voice** — the document presents options, gives and costs only; the Architect frames the recommendation when it goes to the owner (`G-A1`).

## G2 — the renders

- One committed image per option, under **`docs/proposals/2026-10-17-density-renders/`** (names recorded in the document).
- Rendered from the **real Catalog on the lane harness** (the SG-203 driver shape: served build + raw CDP), never a drawn mockup (`PG-EV-07` — the render comes from the real route).
- The leave-it / baseline render MAY reuse the committed SG-203 shots by reference.
- Any option that changes rendering is produced by a **driver-injected CSS/DOM simulation on the real page**; the **EXACT injection** (the CSS/DOM string) is recorded in the document, and the render is **labelled a simulation of the option, never shipped behaviour**.
- Every render opened by the Coder and dispositioned for UI + layout + data issues (`D425`; the audit opens every one too).

## Constraints

- **Scope ceiling:** `docs/proposals/2026-10-17-density-*` ONLY (the document + the renders dir). No product/config/test/lockfile/schema/migration change; `git status` clean apart from the named commit. The lane driver is reused by **copy** under the proposal path (never an edit of SG-203's committed artifacts).
- Reads: lane CDP only; API GETs fulfilled from the direct loopback GET `127.0.0.1:8003`; zero credential/cookie forwarding; `Access-Control-Allow-Origin` injected by the driver only; zero non-GET forwarded; no production or evidence-store writes; fresh temp browser profile; no restart; DB/storage untouched (health start+end).
- **Renders are SIMULATIONS of options, disclosed as such** — never presented as shipped behaviour; no product bytes change.
- Excluded (stated, not silent): auth-live and live-container rendering (no credentials/host grant); native zoom / physical touch (emulations only).
- No interactive prompt or polling loop; no sudo; no alternate identity/mount; no host config change; no secret in any log or artifact. `PB-2`: ANY privileged denial STOPS the whole slice.
- Hang bounds: ordinary reads 120 s; browser/render runs 600 s; visible timeout finding; never approach idle kill 900 s. No waste cut owed — SG-203's audit named `slowest_waste = none` (nothing to remove).
- Full suite untouched/unrun (no product in scope — stated). Simplicity (`G-A7`): a document + N renders; no new machinery.

## Acceptance criteria

- **A1:** the document exists at the path; every factual claim carries its measured source; the option set includes leave-it; the dark focus-ring item and the native-button-off-token item are present; **no recommendation and no owner voice**; the "requirements not on record" note is present.
- **A2:** one committed render per option, each matching its option and labelled; injections recorded for changed-option renders; **every render opened by the Coder** and dispositioned for UI + layout + data issues together.
- **A3:** command + evidence logs; report `docs/worklogs/SG-204_report.md`; elapsed vs the Architect's recorded expectation (**≈ 700 s**, derived from SG-203's 731 s where the driver was written/reused for measurement and this slice reuses it for renders and adds document authoring — state the actual, `G-A9`); constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token `SG-204`.
- **A4:** notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-204 | Report: docs/worklogs/SG-204_report.md`, Work-HEAD recorded, branch/report push complete. Use the bound lane receipt, never the retired finalizer.
- **Presentation-only goal (`CO-25`):** the verification is the document + the renders + an owner checklist line per option; **no FAIL-then-PASS** (no behaviour changes).
- **Vacuity (`PB-3`):** name it — a proposal with zero options, or an option resting on no measurement, is a FAIL.

Guards invoked: PG-EV-02/03/05/07; PG-SC-01/05/09/10; PG-IC-01/07; PG-PR-01/03/04. Stop follows `PB-6`.
