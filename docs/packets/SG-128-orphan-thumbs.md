# SG-128 — Orphan thumbnail cleanup: enumerate by rule, delete exactly that set, prove nothing served flips

**Settings travel on the trigger** (`SG-128 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved slice (seventh of the L3 residual-completion stage; SG-127 batch 98). SG-118 left orphan thumbnails (G-K3); SG-127 F-SG127-2/F-SG127-6 measured them: live PNG evidence carries legacy `_thumb*.png` artifacts (pre-SG-118 naming) the `.jpg` reader never serves. The live scheme, read by the Architect 2026-09-25 (re-verify — every premise below is a hypothesis): `thumbnail_path` (`local_store.py:10-16`) resolves `<sha>_thumb<size>.jpg`; the writer emits JPEG bytes for every source type post-SG-127 (`evidence_service.py:139-144`); the reader serves `image/jpeg` (`api/v1/evidence.py:120`, SG-127 report). ORPHAN RULE (the deletion predicate, decided here — not delegated): a file under the storage root matching `*_thumb<digits>.*` whose suffix is NOT `.jpg`. Safety case: the reader resolves only the `.jpg` path, so deleting rule-members cannot flip any served status (stated; G2 proves it). Regenerability: thumbnails are derivatives the writer re-creates on the upload path — deletion loses no source bytes (originals untouched, never listed for deletion). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** enumerate-then-delete ONLY. No code change, no migration, no rebuild, no recreate, no key, no metered call ($0 — a metered call is a STOP-and-report). Originals (non-thumb files) are never deletion candidates — a candidate that is not a `*_thumb*` path is a STOP. `.tmp` leftovers are NOT in this slice (transient writer state — report if seen, never delete).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-SC-03` · `PG-SC-07` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-01` · `PG-PR-03` · `PG-PR-10`.

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

**DATABASE: none written; live reads only for the served check. STORAGE: the live volume (DELETE of rule-members only, grant D17 — `PG-PR-10`: volume `storagegenie_storage_data`, grant D17, stated here). Restart: none. Deploy: none. Container actions: none.**

## G0 — enumerate by rule BEFORE any delete (nothing is deleted until this is quoted)

- Resolve the volume host path read-only (`docker volume inspect`); list every `*_thumb*` file with full paths + sizes (quote the listing verbatim — the listing IS the blast radius).
- Classify each hit against the ORPHAN RULE: suffix `.jpg` → LIVE (never deleted); any other suffix → ORPHAN candidate. `PG-IC-08` bound at the RULE, not a count: EVERY deleted path must satisfy the rule — one rule-failing path anywhere in the set STOPS the slice before any delete (either direction: an expected orphan that is actually `.jpg`, or an unlisted suffix class nobody named — both stop).
- Empty set is a clean verdict, not a failure (`PG-SC-07`): zero rule-members means the volume is already clean — ship the enumeration as the proof.
- Re-verify the reader premise in-tree (reader resolves ONLY the `.jpg` path): if the reader can serve another suffix, the rule is wrong — STOP, do not delete.

## G1 — delete exactly the enumerated set, nothing else

- Delete ONLY the G0-enumerated rule-members, by exact path, one command per path or a quoted exact list (no globs at delete time — the glob belongs to G0). Before/after volume listing quoted; bytes-reclaimed quoted.
- `PG-EV-06` spirit: every deleted path reported with its size; originals untouched (prove by re-listing a sampled original hash before/after, or state the check used).

## G2 — served regression check (no status may flip 200→404 — `PG-EV-02`)

- BEFORE (from G0, GET-only): per-evidence thumb status for every image evidence. AFTER: identical table. A 200→404 flip is a STOP-and-report (do NOT restore by re-upload — report it; the Architect decides). Pre-existing 404s (legacy-PNG gap, F-SG127-2) staying 404 is unchanged behavior, quoted as such — never counted as proof of anything.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-128.log`, `SG-128_report.md`, `SG-128_verify.log` (enumeration verbatim + delete commands + before/after listings + status tables). First token `SG-128`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for FILE writes; the enumerated live-volume deletes for STORAGE writes. **Any other write — code, tests, originals, `.tmp` files, DB, config — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs volume-inspect + listing + reader read; G1 needs exact-path deletes; G2 needs route GETs; nothing else. No criterion demands a rebuild, a DB touch, a key, or any metered call — no cell collides; stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): list, check the rule, delete the list, prove the serving. No re-uploads, no writer changes, no quota work — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): enumerate — exactly which files are orphans, and why does the rule hold for each? delete — is every deleted path a rule-member and is anything else untouched? serve — did any served status move?
- Full `*_thumb*` enumeration quoted with per-file rule verdicts; every deleted path quoted with size; volume before/after quoted.
- Per-evidence thumb status BEFORE == AFTER (no 200→404 flip); pre-existing 404s quoted as unchanged.
- $0.000000; no code diff of any kind (prove by empty product diff or STOP); no vacuous pass (an enumeration that could not have matched non-jpg suffixes evidences nothing — quote the suffix distribution).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-128 | Report: docs/worklogs/SG-128_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s overall; expected ~300s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
