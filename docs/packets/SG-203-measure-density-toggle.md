# SG-203 — Measure the existing Catalog density toggle (read-only; feeds the D-6 density proposal)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none.**
**Autonomy: L4.** Basis: owner D-6 approval 2026-10-17 (P1 density proposal; recorded `docs/decisions/2026-10-17-d5-d6-d7-answers-l4-window.md`) + D-4 measure-first 2026-10-16 (`docs/decisions/2026-10-16-density-scope-d4.md`). Same class as SG-199/SG-190: lane browser harness, read-only GETs, committed evidence only. Dispatch settings ride the trigger, never this packet. No product change of any kind.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

D-6's binding refinement (1): **the existing Catalog density control has never been exercised.** SG-199 measured only the DEFAULT grid state ("no control designed, per packet", `SG-199_report.md:45`), so the proposal it feeds (SG-204) would rest on an unmeasured control. Measure the control first.

The control as it stands (verified by the Architect 2026-10-17, re-verify on target):
- `frontend/src/components/shell/CatalogToolbar.tsx:5` — `export type Density = "grid" | "table"`; label map at `:14` (`grid: "Standard Grid"` + the table label); props `density`/`onDensityChange` at `:44-45`; the segmented control renders at `:170`.
- `frontend/src/routes/CatalogPage.tsx:40` — `useState<Density>("grid")` (default is grid); threaded to `ProductGrid`/toolbar at `:203`, `:228`, `:238`.
- `frontend/src/components/catalog/ProductGrid.tsx:15-18` — grid CSS breakpoints 2/3/4/5 columns at 768/1024/1536; the table branch at `:330`; its labelled horizontal scroll container tested at `catalog.test.tsx:202-223`.
- Table shape: seven DQ5 columns in order (`catalog.test.tsx:175`); grid/table pass-through behaviour tested at `catalog.test.tsx:157-197`, `:398-446`.
- `frontend/src/components/shell/AppShell.tsx:16-17,40,64` — density state lives in the shell and reaches the toolbar.

Proven lane capability (re-verify on target, do not trust): host `chrome-headless-shell` + raw CDP over the DevTools websocket, dependency-free (SG-183); served-build rendering with loopback GET fulfillment; **the committed driver `docs/worklogs/SG-199_driver.mjs` already carries the fulfillment layer, the privacy masking, the controls and the strict comparator — REUSE it rather than rewriting** (frozen sha 229cffbe…, `SG-199_measure.json` → harness.sha256). Same dark mechanism: `sg-theme` localStorage (`ThemeProvider.tsx:20`), `.dark` on `<html>`, `.dark` token block in `tokens.css`.

## G1 — The toggle, measured on both states

Render the Catalog route in every SG-199 world and BOTH toggle states (select the table through the control itself — a click/keyboard on the segmented control, not a prop injection; record how the state was entered):

| world | states |
|---|---|
| 1440x900 light | grid + table |
| 1440x900 dark (`sg-theme=dark` seeded pre-load) | grid + table |
| 1280x900 light | grid + table |
| 200% zoom (CSS viewport halved @DPR2 — the SG-199 emulation, disclosed as such) | grid + table |
| touch (390x844, `mobile:true`, touch points) | grid + table |

Per world and state record: column/row counts and item width + gap (grid), row height + column count (table), document overflow AND the table container's own overflow/scroll behaviour, AA contrast on table cells (opaque pairs, exception semantics stated), and legibility/interaction notes for the control itself (target size + spacing at touch, focus ring, active-state signalling). Committed screenshots per world/state; **every image opened by the Coder** (`D425` — the audit opens every one too).

## G2 — Reproduce the SG-199 default-grid numbers (a hypothesis, not an assertion)

EXPECT the SG-199 catalog figures to reproduce at 1440/1280 light+dark — 4 cards x 248.0 px (gap 20) — and at the zoom200/touch worlds 2 x 280.5 (gap 16) / 2 x 163.0 (gap 16) (`SG-199_report.md:46`). Report the actual numbers either way; a difference is a finding about the tree (SG-196/SG-198 landed since), never a reason to adjust the expectation.

## Constraints

Scope ceiling: `docs/worklogs/SG-203*` ONLY (driver reuse/copy, controls, measure JSON, shots, report). No product/config/test/lockfile/schema/migration change; `git status` clean apart from the named evidence commits. No proposal document, no option design, no recommendation — that is SG-204.
Reads: lane CDP only; API GETs fulfilled from the direct loopback GET `127.0.0.1:8003`; zero credential/cookie forwarding; `Access-Control-Allow-Origin` injected by the driver only; zero non-GET forwarded; no production or evidence-store writes; fresh temp browser profile; no restart; DB/storage untouched (health start+end).
Fulfillment fidelity (`PG-EV-04`): byte-compare every fulfilled response against the direct loopback GET. **The `nondeterministic_clock_field` classifier SG-199 built and shipped is carried with its four fixture controls** (`SG-199_report.md:6`: `generated_at`-only ISO diffs classified; any other difference stays `unexplained` and exits 3, STOP kept); do not loosen it further without a named control. SG-199 was rated 98 with no flag.
Controls phase first (`SG-183` `controls.json` precedent; failed controls are failed prove executions per `CO-35`): at minimum the toggle control must prove it discriminates (grid state → grid DOM present, table state → table DOM present, and the wrong-expectation arm observed NOT holding), plus the zoom/touch/dark controls SG-199 used.
Masking AFTER measurement, layout-safe (`SG-199` scope: display names + UUID-shaped runs; product-shown short job ids/timestamps stay, same class as SG-199).
Auth-live and live-container rendering remain EXCLUDED (no credentials, no host grant) — stated, not silent.
Ordinary reads 120 s; browser/control runs 600 s; visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity/mount, no host config change. No secret in any log or artifact. `PB-2`: ANY privileged denial STOPS the whole slice. Full suite untouched/unrun (no product in scope — stated). No waste cut owed (`slowest_waste = none`, SG-199).

## Acceptance and report

- A1: per world/state numbers with denominators (columns/rows, item width + gap / row height + columns), document overflow AND table-container overflow, AA contrast pairs with exception semantics, control target size + spacing at touch — all committed in one measure JSON with DOM/API sources named (SG-183 schema precedent).
- A2: committed screenshots per world/state (EXPECT ≥ 20: 5 worlds x 2 states + control-close-ups), every one opened by the Coder and dispositioned for UI + layout + data issues together.
- A3: command + evidence logs, report `docs/worklogs/SG-203_report.md`; elapsed vs the Architect's recorded expectation (≈ 900 s; derived from SG-199's 1132 s where the driver was written from scratch and this slice reuses it — state the actual, `G-A9`); constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned; a named section "facts for the SG-204 proposal" carrying the table-vs-grid deltas and any defect found. First report token SG-203.
- A4: notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-203 | Report: docs/worklogs/SG-203_report.md`, Work-HEAD recorded, branch/report push complete. Use the bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-01/02/03/04/05/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10. Stop follows `PB-6`.
