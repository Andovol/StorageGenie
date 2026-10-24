# Row 14 — the remaining missing photo AI features — code facts read on 2026-10-24 (read-only research, no dispatch)

Read while the SG-241 rider was in flight. Every claim below is a `file:line` in this repo at `04a5351`. **Nothing here is a decision** — the stage shape, the provider choice and the money authority are the owner's, and the ones that are 🟠 go through the two-phase second opinion first (D-1024-10).

## What the roadmap row asks for

`docs/ROADMAP.md:32` — **"Second AI provider and local option with fallback and spending limits | Partly built | Router and limits exist in `backend/app/services/providers/router.py`; one real photo reader plus a test fake (`backend/app/services/providers/`); scene-only web reader in `backend/app/services/scene/`; no second photo reader wired | M"**

The blueprint's phase that owns it: `inception/generic_asset_catalog_expiry_tracker_blueprint.md:533-539` — *"Phase 4 — Provider flexibility, extensibility, analytics: Second cloud provider + optional local provider adapter; router, fallback, budgets."* Its exit condition: *"changing providers needs configuration, not code."*

The blueprint's routing policy (`:318`): *"provider, fallback, local fallback, JSON-schema strictness, per-job cost budget, retryable errors."*

## What already exists (G-A10 — ask before designing)

| Piece | Where | State |
|---|---|---|
| The provider seam | `backend/app/services/providers/protocols.py:28-37` (`VisionExtractionProvider.extract_items` → `ProviderResult`), `:40-45` (`OcrProvider`), `:47-52` (`EmbeddingProvider`), `:55-60` (`WebEnrichmentProvider`) | the four protocols exist; only the first is implemented for real |
| The router | `backend/app/services/providers/router.py:30-36` (`RouterConfig`: provider_id, **fallback_id**, json_strict, cost_budget, retryable_errors), `:52-82` (`execute`: pre-call budget refusal → primary → fallback on a retryable kind only) | **the fallback path works and is tested** (`backend/tests/test_provider_gateway.py:73-91`), but **no production call site ever sets `fallback_id`** — it is hardcoded `None` at `providers/reader.py:465`, `services/chat/service.py:425`, `services/planning/service.py:444`, `services/analytics/service.py:597` |
| The registry (the seam a second reader plugs into) | `backend/app/services/providers/reader.py:90-104` `provider_registry()` | registers **exactly two**: the `fake` double (always) and `opencode-go` (only when `settings.opencode_api_key` is set) |
| The one real photo reader | `backend/app/services/providers/opencode_go.py:209-335` (`OpenCodeGoProvider`), `:32-33` `BASE_URL = https://opencode.ai/zen/go/v1`, `:258-267` the single POST send site, `:151-164` the cost estimate, `:139-148` the rate table | the only real adapter; its key never enters the payload |
| The test double | `backend/app/services/providers/fake.py:23-130` (`FakeProvider`, four modes incl. `outage_retryable`) | already covers "primary fails retryably" |
| Spending limits | `backend/app/config.py:48-49` (`sg_per_job_cap`, `sg_monthly_cap`, **both default `None` = uncapped**), `providers/router.py:71-74` (per-job refusal before any call), `providers/reader.py:486-497` (the monthly cap read from the **durable ledger**, boxed to the current month) | the mechanism exists and is enforced; **the defaults are off** (F2, owner 2026-09-11: "no caps at first, we will re-evaluate later") |
| The consent gate | `providers/reader.py:108-114` `ai_status()` (`sg_consent` default `False`, `config.py:50`) | every cloud call is gated on consent |
| The safe settings surface | `backend/app/api/v1/settings.py:29-36` (`AiSettingsOut` exposes provider_id, model_id, allowed_model_ids, consent, per_job_cap, monthly_cap, prompt_category — **no key anywhere**), `:60-65` (PUT sets a whitelisted model id only) | read-mostly; the provider id is **not** settable at runtime |
| The scene-only web reader | `backend/app/services/scene/openrouter.py` (one httpx client, `:781`/`:783` the two send sites, `openrouter:image_generation` tool) | **image generation, not photo reading** — it does not implement `VisionExtractionProvider` |
| The privacy inventory pin | `backend/tests/test_privacy_audit.py:237-248` | **a tripwire**: the set of files importing httpx and the exact send-site lines are pinned. **A second photo reader with its own client breaks this test until the inventory is updated on purpose** — the pin is a visible ledger, not a bug |
| The redact call sites | `backend/tests/test_privacy_audit.py:251-267` | the redactor's two callers are pinned (the adapter and the reader); a second adapter adds a third and the pin moves |
| The keys the host already has | `.env.example:3-5` (`OPENCODE_API_KEY`, `JINA_API_KEY`, `OPENROUTER_API_KEY`) | the **scene** path already uses OpenRouter; the photo path uses opencode-go |

## The gap, stated as the code states it

1. **No second photo reader is wired.** `provider_registry()` knows two providers and one of them is a test double. The registry is the plug-in point (`reader.py:90-104`) and the `VisionExtractionProvider` protocol is the shape a new adapter must satisfy.
2. **The fallback exists but is unreachable from production.** `RouterConfig.fallback_id` is set to `None` at every one of the four call sites. The blueprint asks for a configured fallback (and a *local* fallback); the code has the switch and nothing turns it on.
3. **The limits exist but default to off** (`sg_per_job_cap`/`sg_monthly_cap` = `None`), and the per-provider **cost estimate** is per-vendor (`opencode_go.py:139-164` reads that vendor's rate table) — a second vendor needs its own rate table and its own estimate, or the pre-call refusal has no number to compare.
4. **"The local option" has no implementation and no defined meaning in this repo.** The blueprint says "optional local provider adapter" (`:535`) and "local fallback" (`:318`); there is no local adapter, no local endpoint setting, and no local-model runtime on the host. What "local" means here (a local model server on the host, an on-device path, a different vendor) is **undefined by the code** — it is a decision, not a build.
5. **The privacy inventory is a pinned ledger** — any new outbound carrier must be added to it deliberately, and the redactor's call-site pin moves with it.

**What the shared host says about "local" (host facts, measured 2026-09-17 by Launcher; `G-A5` — re-measure before building on them).** From this project's own contract cache, `.rules-cache/VPS.md`:

- **F1: 6 logical CPUs (AMD EPYC-Milan), RAM 7.7 GiB, swap ~8 GiB** — and **S6: "RAM is marginal and shared by every project."**
- **F4: "Ollama is installed but INACTIVE (2026-09-17). Do not plan on a local model being served."**
- **S4: every service binds to loopback**; a new always-on service must state its expected memory (S6).

**Consequence for D-R14-b, stated as a fact and not as a decision:** a local *vision* model serving the photo path on this host would run on a 7.7 GiB RAM box shared with every other project, with the one local-model runtime already installed **inactive** and explicitly marked as not-to-plan-on. **No local model is currently serving anything.** The cheapest "local" reading that this host can actually carry is therefore not "a local model server" — it is **a local code path that needs no inference at all** (for example the deterministic `fake` provider already in the registry, or the local OCR/zbar path already in `app/services/signals.py`, which reads text and barcodes from a photo **without any provider**). Whether the owner's "local option" means a local *model* or a local *no-provider path* is exactly the undefined piece D-R14-b exists to settle — and it changes the cost of the whole row by an order of magnitude.

## What is NOT in this row

The scene reader (image generation) is a different surface and stays as it is; `services/scene/` is not photo reading. The OCR/zbar path (`app/services/signals.py`) is a **local** capability already — it is the existing local option for *reading text from a photo*, not for extracting catalog items, and it must not be confused with a local LLM adapter.

## Open decisions for the owner (each 🟠 or above → second opinion first, D-1024-10)

- **D-R14-a — which second provider** (and therefore which key, which rate table, which model id). Candidates visible in this repo's own history: a second cloud vendor, OpenRouter (a key already exists for the scene path — but its current use is image generation, not vision extraction), or a Google path (the scene renders already went Google-only, D-1009-10).
- **D-R14-b — what "the local option" means** (the code does not define it) and whether it runs on the live host, which is a **sensitive area** (project rule) — a local model runtime on `87.106.66.242` is an infrastructure change.
- **D-R14-c — the spending limits' values** (both caps are off today) and the **money authority** for a metered probe of the new provider: every slice so far runs `$0` and a metered call is a STOP-and-report.
- **D-R14-d — the stage shape**: which slices, in what order, and the proof that the new reader is actually **wired** (an offline conformance test plus, if authorised, one live metered call).
