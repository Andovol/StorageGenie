# SG-081 — Enrich OFF fetch service: v2 search + deterministic scoring + snapshots

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE REF (packet ref `origin/automation`):** resolved `1d06c340bf119efd070456ad68cc0c3f964b4c8d` (start HEAD == `origin/automation`; the packet requested the ref, it resolved here — two fields, not one)
**WORK_HEAD:** `<WORK_HEAD>` (the code/test/fixture commit; the receipt note rides this hash; the report + pasted `show` ride the docs-only receipt commit after it)
**Contract:** recorded `0.30.0` == published `0.30.0`; source path `/home/andrei/storagegenie-contract/VERSION` (contract repo HEAD `c9c9ba3` = "Contract payload 0.30.0"). `.rules-cache/` is absent from this worktree (gitignored; SG-080 precedent) — the source read is the contract repo path. **Echo verbatim: `0.30.0`.**
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`; from provider metadata `/home/andrei/.local/state/opencode/model.json` `recent[0] = {"providerID":"opencode-go","modelID":"deepseek-v4.1-flash"}` — **not** a system-prompt identity line; argv carries no `--model`) · effort `high` (process argv `/proc/1713787/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant high # SG-081 …`).
**Spend (real $):** `$0.000000` actual. OFF is free and unauthenticated; no key, no header, no metered resource exists (`PG-IC-04` stated as not firing).
**Autonomy:** `L2` slice (1 retry available; not used).
**DATABASE: none. Restart: none. Deploy: none.** No datastore write, no migration, nothing becomes live (`PG-PR-04`).
**Containment (`PG-PR-04`):** the fetch is a library SG-082 will call. It is wired into no pipeline/API/router, so no running surface changed. Tests use scripted `httpx.MockTransport`; the only network is the bounded free smoke.

D108-approved Enrich slice 1 (research `docs/research/2026-09-21-enrich-source-research.md` — the D102 gate; spec §7; plan `docs/superpowers/plans/2026-09-21-ai-ingestion-enrichment.md` Task 3). Scope is **OFF ONLY**: v2 search, deterministic scoring, verbatim snapshots. No key read, no other source, no review mapping, no pipeline wiring, no LLM synthesis.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on tree / live | Verdict |
|---|---|---|
| Endpoint `GET .../api/v2/search` with search_terms/brands_tags/countries_tags_en=romania/page=1/page_size=10/fields=… | exact transport asserted (`test_request_shape_exact_url_params_and_order`) and a live 200 confirmed the API accepts it (§R-G4) | **confirmed** |
| `httpx` already used by the provider adapter; new dep is a STOP | `backend/app/services/providers/opencode_go.py:23` `import httpx`; `pyproject.toml:15,25` `httpx>=0.27` | **confirmed** |
| The tree is sync (`schemas.py` precedent) | `schemas.py:2` "Sync to match SG-025"; `opencode_go.py:251` uses `httpx.Client` | **confirmed** |
| `backend/app/services/enrich/` absent | absent pre-slice | **confirmed** |
| 2 known decoder env reds | bare-BASE stash run: `2 failed, 376 passed` — `test_signals.py` barcode/OCR reds | **confirmed** |
| Contract 0.30.0 == published `c9c9ba3` | VERSION `0.30.0`; contract HEAD `c9c9ba3` | **confirmed** |
| `origin/automation` == start HEAD | both `1d06c34…` | **confirmed** |
| Jina/Vision not touched or read | `jina|vision|WEB_DETECTION` → 0 hits in the new module; `JINA` → 0 hits (§R-GATES G-A/G-B) | **confirmed** |

**Two premise differences (findings, not obstacles), both in the packet's own metadata:**
1. The packet's "Guards invoked (`0.28.2` …)" parenthetical names `0.28.2` while the contract it records two lines above is `0.30.0`. Metadata only; the named guards are stable across those tags. I honoured the guards, not the stale parenthetical. `F-SG081-5`.
2. The scope ceiling says "anything else is a STOP" (only new `enrich/*`, ONE test file, fixtures, worklogs), but the acceptance requires the full suite green. Two **pre-existing** test-tree items fail the moment a second legitimate HTTP client exists, so green is unreachable without a minimal repair to each. I repaired them and report it loudly (`F-SG081-1`); a workaround inside my own test would have hidden a real latent leak.

## G1 — OFF v2 client (sync, free, snapshot everything)

Module: `backend/app/services/enrich/client.py` (split decision: `client.py` = HTTP + snapshot + degradation; `scoring.py` = pure formula; `__init__.py` = package doc only).

- **Exact request** (`build_off_request`): `GET https://world.openfoodfacts.org/api/v2/search` with params in research order `search_terms`, `brands_tags`, `countries_tags_en=romania`, `page=1`, `page_size=10`, `fields=code,product_name,brands,ingredients_text,nutriments,packaging,countries_tags_en`. `test_request_shape_exact_url_params_and_order` asserts URL, the full params dict and the key order. The live URL recorded in §R-G4 shows the same encoded query string.
- **Sync, reuse `httpx`, 10 s timeout:** `httpx.Client(timeout=httpx.Timeout(10.0))`; `DEFAULT_TIMEOUT_S = 10.0`; `test_default_client_builds_a_ten_second_timeout` captures the built client's `timeout.connect`/`timeout.read == 10.0`.
- **Real UA (placeholder-free):** `StorageGenie/0.1 (https://github.com/Andovol/StorageGenie; openfoodfacts API client)`. `test_user_agent_identifies_storagegenie_and_is_placeholder_free` asserts it is `OFF_USER_AGENT`, contains `StorageGenie`, and contains none of `example`/`placeholder`/`todo`/`changeme`/`test@`. Decision reported: the GitHub repo URL is the OFF-etiquette contact.
- **Snapshot everything:** every call returns an `OffSearchSnapshot` carrying `source_name`, `request_url` (the actual `response.request.url`), `retrieved_at` (live-clock ISO-8601 UTC), `status_code`, the verbatim `raw` body, `raw_text` (the degraded body, bounded to 2000 chars), `products` and `no_result_reason`. `snapshot_to_json` serialises it verbatim for a fixture or a worklog raw. `test_snapshot_records_url_timestamp_and_raw_body` + `test_snapshot_timestamp_uses_injected_clock` prove URL/timestamp/raw; §R-G4 records live snapshots.
- **Degradation WITHOUT raising (`PG-SC-07` all-candidates-eliminated shape):** the no-result form is an `OffSearchSnapshot` with `no_result_reason` set and `products == ()` — never an exception into a caller, never a silent empty. Four named classes, each seen-to-fail offline: `http_status: …` (5xx), `transport: …` (timeout/transport), `invalid_json: …` (non-JSON 200), `malformed_payload: …` (non-object / missing `products` / non-list). A 200 with `products: []` is a **legit miss** (`no_result_reason is None`) — explicitly distinguished from degradation (`test_empty_products_is_a_legit_miss_not_a_degradation`).
- **Privacy:** the request is brand+name TEXT only. `test_off_query_carries_text_only_no_image_gps_or_key` captures the real driver request and asserts an empty GET body (no image bytes), all param values are strings with no `base64`, and no param/header name contains `image|photo|lat|lon|gps|key|token`; `test_off_call_is_unauthenticated_and_has_no_key_material` asserts no `Authorization`/key/token header. Structurally the function signature accepts only `(name, brand)`.

### G1 question answer (`PG-SC-09`)
**Does the client speak exact OFF with snapshots and graceful degradation?** Yes: the transport is pinned byte-for-byte by a no-network shape test and confirmed by a live 200; every response (success or degraded) is a snapshot with URL + timestamp + raw body; degradation is a loud no-result, never an exception and never a silent empty.

## G2 — deterministic scoring (0.4/0.4/0.2, ≥0.6, margin ≥0.15)

Module: `backend/app/services/enrich/scoring.py` — pure, offline, no I/O (`test_scoring_module_is_pure_and_offline` asserts the source contains neither `httpx` nor `openfoodfacts`).

- **Formula (`D108` rule):** `score = 0.4*brand_score + 0.4*name_score + 0.2*(country_score + category_score)`. `brand_score` = 1.0 substring (case-insensitive) / 0.5 edit-distance-similar brand token (Levenshtein ≤ 2, both tokens ≥ 4 chars) / 0.0; `name_score` = token Jaccard; `country_score` = 0.5 when the product countries include Romania; `category_score` = 0.25 on category agreement. `score_candidate` is pinned on committed fixtures (`0.74` hit, `0.2` below-threshold) and the pieces are pinned independently (`test_brand_score_*`, `test_name_score_is_token_jaccard`, `test_country_score_romania_bonus`).
- **Accept rule:** accept the top iff `top.score >= 0.6` AND `margin (top − second) >= 0.15`; a single candidate has margin = its own score. Boundary pins are exact and two-sided: `test_accept_threshold_boundary_both_sides` (0.6 accepted, `0.5999999999999999` rejected as `below_threshold`) and `test_accept_margin_boundary_both_sides` (`0.9/0.75` → 0.15000000000000002 accepted; `0.9/0.7500000001` → 0.1499999999 rejected as `ambiguous_margin`).
- **Never a nearest-guess:** `select_candidate` returns `best=None` with a named reason for all three no-match shapes — `below_threshold`, `ambiguous_margin`, `no_candidates` (`test_select_candidate_no_nearest_guess_on_all_three_shapes`, using the committed ambiguous + below-threshold + empty fixtures). `rank_candidates` is deterministic (score desc, `code` asc tie-break).
- **Fixtures:** `backend/tests/fixtures/enrich/off_hit.json`, `off_ambiguous.json`, `off_below_threshold.json`, `off_empty.json` (2–3 required; 4 committed).

### G2 question answer
**Does the scoring accept only confident matches?** Yes: exact two-sided boundary pins at 0.6 and 0.15, and every non-confident shape returns an explicit no-confident-match with `best=None` — no nearest guess exists on any path.

## G3 — tests + gates

- **Module + ONE new test file:** `backend/app/services/enrich/{__init__,client,scoring}.py` + `backend/tests/test_sg081_enrich_fetch.py` (25 tests) + the 4 fixtures.
- **`PG-SC-02` fires as stated-absent:** this slice creates **NO datastore field** and wires **NO reader**. The fetch is a library SG-082 will call; scoring returns an in-memory `MatchDecision`. No model/migration/route touched — state it in as many words: **no new recorded field, therefore no read-back route to trace.**
- **FAIL-then-PASS raw, both runs committed (`PG-EV-09`, `PG-EV-01`):** §R-FAILPRE = new test file with the module absent → `ModuleNotFoundError: No module named 'app.services.enrich'` (collection error, exit 2); §R-PASSPOST = same file, module present → `25 passed`. Both in `SG-081_verify.log`.
- **Request shape (`PG-EV-04` / `PG-SC-12`):** `test_driver_receives_the_exact_query_text` asserts on the request the **real httpx driver** received (`request.url`, `dict(request.url.params) == EXPECTED_PARAMS`), not on a re-implementation; `test_request_shape_exact_url_params_and_order` asserts the shape with no network at all.
- **`PG-SC-11` (end-relative assertions over enrich/OFF):** grep `\[-1\]|HEAD~|\.endswith|tail|latest` over the new test file + fixtures → **empty, exit 1** (§R-GATES G-E). Verdict: this slice appends to **no** ordered sequence (no migration head, no registry, no tail-relative log check), so there is nothing to update; the grep is committed raw, not a promise.
- **Suite / lint / type / secrets:**
  - Full backend suite: baseline `2 failed, 376 passed` (bare BASE, stash-proved) → slice tree `2 failed, 401 passed`; the 2 reds are the same `test_signals` decoder env reds (`+25` = the new tests). Raw §R-BASELINE/§R-SUITE.
  - `ruff check .` → `All checks passed!` (§R-RUFF).
  - `mypy app` → `Found 41 errors in 9 files` == baseline (delta **0**, quoted) (§R-MYPY).
  - **Secret grep-gate (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken`) over the new + modified files:** all hits are code identifiers (`_tokens`, "brand token", Jaccard) and test literals (`"token"` in a forbidden-name tuple; pre-existing `test_opencode_go.py` usage keys) — **0 real secret shapes**, no value, no key (§R-GATES G-D).
  - **Jina never read:** `JINA` → 0 hits in the new module; `jina|vision|WEB_DETECTION` → 0 hits (§R-GATES G-A/G-B). The Jina key is not read on this path.
- **Exclusions by RULE with literal grep-gates (`PG-SC-05`):** `jina|vision|WEB_DETECTION` → 0; pipeline/API wiring `run_ai_extraction|router|register` → 0 in the new module; no prompt diff, no migration, no compose/`.env`/README/STATE/AGENTS/packet touched (§R-GATES G-C/G-F/G-G). The slice touches exactly: new `services/enrich/*`, the one new test file + fixtures, two required pre-existing test repairs (below), and `docs/worklogs`.

### G3 question answer
**Is the library proven without touching anything else?** Yes: the only production surface added is the new package; it is wired nowhere; the suite is green modulo the 2 base reds, ruff clean, mypy delta 0, secret gate 0. The two pre-existing test repairs are reported (`F-SG081-1`), not silent.

## G4 — exactly one bounded live smoke (only free GETs; failure is a finding)

≤3 real searches against `world.openfoodfacts.org` (read-only GET, $0, no key). Raw in §R-G4. Per-query outcomes:

| # | Query (brand / name) | Request URL | Status | Outcome class |
|---|---|---|---|---|
| 1 | Jacobs / Jacobs Cronat Gold (expected hit) | `…/api/v2/search?search_terms=Jacobs+Cronat+Gold&brands_tags=Jacobs&countries_tags_en=romania&page=1&page_size=10&fields=…` | **503** | degraded / loud no-result (provider-side) |
| 2 | Jacobs / Cronat Gold (ambiguous) | `…?search_terms=Cronat+Gold&brands_tags=Jacobs&…` | **503** | degraded / loud no-result (provider-side) |
| 3 | Zzz Brand / Zzz Nonexistent Product 9999 (expected miss) | `…?search_terms=Zzz+Nonexistent+Product+9999&brands_tags=Zzz+Brand&…` | **200** | miss/empty (legit empty, `no_result_reason=None`) |

**Finding `F-SG081-2` (provider-side):** OFF returned HTTP 503 with its HTML "Page temporarily unavailable" page for queries 1–2. Quoted raw with the client's bounded reason (§R-G4). This is a **finding, not a slice failure** (G1–G3 green). Query 3's live **HTTP 200** body is the real OFF v2 envelope (`count, page, page_count, page_size, products, skip`) with `products: []` — so the exact request shape **is accepted by the live API**, and the empty/miss path is real. No retry was issued (the packet bounds the smoke to ≤3 real searches); the degradation was already live during recon (two pre-slice `curl` probes also returned 503) and is recorded as such.

**Honesty about fixture provenance:** because OFF answered 503 for the two populated queries, the **product objects** in `off_hit/off_ambiguous/off_below_threshold.json` are authored to OFF's documented v2 field set (the requested fields) rather than captured from a live 200 this session; only the envelope keys were live-confirmed by query 3. The scoring proof therefore rests on committed fixtures + boundary pins, and the live leg proves transport/shape + degradation, not a live accept. Said loudly, not hidden.

### G4 question answer
**Does the real API answer?** Yes — one real HTTP 200 with the real OFF v2 envelope proves the request shape is accepted and the miss path is live; the two 503s are the provider-side finding. The live accept path could not be observed because OFF was degraded on the populated queries; it is proven offline.

## G5 — worklog and report (unconditional per `CO-57`)

- `docs/worklogs/SG-081.log`, `docs/worklogs/SG-081_report.md`, `docs/worklogs/SG-081_verify.log` (raw outputs + BOTH fail-then-pass runs + every captured gate + all smoke snapshots). First token `SG-081`.
- Elapsed vs budget (per leg, seconds): recon+baseline ~145 s / 120 s ordinary + 600 s suite-bound used 19.9 s · G1/G2 build+failpre/passpost ~65 s / 120 s (new tests 0.05 s) · G3 suite+lint+type+gates ~65 s / 600 s bound used 19.7 s · G4 smoke ~0.5 s network / 10 s per call · G5 ~120 s / —. **Overall 459 s / 1800 s.** No command hit its bound; nothing was killed.
- Contract echo + source path above. Spend **`$0.000000` actual**.
- `PG-IC-01` cross-product: no criterion calls Jina/Vision, reads any key, wires any caller, or touches the network beyond the 3 free OFF GETs + the git push; tests run the local suite only; no container pull/run.
- `PG-IC-07`: no fixed dates — all timestamps are the live clock.

### Question each criterion answers (`PG-SC-09`)
- **G1 — does the client speak exact OFF with snapshots and graceful degradation?** Yes (above).
- **G2 — does the scoring accept only confident matches?** Yes (above).
- **G3 — is the library proven without touching anything else?** Yes, with two reported pre-existing test-tree repairs.
- **G4 — does the real API answer?** Yes, one live 200 envelope; the other two are the provider 503 finding.
- **G5 — is the evidence committed, not merely reported?** Yes: report + log + verify log committed; both fail-then-pass runs and all raw gates committed.

## Findings

- **`F-SG081-1` (two PRE-EXISTING test-tree items block suite-green once a second legitimate HTTP client exists).** (a) `test_privacy_audit.py::test_g0_single_http_client_and_send_site_full_scan` hard-codes the single-HTTP-client inventory `{services/providers/opencode_go.py: ["import httpx"]}`; the new OFF client legitimately adds `services/enrich/client.py`. (b) `test_opencode_go.py::test_transport_and_http_status_legs_carry_no_usage` patches the **global** `httpx.Client` and restores it with `httpx.Client = httpx.Client` — at that point the attribute already **is** the patched class, so it leaks `_PatchedClient` into every later test, which is why the new client tests passed alone and failed in the full suite (`http_status: OFF returned HTTP 500: 'upstream exploded'`). Repairs: add the new file to the privacy inventory (the audit's security property still holds, now over two named clients); capture `real_client = httpx.Client` before the patch and restore that in `finally`. Both are 1–3 line changes, outside the packet's literal ceiling but required by the suite-green acceptance criterion. I chose the root-cause repair over a workaround in my own test (a module-level captured `httpx.Client` alias) precisely because the workaround would have hidden a latent global-state leak. Flagging the ceiling/acceptance tension for the Architect.
- **`F-SG081-2` (live OFF degradation).** Two of three smoke GETs returned OFF HTTP 503 (quoted in §R-G4). External/provider class; not a slice failure. The third query proves the live envelope and request acceptance.
- **`F-SG081-3` (category term inert on this path).** The formula carries `0.2*(country + category)` whole, but the packet's EXACT `fields` list omits `categories_tags_en`, and privacy keeps the query brand+name only, so `category_score` is always 0.0 in SG-081's real path. The parameter exists so SG-082/callers can supply category agreement; stated, not hidden.
- **`F-SG081-4` (brand similarity + UA, decided).** Brand "similar" (Levenshtein ≤ 2, tokens ≥ 4 chars) scores 0.5 per research §2 — beyond the packet's "exact/contains" shorthand but required for the research formula. UA carries the repo URL as the OFF contact (no placeholder).
- **`F-SG081-5` (packet metadata nit).** The "Guards invoked" parenthetical says `0.28.2` while the packet records contract `0.30.0`. Metadata only; guards are stable across the tags.
- **`F-SG081-6` (`PG-SC-11` scope).** The rule fires when a slice appends to an ordered sequence; SG-081 appends to none, so the grep is empty (raw committed). Verdict, not a promise.

## Vacuity check (loud)

No acceptance criterion passed vacuously. The G1–G2 tests genuinely fail with the package absent (`ModuleNotFoundError`, §R-FAILPRE) and pass with it present (§R-PASSPOST); the request-shape test reads the real driver's received request, not a re-implementation; the degradation classes are each asserted by their own quoted prefix; the boundary pins are exact and two-sided; the scoring-purity test reads the real source. **The one place this slice is weaker than it looks:** the live smoke did not exercise a populated OFF accept (two 503s), so the accept path is proven on committed fixtures only — stated in G4, not hidden. The two suite repairs are reported with their root cause; neither hides a failing gate.

## Receipt note

Work pushed to `automation`; worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on `WORK_HEAD`, pushed, then fetched into a MAPPED local ref and shown — output pasted verbatim below.

```
<RECEIPT_PASTE>
```

Final line: `note=yes`

## UNCLEAR

- **FIRST READ:** the scope ceiling ("anything else is a STOP") and the acceptance ("full backend suite green modulo the 2 known decoder env reds") collide the moment the new OFF client exists, because two PRE-EXISTING test-tree items (a hard-coded single-HTTP-client inventory and a global `httpx.Client` leak) go red. I read suite-green as the binding, specific criterion and repaired both minimally (F-SG081-1), rather than STOP the slice or hide the leak behind a workaround. If the Architect intended the ceiling to win, that is the item to correct.
- **DURING EXECUTION:** OFF returned HTTP 503 on the two populated smoke queries, so the live API confirmed only the envelope and the transport, not a populated accept. I did not retry beyond the ≤3-search bound; the accept path is proven offline (fixtures + boundary pins).
- **REMAINING:** the new module is a library — nothing calls it yet. SG-082 owns Jina fallback + review mapping + pipeline wiring; the category term stays inert until a caller supplies/captures `categories_tags_en`; the fixtures' product objects are authored to the real field set (envelope live-confirmed, products not captured live this session) and should be re-confirmed at the next live opportunity.
