# Google Product Taxonomy ingest — design (2026-09-21)

Status: APPROVED as S1–S5 (`D113`, owner quote "Both approved.").
Spec written after approval per the brainstorming gate; packet + plan follow on user review of this file.

## Decisions carried

| ID | Quote | Verdict |
|---|---|---|
| D110 | owner message m0011 (taxonomy URL + "categorize products ingested based on it") | Use `taxonomy-with-ids.en-US.txt` for ingest categorization |
| D111 | "D111 and D112 approved" | LAYERED — 6 expiry buckets stay behavior authority; Google `id+path+version` stored alongside `category_proposed`, both gated; out-of-scope kinds retained with `non_perishable` fallback |
| D112 | same quote | Resolver P1 — free-text propose + server-side resolve, deterministic scoring, top-level-or-null fallback |
| D113 | "Both approved." | S1–S5 approved as written |
| D114 | same quote | Queue holds: Phase 5 hardening D107 → Enrich D108 → taxonomy |

## Source facts (measured 2026-09-21, not inferred)

- URL `https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt` serves version `2021-09-21`: **5,596** lines, **482,896 B**, **21** top-level roots, **364** nodes under `412 - Food, Beverages & Tobacco`. Scratch copy at session temp only — never committed, never pasted into prompts or chat.
- Ingest today: `ExtractionItem.category_proposed` open-vocab slug, transcribed-only (`schemas.py:56`); frozen `extract-*-v3.md` per `food|medicine|cosmetics` (`reader.py:54-58`); the one gated proposal via `GET /v1/candidates` (`candidates.py:40,56,303`); behavior from the 6-category descriptor (`descriptor.py:134-177`) served by `GET /v1/taxonomy` and read by analytics + inspector from the same registry.

## Goals / non-goals

- GOAL: every ingested item carries a version-stamped Google kind (`id` + full path) resolved deterministically, gated for review, with zero added model cost.
- NON-GOAL: replacing the 6 expiry buckets; catalog filtering on Google kind (deferred); stuffing any of the 5,596 lines into a vision prompt.

## S1 — Architecture

Kind and behavior are orthogonal axes. Expiry buckets answer "how do we treat it" (tiers, chat mode); Google type answers "what is it". Both are stored per item; only the expiry bucket drives behavior.

- Taxonomy vendored as DATA: `backend/app/data/google_taxonomy/2021-09-21.txt` byte-identical to source, plus a parsed index (`id`, full path, normalized tokens) built at startup or lazily. A taxonomy update is a new vendored file + version stamp — never a prompt edit, never a migration of old rows (old rows self-describe via their stamp).
- One pure resolver module (e.g. `services/google_taxonomy.py`), offline-testable, no I/O: normalize (trim, collapse whitespace, casefold) → exact full-path match accepts at 1.0 → else token-set top-k=5, accept top1 iff score `≥0.6` with margin `(top1−top2) ≥0.15` (Enrich-research precedent) → else `UNCLEAR` with top-k surfaced for the reviewer. Every outcome stamps `taxonomy_version`, including `UNCLEAR`.
- One explicit subtree→bucket map as DATA (longest-prefix match): `Food, Beverages & Tobacco` → `food_beverages`; `Health & Beauty` → `cosmetics_personal_care` default with pharma-subtree exceptions → `medicine_pharma` (exception prefixes enumerated by the packet from the vendored file, quoted per M19 — the spec fixes the mechanism, the packet owns the rows); every other top-level → `non_perishable`. Unmapped depth falls back to its top-level default; unknown top-level → uncategorized, never guessed.

## S2 — Components

- Schema: one new nullable free-text field `google_type_proposed` on `ExtractionItem`, transcribed-only, null when absent/illegible with the matching `unknowns` entry, joining the existing non-blank-when-present validator list. Resolved `id/path/version` triple is produced downstream (candidate/`ai_item` home fixed at plan time); the triple is always stored together and nullable together.
- Prompts v4: `extract-*-v4.md` adds ~10 lines; v3 files stay byte-identical as rollback reference (SG-079/SG-080 precedent). Added block (packets quote this file, never chat):

```
## Product type (Google taxonomy)
Propose `google_type_proposed` as the verbatim full category path from the Google
Product Taxonomy, a top-level-only path when unsure, or null when illegible/absent
(plus the matching `unknowns` entry). Never invent numeric IDs or paths.
```

- Candidates: resolved type rides `GET /v1/candidates` as gated fields beside `category_proposed`; never auto-accepted at any confidence (SG-080 G3 precedent).
- Analytics/UI: `GET /v1/taxonomy` unchanged. Catalog filter on Google kind is deferred — store + gate first.

## S3 — Data flow (one pass, no extra provider call)

Photo → v4 extract (free-text Google path + `category_proposed`, nulls allowed) → resolver normalizes to `id+path+version` or `UNCLEAR` → subtree map suggests the expiry bucket → candidates gated → reviewer accepts → `ai_items` + Google triple. Model-cost delta is $0 by construction.

## S4 — Error handling

| Case | Behavior |
|---|---|
| Null/blank proposal | Existing `unknowns` / `needs_evidence` path, unchanged |
| Sub-threshold resolve | `UNCLEAR` with top-k shown; reviewer picks or rejects; nothing auto-maps |
| Version drift | Rows self-describe via `taxonomy_version`; mixed-version reads are normal |
| Out-of-scope kind (`Apparel`, `Electronics`, …) | Type retained, bucket `non_perishable` (D111) |
| Map miss at depth | Falls back to top-level default; unlisted top-level → uncategorized |

## S5 — Testing (offline-first, SG-079/SG-080 shape)

Fixtures through the real resolver: exact-match pins, threshold/margin pins (accept just above, `UNCLEAR` just below), version-stamp pins, subtree-map pins incl. fallback, mutation non-vacuity (each pin fails when the mechanism is disabled). Gates: suite green + base reds stash-reproved, ruff clean, mypy delta 0, secret scan 0, $0 offline; one capped live leg (`≤$0.015` precedent) only if a slice needs it.

## Rollout

After D107 → D108 (D114). Staged shape (IDs assigned at plan time, not here): (1) vendored data + resolver + map; (2) schema field + v4 prompts; (3) candidates gating + offline pins; (4) verify rider. No deploy slice until a rider packet names it.

## Risks

Stale source (2021-09-21) → version stamp + vendored-update rule contains it. Fuzzy mis-resolve → threshold + margin + never-auto-map contains it. Map maintenance → map is data with pins, reviewed like prompts.

## Spec self-review (2026-09-21)

Placeholder scan (five common marker tokens) — clean. Consistency: layered kind-vs-behavior stated identically in S1, S2, S4, rollout. Scope: one stage, slice IDs deliberately unassigned (plan-time). Ambiguity: thresholds exact (`≥0.6`, `≥0.15`, top-k=5), prompt block quoted verbatim, pharma exceptions assigned to the packet with the quoting rule named.
