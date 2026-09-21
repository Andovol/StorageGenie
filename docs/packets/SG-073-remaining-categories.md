# SG-073 — remaining categories: Household/Documents chat fallback + classify activation + nav on landing (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 11 (stage approved D83; D94-approved second half of the D90 split + D95 nav fix riding as a small goal). Two pilot profiles sit in the served taxonomy as inactive DATA (`GET /v1/taxonomy`: `household_chemicals` basic-expiry/no-opened-date/`fallback` chat, `active:false`; `documents_other` long-lead-60-30/no-opened-date/`fallback` chat, `active:false`) and their shipped `CATEGORIES` rows are inactive Phase-3 placeholders (F-SG065-2). Chat serves food + medicine ONLY (`SUPPORTED_CATEGORIES` in `backend/app/services/chat/service.py:53-56`; anything else is an enforced 422) — the descriptor's `fallback` mode is data no code consumes (verified 2026-09-21: no fallback path in the chat service, the API, or the UI). The landing route `/` renders NO nav (`frontend/src/App.tsx:57`, deliberate since SG-054 — owner-reported, D95). THIS slice activates all three. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); host link from SG-072's echo; echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** NETWORK: loopback + container runtime only — NO provider calls ($0; the fallback prompt is proven shape-only, see G1). No migration (active flags are code data, not schema). No deploy, no restart (`PG-PR-04` stated — live proof rides a later owner-gated rider). Secrets: never print, log, quote, or commit a key byte.
**Money posture:** $0.000000 actual vs $0 bound (no live call: the adapter + metered chat path are already meter-proven by SG-038/SG-049; what is new here — fallback prompt assembly, category gating, activation flags — is deterministic code proved offline through the real machinery with a scripted provider).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-03` · `PG-EV-05` · `PG-EV-06` (authority: NONE) · `PG-EV-09` · `PG-SC-02` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NO DEPLOY stated) · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite/build, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: temp SQLite for all tests. Restart: none. Deploy: none.**

## G1 — fallback chat for Household + Documents (generic agent, $0)

- Extend the chat category gate so `household` (→ `household_chemicals`) and `documents` (→ `documents_other`) answer through a GENERIC fallback prompt grounded in that category's catalogue — same adapter text op SG-038 uses, no dedicated agent, no new prompt file unless the shape genuinely earns one (a shared generic template with the category injected is preferred; divergence into per-category prompts is a STOP-and-report, not a silent fork). Cosmetics stays ungated (`chat:"none"` in the descriptor — a dedicated cosmetics agent is a separate decision, explicitly out of this slice).
- Household isolation + unknown-household 404 + corrections path behave exactly as the food/medicine legs (same service function, new keys — prove with the same leg shapes, not fewer).
- FAIL-then-PASS: pre-change `POST /v1/chat/household` → 422 (quoted raw, committed); post-change 200 grounded in the category catalogue (scripted provider through the REAL service + route — `PG-SC-12`). Prompt-shape test pins the fallback prompt carries the catalogue + the question (SG-066 `test_prompt_is_versioned_and_carries_stats` precedent).

## G2 — classify-path activation for Household chemicals + Documents/other (F-SG065-2)

- Follow the SG-036 cosmetics precedent (`test_cosmetics_classifies_without_a_new_task_type`): the activated categories ride the EXISTING classify + manual-entry path — no new task type, no new route, no new table. Flip the shipped `CATEGORIES` rows to their pilot profiles (tier values read from the shipped rows/descriptor — quote them, never invent) AND the served descriptor `active` flags to match (a taxonomy claiming `active:false` for a live classify path is text contradicting inventory — `PG-SC-02` last clause: narrow to what is true).
- The pinning test `test_classification_profiles_round_trip_and_inactive_phase` (`backend/tests/test_plugin_expiry.py:68-108`) MUST change: its `inactive` list asserting 422-`Phase 3` for these two categories becomes 200 + profile assertions (tier_defaults + `opened_date_tracking:false` + slug read-back, cosmetics-leg shape). Pre-change run quoted (passes with 422), post-change run quoted (passes with 200) — the inversion IS the proof.
- Regression: food/medicine/cosmetics legs byte-unchanged in behavior (their asserts untouched and green); manual expiry entry + extensions accept the two newly-active categories (prove with one leg each, not zero).

## G3 — nav renders on the landing route (D95)

- `frontend/src/App.tsx:57`: render `<Nav />` unconditionally (delete the `pathname === "/"` branch). One-line change + a frontend test proving the landing route shows the Analytics link (pre-change fails with the link absent, post-change passes — quoted raw). No other shell change; anything beyond the one line + its test is a STOP.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-073.log`, `SG-073_report.md`, `SG-073_verify.log` (raw suite outputs + BOTH fail-then-pass runs). First token `SG-073`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/chat/` (service + its test file) · `backend/app/plugins/expiry_tracker.py` (`CATEGORIES` rows only) · `backend/app/plugins/descriptor.py` (`active` flags for the two pilot categories only, with the reason quoted) · `backend/tests/test_plugin_expiry.py` (pinning-test inversion only, each edit with reason — `M9` rule) · `frontend/src/App.tsx` (the ONE nav line) + the landing-nav test file (new, or the derived set's named file) · `docs/worklogs` (3 files). **Anything else is a STOP** — provider/seam/router code, other prompts, `.env`, compose, migrations, analytics, saved-searches, taxonomy endpoint, cosmetics chat, storage-location wiring.
- A set is a fact too: where this slice acts on sets (categories to gate, rows to flip, legs to prove), STATE the criterion and ENUMERATE the set on the target — your enumeration, with the difference from my expectation reported either way. My lists above are expectations, not the set.
- Cross-product (`PG-IC-01`): G1 needs the chat route + service read-write; G2 needs the plugin rows + pinning test; G3 needs the one App line. No criterion touches provider code or the seam. Reads MAY pull/run the already-built local images only.
- Full backend suite from `backend/` (600s) + `ruff` clean + `mypy` quoted (delta-0 expected; the 41-base figure re-measured, not restated) + `npm run build` green (quoted) + `npx vitest run` (600s) green. Secret scan 0 (sentinel-key absence included).
- Angle-token standing line: any in-scope file carrying `<...>` literals is re-probed by char codes after editing; tests constructing such strings build them from character codes (SG-062 lineage).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).
- Simplicity (`G-A7`): two gate keys + two row flips + two flag flips + one JSX line; no new agent framework, no new table, no scheduler.

## Acceptance criteria

- `POST /v1/chat/household` + `/v1/chat/documents` 422-before → 200-after, grounded in their catalogues (scripted provider, real route); cosmetics still 422 (quoted); isolation + 404 + corrections legs green.
- Household/Documents classify 422-`Phase 3`-before → 200-after with pilot tier_defaults + `opened_date_tracking:false` + slug read-back; food/medicine/cosmetics legs green unchanged; manual entry + extensions accept the new categories.
- Landing `/` renders the nav with the Analytics link (test fail-then-pass quoted); served taxonomy `active:true` for both pilot categories.
- Suites/build/lint green (quoted); secret scan 0; no migration; no deploy claimed; no vacuous pass; $0 held (no live call).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-073 | Report: docs/worklogs/SG-073_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
