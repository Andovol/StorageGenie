# SG-130 — Legacy PNG thumb backfill: write the missing `.jpg` thumbs through the writer, prove 200s

**Settings travel on the trigger** (`SG-130 coder=opencode effort=high`, D20) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D20-authorized production word (owner quote "D19 and D20 - approved."): SG-129 deleted the 14 orphan `_thumb*.png` files, leaving the 7 PNG evidences with NO thumb at all — their routes 404 (pre-existing legacy-PNG gap, F-SG127-2). THIS slice backfills exactly those thumbs: for each of the 7 PNG evidences × each size in `settings.thumbnail_sizes`, generate JPEG bytes through the REAL writer (`_thumbnail_bytes`, SG-127 unified) and write the `.jpg` artifact the reader resolves (`thumbnail_path`), then prove 200s. Verdicts: BACKFILLED (14 artifacts written, all served 200 with `ffd8ff` magic) / PARTIAL (any evidence unserved — STOP-and-report, no second attempt) / BLOCKED (writer entry unreachable in-image — commit, receipt, clean tree). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** backfill ONLY. Writes: the committed backfill script + fixture tests + exactly the 14 thumb artifacts on live storage + `docs/worklogs` (3 files). No model/migration change (prove by empty diff over `models/`+`alembic/`), no endpoint, no rebuild, no recreate, no key, no metered call ($0 — a metered call is a STOP-and-report). Originals never rewritten; `.tmp` discipline atomic (write-temp-then-replace, the writer's own pattern). Any 15th artifact is a STOP.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-01` · `PG-PR-03` · `PG-PR-06` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none written. STORAGE: the live volume — exactly 14 thumb artifacts (grant D20; `PG-PR-10`: volume `storagegenie_storage_data`, in-container `/data/storage`, grant D20, stated here). Restart: none. Deploy: none. Container actions: exec to run the backfill ONLY (no restart, no pull, no recreate).**

## G0 — enumerate + entry check (nothing is written until both are quoted)

- Enumerate the 7 PNG evidences WITHOUT any `.jpg` thumb (expectation: the SG-129 AFTER set — 7 PNG originals, 2 live `.jpg` thumbs belonging to the JPEG evidence; ANY delta is a STOP per `PG-IC-08`, either direction).
- Verify the backfill entry IN the served image: the writer's decode+thumb path importable via container python (if the script/tools are absent from the image → BLOCKED, do not rebuild here — the rebuild decision returns to the Architect).
- Read `settings.thumbnail_sizes` (expectation: 256/512 — VERIFY); 7 × len(sizes) is the exact artifact count (14 expected — a different size list re-scopes the count before writing, never after).

## G1 — script + fixture proof (fail-then-pass, both runs committed — `PG-EV-09`)

- Commit `backend/scripts/backfill_legacy_png_thumbs.py` (or extend the drill script's family — decide and report): for each target evidence, decode the ORIGINAL through the real `_decode_image` + `_thumbnail_bytes` path and atomic-write each `thumbnail_path` artifact. Pure re-use of the writer's functions — no re-implemented logic (a re-implemented resizer proves the re-implementation, `PG-SC-12`).
- Fixture tests: PNG fixture → `.jpg` artifact with `ffd8ff` magic at every configured size; already-thumbed fixture skipped-or-overwritten per the script's stated idempotency (state which, prove it). Fail-then-pass quoted.
- `PG-EV-08` before-capture: the 404 table for the 7 PNG evidences (SG-129's AFTER table is the standing record — re-capture live, quote it).

## G2 — the live run: exactly the enumerated artifacts, then 200s

- Run the script once against live storage (quoted command + output). After-listing quoted: exactly the expected new `.jpg` artifacts exist; originals sha-identical (13/13 re-check); no 15th artifact (a surprise file is a STOP-and-report, never a silent accept).
- Served proofs, GET-only: all 7 PNG evidences × sizes → 200 `image/jpeg` with `ffd8ff` magic quoted per leg. Any non-200 is PARTIAL (STOP-and-report, no second attempt in-slice).

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-130.log`, `SG-130_report.md`, `SG-130_verify.log` (404-before table, script output, 200-after table with magics, original hashes). First token `SG-130`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the backfill script, its fixture tests, exactly the enumerated thumb artifacts, `docs/worklogs` (3 files). **Any other write — originals, DB, config, endpoints, suite files beyond the new tests — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs listing + image reads; G1 needs script + fixture tests; G2 needs one exec run + route GETs; nothing else. No criterion demands a rebuild, a DB touch, a key, or any metered call — no cell collides; stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): list, script, run once, prove 200s. No writer refactor, no lazy-regeneration feature, no quota work — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): enumerate — which evidences lack thumbs, and is the set exactly SG-129's aftermath? script — does the backfill reuse the writer's path on fixtures? live — are all 7 PNG evidences served 200 with JPEG magic?
- 404-before table quoted; script + tests committed with both runs quoted; exactly the expected artifacts written (paths + magics quoted); 200-after table quoted per leg; originals identical.
- $0.000000; empty diff over `models/`+`alembic/` quoted; no vacuous pass (a 200 proved only by status without magic evidences nothing — magic per leg).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-130 | Report: docs/worklogs/SG-130_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
