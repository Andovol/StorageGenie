# SG-249 — Architect record (round-2 Phase B of the row-14 second opinion, run on 2026-10-24)

**Trigger:** `SG-249 coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh agent=plan` (read-only lane; the same reviewer as every prior review round). The lane returned `exit 0`.
**Status verb read-back:** `result=done id=SG-249 inactive`; the published report was fetched with `SG-249 --status` and copied **unedited** to `docs/worklogs/SG-249_report.md` (26544 bytes, the report body between the `debug-report-begin` / `debug-report-end` markers).
**Receipt:** the reviewer published no receipt note of its own — the record of this phase is this file and the committed report.

**This round's picks are RECOMMENDATIONS, not decisions** (owner, D-1024-16: *"Don't make model decisions without asking me first."*). The review protocol requires the Architect's pick to be in the repository before Phase B — that is what makes the blindness work — so it stays, labelled. The vendor, the vision model id and the whitelist are the owner's.

## The Architect's disposition of every Phase B finding

| # | Finding (Phase B) | Disposition | Why |
|---|---|---|---|
| **a1** | **A3 creates a second personal-data recipient** while A1 reuses the recipient the product already sends photos to (the scene client already sends the asset photo as image content, `scene/openrouter.py:22-23`, `:781`/`:783`); a new vendor means a new key, account, billing, rotation, sub-processor and consent scope — so G-K2 prices A3 higher on the privacy/secrets surface, the opposite of my economy argument. **Neither phase weighed recipient-count** | **ACCEPTED — and it changes what the owner is asked** | Correct, and it is the kind of factor I had framed as a pure win. The trade is now stated honestly: **a new vendor buys structural budget separation and a distinct failure domain, and costs a new personal-data recipient; reuse costs no new recipient but couples the budgets** (the scene cap filters `provider == "openrouter"` with no month filter, `scene/openrouter.py:288-297`) and shares one key's blast radius. The id collision *is* avoidable (a distinct photo provider id); the key/billing coupling is not. **The deciding number is the pool's magnitude** — one grouped read on a **copy** of the app database, the owner's to approve |
| **a2** | **Unverified:** that OpenAI's vision usage/cost envelope matches `guard_usage`/`compute_cost` (`opencode_go.py:85-148`) and that its pricing holds at probe time — tiled or detail-based image tokens, cached-token lines, a different output price. Then the estimator is wrong and S2's ceiling is **circular** (the table calibrates the probe that calibrates the table) | **ACCEPTED** | S1 ships the adapter's **own** table and estimator **plus a fixture-level arithmetic proof** (kilobytes → cents) before any owner photo is authorised; S2's ceiling derives from **that** table, never from the gateway's |
| **b1** | **`invalid_json` in production is not "a prompt or schema bug" — it is the bucket for billed post-200 wire defects a second vendor could rescue.** The code covers empty-200 rejects (`opencode_go.py:80-82`; SG-099 burned the full 2000-token budget and returned empty content — a billed truncation), zero/absent usage (`:91-97`), non-JSON and non-object bodies (`:275-278`), no-choices (`:319`, text `:380-382`), stray `<think>` (`:101-111`), and billed shape rejections that **attach usage/cost/latency before raising** (`:114-136`, text `:387-393`); `_extract_one` writes an error ledger row for every failed attempt (`reader.py:421-429`) with the cost persisted when the error carries it (`:359-390`). So if `invalid_json` never retries, a primary's **paid** malformation is final — a user-visible failure after spend. The fix is to widen the **test**, not to narrow production | **ACCEPTED — the removal is WITHDRAWN** | My one-line deletion was wrong, and the review's evidence for it is in the code. Corrected position: **production keeps `invalid_json` retryable**; the gateway test is **widened to all six production classes** (new `transport`/`http_status` fake modes; `FakeProvider` has none today, `fake.py:20,38,41`); and the **offline billed-leg probe** (a recording double that raises `invalid_json` *with* usage+cost, run once under production's set and once under the test's set — no network, no key, no DB) decides whether a billed `invalid_json` leg is rescuable. If it is, the answer is a **billed-vs-unbilled split or per-destination sets**, not a deletion |
| **b2** | **Unverified:** that every production `invalid_json` is a bug a second vendor would repeat | **ACCEPTED** — it is now the subject of the offline probe above | The probe is the settling observation, and it is free |
| **c1** | **"Per-surface provider ids" as scoped separate nothing.** `_recorded_spend` has **no provider filter** (`reader.py:270-306`), `ProviderCall` has no household column (`models/provider_call.py:8-24`), and `None`-job rows can never satisfy the `Job` join — so distinct id strings without a **reader edit** leave the monthly cap mixing exactly as today, and this month's historical rows stay mixed (a backfill would be a sensitive-DB write, not authorised). My gate — "no standing monthly cap until the per-surface attribution exists" — therefore had **no definition of done**, and the stage blocked on a vacuous condition | **ACCEPTED** | SG-247's "the policy/ledger half stays untouched" box was wrong for this purpose. Corrected: the **ledger-reader edit is in scope** (a provider filter in `_recorded_spend`, or an equivalent separation of the unattributed pool), the fix applies **forward only**, and the gate is defined: *no standing monthly cap until the reader separates the surfaces, or the pool is measured empty* |
| **c2** | **Unverified:** that the new adapter's table and estimator exist and are right before the ceiling is derived from them | **ACCEPTED** | Same as a2: the fixture-level arithmetic proof comes with the adapter (S1), the ceiling comes from it (S2) |
| **c3** | **Settling observation:** the authorisation must name **redacted** bytes (PNG, no resize) — known only after `redact_image` runs — or the fixture arithmetic decides which | **ACCEPTED** | The probe's authorisation will name the redacted bytes' base64 length, and the packet will say so explicitly |
| **d1** | **S1 as scoped is unbuildable without S2's id, mixes the concerns it accuses Phase A's D3 of, and needs the ledger edit it disclaims.** The ids are validated against **registered** ids (`reader.py:108-114`, registry `:90-105`), so a read-back of a not-yet-registered id is a **string echo, not a resolution proof** (PB-3); widening the gateway test needs new fake modes (a test *feature*); bringing `synthesize.py` in adds fallback+budget to a text path that never had them; the shared base moved beside the adapter has **no baseline**, and the conformance rail checks only the signature (`test_provider_conformance.py:34-47`), not the guards — the exact silent-divergence risk. **"The split optimises slice count, not dependency order"** | **ACCEPTED — the stage shape is redrawn** | The dependency inversion is real and my S1's read-back could not have been a resolution proof before the adapter existed. And the review is right that suite-green on a pure move **is** an observation — my dismissal of a base-alone slice as "nothing changed" was wrong. New shape, in dependency order |
| **d2** | **Unverified:** that S1's three $0 exits are observable without the adapter | **ACCEPTED** | That is precisely why the shape moved |
| **d3** | **Settling observation:** a static repo check of how the ids are validated against the registry — either outcome redraws S1 | **ACCEPTED** | Answered by the redraw: the wiring and the ids now ride **with** the adapter, where the registered id exists |

## The corrected picks (recommendations, D-1024-16)

**D-R14-a — the second cloud provider: the owner's choice between a direct vendor and the recipient the
product already uses, with the trade priced.** A direct vendor (a new key, account, billing and **a new
personal-data recipient**) buys **structural budget separation** — a distinct provider id that the scene cap
cannot capture (`scene/openrouter.py:288-297`), a distinct failure domain from the primary gateway, no SDK and
no lockfile change (the tree already speaks `POST …/chat/completions` twice) — and its rates sit in today's class
so the estimate transfers best of the candidates. Reuse (the OpenRouter key the scene path already sends their
photos to) adds **no new recipient** but couples the budgets and shares one key's blast radius, and the id
collision is avoidable while the key coupling is not. **The deciding number is the unattributed pool's magnitude**
— one grouped read (`SELECT provider, count(*), sum(cost)` by provider and month) on a **copy** of the app
database, the owner's to approve. Whatever is chosen: **a provider id that is never `openrouter`**, the
adapter's **own rate table and estimator** plus a fixture-level arithmetic proof before any photo is
authorised, and the key as the owner's own action (a photo-only key, never the scene key).

**D-R14-b — the local option: no provider-level local destination; the local option is the existing local
signals path.** Inside the owner's ruling the only honest readings are the existing path (measured present in
the served image) or nothing at the provider level; the deterministic double fabricates (`fake-item`,
`fake.py:63`), so a landing there would present a reading that was never taken; and `fallback_id` must never
resolve to anything local. **Corrected from the earlier recommendation:** production **keeps** `invalid_json`
retryable until the offline billed-leg probe says otherwise, and the **test** is widened to all six production
classes (with new `transport`/`http_status` fake modes) rather than production narrowed. The blueprint's
local-fallback language (`:318`, `:533-539`) is **amended** to the no-model reading, not built. The trigger to
revisit stays named: a measured OCR/barcode quality check on the owner's own photos (their consent); if the
quality is good, a later slice may wrap that path as the fallback destination, with **no model**.

**D-R14-c — the caps and the money authority: caps first, no standing authority, every probe authorised in
input terms with the ceiling derived from that input's bound.** The authorisation names the **redacted** bytes
and their base64 length, one call, one model (the estimate is a pure function of those, `opencode_go.py:151-164`),
and the dollar ceiling is **derived** from that bound — never chosen, because a ceiling below the bound fires the
probe's own refusal (`router.py:71-74`) and vetoes the probe. The probe's acceptance is **the measured cost
against the new adapter's own estimate** and **the probe's own job-linked ledger rows** — never the household
total. **No standing monthly cap** until the ledger reader separates the surfaces, or the pool is measured
empty. The probe's image: one of the owner's photos, or a thumbnail of it, **with their consent** — or a
repository fixture, which measures overhead only.

**D-R14-d — the stage: three slices in dependency order, $0 first, spend last.**
**Z0 ($0, vendor-independent):** the gateway test widened to all six production classes with the new fake modes;
the **offline billed-leg probe** (the `invalid_json` disposition); the **landing contract** specified (what the
pipeline and the review queue do when the fallback also fails or lands empty); the **shared-base extraction on
its own** (the measured 119 lines, proved by a suite-green pure move); and the **fixture arithmetic** (kilobytes
→ cents; raw-versus-redacted disambiguated). Exits: pytest green, the contract read back, the diff confined to a
move, the arithmetic as numbers.
**S1 ($0, needs the vendor id):** the adapter with its **own rate table and estimator** and the fixture
arithmetic proof; the registry gate (a registration condition that is not a key, `reader.py:97`); the key seam;
the settings surface (provider/fallback ids, whitelist, validation against the registry); **all five wirings**
including the `synthesize.py` bypass; **the `_recorded_spend` provider filter**; the deliberate privacy-pin
updates; and the conformance test. Exit: provider and fallback switchable by configuration, $0 green.
**S2 (spend):** the caps and **one** authorised metered probe — input terms, the ceiling derived from S1's table,
the owner's image with consent or a fixture, the probe's own rows read back, the caps set from the measurement.
**No local slice** — the blueprint is amended instead. And the exit condition is read as **a stable seam with
per-vendor adapters**; the literal reading is false today (measured), and the owner confirms that reading or the
row cannot proceed.

## What the Architect adds

1. **The offline billed-leg probe is free and decisive** — it settles the `invalid_json` disposition with no
   network, no key, no database, no spend. It belongs in Z0.
2. **The ledger-reader edit is now in scope** — and it applies forward only; no backfill (a sensitive-DB write
   the owner has not authorised).
3. **Recipient count is a first-class cost** — it belongs in the decision item, not buried in the reason.
4. **The stage shape optimises dependency order, not slice count** — and the owner should see that reasoning,
   because it is why the shape changed twice.
