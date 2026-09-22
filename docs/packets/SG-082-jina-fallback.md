# SG-082 — Enrich Jina fallback + review mapping + one capped synthesis pass (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D127-approved L3 arc slice 1 of 4 (SG-082 → T1 → T2 → T3; riders parked for individual owner words). D108-approved Enrich slice 2 (research `docs/research/2026-09-21-enrich-source-research.md` — the D102 gate; spec `docs/superpowers/specs/2026-09-21-ai-ingestion-enrichment-design.md` §3–§6; plan `docs/superpowers/plans/2026-09-21-ai-ingestion-enrichment.md` Task 4). SG-081 shipped the OFF-only library (client + scoring + snapshots, `backend/app/services/enrich/`, rated 98) as an unwired library. THIS slice adds the Jina fallback for OFF misses/non-food, maps both sources into the existing review machinery as gated proposals, and runs exactly one capped synthesis pass. Vision Web Detection is DEFERRED and never touched (D108). No deploy, no restart — code becomes live only on a later owner-gated rider (`PG-PR-04`). **Authoring date (metadata, never a gate):** 2026-09-22. Transport: the standard job_spawn lane. Contract: recorded `0.30.0` == published (`c9c9ba3`; D125 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** OFF stays untouched and green; Jina + synthesis are the only metered touches and both are capped below. Secrets: never print, log, quote, or commit a key byte — the Jina key is USED via settings, never READ as a value; `docker compose config` output is FORBIDDEN (`PG-SC-05` exclude-by-rule — it prints secrets); key-name discovery lists NAMES only. No migration, no schema change, no container builds, no provider beyond the two named here ($ caps below).
**Money posture:** Jina ≤5 searches this slice (token-budget headers on every call) + synthesis EXACTLY ONE call ≤$0.05 worst-case (expected <$0.01; `PG-IC-04` worst case binds). Per-press cap for the button stated uncalibrated (`G-A9`). Actual-vs-budget per leg with units.
**Guards invoked (0.30.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-04` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.
**Answers to SG-081's open UNCLEAR lines (PACKET.md §5):** ceiling-vs-suite-green decided — suite-green binds on collision, repairs minimal + root-cause + disclosed (`M45`, in the ceiling below); OFF 503 fixtures re-confirm at the next OFF live opportunity, NOT this slice (this slice's live legs are Jina + synthesis); REMAINING destinations land here — Jina fallback, review wiring, category activation on Jina-supplied categories, synthesis.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 60s per live call. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (read-only `docker info`-class queries at most; any denial is reported as unanswered, never routed around).

## G0 — key-name + consent gates (STOP-as-SUCCESS on absent, SG-049/SG-055 precedent)

- Establish the env var NAME carrying the Jina key by listing NAMES ONLY from the host backend `.env` and the settings module that reads it — values never printed, logged, quoted, or committed. If no Jina key name exists, or `SG_CONSENT` is not true, STOP-as-SUCCESS: ship every offline goal below (scripted Jina transport, mapping, UI, tests) with the live legs unrun and the spend $0. Stopping here is a SUCCESS habit, not a failure — say so. What does NOT count as grounds to stop: anything else in this packet.
- Contract echo + source path; model/effort per `CO-78` from process arguments.

## G1 — Jina fallback client (scripted-first, EU base, token-budgeted)

- New module beside SG-081's client (same `backend/app/services/enrich/` package, no new package): `GET https://eu.s.jina.ai/{urlencoded_query}` (EU data residency for the Romania scope — decided, reason stated; if the EU base is unreachable and the global base answers, that is a finding, never a silent switch) with `Accept: application/json`, repeated `site` filters (`mega-image.ro`, `emag.ro`, `farmaciatei.ro`), `num≤5`, `type=web`, `gl=ro`, headers `X-Token-Budget: 6000`, `X-Timeout: 15`, `X-Respond-With: content`, `Authorization: Bearer <key-from-settings>`. Research source: `docs/research/2026-09-21-enrich-source-research.md:69-119` (hypothesis — verify each field against the live API's actual acceptance in the smoke leg).
- Same snapshot discipline as SG-081 (URL + timestamp + verbatim raw + named `no_result_reason` degradation classes, never raise). Fallback rule: Jina fires ONLY on OFF miss/degradation or non-food (OFF stays first); both sources' snapshots persist in the decision record. `PG-EV-04`: one test asserts the exact shape of what would be sent (URL, params, headers NAMES only — the Bearer VALUE never appears in any assertion, fixture, or log, `PG-EV-09`).
- Live smoke: ≤3 real Jina searches (read-only GET, key-metered, counted against the ≤5 cap). Failure is a finding with the verbatim class, never a retry beyond the bound.

## G2 — review mapping + gated proposals (existing machinery only)

- Map OFF decisions (`MatchDecision`) AND Jina results into the existing structures in `backend/app/services/candidates.py` (enumerate the mapping functions on target with the criterion stated — a list is a fact too — and report the difference either way) with `source_type=web:<source>`; conflict rule label-photo-wins label-visible, web fills gaps, both visible with sources (spec §4); per-field accept through the existing candidate UI only (`frontend/src/routes/ReviewPage.tsx`, `frontend/src/components/CandidateCard.tsx` — verify on target, do not inherit my paths blindly).
- Enrich button + spend display on the product page (`frontend/src/routes/AssetDetailPage.tsx` — verify on target) under the per-press cap (stated uncalibrated): the button shows the last measured spend and refuses above the cap with a named reason. No new review UX anywhere.
- Category activation: `category_score` (inert 0.0 on the OFF path per F-SG081-3) activates on Jina-supplied categories — decide the agreement rule and report it; the OFF path stays byte-identical.
- `PG-SC-02` stated-absent: NO new recorded field, NO model, NO migration this slice — snapshots stay in-memory/JSON-serializable; persistence rides a later slice. Say it in as many words.

## G3 — exactly one capped synthesis pass (or a reported non-run)

- Reuse the project's existing metered TEXT path for exactly one normalisation call over OFF JSON + Jina content with explicit source attribution (URL + retrieval date) — FIRST establish which seam serves text synthesis and name it; if none exists without new provider wiring, ship everything else and report synthesis unexecuted as REMAINING (no new wiring in this slice). Bound: ONE call, ≤$0.05 worst-case, actual-vs-budget with units (`PG-PR-06`). Consent + monthly-ledger refusal proven with 0 extra invocations outside this one.
- FAIL-then-PASS raw both runs committed (`PG-EV-09` destinations: the verify log carries BOTH); request-shape assertions read the real driver's received request (`PG-SC-12`); suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real; `PG-SC-11` end-relative grep over touched test files committed raw.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-082.log`, `SG-082_report.md`, `SG-082_verify.log` (raw command outputs + BOTH fail-then-pass runs + every gate + all smoke snapshots). First token `SG-082`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** actuals for Jina count + synthesis $); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling (M45 decided):** new `services/enrich` Jina file(s) + additive hunks in `backend/app/services/candidates.py` + `frontend/src/routes/AssetDetailPage.tsx` (+ its test) + ONE new test file + fixtures + `docs/worklogs` — NOTHING else. **Suite-green binds on collision:** a pre-existing red the new code legitimately trips is repaired minimally at root cause and disclosed (F-SG081-1 precedent), never worked around inside the new test. Anything else is a STOP.
- Cross-product (`PG-IC-01`): every criterion is checked against every blanket constraint above — name the forbidding constraint per criterion or write that none forbids it. Pulling/running a container image or launching an unnamed runtime counts as execution, not a read — not authorised here.
- Privacy: request carries brand+name TEXT only (same text-only tests as SG-081 extended to the Jina driver); key material never in any file, log, or assertion; Vision/Jina-key-print/`docker compose config` excluded by rule with literal grep-gates (`vision|WEB_DETECTION` → 0; key-name grep reports names only).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- G0 gates quoted (key NAME source, consent value) with the taken branch named; if STOP-as-SUCCESS, offline goals still ship green.
- Jina request shape pinned byte-for-byte with header NAMES (Bearer value nowhere); EU base verified or the deviation reported as a finding.
- OFF→Jina fallback order proven (OFF miss triggers Jina; OFF hit never does); both snapshots in the decision record.
- Mapping lands in the existing review UI as gated proposals (never auto-accepts — prove with a threshold-0.0-class assertion); label-wins conflicts demonstrated; button shows spend and enforces the per-press cap (seen-to-fail once).
- Synthesis ran exactly once within $0.05 with attribution — or is reported unexecuted with the named missing seam (no vacuous pass either way).
- Suite/ruff/mypy/secret gates as in G3; nothing written outside the ceiling; no vacuous pass; diff is the evidence.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** actuals.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-082 | Report: docs/worklogs/SG-082_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 60s per live call · 2400s overall (all uncalibrated per `G-A9`); Jina ≤5 searches + synthesis ONE call ≤$0.05 worst-case; actual-versus-budget per leg with units.
