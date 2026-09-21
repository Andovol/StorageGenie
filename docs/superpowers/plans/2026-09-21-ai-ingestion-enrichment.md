# AI Ingestion + Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Project note:** implementer here is the Coder via dispatched slices (SG-079…), one packet per slice. Task checkboxes below map to slice acceptance, not micro-steps.

**Goal:** Photo ingest derives category + fuller properties and every product gains a manual Enrich button, all web data proposed never auto-accepted.

**Architecture:** Same pipeline wider schema (frozen prompt v3, transcript as evidence, split-first, category proposed); new fetch-only Enrich service (verbatim snapshots → proposed candidates, exact-first/fuzzy-as-proposal, label-wins-visible conflicts, versioned manual refresh).

**Tech Stack:** FastAPI/SQLAlchemy/Alembic + SQLite, Pydantic v2 strict schemas, existing provider seam (`extract_items(image_bytes, prompt)`), existing candidate/review UI, fetch-only HTTP for Enrich (no SDK until sources named).

## Global Constraints

- Proposed never auto-accepts; human confirmation mandatory throughout (standing guardrail rule).
- Consent-gated + ledgered provider spend; monthly ledger as today; spend shown on the button under a per-press cap.
- Sends identifiers only, never photos, never GPS.
- Web snapshots are versioned rows, never overwrites; corrections remembered per product.
- At most one metered live leg across the whole plan; full suites green; secret scan 0.
- v1/v2 prompt bytes untouched; v3 frozen new files; no new review UX (existing candidate UI, per-field accept).

---

## File structure (what each slice touches)

- `backend/app/services/providers/schemas.py` — extend `ExtractionItem` (brand, variant, size, barcode, transcript ref, care, nutrition, category-proposed) + strict unknowns rules. No core-table change.
- `backend/app/services/providers/prompts/extract-{food,medicine,cosmetics}-v3.md` — new frozen files (front matter `template_version`), v1/v2 bytes untouched.
- `backend/app/services/providers/reader.py` — `PROMPT_FILES` + `load_prompt` for v3, transcript-to-evidence write, split-first preserved, consent/ledger/candidate flow unchanged.
- `backend/eval/corpus/sg079/*` + `backend/eval/run.py` — extended-schema corpus (fail-then-pass), v1 metrics reproduced identical.
- `backend/app/models/enrich_snapshot.py` (new) + migration — verbatim raw response rows (source id, query, body, version), never overwrites.
- `backend/app/services/enrich/*` (new) — fetch-only service (barcode/name query → snapshot → map to `source_type=web:<source>` candidates); per-press cap; identifiers-only.
- `backend/app/api/v1/enrich.py` (new) + `backend/app/services/candidates.py` — manual trigger, conflict rule (label-photo wins label-visible, web fills gaps, both visible with sources), existing per-field accept.
- `frontend/src/*` (Asset detail) — Enrich button per product + spend display; no new review UX.
- `backend/tests/test_sg079_*`, `test_sg080_*`, `test_sg081_*`, `test_sg082_*` — corpus + scripted-provider tests; one live leg only.

---

### Task 1 (SG-079): photo-ingest schema v3 — READY, needs nothing

**Files:**
- Modify: `backend/app/services/providers/schemas.py`
- Create: `backend/app/services/providers/prompts/extract-food-v3.md`, `extract-medicine-v3.md`, `extract-cosmetics-v3.md`
- Test: `backend/tests/test_sg079_v3_schema.py`, `backend/eval/corpus/sg079/*`

**Interfaces:**
- Consumes: `ExtractionOutput` / `extract_with_single_repair` (unchanged envelope).
- Produces: extended `ExtractionItem` fields — `brand, variant, size_text, barcode, category_proposed, transcript, storage, warnings, allergens, nutrition_per100g, nutrition_serving` (all nullable, transcribed-only, never inferred) + `unknowns` entries `items.<i>.<field>` (null-beside-unknown enforced).

- [ ] Step 1: Write failing schema tests (new fields accept transcribed values, reject inferred/fabricated values, unknowns-null rule, prose never parsed).
- [ ] Step 2: Run to verify they fail.
- [ ] Step 3: Extend `ExtractionItem` minimally + write frozen v3 prompt files (transcribe-only, category as proposed field, transcript = evidence-only verbatim).
- [ ] Step 4: Run new tests + full suite (green modulo 2 base decoder reds); v1/v2 bytes untouched verified by diff.
- [ ] Step 5: Commit (no deploy, $0, no migration).

### Task 2 (SG-080): photo-ingest pipeline — READY, needs nothing

**Files:**
- Modify: `backend/app/services/providers/reader.py`, `backend/app/services/candidates.py`, `backend/app/services/job_service.py` (as needed, enumerated in packet)
- Test: `backend/tests/test_sg080_ingest_pipeline.py`, extended corpus fail-then-pass via `backend/eval/run.py`

**Interfaces:**
- Consumes: Task 1 extended schema + v3 prompts.
- Produces: transcript stored as evidence (never a fact), split-first multi-item preserved, category as `proposed` candidate, consent gate + ledger + candidate flow unchanged, zero auto-accept.

- [ ] Step 1: Write failing pipeline tests (transcript lands as evidence, split-first, category proposed not accepted, corrections auditable).
- [ ] Step 2: Run to verify they fail.
- [ ] Step 3: Wire reader → evidence → candidates (minimal, no behavior change except wider schema).
- [ ] Step 4: Corpus fail-then-pass on extended schema; suite green; secret scan 0; at most ONE metered live leg here (G0-gated, ≤3 images, worst-case bound stated, SG-049/SG-066 precedent) — else $0 structural proof.
- [ ] Step 5: Commit (deploy rides a separate rider, owner-gated per G-K2).

### Task 3 (SG-081): Enrich fetch-only service + snapshots — BLOCKED on owner source research

**Gate:** no packet until owner names sources (source policy under separate research, per spec §7). No guessing, no placeholder source.

**Files (planned, not built until gate clears):**
- Create: `backend/app/models/enrich_snapshot.py` + migration, `backend/app/services/enrich/service.py`, `backend/app/api/v1/enrich.py`
- Test: `backend/tests/test_sg081_enrich_fetch.py` (scripted-provider fetch/mapping/snapshot rules)

**Interfaces:**
- Consumes: identifiers only (barcode/name) — never photos, never GPS.
- Produces: verbatim snapshot rows (source, query, raw body, version) → mapped proposed candidates (`source_type=web:<source>`); barcode-exact links identity, fuzzy as proposals; spend shown on button under per-press cap.

- [ ] Steps run only after D102 clears (sources named). Same TDD shape as Tasks 1–2.

### Task 4 (SG-082): Enrich review mapping — BLOCKED (rides Task 3)

**Files (planned):** `backend/app/services/candidates.py`, `frontend/src/*` (Enrich button + spend display), existing candidate UI only.
- Conflict: label-photo wins label-visible facts, web fills gaps; both stay visible with sources; versioned snapshots, manual refresh; corrections remembered per product. No new review UX.

### Task 5 (SG-083): deploy rider — owner-gated per G-K2

Rebuild + one recreate + verify (SG-067 shape): bundle hash differs, regressions 200, gate 401, alembic identical unless a migration shipped, DB byte-identical unless migration, $0 unless the single live leg rides here.

## Self-review (spec coverage)

- §1 property model → Tasks 1 + 3 (identity/codes/dates/quantity/category/transcript/care/nutrition + source/snapshot/review-state).
- §2 photo ingest → Tasks 1–2 (v3 frozen, transcript evidence, split-first, category proposed, consent/ledger/candidate unchanged, nothing auto-accepts).
- §3 Enrich service → Task 3 (manual button, barcode/name → verbatim snapshot → `web:<source>` proposals, exact-first/fuzzy-as-proposal, per-press cap, identifiers-only).
- §4 review lifecycle → Task 4 (existing candidate UI, label-wins-visible, versioned manual refresh, no new UX).
- §5 cost/privacy/safety → Global Constraints + per-task gates.
- §6 testing → per-task fail-then-pass + scripted-provider + at most one live leg + suites green + secret scan 0.
- Placeholders: none — Task 3/4 explicitly gated on owner source research, not TBD-built.
- Type consistency: `source_type=web:<source>` string, `unknowns` path `items.<i>.<field>`, snapshot rows append-only.
