# Phase 5 — Hardening (slice plan)

**Date:** 2026-09-21 · **Stage autonomy:** L3 recommended for the next-session implementation arc (owner approves scope + L-grant now, building next session — D34 precedent) · **Coder:** opencode/medium (standing) · **Blueprint:** v3 §14 Phase 5 (p. 541–544, "Hardening (ongoing)"): privacy controls, backup/restore, export/import, observability, regression evaluations; PG/S3 profile only when scale demands (explicitly OUT — SQLite/local stands).

**Basis:** Phases 0–4 closed (photo-ingest v3 live since SG-083); Enrich design approved but HELD on owner source research (D102 — not in this stage); open threads carried below. **Landscape note:** everything here is in-house verification of in-house machinery (ledger, redaction helper, eval runner, static registry) — no dependency beats a drill script and a scoring run, and none is proposed.

**Exit condition (bounded; hardening is "ongoing" per blueprint):** eval runner scores every frozen corpus with recorded baselines; backup restores to temp byte-equal with a runbook; privacy audit proves redaction + identifiers-only on every provider path; the static table registry is derived, not listed. Then the stage closes; Enrich + UX tracks remain queued, not staged.

## Slice 1 — SG-085: regression-eval hardening (offline, $0)

**Outcome:** the eval runner outgrows its single-corpus hardwire (F-SG079-1 closed properly): manifest selector (sg029 + sg079, extensible), frozen baselines recorded for both, v1-metrics-identical guard.
**Files:** `backend/eval/run.py` (selector only, scoring untouched) · `backend/eval/baseline_*.md` (recorded numbers) · `backend/tests/test_eval_corpus.py` (selector + frozen-baseline tests).
**Out of scope:** new fixtures, prompt tuning, `--live`, any provider call.
**Tests:** both corpora score offline with baselines reproduced exactly; a baseline drift fails loudly (seen-to-fail gate).
**Deliverables:** multi-corpus runner + frozen baseline record.

## Slice 2 — SG-086: backup/restore drill (production READ, G-K3)

**Outcome:** the live SQLite + storage backup story exists and is proven: backup to temp, restore-to-temp, byte-equal proof, runbook in README.
**Authority (G-K2, stated here for the approval to carry):** read-only copy of the production DB file + storage dir; restore lands on TEMP paths only, never the live paths; no `UPDATE/DELETE/INSERT` against production; row counts before/after quoted.
**Files:** drill script (`backend/scripts/` or docs-runbook-driven commands — Coder decides, reports) · `backend/tests/` (restore-to-temp byte-equality, temp fixtures only) · README runbook section.
**Out of scope:** scheduled cron, off-box copies, PG/S3, any production write.
**Tests:** temp-DB drill green; production touched by reads only (prove by command log, no writer invoked).
**Deliverables:** proven drill + runbook.

## Slice 3 — SG-087: privacy-controls audit ($0, no new machinery)

**Outcome:** every provider path proven redacted + identifiers-only: reader pipeline, direct adapter, analytics/planning carriers; retention statement written (what is kept, where, how long — from ADR-007 + measured code, no new policy invented).
**Files:** `backend/tests/test_privacy_audit.py` (new: EXIF/GPS absence on every path's outbound bytes; no photo/GPS to web paths — Enrich absent, assert the absence) · docs privacy note if the retention statement needs a home (else worklog only).
**Out of scope:** new redaction code (unless the audit finds a hole — then STOP-and-report, fix rides its own slice), consent-flow changes.
**Tests:** redaction proof green on all paths; secret scan 0.
**Deliverables:** audit verdict + retention statement.

## Slice 4 — SG-088: derived table registry (small, mechanical)

**Outcome:** the `EXPECTED_TABLES` static-registry trap removed: the check derives from `Base.metadata.tables` (or the registry gains a derivation test) so table-adding slices stop tripping it.
**Files:** the registry test + whatever it reads (enumerated in-packet; M9 lineage).
**Out of scope:** schema changes, new tables, behaviour change.
**Tests:** full suite green; a planted extra-table fixture fails the derived check (seen-to-fail).
**Deliverables:** trap removed, suite green.

## Slice 5 — SG-089: Phase 5 exit + close-out

**Outcome:** the stage closes on its exit condition: multi-corpus baselines quoted, drill + audit verdicts carried unmodified, limits stated (Enrich ungated? no — still held; PG/S3 declined; UX tracks queued).
**Deliverables:** exit verdict + README deltas + ratings complete; Phase 6/Enrich proposal goes to the owner next — never auto-chained.

## Explicitly NOT in this stage

- **Enrich SG-081/082** — gated on owner source research (D102 stands; the moment sources land, Enrich packets table as their own stage).
- **Per-field accept UI / chat persistence** — queued UX tracks; each needs its own design slice before build (no combined design-build).
- **Pilot tier calibration** — needs owner usage evidence (F-SG073-1); unmeasurable until the house is used.
- **D61 taste prompts / beauty follow-ups** — owner-gated, arrive as prompts.
- **PG/S3 deployment profile** — declined until scale demands (blueprint:544).
- **Desk items** (#30/#42/#49, EROFS drop-in) — desk-side, never slices.

## Close-out

Stage exit verdict against the bounded condition above; L3 ends; Enrich-on-sources proposal or UX-track design goes to the owner as the next decision — never auto-chained.
