# SG-093 — Taxonomy T1: vendored Google data + pure resolver + bucket map (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D127-approved L3 arc slice 2 of 4 (SG-082 GREEN 98 → T1 → T2 → T3; riders parked). Taxonomy stage D115 (L3 bounds identical to D107) with spec `docs/superpowers/specs/2026-09-21-google-taxonomy-design.md` APPROVED (D116) and plan `docs/superpowers/plans/2026-09-21-google-taxonomy.md` Task 1 APPROVED (D117). SG-082 closed Enrich fetch; THIS slice vendors the taxonomy data and builds the pure offline resolver — nothing else. **Authoring date (metadata, never a gate):** 2026-09-22. Transport: the standard job_spawn lane. Contract: recorded `0.30.0` == published (`c9c9ba3`; D125 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** pure offline $0 — the ONLY network is the single taxonomy download below (free GET, unmetered); no provider calls, no key reads, no secrets anywhere on this path. No schema change, no prompt change, no candidates wiring, no migration, no container actions.
**Money posture:** $0.000000 actual vs $0 bound (one free download GET; nothing metered exists).
**Guards invoked (0.30.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-05` · `PG-EV-09` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-PR-03`.

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

## G1 — vendor the taxonomy file (exactly one download, verified three ways, never hand-edited)

- Download `https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt` to `backend/app/data/google_taxonomy/2021-09-21.txt` (new directory — verified absent at packet time). Verify ALL THREE: first line `# Google_Product_Taxonomy_Version: 2021-09-21`, size `482896` B, `5596` lines (spec `docs/superpowers/specs/2026-09-21-google-taxonomy-design.md:18` — hypothesis, the download is the authority). ANY mismatch is STOP-and-report, never a hand-edit. No scratch copy committed anywhere else.

## G2 — pure resolver + bucket map (no I/O outside the vendored file, no network, no clock)

- New `backend/app/services/google_taxonomy.py`: `TAXONOMY_VERSION = "2021-09-21"`, `ACCEPT_SCORE = 0.6`, `ACCEPT_MARGIN = 0.15`, `TOP_K = 5`; frozen `Resolution` (`status` resolved|unclear|uncategorized, `google_type_id`, `google_type_path`, `taxonomy_version`, `score`, `margin`, `alternatives`); `resolve_google_type(proposal: str | None) -> Resolution` (trim + collapse-whitespace + casefold; exact full-path match accepts at 1.0; else token-set top-5 with the accept gates; `None` → uncategorized, below-gates → unclear, never mapped); `bucket_for(google_type_id, google_type_path) -> str` (longest-prefix map: `Food, Beverages & Tobacco` → `food_beverages`, `Health & Beauty` → `cosmetics_personal_care` default with pharma-prefix exceptions enumerated from the vendored file and quoted, all other top-levels → `non_perishable`, unknown → `uncategorized`). Design calls inside these rules are yours; the D111 layered decision (6 expiry buckets stay behavior authority, Google id+path+version stored alongside) is NOT this slice — no schema touched.
- New `backend/tests/test_google_taxonomy.py`: at minimum the 5 plan cases (exact-path resolves with id+version; vague paraphrase unclear-never-mapped; None uncategorized; food subtree bucket; out-of-scope retains type with non_perishable). FAIL-then-PASS raw BOTH runs committed (`PG-EV-09`): pre-run with the module absent (import/attribute errors), post-run green.
- Gates: full backend suite green modulo the 2 known decoder env reds (stash-proved), `ruff check` clean, `mypy` delta 0, secret gate 0.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-093.log`, `SG-093_report.md`, `SG-093_verify.log` (raw command outputs + BOTH fail-then-pass runs). First token `SG-093`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling (M45 decided):** `backend/app/data/google_taxonomy/2021-09-21.txt` + `backend/app/services/google_taxonomy.py` + `backend/tests/test_google_taxonomy.py` + `docs/worklogs` — NOTHING else. **Suite-green binds on collision** (repairs minimal + root-cause + disclosed); anything else is a STOP.
- Cross-product (`PG-IC-01`): the download is the only network act — no criterion forbids it and no blanket constraint forbids the suite, ruff, or mypy runs; named here so no cell is empty.
- No fixed dates except this header's authoring-date metadata; the taxonomy version `2021-09-21` is DATA (part of the pinned artifact identity), not a clock; all time reads are the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Vendored file byte-verified all three ways (line + size + count quoted); any deviation STOP-reported, never edited.
- The 5 plan cases fail-pre (module absent) and pass-post, both runs committed raw; resolver reads only the vendored file (assert no `httpx`/`urllib`/socket import in the module source).
- Gates green as in G2; nothing written outside the ceiling; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-093 | Report: docs/worklogs/SG-093_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite; $0.000000 (one free download GET); actual-versus-budget per leg with units.
