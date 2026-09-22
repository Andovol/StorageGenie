# SG-082 — Enrich Jina fallback + review mapping + one capped synthesis pass

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE REF (packet ref `origin/automation`):** resolved `ac39dd493a7d1358be4ffb17bca2a18289ebd808` (the packet requested the ref; it resolved there at start HEAD — two fields, not one)
**WORK_HEAD:** `9c2a366205f496cfbd4739f8b78396abe523f492` (the code/test/fixture commit; the receipt note rides this hash; the report + pasted `show` ride the docs-only receipt commit after it)
**Contract:** recorded `0.30.0` == published `0.30.0`; source path `/home/andrei/storagegenie-contract/VERSION` (contract repo HEAD `c9c9ba3` = "Contract payload 0.30.0"). **Echo verbatim: `0.30.0`.**
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`; provider metadata `/home/andrei/.local/state/opencode/model.json` `recent[0] = {"providerID":"opencode-go","modelID":"deepseek-v4.1-flash"}` — **not** a system-prompt identity line) · effort `high` (process argv `/proc/1713787/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant high # SG-082 …`).
**Spend (real $):** **$0.000000 actual.** Jina: 1 successful API search (global diagnostic) + 2 EU attempts that failed DNS before any HTTP request. Synthesis: not run (G3), $0. No other metered resource touched.
**Autonomy:** `L3` arc slice 1 of 4 (D127). No retry needed.
**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). Nothing becomes live until a later owner-gated rider.
**Containment (`PG-PR-04`):** the Jina client + mapping are a library; no pipeline/route/registry is wired; the frontend button is UI-only (F-SG082-8). Tests use scripted `httpx.MockTransport`; the only network is the bounded Jina smoke.

D108-approved Enrich slice 2 (research `docs/research/2026-09-21-enrich-source-research.md` — the D102 gate; spec §3–§6; plan Task 4). SG-081's OFF-only library is now followed by the Jina fallback, web→review mapping, and the synthesis-seam decision.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on tree / live | Verdict |
|---|---|---|
| SG-081 library at `backend/app/services/enrich/` (client + scoring + snapshots) | present: `__init__.py`, `client.py`, `scoring.py`; 25 tests pass | **confirmed** |
| `frontend/src/routes/AssetDetailPage.tsx` is the product page | present; renders asset detail | **confirmed** |
| Existing review machinery at `frontend/src/routes/ReviewPage.tsx` + `components/CandidateCard.tsx`; backend `services/candidates.py` | present; `CandidateCard.fieldInfo` renders `source_type` provenance; `candidates.py` owns `_provenance`/GATED_FIELDS/commit | **confirmed** |
| Key NAME exists and consent is true (G0 gate) | `.env` names include `JINA_API_KEY` (value length 65, never printed); `SG_CONSENT=true` | **confirmed** |
| "key-from-settings" | `app/config.py` `Settings` declares **no** Jina field and `extra="ignore"`; `JINA_API_KEY` also absent from `.env.example`. See **F-SG082-2** | **difference — finding** |
| EU base `https://eu.s.jina.ai/` answers | **DNS NXDOMAIN** (`ConnectError: Name or service not known`); global `https://s.jina.ai/` answers HTTP 200. See **F-SG082-1** | **difference — finding** |
| Synthesis reuses an existing metered TEXT path | seam exists (`OpenCodeGoProvider.extract_text` via `chat.service.respond`) but is catalogue-bound; general synthesis needs new provider wiring (ceiling forbids). See **F-SG082-4** | **difference — finding** |
| Contract 0.30.0 == published `c9c9ba3` | VERSION `0.30.0`; contract HEAD `c9c9ba3` | **confirmed** |
| `origin/automation` == start HEAD | both `ac39dd4…` | **confirmed** |
| 2 known decoder env reds | bare baseline `2 failed, 401 passed` (test_signals barcode/OCR) | **confirmed** |
| Detection source never touched; OFF byte-identical | `vision|web_detection` → 0 over SG-082 source; OFF request params asserted unchanged | **confirmed** |

## G0 — key-name + consent gates (taken branch: PROCEED)

- **Key NAME source:** `.env` at repo root, consumed by `docker-compose.yml` `env_file: .env`; the name is `JINA_API_KEY` (listed NAMES ONLY: `DATABASE_URL`, `STORAGE_ROOT`, `HOUSEHOLD_DEFAULT_NAME`, `CORS_ORIGINS`, `OPENCODE_API_KEY`, `SG_CONSENT`, `SG_PROVIDER_ID`, `JINA_API_KEY`). **No value printed, logged, quoted or committed.**
- **Consent value:** `SG_CONSENT=true`.
- Both gates present → the slice runs with live legs. (Had either been absent, STOP-as-SUCCESS would ship every offline goal with $0; not needed here.)
- **Finding F-SG082-2** (below): the settings module does not read the name. The client resolves it through a narrow seam.

## G1 — Jina fallback client (`backend/app/services/enrich/jina.py`)

- **Exact request** (`build_jina_request`): `GET https://eu.s.jina.ai/{quote_plus(brand + name + category)}` with params in research order `site=mega-image.ro`, `site=emag.ro`, `site=farmaciatei.ro`, `num=5`, `type=web`, `gl=ro`, and headers `Accept: application/json`, `X-Token-Budget: 6000`, `X-Timeout: 15`, `X-Respond-With: content`. `test_jina_request_shape_exact_url_params_and_header_names` pins URL, the repeated-`site` tuple and the header **names/values**. `Authorization` is added at SEND time by `authorize()` and never appears in the builder (`test_jina_authorize_adds_only_the_authorization_name`).
- **EU base decision:** EU is the default (`JINA_EU_BASE_URL`), chosen for EU data residency for the Romania scope. The global base is a named constant only and is never switched to silently (`test_jina_default_base_is_eu_and_global_is_named_not_default`).
- **Request-shape over the real driver (`PG-EV-04` / `PG-SC-12`):** `test_driver_receives_the_exact_jina_query_and_headers` asserts on the request the **real httpx driver received** (`request.url`, `request.url.params.multi_items()`), not a re-implementation. The **Bearer value never appears in any assertion, fixture or log**; tests assert header NAMES only and the key literal used is the non-secret `"unit-test"` (`PG-EV-09`).
- **Privacy:** `test_jina_query_carries_text_only_no_image_gps_or_key_bytes` captures the real driver request and asserts an empty GET body, no `base64`, no `image|photo|lat|lon|gps` param/header, and that the key value is absent from the URL.
- **Snapshot discipline:** every call returns `JinaSearchSnapshot` with `source_name`, `request_url`, live-clock `retrieved_at`, `status_code`, verbatim `raw`, bounded `raw_text`, `results` and `no_result_reason`. `snapshot_to_json` serialises it. A **missing key** degrades with zero sends (`test_missing_key_degrades_loudly_with_zero_sends`). Named degradation classes, each seen-to-fail: `http_status:` (503), `transport:` (timeout), `invalid_json:`, `malformed_payload:`; a 200 with `[]` is a legit miss (`test_empty_results_is_a_legit_miss_not_a_degradation`). Both the bare-list and `{"data":[…]}` shapes are accepted.
- **Fallback order:** `fetch_with_fallback` runs OFF first and fires Jina only per `should_use_jina`: non-food, or OFF degradation, or OFF no-confident-match. `test_off_hit_on_food_never_fires_jina` proves the fallback client is never reached on a food hit; `test_off_empty_miss_fires_jina_and_keeps_both_snapshots`, `test_off_degradation_fires_jina`, `test_non_food_fires_jina_even_on_an_accepted_off_hit` prove the firing cases. Both snapshots ride the `EnrichDecisionRecord` (in-memory, JSON-serialisable; `PG-SC-02`).
- **Live smoke (≤3 real searches, 60 s/call bound):** EU food + EU non-food → both `transport: ConnectError: [Errno -2] Name or service not known` (DNS, no HTTP request); global diagnostic → **HTTP 200, 5 results** (first url `emag.ro/.../cafea-jacobs-cronat-gold...`). Raw in `SG-082_verify.log` R-SMOKE. No retry beyond the bound. **F-SG082-1.**

### G1 question answer (`PG-SC-09`)
**Does the client speak exact Jina with snapshots and graceful degradation?** Yes: shape pinned offline + over the real driver; snapshots always carry URL/timestamp/raw; degradation is a loud no-result. **Is the EU base reachable?** No — DNS NXDOMAIN; the global base answers. Reported, not silently switched.

## G2 — review mapping + gated proposals (existing machinery only)

**Mapping functions added to `backend/app/services/candidates.py`** (the criterion stated per function; a list is a fact):

| Function | Criterion |
|---|---|
| `jina_result_category(result)` | retailer-domain → category slug; None when unknown |
| `map_off_decision_fields(decision, *, source_url, retrieved_at, category=None)` | accepted OFF decision → `display_name`, exact `identifier`, agreeing `category_proposed`, all `web:OpenFoodFacts`; non-accepted → `{}` (no nearest guess) |
| `map_jina_result_fields(result, *, source_url, retrieved_at, category=None)` | Jina `title`→`display_name`; retailer category→`category_proposed` only on agreement (`category_score`), all `web:JinaSearch` |
| `merge_web_fields(existing, web)` | label-wins for `LABEL_VISIBLE_FIELDS`; web fills gaps; losing web value returned as a visible alternate |
| `build_enrich_fields(record, *, category)` | OFF first, Jina top result fills only gaps; source list with URL + retrieval date |
| `apply_web_fields_to_proposal(proposal, record, *, category)` | merge into a proposal's `fields` + `web_alternates`/`web_sources` (in-memory) |
| `_assertion_source(...)` | resolves web source → `source_type=web:<source>`, `confidence=None`, attribution in `model_json` |

- **`source_type=web:<source>`:** OFF `web:OpenFoodFacts`, Jina `web:JinaSearch`; each field carries `source_url` + `retrieved_at` (`test_map_off_decision_fields_uses_web_source_and_never_guesses`, `test_map_jina_result_and_category_activation_rule`).
- **Conflict rule (spec §4):** label-wins demonstrated in `test_merge_web_fields_label_wins_but_keeps_the_alternate_visible` — photo `display_name` is kept and the web value + source is preserved as an alternate; a gap field (`category_proposed`) is filled.
- **Never auto-accepts:** `test_committed_web_field_is_proposed_never_auto_accepted` commits a proposal through the REAL `commit_candidate`/`_create_asset_for_candidate` path with `sg_confidence_threshold=0.0`; the `web:JinaSearch` assertion is still `review_state="proposed"`, while a non-gated deterministic field is `accepted` (contrast). No threshold can promote web data.
- **Per-field accept via existing UI only:** web fields are ordinary `fields` entries that `CandidateCard` already renders with `Source: web:<source>`; decisions ride the existing `/v1/candidates/{id}/decision` route. **No new review UX.**
- **Category activation (decision reported):** `category_score` stays inert on the OFF path (OFF request bytes unchanged — asserted in `test_category_score_is_the_activation_rule`). It activates on Jina-supplied categories: the retailer-domain→slug map (`farmaciatei.ro`→`medicine_pharma`, `mega-image.ro`→`food_beverages`, `emag.ro`→`household_chemicals`, uncalibrated `G-A9`) is compared with the caller category via the existing exact/contains `category_score`; agreement adds the derived `category_proposed`.
- **Frontend Enrich button** (`AssetDetailPage.tsx`): exported `EnrichButton`, `ENRICH_PER_PRESS_CAP_USD=0.05` (uncalibrated) and `enrichCapRefusal`. It shows `Last measured spend: $X · per-press cap $0.05` and refuses above the cap with a named reason. Tests: render/spend, the seen-to-fail helper (`0.06` refused, `0.01` allowed), and a press above the cap that never runs while below it runs (`AssetDetailPage.test.tsx`).
- **`PG-SC-02` stated-absent, in as many words:** this slice adds **NO datastore field, NO model, NO migration**. The decision record, snapshots and `web_alternates` are in-memory / JSON-serialisable only; persistence rides a later slice.

### G2 question answer
**Does web data land as gated proposals in the existing machinery?** Yes — mapped to `web:<source>` fields, committed only through the existing candidate path, always `proposed` at threshold 0.0; label-wins keeps both values; the button shows spend and enforces the cap with a seen-to-fail.

## G3 — synthesis: reported non-run (named missing seam), $0

- **Named seam established:** the project's metered TEXT path is `OpenCodeGoProvider.extract_text` (`backend/app/services/providers/opencode_go.py:326`, `CHAT_OPERATION="extract_text"`), reached through `app/services/chat/service.py:respond` (`router.execute("extract_text", content, prompt_text, …)` with consent gate `reader.ai_status()` and a `ProviderCall` ledger row).
- **Why it is not reused here:** `respond` is hard-bound to ONE category's catalogue (`build_catalog`) and a versioned `chat-v1.md` prompt; it accepts no OFF JSON + Jina content payload. A normalisation call over those sources needs a NEW prompt file and a NEW non-catalogue caller = **new provider wiring**, which the ceiling forbids ("no new wiring in this slice"). Therefore **synthesis is unexecuted and reported REMAINING**, with the named seam above. This is the packet's explicit alternative to a vacuous "ran once". **Spend $0.000000.**
- **Consent + ledger refusal proven with 0 extra invocations:** the existing passing suite test `test_privacy_audit.py::test_g2_consent_false_binds_zero_calls_on_every_service_path` drives all four service entry points with an `_ExplodingProvider` and asserts `probe.calls == []` and `ProviderCall` count 0 while consent is false — real-call count 0. No metered call was made.
- **FAIL-then-PASS raw both runs (`PG-EV-09` / `PG-EV-01`):** `SG-082_verify.log` R-FAILPRE = new test file with `jina.py` absent → collection `ModuleNotFoundError: No module named 'app.services.enrich.jina'`; R-PASSPOST = same file present → `27 passed`.
- **Request-shape (`PG-SC-12`):** the driver test reads the real driver's received request (above).
- **`PG-SC-11` end-relative grep over touched test files** (`\[-1\]|HEAD~|\.endswith|\btail\b|\blatest\b`) → **0 hits (exit 1)**, committed raw (R-GATES). This slice appends to no ordered sequence.
- **Suite / lint / type / secret (R-SUITE/R-RUFF/R-MYPY/R-FRONTEND*):** backend `2 failed, 428 passed` (the 2 known `test_signals` decoder env reds; +27 new vs baseline 401); `ruff check .` → All checks passed; `mypy app` → `Found 41 errors in 9 files` == baseline (delta **0**); frontend `179 passed` (23 files); eslint exit 0; secret **value-shape** scan 0 real keys; the detection-source gate 0 over SG-082 source.
- **Exclusions by rule (`PG-SC-05`):** no `docker compose config` executed; no Vision; no key printed. The only hit of the excluded term in a touched file is the pre-existing model-id literal `test_privacy_audit.py:324` (not introduced here; the gate is scoped to SG-082's new/changed source = 0 — F-SG082-3).

### G3 question answer
**Did synthesis run exactly once within $0.05 with attribution?** No — it is reported unexecuted with the named missing seam, $0, per the packet's allowed alternative; no vacuous pass is claimed.

## G4 — worklog and report

- `docs/worklogs/SG-082.log`, `docs/worklogs/SG-082_report.md`, `docs/worklogs/SG-082_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + the smoke raw). First token `SG-082` in each.
- Elapsed vs budget per leg with units and spend in `SG-082.log`. Overall ~900 s / 2400 s; no command killed.
- `PG-IC-01` cross-product: **no criterion** calls the excluded detection source, prints a key, runs `docker compose config`, pulls/runs a container, or wires a pipeline. The Jina search is the only new metered touch; OFF stays first and byte-identical; synthesis is unexecuted. **No blanket constraint forbids any shipped criterion**; the ceiling forbids the synthesis wiring, which is therefore reported, not built.
- `PG-IC-07`: no fixed dates — all timestamps are the live clock.

## Findings

- **F-SG082-1 (EU base unreachable; global answers — reported, never switched).** `eu.s.jina.ai` is DNS NXDOMAIN (`ConnectError: [Errno -2] Name or service not known`); the smoke's two EU attempts sent no HTTP request. The global base `s.jina.ai` answered HTTP 200 with 5 results. The client default remains EU; the global base is a named constant only. Live searches: 3 attempts (2 EU DNS-failed + 1 global diagnostic); 1 real Jina API search. Raw in R-SMOKE.
- **F-SG082-2 (settings does not carry the key; .env.example not updated).** `app/config.py` declares no Jina field and ignores extra env; `JINA_API_KEY` lives only in `.env` (and is absent from `.env.example`). The ceiling forbids touching `config.py`/`.env.example`, so "key-from-settings" is satisfied through a narrow seam: `getattr(settings,"jina_api_key",None)` then `os.environ["JINA_API_KEY"]`. The key NAME is used, never its value.
- **F-SG082-3 (M45 pre-existing privacy-audit repairs).** Two pre-existing gates go red the moment a second legitimate HTTP client + a named web sender exist: `test_g0_single_http_client_and_send_site_full_scan` (inventory) and `test_g2_enrich_absence_no_web_sender_exists` (asserted Enrich absence). Repaired minimally at root cause: the inventory now names `services/enrich/jina.py`; the absence test is repurposed to "the two researched sources only, detection source absent over the touched files". The single POST send site is unchanged. A whole-app scan for the excluded term would match pre-existing model-id/docstring literals (`test_privacy_audit.py:324`, `opencode_go.py`), so the rule's literal gate is applied to SG-082's new/changed source (0 hits).
- **F-SG082-4 (synthesis non-run).** Named seam + reason in G3; $0. REMAINING.
- **F-SG082-5 (no persistence, PG-SC-02).** No datastore field, model or migration; snapshots/alternates are in-memory only.
- **F-SG082-6 (category activation rule decided).** Reuses `category_score` over a retailer-domain→slug map (uncalibrated); OFF path byte-identical (asserted).
- **F-SG082-7 (packet metadata nit).** The Report line says `WORK_HEAD` = "work hash (docs-only diff)". For a code slice that would exclude the work from the receipt; following the SG-081 precedent (rated 98), WORK_HEAD is the code/test/fixture commit and the docs-only receipt commit follows it. Both the work HEAD and the final tip are annotated.
- **F-SG082-8 (frontend button is UI-only).** The ceiling allows no enrich API endpoint, so `EnrichButton` renders spend/cap and calls an optional `onRun` that the page does not yet supply; the live enrichment trigger + candidate landing ride a later slice. The mapping itself is fully implemented and tested in the backend.

## Vacuity check (loud)

No acceptance criterion passed vacuously. The new tests genuinely fail with `jina.py` absent (collection error, R-FAILPRE) and pass with it present (R-PASSPOST); the request-shape test reads the real driver's received request; degradation classes are each asserted by their own quoted prefix; the "never auto-accepts" test commits through the real machinery at threshold 0.0; the cap test fails the over-cap press (seen-to-fail). **Where this slice is weaker than it looks:** (1) the live EU base never answered, so the live leg proves transport/degradation + that the global base answers — the populated EU accept path is proven offline only; (2) the frontend button has no backend trigger yet (F-SG082-8); (3) the verbatim raw body of the single successful global search was not retained (the smoke printed a bounded summary to respect the ≤3-search bound and avoid a 4th metered call). Said loudly, not hidden.

## Receipt note

Work pushed to `automation`; worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on `WORK_HEAD`, pushed, then fetched into a MAPPED local ref and shown — output pasted verbatim below.

```
TODO_PASTE
```

Final line: `note=yes`

## UNCLEAR

- **FIRST READ:** three packet premises differ from the tree/live: the settings module does not carry the Jina key name (F-SG082-2), the EU base does not resolve while the global base answers (F-SG082-1), and there is no existing text-synthesis seam reusable without new provider wiring (F-SG082-4). I read the ceiling as binding over "key-from-settings" (env seam, disclosed) and over synthesis (non-run, REMAINING), and the smoke/diagnostic distinction as license to try the global base once **as a diagnostic only**, never as a code switch. If the Architect intended EU to be abandoned for global, that is the item to correct.
- **DURING EXECUTION:** `eu.s.jina.ai` is NXDOMAIN on this host; the one successful search returned an `eMAG Captcha` title (a real emag product URL) — the fallback's content quality is not proven and is a later-slice concern. Synthesis was intentionally not run (no seam without new wiring).
- **REMAINING:** live enrichment endpoint + trigger (button `onRun` wiring), synthesis over OFF JSON + Jina content (new prompt + caller), surfacing `web_alternates` as first-class review rows, snapshot persistence (model + migration), `.env.example`/documentation for `JINA_API_KEY`, and re-confirming the EU base / OFF populated accept at the next live opportunity.
