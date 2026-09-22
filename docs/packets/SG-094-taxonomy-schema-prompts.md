# SG-094 — Taxonomy T2: schema field + v4 prompts, transcribe-only (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D127-approved L3 arc slice 3 of 4 (SG-082 GREEN 98 → SG-093 GREEN 98 → T2 → T3; riders parked). Taxonomy stage D115 (L3 bounds identical to D107) with spec `docs/superpowers/specs/2026-09-21-google-taxonomy-design.md` § S2 APPROVED (D116) and plan `docs/superpowers/plans/2026-09-21-google-taxonomy.md` Task 2 APPROVED (D117). T1 shipped the vendored data + pure resolver. THIS slice adds the transcribed-only schema field and freezes three v4 prompt files. It deliberately does NOT flip the live pipeline: `reader.py` `PROMPT_FILES` stays on v3 (SG-079/SG-080 precedent), so the running service is untouched and this slice is $0 offline. T3 flips the reader + wires the triple. Per `PG-SC-02`: the new field is UNRECORDED this slice (no writer fills it, no reader shows it) — T3 is the writer/reader slice. **Authoring date (metadata, never a gate):** 2026-09-22. Transport: the standard job_spawn lane. Contract: recorded `0.30.0` == published (`c9c9ba3`; D125 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** schema + prompts ONLY. No reader flip, no candidates wiring, no resolver calls in the pipeline, no migration (a nullable model field needs none — state why in the report), no secrets, no deploy, no restart, no provider calls ($0 — a metered call is a STOP-and-report).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.30.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-PR-03`.

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

## G1 — schema field (nullable, transcribed-only, validated)

- `backend/app/services/providers/schemas.py`: add `google_type_proposed: str | None = None` beside the SG-079 v3 fields (verified at `schemas.py:52-62`), joining the `_non_blank_when_present` validator list (verified at `schemas.py:75-87` — add the name to that decorator list, touch nothing else in it). Null when absent/illegible with the matching `unknowns` entry (verify the unknowns mechanism on target from a v3 field — do not inherit my path, quote what you found). Per `PG-SC-02` in as many words: this field is UNRECORDED this slice — no writer fills it, no reader shows it, T3 owns both.

## G2 — three frozen v4 prompts (v3 byte-identical as rollback reference)

- Create `backend/app/services/providers/prompts/extract-food-v4.md`, `extract-medicine-v4.md`, `extract-cosmetics-v4.md`: each = its v3 file's exact content (verified present at packet time) + the spec's verbatim block below + front-matter `template_version` bumped v3→v4. The added block (spec §S2, packets quote the spec file, never chat):
```
## Product type (Google taxonomy)
Propose `google_type_proposed` as the verbatim full category path from the Google
Product Taxonomy, a top-level-only path when unsure, or null when illegible/absent
(plus the matching `unknowns` entry). Never invent numeric IDs or paths.
```
- Prove v3 untouched: `git diff` over the three v3 files is empty (quote it). `PROMPT_FILES` in `reader.py` stays on v3 — assert it still does with the existing live-prompt-map pin (name the test that pins it on target).

## G3 — tests + gates

- Extend `backend/tests/test_google_taxonomy.py` (the T1 file — verify it exists on target): blank `google_type_proposed` (`"  "`) rejected; an `unknowns` entry for the field validates with null value; v4 files load through the real prompt loader with the block present and v3 byte-identical. FAIL-then-PASS raw BOTH runs committed (`PG-EV-09`): pre-run fails on the unknown keyword, post-run green.
- `PG-SC-12`: the prompt-content assertions read the real loader's output, never a re-typed copy. Suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-094.log`, `SG-094_report.md`, `SG-094_verify.log` (raw command outputs + BOTH fail-then-pass runs). First token `SG-094`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling (M45 decided):** `schemas.py` (field + one validator-list entry only) + 3 new v4 files + `test_google_taxonomy.py` additions + `docs/worklogs` — NOTHING else. **Suite-green binds on collision** (minimal root-cause repair + disclosure); anything else is a STOP.
- Cross-product (`PG-IC-01`): no criterion demands a reader flip, wiring, migration, or container act — no cell collides; stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Field present, nullable, blank-rejected, unknowns-paired; validator list otherwise byte-identical in behavior (suite proves).
- v4 files = v3 bytes + verbatim block + version bump (diff quoted); v3 files byte-identical (empty diff quoted); reader still on v3 (pin named green).
- Tests fail-pre/post-pass both committed raw; gates green; nothing outside the ceiling; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-094 | Report: docs/worklogs/SG-094_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite; $0.000000 (no download, no provider call); actual-versus-budget per leg with units.
