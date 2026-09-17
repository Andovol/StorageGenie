# SG-060 — closer: cap-enforcement split documented + ItemInspector fallback (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** L3 stage D80 slice 4 of 4 (closes the stage). Two leftovers: (1) F-SG056-1 refined — the adapter-level cap guard (`opencode_go.py:242-253` + `:295-305`) is NOT dead: it fires for DIRECT invocations (proven by `test_opencode_go.py:128-130`, `test_chat.py:276`), but never for router-routed calls because `router.execute` (`router.py:52-72`) consumes `estimated_cost` for its own pre-call refusal and forwards only `*args, **kwargs` (adapter always sees `0.0`). Routed enforcement is owned by the router (`cost_budget`) + the reader's ledger-durable monthly check (`reader.py:359-387`) + chat/planning's own router configs. DECIDED by the Architect (not delegated): KEEP the split, DOCUMENT it — forwarding the estimate through the router would touch every provider call path for zero new enforcement (double-refusal), and removing the adapter guard breaks direct-call tests. (2) F-SG059-1 one-liner — `ItemInspectorDrawer.tsx:129` host-stale fallback → `:8003` (same proof as SG-059's seven). Vite proxy (`vite.config.ts:9`) DECIDED: leave UNCHANGED (inert — dev client uses absolute `VITE_API_BASE`; retargeting to `backend:8000` assumes dev-topology facts this slice does not establish — M17 family). **Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-059 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration; no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); no behaviour change to enforcement logic (docstrings + one fallback string + tests only — any logic hunk to router/adapter/reader budget checks is a STOP-first finding, not a silent add); NETWORK: loopback + container-runtime only, nothing else.
**Money posture (F2):** spend UNCAPPED-but-ledgered with re-evaluation owed; this slice makes zero provider calls so the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-SC-09` name-the-world · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-DP-02` no-sweep-waiver.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** All tests use scratch temp SQLite; no live import runs; the production SQLite is touched by nothing.

## Why this exists

F-SG056-1 left the enforcement story half-told ("dead path" — imprecise: it is shadowing, not death), and the next reader of `router.execute` will re-derive the confusion. The ItemInspector fallback is the eighth stale string SG-059 could not touch. Both are two-line-class changes with a test pin; together they close the L3 batch with no open threads except owner-owned futures.

## G1 — ItemInspector fallback (one string)

- `ItemInspectorDrawer.tsx:129` `VITE_API_BASE || "http://localhost:8000"` → `"http://localhost:8003"`, same one-string shape as SG-059's seven. Verify the line pre-hunk; report if it differs (finding, not obstacle).
- `vite.config.ts:9`: NO HUNK (decided above — verify the line, state the inertness reason in your own words from a live read, never from this packet).

## G2 — enforcement split documented + pinned (docstrings + one test)

- `router.py:52` docstring: state that `estimated_cost` is consumed HERE for the pre-call refusal and is NOT forwarded (providers always see the default) — with the reason (single enforcement point per routed call).
- `opencode_go.py` adapter guard (`:242-253` + `:295-305`): docstring stating it enforces for DIRECT invocations only (tests, eval harnesses) and is shadowed-but-harmless on the routed path, which the router + reader own. No logic change.
- Pinning test (new or extended — say which and why): a recording double through `router.execute` with a nonzero estimate asserts (a) refusal happens at the router with ZERO provider invocations when over budget, and (b) on success the provider receives the estimate default (documents the shadowing in executable form). No network, no key, no adapter construction with credentials — a local double only.
- No FAIL-then-PASS leg exists (nothing fails today) — state that honestly instead of manufacturing one; the guards are suite green + the pin test green.

## G3 — suite + lint + build + hygiene (NO deploy)

- Backend suite + frontend suite + `ruff`/`eslint` + `tsc && vite build` green; only base-proven pre-existing reds permitted (cite base commit + base-run command and output, or they are new findings with destinations). Gates name files checked with counts+elapsed; silent gates FAIL.
- NO DEPLOY, stated with reason: zero behaviour change (two docstrings, one dev-fallback string dead-code-eliminated from prod bytes per SG-059 F-SG059-2, tests) — `PG-PR-04` binds packets demanding live proof of NEW CODE, and there is none; the next scheduled rebuild carries the string automatically. Full sweep WAIVED per `PG-DP-02` (substitute = suite/lint/build + pin test, named here).
- Prod DB untouched (state the construction); no migration; dep list unchanged; secret scan n/a (no secrets touched — state it); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- `PG-SC-09`: name the world where documenting-not-forwarding is wrong (a future direct caller assumes router-level protection it does not get) and why the slice still ships (the docstrings state exactly which layer protects which path; the pin test locks it).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-060.log`, `{{WORKLOG_DIR}}/SG-060_report.md`, `{{WORKLOG_DIR}}/SG-060_verify.log` (pin test + suite raw). First token `SG-060`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/shell/ItemInspectorDrawer.tsx` (one-string hunk) · `backend/app/services/providers/router.py` + `backend/app/services/providers/opencode_go.py` (docstring hunks only — any logic hunk is a STOP) · backend tests (ONE new or extended pin test — say which) · `docs/worklogs` (3 files). **Anything else is a STOP** — including `vite.config.ts`, `AGENTS.md`, `docker-compose.yml`, `.env`, enforcement logic, and any new dependency.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks share no condition with any remediation step — stops win (`PG-IC-03`). Reads MAY pull/run the already-built local images only.
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1200s early-close** · **1800s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): two docstrings, one string, one pin test; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular the ItemInspector line, `router.py:52-72`, the adapter guard blocks, `test_opencode_go.py:128-130`, `vite.config.ts:9`.
- ItemInspector fallback fixed (quoted); vite proxy verified unchanged with the inertness reason in the Coder's own words; docstring hunks quoted; pin test green (quoted) with its placement reason.
- Suite + lint + build green (only base-proven reds); no-deploy reason stated (zero behaviour change); served bundle NOT rebuilt by this slice (state it — no deploy ran); prod DB untouched; no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-060 | Report: docs/worklogs/SG-060_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
