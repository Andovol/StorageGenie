# SG-127 — Follow-up batch: thumbnail bytes, brand promotion, job→candidates route (serve it)

**Settings travel on the trigger** (`SG-127 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved slice (sixth of the L3 residual-completion stage; SG-126 re-drill 98). Three backlog follow-ups, one slice (SG-118 batch precedent): F-SG118-2 (thumbnail bytes mismatch), F-SG119-3 (extraction brand unpromoted), and the GET job→candidates route gap. Orphan thumbs ride SG-128 (storage deletion gets its own enumeration gate); dark-link hue waits on owner eyes (no slice). Verified by the Architect 2026-09-25 (re-verify — every premise below is a hypothesis): F-SG118-2 (`SG-118_report.md:87`) — `_thumbnail_bytes` emits PNG/WEBP bytes under a JPEG-suffixed name (reader hardcoded `image/jpeg`); outline: extend the JPEG flatten branch to png/webp or pass media type into `thumbnail_path` (`local_store.py:12`, writer `evidence_service.py:139-212`, reader `evidence.py:108-117`). F-SG119-3 (`SG-119_report.md:102`) — v3 extraction `brand` (`schemas.py:52`, field list `:83`) is not promoted into candidate `fields` by `build_candidate_from_extraction` (`candidates.py:607`, called `:781`), and no writer produces a `brand` label assertion. Route gap — candidates carry `job_id` (`candidates.py:48,66,88,181`) and `GET /candidates/{candidate_id}` exists (`:148`), but NO route lists a job's candidates (`jobs.py` has `/jobs`, `/jobs/{job_id}`, `/imports/{job_id}` — no candidate listing). THIS slice ships all three + serves them (rebuild + exactly ONE recreate, D17 chain authority; production writes: none — reads and code-serve only). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** three features + serve, nothing else. No migration (no model change — prove by empty diff over `models/`+`alembic/`), no sender/scheduler, no key, no metered call ($0 — a metered call is a STOP-and-report). Exactly ONE recreate; a second is a STOP. No orphan-thumb deletion here (SG-128 owns storage writes); no hue changes (owner eyes own them).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-DP-02` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

**DATABASE: none touched by the features (no model change); live reads only for served verify. Restart: exactly ONE backend recreate (serve leg). Deploy: rebuild + recreate in-slice (`PG-PR-04`: this is how the code becomes live).**

## G1 — thumbnail bytes match the name (F-SG118-2)

- Fix, your choice within the constraint (flatten png/webp to JPEG like the existing branch, or carry the real media type into the name): served thumbnail BYTES must match the served NAME for every source type (jpeg/png/webp; heic via the SG-110 path — state its fate explicitly).
- Fail-then-pass with REAL fixtures per source type asserting magic bytes vs suffix, both runs committed (`PG-EV-09`). Reader hardcoded `image/jpeg` is in-ceiling if the fix moves the type there.

## G2 — extraction brand promotion (F-SG119-3)

- Promote the v3 extraction `brand` into candidate `fields` in `build_candidate_from_extraction`, plus the `brand` label-assertion writer the SG-119 vocabulary already reserves (`candidates.py:38-42,93-95` — re-verify). Null stays null: no invented or substituted brand, ever (SG-119 gap-fill discipline).
- `PG-SC-02`: trace to the read-back — the promoted brand must be visible through the served candidate read (`GET /candidates/{candidate_id}` or the review list the UI consumes); name the route that shows it. Fail-then-pass both committed.

## G3 — GET job→candidates route (review-flow gap)

- New household-scoped GET listing a job's candidates (sibling-gated like the neighboring reads: unknown job → 404, foreign household → denied — mirror the exact gate shape, never invent one). Fail-then-pass both committed.
- Full suite green-except-base-proved-reds (bound 600s, base reds stash-reproved — never inherited); ruff clean; mypy delta 0 quoted; secret gate 0.

## G4 — serve + verify + worklog (rebuild, ONE recreate, served proofs)

- Rebuild; exactly ONE recreate (container-id change quoted, healthy ≤60s else STOP); health exact; gate; alembic head unchanged; table counts delta 0 (the seed rows stay — quote them); served proofs: thumbnail bytes-vs-name on live routes, brand field on a served candidate read, new route 200 + 404 legs.
- `PG-DP-02`: no full end-to-end sweep (the recreate gates it) — targeted served probes above are the authority; the waived sweep is stated with this substitute location.
- `{{WORKLOG_DIR}}/SG-127.log`, `SG-127_report.md`, `SG-127_verify.log` (both test runs + served proofs + counts). First token `SG-127`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.
- Runtime-versus-budget per leg with units (`PG-PR-06` stated against the build+serve bound).

## Constraints

- **Scope ceiling:** WRITES — thumbnail writer/reader hunks, candidate builder + brand writer hunks, the new route + its tests, feature tests, `docs/worklogs` (3 files). **Any other hunk — schema/migrations, orphans, hue tokens, caps, keys — is a STOP.**
- Cross-product (`PG-IC-01`): G1 needs writer/reader + fixtures; G2 needs builder + writer + served read; G3 needs one route + tests; G4 needs rebuild + one recreate + probes; nothing else. No criterion demands a migration, a second recreate, a press, or any metered call — no cell collides; stated so the check exists on paper. Reads explicitly INCLUDE running the suite + build in-process; pulling foreign images or launching unnamed runtimes is NOT included and is a STOP.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): bytes, brand, route, serve. No thumbnail redesign, no review-UX rework, no cap changes — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): bytes — does every served thumbnail's magic match its suffix? brand — does an extracted brand survive to the served candidate? route — can the review flow list a job's candidates?
- Per-type thumbnail magic-vs-suffix quoted from committed runs; brand visible on the served read quoted; route 200 + 404/denied legs quoted.
- Suite/ruff/mypy/secrets per G3; one rebuild + one recreate with identity change; counts delta 0 with seed rows quoted; $0; no vacuous pass (a passing test that never drives the changed path is named, not counted).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-127 | Report: docs/worklogs/SG-127_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/build · 1800s overall; expected ~1200s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
