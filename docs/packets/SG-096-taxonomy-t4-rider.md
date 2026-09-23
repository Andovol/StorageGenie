# SG-096 — Taxonomy T4 rider: v4 live on the public entry (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D128-approved T4 verify rider (production restart, G-K2) closing the D115/D117 taxonomy stage: SG-093 (vendored data + resolver) + SG-094 (schema field + frozen v4 prompts) + SG-095 (reader on v4, triple wired, gated candidates) are committed but the running service still serves the pre-slice build (SG-083 image). THIS slice rebuilds + recreates + verifies, nothing else. NO code changes — any diff outside `docs/worklogs` is a STOP. SG-095 REMAINING (reviewer alternatives surface on `google_type_resolution`, catalog filter) is OUT OF SCOPE — deferred spec non-goal, not this rider. **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.30.0` == published (`c9c9ba3`; D125 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** rebuild + one recreate + verify ONLY. No migration (none shipped since `20260917_sg068_saved_search` — T1–T3 touched no model; verify on target, don't assume), no data writes, no provider calls ($0 — no extraction POST, structural proof). `PG-PR-04` stated: this packet IS the production run it proves. Host `.env` may have gained `JINA_API_KEY` since the running image (D109) — the recreate loads it; Enrich stays unwired so no behavior change; disclose the key NAME presence only, never values.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.30.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-09` · `PG-SC-11` (no migration — stated) · `PG-SC-12` · `PG-DP-01` · `PG-DP-02` (restart-gated: no full sweep, targeted in-process only) · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (THIS DEPLOY stated) · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s build, 600s recreate+verify, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (read-only probes + counts). Restart: ONE backend recreate (D128). Deploy: THIS slice.**

## G1 — capture BEFORE (every observable the proof moves)

- Before any build: image id + `RestartCount` of the running backend container, served frontend bundle name+size+sha256 (capture live — EXPECTED to differ from SG-083's `index-fOM9Er4k.js` since SG-082 shipped frontend; AFTER must equal THIS BEFORE, not any named old file), `alembic current` (expected single head `20260917_sg068_saved_search` — verify), the 24-table row counts + DB mtime+bytes, gate behaviour (http 301 / https 401 without login), regressions sample (taxonomy/saved-searches/facets/analytics-summary 200). Quote all raw — a production-change claim without a before-capture is not a claim (`PG-EV-08`).
- Taxonomy BEFORE (expected, verify): live `load_prompt` versions (running image predates T1–T3 — expected v3, confirm through the running container or state why unobservable); candidates triple absent-or-null on a fresh read. Tag both expected, never certain.

## G2 — rebuild + one recreate

- Rebuild the backend image from the committed tree (build log quoted; it must show the taxonomy data file `backend/app/data/google_taxonomy/2021-09-21.txt` + the three `extract-*-v4.md` entering the image — grep the build context/file list, raw). Up to ONE `up -d` recreate of the backend service. No migrate (if `alembic history` shows an unapplied head you did not expect, STOP, do not upgrade). `BUILDX_CONFIG` relocation to a writable tmp is allowed if the confinement denies it (SG-067 precedent, ruled acceptable); anything else denied is `unanswered`, never routed around.
- Enumerate on target the set this slice acts on (a list is a fact too): the vendored data path + the three v4 prompt paths as resolved inside the build context; require the difference from my expectation reported either way.

## G3 — verify AFTER (delta from the captured baseline)

- Image id DIFFERS, `RestartCount` +1, loopback-only preserved (`ss`), health `ok/ok/ok` exact, gate 301/401 both sides, regressions 200 (analytics body may differ only in `generated_at` — disclosed, SG-078 precedent), `alembic current` IDENTICAL both sides, row counts identical, DB mtime + bytes unchanged (no data writes), frontend bundle name+size+hash IDENTICAL to G1 BEFORE (expected — this slice writes no code; a difference is a STOP-and-report finding).
- New-image proof (`PG-SC-12` — decode what the consumer runs): the FRESH container was created from the NEW image id (quote `docker ps` image column + `docker images` hashes); in-image bytes: taxonomy file + all three v4 prompts read through the REAL runtime loaders inside the running container (`reader.load_prompt` returning v4 all three + resolver row count/version quoted); live gating: `GET /v1/candidates/{candidate_id}` shape structurally proven on the live service or live-proven with the reason stated (`PG-PR-04` scope). `docker exec` into the fresh backend container and one `docker run --rm` image inspection ARE reads for this packet (`PG-IC-01` decided either way). No extraction POST ($0 — stated, not silent).
- Full-suite sweep WAIVED (`PG-DP-02` — restart-gated slices never order it; every externally-driven test would exercise the previous build); substitute: targeted in-process taxonomy legs by node ID (`test_google_taxonomy.py` v4-reader + triple legs) run against the new build; name the post-restart run as the authority. A count or absence premise carries the RAW command output, never a paraphrase.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-096.log`, `SG-096_report.md`, `SG-096_verify.log` (raw outputs + before/after captures + BOTH fail-then-pass runs where a gate claims one, `PG-EV-09`). First token `SG-096`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for WRITES. Everything else is commands (build/up/probes), never edits. **Any file edit outside `docs/worklogs` is a STOP.**
- Cross-product (`PG-IC-01`): G1–G3 need container/DB/gate reads + `docker exec` image reads (authorised above) + one rebuild + one recreate; nothing else. No extraction call, no migration, no data write, no alternatives-surface change.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): one rebuild, one recreate, before/after captures. No code, no tuning, no Enrich wiring.
- Premises re-verified this session (`PG-IC-09`): `reader.py:54-58` v4 map · `Dockerfile:17` `COPY backend/ ./` · `.dockerignore:19-20` `data`+`backend/data` (root-only, `backend/app/data` survives) · `pyproject.toml:48` hatch `packages=["app"]` · prompts `extract-*-v4.md` on disk · alembic 5 files ending `20260917_sg068_saved_search` · frontend last touched SG-082 (bundle capture-within-slice, never a named old file).

## Acceptance criteria

- Before-captures quoted for every observable (image, RestartCount, bundle, alembic, counts, mtime, gate, regressions, taxonomy BEFORE expected).
- After: image differs + RestartCount +1 + loopback + health exact + gate + regressions 200 + alembic identical + counts/mtime/bytes identical + bundle IDENTICAL to G1 BEFORE + taxonomy file + v4 prompts in-image through the REAL loaders + gating live-or-structurally proven with reason.
- $0; no migration run; no data writes; targeted taxonomy legs green; full sweep explicitly waived with substitute named; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — what did production look like before? G2 — was exactly one rebuild + one recreate performed with the taxonomy bytes in the image? G3 — is the new image live with everything else unchanged and v4 served?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units (`PG-PR-06` stated against the rebuild/recreate bounds).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-096 | Report: docs/worklogs/SG-096_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s build · 600s recreate+verify · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
