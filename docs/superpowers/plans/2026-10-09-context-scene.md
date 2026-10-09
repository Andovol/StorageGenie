# Context Scene (OpenRouter) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove OpenRouter-routed scene rendering (T0 catalogue + T1b 3 renders) and exit with the D7 model pick on stored-render evidence.

**Architecture:** One OpenRouter client module mirroring `services/enrich/jina.py` (settings-field-first key seam, frozen request envelope, loud degradations, never-raises); orchestrator-vision + `openrouter:image_generation` tool with `tool_choice: "required"`; renders downloaded immediately into Evidence rows with provenance; spend ledgered per call.

**Tech Stack:** backend FastAPI (Python, `httpx`), OpenRouter `/api/v1/chat/completions` + `/api/v1/models` (OpenAI-compatible), pytest + ruff + mypy gates.

## Global Constraints

- T0: read-only, $0, no production writes, no served-code change (no refresh per D145).
- T1b: max 3 renders, ≤$1 total, consent-gated; every billed call ledgered even on empty/error content.
- Key seam: `settings.openrouter_api_key` first, `OPENROUTER_API_KEY` env fallback; key value never returned, stored, or logged (Jina precedent).
- Suite-green binds (M45); fail-pre→pass-post both committed; live rows left with ids quoted (PG-EV-06).
- Envelope values below marked T0-PINNED are verified live at T0 and re-stated verbatim in the T1b packet — never inherited from this plan or the spec.

---

### Task 1: SG-155 T0 — OpenRouter catalogue + envelope verification (read-only)

**Files:**
- Create: `backend/app/services/scene/__init__.py`, `backend/app/services/scene/openrouter.py`
- Create: `backend/tests/test_sg155_scene_t0.py`
- Modify: `backend/app/config.py` (add `openrouter_api_key: str | None = None`, `sg_scene_cap: float | None = None`, both default None/off)
- Modify: `.env.example` (names-only `OPENROUTER_API_KEY=` line, SG-097 precedent)

**Interfaces:**
- Consumes: `app.config.settings` (new fields), host env (owner-placed key, name-only in reports).
- Produces (for Task 2): `resolve_openrouter_key(explicit=None) -> str | None`, `build_scene_request(photo_ref, brief, image_model, orchestrator) -> dict` (exact envelope incl `tool_choice: "required"`, `max_tool_calls: 1`, spend-stop), `SceneRefusal` loud classes, T0-PINNED values (shortlist slugs, per-call prices, reference-image support yes/no, stop-condition schema).

- [ ] **Step 1: Write the failing tests** — `resolve_openrouter_key` seam (explicit > settings > env > None, mirrors `test_sg082` key tests); `build_scene_request` asserts the frozen envelope: URL `https://openrouter.ai/api/v1/chat/completions`, `tool_choice == "required"`, tools array holds exactly one `{type: "openrouter:image_generation"}` entry, headers never carry `Authorization` (added at send time), photo enters as message image content, never as query text.
- [ ] **Step 2: Run to verify they fail** — `cd backend; pytest tests/test_sg155_scene_t0.py -v`, expect FAIL (module missing).
- [ ] **Step 3: Implement `openrouter.py`** — `OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"`; `resolve_openrouter_key` (jina.py:120-133 shape); `build_scene_request` returning the exact sendable dict; refusal constructors (`missing_key`, `refused_consent`, `over_cap`); send function used ONLY by the live legs below, never in tests (tests assert the built dict offline).
- [ ] **Step 4: Run tests to verify pass** — same pytest, expect PASS; then suite + `ruff` + `mypy` gates green (decoder-reds class stash-proved if present).
- [ ] **Step 5: Live leg T0a (models catalogue, $0)** — `GET /api/v1/models` on the lane, filter image-output models, record the two shortlist slugs + per-call prices + orchestrator candidate slugs. No render.
- [ ] **Step 6: Live leg T0b (schema proof, $0)** — no render: confirm the exact `stop_server_tools_when` condition schema with a 0-cost read (models endpoint metadata or the error body of a keyless malformed request — whichever spends $0, stated in the report), and answer the reference-image question from the live tool contract. Both answers recorded verbatim — T1b is blocked without them.
- [ ] **Step 7: Commit** — work commit (CO-53: ID prefix allowed) + receipt; report carries T0-PINNED values, both live answers, $0 proof.

### Task 2: SG-156 T1b — 3 controlled renders + D7 pick (≤$1)

**Files:**
- Create: `backend/tests/test_sg156_scene_t1b.py`
- Modify: `backend/app/services/scene/openrouter.py` (only what T0 evidence forces; T0-PINNED envelope restated verbatim, never re-derived)
- Uses: existing asset Evidence photos (2–3, ids quoted); Evidence writer + spend ledger (same rows SG-132 precedent)

**Interfaces:**
- Consumes: Task 1's `build_scene_request`, `resolve_openrouter_key`, T0-PINNED slugs/prices/schemas.
- Produces: 3 Evidence rows (render bytes + provenance: provider=`openrouter`, image model, orchestrator, prompt, usage cost, timestamp) + 3 ledger rows + D7 pick with per-render judgment (faithfulness vs scene quality, stated per render, no aggregates — D30).

- [ ] **Step 1: Write the failing tests** — download-then-store path (temp-URL bytes → Evidence row, provenance fields exact); billed-failure ledgering (forced-error run still writes its row); cap enforcement (4th render refused with `over_cap`, 0 HTTP bytes); consent refusal (no consent → no send).
- [ ] **Step 2: Run to verify they fail** — `cd backend; pytest tests/test_sg156_scene_t1b.py -v`, expect FAIL.
- [ ] **Step 3: Implement the minimal render path** — consent check → one request per run (`max_tool_calls: 1`, spend-stop from T0-PINNED schema) → immediate download → Evidence + ledger rows. Nothing else.
- [ ] **Step 4: Run tests to verify pass** — same pytest, expect PASS; suite + ruff + mypy gates green.
- [ ] **Step 5: Live leg (3 renders, ≤$1, consent-gated)** — render 1 (OpenAI-family slug) + render 2 (Google slug), same photo + frozen brief; render 3 confirms the winner on a second photo. Quote all row ids, per-render judgments, total spend ≤$1. Rows left by design (PG-EV-06).
- [ ] **Step 6: Commit** — work commit + receipt; report ends with the D7 pick on the three rows. Arc exit: D7 + spec + T0/T1b receipts.
