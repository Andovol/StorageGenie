# SG-095 — Taxonomy T3: reader flip to v4 + triple wiring + gated candidates (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D127-approved L3 arc slice 4 of 4 — LAST build slice (SG-082 GREEN 98 → SG-093 GREEN 98 → SG-094 GREEN 98 → T3; T4 rider parked for its own owner word). Taxonomy stage D115 (L3 bounds identical to D107) with spec `docs/superpowers/specs/2026-09-21-google-taxonomy-design.md` § S3–S4 APPROVED (D116) and plan `docs/superpowers/plans/2026-09-21-google-taxonomy.md` Task 3 APPROVED (D117). T1 shipped data + resolver; T2 shipped the field + frozen v4 prompts with the live path still on v3. THIS slice flips the reader to v4, resolves every item's triple, and carries it as gated candidate fields. Per `PG-SC-02`: the triple is RECORDED here — writer (proposal builder) and reader (`GET /v1/candidates` showing the gated fields) are both in the acceptance below. **Authoring date (metadata, never a gate):** 2026-09-22. Transport: the standard job_spawn lane. Contract: recorded `0.30.0` == published (`c9c9ba3`; D125 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** wiring ONLY. No deploy, no restart, no catalog filter UI, no analytics changes, no live provider call ($0 — a metered call is a STOP-and-report), no migration (triple rides existing candidate field storage — prove the no-migration claim on target the way T2 proved the pydantic case, or report the migration this slice would need and STOP before writing it). Nothing becomes live until the owner-gated T4 rider (`PG-PR-04`).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.30.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-04` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-09` · `PG-SC-11` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04`.

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

**DATABASE: none (triple rides existing candidate field storage — the no-migration proof is G1). Restart: none. Deploy: none. Container actions: none** (read-only queries at most; any denial is unanswered, never routed around).

## G1 — reader flip v3→v4 + version pins (the SG-080 precedent)

- `backend/app/services/providers/reader.py`: `PROMPT_FILES` (verified at `reader.py:54`, currently v3 for all three categories) flips v3→v4 at runtime. Enumerate tree-wide every pin asserting v1/v2/v3 prompt versions and flip exactly the ones this flip invalidates (SG-080 precedent); an injected-version self-consistency pair is kept ONLY if one exists, and then reported with its reason. Quote the enumeration (paths + lines) either way — a list is a fact too.
- Prove the no-migration claim: show where candidate `fields` persist (JSON column vs new column) and state why the triple needs no migration — or, if a migration IS needed, report it and STOP before writing it (a live-DB surface needs its own owner word; this slice does not carry one).

## G2 — triple wiring + gated candidates (resolve every item, gate everything)

- Pipeline step that builds proposals (enumerate on target — the function that turns extraction items into proposals — with the criterion stated): call T1's `resolve_google_type` + `bucket_for` per item; the resolved triple (`google_type_id`, `google_type_path`, `taxonomy_version` — always together, nullable together) rides the candidate as GATED fields beside `category_proposed` (spec §S2).
- `UNCLEAR` surfaces top-k alternatives to the reviewer (alternatives list from `Resolution`, never auto-resolved). Nothing auto-accepts at threshold 0.0 — prove with a committed proposal through the REAL commit path at 0.0 (SG-082 precedent), contrasting a non-gated deterministic field that does accept.
- Read-back proof (`PG-SC-02`): `GET /v1/candidates` shows the gated triple on a resolved item (test through the route, not around it). D111 layered rule holds: the 6 expiry buckets stay behavior authority; Google id+path+version stored alongside, both gated.

## G3 — runtime-visibility verdict (enumerate now, image proof rides T4)

- Verdict, per mechanism, with outputs quoted: (1) `backend/Dockerfile:17` `COPY backend/ ./` — what it carries; (2) `.dockerignore` `data` + `backend/data` lines — whether `backend/app/data/google_taxonomy/` and the v4 prompt files survive them (state the matching semantics you established and how); (3) `backend/pyproject.toml:48` hatch `packages = ["app"]` — whether non-`.py` data files ride the wheel. In-tree proof: load the vendored file + a v4 prompt through the REAL runtime loaders (`importlib.resources`-or-equivalent + `reader.load_prompt`) from the repo root and quote the versions. The IN-IMAGE proof (bytes in the built image, SG-083 precedent) is explicitly T4's — name it as such, do not build here.

## G4 — tests + gates

- Extend `backend/tests/test_google_taxonomy.py`: resolved item carries triple + version end-to-end offline (fake provider scripted with `google_type_proposed` set); paraphrase item asserts `unclear` + alternatives present + no auto-accept; `PG-SC-11` end-relative grep over touched test files committed raw. FAIL-then-PASS raw BOTH runs committed (`PG-EV-09`).
- `PG-SC-12`: assertions read the real loader/router/candidate machinery — no re-implemented boundary. Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-095.log`, `SG-095_report.md`, `SG-095_verify.log` (raw command outputs + BOTH fail-then-pass runs + every gate). First token `SG-095`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling (M45 decided):** `reader.py` (flip only) + `candidates.py` (triple wiring only) + the proposal-builder step's file + `google_taxonomy.py` (only if the resolver needs a T3-driven fix, disclosed) + `test_google_taxonomy.py` additions + `docs/worklogs` — NOTHING else. **Suite-green binds on collision** (minimal root-cause repair + disclosure); anything else is a STOP.
- Cross-product (`PG-IC-01`): no criterion demands a deploy, filter UI, analytics change, provider call, migration write, or container act — no cell collides; stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Reader serves v4 at runtime for all three categories (version asserted through the real loader); v1/v2/v3 pins enumerated with the flip list quoted; injected pair kept-iff-exists with reason.
- Resolved item shows the full triple + version through `GET /v1/candidates`; unclear item gates with alternatives; 0.0-threshold proof with contrast; no auto-accept anywhere on the triple.
- Runtime-visibility verdict per mechanism quoted; in-tree loader proof green; image proof named as T4's.
- Tests fail-pre/post-pass both committed raw; gates green; nothing outside the ceiling; no vacuous pass; no-migration proof stated (or the needed migration STOP-reported, unwritten).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-095 | Report: docs/worklogs/SG-095_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite; $0.000000 (no download, no provider call); actual-versus-budget per leg with units.
