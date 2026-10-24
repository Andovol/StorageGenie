# SG-248 — Architect record (round-2 Phase A of the row-14 second opinion, run on 2026-10-24)

**Trigger:** `SG-248 coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh agent=plan` (read-only lane; the same reviewer as every prior review round). The lane returned `exit 0`.
**Status verb read-back:** `result=done id=SG-248 inactive`; the published report was fetched with `SG-248 --status` and copied **unedited** to `docs/worklogs/SG-248_report.md` (16710 bytes, the report body between the `debug-report-begin` / `debug-report-end` markers).
**Receipt:** the reviewer published no receipt note of its own — the record of this phase is this file and the committed report.
**Blindness held:** the reviewer did not open the round-1 reports or the Architect's records; it declared that grep surfaced snippets of them incidentally and that nothing from the snippets was used. It did read the review ledger's lane-condition line, which disclosed the prior round's pick row, and set it aside — and reported that its four picks **diverge from that row on three of four decisions**, each re-evidenced from the code.

## Phase A's picks

| Decision | Phase A's pick | Its missed option | Its riskiest premise |
|---|---|---|---|
| **D-R14-a** | **A3 — OpenAI directly**, with a new key slot, a provider id that is never `openrouter`, its own rate table and estimator, and the shared-base extraction in the same slice | **M** — a vendor-agnostic enabling slice first: extract the vendor-neutral logic into a shared base **before** naming the vendor | that "same API shape" means a **cheap adapter** — the per-family branching that already exists (`response_format_for`, `opencode_go.py:63-67`) and the usage/cost fields (`guard_usage`/`compute_cost`, `:85-148`) may not transfer |
| **D-R14-b** | **B3 — no provider-level local destination**; the provider layer is cloud-only, `fallback_id` never resolves to anything local, total failure lands in the existing skipped/error shapes | **B5** — a local deterministic **validator**: cloud proposes, local disposes (the check-digit validators at `signals.py:195-202` and the `validated` flags exist, and **no path consumes them** against cloud-proposed identifiers) | that the signals path can do anything useful on the owner's real photos — **unmeasured by construction** — and **two gaps**: the blueprint's "local fallback" (`:318`) and "optional local provider adapter" (`:533-539`) are unmappable under the owner's ruling, and the landing contract is undefined |
| **D-R14-c** | **C1** — caps set explicitly before any metered call, no standing money authority, each probe separately authorised with a ceiling derived from the estimate's upper bound for the actual probe image | **C5** — authorise the probe by **input**, not dollars (the estimate is a pure function of bytes and prompt), and gate any standing cap on attribution repair | that the estimate transfers to another vendor — until the new adapter ships its own rate table and estimator, `_estimate_call` returns `0.0` (`reader.py:233-242`) and the caps bind nothing |
| **D-R14-d** | **D3 — two slices** (the adapter, then caps and the one authorised probe; the plumbing folded into the adapter slice; the local landing deferred), with **D5 resolved as the seam reading** | **D6** — a **zero slice first**: attribution and test alignment before the adapter (distinct per-surface provider ids; the gateway test widened to the production retryable set) | that the owner will confirm the seam reading of `blueprint.md:539` — otherwise every shape fails acceptance and the row becomes renegotiate-or-close |

**Its structural judgement:** the four decisions **must be split, never one package** — the vendor/key authority
touches secrets and infrastructure, the caps and probe authority touch spend, the local consequent is already
ruled, and the stage shape depends on the other three. Bundling would let a wrong vendor pick drag spend
authority with it, and standing caps set on mixed attribution would bind surfaces the owner never meant to cap.

## The Architect's disposition of every Phase A finding

| # | Finding | Disposition | Why |
|---|---|---|---|
| a1 | **A3 — OpenAI directly** | **ACCEPTED — the Architect's pick moves from OpenRouter to a direct vendor** | The measured separation decides it: the `OPENROUTER_API_KEY` slot is **the scene key** (`config.py:41-44`, `sg_scene_cap` `:45-47`), the scene ledger id is the literal `"openrouter"` (`scene/openrouter.py:247`) and the scene cap filters it with **no month filter** (`:288-297`), so photos on that key or that id would couple two features and two budgets through the very mechanism the caps exist to separate. A direct vendor key is a different vendor, account and failure domain from the primary gateway — which is what a fallback is for — while the API shape and the raw-httpx pattern mean **no SDK and no lockfile change**. The rates sit in today's class (`opencode_go.py:44-45`) |
| a2 | **Missed option M** — the shared base as an enabling slice before naming the vendor | **ACCEPTED IN PART — the shared base goes into the adapter slice (S2), not its own slice** | The shared base is now **119 measured lines** and it is the adapter's dependency, so a slice of its own has the weakest exit available ("nothing changed"). Its purpose — one copy of the guards instead of two that can diverge — is real inside S2, where a second adapter actually consumes it |
| a3 | **Risk: "same API shape" ≠ "cheap adapter"** | **ACCEPTED as the riskiest premise of the Architect's own pick** | Carried into the decision item: the per-family branching and the usage/cost fields may not transfer, and if they do not, the adapter is dearer than the shape argument suggests. Phase B must attack it |
| b1 | **B3 — no provider-level local destination** | **ACCEPTED**, with two additions | Agrees under the owner's ruling: the only honest readings are the existing local signals path (measured present) or nothing at the provider level. **Addition 1:** production's retryable set **loses `invalid_json`** (`reader.py:61-63`) — a schema bug must surface, not trigger a second vendor's spend — which also makes the gateway test's current assertion correct (`test_provider_gateway.py:85-91`) and means **no per-destination retryable sets are needed at all** while no local destination exists. **Addition 2:** the trigger to revisit is named — a measured OCR/barcode quality check on the owner's own photos (their consent); if the quality is good, a later slice may wrap that same path as the fallback destination, with no model |
| b2 | **Missed option B5 — a local deterministic validator (cloud proposes, local disposes)** | **ACCEPTED — recorded as backlog W5, not as part of row 14** | The slot is genuinely empty (the check-digit validators and the `validated` flags exist; no consumer) and the idea keeps local in the loop with zero fabrication risk and zero router change. It is a **separate feature** — it is not the row's fallback — so it goes to the backlog rather than into this stage |
| b3 | **Two gaps the Architect must name to the owner** | **ACCEPTED** | The **blueprint amendment** is an owner item (the product blueprint's local-fallback language is unmappable under the ruling, and it must be amended rather than silently inherited). The **landing contract** is a slice requirement: what the pipeline and the review queue do when the fallback also fails or lands empty must be specified in S1 |
| c1 | **C1 — caps first, no standing authority, derived per-probe ceiling** | **ACCEPTED**, with the input-side authorisation and the attribution gate added | The pick holds: nothing can spend today (consent closed, caps `None`), a standing cap set now would be uninterpretable while the monthly cap mixes surfaces (`reader.py:292-306`), and a ceiling below the bound vetoes its own probe. The additions are Phase A's own missed option C5: authorise the probe in **input terms** (the image's bytes and base64 length, one call, one model) with the dollar ceiling derived from that input, and **no standing monthly cap until the per-surface attribution exists** |
| c2 | **Risk: the estimate transfers to another vendor** | **ACCEPTED** | It does not, until the new adapter ships its own rate table and estimator — so S2 ships them, and the ceiling in S3 is derived from **that** table, never from the current one |
| d1 | **D3 — two slices** | **REJECTED — the Architect's shape is three slices** | Folding the plumbing into the adapter slice makes one slice carry a refactor, an adapter, the registry, the settings surface, five call-site wirings, the attribution ids and the privacy pins — a slice whose failures mix two concerns. And the plumbing-only slice is **not** vacuous when it carries the settings read-back, the gateway test at production parity and the attribution separation: all three are $0 and all three are observable. The local slice is gone under the owner's ruling and B3 — the blueprint is amended instead, not built |
| d2 | **Missed option D6 — a zero slice first (attribution + test alignment)** | **ACCEPTED — it converges with the Architect's S1** | S1 *is* D6, plus the fallback wiring and the settings surface: per-surface provider ids, the gateway test widened to the production classes with its inverted assertion fixed, the sixth caller brought in, and the landing contract specified |
| d3 | **Risk: the owner confirms the seam reading** | **ACCEPTED** | It is an owner item and the stage waits on it — the literal reading is **false today** (measured by SG-247), so the confirmation is a confirmation of the seam reading |

## The Architect's picks after Phase B (what goes to the owner)

**D-R14-a — the second cloud provider: OpenAI directly, with a provider id that is never `openrouter`.** The
shape and the separation, not the price: the tree already speaks the OpenAI-compatible `POST …/chat/completions`
shape **twice** (the existing reader `providers/opencode_go.py:32-33`, the payload builder `:167-186`; the
scene client `services/scene/openrouter.py:1-6`), and the raw-httpx precedent (`opencode_go.py:258-263`, one
POST send site, no vendor SDK) means the adapter adds **no SDK and no lockfile change**. The separation is the
reason: the `OPENROUTER_API_KEY` slot was declared **for scene rendering** (`config.py:41-44`, `sg_scene_cap`
`:45-47`), the scene ledger id is the literal `"openrouter"` (`scene/openrouter.py:247`), and the scene cap
filters `provider == "openrouter"` with **no month filter** (`:288-297`) — so a photo adapter under that id or
that key would couple two features and two budgets with the very mechanism the caps exist to separate. A
**direct** vendor key is a different vendor, a different account and a different failure domain from the primary
gateway (`opencode.ai/zen/go/v1`), which is what a *fallback* is for; the rates sit in the same class as today's
table (`opencode_go.py:44-45`), so the estimate arithmetic transfers best of the candidates. What the pick
contains: the adapter, **its own rate table and estimator**, a **provider id that is never `openrouter`**, the
**shared-base extraction** (the measured **119** vendor-neutral lines) in the same slice, and the key as the
owner's own action. What it does not contain: the cap values, the probe, and the money authority.

**D-R14-b — the local option: no provider-level local destination now (the "local option" is the existing local
signals path).** The owner's ruling (**no local models on the server**) is closed, and inside it the only
honest readings are: the **existing local OCR/barcode signals path**, measured present in the served image
(`docs/worklogs/SG-238_g3_image_libs.log:4-6`; SG-247 re-measured it in a container: `tesseract 5.3.0`,
`libzbar.so.0` loadable, both imports OK), or **nothing** at the provider level. The provider layer therefore
gets cloud providers only, and `fallback_id` must never resolve to anything local. Two consequences carried into
the stage: **a local landing must never fabricate** (the deterministic double returns `fake-item`,
`fake.py:63`), and **`invalid_json` must surface** — it stands for a prompt or schema bug, not an outage — so
production's retryable set **loses `invalid_json`** (`reader.py:61-63`), which also aligns production with the
gateway test's current assertion (`test_provider_gateway.py:85-91`); while no local destination exists, **no
per-destination retryable sets are needed at all**. The **blueprint is amended** rather than silently inherited:
"local fallback" (`blueprint.md:318`) and "optional local provider adapter" (`:533-539`) are re-defined to the
no-model reading. The **trigger to revisit** is named: a measured OCR/barcode quality check on the owner's own
photos (their consent) — if the quality is good, a later slice may wrap that same path as the fallback
destination, with **no model**.

**D-R14-c — the caps and the money authority: caps set explicitly before any metered call, no standing money
authority, every probe separately authorised — stated in input terms, with the dollar ceiling derived from the
estimate's upper bound for that input.** The estimate is a pure function of the bytes and the prompt
(`opencode_go.py:151-164`: input tokens ≈ prompt bytes + the image's base64 length, output bounded by
`max_tokens`), so the probe's authorisation is stated in **input terms** — the image's bytes and base64
length, one call, one model — **and** the dollar ceiling is **derived** from that input's bound, never chosen:
a ceiling **below** the bound fires the probe's own pre-call refusal (`router.py:71-74`) and vetoes the probe
(a 3 MB image bounds at ≈$0.60, a 2–4 MB photo at ≈$0.40–0.80, the 20 MB upload cap at ≈$4, and
`redact_image` re-encodes to PNG **without resizing**, `redaction.py:16-21`). The probe's image is **one of the
owner's photos, or a thumbnail of it, with their consent** — the product will send their photos to this vendor
anyway — or a repository fixture if they prefer, which measures only the overhead. The probe's acceptance is
**the measured cost against the estimate** and **the probe's own job-linked ledger rows** — never the household
total, which mixes text, photo and scene spend (`reader.py:292-306`: the household's job-linked rows **plus
every `job_id IS NULL` row**, and chat, planning, analytics, synthesize and scene all write `None`). **No
standing monthly cap until the per-surface attribution exists.**

**D-R14-d — the stage: three slices, $0 first, spend last, no local slice.** **S1 — the seam and the wiring,
$0:** the settings surface for the provider and fallback ids (with the model whitelist); the fallback-id
plumbing at the four router sites **and** `services/enrich/synthesize.py:276-285`, which bypasses the router
entirely; **per-surface provider ids, so the monthly cap stops charging one surface's spend to another**; the
gateway test widened to the production retryable classes with its **inverted `invalid_json` assertion** fixed;
and the **landing contract specified** — what the pipeline and the review queue do when the fallback also fails
or lands empty. Exit: the configured ids resolve in the live process and read back through the settings surface;
the fallback fires for every production retryable class and **not** for `invalid_json`; the monthly cap's reader
separates the surfaces. **S2 — the second adapter, $0:** the **shared base** (the measured 119 vendor-neutral
lines) plus the adapter, its **own rate table and estimator**, the registry gate (a registration condition
that is not a key, `reader.py:97`), the key seam, the **deliberate** privacy-pin updates
(`tests/test_privacy_audit.py:237-248`, `:251-267`) and the conformance test. Exit: the provider is switchable
by configuration with $0 tests green. **S3 — the caps and one authorised metered probe:** exit: the measured
cost against the estimate, the probe's own ledger rows read back, and the caps set from the measurement. **No
local slice** — under the owner's ruling and the pick above there is nothing to build there, so the blueprint is
amended instead. And the exit condition is read as **a stable seam with per-vendor adapters** — the literal
reading is **false today** (measured), and that reading needs the owner's confirmation.

## The owner's items this round (four, deliberately not bundled)

1. **The vendor and its key** — the vendor (🟡) and the key that funds it (🟠, secrets; the key's scope must be
   photo-only, never the scene key).
2. **The blueprint amendment** — the local-fallback language under the ruling (🟡; a product document, the
   owner's).
3. **The money shape, the probe's image and one read-only ledger query** (🟠).
4. **The stage shape and the exit-condition reading** (🟡).

Each carries its own review line; none rides inside another.

## What the Architect adds to the review's own list

1. **Production's retryable set should lose `invalid_json`** — the schema bug must surface, and the gateway
   test already asserts it should not fall back. One line of product behaviour, and it removes the need for
   per-destination retryable sets entirely.
2. **The monthly cap must separate surfaces before any standing cap** — and the scene cap's provider filter
   (all-time, no month filter) means the photo adapter must carry a **different provider id**, or the scene cap
   would charge the photo spend.
3. **The probe's authorisation should be stated in input terms** (bytes, base64 length, one call, one model) —
   the estimate is a pure function of those, so the input cap *is* the spend cap, and the dollar figure follows.
4. **Backlog W5** — the review's missed option B5 (a local deterministic validator: cloud proposes, local
   disposes) is a real, empty slot in the tree and belongs in the backlog, not in this stage.
