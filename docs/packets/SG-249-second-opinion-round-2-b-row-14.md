# SG-249 — Second opinion round 2, Phase B (critique): attack the Architect's four picks on roadmap row 14

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**
**Provider: none.** No provider call, no metered probe, no model download, no key read, no spend. Target: **$0**.

## Why this exists

Phase A of this round (`SG-248`, blind) has reported. Its report is committed, **unedited**, at
`docs/worklogs/SG-248_report.md`. This phase attacks the **Architect's** picks — which agree with Phase A on two
decisions and differ on the other two — with evidence.

## The Architect's picks — carried VERBATIM

**D-R14-a — the second cloud provider: OpenAI directly, with a provider id that is never `openrouter`.** The
pick follows the shape and the separation, not the price: the tree already speaks the OpenAI-compatible
`POST …/chat/completions` shape **twice** (the existing reader `providers/opencode_go.py:32-33`, the payload
builder `:167-186`; the scene client `services/scene/openrouter.py:1-6`), and the raw-httpx precedent
(`opencode_go.py:258-263`, one POST send site, no vendor SDK) means the adapter adds **no SDK and no lockfile
change**. The separation is the reason: the `OPENROUTER_API_KEY` slot was declared **for scene rendering**
(`config.py:41-44`, `sg_scene_cap` `:45-47`), the scene ledger id is the literal `"openrouter"`
(`scene/openrouter.py:247`), and the scene cap filters `provider == "openrouter"` with **no month filter**
(`:288-297`) — so a photo adapter under that id or that key would couple two features and two budgets with the
very mechanism the caps exist to separate. A **direct** vendor key is a different vendor, a different account and
a different failure domain from the primary gateway (`opencode.ai/zen/go/v1`), which is what a *fallback* is for;
the rates sit in the same class as today's table (`opencode_go.py:44-45`), so the estimate arithmetic transfers
best of the candidates. What the pick contains: the adapter, **its own rate table and estimator**, a **provider
id that is never `openrouter`**, the **shared-base extraction** (the measured **119** vendor-neutral lines) in
the same slice, and the key as the owner's own action. What it does not contain: the cap values, the probe, and
the money authority.

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

## What Phase A found (read the report itself; this is a pointer, not a substitute)

`docs/worklogs/SG-248_report.md` — its four picks (**A3** OpenAI directly · **B3** no provider-level local
destination · **C1** caps first with a derived per-probe ceiling · **D3** two slices with D5 resolved as the
seam reading), its four missed options (a shared-base enabling slice before naming the vendor · a local
deterministic **validator** that confirms cloud output instead of producing it · authorising the probe by
**input** rather than dollars · a zero slice for attribution and test alignment before the adapter), and its
four riskiest unverified premises. It also names **two gaps the Architect must put to the owner**: the
blueprint's local-fallback language is unmappable under the ruling, and the landing contract is undefined.

## G1 — Read

1. `AGENTS.md` — the top section (project identity and configuration) and its "Project rules" section;
2. the context pack `docs/reviews/2026-10-24-row-14-round-2-context.md`;
3. the Phase A report `docs/worklogs/SG-248_report.md`;
4. the Architect's record `docs/worklogs/SG-248_architect.md`;
5. every file the context pack names in its tables.

**LIST every file you read beyond those.** Not optional: it is how the Architect detects inputs you were not
meant to have.

## G2 — The critique

Against the Architect's four picks, produce:

- **(a) THE STRONGEST CASE AGAINST EACH PICK, with evidence** — a quote or a `file:line` or a measurement. A
  claim you cannot evidence is labelled `opinion`. For each pick, name the strongest objection **the Architect
  did not raise** — Phase A's objections are already on the table.
- **(b) THE STRONGEST CASE FOR EACH PICK**, with the same evidence standard.
- **(c) A PREMISE OF EACH PICK THAT IS UNVERIFIED** — say what would be true if it were false.
- **(d) THE OBSERVATION THAT WOULD SETTLE EACH DISAGREEMENT** — the single measurement or read that decides.
  Name what it is, where it would run, and what result would mean which pick. **Do not perform it.**

**Also required:** judge the **three-slice stage** against Phase A's two-slice shape and against the options
Phase A named (the shared-base enabling slice first; the attribution-and-test-alignment zero slice first) — say
which of the three shapes you believe is right and why; and state what the owner should be told, in one line per
decision, if the picks stand. Say plainly if the Architect's picks cannot all stand together.

## G3 — Report

Your final message **is** the report (the engine publishes it; read it back with `SG-249 --status`; the
Architect copies it unedited to `docs/worklogs/SG-249_report.md`). Required shape:

- `SG-249` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- the answers (a)–(d) for each of the four decisions;
- your judgement on the stage shape, and the owner lines;
- a short closing statement of what you read and deliberately did not use.

Do not restate the context pack, Phase A's report, or the Architect's record at length — your value is the
evidence against and for, the unverified premises, and the settling observations.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial
  anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- **No provider call, no metered probe, no model download.** Name what a probe would cost and prove; do not run
  it.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the
  lane's `RUN_BUDGET_S`.
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live
  clock at execution (`PG-IC-07`).
- **Do not simply choose between the Architect's picks and Phase A's.** If the honest answer is "none of them",
  say so and name what beats all of them.

## Acceptance criteria

- (a)–(d) present for each of the four decisions, with at least one evidence item (quote or `file:line` or
  measurement) in (a) and (b), or an explicit `opinion` label; (c) names a premise with what-would-be-true-if-
  false; (d) names one concrete observation and its decision rule.
- The extra-files list is present and complete for your run.
- A judgement on the stage shape (the Architect's three slices, Phase A's two, and the two options Phase A
  named), and the owner lines.
- `PB-3` vacuity: an objection without evidence, labelled `opinion`, does not satisfy (a); "the picks are fine"
  does not satisfy the phase — the phase's whole purpose is a disagreement with evidence.

## Report

Destination: final message (engine-published; the Architect copies it unedited to
`docs/worklogs/SG-249_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You
publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote
nothing.
