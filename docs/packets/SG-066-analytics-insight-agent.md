# SG-066 — Analytics Insight Agent: household stats + one metered NL summary (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 9 (stage approved D83; scope split approved D90 — analytics agent ALONE first; remaining-categories chat + F-SG065-2 activation ride later slices). Blueprint §9.4: the Analytics Insight Agent generates natural-language summaries over the household's own structured data (waste trends, category breakdowns, adherence patterns); no external web access; fully grounded in first-party data. Blueprint §11.2 item 10: an Analytics screen. NOTHING exists today (SG-039 ledger: "no analytics"). The established agent shape to mirror is the SG-037 planning service (verified in-tree 2026-09-21): manual trigger endpoint, consent gate BEFORE any call or row (`reader.ai_status`), the reader seam's ONE operation `extract_items(image_bytes, prompt)` reused with a frozen versioned prompt file under `backend/app/services/providers/prompts/`, rows written are suggestion + `guardrail_event` + `provider_call` only, nothing executes. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); host link from SG-070's receipt echo (`0.28.2` from `/home/andrei/storagegenie-contract/VERSION` — SG-062 precedent); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** NETWORK: loopback + container runtime + the configured provider (metered legs only, bounded below) — no other external call. Secrets: never print, log, quote, or commit a key byte; `docker compose config` output is FORBIDDEN (`PG-SC-05` exclude-by-rule).
**Money posture:** at most TWO metered provider calls, worst-case bound **$0.010** (derived: SG-049 run-2 measured ~$0.0036–0.005 per call over 7 attempts; 2 calls × $0.005 worst case). Actual-vs-budget per call with units; 80% ($0.008) is the warning line (uncalibrated per `G-A9`).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-03` · `PG-EV-05` · `PG-EV-06` (authority: ONE analytics summary run — see G2) · `PG-EV-09` · `PG-SC-02` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NO DEPLOY stated) · `PG-PR-06` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite/build, 300s single live-call, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: temp SQLite for all new tests; exactly ONE metered summary run against the live backend (G2 authority below).** No migration ships (stateless: no new table). **Restart: none. Deploy: none** (`PG-PR-04` stated — the live proof rides a later owner-gated rider; nothing production-effect is claimed beyond the gates + the one authorized run).

## G0 — consent + seam gate (STOP-as-SUCCESS, zero spend if absent)

- `GET /v1/settings/ai` quoted (expect a consent-true shape; anything else = STOP-as-SUCCESS: ship the offline proofs + unrun live legs, $0). Provider key existence probe from inside the backend container, booleans + length only. `ai_status()`-equivalent quoted. Stopping here is a SUCCESS — say so.
- Enumerate the reader seam surface you will reuse (`extract_items` signature, router config, prompt dir) with quoted reads — do not assume the SG-056 shape survived.

## G1 — deterministic household stats endpoint (no provider, $0)

- New `GET /v1/analytics/summary?household_id=` returning computed-from-tables stats ONLY: per-category asset counts (from the served taxonomy's category ids — read `/v1/taxonomy`, never a hardcoded list), expiry urgency buckets (expired / 7-day / 30-day / safe — mirror the expiry dashboard semantics in-tree), waste signals (expired-untouched counts), adherence signals (planning suggestion confirm/dismiss counts, review decision counts). Every number traces to a named table+query (`PG-SC-02`); an empty household returns zero-maps (200, no error — `PG-SC-07`: state what empty means).
- Household isolation enforced (cross-household = 403/404 per the established pattern); unknown household = 404.
- FAIL-then-PASS: the new tests run against pre-change code first (routes 404 — quoted raw, committed) then pass (`PG-EV-01`/`PG-EV-09`).

## G2 — one metered NL summary over the stats (the authorized production run)

- `POST /v1/analytics/insights?household_id=` — manual trigger ONLY (no schedule, no auto-run). Consent-gated BEFORE any call or row (G0 shape). Reuses the reader seam's one operation with a FROZEN versioned prompt file (new file under the prompts dir, front-matter `template_version`, read-only at runtime — planning-prompt discipline). The stats from G1 are supplied in the prompt; the model returns prose + cited stat ids; every cited id resolves to a G1 stat or the call is a loud failure (grounding check — a summary citing numbers that are not in the supplied stats is a FAIL, never trimmed silently).
- **Production-write authority (`PG-EV-06`/`PG-PR-10`, D90 scope approval): exactly ONE insights run against the live backend.** Rows it creates (`provider_call` + ledger, NO catalogue writes — no asset/assertion/evidence/audit-suggestion rows) are REPORTED with identifiers and LEFT in place. Any second run, any catalogue write, or any spend past the $0.010 bound is a STOP-and-report. Actual-vs-budget quoted per call with units.
- The metered path is ALSO proven offline (fake/scripted provider through the same service function — the mechanism), but the live run is the authority for the production claim (`PG-SC-12`: name what each check runs against).

## G3 — Analytics screen (read-only)

- One Analytics route rendering G1 stats + a manual "Generate summary" action calling G2 + the returned prose with its cited stats. No confirm/dismiss lifecycle (insights are not actions), no auto-refresh, no polling. Empty states asserted (an unasserted empty state is a vacuity risk).
- `PG-SC-02` end-to-end: stats rendered are the endpoint's values (test with a mocked endpoint asserting render-from-response, plus the real-HTTP backend tests from G1/G2).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-066.log`, `SG-066_report.md`, `SG-066_verify.log` (raw suite outputs + BOTH fail-then-pass runs + live run outputs + spend lines). First token `SG-066`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** actual vs $0.010 bound); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/analytics/` (new) · `backend/app/api/v1/analytics.py` (new) · `backend/app/main.py` (EXACTLY one mount hunk — import + include lines, quoted verbatim in the report; anything more is a STOP) · one new frozen prompt file under the prompts dir · backend tests (new `test_analytics.py`; may extend NO other test file — a red elsewhere is reported, not fixed) · frontend Analytics screen (new route file + `App.tsx` route registration only + `api/client.ts` + `api/types.ts` endpoint additions only + focused test file) · `docs/worklogs` (3 files). **Anything else is a STOP** — chat service, planning service, reader/router/provider code, prompts for other agents, `.env`, compose, migrations, saved-searches/facets/taxonomy, remaining-categories chat, F-SG065-2 activation.
- Cross-product (`PG-IC-01`): G2's live run needs the provider seam read-through only (no seam edits); G1/G3 are offline-capable; no criterion requires touching a forbidden file. Reads MAY pull/run the already-built local images only.
- Full backend suite from `backend/` (600s) + `ruff` clean + `mypy` quoted (delta-0 expected; pre-existing lines reported, not fixed) + `npm run build` green (quoted) + `npx vitest run` (600s) green. Secret scan 0 (sentinel-key absence included).
- Angle-token standing line: any in-scope file carrying `<...>` literals is re-probed by char codes after editing; tests constructing such strings build them from character codes (SG-062 lineage).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).
- Simplicity (`G-A7`): one stats function + one summary function + two routes + one screen; no scheduler, no new table, no streaming, no chat-history persistence.

## Acceptance criteria

- G0 quoted (consent-true or STOP-as-SUCCESS with $0); seam enumeration quoted.
- Stats endpoint live on the real HTTP path with household isolation + empty-household zero-maps; every stat traced to a table+query; pre-change 404 quoted, post-change 200 quoted.
- Exactly one live insights run: prose returned, every cited id resolves to a supplied stat, spend ≤ $0.010 quoted, created rows reported by id and left, zero catalogue writes (construction stated + row counts quoted).
- Screen renders endpoint stats + manual summary action; empty states asserted; suites/build/lint green (quoted); secret scan 0; no vacuous pass.
- No migration shipped; no deploy claimed; no second metered call.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** actual vs $0.010 bound.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-066 | Report: docs/worklogs/SG-066_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/build · 300s single live-call · 1800s overall; metered ≤ 2 calls, worst-case **$0.010** (derivation above); actual-versus-budget per leg with units.
