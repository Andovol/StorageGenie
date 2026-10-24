# Second-opinion context pack — roadmap row 14, round 2: the four decisions as they now stand

**Purpose:** an independent pick on the four owner decisions of roadmap row 14 **before** they reach the owner
(`SECOND_OPINION.md`, D-451; the project's "Second opinion before the owner" rule, D-1024-10). The owner asked
for a second opinion on all of them (2026-10-24).

**This pack states no pick and no preference.** It gives the facts, the options and the rules, each traceable.
Anything the Architect thinks is a lean belongs in Phase B, after Phase A has reported.

---

## The problem in plain words, and why it matters now

The app reads one photo through one cloud provider. Roadmap row 14 (`docs/ROADMAP.md:32`) asks for **a second
AI provider and a local option, with fallback and spending limits**. The owner's standing priority (D-1024-12,
2026-10-24) is *"the remaining missing photo AI features"*, so this row is next. Four decisions ride on it, and
they are the owner's: **which second provider**, **what "the local option" means**, **the spending caps and the
money authority for a metered probe**, and **the shape of the stage**. One of them has since been decided by
the owner (below), which is why the review runs again rather than the decisions going straight out.

## The owner's ruling — taken, not open (D-1024-15)

Owner, 2026-10-24, verbatim: ***"We will not have local models on the server."***

**Consequences that are settled:** the live server (`87.106.66.242`) never runs a local model — no model
server, no on-demand model sidecar, no model downloaded to the host. The host's own guide already said
*"Do not plan on a local model being served"* (`.rules-cache/VPS.md` F4, measured 2026-09-17 on a shared
7.7 GiB box); the owner has now made it a rule. **This closes the branch in which a local model serves the
photos** — it is not a deferred choice and it does not go back to the owner.

**Consequences that are still open inside the ruling:** what "local" can mean now (the deterministic no-model
path, the local OCR/barcode observations, or nothing at the provider level), and what the routing must do when
the local path is the landing.

## What exists (read these)

| What | Where | Note |
|---|---|---|
| The capability interface | `backend/app/services/providers/protocols.py:28-60` | `VisionExtractionProvider`, `OcrProvider`, `EmbeddingProvider`, `WebEnrichmentProvider` — **only the first is implemented for real** |
| The router | `backend/app/services/providers/router.py:30-36` | `RouterConfig(provider_id, fallback_id, json_strict, cost_budget, retryable_errors)` — **one** retryable set, consumed at `:79` |
| The router's execution | `backend/app/services/providers/router.py:52-82` | pre-call budget refusal (`:71-74`) → primary → fallback **only on a retryable error kind** (`:79`) |
| The retryable set | `backend/app/services/providers/reader.py:61-63` | `{outage, timeout, rate_limited, transport, http_status, invalid_json}` |
| The provider registry | `backend/app/services/providers/reader.py:90-105` | `fake` always; `opencode-go` only when `settings.opencode_api_key` exists |
| The one real reader | `backend/app/services/providers/opencode_go.py:209-335` | `BASE_URL https://opencode.ai/zen/go/v1`, `CHAT_PATH /chat/completions`, one POST send site (`:263`); the vendor-neutral guards sit **inside** this file (`:70-164`, `:298-309`) |
| Its rate table | `backend/app/services/providers/opencode_go.py:44-45` | input `$0.15/1M`, output `$0.60/1M`; `DEFAULT_MAX_TOKENS` 2000 (`:36`) |
| The cost estimate | `backend/app/services/providers/opencode_go.py:151-164` | **a deliberate upper bound**: input tokens ≈ prompt bytes + the image's **base64 length**; output bounded by `max_tokens`. "an upper bound, not a forecast" |
| The estimate's absence | `backend/app/services/providers/reader.py:233-242` | `_estimate_call` returns `0.0` for a provider with no estimator — **caps cannot bind a provider without a rate table** |
| The monthly cap | `backend/app/services/providers/reader.py:293-306`, `:486-497` | a household-joined sum **and** an unattributed pool that counts every `job_id=None` row against every household |
| The photo path's ledger writer | `backend/app/services/providers/reader.py:208-230` | writes `job_id=job.id` |
| The consent gate | `backend/app/services/providers/reader.py:108-114`, `config.py:50` | `sg_consent` default `False` → deny by default |
| The spending caps | `backend/app/config.py:48-49` | `sg_per_job_cap`, `sg_monthly_cap` — **both `None` = uncapped** (owner, 2026-09-11: "no caps at first") |
| The scene key's declared purpose | `backend/app/config.py:41-44`, `:47` | `openrouter_api_key` is declared **for scene rendering**, with its own scene cap `sg_scene_cap` |
| The scene's OpenRouter client | `backend/app/services/scene/openrouter.py` | one httpx client, key added at send time (`:762`), a frozen render envelope (`:17-38`); its send sites `:781`/`:783` |
| The key slots | `.env.example:3-5` | `OPENCODE_API_KEY`, `JINA_API_KEY`, `OPENROUTER_API_KEY` (names only) |
| The redaction helper | `backend/app/services/providers/redaction.py:16-21` | re-encodes to **PNG, no resize** — pixels preserved, bytes not reduced |
| The privacy tripwire | `backend/tests/test_privacy_audit.py:237-248` | pins the httpx-client file set and the exact send-site lines — **a second reader breaks it until it is updated deliberately** |
| The redaction tripwire | `backend/tests/test_privacy_audit.py:251-267` | pins the `redact_image` call sites (adapter + reader only) |
| The settings surface | `backend/app/api/v1/settings.py:26`, `:29-36`, `:39-41` | the model whitelist (one id today), the settings a PUT may change (**no** caps, **no** provider id), one allowed model id |
| The fallback's test | `backend/tests/test_provider_gateway.py:43-56`, `:73-91` | the gateway test's retryable set is `{outage, timeout, rate_limited}` — **narrower than production's** |
| The local signal path | `backend/app/services/signals.py:102-111`, `:205-216`, `:153-192` | pyzbar missing → warning + empty list; tesseract missing → warning + `None`; `_fallback_ean13` is pure Python |
| The deterministic double | `backend/app/services/providers/fake.py:23-130` | `fake` fabricates `items: [{"name": "fake-item", …}]` (`:63`); `ScriptedProvider` (`:82-130`) is schema-valid, offline, cost 0.0 |
| The blueprint's phase 4 | `inception/generic_asset_catalog_expiry_tracker_blueprint.md:533-539` | "Second cloud provider + optional local provider adapter; router, fallback, budgets"; exit: "changing providers needs configuration, not code" |
| The blueprint's routing policy | `inception/generic_asset_catalog_expiry_tracker_blueprint.md:318` | provider, fallback, local fallback, JSON-schema strictness, per-job cost budget, retryable errors |

## What is missing (the gap)

1. **No production call site ever sets `fallback_id`** — hardcoded `None` at `providers/reader.py:465`,
   `services/chat/service.py:425`, `services/planning/service.py:444`, `services/analytics/service.py:597`.
   The fallback exists and is tested; it is unreachable from production.
2. **No second photo reader** exists, so no second rate table, no second estimate, no second key seam.
3. **"The local option" has no implementation** — no `OcrProvider`, no `EmbeddingProvider`, no
   `WebEnrichmentProvider`; the only no-provider entries are the deterministic double and the signals path.
4. **The caps bind nothing** (`None`), and the consent gate is closed by default, so nothing can spend today.

## The four decisions, as they now stand (options only — no pick)

### D-R14-a — which second cloud provider

- **A1** — **OpenRouter**, as a second provider behind a new adapter: the key slot exists (`.env.example:5`),
  the API shape is the one the existing reader already speaks, and an OpenRouter client already exists in the
  tree. The facts the reviewer must weigh against it: the key slot was declared **for scene rendering**
  (`config.py:41-44`) with its own cap (`sg_scene_cap`) — so both image surfaces would sit on **one vendor and
  one key**; and the vendor-neutral guards live **inside** the vendor file, so a second adapter **duplicates
  them** and the two copies can diverge silently (measured: **119 lines**). Measured in SG-247: **scene spend is
  unattributed and the scene cap filters `provider == "openrouter"` with no month filter** — so a photo adapter
  that reused the id `openrouter` would also be charged to the scene cap, and the two surfaces' budgets would be
  coupled. The reviewer must say how the photo adapter's provider id and its budget separation would work.
- **A2** — **Google AI Studio (Gemini) directly**: the cheapest vision class per published rates, but it needs
  a new key slot and its own API surface (the pack's earlier rate note: Gemini 2.5 Flash $0.30 in / $2.50 out;
  Gemini 2.5 Flash-Lite $0.10 / $0.40; ~258 tokens per 1024×1024 image).
- **A3** — **OpenAI directly**: the same API shape as the existing reader, a new key slot, `gpt-4o-mini`
  $0.15 in / $0.60 out.
- **A4** — **a second model on the existing `opencode-go` gateway**: the cheapest change, and it exercises
  `fallback_id` and the caps with no new key — but it is **not vendor-independent** (the gateway is still the
  single point of failure).
- **A5** — another vendor the reviewer names.

### D-R14-b — what "the local option" means, inside the owner's ruling (no local model on the server)

- **B1** — **the no-model local path as the provider fallback destination** (the deterministic double plus the
  local OCR/barcode observations), reached **only** on transport/outage classes. Constraints that any version of
  this must satisfy: a local landing must **never** present a fabricated reading (the double returns
  `fake-item`), and `invalid_json` — which stands for a prompt or schema bug — must **surface**, not be
  absorbed by a fixture.
- **B2** — **the local signals path as the default for what it can do** (barcode and OCR from the local
  libraries), with the cloud called only for the item proposals the local path cannot make. This path is
  already in the tree as a *signals* service, not a provider — and the local libraries are present in the
  project's image (`docs/worklogs/SG-238_g3_image_libs.log:4-6`: `tesseract 5.3.0`, `libzbar.so.0`, both
  imports ok).
- **B3** — **no provider-level local destination at all**: the row's "local option" is satisfied by the existing
  local signals path, and the provider layer gets cloud providers only.
- **B4** — another reading the reviewer names, inside the ruling.

The review must also say what the **landing contract** is: the existing skipped shapes
(`providers/reader.py:452-454`, `:472-479`, `{"status":"skipped","reason":…}`) and what happens if the pipeline
or the review queue treats a fired-but-empty fallback as a failure.

### D-R14-c — the spending caps and the money authority for a metered probe

- **C1** — **caps set explicitly before any metered call, no standing money authority, every probe separately
  authorised with a ceiling derived from the estimate's upper bound for the image the probe actually uses.**
- **C2** — **standing caps** (a per-job cap and a monthly cap) chosen by the owner now, with per-probe
  authorisation inside them.
- **C3** — **a one-shot probe budget that the per-job cap does not bound** (the "bound-exempt one-shot
  budget"), with the standing caps still unset.
- **C4** — **no metered call at all in this stage**: calibrate with the deterministic double and the estimate
  arithmetic only, and defer the probe.

The arithmetic the reviewer must work from (all measured, not assumed): `input_tokens ≈ len(prompt bytes) +
base64 length of the image`; output bounded by `max_tokens` (2000 by default); `redact_image` re-encodes to PNG
**without resizing**, so the PNG's bytes are what the estimate sees. A **3 MB** image → ≈4.0 M base64 chars →
≈**$0.60** of upper-bound input cost at `$0.15/1M`; a **2–4 MB** photo → ≈**$0.40–0.80**; the app's **20 MB**
upload cap (`config.py:20`) → ≈**$4**. A small repository test image (kilobytes) → **cents**. The consequence
to reason about: a ceiling **below** the bound makes the probe's own pre-call refusal fire, so the ceiling vetoes
its own probe.

### D-R14-d — the shape of the stage (and what the blueprint's exit condition means)

- **D1** — **four ordered slices**: fallback plumbing with doubles → the second adapter with its own rate table
  and the deliberate pin updates → caps calibration and one authorised metered probe → the local landing.
- **D2** — **three slices** (fold the plumbing into the adapter slice), which the earlier critique raised as the
  honest alternative when the plumbing slice's exit is not observable.
- **D3** — **two slices** (the adapter, then caps and the probe) — the plumbing folded in and the local landing
  deferred.
- **D4** — **close or defer the row** until the host is re-measured (the host figures are from 2026-09-17 on a
  shared box).
- **D5** — **what "changing providers needs configuration, not code" (`blueprint.md:539`) means**: a **stable
  seam with per-vendor adapters** (the tree already branches per model family, `opencode_go.py:63-67`), or
  literally **no code per vendor** — which no adapter can satisfy. **The measured answer (SG-247): the literal
  reading is false today** — adding a vendor needs an adapter, a registry branch and a rate table; selecting a
  provider or fallback needs the settings surface and the caller wiring at five call sites. What the stage can
  meet is the seam reading, with the touch-list as its scope. This reading is the owner's to confirm, and the
  reviewer should say which reading it believes the stage can actually meet.

The slice-1 exit question the reviewer must answer: with **no production fallback configured** (so nothing can
fabricate a reading), what is an exit that is **observable rather than vacuous** — a configuration read-back, or
something else?

## Measured facts from the read-only verification slice (SG-247)

Measured in a slice that wrote nothing: no product byte, no database opened (not even read-only), no provider
called, no key read, **$0**, 569 s. Evidence: `docs/worklogs/SG-247_report.md`, `SG-247_g1_g3.log`,
`SG-247_g2_build.log`, `SG-247_g2_measure.log`, `SG-247_g2_digest.log`, `SG-247_orientation.log`.

**G1 — the adapter touch-list (measured).** A second adapter must touch: a **new adapter file**;
`providers/reader.py` (registry gate `:90-105`, `ai_status()` `:108-114`, `run_ai_extraction` `:456-469`);
`config.py` (the new key/base-url/model **and** a fallback-id setting); `api/v1/settings.py` (whitelist `:26`,
GET shape `:29-36`, PUT shape `:39-40`, validation `:62-63`); the **four `RouterConfig` call sites**
(`reader.py:463-469`, `chat/service.py:423-429`, `planning/service.py:442-448`, `analytics/service.py:595-601`);
**`services/enrich/synthesize.py:276-285` — a sixth caller the slice found, which calls the provider directly
and bypasses `ProviderRouter` entirely**; `tests/test_privacy_audit.py` (client file set `:237-243`, send sites
`:244-248` and `:524-528`, `redact_image` sites `:264-267`); conditionally `providers/router.py` (the
per-destination retryable set) and `providers/opencode_go.py` (the shared base); `tests/test_provider_conformance.py`
plus a new adapter test file; the lockfiles **only** if a new SDK is used.

- **G1.1 — the seam question, measured: NO.** The list does **not** stay inside seam + adapter + pins. The
  **policy, ledger and outcome half stays untouched** (the repair policy, the ledger writers, `ExtractionOutput`,
  `ProviderResult`, `models/provider_call.py`, `redaction.py`, `protocols.py`, `reader._estimate_call` need no
  edit) — but the four router sites need a caller **wiring** edit, `synthesize.py` bypasses the router, and the
  runtime-selection surface does not exist. So "changing providers needs configuration, not code" is **false
  today**, both for adding a vendor and for selecting provider/fallback.
- **G1.2 — the vendor-neutral logic is 119 lines** (`70-164` = 95, `298-309` = 12, `361-372` = 12, measured with
  `wc -l`) — the guards, the accounting, the estimate shape and the two copies of the budget guard. The rate
  constants `:44-45` and the vendor-specific `response_format_for` `:63-67` stay per adapter.
- **G1.3 — what runtime selection needs:** `sg_fallback_id` in `config.py`; `_runtime_provider_id` /
  `_runtime_fallback_id` and `effective_provider_id()` / `effective_fallback_id()` in `reader.py`; every configured
  adapter registered; the effective ids used in `ai_status()`, `run_ai_extraction` and the four router sites;
  `AiSettingsOut` / `AiSettingsUpdate` extended with `provider_id` / `fallback_id` and validated against the
  registered ids; `synthesize.py` if text is in scope. **A restart resets the overrides to the env defaults.**

**G2 — the served image's local-signal path (measured inside a `--network none` throwaway container).**
`tesseract 5.3.0` at `/usr/bin/tesseract` (`which_rc=0`); `from pyzbar.pyzbar import decode` **OK**;
`import pytesseract` **OK** (its own version read 5.3.0); `libzbar.so.0` **loadable** (`ctypes.CDLL` rc=0) at
`/lib/x86_64-linux-gnu/`. The built tag's top-level digest differs from the running image's (a BuildKit
attestation manifest), while the **12 rootfs layer digests and the runtime Config are identical** — so the facts
transfer by layer identity, and the running container was not touched. **OCR quality on real photos is NOT
measured** — that needs the owner's photos and their consent.

**G3 — where the spend lands, and which retryable classes are tested (measured from the code).**

- **Scene rows land in `provider_call` with `job_id=None`** (`scene/openrouter.py:623`; cost from the response's
  `usage.cost` `:803-809`; row appended `:853-869`), and the scene cap filters `provider == "openrouter"` with
  **no month filter** (`:288-296`) — so scene spend is **all-time by provider**, and it reaches the monthly cap
  only through the unattributed pool. **A photo adapter that reused the id `openrouter` would therefore be
  charged to the scene cap as well.**
- **The monthly cap mixes categories** (`reader.py:292-306`): the household's job-linked rows **plus every
  `job_id IS NULL` row** — chat (`:331`, `:369`), planning (`:238`, `:272`), analytics (`:434`, `:469`),
  synthesize (`synthesize.py:310`) and scene (`openrouter.py:623`) — charged against **every household** reading
  that month. The photo path writes job-linked rows (`reader.py:226`, `:386`); the Jina snapshot writer is
  job-linked too (`snapshots.py:140`).
- **The gateway test is narrower than production and misclassifies one class**: production
  `{outage, timeout, rate_limited, transport, http_status, invalid_json}` (`reader.py:61-63`) against the test's
  `{outage, timeout, rate_limited}` (`test_provider_gateway.py:54`); the test exercises only `outage`, and its
  negative branch asserts that `invalid_json_once` does **not** fall back (`:85-91`) — **the opposite of
  production**. Uncovered by name: **`transport`**, **`http_status`**, **`invalid_json`**.
- **A keyless local adapter cannot register through the current gate** (`reader.py:97` is
  `if settings.opencode_api_key`), so a local provider needs a registration condition that is **not** a key.

**Not measured, and left to the owner:** the runtime magnitude of the unattributed pool (one read-only query on
the app database — a declared sensitive surface), the cap values, the money authority, and the OCR's quality on
the owner's own photos.

## What binds it

- **G-K2** — "These reach the owner however trivial they look: production data destruction or any production
  write, secrets / infrastructure / database-role changes, anything touching a declared sensitive surface,
  anything irreversible or outward-facing. They hold at every autonomy level."
- **The project's sensitive-areas rule** (`AGENTS.md`) — the stored photos and files, the app database, the
  dispatch key and the host are declared sensitive; an area not listed there is not declared safe.
- **G-A7 (simplicity)** and **G-A10 (ask what already exists)** — the deterministic double, the signals path,
  the gateway test, the scene client and the local OCR path all exist; a new mechanism that duplicates one of
  them is a cost, not a win.
- **G-A9** — any window, budget or threshold starts **uncalibrated** and says so at its site.
- **G-M11 / G-A6 (root cause)** — the fallback is unreachable because **no call site passes `fallback_id`**, not
  because the router lacks one.
- **PG-PR-01** — establish the capability model before building; enumerate what this identity can do to these
  objects, never "why did this one statement fail".
- **PG-IC-07** — every time-dependent statement reads the live clock at execution.
- **Decisions already taken, not reopened:** D-1024-6 (the cheapest route first; the image route already proved
  the two host test libraries) · D-1024-12 (row 14 is the standing priority) · D-1024-15 (no local models on
  the live server) · D-1024-10 (every 🟠/🔴 item gets this review before the owner sees it).

## The guard on the reviewer's pick

The pick is **not** allowed to assume that a key can be added or that its authority extends, that the host can
carry a service (the owner has ruled it out), that a probe is free or that a ceiling below the estimate's bound
is meaningful, that the estimate transfers to another vendor, that the local path can read a photo it has never
read, that the unattributed spend pool is empty, that a second adapter is free, or that "configuration, not
code" can be met literally. If the reviewer believes a decision should be closed, deferred or split, that is a
legitimate pick — say so and name what would have to be true first.
