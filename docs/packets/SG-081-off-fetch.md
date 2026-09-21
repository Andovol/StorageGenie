# SG-081 — Enrich OFF fetch service: v2 search + deterministic scoring + snapshots (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D108-approved Enrich slice 1 (research `docs/research/2026-09-21-enrich-source-research.md` — the D102 gate; spec §7; plan `docs/superpowers/plans/2026-09-21-ai-ingestion-enrichment.md` Enrich tasks). Scope is OFF ONLY: v2 search + deterministic scoring + snapshots. Jina is SG-082 (do not read the Jina key, do not call it); Vision Web Detection is DEFERRED and never touched (D108 — second cloud provider declined for this deployment by D83). No review mapping, no pipeline wiring, no LLM synthesis in this slice (SG-082 owns them). **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** OFF fetch library ONLY (enumerated ceiling below). No Jina, no Vision, no key reads, no pipeline/API wiring, no migration, no secrets in logs, no deploy, no restart (`PG-PR-04` — nothing becomes live). OFF is free and unauthenticated: $0.00.
**Money posture:** $0.00 actual — OFF carries no spend; the bounded live smoke (G4) is free GETs only. No bound to multiply out (`PG-IC-04` stated as not firing: nothing metered exists).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-04` · `PG-EV-05` · `PG-EV-07` · `PG-EV-09` · `PG-SC-02` (no new recorded field — stated) · `PG-SC-05` · `PG-SC-09` · `PG-SC-11` (grep + verdict, see G3) · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NOTHING live stated).

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary (10s per OFF call per research, stated), 600s suite, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (no datastore writes; snapshots are committed fixture files + worklogs). Restart: none. Deploy: none.**

## G1 — OFF v2 client (sync, free, snapshot everything)

- Endpoint `GET https://world.openfoodfacts.org/api/v2/search` with EXACTLY the research params: `search_terms` (name), `brands_tags` (brand), `countries_tags_en=romania`, `page=1`, `page_size=10`, `fields=code,product_name,brands,ingredients_text,nutriments,packaging,countries_tags_en` (research §1). Re-read the research file on target before coding (`PG-IC-09`) — my quotes above are hypotheses.
- SYNC client (this tree is sync — `schemas.py` sync precedent; no async, no new event loop). Reuse the tree's HTTP client if one exists (`httpx` is used by the provider adapter — verify on target; a new dependency is a STOP). 10s per-call timeout (research value).
- `User-Agent` identifies StorageGenie (contact form per OFF etiquette) — decided and reported, never the research sketch's placeholder.
- Every response snapshot: raw JSON + request URL + retrieval timestamp persisted (committed fixtures for tests, worklog raws for runs). Snapshots carry source attribution (URL + timestamp) on every record.
- Degradation WITHOUT raising (`PG-SC-07` all-candidates-eliminated shape): OFF 5xx/timeout/malformed → return an explicit no-result with the reason quoted (loud-`unanswered`), never an exception into a caller, never a silent empty. State which form the no-result takes.
- Privacy: queries carry brand+name TEXT ONLY — assert in-test that no image bytes, GPS, or key material can reach the OFF call (no photo leaves the machine on this path, stated + tested).

## G2 — deterministic scoring (0.4/0.4/0.2, ≥0.6, margin ≥0.15)

- Formula from research §2 (D108 rule): `score = 0.4*brand + 0.4*name + 0.2*(country + category)` with brand exact/contains, name token-overlap, Romania country bonus. Accept top iff score `≥0.6` AND margin to second `≥0.15`; else explicit no-confident-match (never a nearest-guess accept).
- Pure function, offline-testable, no I/O: committed OFF fixture payloads (real shapes, 2–3 fixtures incl. a multi-hit ambiguous case + a below-threshold case) scored exactly; boundary pins at 0.6/0.15 (accept just above, reject just below — seen-to-fail, `PG-EV-01`).
- `PG-EV-04`: a request-SHAPE test asserts the exact URL + params that WOULD be sent (no network) — the slice's verification must not stop at the mock; also assert on the query text passed to the HTTP driver (`PG-SC-12`).

## G3 — tests + gates (no new recorded field, stated)

- New module `backend/app/services/enrich/` (client + scoring; exact split decided and reported) + ONE new test file. `PG-SC-02` fires as stated-absent: this slice creates NO datastore field and wires NO reader — the fetch is a library SG-082 will call; say so in as many words, never silently.
- FAIL-then-PASS raw, both runs committed to `SG-081_verify.log` (`PG-EV-09`): scripted-transport tests fail pre-change (no module), pass post; scoring pins fail-then-pass on the formula.
- `PG-SC-11`: grep the test tree for end-relative assertions over enrich/OFF paths; list hits with verdicts (expectation: none — state the empty result raw).
- Full backend suite green modulo the 2 known decoder env reds (base-proved premise — re-verify on bare BASE with stash, do not inherit); `ruff` clean; `mypy` delta 0 quoted; secret grep-gate over the diff (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken` identifiers, SG-037 shape) with 0 real secret shapes — plus assert the Jina key is NEVER read on this path (grep the new module for `JINA`, expect 0 hits, quoted).
- Exclusions by RULE with literal grep-gates (`PG-SC-05`): no Jina/Vision identifiers in the new code (`jina|vision|WEB_DETECTION` → 0 hits quoted); no pipeline/API wiring (`run_ai_extraction|router|register` untouched — state the check); no prompt diff; no migration.

## G4 — exactly one bounded live smoke (only free GETs, failure is a finding)

- ≤3 REAL searches against `world.openfoodfacts.org` (read-only GET, $0, no key): one expected-hit food query, one ambiguous query, one expected-miss. Quote request URLs + outcome class per query (hit/scored, ambiguous/no-confident-match, miss/empty) + the snapshot recorded.
- A provider-side failure (5xx/timeout/degraded v2) is a FINDING with the raw error quoted, not a slice failure — provided G1–G3 are green. If the smoke cannot run (no egress), it reports `unanswered` with the exact red leg quoted (never routed around).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-081.log`, `SG-081_report.md`, `SG-081_verify.log` (raw outputs + BOTH fail-then-pass runs + every snapshot). First token `SG-081`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **$0.000000 actual**; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** NEW `backend/app/services/enrich/*` (decided split, quoted) · ONE new test file + committed OFF fixture JSONs · `docs/worklogs` (3 files). **Anything else is a STOP** — Jina/Vision, key reads, pipeline/API wiring, prompts, migrations/models, compose/`.env`, README, STATE/AGENTS/packet dirs.
- Cross-product (`PG-IC-01`): no criterion calls Jina/Vision, reads any key, wires any caller, or touches the network beyond OFF GETs + pushes; reads include the suite only — no container image pull/run; G5's smoke is covered by the free-GET-only rule.
- A count or absence premise carries the RAW command output, never a paraphrase.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition — reachability form only.
- Simplicity (`G-A7`): client + scoring + snapshots; no caching layer, no retry policy beyond the loud no-result, no review mapping, no synthesis.

## Acceptance criteria

- OFF client sync, exact research params (shape test quoted), real UA (placeholder-free), 10s timeouts; every response snapshotted with URL + timestamp; degradation returns loud no-result (quoted).
- Scoring formula exact with boundary pins both sides; ≥0.6 + margin ≥0.15 accept rule; no nearest-guess accept (quoted).
- New tests FAIL-then-PASS raw both committed; Jina/Vision/pipeline grep-gates empty (quoted); JINA unread (0 hits); suite/ruff/mypy/secrets per G3; $0.000000; no vacuous pass.
- Live smoke ≤3 free GETs with per-query outcomes quoted, or `unanswered` with the red leg; external failure is a finding, not a slice failure.
- Question each criterion answers (`PG-SC-09`): G1 — does the client speak exact OFF with snapshots and graceful degradation? G2 — does the scoring accept only confident matches? G3 — is the library proven without touching anything else? G4 — does the real API answer? G5 — is the evidence committed, not merely reported?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **$0.000000 actual** (OFF free; containment per `PG-PR-04` stated: nothing live exists to contain).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-081 | Report: docs/worklogs/SG-081_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary (10s per OFF call) · 600s suite · 1800s overall; **$0.00** — OFF is free and unauthenticated.
