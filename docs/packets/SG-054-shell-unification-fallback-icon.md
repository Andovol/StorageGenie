# SG-054 — shell unification + sourceless fallback icon + table overflow + count grammar (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Feedback track (D71, L2) after the wardrobe arc: the catalog ships the
new token shell but the legacy light `Nav` still wraps every route, so the live catalog shows two
"StorageGenie" wordmarks (white bar over dark header). S2/SG-048 fires after this lands (D72); S3/SG-049
after that (D73/D62). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard
job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-053 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (frontend-only; a needed backend change is a finding: STOP if it blocks, otherwise report and ship the rest); **no migration** (an alembic diff is a STOP); **AI stays OFF**: no provider calls, **$0 metered**; no new dependencies (lucide-react is already installed — verify the glyph export by grep, never assume it); NETWORK: none except loopback health/bundle reads on the box.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-08` before-capture · `PG-EV-09` both-runs-committed · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-SC-11` end-relative-assertions · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-04` code-becomes-live · `PG-DP-02` no-sweep-in-restart-slice · `PG-DP-03` live-repro. (`PG-EV-06`/`PG-SC-02`/`PG-DP-04` do not fire: no datastore rows created, no new recorded field, no new entry point.)

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 900s host build/up leg. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (no migration; blessed rows read-only). Restart: backend container via compose rebuild+up (authority D71 below; `PG-PR-04`). NETWORK: none except loopback reads on the box.**

## Why this exists

Owner live pass 2026-09-16 (filed `docs/feedback/2026-09-16-live-UI-feedback.md`, 4 screenshots): (1) the
catalog shows the legacy white `Nav` stacked over the dark token `AppHeader` — two "StorageGenie"
wordmarks; (2) the Toothpaste asset (source-only, no photo) renders an empty dark well in the grid and an
empty square in the table — no fallback; (3) the compact table forces page-level sideways scroll (columns
cut: "Dim…", pills cut: "Standard…"); (4) the header reads "Total: 1 items". Expected-state premises
(re-verify in-slice per `PG-IC-09`, quote what you read): legacy nav `frontend/src/App.tsx:11-47`
(hard-coded `#f9fafb`, six text links) + root `App.tsx:51` hard-coded white; shell
`frontend/src/components/shell/AppShell.tsx:44-63` + `AppHeader.tsx:37-112` (tokens, count pill
`AppHeader.tsx:56-63`); empty branches `frontend/src/components/catalog/ProductCard.tsx:136-144` and
`TableThumb` `frontend/src/components/catalog/ProductGrid.tsx:71-97`; fixed columns
`ProductGrid.tsx:41-49` with a bare `<table>` at `:113`.

## G1 — one header on the catalog route (scope: `frontend/src/App.tsx` only)

- On the catalog route (`/`), render NO legacy nav — `AppShell` (header + toolbar) is the single header.
  On every other route, the legacy nav stays byte-identical (their token migration is SG-055+, not here).
- Routing, all six links, and every non-catalog route's rendering are unchanged. Criterion is by ROUTE
  (enumerate the routes on the target: `/`, `/capture`, `/settings`, `/inbox`, `/planning`, `/chat`,
  `/assets/:id`, `/review/:candidateId` — state the criterion, enumerate there, report any difference
  either way): exactly one "StorageGenie" wordmark on `/`, nav present elsewhere.

## G2 — fallback glyph for sourceless items (scope: `ProductCard.tsx` + `ProductGrid.tsx` hunks only)

- Grid well and table thumb with no media (no cutout/scene/evidence thumb, or broken image) render a
  neutral glyph tile: a parcel/box glyph from the ALREADY-INSTALLED lucide-react (verify the export by
  grepping the installed package — I do NOT know which glyph names exist, establish before choosing; if
  none fits, a styled initial-letter tile — decide and report), muted-token styling, `data-testid="product-fallback-icon"`.
- Failed-state visuals (`failed` badge, `AlertTriangle`, rose border) are untouched.

## G3 — no page-level sideways scroll (scope: `ProductGrid.tsx` hunk only)

- The compact `<table>` rides in a scroll container (`overflow-x: auto`, labelled region) so the PAGE never
  scrolls sideways; every column stays reachable by container scroll. Toolbar pills are NOT restyled unless
  your enumeration finds a real pill overflow after the table fix — report the check either way.

## G4 — count grammar (scope: `AppHeader.tsx` hunk + shell-test update only)

- `Total: 1 item` singular vs `Total: N items` otherwise; the loaded-count label/title semantics stay
  (`aria-label` keeps carrying the loaded-count meaning). `PG-SC-11`: grep every assertion written
  relative to the count text ("Total:", "total loaded") and update each hit in this slice — name the hits.

## G5 — tests: extend `shell.test.tsx` + `catalog.test.tsx`, mutation proof, both runs committed

- New assertions (real `CatalogPage` render, existing mock pattern): single wordmark on `/` + nav present
  on `/capture`; fallback glyph renders for an evidenceless asset in BOTH densities (grid well + table
  thumb) and vanishes when media exists; table scroll container present with no page-level overflow marker;
  singular/plural count text.
- **Pre-change honesty:** FAIL-then-PASS against the pre-change code for every new behaviour, BOTH runs raw
  committed to `{{WORKLOG_DIR}}/SG-054_verify.log` (`PG-EV-09`); mutation run post-change (2–3: fallback
  branch, grammar branch, scroll wrapper — each caught singly, reverted clean, raw committed, `PG-EV-01`).
- Full frontend suite green, lint clean, build clean.

## G6 — deploy + prove live (authority D71; `PG-PR-04`: code becomes live via compose rebuild+up)

- BEFORE capture (`PG-EV-08`/`PG-DP-03`, read-only): served bundle asset name, bundle contains the legacy
  marker (grep the served asset for the legacy hard-coded value), health exact, blessed-row counts
  (household=1, user=2, asset=1 Toothpaste, evidence=1, assertion=3, audit_event=3 — `PG-IC-08`: if the
  measured counts differ from these in EITHER direction, STOP and report before writing anything).
- Rebuild + up (900s bound; build TEXT is the verdict, never the exit code), idempotent re-`up -d`
  (same container, RestartCount=0). AFTER: health exact, served asset name CHANGED, legacy marker ABSENT
  from the served bundle, wardrobe markers present, 8003 loopback-only, nginx gate 301/401 (on-box checks
  use the loopback Host-header form per the F-SG053-2 standing line — never claim an external vantage from
  the box). Blessed counts re-read EQUAL. Full e2e sweep WAIVED per `PG-DP-02` (restart-gated slice);
  substitute = the targeted checks in this goal, named here.

## G7 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-054.log`, `{{WORKLOG_DIR}}/SG-054_report.md`, `{{WORKLOG_DIR}}/SG-054_verify.log`
(G5 both runs + mutations raw, G6 before/after captures raw). First token `SG-054`;
elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`);
three UNCLEAR lines. "STOP and report" is satisfied ONLY by the `BLOCKED:` commit path, never by
disclosure alone (`PG-EV-03`).

## Constraints

- **Scope ceiling:** `frontend/src/App.tsx` (nav-conditional hunk only) · `frontend/src/components/catalog/ProductCard.tsx` (fallback hunk only) · `frontend/src/components/catalog/ProductGrid.tsx` (thumb + scroll-container hunks only) · `frontend/src/components/shell/AppHeader.tsx` (grammar hunk only) · `frontend/src/components/shell/shell.test.tsx` + `frontend/src/components/catalog/catalog.test.tsx` (assertion hunks only) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`, grep-gated), Capture/Chat/Settings/Inbox/Planning/Review/AssetDetail/AssetForm restyles (SG-055+ owns them), and any new dependency. No new files outside worklogs.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued; G6's restart shares no condition with any remediation step — stops win. Reads MAY pull/run the already-built local images only (no new runtime); anything else is a STOP.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-02`: rendered DOM / served bundle bytes / committed logs, never exits. `PG-EV-05`: properties ("one wordmark on `/`", "glyph shows with no media in both densities", "page has no sideways scroll", "`1 item` vs `N items`").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 900s host build/up leg · **1500s early-close** · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): header dedup + fallback glyph + scroll container + grammar; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular `App.tsx:11-65`, `ProductCard.tsx:60-78 + :116-170`, `ProductGrid.tsx:41-49 + :71-113`, `AppHeader.tsx:49-63`, installed lucide-react glyph exports.
- Route enumeration: one wordmark on `/`, legacy nav intact elsewhere; no restyle outside the ceiling.
- **FAIL-then-PASS honestly (`PG-EV-09`):** pre-change failing run + green run + mutation run caught-singly, all three raw committed. Live before/after captures raw committed (`PG-EV-08`).
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; dep list unchanged; blessed counts equal; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: no DB writes, blessed counts before/after, live spend `$0`, no network beyond loopback.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-054 | Report: docs/worklogs/SG-054_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (a default fetch never carries notes), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 900s host build/up · 1500s early-close · 2100s overall; $0 metered; actual-versus-budget per leg with units.
