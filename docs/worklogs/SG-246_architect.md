# SG-246 — Architect record (Phase B of the row-14 second opinion, run on 2026-10-24)

**Trigger:** `SG-246 coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh agent=plan` (read-only lane; the same reviewer as Phase A and as the W1 review). The lane returned `exit 0`.
**Status verb read-back:** `result=done id=SG-246 inactive`; the published report was fetched with `SG-246 --status` and copied **unedited** to `docs/worklogs/SG-246_report.md` (17178 bytes, the report body between the `debug-report-begin` / `debug-report-end` markers).
**No provider was called, no model downloaded, no spend occurred** — in the lane.

## The Architect's disposition of every Phase B finding

| # | Finding (Phase B) | Disposition | Why |
|---|---|---|---|
| **a1** | **Against OpenRouter: concentration, not diversification.** The `OPENROUTER_API_KEY` slot was declared **for scene rendering** (`config.py:41-44`, SG-155) with its own scene spend cap (`sg_scene_cap`, `:47`) and a frozen envelope (`scene/openrouter.py:17-38`). Putting the photo fallback on OpenRouter as well leaves **both image surfaces on one vendor and one key** — one outage or one key revocation kills scene rendering and the photo fallback together. Also: the "same shape" economy is **part-copy** — vendor-neutral logic (usage guard, think-strip, estimate shape, budget guards, `opencode_go.py:70-164`, `:298-309`) sits inside the vendor file with no shared base, so a second adapter duplicates ~150 lines and two guard behaviours that can diverge silently | **ACCEPTED** | The citation checks out (`config.py:41-44` names the key as the scene-render key; `sg_scene_cap` is its own cap). Two consequences for the pick: the vendor choice becomes **conditional** (the key's authority must extend beyond scene rendering, and the spend must be attributable separately), and slice 2 gains a requirement: **extract the vendor-neutral logic into a shared base before the second adapter**, so the two cannot diverge silently (G-A7: a duplicated guard is a future defect) |
| **a2** | **Unverified premise:** that the owner-placed OpenRouter key's authority extends from scene rendering to photo fallback — one key funding two capped surfaces (`sg_scene_cap` vs `sg_per_job_cap`/`sg_monthly_cap`) with client-side-only attribution; mixed spend under one key misattributes against whichever cap is checked first | **ACCEPTED** | This is a **secrets** item (G-K2): the key's scope is the owner's, not the Architect's. It becomes one of the owner's decision items |
| **a3** | **Settling observation:** read the scene ledger writer (`scene/openrouter.py` ≈`:800-885`) and `models/provider_call.py`'s columns — do scene rows land in `provider_call` with `job_id=None`? If yes, scene spend already flows into the photo monthly cap through the unattributed pool (`reader.py:300-306`), the concentration objection becomes budget-grade and favours a different vendor for photos; if not, concentration is availability-only and OpenRouter stands on shape economy | **ACCEPTED — dispatched** | It is a **code read**, not a database read, so it needs no owner permission: **SG-247** G3. The runtime magnitude of the unattributed pool is a separate, owner-approved, read-only query (it touches the app database) |
| **b1** | **Against L1: code presence is not availability.** Both local-signal paths are ImportError-guarded degradation — pyzbar missing → warning plus an empty list (`signals.py:102-111`); tesseract missing → warning plus `None` (`:205-216`). Nothing in-tree proves tesseract or libzbar in the served container, so "already in the tree" could mean landing on **empty observations** | **ACCEPTED IN PART — the availability part is already measured, the usefulness part is not** | Measured: `docs/worklogs/SG-238_g3_image_libs.log:4-6` — in the project's own image `tesseract 5.3.0`, `libzbar.so.0` at `/lib/x86_64-linux-gnu/`, and `pyzbar+pytesseract import ok`. The served container runs that image. So the *empty observations* risk is answered for the image; what is **not** measured is the OCR's usefulness on real photos, and the served container's own copy gets one read-only confirmation in **SG-247** G2 |
| **b2** | **Against L1: the two landing constraints are designed, not free.** `RouterConfig` carries exactly **one** retryable set (`router.py:30-36`, consumed at `:79`), so "local only for transport/outage, never `invalid_json`" while keeping `invalid_json` retryable for the cloud needs **per-destination error classes** (a router change) or narrowing the shared set, which changes all four call sites' cloud behaviour at once | **ACCEPTED** | The constraint stands, the mechanism is now specified: the router gains a **per-destination retryable set** (default = today's shared set, so cloud behaviour does not change). Narrowing the shared set is rejected — it would change cloud behaviour everywhere at once |
| **b3** | **Unverified premise:** that a non-fabricating landing ("no candidate proposal" or a labelled "no provider" outcome) can travel the current job pipeline unchanged — the existing skipped shapes (`reader.py:452-454`, `:472-479`, `{"status":"skipped","reason":…}`) may not be an acceptable landing contract; if not, slice 4 needs a new outcome contract plus caller handling — unpriced work | **ACCEPTED** | Slice 4's packet must name the landing contract and price the caller handling. Folded into the slice-4 requirements, not a new decision |
| **c1** | **Against $0.50: the ceiling is incoherent with the machinery that must enforce it.** Caps compare against the deliberate **upper bound** (`estimate_call_cost`, `opencode_go.py:151-164`: one token per base64 byte of the image plus the prompt), and `redact_image` does **not** resize — it re-encodes to PNG with the pixels preserved (`redaction.py:16-21`), and PNG meets or exceeds JPEG bytes. A 2–4 MB phone photo therefore bounds at **≈$0.40–0.80** at `$0.15/1M`, and the 20 MB upload cap bounds at ≈$4. A $0.50 per-job cap fires the probe's own pre-call refusal (`router.py:71-74`) — **the ceiling vetoes its own probe**; and the number is uncalibrated with no derivation in-tree | **ACCEPTED — the number is withdrawn** | Verified this turn: `estimate_call_cost` computes `input_tokens = len(prompt) + base64_len` (`opencode_go.py:162-164`) and `redact_image` saves PNG without resizing (`redaction.py:19-21`) — a 3 MB image → 4.0 M base64 chars → ≈$0.60 of upper bound. **$0.50 is withdrawn.** The replacement: the ceiling is **derived from the bound for the image actually probed**, and the probe's image is either a small repo image (bound ≈ cents) or one of the owner's own photos — and the owner's stored photos are a **declared sensitive surface**, so probing with them needs their explicit consent |
| **c2** | **Unverified premise:** that the probe's spend is cleanly attributable — the photo path writes job-linked rows (`reader.py:208-230`), but the SG-142 unattributed-pool fix (`:300-306`) counts **all** `job_id=None` rows (chat/planning/analytics writers) against **every** household; if that pool is non-zero on this single-household box, the household monthly total already over-counts and the probe's "the ledger proved the caps held" criterion conflates photo and text spend | **ACCEPTED** | The probe's criterion becomes **its own job-linked rows**, not the household total. The pool's magnitude is the owner-approved read-only query (SG-247's G3 answers the code question; the runtime magnitude stays for the owner) |
| **d1** | **Against slice 1: its exit is vacuous.** Threading `fallback_id` toward a configured `None` is verifiable only by reading (PB-3 risk); the gateway test already proves a fallback fires but under a **narrower** retryable set (`test_provider_gateway.py:43-56` = `{outage,timeout,rate_limited}`) than production (`reader.py:61-63` adds `transport`, `http_status`, `invalid_json`) — so three production classes stay untested. And **slice 4's exit is overspent**: the blueprint matrix across provider/fallback/local-fallback/budgets needs ≥3 metered legs, contradicting the single-probe discipline unless it runs on doubles (which proves nothing about measured cost) | **ACCEPTED — both exits amended** | Slice 1's exit becomes: **the configured fallback id resolves in the live process and is read back** (a read-back, not a fired fallback), and the gateway test is widened to the production classes so `transport`, `http_status` and `invalid_json` are covered. Slice 4's exit becomes: a **doubles-matrix for the routing shape plus exactly one metered leg for cost truth** |
| **d2** | **Unverified premise:** that the blueprint's exit — "changing providers needs configuration, not code" (`blueprint.md:539`) — survives a stage that by design ships code (adapter, registry gate, rate table, response-format branch, two pin updates). If the owner reads `:539` literally, slices 2–4 fail their own exit on delivery day | **ACCEPTED** | The exit condition is re-stated as **"a stable seam with per-vendor adapters"** and the owner confirms that reading — a one-line decision item |
| **d3** | **Settling observation:** a static, $0 **touch-list** — every file a second adapter MUST touch (registry gate `reader.py:90-105`, `RouterConfig` wiring ×4 sites, rate table + `estimate_cost`, the `response_format` branch, both privacy pins, the settings whitelist `settings.py:26`, the PUT limits `settings.py:39-41`) — decided **before** slice 1 is authorised. If the touch-list stays inside seam + adapter + pins, the "stable seam" reading holds; if any caller-logic edit is required (repair policy, ledger writers, outcome contracts), the `:539` exit must be renegotiated with the owner **before** slice 1 | **ACCEPTED — dispatched** | A static read, $0, and it decides something that would otherwise be discovered late: **SG-247** G1 |
| — | **The split is right; the sequence needs two amendments** (slice 1's exit vacuous → read-back exit; slice 4's exit overspent-or-vacuous → doubles-matrix + one metered leg). Without them, the honest alternative is folding slice 1 into slice 2 | **ACCEPTED** | Both amendments are folded into the pick below |

## The Architect's picks after Phase B (what goes to the owner)

**D-R14-a — the second cloud provider: OpenRouter, CONDITIONAL.** It stands on the shape economy — one
OpenAI-shaped POST today (`opencode_go.py:32-33`, `:258-263`), an OpenRouter client already in the tree
(`services/scene/openrouter.py`), a key slot already declared (`.env.example:5`, `config.py:44`) — and on the
fallback **direction** (a second model on the same gateway is not a provider fallback). **Three conditions:**
(i) the key's authority extends beyond scene rendering (the owner's item — secrets), (ii) scene and photo
spend stay attributable separately (SG-247 G3 answers where scene rows land; the runtime pool magnitude is an
owner-approved read), and (iii) the vendor-neutral logic is extracted into a **shared base** before the second
adapter, so the two cannot diverge silently. If (ii) fails, the pick changes to a **different vendor** — the
review names the concentration objection, and it stands.

**D-R14-b — the local option: L1 now, L3 as the routing destination, L2 closed.** Availability in the served
image is measured (`SG-238_g3_image_libs.log:4-6`); usefulness on real photos is not, and the landing must
never present a fabricated reading (`fake` returns `fake-item`, `fake.py:63`) nor absorb `invalid_json`
(`reader.py:61-63`) — the router gains a **per-destination retryable set** so the local landing sees only
transport/outage classes without changing cloud behaviour anywhere.

**D-R14-c — the caps and the money authority: caps first, no standing authority, per-probe ceiling, and the
number is derived rather than guessed.** **$0.50 is withdrawn** (it would have vetoed its own probe). The
ceiling is derived from the estimate's **upper bound for the image actually probed** — for a 2–4 MB photo that
is ≈$0.40–0.80, at the 20 MB upload cap ≈$4 — and the probe's image is either a small repo image or one of
the owner's own photos, which needs their consent (stored photos = sensitive surface). The probe's acceptance
is its **own job-linked ledger rows** plus the measured cost against the estimate, not the household total.

**D-R14-d — the stage: four ordered slices, $0 first, spend last, with both exits amended.** (1) fallback
plumbing with doubles, exit = the configured fallback id **resolves in the live process and is read back**, the
gateway test widened to the production classes; (2) the second adapter with its own rate table, the shared
base, the deliberate pin updates, and the touch-list from SG-247 as its ceiling; (3) caps calibration plus
**one** authorised metered probe; (4) local as the fallback destination — exit = **doubles-matrix for routing
shape plus exactly one metered leg for cost truth**. The stage's exit condition is read as **a stable seam
with per-vendor adapters**, and the owner confirms that reading.

## What the Architect adds to the review's own list

1. **The probe's image needs the owner's consent** if it is one of their photos — the stored photos are a
   declared sensitive surface (the project's own rule) and sending them to a second vendor is an outward-facing
   action. A repo test image avoids the question but measures a different cost shape.
2. **Slice 1 is worth keeping** now that its exit is a read-back — but only if the touch-list (SG-247 G1) shows
   no caller-logic edit is required; otherwise slice 1 folds into slice 2, as the reviewer said.
3. **The `local` landing's contract** (the `skipped` shapes, `reader.py:452-454`, `:472-479`) must be named in
   slice 4's packet, with the caller handling priced.
4. **The owner's own "local" intent** remains the one thing the code cannot answer: if "the local option" meant
   genuine offline photo understanding, L1 is a redefinition and only a measured L2 (or an explicit de-scope)
   answers it.

## Next

**SG-247** — a **read-only, $0 verification slice** carrying the review's three settling observations that need
no database and no owner permission: the static adapter touch-list (G1), the served-image dependency probe
(G2), and the scene-ledger attribution and retryable-set coverage reads (G3). It produces the evidence the
owner's four row-14 items need.
