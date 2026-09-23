# SG-099 — Enrich synthesis prompt + non-catalogue caller, one capped call (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D139-approved L3 Arc A slice 1 of 4 (synthesis → persistence → live re-confirms + reviewer alternatives); D138-approved scope (owner quote "D138 - approved."), spec-doc step skipped on owner word. SG-082 left synthesis NON-RUN with the named seam: the metered TEXT path is `OpenCodeGoProvider.extract_text` (`backend/app/services/providers/opencode_go.py:326`, signature `extract_text(text, prompt, *, estimated_cost=0.0)`), but `chat/service.py:respond` (`:286`) is catalogue-bound (`build_catalog` at `:310`, `chat-v1.md` prompt at `:325`) with the consent gate `reader.ai_status()` (`:297`, defined `reader.py:100`) — all re-verified by the Architect 2026-09-23, re-verify. THIS slice adds the missing wiring as an unwired library (SG-081 precedent): one new frozen synthesis prompt + one new non-catalogue caller over OFF JSON + Jina content. Consumption (endpoint/persistence) rides later slices. **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-23); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** synthesis ONLY. No persistence model/migration (prove by diff: `models/` + `alembic/` untouched — output is RETURNED, never stored; `PG-SC-02` unrecorded this slice, said in as many words), no endpoint/UX wiring (`api/v1/enrich.py` + `main.py` read-only pattern sources), no deploy, no restart, no container action. Exactly ONE metered TEXT call ≤$0.05 worst-case (expected <$0.01); no other network — OFF/Jina inputs come from COMMITTED fixtures only, never live fetch. Key NAMES only, never bytes; `docker compose config` FORBIDDEN (`PG-SC-05` — it prints secrets).
**Money posture:** REAL metered spend, ONE call, ≤$0.05 worst-case binds (`PG-IC-04`), actual-vs-budget with units (`PG-PR-06`).
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-04` · `PG-EV-05` · `PG-EV-06` · `PG-EV-07` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-10` · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` · `PG-IC-04` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 60s per live call, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none** (no migration — prove by empty diff over `models/`+`alembic/`; the ONE live call runs with a temp `DATABASE_URL` per the SG-080 precedent, so production rows are untouched by construction and live counts read back identical before/after via a read-only query, `PG-EV-06`). **Restart: none. Deploy: none. Container actions: none** — new code goes live on a later owner-gated rider; proof is tests + the one metered call (`PG-PR-04`).

## G0 — consent/key-name gate (read-only, NAMES only)

- Before any metered touch, establish `ai_status()` enabled + the provider key NAME present (never its value). If the gate is closed (`consent_disabled` or key-name absent), the live leg is reported UNEXECUTED with the named reason and everything else still ships (SG-082 allowed-alternative precedent — stopping here is a SUCCESS for the shipped remainder, `PG-SC-03`). Where a STOP and a retry itch meet, the STOP wins (`PG-IC-03`) — the one L3 retry covers transients only (upstream invalid-JSON with zero commits + clean tree, SG-084/090/091 precedent), never a routed STOP.

## G1 — frozen synthesis prompt (new file, v1–v4 bytes untouched)

- New `backend/app/services/providers/prompts/enrich-synthesis-v1.md` with `template_version` front matter (frozen-file discipline): normalise OFF JSON + Jina content into attributed proposals — every carried fact cites source URL + retrieval date; NOTHING inferred (brand-absent input synthesizes with brand absent, never guessed — F-SG098-3 lineage, `PG-SC-07`); conflicts resolve label-wins-visible (SG-082 rule, restated not re-decided).
- Prove `extract-food/medicine/cosmetics-v1..v4.md` byte-identical before/after (empty diff quoted).

## G2 — non-catalogue caller (new module, unwired library)

- New `backend/app/services/enrich/synthesize.py`: takes OFF JSON + Jina content TEXT plus the frozen prompt, calls `extract_text` DIRECTLY (never through catalogue-bound `respond`), enforces consent refusal (0 invocations when disabled) + per-call cap refusal (`estimated_cost` over cap raises before the call, seen-to-fail both), writes the provider's `ProviderCall` ledger row on the SAME temp DB the live call runs against, returns the attributed synthesis (no persistence write — consumption is the next slice, said explicitly per `PG-SC-02`).
- No existing-file edits expected; a touch elsewhere ships ONLY on failing-test proof, minimal + root-cause + disclosed (suite-green binds on collision, M45) — anything else is a STOP.

## G3 — tests + gates + the one live call

- New `backend/tests/test_sg099_synthesis.py` (fail-then-pass, BOTH raw runs committed to the verify log, `PG-EV-09`; new checks fed deliberately wrong inputs and shown failing in the same run, `PG-EV-01`): consent-off → 0 invocations; over-cap estimate → refusal before any call; request-shape assert on EXACTLY what crosses into `extract_text` (payload carries fixture-derived OFF+Jina text + attribution slots — `PG-EV-04`, `PG-SC-12` boundary side); output attribution present per fact; brand-absent fixture output carries no brand (`PG-SC-07`); frozen prompt loads by version.
- Inputs are the COMMITTED SG-081/082 fixtures (`test_sg081_enrich_fetch.py`, `test_sg082_enrich_jina.py` shapes) — never hand-authored blobs (`PG-EV-07`). Every assertion drives the REAL caller/seam/prompt — no re-implemented stand-in (`PG-SC-12`); the one live leg runs the REAL `extract_text` path, not the fake.
- The ONE live call (60s bound): fixture OFF JSON + fixture Jina content through the new caller on a temp DB; quote cost/usage/model/latency + actual-vs-budget. Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-099.log`, `SG-099_report.md`, `SG-099_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + the live-call capture). First token `SG-099`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** actuals); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** new prompt file + new `enrich/synthesize.py` + new test file + `docs/worklogs` (3 files) — NOTHING else (existing-file touch only on M45 terms above). Ordered paths committable per `.gitignore` (verified 2026-09-23: no rule ignores them, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands persistence, endpoint wiring, deploy, restart, container acts, or a second metered call — no cell collides; stated so the check exists on paper. Reads include TestClient + host commands only; pulling/running images or launching unnamed runtimes counts as execution — not authorised.
- Privacy: fixture TEXT only; key never in any file, log, or assertion (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Frozen prompt exists with version; v1–v4 byte-identical; caller invokes `extract_text` directly with consent + cap refusals seen-to-fail; output attributed per fact, brand never guessed when absent.
- Request-shape test pins the exact cross-boundary payload; tests fail-pre/pass-post both committed raw; gates green.
- ONE live call within $0.05 on temp DB with quoted actuals; production counts identical before/after; $0 otherwise; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — is the synthesis contract frozen and honest? G2 — does the caller reach the metered path without the catalogue? G3 — does it work for real, once, within budget?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** actuals. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-099 | Report: docs/worklogs/SG-099_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 60s per live call · 1500s early-close · 2100s overall; REAL metered ONE call ≤$0.05 worst-case (expected <$0.01); actual-versus-budget per leg with units.
