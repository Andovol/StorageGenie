# Google Taxonomy Ingest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the Google Product Taxonomy (2021-09-21, 5,596 nodes) into photo ingest as a layered, version-stamped, review-gated kind axis with $0 added model cost.

**Architecture:** Vision prompts propose a verbatim Google path (or top-level-only, or null); a pure server-side resolver normalizes it to `id+path+version` with deterministic accept gates; an explicit subtree→bucket map suggests the expiry bucket; resolved types ride candidates gated, never auto-accepted.

**Tech Stack:** Python / Pydantic v2 (schemas), stdlib matching (resolver — no new dependency), frozen Markdown prompts, pytest + ruff + mypy.

## Global Constraints

- Taxonomy source version `2021-09-21`: **5,596** lines, **482,896 B**, **21** top-level roots.
- Resolver accept: score `≥0.6`, margin `(top1−top2) ≥0.15`, top-k `5`; below bar is `UNCLEAR`, never auto-mapped.
- v1/v2/v3 prompt files stay byte-identical (rollback reference).
- Suite green + base reds stash-reproved, ruff clean, mypy delta 0, secret scan 0, `$0` offline; any live leg capped `≤$0.015`.
- The 6 expiry buckets stay the behavior authority; out-of-scope kinds retain type with `non_perishable`.
- Spec: `docs/superpowers/specs/2026-09-21-google-taxonomy-design.md` (S1–S5 approved, D113).

---

### Task 1: Vendored data + resolver + subtree map (pure, offline, $0)

**Files:**
- Create: `backend/app/data/google_taxonomy/2021-09-21.txt` (byte-identical vendored copy)
- Create: `backend/app/services/google_taxonomy.py` (index, resolver, map)
- Test: `backend/tests/test_google_taxonomy.py`

**Interfaces:**
- Consumes: nothing (reads the vendored file only).
- Produces: `Resolution` (fields `status: str`, `google_type_id: str | None`, `google_type_path: str | None`, `taxonomy_version: str`, `score: float`, `margin: float`, `alternatives: list[tuple[str, str]]`); `resolve_google_type(proposal: str | None) -> Resolution`; `bucket_for(google_type_id: str | None, google_type_path: str | None) -> str`; `TAXONOMY_VERSION = "2021-09-21"`.

- [ ] **Step 1: Vendor the taxonomy file**

Run (workdir `backend`): download the URL to `app/data/google_taxonomy/2021-09-21.txt`, then verify: first line `# Google_Product_Taxonomy_Version: 2021-09-21`, size `482896` B, `5596` lines.
Expected: all three match; any mismatch is STOP-and-report, never a hand-edit.

- [ ] **Step 2: Write the failing tests**

```python
def test_exact_path_resolves_with_id_and_version():
    r = resolve_google_type("Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer")
    assert r.status == "resolved" and r.taxonomy_version == "2021-09-21" and r.google_type_id is not None

def test_below_threshold_is_unclear_never_mapped():
    r = resolve_google_type("vague paraphrase with no close node")
    assert r.status == "unclear" and r.google_type_id is None

def test_none_proposal_is_uncategorized():
    assert resolve_google_type(None).status == "uncategorized"

def test_food_subtree_maps_to_food_bucket():
    assert bucket_for("414", "Food, Beverages & Tobacco > Beverages") == "food_beverages"

def test_out_of_scope_retains_type_with_non_perishable():
    assert bucket_for("222", "Electronics") == "non_perishable"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_google_taxonomy.py -v` (workdir `backend`)
Expected: FAIL with import/attribute errors (module does not exist yet).

- [ ] **Step 4: Write minimal implementation**

```python
TAXONOMY_VERSION = "2021-09-21"
ACCEPT_SCORE = 0.6
ACCEPT_MARGIN = 0.15
TOP_K = 5

@dataclass(frozen=True)
class Resolution:
    status: str  # "resolved" | "unclear" | "uncategorized"
    google_type_id: str | None
    google_type_path: str | None
    taxonomy_version: str
    score: float
    margin: float
    alternatives: list[tuple[str, str]]

def resolve_google_type(proposal: str | None) -> Resolution: ...
def bucket_for(google_type_id: str | None, google_type_path: str | None) -> str: ...
```

Normalize by trim + collapse-whitespace + casefold; exact full-path match accepts at 1.0; else token-set top-5 with the accept gates; longest-prefix map match for buckets (`Food, Beverages & Tobacco` → `food_beverages`, `Health & Beauty` → `cosmetics_personal_care` default with pharma-prefix exceptions enumerated from the vendored file and quoted in the report, all other top-levels → `non_perishable`, unknown → `uncategorized`). No I/O outside the vendored file, no network, no clock.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_google_taxonomy.py -v` (workdir `backend`)
Expected: PASS, all 5+ tests.

- [ ] **Step 6: Run gates**

Run: `ruff check` and `mypy` deltas clean (workdir `backend`).
Expected: ruff clean, mypy delta 0.

- [ ] **Step 7: Commit**

```bash
git add backend/app/data/google_taxonomy/2021-09-21.txt backend/app/services/google_taxonomy.py backend/tests/test_google_taxonomy.py
git commit -m "feat: vendored Google taxonomy with pure resolver and bucket map"
```

**Out of scope:** schema changes, prompt changes, candidates wiring, any provider call.
**Deliverables:** version-pinned data + tested resolver + map.

### Task 2: Schema field + v4 prompts (transcribe-only, $0)

**Files:**
- Modify: `backend/app/services/providers/schemas.py` (add `google_type_proposed: str | None`, join the non-blank-when-present validator list)
- Create: `backend/app/services/providers/prompts/extract-food-v4.md`, `extract-medicine-v4.md`, `extract-cosmetics-v4.md` (v3 content + the spec's quoted 10-line block, front matter `template_version` bumped)
- Test: extend `backend/tests/test_google_taxonomy.py` (schema leg) — blank-when-present rejects `""`, `unknowns` entry `items.0.google_type_proposed` validates with null value

**Interfaces:**
- Consumes: Task 1 vocabulary only (field name `google_type_proposed`).
- Produces: `ExtractionItem.google_type_proposed`; v4 prompt files on disk (reader flip is Task 3).

- [ ] **Step 1: Write the failing schema tests**

```python
def test_blank_google_type_proposed_rejected():
    with pytest.raises(ValidationError):
        ExtractionItem(name="X", confidence=1.0, google_type_proposed="  ")
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_google_taxonomy.py -v` (workdir `backend`)
Expected: FAIL (`google_type_proposed` unexpected keyword).

- [ ] **Step 3: Implement** — add the field + validator entry; author the three v4 files (v3 files untouched, verified byte-identical with `git diff --stat` showing only the three new files).

- [ ] **Step 4: Run tests + gates**

Run: `python -m pytest tests/test_google_taxonomy.py -v`, `ruff check`, `mypy` (workdir `backend`)
Expected: PASS, ruff clean, mypy delta 0.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/providers/schemas.py backend/app/services/providers/prompts/extract-*-v4.md backend/tests/test_google_taxonomy.py
git commit -m "feat: google_type_proposed schema field and v4 prompts"
```

**Out of scope:** reader flip, candidates wiring, resolver calls in the pipeline.
**Deliverables:** schema + prompts ready, v3 preserved.

### Task 3: Pipeline wiring + gated candidates + pins (offline, $0)

**Files:**
- Modify: `backend/app/services/providers/reader.py` (`PROMPT_FILES` v3→v4 at runtime)
- Modify: `backend/app/services/candidates.py` (resolved triple rides the candidate as gated fields)
- Modify: pipeline step that builds proposals (call `resolve_google_type` + `bucket_for` per item; `UNCLEAR` surfaces top-k to the reviewer)
- Test: `backend/tests/test_google_taxonomy.py` (end-to-end offline legs: resolved item carries triple + version; unclear item gates with alternatives; nothing auto-accepts at threshold 0.0)

**Interfaces:**
- Consumes: Task 1 (`resolve_google_type`, `bucket_for`, `Resolution`) and Task 2 (`google_type_proposed`, v4 files).
- Produces: candidate fields `google_type_id`, `google_type_path`, `taxonomy_version` (gated, never auto-accepted).

- [ ] **Step 1: Write the failing wiring tests** (fake provider scripted with `google_type_proposed` set; assert triple on the candidate; scripted paraphrase asserting `unclear` + alternatives present + no auto-accept).

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_google_taxonomy.py -v` (workdir `backend`)
Expected: FAIL (no triple on candidates).

- [ ] **Step 3: Implement** — minimal wiring; v1/v2/v3 pins enumerated tree-wide and flipped exactly like SG-080 (injected-version self-consistency pair kept only if one exists and is reported).

- [ ] **Step 4: Full suite + gates**

Run: full backend suite, `ruff check`, `mypy`, secret grep-gate over the diff (`api_key|OPENCODE_API_KEY|Bearer|token` identifiers, SG-037 precedent) (workdir repo root for the gate, `backend` for the rest)
Expected: suite green except base reds stash-reproved; ruff clean; mypy delta 0; gate 0 real secret shapes.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/providers/reader.py backend/app/services/candidates.py backend/app/services/google_taxonomy.py backend/tests/test_google_taxonomy.py
git commit -m "feat: Google type resolution wired with gated candidates"
```

**Out of scope:** deploy, catalog filter UI, analytics changes, any live provider call.
**Deliverables:** wired pipeline, gated proposals, green suite.

### Task 4: Verify rider (bounded, deploy only if named)

**Files:** none unless the packet names a deploy (then the rider follows the SG-067/072/074/083 shape: one rebuild + one recreate + verify).

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: verify verdict (`GET /v1/health` exact ×6, `GET /v1/taxonomy` unchanged body, candidates gating live-proven or structurally proven with the reason stated).

- [ ] **Step 1: Health + regression** — `GET /v1/health` before/after (delta none), taxonomy body unchanged, saved-searches/facets spot-checks, gate 401 both sides.
- [ ] **Step 2: Report** — bundle hash only if a rebuild was authorized; `$0` held unless the packet authorized one capped live leg (`≤$0.015`).

**Out of scope:** everything not in the authorizing packet; catalog filter; analytics.
**Deliverables:** rider verdict, no stray writes.

## Explicitly NOT in this stage

- Catalog filter/search on Google kind (deferred by design).
- Analytics taxonomy changes (`GET /v1/taxonomy` unchanged).
- Taxonomy version update (a later slice vendors a newer file; old rows keep their stamp).
- Phase 5 D107 and Enrich D108 work (queue holds per D114).
