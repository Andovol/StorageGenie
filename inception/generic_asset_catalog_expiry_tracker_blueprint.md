# Generic AI Asset Catalog — with Expiry & Validity Tracker Plugin
## Merged Product & Implementation Blueprint (v3)

**Status:** implementation-ready foundation
**Audience:** AI coding agent, software architect, product owner
**Primary goal:** Build a local-first, provider-flexible, generic asset catalog platform — capable of ingesting *any* physical or digital item via photo capture and AI extraction — with the Expiry & Validity Tracker as its first, flagship vertical plugin.

---

## 1. Product Identity & Scope

### 1.1 What this is

This is, first and foremost, a **generic AI-native asset catalog**: a camera-first system that turns photos and documents of physical or digital items into a searchable, evidence-backed catalog, regardless of category. The platform's core has no built-in concept of "expiry," "food," or "medicine" — those are properties introduced by plugins.

The **Expiry & Validity Tracker** is the first plugin built on this core, and the one driving the initial roadmap, but the platform is designed from the outset to support other domains later (equipment, documents, collectibles, tools) without core rework.

### 1.2 Initial deployment context

Personal, multi-user product. Users belong to households (a household is a shared inventory/catalog context, not a separate account type). Initial users: two people forming a single household. The data model supports multiple households and multiple plugins from the outset, even though only one household and one active plugin (Expiry Tracker) exist initially.

### 1.3 Core Product Principles

- **Evidence before inference.** Original images, documents, OCR regions, barcode reads, and model outputs are immutable evidence. AI-generated fields are hypotheses (assertions) until accepted.
- **Generic core, vertical plugins.** The core represents arbitrary items without requiring domain-specific tables. All expiry-tracking logic (categories, notification tiers, dosage pacing, opened-date tracking) lives in the Expiry Tracker plugin, not the core schema.
- **Local-first by default.** Runs on SQLite and local disk for a single household; the same boundaries permit a future multi-household/remote deployment with PostgreSQL and object storage.
- **Provider-flexible AI.** No domain logic, prompt template, or persistence layer depends directly on a single LLM/vision-model provider.
- **Human-in-the-loop by design.** Review is an explicit state transition with clear confidence and evidence — not a fallback bolted on afterward.
- **Idempotent ingestion.** Retrying the same source input must not create duplicate records.
- **Deterministic operations around nondeterministic AI.** Explicit manifests, jobs, validation, content hashes, versioned prompts, and audit events wrap every AI call.
- **Privacy-aware.** Personal images, receipts, medicine photos, and identifying documents are sensitive. Keep data local unless a provider is explicitly configured otherwise.
- **Not every asset has an expiry.** The core `asset` entity is domain-neutral — clothing, tools, and documents may never expire. Expiry-related fields (expiry date, date type, opened-date) are plugin-scoped attributes on the asset, not universal core fields.
- **Guardrails start permissive and tighten with evidence.** Health/dosage-related AI suggestions (Expiry Tracker plugin, medicine category) begin with no hardcoded restrictions in the MVP. Constraints are added incrementally as real usage reveals where AI suggestions are unreliable or risky — this is a deliberate, logged process, not an oversight (see Section 11).

### 1.4 Non-Goals

- Autonomous purchasing, selling, disposal, or external publishing.
- Declaring safety, legal, medical, electrical, or fitment compliance from an image alone, without user confirmation.
- Perfect object recognition in cluttered scenes.
- Full inventory accounting, warehouse optimization, or ERP replacement.
- A native mobile app; responsive web capture is sufficient initially.
- Image generation as a core requirement (optional presentation plugin only, later).
- Enforcing an expiry date on categories/assets that don't logically have one (e.g., clothing, tools, most documents).

---

## 2. Target Outcomes

### 2.1 MVP user journeys (generic core)

**A. Capture an item.** User creates an import job (photos, optionally documents/barcodes). System normalizes files, computes hashes, stores evidence. AI proposes candidate asset records (category, attributes, confidence). User reviews and accepts, edits, merges, splits, holds, or rejects.

**B. Find an item.** Search by text, tags, category, location, brand, identifier, status, date, or similarity. Results always show verification level and evidence for critical fields.

**C. Track an item lifecycle.** Record events: acquired, installed, inspected, loaned, moved, maintained, consumed, sold, retired, disposed. Events retain timestamps, evidence, notes, quantities/costs.

**D. Add structured evidence.** Scan a barcode, upload a receipt/manual, or photograph a label/plate. System extracts candidate identifiers, links after approval.

### 2.2 MVP user journeys (Expiry Tracker plugin, layered on the above)

**E. Capture a perishable/limited-validity item.** Same capture flow as (A), but the plugin attempts to extract an expiry-relevant date. If the AI cannot find or confidently read a date, the field is left as `unknown` and the user is prompted to enter it manually — the system never fabricates a date. Products with no applicable expiry concept (as determined by category) simply skip this field entirely.

**F. Get notified before expiry.** Category-specific tiered reminders, once the asset has a resolved expiry-relevant date.

**G. Get consumption guidance.** Daily Planning Agent proposes pacing/usage plans for assets nearing expiry.

**H. Chat about a category.** Category-scoped conversational agent answers questions about owned items in that domain.

### 2.3 Success criteria

| Metric | MVP target | Notes |
|---|---:|---|
| Time to first accepted asset | under 90 seconds | Excluding external AI provider latency |
| Manual fields required per basic item | 0–3 | User corrects only what AI cannot determine |
| Duplicate prevention | 100% for identical files | Content hash is deterministic |
| Critical-field provenance | 100% | Identifier, category, expiry (if applicable), and lifecycle facts carry evidence or explicit user assertion |
| Asset search latency | under 300 ms | Local catalog up to ~10,000 assets |
| Failed job recoverability | 100% | Retry resumes safely without corrupting catalog data |
| Expiry-date extraction accuracy | ~90%+ under good capture conditions | Below threshold or no date found → mandatory manual entry, never a guessed value |
| Health-action safety | zero unconfirmed health-related auto-actions | Hard pass/fail; applies regardless of guardrail relaxation stage (Section 11) |

---

## 3. System Architecture

### 3.1 Logical architecture

```text
Responsive web UI / API clients
            |
            v
        Application API
            |
   +--------+---------+-------------------+
   |                  |                   |
   v                  v                   v
Catalog service   Job orchestration    Search service
   |                  |                   |
   |             AI provider gateway   FTS / vector index
   |                  |
   v                  v
Relational DB     Evidence storage
SQLite/Postgres   local FS / S3-compatible storage

Plugin layer (e.g. Expiry Tracker):
   - Category taxonomy & behavior profiles
   - Notification engine
   - Daily Planning Agent
   - Category Chat Agents
   - Analytics Insight Agent
```

The plugin layer sits above the generic core and consumes its services (catalog, job orchestration, AI provider gateway) rather than duplicating them.

### 3.2 Recommended stack (recommendation only, not mandated)

| Concern | Suggested MVP choice | Production evolution | Rationale |
|---|---|---|---|
| Web UI | React + TypeScript + Vite | Same | Matches existing skills; fast iteration |
| API | FastAPI + Python | FastAPI workers or separate services | Strong typing via Pydantic, good AI/image ecosystem |
| Database | SQLite (WAL) | PostgreSQL | Single/two-user simplicity; relational integrity from day one |
| ORM/migrations | SQLAlchemy + Alembic | Same | Explicit schema, portable migrations |
| Asset storage | Local filesystem outside web root | S3/MinIO | Cheap, privacy-friendly initially |
| Job execution | Durable job table + worker process | Redis + Celery/Arq, or Temporal | Avoid infra until concurrency requires it |
| Image processing | Pillow + OpenCV | Same | EXIF correction, thumbnails, cropping |
| OCR/barcodes | Pluggable adapters | Same | Deterministic extraction complements vision LLMs |
| Search | SQLite FTS5 | PostgreSQL FTS + pgvector | Start deterministic; add semantic search only when useful |
| Deployment | Docker Compose | Kubernetes only if justified | Operable on a VPS or local machine |

This table is a starting recommendation for the implementing architect, not a constraint — deviate if a better-justified choice emerges during implementation planning.

### 3.3 Architectural rules

- UI calls the API; it never reads the database or filesystem directly.
- The API creates jobs; it does not block on long AI/image operations in request handlers.
- Workers own enrichment execution; catalog writes happen through domain services, not direct table access.
- Original evidence is immutable. Derived files may be regenerated or deleted.
- Every AI call stores provider, model, prompt-template version, input hashes, output payload, cost/usage (if available), timestamps, and error state.
- Plugin code may propose facts (assertions) but cannot bypass validation or write core tables directly.
- Plugins register their own taxonomy, extension schema, and agents through a defined contract (Section 8); they do not fork or modify core entities.

---

## 4. Canonical Domain Model (Core — Generic, Non-Rigid)

### 4.1 Design approach

A stable generic core, extended by typed plugin payloads. Relational columns are used for frequently queried generic fields; JSON is used only for versioned, plugin-specific attributes. This structure is a strong default, not a rigid contract — the implementing architect may adapt field names, add indices, or split tables as real usage patterns emerge, provided the underlying provenance and evidence-immutability guarantees are preserved.

An `Asset` represents a real-world item or logically tracked unit. An `Observation` represents what the system saw in a specific input. An `Assertion` represents a field claim with a source, confidence, and approval state.

### 4.2 Core entities

| Entity | Purpose | Key fields |
|---|---|---|
| `asset` | Canonical tracked item | id, display_name, asset_type, status, quantity, unit, condition, household_id, created_at |
| `evidence` | Immutable source input | id, sha256, media_type, storage_key, original_filename, captured_at, source_kind |
| `observation` | Per-evidence extracted candidate | id, evidence_id, bounding_box, candidate_label, raw_model_output, confidence |
| `assertion` | Provenanced claim about an asset | id, asset_id, field_path, value_json, source_type, confidence, review_state |
| `identifier` | Barcode, MPN, serial, SKU, QR, external ID | id, asset_id, identifier_type, normalized_value, verification_state |
| `classification` | Category/tag assignment | asset_id, taxonomy_id, label, confidence, source |
| `asset_relation` | Typed relationship between assets | source_asset_id, relation_type, target_asset_id, metadata |
| `location` | Physical/logical location tree | id, parent_id, name, location_type |
| `asset_location` | Current or historical placement | asset_id, location_id, start_at, end_at, confidence |
| `lifecycle_event` | Auditable state/history event | asset_id, event_type, occurred_at, actor, notes, payload_json |
| `job` | Long-running orchestration record | id, job_type, state, idempotency_key, config_snapshot |
| `job_step` | Individual pipeline operation | job_id, step_name, state, attempts, input_refs, output_refs |
| `review_task` | Human decision work item | id, task_type, priority, subject_ref, proposed_change |
| `audit_event` | Immutable system trail | actor, action, entity_type, entity_id, before, after, timestamp |
| `household` | Shared catalog/inventory context | id, name, created_at |
| `user` | Individual account | id, household_id, display_name, email |

Households and users are treated as **core-level** concepts (not plugin-scoped) since multi-user sharing is a generic capability useful to any future plugin, not specific to expiry tracking.

### 4.3 Asset lifecycle states (core)

```text
DRAFT
  -> PENDING_REVIEW
  -> ACTIVE
  -> ARCHIVED
  -> DISPOSED

Any state -> REJECTED (candidate only; not a canonical asset)
Any active state -> MERGED (redirect to surviving asset)
```

The Expiry Tracker plugin adds its own sub-states on top of `ACTIVE` (e.g., Opened, Consumed, Expired, Recalled) as plugin-scoped status metadata — the core lifecycle is not overloaded with expiry-specific semantics.

### 4.4 Assertion model

All AI-extracted metadata enters through assertions:

```json
{
  "fieldPath": "expiry_date",
  "value": "2026-11-30",
  "sourceType": "ai_vision",
  "sourceEvidenceIds": ["ev_01J..."],
  "sourceObservationIds": ["ob_01J..."],
  "confidence": 0.74,
  "reviewState": "proposed",
  "model": {
    "provider": "configured-at-runtime",
    "modelId": "configured-at-runtime",
    "promptVersion": "extract-expiry-v1"
  }
}
```

Review states: `proposed` (machine-generated, unconfirmed) → `accepted` (user or trusted deterministic source confirmed) → `rejected` → `superseded` → `needs_evidence`.

If no expiry-relevant date is visible or extractable, the field is marked `needs_evidence` rather than populated with a guess, and a `review_task` is created prompting manual entry. Assets whose category has no applicable expiry concept simply have no `expiry_date` assertion at all — this is a normal, expected state, not an error.

### 4.5 Generic taxonomy (core level)

```text
item
├── equipment
├── component
├── consumable
├── product
├── document-linked item
├── collection item
├── container
└── unknown
```

This is a shallow, configurable starting taxonomy. Plugins layer domain-specific taxonomies (e.g., the Expiry Tracker's Food/Medicine/Cosmetics/Household-Chemicals/Documents categories) underneath or alongside this generic tree via the classification entity — see Section 9.1.

### 4.6 Extension model

A plugin registers: `plugin_id` + semantic version, JSON Schema for extension attributes, UI form metadata, extraction prompt fragments and output schema, deterministic validators, optional enrichers, and relationship types.

```json
{
  "pluginId": "expiry-tracker",
  "pluginVersion": "1.0.0",
  "attributes": {
    "expiryDateType": "best_before",
    "openedDate": "2026-08-01",
    "notificationTierOverride": null
  }
}
```

An extension cannot redefine or silently conflict with core fields such as `identifier`, `condition`, `location`, or `status`.

---

## 5. Ingestion Pipeline (Core)

### 5.1 Pipeline states

```text
CREATED
 -> VALIDATING_INPUT
 -> NORMALIZING
 -> EXTRACTING_DETERMINISTIC_SIGNALS
 -> ANALYZING_WITH_AI
 -> BUILDING_CANDIDATES
 -> DEDUPLICATING
 -> AWAITING_REVIEW
 -> COMMITTING
 -> COMPLETED

Any state -> FAILED | CANCELLED
FAILED -> RETRYING -> prior resumable state
```

### 5.2 Pipeline steps

1. **Receive input** — accept JPEG, PNG, WebP, HEIC/HEIF, TIFF, PDF; enforce size/type/decompression-bomb limits; compute SHA-256 before expensive work.
2. **Normalize and preserve** — store immutable original; correct EXIF orientation in a derived working file; generate normalized image/rendered pages; create thumbnails.
3. **Extract deterministic signals** — OCR text/bounding boxes, barcode/QR values, EXIF timestamps (privacy-gated), perceptual hash.
4. **Vision and semantic extraction** — detect candidate objects/regions; generate structured candidate descriptions constrained by JSON Schema; extract only visible properties; return confidence and uncertainty reasons per assertion. For the Expiry Tracker plugin specifically: attempt expiry-date extraction using the plugin's prompt fragment; if no date is visible/legible, return `needs_evidence` rather than a guess.
5. **Candidate formation** — create asset candidates linked to observations; split multi-object scenes only where boundaries are unambiguous; require manual split otherwise.
6. **Deduplication** — exact hash (reject/link duplicate evidence), perceptual hash (propose similar records), identifier exact match (review task, never auto-merge serialized items), semantic similarity (advisory only).
7. **Policy and confidence gating** — auto-accept only low-risk fields under configurable thresholds; route identifiers, price, safety-related attributes, expiry dates, and condition claims to review by default.
8. **Review and commit** — user accepts/edits/rejects candidates; create asset, assertions, evidence links, initial location, and lifecycle event atomically.

### 5.3 Quality gates

| Gate | Deterministic check | On failure |
|---|---|---|
| Original preservation | SHA-256 and storage existence | Fail job; never continue |
| Normalization | Decodable media, correct orientation, valid dimensions | Quarantine unsupported/damaged input |
| OCR/barcode | Syntax and checksum where standards support it | Store as low-confidence observation, not an identifier |
| AI output | Valid JSON Schema | Retry with repair prompt once; then fail step |
| Expiry-date extraction | Plausible date format/range | If absent or implausible, mark `needs_evidence`; never store a guessed date |
| Duplicate candidate | Exact hash / identifier collision policy | Create review task |
| Commit | DB constraints plus audit write | Roll back transaction |

---

## 6. AI Provider Abstraction

### 6.1 Provider interfaces

```python
class VisionExtractionProvider(Protocol):
    async def extract_items(self, request: VisionExtractionRequest) -> VisionExtractionResult: ...

class OcrProvider(Protocol):
    async def extract_text(self, request: OcrRequest) -> OcrResult: ...

class EmbeddingProvider(Protocol):
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResult: ...

class WebEnrichmentProvider(Protocol):
    async def search_and_summarize(self, request: EnrichmentRequest) -> EnrichmentResult: ...
```

Each result includes normalized output, raw provider payload, request ID, usage/cost, model ID, and latency.

### 6.2 Provider router

Routing policy is configuration-driven (provider, fallback, local fallback, JSON-schema strictness, per-job cost budget, retryable errors). Do not route on nominal model quality alone — measure structured-output validity, extraction agreement, latency, cost, and human-correction rate against a private evaluation set.

### 6.3 Prompt and schema discipline

- Store prompts as versioned files/packages.
- Prompts must require source-grounded output and an explicit `unknowns` array.
- Use JSON Schema/Pydantic for every machine-readable response; never parse free-form prose into production records.
- Every prompt change increments its version, traceable from every assertion it produced.
- Provider-neutral system instruction: **do not infer invisible identifiers, technical specifications, compatibility, safety status, provenance, condition, or expiry dates beyond visible evidence.**

### 6.4 Web enrichment grounding

Any product information sourced from the web (ingredients, allergens, dosage guidance, recall status, general usage information) must carry a retrievable source reference stored alongside the assertion. Enrichment must be grounded in retrieved sources, not generated from the model's unverified training knowledge; absence of a reliable source must be surfaced as "unverified," not silently omitted or guessed.

---

## 7. API Specification (Core)

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/v1/imports` | Create an import job and upload/attach evidence |
| `GET` | `/v1/imports/{job_id}` | Read job state, candidates, errors, progress |
| `POST` | `/v1/imports/{job_id}/retry` | Retry failed resumable steps |
| `POST` | `/v1/candidates/{candidate_id}/decision` | Accept, edit, split, merge, hold, or reject |
| `GET` | `/v1/assets` | Filtered and paginated catalog search |
| `POST` | `/v1/assets` | Manually create an asset |
| `GET` | `/v1/assets/{asset_id}` | Asset detail with evidence and assertion provenance |
| `PATCH` | `/v1/assets/{asset_id}` | Explicit user updates through assertions |
| `POST` | `/v1/assets/{asset_id}/events` | Append lifecycle event |
| `POST` | `/v1/assets/{asset_id}/evidence` | Attach new evidence |
| `GET` | `/v1/review-tasks` | Review queue |
| `POST` | `/v1/review-tasks/{task_id}/resolve` | Resolve a review task |
| `GET` | `/v1/export` | Export catalog/evidence manifest |
| `GET` | `/v1/health` | Process/dependency health |

Plugin-specific endpoints (notification rules, planning-agent suggestions, category chat) are additive and namespaced (e.g., `/v1/plugins/expiry-tracker/...`), never overriding core routes.

API-wide requirements: opaque UUIDv7/ULID identifiers; idempotency keys on mutable requests; cursor pagination for lists; RFC 9457-style problem details for errors; `provenance`/`confidence` fields on relevant views; optimistic concurrency via version/ETag.

---

## 8. Plugin Contract

A plugin is the mechanism by which any vertical domain (Expiry Tracker, and future domains) extends the generic core without modifying it. A plugin defines:

- A category taxonomy (Section 9.1) mapped to `classification` records.
- A behavior profile per category: notification defaults, whether opened-date tracking applies, whether disposal guidance applies, which chat agent (if any) handles it.
- Extension attribute schema (JSON Schema), validated on write.
- Prompt fragments for AI extraction/enrichment specific to the domain.
- Optional scheduled agents (e.g., Daily Planning Agent) and conversational agents (Category Chat Agents), registered separately from the core ingestion pipeline.
- UI form metadata for plugin-specific fields.

Plugins cannot redefine core fields or bypass assertion/review-state validation.

---

## 9. Expiry & Validity Tracker Plugin

### 9.1 Category Taxonomy (plugin-level)

| Priority | Category | Notification behavior | Notes |
|---|---|---|---|
| 1 | Food & beverages | Tiered (30/7/1 day defaults) | Highest interaction frequency; build first |
| 2 | Medicine/pharma | Tiered, shorter windows | Dosage-pacing plugin logic applies (Section 9.4); build second |
| 3 | Cosmetics/personal care | Opened-date secondary countdown | Requires opened-date mechanic |
| 4 | Household chemicals | Basic expiry only | Minimal special logic |
| 5 | Documents/other | Long-lead windows (60/30 day) | No consumption/expiry concept in the strict sense; reminder-only |
| — | Non-perishable (clothing, tools, etc.) | No expiry field applicable | Asset exists in the generic core with no expiry assertion at all |

### 9.2 Additional Taxonomies (plugin-level)

- **Expiry/date type**: expiry date, best-before, use-by, manufacture date (+ shelf-life offset), period-after-opening (PAO), batch/lot code.
- **Storage location**: fridge, freezer, pantry, bathroom cabinet, medicine cabinet, garage/utility, custom (may reuse core `location` entity rather than a separate list).
- **Notification urgency tier**: Critical, Urgent, Upcoming, Long-lead — configurable per category/user.
- **Unit of measure**: piece/unit, ml/L, g/kg, dose/tablet, application — supports partial-consumption and dosage-pacing calculations.

### 9.3 Expiry Date Handling Rule (explicit, non-negotiable)

If AI extraction cannot find or confidently read an expiry-relevant date, the field is left `needs_evidence` and the user must enter it manually before the asset is treated as having a resolved expiry state. Categories with no applicable expiry concept (clothing, tools, most documents) simply have no expiry assertion — the system must never force a date onto a category that doesn't logically need one, and must never fabricate a plausible-sounding date when none is visible.

### 9.4 Plugin-Level Agents

Ingestion and Enrichment reuse the core pipeline (Sections 5-6) with plugin-specific prompt fragments. The following are additional, plugin-scoped agents with no core-level equivalent:

**Daily Planning Agent** — runs on a schedule, reviews household inventory, proposes consumption plans (dosage pacing for medicine/supplements, recipe suggestions for near-expiry food, usage pacing for opened cosmetics). All proposals require explicit user confirmation before being treated as accepted; no auto-scheduling or auto-execution of any action.

**Category Chat Agents** — conversational, scoped per category. Launch with Food and Medicine agents; Cosmetics agent follows once opened-date tracking is stable; Household/Documents use a generic fallback agent.

**Analytics Insight Agent** — generates natural-language summaries over the household's own structured data (waste trends, category breakdowns, adherence patterns); no external web access; fully grounded in first-party data.

---

## 10. Guardrail Rollout Strategy (Health/Dosage Suggestions)

This project deliberately starts with **no hardcoded restrictions** on the Daily Planning Agent's or Medicine Chat Agent's dosage-related suggestions, and adds constraints incrementally as real usage with two actual users (household members) reveals where AI suggestions are unreliable or risky. This is a conscious, staged approach — not an oversight — and should be tracked explicitly:

- **Stage 0 (MVP)**: no hardcoded dosage guardrails. Suggestions are generated freely; human-in-the-loop confirmation (Section 1.3) remains mandatory for all health-related proposals regardless of stage.
- **Stage 1**: after initial real usage, review logged suggestions and user corrections; identify patterns of unreliable or risky suggestions (e.g., suggesting doses beyond label maximums).
- **Stage 2**: introduce targeted constraints only where Stage 1 evidence shows a real problem (e.g., "never suggest exceeding label-stated maximum dose") rather than pre-emptively restricting all dosage logic.
- **Ongoing**: log every guardrail addition as a decision record (Section 13) with the triggering evidence, so the rule set remains evidence-driven rather than speculative.

Regardless of stage, the hard, non-negotiable constraints from Section 1.3 (human confirmation required, no autonomous execution of health actions) apply from day one and are never subject to relaxation.

---

## 11. UX Specification (Core + Plugin)

### 11.1 Main screens (core)

1. **Inbox** — pending imports, processing progress, failed jobs, review tasks.
2. **Capture** — drag/drop, camera capture, paste, barcode scan, document attach.
3. **Review workspace** — source image, candidate fields, evidence/provenance, duplicate suggestions.
4. **Catalog** — grid/table, filters, facets, bulk actions, saved searches.
5. **Asset detail** — canonical fields, evidence timeline, identifiers, lifecycle, locations, relationships, audit history.
6. **Settings** — providers, privacy, storage, taxonomy, plugins, confidence thresholds, export/backup.

### 11.2 Plugin-added screens (Expiry Tracker)

7. **Expiry dashboard** — urgency-sorted view (expired/this week/this month/safe), category filters.
8. **Planning suggestions** — Daily Planning Agent proposals, pending confirmation.
9. **Category chat** — conversational interface scoped per category.
10. **Analytics** — waste trends, category breakdowns, AI-generated summaries.

### 11.3 Review workspace behaviors

- User must see source evidence while accepting any AI suggestion.
- Show field-level confidence and extraction source.
- `Unknown` is a valid, easy choice — never force a guessed field, especially for expiry dates.
- Keyboard-centric review: accept, reject, previous/next, merge, split, crop adjustment.
- Batch accept only for safe, non-critical fields.

---

## 12. Security, Privacy, and Data Integrity

### 12.1 Threat model priorities

- Exposure of personal photos, receipts, medicine photos, and identifying documents.
- API-key leakage to browser clients or logs.
- Prompt injection embedded in OCR text or uploaded documents.
- Malicious file uploads and image-parser attacks.
- Incorrect AI inference treated as fact (especially expiry dates and dosage figures).
- Silent corruption/duplication after retries or concurrent edits.

### 12.2 Mandatory controls

- Provider keys only in backend/worker environment; never exposed to frontend.
- Original media stored outside web root; served via authenticated API URLs.
- EXIF GPS stripped or gated by configuration.
- OCR/document text treated as untrusted data, never as instruction content.
- Media-type verification by file signature, size limits, isolated conversion processes.
- Full audit record of human and automated writes.
- Backups cover DB plus evidence manifest together.

### 12.3 Safety policy

The system may suggest. It must not autonomously certify: compatibility/fitment, operational safety, authenticity, medical suitability, regulatory compliance, expiry/lot status, monetary valuation, or ownership/provenance — these require user confirmation or explicitly attached documentary evidence. Dosage-*pacing arithmetic* (days remaining × label-stated dose = feasibility) is an explicit, scoped exception: it is deterministic math on user-confirmed label data, not a medical suitability claim, and is permitted under the Guardrail Rollout Strategy (Section 10), always subject to mandatory human confirmation.

---

## 13. Testing and Evaluation

| Layer | Tests |
|---|---|
| Domain | State transitions, precedence rules, duplicate rules, audit invariants |
| API | Auth, validation, idempotency, pagination, concurrency, error contracts |
| Worker | Resumability, retries, exactly-once commit, provider failure handling |
| Media | EXIF rotation, unsupported/corrupted input, thumbnails, crop bounds, hashing |
| UI | Review decisions, evidence visibility, accessibility, keyboard workflow |
| Plugin | Category taxonomy resolution, behavior-profile application, expiry-date-missing fallback |
| Agent | Planning-agent proposal correctness against label data, chat-agent category scoping |
| Evaluation | Curated image/document set with field accuracy and correction-rate tracking |

Build a private evaluation set before optimizing prompts, covering: visible vs. document-backed vs. unknowable fields, expected `unknown`/`needs_evidence` cases, duplicate relationships, and difficult examples (clutter, glare, partial labels, non-Latin text).

---

## 14. Delivery Plan (Interleaved Core + Plugin)

### Phase 0 — Foundation (generic core, manual only)

- Monorepo, Docker Compose, CI, linting, migrations, local data directories.
- Core schema: asset, evidence, job, assertion, audit_event, review_task, household, user.
- Evidence upload, SHA-256, normalization, thumbnails, basic asset CRUD.
- Catalog and asset-detail screens with manually created records.

**Exit condition:** manually catalog an item, attach source photos, search it, export a consistent backup.

### Phase 1 — Deterministic import + Expiry Tracker skeleton

- Job engine with durable step state and retry.
- OCR, barcode/QR scanning, EXIF extraction, duplicate detection.
- Expiry Tracker plugin registered: category taxonomy, behavior-profile config, manual expiry-date entry flow.
- Import inbox and review workspace.

**Exit condition:** ingest a mixed folder of files, resume after failure, request human review — including manual expiry-date entry — without any LLM dependency yet.

### Phase 2 — AI extraction (Food + Medicine categories)

- Provider gateway and one cloud vision adapter.
- Strict structured extraction, candidate formation, assertion provenance, confidence gates.
- Expiry-date extraction prompt fragment; `needs_evidence` fallback wired to manual entry.
- Baseline evaluation corpus focused on Food and Medicine.

**Exit condition:** AI proposes candidates including expiry dates for Food/Medicine; corrections are auditable; a working expiry tracker is usable end-to-end for the two initial users.

### Phase 3 — Agents and remaining categories

- Web Enrichment Agent (grounded, source-attributed product pages).
- Daily Planning Agent (Stage 0 guardrails per Section 10).
- Food and Medicine Category Chat Agents.
- Cosmetics category + opened-date tracking.

**Exit condition:** daily planning suggestions and category chat are functional; guardrail rollout tracking (Section 10) is active.

### Phase 4 — Provider flexibility, extensibility, analytics

- Second cloud provider + optional local provider adapter; router, fallback, budgets.
- Taxonomy editor, plugin contract hardening, FTS, advanced filters, asset relations.
- Analytics Insight Agent; remaining categories (Household chemicals, Documents).

**Exit condition:** changing providers needs configuration, not code; a new plugin domain can be defined without modifying core tables.

### Phase 5 — Hardening (ongoing)

- Privacy controls, backup/restore, export/import, observability, regression evaluations.
- PostgreSQL/S3 deployment profile only when multi-household scale makes SQLite/local disk inadequate.

---

## 15. Governance

### 15.1 Agent roles (build process)

| Role | Responsibility | Must not do |
|---|---|---|
| Architect agent | ADRs, boundaries, schemas, backlog slicing, review of major PRs | Write broad untested features directly |
| Coding agent | Implements one bounded task with tests and docs | Change architecture or dependencies without an ADR |
| QA agent | Runs tests, inspects migrations/API contracts, exercises failure paths | Approve its own implementation |
| Evaluation agent | Runs extraction corpus, compares provider metrics, reports regressions | Modify ground truth to make metrics look better |
| Security reviewer | Reviews uploads, secrets, prompt injection, access paths | Sign off on skipped threat controls |

### 15.2 Task specification template

```markdown
# Task: <short outcome>

## Context
<Links to ADR, schema, endpoint, affected user journey>

## Scope
- In scope:
- Explicitly out of scope:

## Acceptance criteria
- [ ]

## Contracts
- API:
- Database migration:
- Events/jobs:
- Error behavior:

## Tests
- Unit:
- Integration:
- Manual UX check:

## Constraints
- Preserve evidence immutability.
- Do not bypass provider interfaces.
- Do not add undocumented dependencies.
- Never fabricate an expiry date; unknown must remain unknown until manually entered.

## Deliverables
- Code
- Tests
- Migration
- Documentation / ADR update if needed
```

### 15.3 Architecture Decision Records to create before implementation expands

1. **ADR-001**: Local-first storage and migration path (SQLite+FS now, Postgres+S3 later).
2. **ADR-002**: Evidence and provenance model (immutable evidence, observations, assertions, precedence, audit).
3. **ADR-003**: Job orchestration (durable DB job state, retry semantics, future queue/workflow engine).
4. **ADR-004**: AI provider abstraction (capability interfaces, raw response retention, routing/fallback).
5. **ADR-005**: Generic core and plugin contract (taxonomy, extensions, schema validation, plugin isolation).
6. **ADR-006**: Duplicate policy (exact, perceptual, identifier, semantic matching; merge rules).
7. **ADR-007**: Privacy and external-AI data handling (retention, EXIF, provider consent, secrets, backup encryption).
8. **ADR-008**: Search architecture (deterministic FTS first; criterion for semantic/vector search).
9. **ADR-009**: Expiry Tracker category/behavior-profile design and notification tiering.
10. **ADR-010**: Guardrail rollout tracking for health/dosage-related AI suggestions (Section 10) — log of triggering evidence for every constraint added post-MVP.

### 15.4 Guardrails for coding agents

- Read architecture docs and active ADRs before editing.
- Work in small vertical slices.
- Never fabricate API responses, test results, migrations, benchmark figures, or provider capabilities.
- Do not delete or rewrite original evidence during processing.
- Do not auto-commit generated data, user media, API keys, database files, or `.env` files.
- When a requirement is ambiguous, create a decision record or ask rather than assuming.
- Before claiming completion, run the specified tests and report actual output.

---

## 16. Risks and Mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Generic scope becomes abstract infrastructure | No usable product reaches the two initial users | Interleave core phases with Expiry Tracker MVP (Section 14); delay plugin marketplace and complex workflows |
| AI hallucinates expiry dates or identifiers | Bad data destroys trust; wrong expiry dates create real safety/waste consequences | Field-level provenance, strict `needs_evidence` fallback, confidence gates, mandatory manual entry when unknown |
| Relaxed guardrails (Section 10) allow a risky dosage suggestion before Stage 2 constraints exist | Health-related suggestion errors have real consequences for two actual household users | Human-in-the-loop confirmation is non-negotiable regardless of guardrail stage; track every incident toward Stage 1/2 rule creation |
| Vendor lock-in or silent model regressions | Provider models/pricing change over time | Provider gateway, evaluation corpus, prompt/version logging, budget controls |
| JSON becomes an unqueryable junk drawer | Generic products tempt storing everything as blobs | Relational core, JSON Schema extensions, indexed promoted fields |
| Jobs fail halfway | Uploads and AI calls are unreliable | Durable steps, idempotency keys, content hashes, atomic commit stage |
| Duplicate explosion | Multiple photos of the same real object are common | Exact/perceptual hashes plus reviewable merge candidates |
| Privacy breach via cloud inference | Photos of medicine/personal items may be sensitive | Explicit provider consent, redaction options, local providers, storage controls |
| Premature microservices | Slower iteration, operational burden | Modular monolith with worker boundary; split only under evidence of need |

---

## 17. First Implementation Prompt

```text
You are implementing Phase 0 of the Generic AI Asset Catalog (with the Expiry & Validity Tracker as the first plugin).

Read the merged blueprint before coding. Build only the local-first generic foundation:
- FastAPI backend and React/Vite frontend.
- SQLite database with Alembic migration for asset, evidence, assertion, job, review_task,
  audit_event, household, and user.
- Immutable local evidence storage outside the web root, SHA-256 hashing, thumbnail generation.
- Manual asset creation and asset detail endpoints/UI, scoped to a household.
- Asset detail must display linked evidence and all assertion provenance.
- Unit and integration tests for upload hashing, database constraints, basic CRUD, audit events.

Do not implement LLM calls, OCR, barcode scanning, semantic search, image generation,
authentication, the Expiry Tracker plugin, or background workers yet.

Before modifying code, write an implementation plan document containing proposed files,
API contracts, schema decisions, test plan, and open questions. Then implement in small
commits. Report actual test commands and results at the end.
```
