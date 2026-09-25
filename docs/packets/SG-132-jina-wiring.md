# SG-132 — Jina wiring: ledger every search at the estimated cost, cap covers it, served

**Settings travel on the trigger** (`SG-132 coder=opencode effort=high`, D2) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D2-authorized slice (owner quote "D2 - approved", ISS-2): close the SG-124 REMAINING — the estimator is defined but unwired (by design): no Jina search writes a `provider_call` ledger row, and the enrich cap cannot see Jina spend. Facts in hand (hand-over, not pre-solve): estimator `estimate_jina_search_cost` + `JINA_SEARCH_TOKENS_PER_REQUEST = 10_000` + `JINA_TOKEN_USD_PER_1M = 0.05` live in `backend/app/services/enrich/jina.py` (SG-124, rated 98); `synthesize.py` already carries its own `INPUT_USD_PER_1M`/`OUTPUT_USD_PER_1M`/`estimate_text_cost` (F-SG124-1 — EXTEND beside the Jina client, never duplicate or touch it); exactly one spend reader `reader._recorded_spend`, month-boxed, joining `provider_call → job → household_id` (F-SG125-2 — a Jina row recorded through the production writer is counted with no reader change; VERIFY, never assume); ledger writers `_write_ledger`/`_write_error_ledger` exist on the reader + enrich paths (F-SG125-2); enrich trigger endpoint `api/v1/enrich.py` + cap-refusal precedent SG-080/SG-098. THIS slice wires the estimator into every Jina search path, proves cap coverage through the real seam, re-checks the vendor spread/floor keylessly (F-SG124-3/4), and serves it (rebuild + exactly one recreate + verify — D145: this slice changes served code, so it owns its refresh). Verdicts: WIRED (every Jina search ledgers its estimate, cap sees it, live search proves the row) / BLOCKED (a needed model change — migration takes its own word — or the vendor rate moved against the constant; commit, receipt, clean tree). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** Jina-cost wiring ONLY. Writes: the wiring hunks, tests, `docs/worklogs` (3 files) — and NOTHING else. No model change (prove by empty diff over `models/`+`alembic/` — a NEEDED model change is a STOP, not an improvisation), no synthesize.py cost-symbol change, no cap-value change, no scheduler. **Authorising grant (`PG-PR-10`):** D2, production restart via exactly one recreate (D145 standing, `G-K2` — stated here). Jina live searches ≤2 (containment with unit, `PG-PR-06`); synthesis $0; a 3rd live search or any synthesis call is a STOP.
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path) + Jina token-credit bound ≤2 live searches (~$0.0005 est each — credits, not USD). `PG-PR-06` stated upfront; `PG-PR-07` success-delta: after this slice, Jina searches consume the household's monthly cap like every other provider call — a household at cap will see enrich refuse where it previously sailed through on Jina spend. Actual-versus-budget per leg with units in the report.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-07` · `PG-EV-08` · `PG-EV-09` · `PG-SC-02` · `PG-SC-06` · `PG-SC-07` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-04` · `PG-PR-06` · `PG-PR-07` · `PG-PR-10` · `PG-DP-02`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite/build, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none written by the product change (empty diff over `models/`+`alembic/` quoted). Live-DB reads: GET-only served proofs. Press rows the live search creates are reported with identifiers and left in place (removal is the Architect's call, `PG-EV-06`). Restart: exactly ONE recreate (`PG-PR-04`: the proof below runs against the new build, in order — rebuild, recreate, then served legs). Deploy: that recreate only. Container actions: rebuild + one recreate + exec probes.**

## G0 — read paths + vendor re-check (reads only — stated, not solved)

- Read the Jina search path end-to-end (client call sites → snapshot writer → enrich endpoint → cap check → `_write_ledger`): enumerate EVERY Jina call site on the target by criterion (any code path that can emit an s.jina.ai request), expectation stated and differenced either way (a handed list is a fact too — DISPATCH.md §2a). Read-back trace (`PG-SC-02`): the exact query/screen that will show a Jina ledger row in production — writer that persists it + reader that displays it — ceiling includes every file on that route.
- Vendor re-check, keyless GETs only (F-SG124-3/4): is `$0.05/1M × 10k floor = $0.0005` still conservative against the live pack table? Quote figure + URL + capture time. A moved rate is a finding (BLOCKED only if it falsifies the constant — decide and report).
- Caps inventory (`PG-SC-06`): name EVERY cap on the enrich path (per-call, monthly, estimator floor) + their JOINT expected outcome after wiring — naming is not composing.

## G1 — wire the estimator (fail-then-pass, both runs committed — `PG-EV-09`)

- Every enumerated Jina search path records one `provider_call` row carrying the estimator's figure (default floor + caller-bound override where the caller knows better — decide placement and report). `synthesize.py` symbols byte-untouched.
- Proof: fail-pre (Jina-path run with NO ledger row — red quoted) → pass-post (same run WITH the row — green quoted), both committed. The row MUST be written by the production writer through the real seam (`PG-SC-12`, `PG-EV-07`): a test that writes the row itself proves nothing — assert on what crosses the real boundary. Empty-household world named: no search → no row, spend 0.0 (`PG-SC-07`).
- `PG-IC-08` blast radius: expected row counts + expected estimate figures written in the tests — a measured figure differing either way stops the run.

## G2 — cap coverage through the real seam (no Jina-credit burn for the refusal proof)

- Prove a Jina ledger row moves the month-boxed total: BEFORE/AFTER `_recorded_spend` around the G1 path (real reader, real rows — BEFORE derived at base, `PG-SC-12`).
- Prove the enrich cap refuses on Jina spend: seed the cap via the production writer (NOT via live searches — credits cost), then the enrich trigger refuses with the refusal quoted. No live-search loop to reach cap, ever.
- Targeted suite + full suite green-except-base-proved-reds (600s bound); ruff clean; mypy quoted. Full-directory e2e waived explicitly (`PG-DP-02` — restart-gated slice); substitute: the in-process tests above + the G3 post-restart run as authority. Empty `models/`+`alembic/` diff quoted.

## G3 — serve it: rebuild + ONE recreate + live proof (in this order)

- Rebuild (quote image id) + exactly ONE recreate (container-id change quoted — `RestartCount` never the proof, M42) + verify: health exact-shape ×6, gate 301/401, alembic head unchanged, live counts delta == press rows only.
- Exactly ONE live Jina search (≤2 bound): ledger row asserted with the `$0.0005`-family estimate + month total moved + snapshot recorded. Quote request shape + row id + figures. `PG-EV-06`: press rows (Job/Candidate/snapshots/provider_call) reported with identifiers, left in place.
- Second live search ONLY if the first is inconclusive (state why); never a third.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-132.log`, `SG-132_report.md`, `SG-132_verify.log` (vendor re-check, both test runs, suite/mypy, rebuild/recreate proofs, live-search row). First token `SG-132`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000 USD + Jina searches used vs ≤2 bound); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the wiring hunks, their tests, `docs/worklogs` (3 files). **Any other write — schema, cap values, synthesize.py cost symbols, schedulers, suite files beyond the new tests — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs reads + keyless GETs; G1 needs wiring + committed runs (modify-versus-call: tests CALL the seam, fixtures never bypass it); G2 needs writer-seeded refusal + suites; G3 needs rebuild + one recreate + one live search. Per-command-class bounds (120s ordinary / 600s suite-build / 2400s overall), never one blanket timeout. Reads INCLUDE in-process tests + container exec probes; pulling any image besides the slice's own rebuild is NOT included and is a STOP. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): ledger the search, prove the cap sees it, serve it. No per-provider windows, no UI surfacing of Jina cost, no auto top-up logic — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): wiring — does EVERY Jina search leave a ledger row with the estimated figure? cap — does Jina spend move the month total and trip the enrich refusal? live — does the served build prove it on a real search?
- Enumeration of call sites + difference quoted; both test runs quoted from the commit; BEFORE/AFTER month totals quoted; refusal quoted without live-search burn; vendor re-check quoted (figure + URL + time); rebuild + one-recreate proofs quoted; one live row quoted (id + estimate + month delta); empty `models/`+`alembic/` diff quoted.
- $0.000000 USD + ≤2 Jina searches; no vacuous pass (self-written rows, status-without-row, return-value-only proofs evidence nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + Jina usage vs bound. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-132 | Report: docs/worklogs/SG-132_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/build · 2400s overall; expected ~1200s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 USD + ≤2 Jina searches (~$0.0005 est each, credits); actual-versus-budget per leg with units.
