# SG-065 — plugin-contract taxonomy: Household chemicals pilot + served taxonomy + exit-proof (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 7 (stage approved D83; pilot domain **Household chemicals** named by owner D86). Purpose: the second Phase-4 exit half — **"a new plugin domain can be defined without modifying core tables"** — plus killing the hardcoded frontend category lists. Recorded facts, verify each in-slice with QUOTED reads (addresses, not content facts):
- `inception/…blueprint.md:359-370` (§8 Plugin Contract): a plugin defines a category taxonomy, a behaviour profile per category (notification defaults / opened-date applies? / disposal guidance? / which chat agent), an extension attribute schema, prompt fragments, optional agents, UI form metadata. **Plugins cannot redefine core fields or bypass assertion/review-state validation.**
- `:376-392` (§9.1/§9.2): plugin taxonomy table — Household chemicals = **"Basic expiry only — minimal special logic"** (priorities listed); Documents = long-lead reminder windows, generic chat fallback; date-type enum (expiry/best-before/use-by/manufacture+offset/PAO/batch-lot); unit enum (piece, ml/L, g/kg, dose/tablet, application).
- `backend/app/plugins/registry.py` (48 lines): `register_plugin(plugin_id, version, implementation)` + `get_plugin`; built-ins registered at import (`expiry_tracker` registered with its `PLUGIN_ID`/`PLUGIN_VERSION` module constants).
- The expiry plugin implementation is `backend/app/plugins/expiry_tracker.py` (~19 KB) — the shape to imitate for descriptor structure, but Household chemicals is DATA-ONLY this slice (no new agents, no opened-date mechanic — blueprint:383 names it minimal; chat for Household/Documents is a generic FALLBACK, not a new agent).
- Frontend category lists are hardcoded TODAY: `frontend/src/types/product.ts:7-14` `CANONICAL_CATEGORIES` (DQ1 generic labels) + `CatalogToolbar.tsx:21` pills derive from it while SG-064 made pills DATA-driven from facet keys — the static list now mislabels the real `asset_type` population (SG-064 finding F-SG064-2 noted it). Where else category lists appear (import modal, capture form, chat/ planning category gates — the supported-category set the chat enforces, exact file to be found by the Coder per the M12 standing rule) — ENUMERATE with a grep and hand the result into this patch; "a list is a fact too": state the criterion, enumerate the set on the target.
- Chat supported-category set: the recorded stage limit "chat is Food + Medicine only" lives in shipped code the Coder must find (not restate); Household chemicals introduces NO chat agent (fallback only, per blueprint).
**Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration; no new dependencies; no prompt/template-content changes (labels/descriptors are UI text, not the frozen v1/v2 extraction prompts); no provider calls ($0 — a metered call is a STOP-and-report); no new agents; NETWORK: loopback + container-runtime only. THINK-TAG standing line: any in-scope file expected to carry an angle-bracket token is re-probed by char codes after editing; tests build such strings from `chr()` codes.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-02` (taxonomy read-back: the UI dropdowns must serve from the NEW source) · `PG-SC-05` (exclude by rule for any category-string cleanup) · `PG-SC-07` (a plugin providing an empty category map renders gracefully) · `PG-SC-09` · `PG-SC-12` (the exit-proof runs the REAL registration path, not a self-supplied fake) · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-DP-02`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 1200s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** Scratch temp SQLite only. **Restart: none.** **Deploy: none** (user-visible change rides the next owner-gated deploy slice, as SG-064/068).

## Why this exists

The plugin contract (blueprint §8) promises that a vertical domain extends the core WITHOUT modifying it — the Phase-4 exit condition is half where. Today that generality is unproven: exactly one plugin exists (expiry), the frontend's category lists are hardcoded DQ1 labels, and Household chemicals — the blueprint's "minimal special logic" category — has no taxonomy/behavior entry to prove the shape. One slice formalizes the descriptor contract, pilots Household chemicals as pure data, serves the taxonomy, and pins the exit property with a real registration proof.

## G1 — plugin taxonomy descriptor (contract made real)

- Extend the plugin surface with an explicit, immutable taxonomy descriptor: categories (id/name), per-category behaviour profile (`notification: "tiered-30-7-1" | "tiered-short" | "basic-expiry" | "long-lead-60-30" | "none"`, `opened_date_tracking: bool`, `chat: "category" | "fallback" | "none"`), the plugin's date-type enum, and its default units — Household chemicals per the blueprint table (basic expiry, NO opened-date, NO chat agent); Documents entry present with its long-lead profile and a `"chat": "generic-fallback"` marker (data now, agents later — this packet adds NO agent code). Food/Medicine/Cosmetics entries reflect what the SHIPPED profiles already enforce (enumerate the live set; do not invent — where an existing profile contradicts the blueprint, that is a FINDING).
- Registered on `registry.py`'s existing mechanism (`register_plugin` import-time, same shape as expiry) — `get_plugin` access stays the ONLY route (never a parallel bypass).
- Shape decision (yours to make, report it): descriptor fields live as module constants/dataclasses in a new or existing plugin module — the constraint is IMMUTABILITY (frozen), single source, and no core-table or core-schema change (no migration at all).

## G2 — taxonomy served + consumed (read-back complete)

- `GET /v1/taxonomy` → the registered plugins' descriptors (shape you design; stable keys, deterministic order). Serves at least: category list with per-category `opened_date_tracking` and `chat` mode.
- Frontend: category dropdown sources replace the hardcoded `CANONICAL_CATEGORIES` at the surfaces the derived set names (CatalogToolbar's DQ1 pills, import/capture forms). **Careful (`PG-SC-02`/`PG-SC-05`):** `toProductCategory`'s passthrough must keep working for facet keys; the DQ1 labels retire only from the LIVE PATHS the new source replaces (screenshots/mock-dependent tests get updated with reasons — `M9` walk: every UI requirement names its test registries). Keep `product.ts` edits minimal: consumed constants may stay where they are legitimately used (grid mock shapes are expectations, per SG-064 precedent).
- Empty/absent descriptor (`PG-SC-07`): a plugin with no categories renders nothing hard-crashing — graceful fallback to the existing UI behaviour (state the fallback shape).

## G3 — the exit property, PROVEN (this slice's load-bearing leg)

- A pinning test that defines a REGISTERED new domain (e.g. `documents` — data-only descriptor, in TEST space: registered in the test, not shipped as a product plugin) and proves: (a) it answers through `get_plugin` + the taxonomy endpoint path machinery with zero migration and zero new core-table writes; (b) an inspector assertion that the table registry (`EXPECTED_TABLES` live shape, SG-068) is unchanged across a registration exercise — the "no core-table modifications" half made executable.
- Pin RED on a deliberately broken variant: register a plugin whose descriptor TRIES to redefine a core field (same name as a core asset field) — the contract must REJECT or clearly isolate it (name the enforcement mechanism you implement/wire: descriptor schema validation on registration). FAIL-then-PASS raw both runs into the verify log (`PG-EV-09`).

## G4 — suite + lint + build (NO deploy)

- Derived test set (0.28.2: a hit is a FILE): grep the tree for the touched symbols/strings; run every node in hit files. Report derived-vs-intuition.
- Backend suite + `ruff` + mypy delta-0 + frontend suite + `tsc && vite build` + eslint green; only base-proven reds (2 decoder env reds).
- **NO DEPLOY, stated (`PG-PR-04`):** same shape as SG-064/068 — the next owner-gated deploy slice carries it; nothing production-effect is claimed beyond gates. Full sweep WAIVED; substitutes named: suites + lint + build + the new endpoint/registration tests on the real HTTP path.
- Secret scan zero; no ignored file staged; nothing pushed to `storagegenie-evidence`; prod DB untouched; no migration; dep list unchanged; no vacuous pass.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-065.log`, `SG-065_report.md`, `SG-065_verify.log` (descriptor table + FAIL-then-PASS raws). First token `SG-065`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/plugins/` (new `descriptor`/contract module + Household chemicals/Documents data + registry wiring; `expiry_tracker.py` descriptors only if the shared-shape refactor genuinely earns it — DIVERGENCE IS A STOP, `AUDIT.md` §5 behaviour-preservation rail) · `backend/app/api/v1/assets.py` or a NEW router file (router-mount decision as in SG-068; `main.py` mount is off-ceiling — say which file the mount requires; if `main.py` IS required, your STOP-first finding names the one needed line and the slice ships without the endpoint wired only if the taxonomy endpoint cannot exist without it) · backend tests (`test_postgres_dialect.py` registry only if it names descriptors — verify, else skip; new `test_plugin_taxonomy.py`) · `frontend/src/types/product.ts` (category-source swap) + the UI files + test files the derived set names (each edit with reason) · `docs/worklogs` (3 files). **Anything else is a STOP** — `router.py`, provider code, ledger, `.env`, compose, `AGENTS.md`, migrations, the frozen prompt files.
- Cross-product (`PG-IC-01`): no criterion introduces a migration or a table; the exit-proof test uses the REAL registry (no fake registry that re-implements the logic). The core-field-redefinition probe must live in the descriptor contract, NOT touched schema.
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall — actual-vs-budget per leg with units.
- Simplicity (`G-A7`): one descriptor contract + two data entries + one endpoint + dropdown source swap + the two proof tests; no plugin loader framework, no dynamic plugin discovery, no new JSON-Schema dependency (schema validation stays stdlib/pydantic — say which).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Out of scope: Documents chat agent (generic fallback already in shipped chat), analytics agent (SG-066), prompt tuning, storage-location taxonomy wiring beyond listing it in the descriptor (listing only — no storage-location UI this slice).

## Acceptance criteria

- Starting tree quoted (clean expected); premises re-verified with quoted reads (registry shape, expiry plugin constants, the live chat-supported-category set, the category list consumers).
- Taxonomy descriptor immutable + registered; `GET /v1/taxonomy` answers with the descriptor (quoted test, real HTTP path); UI dropdowns consume it (at least one derived-set test proves the old hardcoded list is GONE from the live path).
- Exit proof: new-domain registration exercises the real registry + taxonomy path with zero new tables (inspector-diff quoted); core-field redefinition attempt is REJECTED (FAIL-then-PASS raw ×2 runs committed).
- Household chemicals pilot entry complete per blueprint (basic expiry, no opened-date, no chat agent) — its behaviour profile is DATA, labeled and quoted.
- Suite + lint + build green (only base-proven reds); no-deploy reason stated; prod DB untouched; no migration; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-065 | Report: docs/worklogs/SG-065_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
