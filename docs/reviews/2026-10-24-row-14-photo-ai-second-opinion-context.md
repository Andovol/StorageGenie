# Second-opinion context pack — roadmap row 14: the second photo reader, the fallback, the local option, the caps

**Purpose:** an independent pick on four owner decisions before any of them reaches the owner
(`SECOND_OPINION.md`, D-451; the project's "Second opinion before the owner" rule, D-1024-10).
**This pack states no pick and no preference.** Its job is to hand the reviewer the facts, the options and
the rules, with every claim traceable. Anything the Architect thinks is a lean belongs in Phase B, after
Phase A has reported.

**The decision in plain words.** The app reads one photo through one cloud provider. The owner's standing
priority (2026-10-24, D-1024-12) is *"the remaining missing photo AI features"* — roadmap row 14: a second
AI provider and a local option, with fallback and spending limits. Before the owner is asked to choose a
vendor, a local runtime, or a spending authority, an independent reviewer picks.

## What exists (read these)

| What | Where | Note |
|---|---|---|
| The capability interface | `backend/app/services/providers/protocols.py:28-60` | `VisionExtractionProvider`, `OcrProvider`, `EmbeddingProvider`, `WebEnrichmentProvider` — **only the first is implemented for real** |
| The router | `backend/app/services/providers/router.py:30-36` | `RouterConfig(provider_id, fallback_id, json_strict, cost_budget, retryable_errors)` |
| The router's execution | `backend/app/services/providers/router.py:52-82` | pre-call budget refusal → primary → fallback **only on a retryable error kind** |
| The provider registry | `backend/app/services/providers/reader.py:90-105` | `fake` always; `opencode-go` only when `settings.opencode_api_key` exists |
| The one real reader | `backend/app/services/providers/opencode_go.py:209-335` | `BASE_URL https://opencode.ai/zen/go/v1`, `CHAT_PATH /chat/completions`, one POST send site (`:263`) |
| Its rate table | `backend/app/services/providers/opencode_go.py:44-45` | input `$0.15/1M`, output `$0.60/1M`; cost estimate at `:151-164` |
| The test double | `backend/app/services/providers/fake.py:23-130` | four modes, incl. `outage_retryable` |
| The spending caps | `backend/app/config.py:48-49` | `sg_per_job_cap`, `sg_monthly_cap` — **both default `None` = uncapped** (owner, 2026-09-11: "no caps at first") |
| Where the caps are enforced | `providers/router.py:71-74`, `providers/reader.py:486-497` | monthly cap reads the durable ledger |
| The consent gate | `providers/reader.py:108-114` | `sg_consent` default `False` (`config.py:50`) |
| The settings surface | `backend/app/api/v1/settings.py:29-36` | `provider_id`, `model_id`, `allowed_model_ids`, consent, caps, prompt category — **no key field**; `provider_id` is **not settable at runtime** |
| The allowed model ids | `backend/app/api/v1/settings.py` | one only: `deepseek-v4-flash-vision-exp` |
| The scene-only reader | `backend/app/services/scene/openrouter.py` | **image generation**, one httpx client, send sites `:781`/`:783` — it does **not** implement `VisionExtractionProvider` |
| The privacy tripwire | `backend/tests/test_privacy_audit.py:237-248` | pins the httpx-client file set and the exact send-site lines — **a second reader breaks this test until it is updated deliberately** |
| The redaction tripwire | `backend/tests/test_privacy_audit.py:251-267` | pins the `redact_image` call sites (adapter + reader only) |
| The keys the host may hold | `.env.example:3-5` | `OPENCODE_API_KEY`, `JINA_API_KEY`, `OPENROUTER_API_KEY` (names only; the file holds no values) |
| The fallback's test | `backend/tests/test_provider_gateway.py:73-91` | the fallback path is **tested** |

## What is missing (the gap, in the roadmap's own words)

`docs/ROADMAP.md:32` — *"Second AI provider and local option with fallback and spending limits | Partly built |
Router and limits exist in backend/app/services/providers/router.py; one real photo reader plus a test fake;
scene-only web reader in backend/app/services/scene/; no second photo reader wired | M"*.

Three facts a candidate decision must survive:

1. **No production call site ever sets `fallback_id`.** It is hardcoded `None` at
   `providers/reader.py:465`, `services/chat/service.py:425`, `services/planning/service.py:444`,
   `services/analytics/service.py:597`. The fallback is reachable in tests only.
2. **Each vendor needs its own rate table and its own cost estimate** (`estimate_call_cost` is per-adapter,
   `opencode_go.py:151-164`). A second reader without a rate table cannot produce a cost number, and the
   caps consume cost numbers.
3. **"The local option" is undefined by the code.** No `OcrProvider`, no `EmbeddingProvider` and no
   `WebEnrichmentProvider` is implemented; the only no-provider path in the registry is the deterministic
   `fake`.

## The host this runs on (measured, not assumed)

From this project's own `.rules-cache/VPS.md` (**measured 2026-09-17 — re-measure before building**):

- 6 logical CPUs.
- **RAM 7.7 GiB, marginal, and shared by every project on the host** (S6).
- **Ollama is installed but INACTIVE — the guide says "Do not plan on a local model being served"** (F4).
- Every service binds loopback (S4); a new always-on service must state its expected memory.

## The candidate readings of "the local option" (three readings; the reviewer picks or names a fourth)

- **L1 — local without a provider.** The deterministic `fake` provider already in the registry
  (`reader.py:96`), or the local OCR/zbar path in `app/services/signals.py`. No model, no network, no
  always-on service; the cost is that it returns fixtures, not readings.
- **L2 — a local model served on the live host.** The realistic small candidates are Qwen3-VL 2B (GGUF,
  ~2 GB weights, ~3–4 GB RAM) or 8B (~6.1 GB at Q4_K_M, ~6–8 GB VRAM floor); Ollama serves `qwen3-vl:2b`
  / `qwen3-vl:8b` natively, and llama.cpp runs the same GGUF with a separate `mmproj` file. On a
  **7.7 GiB RAM host shared with other projects**, the 2B class is the only size that plausibly fits, and
  this contradicts VPS.md F4 ("do not plan on a local model being served") — so this reading needs the
  owner to change a host rule, and it makes the app depend on a service that can be down.
- **L3 — local as a fallback destination only.** The local path is not a default; it is where the router
  lands when the cloud provider is unreachable or over budget.

## The candidate second cloud providers (facts only; the reviewer picks)

The host's `.env` template already names `OPENROUTER_API_KEY` (and the scene path already uses OpenRouter),
so OpenRouter is the only candidate with a key slot already present in this repo's configuration.

| Provider | Interface | Vision-capable small model | Published rate (per 1M tokens) | Source and date |
|---|---|---|---|---|
| OpenRouter (aggregator) | OpenAI-compatible `POST /chat/completions` — the same shape the existing reader uses | serves `openai/gpt-4o-mini`, Google Gemini 2.5 Flash, and others | `gpt-4o-mini` $0.15 in / $0.60 out; Gemini 2.5 Flash $0.30 in / $2.50 out | computeprices.com / llmreference.com / cloudprice.net, refreshed 2026-10-17 → 2026-10-23 |
| Google AI Studio (direct) | its own SDK/REST, **not** OpenAI-shaped | Gemini 2.5 Flash | $0.30 in / $2.50 out; Gemini 2.5 Flash-Lite $0.10 / $0.40 | braindetox.kr API comparison (2026-06-15), costbench.com (2026) |
| OpenAI (direct) | OpenAI-compatible | `gpt-4o-mini` | $0.15 in / $0.60 out | llmreference.com, refreshed 2026-10-17 |
| Jina | embeddings/search, **not a vision extractor** | — | — | `.env.example:5` (key slot only); Jina's published products are embedding/rerank/search |

Cost shape worth carrying into the pick: a 1024×1024 image is ~765 input tokens on GPT-4o high detail,
~258 on Gemini 2.5 Flash (dev-toolbox, vision cost table), and Gemini-class models are typically 5–10× (or
30–100× for the newest Flash) cheaper per image than premium vision models (aicost.ai, verified 2026-10-13).
**No provider here has been called by this app yet** — every slice to date ran `$0`, `provider_call` 39 → 39.

## The four owner decisions this pack is for

- **D-R14-a — which second provider.** Options: OpenRouter (key slot exists, OpenAI-shaped, one adapter
  shape for many vendors) · Google direct (cheapest flash tier, new SDK surface, no key slot yet) · OpenAI
  direct (OpenAI-shaped, new key slot) · a different vendor named by the reviewer.
- **D-R14-b — what "the local option" means** (L1, L2, L3, or a fourth). **L2 puts a runtime on the live
  host**, which is a sensitive surface (the project's own rule) and collides with VPS.md F4.
- **D-R14-c — the caps' values and the money authority for a metered probe.** Both caps are `None` today;
  the reviewer must not assume a value. A metered probe is a **STOP-and-report** event under the standing
  lane rules.
- **D-R14-d — the stage shape.** How many slices, in what order, and what the exit condition is. The
  blueprint's exit condition for this phase is *"changing providers needs configuration, not code"*
  (`inception/generic_asset_catalog_expiry_tracker_blueprint.md:533-539`); the routing policy it names is at
  `:318` (provider, fallback, local fallback, JSON-schema strictness, per-job cost budget, retryable errors).

## What binds it

- **G-K2** — "These reach the owner however trivial they look: production data destruction or any production
  write, secrets / infrastructure / database-role changes, anything touching a declared sensitive surface,
  anything irreversible or outward-facing. They hold at every autonomy level."
- **The project's sensitive-areas rule** (`AGENTS.md`) — the stored photos and files, the app database, the
  dispatch key and the host are declared sensitive; an area not listed there is not declared safe.
- **G-A7 (simplicity)** and **G-A10 (ask what already exists)** — the `fake` provider, the `fake`-backed
  gateway test, the scene reader's httpx client and the local OCR path all exist; a new mechanism that
  duplicates one of them is a cost, not a win.
- **G-A9** — any window, budget or threshold here starts **uncalibrated** and says so at its site.
- **PG-PR-01** — establish the capability model before building: what can this identity do to these objects?
- **G-M11 / G-A6** — name the root cause, not a band-aid: the reason the fallback is unreachable is that
  **no call site passes `fallback_id`**, not that the router lacks one.

## The guard on the reviewer's pick

The pick is **not** allowed to assume that a vendor's key can simply be added, that the host can carry a new
always-on service, that the caps can be left uncapped, that a metered probe is free, or that the existing
`fake` provider answers a real photo. If the reviewer believes the roadmap row should be closed, deferred, or
split, that is a legitimate pick — say so and name what would have to be true first.
