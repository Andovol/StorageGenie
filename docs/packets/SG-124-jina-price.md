# SG-124 — Jina price foundation: rate constant + estimator + tests (offline, no wiring)

**Settings travel on the trigger** (`SG-124 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved slice (third of the L3 residual-completion stage; SG-122 SEEDED 98, SG-123 BLOCKED 98 → D18 retired the freeze). D17's "ledger retention + Jina price" splits here by smaller-slices-by-default: THIS slice is the price foundation only — retention rides SG-125, wiring the cost into served paths rides later with it. Nothing in this slice touches a served path, so no rebuild and no recreate. Verified by the Architect 2026-09-25 (re-verify — every premise below is a hypothesis): `jina.py` carries NO cost/USD/usage symbol (request constants `TOKEN_BUDGET = "6000"`, `PAGE_TIMEOUT = "15"`, bases EU/global at `:52-53`); `JinaSearchSnapshot` (`:87-97`) carries no usage/cost field; `EnrichSnapshot` has no cost column; `provider_call` HAS `cost` + `usage_json`; the enrich endpoint prices nothing itself (`last_spend_usd` is caller-supplied at `enrich.py:149`); the sibling pattern is `opencode_go.py:44-45` (`INPUT_USD_PER_1M = 0.15`, `OUTPUT_USD_PER_1M = 0.60`) + `synthesize.py:118-131` (`estimate_text_cost`) + per-call caps. SG-116's open caveat ("tokens-not-USD") is what this slice closes at the foundation level. **No rate value is stated here — the vendor page is the authority, read at execution (`PG-SC-03`); inventing a rate is a STOP.** **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** offline ONLY — no Jina call, no OFF call, no live leg of any kind ($0 — scripted transports only; a metered call is a STOP-and-report). One new egress shape exists: a single keyless GET to the vendor pricing page (G0; quoted URL + figure or BLOCKED). Writes: the constant + estimator + tests + `docs/worklogs` (3 files) — and NOTHING else. No served-path hunks (endpoint, snapshot writer, snapshot model, provider_call writer — any hunk there is a STOP); no migration; no rebuild; no recreate; no key read (pricing is public; the key is never needed here).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-03` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-04` (no served-code change — proof scoped to offline runs).

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none. Container actions: none.**

## G0 — rate sourcing from the vendor page (a GOAL with stop conditions — `PG-SC-03`)

- Read the vendor's CURRENT pricing page for the Search API (one keyless GET; quote URL + the captured figure + billing unit: per-request, per-token, or credits-then-USD). State what does NOT count as grounds to stop: the page moved (one site-search retry, quoted), the rate in credits (convert with the quoted credit price, or BLOCKED if no conversion is stated), separate input/output rates (take both, mirror the sibling shape). What STOPS: page unreachable, no Jina Search rate findable, or an ambiguous unit — BLOCKED with the constant UNWRITTEN (an invented rate is worse than no constant).
- Re-verify the no-cost premise in-tree (one grep over `enrich/` for `cost|usd|USD|price` quoted) — a cost symbol already present re-scopes everything below to extending it, never duplicating it.

## G1 — constant + estimator beside the Jina client (sibling shape, no served wiring)

- Add the rate constant(s) next to the Jina request constants (`jina.py`, beside `TOKEN_BUDGET`), each with a sourced comment (vendor page URL + capture date from the live clock + quoted figure). Hardcode nothing else.
- Add `estimate_jina_search_cost(...)` mirroring `estimate_text_cost`'s contract (bounded worst-case USD for ONE search from the constant; pure function, no network, no key). Signature is yours within that contract — decide and report.
- Seen-to-fail (`PG-EV-01`): feed the estimator a deliberately wrong input (negative tokens / unknown unit) and quote the failure in the same run.

## G2 — tests fail-then-pass + suite (both runs committed — `PG-EV-09`)

- New tests: rate-constant present with the sourced figure; estimator math against hand-computed USD (quote the arithmetic); estimator refusal on the G1 adversarial input; no served-path import added by the new code (the foundation imports nothing outside `enrich/`).
- FAIL-pre → PASS-post, both raw runs committed and quoted. Full suite green-except-base-proved-reds (bound 600s); ruff clean; mypy quoted. Empty diff over every served path (endpoint, snapshot writer/model, provider_call writer, caps) quoted — a hunk there is a STOP.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-124.log`, `SG-124_report.md`, `SG-124_verify.log` (pricing page capture + both raw test runs + every empty diff). First token `SG-124`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the constant, the estimator, the new tests, `docs/worklogs` (3 files). **Any other hunk — served paths, snapshot model, migrations, caps, suite files beyond the new tests — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs one keyless page GET + one in-tree grep; G1 needs constant + pure function; G2 needs test runs + suite; nothing else. No criterion touches containers, the DB, the network beyond G0's page, keys, or the running service. Reads explicitly INCLUDE running the suite in-process; pulling any image or launching any other runtime is NOT included and is a STOP.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): source, define, estimate, test. No cap wiring, no snapshot column, no provider_call row — however small; those ride the retention/wiring slice.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): source — what does the vendor charge for one search, in what unit? define — is the rate a named constant with provenance? estimate — does the pure function convert a search to bounded USD?
- Pricing capture quoted (URL + figure + unit) or the `BLOCKED:` path taken with the constant unwritten.
- Constant + estimator present in the stated files with sourced comments; adversarial input seen-to-fail quoted.
- Tests FAIL-pre→PASS-post both committed and quoted; suite holds; served-path diffs empty as quoted.
- No live call, no key touched, no vacuous pass (an estimator asserted only by its own docstring evidences nothing — the hand-computed arithmetic is the proof).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-124 | Report: docs/worklogs/SG-124_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
