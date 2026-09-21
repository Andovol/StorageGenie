# SG-079 — photo-ingest schema v3 + frozen v3 prompts (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D101-approved slice 1 of the photo-ingest track (plan `docs/superpowers/plans/2026-09-21-ai-ingestion-enrichment.md`; spec `docs/superpowers/specs/2026-09-21-ai-ingestion-enrichment-design.md` §1–§2). THIS slice extends the strict extraction schema and freezes three v3 prompt files. It deliberately does NOT flip the live pipeline: `reader.py` `PROMPT_FILES` stays on v2 (verified this session: `food → extract-food-v2.md`, `medicine → extract-medicine-v2.md`, `cosmetics → extract-cosmetics-v2.md`), so the running service is untouched and this slice is $0 offline. SG-080 flips the reader + wires transcript/category. Per `PG-SC-02`: the new fields are UNRECORDED this slice (no writer fills them, no reader shows them) — SG-080 is the writer/reader slice. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** schema + prompts + tests + fixtures ONLY. No reader/router/pipeline change, no migration, no secrets, no provider calls ($0). No deploy, no restart (`PG-PR-04` stated — ships on the SG-083 rider). NETWORK: none (prove it).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-07` · `PG-EV-09` · `PG-SC-02` (unrecorded-stated) · `PG-SC-09` · `PG-SC-10` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NO DEPLOY stated).

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none.**

## G1 — extend the strict schema (transcribed-only, Pydantic v2)

- Re-read `backend/app/services/providers/schemas.py` before touching it (`PG-IC-09`): I hold `ExtractionItem` with `name, expiry_date, opened_date, date_type, lot, quantity, unit, asset_type, confidence, uncertainty_reasons` (validators: quantity finite ≥ 0; unit/asset_type non-blank when present; ISO dates; uncertainty required below 1.0; `unknowns` entries `items.<i>.<field>` with null-beside-unknown enforced via `ExtractionItem.model_fields`). If your read differs, your read wins — report it.
- Add nullable transcribed-only fields: `brand, variant, size_text, barcode, category_proposed, transcript, storage, warnings, allergens, nutrition_per100g, nutrition_serving` (all null when absent/illegible + `unknowns` entry; never inferred — a value beside an `unknowns` entry fails validation, reusing the existing mechanism). `category_proposed` is an open-vocabulary slug (canonical mapping happens downstream in SG-080, never here). `transcript` is verbatim label text, evidence only, never a fact. Exact container types are yours within `extra="forbid"` strictness; extend the non-blank-when-present validator to the new string fields.
- FAIL-then-PASS raw: new tests asserting the new fields (accept transcribed values; reject fabricated value-beside-unknowns; prose never parsed) FAIL on pre-change code and PASS post-change. BOTH runs committed to the verification log (`PG-EV-09`); the gate is the tests, not the command (`PG-EV-02`); the failing run must be seen to fail (`PG-EV-01`).

## G2 — freeze three v3 prompt files (v1/v2 bytes untouched)

- Re-read one v2 file + the `PROMPT_FILES` map before writing (`PG-IC-09`): I hold front matter `template_version/category/output_schema/repair_policy`, transcribe-only rules, `unknowns` `items.<index>.<field>`, `needs_evidence`, JSON-only, single-retry Repair section. Create `extract-food-v3.md`, `extract-medicine-v3.md`, `extract-cosmetics-v3.md` with `template_version: extract-<cat>-v3`, same envelope, extended field rules (each new field: transcribe verbatim or null + `unknowns`; category as proposed slug; transcript verbatim), JSON-only + Repair preserved.
- v1/v2 byte-identical post-change: `git diff --stat` on the six old files empty, quoted raw. The v3 files under test are the COMMITTED files from this packet's base (`PG-EV-07` — no Coder-authored stand-in input; `PG-SC-12` — score through the real `schemas` module + real `eval/run.py` offline path where it runs without modification).
- New fixtures `backend/eval/corpus/sg079/` (small, ~6: clean + partial + glare across food/medicine/cosmetics exercising the new fields) + manifest. If `eval/run.py` needs a loader change for the new dir, that hunk is quoted with reason; default: runner untouched. `--live` is FORBIDDEN this slice (offline only); any corpus file the runner rewrites by design is reverted.

## G3 — what must NOT change

- `reader.py`, router, pipeline, candidates, API, frontend, migrations, compose, `.env` untouched. No table change (the static table registry stays green unchanged). Full backend suite green modulo the 2 base decoder reds — base-reprove the reds by stash on this tree (SG-073 precedent), quoted. `ruff` clean; `mypy` delta 0 from the pre-change baseline, quoted. Secret scan 0. $0; no network (state how proven: no new socket/http import + offline run).
- A count or absence premise in the report carries the RAW command output, never a paraphrase. Angle-token standing line: any in-scope file carrying `<...>` literals is re-probed by char codes after editing; tests constructing such strings build them from character codes.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-079.log`, `SG-079_report.md`, `SG-079_verify.log` (raw outputs + BOTH fail-then-pass runs). First token `SG-079`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/providers/schemas.py` · 3 NEW prompt files (`prompts/extract-{food,medicine,cosmetics}-v3.md`) · ONE new test file (`backend/tests/test_sg079_v3_schema.py`) · NEW fixtures `backend/eval/corpus/sg079/*` · `backend/eval/run.py` ONLY if the new corpus needs a loader change (hunk quoted + reason, else untouched) · `docs/worklogs` (3 files). **Anything else is a STOP** — reader/router/pipeline/candidates/API/frontend/migrations/compose/`.env`/STATE/AGENTS/packet dirs.
- Cross-product (`PG-IC-01`): G1 needs schemas + its test; G2 needs the 3 new files + fixtures; no criterion touches the network, the DB, or the running service. Reads include executing the test suite and the offline eval runner only — no container image pull/run, no runtime the packet does not name.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition.
- Simplicity (`G-A7`): schema fields + frozen prompts + fixtures; no pipeline, no UI, no framework.

## Acceptance criteria

- New-field tests fail-pre → pass-post (both runs committed raw); fabricated value-beside-unknowns rejected; prose never parsed.
- Three v3 files exist with exact front matter; six v1/v2 files byte-identical (empty diff quoted raw); `PROMPT_FILES` still maps v2 (live behavior unchanged).
- Extended fixtures scored through the real schema module (and real eval runner where it runs unmodified); no live call; $0.
- Full suite green modulo 2 stash-reproved base reds; ruff clean; mypy delta 0; secret scan 0; no migration; no deploy claimed; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — does the schema accept transcribed v3 fields and reject fabrication? G2 — are the frozen v3 prompts complete with v1/v2 preserved and the live path untouched? G3 — did nothing else move?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units (no production run — `PG-PR-06` containment N/A, stated).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-079 | Report: docs/worklogs/SG-079_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
