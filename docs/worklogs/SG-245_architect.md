# SG-245 — Architect record (Phase A of the row-14 second opinion, run on 2026-10-24)

**Trigger:** `SG-245 coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh agent=plan` (read-only lane; the same reviewer as the W1 review). The lane returned `exit 0`.
**Status verb read-back:** `result=done id=SG-245 inactive`; the published report was fetched with `SG-245 --status` and copied **unedited** to `docs/worklogs/SG-245_report.md` (18884 bytes, the report body between the `debug-report-begin` / `debug-report-end` markers).
**Receipt:** the reviewer published no receipt note of its own; the record of this phase is this file and the committed report.
**No provider was called, no model downloaded, no spend occurred** — in the lane and in the pack.

## What Phase A picked

| Decision | Phase A's pick | Its riskiest unverified premise |
|---|---|---|
| **D-R14-a** vendor | **OpenRouter** (OpenAI-compatible aggregator) as the second cloud reader; not Google-direct, not OpenAI-direct, not Jina | that OpenAI-shape similarity implies **vision-extraction** equivalence (structured-output contract honoured, image tokenisation, rate card) |
| **D-R14-b** local | **L1 now, L3 as the routing destination, explicitly not L2 on the live host** | that fixtures-plus-OCR satisfy what the owner meant by "the local option" — and that landing on local at `invalid_json` is safe, when `invalid_json` is in `RETRYABLE_ERRORS` (`reader.py:61-63`) |
| **D-R14-c** caps and money | **caps set before any metered call; no standing money authority; each probe separately authorised with its own ceiling**; no probe in the lane | that the **estimate upper bound transfers to the new vendor** (`_estimate_call → 0.0` for a provider with no estimator, `reader.py:233-242`), and that the probe's spend lands in the ledger (the monthly check joins through `Job`, `reader.py:270-284`) |
| **D-R14-d** stage shape | **four ordered slices**: fallback wiring with doubles only → the second adapter with its own rate table and the deliberate privacy-pin update → caps calibration plus one authorised metered probe → local as the fallback destination | that "**configuration, not code**" is achievable — in practice a stable seam with per-vendor adapters, not zero code per vendor |

**Its missed options** (named by the reviewer, checked and recorded): a second **model through the same gateway** rather than a second vendor (D-R14-a) · local as a **build-time/offline eval harness only** (D-R14-b) · a **server-enforced `max_cost`**, a **single-use per-probe budget**, and **zero-spend calibration only** (D-R14-c) · **close or defer the row** (D-R14-d).

**Its structural judgement:** the four decisions must be **SPLIT, not one package** — "one package would let an L2-yes smuggle an always-on runtime onto the shared host and an uncapped-yes smuggle spend into a probe" (minimum split: vendor + fallback-first order · local meaning with the host rule explicit · cap values · per-probe spend authority, sequenced a→d→c→b-host).

**Blindness held:** the reviewer read the pack and its named files only, listed 5 extra files read (4 fully, 1 by search), and deliberately did **not** read the review ledger, any packet, `STATE.md`, `.env` values, or anything that could carry the Architect's lean.

## The Architect's own picks — carried verbatim into SG-246

**D-R14-a — which second cloud provider. OpenRouter as the second cloud provider, with the model id carried in
configuration; the key's provisioning is a separate owner item.** The pick follows the *shape*, not the price:
the existing reader is one OpenAI-shaped POST (`providers/opencode_go.py:32-33`, `:258-263`), OpenRouter speaks
the same shape, and the repo already carries an OpenRouter client and a key slot (`.env.example:5`,
`config.py:44`, `services/scene/openrouter.py`). The pick is also about the **fallback direction**:
`opencode-go` stays the primary and OpenRouter becomes the fallback — real vendor independence, because a
second *model* on the same gateway would not survive the vendor being down and is therefore not a provider
fallback at all. "Changing providers needs configuration, not code" (blueprint `:533-539`) then means: a
stable seam plus a per-vendor adapter plus a configurable model id — **not zero code per vendor** (the tree
already branches per model family, `opencode_go.py:63-67`). Key provisioning, cap values and probe spend are
**not** part of this pick.

**D-R14-b — what "the local option" means. L1 now, with L3 as the routing destination; L2 (a local model
served on the live host) stays closed.** "Local" = the deterministic no-provider path already in the tree (the
`fake` registry entry `reader.py:96` and `ScriptedProvider` `fake.py:82-130`, plus the local OCR and barcode
observations `signals.py:102-109`, `:205-245`), used as the offline/fallback landing; no always-on runtime, no
host change. Two hard constraints on that landing, which the reviewer's premise (d) forces: **a local landing
must never be presented as a reading** — `fake` fabricates `items: [{"name": "fake-item", …}]`
(`fake.py:63`), so a fallback that lands there must produce **no candidate proposal**, or an explicitly
labelled "no provider" outcome, never a fabricated item (the app's rule: never guessed); and **local must be
the destination only for transport/outage classes, never for `invalid_json`** — that class is in
`RETRYABLE_ERRORS` (`reader.py:61-63`) and stands for a prompt or schema bug, which must surface rather than be
absorbed by a fixture. L2 is **deferred, not rejected**: it needs the owner to change a host rule (VPS.md F4),
a stated memory budget, and a re-measure of the shared host (7.7 GiB, measured 2026-09-17).

**D-R14-c — the caps and the money authority. Set explicit caps before any metered call; grant no standing
money authority; every metered probe is separately authorised with a hard ceiling.** No probe in the review
lane. The caps exist and bind nothing today (`config.py:48-49`, both `None`), and the machinery already refuses
a pre-call estimate over budget (`router.py:71-74`) and checks the monthly ceiling from the durable ledger
(`reader.py:486-497`); consent already defaults to deny (`config.py:50`). The magnitudes are the owner's,
informed by the estimate arithmetic — and the estimate is a deliberate **upper bound**
(`opencode_go.py:151-164`), not a forecast, and it is **per adapter**: the new reader needs its own rate table
before any cap can bind on it (`_estimate_call → 0.0` for a provider with no estimator, `reader.py:233-242`).
The first probe's ceiling I propose as **$0.50 for one image, one model, one call** — a ceiling, not a
forecast; the measured cost is expected far below it, and the probe's job is to measure it against the
estimate. Two things the probe must prove before anyone says the caps held: the **measured cost against the
estimate**, and the **ledger row** for that probe (the monthly check joins through `Job`,
`reader.py:270-284`, and writers with `job_id=None` already under-count).

**D-R14-d — the stage shape. Four ordered slices, $0 first, spend last.** (1) **Fallback plumbing with test
doubles only** — the mechanism made reachable (`fallback_id` is hardcoded `None` at
`providers/reader.py:465`, `services/chat/service.py:425`, `services/planning/service.py:444`,
`services/analytics/service.py:597`) with **no production fallback configured**, so nothing can fabricate a
reading; exit: the fallback path is exercised in the production code path by a double, $0. (2) **The second
cloud adapter** (OpenRouter) with its own rate table, `estimate_call_cost`, registry entry, key seam, and the
**deliberate** update of the two privacy pins (`backend/tests/test_privacy_audit.py:237-248` the send-site
set, `:251-267` the `redact_image` sites); exit: the provider is switchable by configuration, $0. (3) **Caps
calibration plus one authorised metered probe** — exit: measured cost against the estimate, ledger rows read
back. (4) **Local as the fallback destination** (L1/L3) — exit: the blueprint's test demonstrated across
provider, fallback, local fallback and budgets (`:318`, `:533-539`). The stage's exit condition is read as **a
stable seam with per-vendor adapters** (the tree already branches per model family, `opencode_go.py:63-67`),
not "zero code per vendor".

**Structural position: the four decisions are split, not one package** — agreed with Phase A. The vendor and
the slice order can ride together; the local-host branch (L2) and the money authority stay separate items and
never ride inside a vendor-and-caps bundle.

## The Architect's disposition of Phase A's four picks

| Phase A pick | Disposition | Why |
|---|---|---|
| **OpenRouter** (a) | **ACCEPTED** | The shape argument holds and re-checked: one OpenAI-shaped POST today (`opencode_go.py:32-33`), an OpenRouter client already in the tree, a key slot already declared. The Architect's addition: the pick must also fix the **fallback direction** (a second model on the same gateway is not a provider fallback) and name that the exit condition means "a stable seam", not "zero code per vendor" |
| **L1 + L3, not L2** (b) | **ACCEPTED, with two constraints added** | Agree with deferring L2 — it needs a host-rule change, a memory budget and a re-measure on a shared 7.7 GiB box. The two constraints: a local landing must never produce a fabricated item (`fake.py:63` fabricates `fake-item`), and local must never absorb `invalid_json` (`reader.py:61-63`) — a schema bug must surface |
| **Caps first, no standing money authority** (c) | **ACCEPTED, with a ceiling proposed** | The machinery and the deny-by-default consent are already in place; the owner's own 2026-09-11 "no caps at first" is what this reverses, so it is an owner item. The Architect's addition: a concrete first-probe ceiling ($0.50, one image, one model, one call) and the two things the probe must prove — measured cost against the estimate, and the probe's ledger row |
| **Four slices, $0 first, spend last** (d) | **ACCEPTED, with one correction to slice 1** | The ordering holds. The correction: slice 1 wires the fallback **mechanism** with doubles and leaves **no production fallback configured** — pointing production at the `fake` double would fabricate readings, which is why the local-landing constraint from (b) applies to slice 1 as well |
| **Split the four decisions** (package vs split) | **ACCEPTED** | It is the right structure under G-K2: the host branch and the money authority cannot ride inside a vendor-and-caps bundle |

**The Architect's own residual uncertainty:** whether the owner's "local option" meant genuine offline
photo *understanding* (the reviewer's premise (d) for D-R14-b). If it did, L1 is a redefinition and the framing
is wrong — only a measured L2, or an explicit de-scope, answers it. That is the one place where the owner's
intent, not the code, decides.
