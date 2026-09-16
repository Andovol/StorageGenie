# SG-044 — catalog shell: header, toolbar, taxonomy correction, note recovery (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Wardrobe track (D63, L3) step 2 of 5: SG-045 grid/cards own both density views over new cards; SG-046 drawer; SG-047 import modal. Prompt 2 + DQ answers are the spec; load-bearing brief/chat content is EMBEDDED below, never cited remotely (M19 — `docs/design/DQ-answers.md` is committed and citable by path). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (frontend-only; a needed backend change is a finding: STOP if it blocks, otherwise report and ship the rest — server-side category aggregation is EXPECTED to be missing, see G2); **no migration** (an alembic diff is a STOP); **AI stays OFF**: no provider calls, **$0 metered**; no new dependencies (lucide-react is already in); NETWORK: none.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` omission-traced · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-SC-11` end-relative-assertions · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live. (`PG-EV-06`/`PG-EV-08`/`PG-DP-02..04` do not fire: no live writes, no delivery change, no entry point, no reported failure.)

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. NETWORK: none.**

## Why this exists

The Catalog screen is unthemed inline controls (`CatalogPage.tsx:59-129` — household select, search input, two native dropdowns, `AssetCard` grid, Load-more); the global `Nav` (`App.tsx:11-47`) is a gray bar with six text links. This slice puts the wardrobe shell on the Catalog route: header (wordmark, count, search + ⌘K, toggle, Import) + toolbar (pills, sort, density state, filter tags) over the EXISTING data plumbing (`useAssets:useAssets.ts:5-25`, `AssetCard` grid stays this slice — SG-045 replaces cards and owns both density views).

## G0 — recover the two missing lane-local notes (first, cheapest, most load-bearing last)

Root mechanism (read from the runner, `dispatch:276-278`): `report_missing` does NOT mean
"no note" — it means a `Dispatch-ID:` note was found but `obj:path` does not resolve, i.e.
the note sits on a commit that does not contain the report file (the likely shape: noted
the feature commit, then committed worklogs after — against the "no commit after" order).
So for each of the SG-042 work HEAD `0c3b5702a7fede00cb939b88aa605fdd766b9062`
and the SG-043 work HEAD `307ae8c8698a2950fe22d8f7f04d67be30b16f8f`, classify the way the
runner does: find the note in the LANE-LOCAL notes ref, parse its `Report:` path, and run
`git cat-file -e <obj>:<path>`.
- Resolves → push the notes ref (300s bound), re-fetch, verify by `show` against the
  FETCHED ref, quote. Done: `notes-recovered`.
- Note exists but unresolvable (wrong obj) → re-attach the IDENTICAL note text to the
  final work HEAD (content unchanged, placement repaired), then push + fetched-verify +
  quote. Done: `notes-repointed`.
- Neither exists locally → report `notes-absent-on-lane` and move on — the gap stays a
  desk matter, not a second investigation.
Same lane, same dispatch user: provenance stays intact. This goal is reported with its own
elapsed line; it never blocks G1–G4.

## G1 — taxonomy correction (M19 fallout, `frontend/src/types/product.ts` + test)

- Replace `CANONICAL_CATEGORIES` with the DQ1 six EXACTLY (embedded — do not infer, do not "improve"): `Hardware & Tools`, `Electronics & Gadgets`, `Apparel & Textiles`, `Home & Decor`, `Packaging & Materials`, `Uncategorized`.
- Update the SG-043 test that locks the fashion six to assert these six (`PG-SC-11`: an assertion written relative to a wrong end is fixed where the end moves, in this slice, not left red).
- `toProductCategory` keeps passing custom strings through; `""`/`"unknown"` → `Uncategorized` (unchanged).

## G2 — header + toolbar + shell (new `frontend/src/components/shell/`: `AppHeader.tsx`, `CatalogToolbar.tsx`, `AppShell.tsx`)

- `AppHeader`: left wordmark "StorageGenie" + count pill `Total: N items` where N = the LOADED item count passed as a prop (labeled as loaded-count, never as a household total — the list API returns no total); center reserved (pills live in the toolbar, not the header); right search input (wired to the existing `q`/`qRaw` state), ⌘K/Ctrl+K keydown focuses it and selects text (DQ6 MVP fallback — the full palette is a later slice, and no user-facing text promises one), `ThemeToggle` MOUNTED here (the SG-043 deferred mount lands now), `Import Asset` primary button routing to `/capture` (the DQ9 modal arrives SG-047 — the button routes to the existing flow, labeled truthfully).
- `CatalogToolbar` (sticky below header): category pills = `All` + the DQ1 six + `Uncategorized`, active pill solid primary, inactive subtle; sort dropdown (`Recently Added` = `created_at` desc, `Name (A-Z)`, `Processing Status` = `status` field) applied CLIENT-SIDE over loaded items; density state (`Standard Grid` active, `Compact Table` present but routed to the grid with an honest "table view arrives with the new cards" note — SG-045 owns both views, and no text promises otherwise); active-filter tags (`q`, pill, sort) + `Clear all` resetting all three.
- Server-side category aggregation does NOT exist (no endpoint returns per-category counts): pills filter the loaded page via `toProductCategory`; the slice states this boundary in the report and queues a backend aggregation slice (named destination, not this slice).
- `AppShell`: composes header + toolbar + children; `CatalogPage` renders its content inside it, replacing ONLY its filter row (`CatalogPage.tsx:62-102`); the global `Nav` stays for other routes (their restyle is not this slice — no cross-route blast radius).
- All styling via SG-043 tokens + utility classes; focus rings visible in both themes; zero arbitrary colors.

## G3 — tests: new `frontend/src/components/shell/*.test.tsx`, mutation proof, both runs committed

- Render with the same `vi.mock("../api/client")` pattern; mock data via `assetToProductItem` (real mapper, not fixtures): pills filter the loaded set, search narrows, sort orders, clear-all resets, ⌘K focuses search, toggle flips the theme class, Import routes to `/capture`, taxonomy test asserts the DQ1 six.
- **Pre-change honesty (class 8):** new modules fail on unresolvable imports — quote + label hollow, never evidence. Discriminating proof is a post-change mutation run (2–3: a pill label, the sort comparator, the taxonomy list — each caught singly, reverted clean, raw committed).
- Full frontend suite green, lint clean, build clean — the §3 conditional derived-test-set block is NOT pasted.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-044.log`, `{{WORKLOG_DIR}}/SG-044_report.md`, `{{WORKLOG_DIR}}/SG-044_verify.log` (G0 output, hollow run labeled, mutations raw). First token `SG-044`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/shell/` (4 files, new) · `frontend/src/routes/CatalogPage.tsx` (filter-row replacement only) · `frontend/src/types/product.ts` (taxonomy hunk only) · `frontend/src/types/product.test.ts` (lock-fix hunk only) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`, grep-gated), `App.tsx`/`AssetCard.tsx` (untouched this slice), and any new dependency. No new files outside `shell/` + worklogs.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G0 needs only git (no tree writes); G1 the types file + its test; G2 the four shell files + `CatalogPage` filter row; G3 the shell tests. No blanket exclusion is issued. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: mutations fed wrong values in the same run, shown failing singly. `PG-EV-02`: rendered DOM / committed outputs, never exits. `PG-EV-05`: properties ("active pill carries the primary style", "⌘K moves focus to search", "clear-all empties all three filters", "taxonomy equals the six embedded names").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1500s early-close** · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): shell + taxonomy fix + note recovery; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises verified in-slice with quoted reads — in particular `App.tsx:11-65`, `CatalogPage.tsx:15-58` (state) + `:62-129` (filter row + grid), `useAssets.ts:5-25`, the DQ1 six (embedded above), the two note HEADs (G0).
- G0 reported with its own elapsed line, either `notes-recovered` (pushed + fetched-verified + quoted) or `notes-absent-on-lane`.
- Taxonomy equals the six embedded names; the old fashion-six test is updated, not left red; badge hexes UNTOUCHED (SG-045 owns them — touching them here is scope overreach, `RATING_ISSUE.md` class 15).
- **FAIL-then-PASS honestly (`PG-EV-09`):** hollow run labeled hollow; green run; mutation run caught-singly + reverted; all three raw committed.
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: no DB writes, live spend `$0`, no network.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-044 | Report: docs/worklogs/SG-044_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (a default fetch never carries notes), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered; actual-versus-budget per leg with units.
