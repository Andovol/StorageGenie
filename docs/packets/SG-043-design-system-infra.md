# SG-043 — design-system infra: semantic tokens, theme provider + toggle, product view types (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Wardrobe design track (D63, L3) step 1 of 5: SG-044 shell → SG-045 grid → SG-046 drawer → SG-047 import modal build on this slice. Prompts 1–4 + DQ1–DQ10 answers are the spec; the answers override the prompts where they differ (taxonomy DQ1, tokens-over-Tailwind DQ2, dark table DQ3, retention DQ4, MVP fallback DQ6, system fonts DQ8). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (frontend-only; a needed backend change is a STOP); **no migration** (an alembic diff is a STOP); **AI stays OFF**: no provider calls, **$0 metered**; frozen prompts read-only context. **Single network exception:** exactly one `npm install lucide-react` (registry only, honors the `^` range convention in `frontend/package.json:12-18`); if the registry is unreachable → STOP, do not vendor, do not substitute. No other network.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` omission-traced · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live. (`PG-EV-06`/`PG-EV-08`/`PG-DP-02..04` do not fire: no live writes, no delivery change, no entry point, no reported failure.)

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 300s the single npm install, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. NETWORK: the single lucide-react install only.**

## Why this exists

The app is unthemed inline styles; the wardrobe track needs tokens, a dark/light provider, and view schemas before any screen is restyled. Verified current shape: `frontend/src` holds **zero `.css` files** (glob 2026-09-16 — every screen is inline styles); `main.tsx:1-19` imports no stylesheet and mounts no provider; `index.html:1-12` has a bare `<head>` (the FOUC-guard insertion point); `package.json:12-31` has no lucide, no tailwind, test = `vitest run`, lint = `eslint src`, build = `tsc && vite build`; `api/types.ts:1-197` carries the domain to map from (`Asset:29-44`, `Evidence:3-10`, `Job:61-71`, `AiSettings:115-123` with consent + provider/model ids).

## G1 — semantic tokens (`frontend/src/theme/tokens.css`, new, first stylesheet)

- `:root` (light) + `.dark` (class on `<html>`) carrying every token as `hsl(var(--x))`-shaped custom properties per DQ2: `background, foreground, card, card-muted, border, muted, muted-foreground, primary, primary-foreground`.
- Values: light canvas Stone-50 (`#fafaf9`); dark layers EXACTLY per DQ3 (`--background #0F0E0D`, `--card #1C1A18`, `--card-muted #262320` inset wells, `--border #2C2926`); status badge palettes for both themes EXACTLY per DQ3 (emerald/sky/stone/rose pairs — no neon, WCAG AA contrast pairs as specified).
- Utility-mapping classes for every token used (`.bg-card`, `.text-muted-foreground`, `.border-border`, … — DQ2's plain-CSS mapping, no Tailwind installed for this).
- Type: system sans stack + `ui-monospace…` stack per DQ8; **no webfont, no `@import` of remote fonts.**
- Zero arbitrary colors elsewhere in this file: every rule references a token.

## G2 — provider, toggle, wiring (`frontend/src/theme/ThemeProvider.tsx`, `ThemeToggle.tsx`, `index.html`, `main.tsx`)

- `ThemeProvider`: system/light/dark, class toggle on `<html>`, `localStorage` persistence, OS-preference default; FOUC guard = a small inline script in `index.html:<head>` (reads the stored/system choice before paint) — the index.html change is that ONE hunk, byte-diff quoted.
- `main.tsx` change is TWO hunks only: import `tokens.css`, wrap the tree in `ThemeProvider`. No other behaviour change.
- `ThemeToggle`: `Sun`/`Moon` from `lucide-react`, accessible label, keyboard-focusable with a visible ring in both themes.
- **The toggle is delivered + tested but NOT mounted in `App` this slice** (decision, reported not hidden): no screen reads tokens yet, so a live toggle would flip nothing — mounting arrives with the SG-044 shell. No dead control ships.

## G3 — product view types + mappers (`frontend/src/types/product.ts`, new, + tests)

- `ProductItem` (`id, name, category: string, description?, tags: string[], dateAdded, status 'raw'|'processed'|'rendered', metadata {dimensions?, primaryColors?, material?, notes?}`), `AssetMedia` (`originalUrl, isolatedCutoutUrl?, sceneRenderUrl?, boundingBox? {x,y,width,height}` fractions 0–1 per DQ4), `RenderJob` (`jobId, status 'idle'|'processing'|'completed'|'failed', modelInfo? {provider, model, executedAt, latencyMs} per DQ4`) — **no `rawResponse` field anywhere, by rule (DQ4 retention: raw provider payloads are never persisted; a test asserts mapper output carries no such key).**
- `CANONICAL_CATEGORIES` = the DQ1 six, exported; category mapping passes custom strings through (user-extensible per DQ1).
- Mappers `assetToProductItem` / `evidenceToAssetMedia` / `jobToRenderJob` read ONLY `api/types.ts` (read-only context, ceiling exception below): name←`display_name`, dateAdded←`created_at`, status defaults `'raw'` (DQ10 initial), media past the original + cutout/scene absent until the S3 era, job states mapped with an explicit default + test. Nothing invented: unmapped spec fields stay optional/empty WITH a comment naming the slice that will fill them. **No user-facing text asserts derivation that does not happen** (`PG-SC-02`).
- Evidence URL resolution: `EvidenceGallery.tsx` is the file that knows it — read it in-slice for the `originalUrl` construction, do not guess the route.

## G4 — tests: FAIL-then-PASS honestly, both runs committed

- New `frontend/src/theme/theme.test.tsx` (provider class application + persistence + toggle icons/labels) and mapper tests in `frontend/src/types/product.test.ts` (taxonomy passthrough, status mapping + default, bbox fractions, no-`rawResponse`-key assertion).
- **Pre-change honesty (`RATING_ISSUE.md` class 8):** these modules do not exist on the base tree, so a pre-change run fails on unresolvable imports — quote it as context and LABEL it hollow, never as evidence. The discriminating proof is a **mutation run post-change** (2–3 mutations: a token value, a mapper default, the taxonomy list — each caught, reverted clean, raw committed), per the adopted P1 direction.
- Full frontend suite green (`npm test`), `npm run lint` clean, `npm run build` clean — so the §3 conditional derived-test-set block is NOT pasted.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-043.log`, `{{WORKLOG_DIR}}/SG-043_report.md`, `{{WORKLOG_DIR}}/SG-043_verify.log` (mutation runs raw; pre-change hollow run labeled). First token `SG-043`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/theme/tokens.css` (new) · `frontend/src/theme/ThemeProvider.tsx` (new) · `frontend/src/theme/ThemeToggle.tsx` (new) · `frontend/src/theme/theme.test.tsx` (new) · `frontend/src/types/product.ts` (new) · `frontend/src/types/product.test.ts` (new) · `frontend/index.html` (ONE head-script hunk) · `frontend/src/main.tsx` (TWO hunks: css import + provider wrap) · `frontend/package.json` + lock (the lucide-react line only) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`: "no file under `backend/`", grep-gated by `git status --short` showing no `backend/` path) and `App.tsx` (toggle mounts in SG-044; a needed change there now is a finding: STOP if it blocks, otherwise report and ship the rest). `api/types.ts` + `EvidenceGallery.tsx` are READ-ONLY context (the exception in this sentence).
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G1 needs only the new css file; G2 the two components + two gated hunks; G3 the new types file + read-only api types; G4 the two test files; G5 worklogs. No blanket exclusion is issued. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: the mutation run feeds deliberately wrong values in the same run and shows them failing. `PG-EV-02`: artifacts checked are the rendered DOM / committed outputs, never exits. `PG-EV-05`: properties ("`.dark` resolves `--card` to `#1C1A18`", "toggle flips the class and persists", "mapper carries `display_name`→`name` and no `rawResponse` key").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 300s single npm install · 600s suite+lint+build · **1500s early-close** (stop starting new work, commit what is finished, write the report, publish the receipt) · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): tokens + provider + toggle + view types; nothing else.
- No fixed dates anywhere except this header's authoring-date metadata; every time-dependent check reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads — in particular zero-css glob, `main.tsx:1-19`, `index.html:1-12`, `package.json:12-31`, `api/types.ts` field lines used by the mappers.
- **FAIL-then-PASS honestly (`PG-EV-09`):** pre-change hollow run quoted + labeled hollow (class 8, not evidence); post-change green; mutation run (2–3 caught + reverted) raw; all three committed in the verify log.
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; no frozen-prompt diff; only the lucide-react dep added; the two gated hunks byte-quoted; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- Report states the unmounted-toggle decision and the `originalUrl` source line read from `EvidenceGallery.tsx`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: no DB writes, live spend `$0`, network = the single lucide-react install only.
- **Receipt note on the notes ref (proven shape, unchanged obligation):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-043 | Report: docs/worklogs/SG-043_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- **Receipt-paste gate (standing, from SG-042): a receipt subsection with no pasted `show` output means the step was not executed — say so loudly instead of writing the subsection as done.**
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 300s single npm install · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered (+1 pinned OSS dep); actual-versus-budget per leg with units.
