# SG-080 — photo-ingest pipeline on v3: reader flip + transcript evidence + category proposed (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D101-approved slice 2 of the photo-ingest track (plan `docs/superpowers/plans/2026-09-21-ai-ingestion-enrichment.md` Task 2; spec §2). SG-079 shipped the schema + frozen v3 prompts with the live path still on v2 (`PROMPT_FILES` v2 pinned by `test_live_prompt_map_still_points_at_v2` — that pin is a freshness pin this slice EXPECTEDLY flips, see G1). THIS slice flips the reader to v3, persists transcripts as evidence, carries `category_proposed` as a gated proposal, preserves all other v3 fields through `ai_items`, keeps split-first + consent + ledger, and attempts exactly one bounded live leg when G0 is green. `eval/run.py` stays untouched (F-SG079-1 default carried). **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** pipeline wiring ONLY (enumerated ceiling below). No migration, no secrets in logs, no deploy, no restart (`PG-PR-04` stated — ships on the SG-083 rider). Live leg: temp DB only, never production (`PG-PR-10` — no production-write authority granted or inferred).
**Money posture:** REAL metered actual-vs-bound in the report; worst-case bound **$0.015 for ≤3 live images** (unit USD; basis: SG-049 run-2 measured ≈$0.005/image worst leg; `PG-IC-04` multiply-out on the worst case, not the expected).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-04` · `PG-EV-06` (authority: NONE — temp DB; report rows, leave them) · `PG-EV-07` · `PG-EV-09` · `PG-SC-02` · `PG-SC-09` · `PG-SC-11` (no migration — stated) · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NO DEPLOY stated) · `PG-PR-06` · `PG-PR-10` (temp-DB-only stated).

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

**DATABASE: temp/throwaway only for the live leg; otherwise none. Restart: none. Deploy: none.**

## G0 — enablement re-gate (states whether the live leg runs)

- Read (never print) the key presence + `SG_CONSENT` + `SG_PROVIDER_ID` the way SG-055/SG-066 did, and assert the SELECTED provider id + route, not only `ai_status`-enabled (M32 lineage: `ai_status`-enabled does not prove the metered adapter is selected — quote `settings.sg_provider_id`, the registry id the call uses, and the route function name). Stopping is SUCCESS: if any leg is red, the live leg (G5) reports `unanswered` with the exact red leg quoted, and G1–G4 still ship offline at $0.

## G1 — flip the reader to v3 (live behaviour change, fully traced)

- Re-read `reader.py:50-55` + `load_prompt` + one v2/v3 file head before touching (`PG-IC-09`): I hold `PROMPT_FILES = {food: extract-food-v2.md, medicine: extract-medicine-v2.md, cosmetics: extract-cosmetics-v2.md}`. Flip all three to v3. v1/v2 files byte-untouched (empty diff quoted raw).
- The SG-079 v2-pin test (`test_live_prompt_map_still_points_at_v2`) EXPECTEDLY fails after the flip — it is a freshness pin (`PG-SC-09` inverse: the feature working makes it fail), not a regression: update it to the v3 expectation (surgical hunk, quoted). Then grep the whole test tree for every other v2 pin (`extract-.*-v2`, `PROMPT_FILES`, `template_version.*v2` — state the criterion, enumerate on target, report the diff either way; a list is a fact too): each hit is either updated with reason or reported as intentionally v1/v2-locked.
- FAIL-then-PASS: pin test fails pre-flip on the flipped expectation (quoted), passes post. `provider_call` rows written post-change carry `prompt_template_version = extract-<cat>-v3` (assert on what crosses the real boundary — the ledger row, `PG-SC-12`).

## G2 — transcript persisted as evidence (never an assertion value)

- Enumerate the evidence write path on target (criterion: the constructor/service function that creates `Evidence` rows and what links them to a job/household) — do not assume my shape. Store each item's `transcript` as retrievable evidence linked to the same job (or the source evidence row, decided and reported), readable through the existing evidence read path. Assert the negative: no `transcript` text lands in any assertion `value_json` (grep-gated, raw output).

## G3 — category proposed + v3 fields preserved (read-back traced per field)

- `category_proposed`: carried as a GATED proposal (never threshold-auto-accepted — extend `GATED_FIELDS` only if that set is what gates it on this tree; if the gate lives elsewhere, name it and extend there, quoted). It must be visible on the existing candidate/review read path: name the exact reader (route or query) that shows it, or state in as many words that it rides `ai_items` only this slice and which later slice promotes it (`PG-SC-02` — resolution recorded or explicitly unrecorded, never silent).
- All other v3 fields (brand/variant/size/barcode/storage/warnings/allergens/nutrition): preserved verbatim into proposal `ai_items` (already `item.model_dump()` — prove with a test driving the REAL candidate builder on a v3-shaped `ExtractionOutput`: every new field crosses into `ai_items` byte-equal). They are NOT promoted to accept-writable fields this slice — stated, not silent.
- Zero auto-accept: a test proves no v3-sourced field auto-accepts at any confidence (gated or unrecorded-by-decision above).

## G4 — split-first + pipeline end-to-end on scripted v3 ($0)

- Multi-item v3 output splits first (existing split path, v3-shaped items incl. null-heavy ones); per-item quantity stays per-item (SG-049 advisory lineage — verify, don't assume).
- End-to-end through the REAL `run_ai_extraction` with a scripted v3 provider payload (Fake/scripted seam, no network): extraction → evidence → candidates → gated review tasks, consent gate + monthly-ledger refusal path exercised (refusal BEFORE any call). `PG-EV-04`: assert the SHAPE of what would have been sent (bytes + prompt handed to the seam) in one test — the slice's verification must not stop at the mock.
- Consent/ledger/candidate flow otherwise unchanged; full suite green modulo 2 stash-reproved base reds; ruff clean; mypy delta 0 quoted; secret scan 0.

## G5 — exactly one bounded live leg (only when G0 is green)

- ≤3 COMMITTED images (`backend/eval/corpus/sg029/images/*.png` — real source, `PG-EV-07`) through the real pipeline on a TEMP db with the real metered adapter. Worst-case bound $0.015; report actual-vs-bound with units (`PG-PR-06`). Rows the run creates (job/evidence/candidate/provider_call, ids quoted) are REPORTED and LEFT in the temp db (`PG-EV-06`; authority NONE — production never touched, `PG-PR-10`). A provider-side failure (e.g. loud-502) is a FINDING with the raw error quoted, not a slice failure — provided G4 is green. If G0 is red, this goal reports `unanswered` (never routed around).

## G6 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-080.log`, `SG-080_report.md`, `SG-080_verify.log` (raw outputs + BOTH fail-then-pass runs). First token `SG-080`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** actual vs $0.015 bound); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/providers/reader.py` (PROMPT_FILES flip + whatever G2/G3 wiring the enumeration finds — every touched function quoted) · `backend/app/services/candidates.py` (gating/whitelist/proposal only) · `backend/app/services/evidence_service.py` ONLY if G2 needs a writer hunk (quoted + reason, else untouched) · `backend/app/services/job_service.py` ONLY if the AI-step call needs change (quoted + reason, else untouched) · ONE test file NEW (`backend/tests/test_sg080_ingest_pipeline.py`) + SURGICAL edits to `backend/tests/test_sg079_v3_schema.py` (v2→v3 pin only, quoted) + any other v2-pin test the enumeration finds (each quoted) · `docs/worklogs` (3 files). **Anything else is a STOP** — router/schemas/prompts content (v3 files frozen — content edits need a new slice)/API/frontend/migrations/models/compose/`.env`/`eval/run.py`/STATE/AGENTS/packet dirs.
- Cross-product (`PG-IC-01`): no criterion touches production, the network beyond the single G5 leg, or the running service (no restart; `PG-PR-04` — the flip takes effect on the next rider deploy, stated). Reads include the suite + offline runner only — no container image pull/run.
- A count or absence premise carries the RAW command output, never a paraphrase. Angle-token standing line: any in-scope file carrying `<...>` literals is re-probed by char codes after editing; tests constructing such strings build them from character codes.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition.
- Simplicity (`G-A7`): flip + evidence writer + gated proposal + preservation proofs + one bounded live leg; no new review UX, no Enrich (D102-held).

## Acceptance criteria

- G0 green-or-honestly-red (selected provider id + route quoted, or the exact red leg quoted with G5 `unanswered`).
- Reader loads v3 for all three categories (runtime read, not a copy); v1/v2 byte-identical; v2-pin updated + full-tree v2 enumeration reported; ledger rows carry v3 versions.
- Transcript retrievable as evidence AND absent from every assertion value (both proved, raw).
- `category_proposed` visible on a named read path, gated (never auto-accepts at any confidence); every other v3 field byte-equal in `ai_items`; accept-writable promotion explicitly deferred, not silent.
- Split-first on v3 items; scripted end-to-end green through the real pipeline + refusal path; request-shape test present; suite/ruff/mypy/secrets per G4; $0 outside G5.
- G5 (if green): ≤3 committed images, real adapter, temp DB, actual-vs-$0.015 quoted, rows reported + left; no production touch; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — does the live path load v3 with v1/v2 preserved? G2 — is the transcript evidence (and only evidence)? G3 — is the category a visible, gated proposal with everything else preserved? G4 — does the wired pipeline refuse-before-call and never auto-accept? G5 — does v3 survive one real metered call within bound?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** actual vs $0.015 bound, per leg with units (no production run — containment per `PG-PR-06` stated against the temp-DB leg).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-080 | Report: docs/worklogs/SG-080_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1800s overall; REAL metered worst-case **$0.015 for ≤3 live images** (USD; SG-049 run-2 ≈$0.005/image basis); actual-versus-budget per leg with units.
