# SG-124 — Jina price foundation: report (CHANGED)

**Dispatch-ID:** SG-124 · **Coder:** opencode · **Effort:** high · **Model:** opencode-go/deepseek-v4.1-flash
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE REF:** `origin/automation` · **BASE_RESOLVED:** `b041ee98858dd5b6280aac2c490a83e649240a87` · **START_HEAD:** `b041ee98858dd5b6280aac2c490a83e649240a87` · **WORK_HEAD:** the commit carrying this report + worklog + verify log (resolved hash published in the receipt note below).
**Spend (real $):** $0.000000 — zero metered calls on any path; no Jina search call; no key read.
**Contract:** recorded `0.37.0` == published `1acd7730e5fa6de5b7403aacce71207e9946461d`; source path `/home/andrei/storagegenie-contract/{VERSION, HEAD}`; `RULES.md` sha256 `18de7fd7…` == payload `RULES.sha256`.

## MODEL + EFFORT provenance
- EFFORT `high` read from process arguments: `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>` (`output/dispatch/SG-124.launcher.sh`).
- MODEL `deepseek-v4.1-flash` read from provider metadata in the run log (`> build · deepseek-v4.1-flash`, `output/dispatch/SG-124.log`). No model id rode the trigger (contract-legal omitted-model subset, D302).

## (a) Issues / deviations / surprises
- **F-SG124-1 (premise false):** the packet's G0 premise "`enrich/` carries no cost symbol" is **false** as written — `synthesize.py` already carries `INPUT_USD_PER_1M`, `OUTPUT_USD_PER_1M`, `estimate_text_cost`, `SYNTHESIS_PER_CALL_CAP_USD`. The narrower `jina.py` premise is **true**. Resolved by **extension, not duplication**: the Jina rate is a distinct vendor/unit added beside the Jina client; `estimate_text_cost` is untouched.
- **F-SG124-2 (egress deviation):** `https://jina.ai/pricing/` is now **HTTP 404**; the current page is `https://jina.ai/api-dashboard/pricing/` (found via the vendor sitemap). The page is an SPA whose top-up pack prices are loaded from `https://dash.jina.ai/api/v1/product`. This needed extra **keyless** GETs beyond the packet's "single GET" (page-moved clause). No auth header, no key, no metered call; all GETs listed in the worklog.
- **F-SG124-3 (rate ambiguity handled):** no single official token→USD price is stated; the 17 quoted packs span **$0.0169–$1.00 per 1M tokens**. The constant uses the base *currently-offered* pack (`1B tokens` for `$50.0` USD → **$0.05/1M**), the higher of the two offered, as a conservative bound. The spread is stated in the constant comment.
- **F-SG124-4 (floor not ceiling):** the vendor says a search costs "**starting from** 10,000 tokens" — a minimum, not a proven ceiling on tokens. The estimator default is that minimum and accepts a larger caller bound; it does not claim to cap tokens.
- **F-SG124-5 (minor, CO-08/CO-83):** `AGENTS.md` binds no `{{VENV}}`, `{{VTEST}}`, `{{EVIDENCE_DIR}}`; I used the real `backend/venv/bin/python` and the packet-named commands, and committed mypy output into this verify log instead of an `{{EVIDENCE_DIR}}` path. No value invented.
- **F-SG124-6 (carried, outside scope):** `STATE.md:2` still reads contract `0.36.0` while AGENTS/packet/checkout read `0.37.0`.
- **F-SG124-7 (minor):** the vendor's rate table labels the `s.jina.ai` row "Reader API"; its description ("Search the web…") and endpoint identify the Search API. No costing ambiguity.

## (b) Actions
- Changed paths: `backend/app/services/enrich/jina.py` (+37: `JINA_SEARCH_TOKENS_PER_REQUEST`, `JINA_TOKEN_USD_PER_1M`, `estimate_jina_search_cost`); new `backend/tests/test_sg124_jina_price.py` (+81). Evidence: `docs/worklogs/SG-124.log`, `SG-124_report.md`, `SG-124_verify.log`.
- Commits: work commit (code + tests + evidence) = `WORK_HEAD`; docs commit fills the receipt below. Push `origin automation`.
- No served path, no snapshot model/writer, no `provider_call` writer, no cap, no migration, no rebuild, no recreate, no container, no DB. No live leg.
- Retry count: 0. Test-command count: fail-pre 1, pass-post 1, targeted 1, candidate suite 1, base suite 1, base mypy 1, candidate mypy 1, ruff 1. Provider-call count: 0. Health: not run (packet declares no service/db and the slice is offline; the running container is untouched).
- Highest-impact action: sourcing the vendor rate **live** and pinning it to `$0.05/1M` × `10,000` tokens = `$0.0005` per search, proven by hand-computed arithmetic.

## G0 — vendor rate (source / unit / figure)
- **What does the vendor charge for one search, in what unit?** Search API (`https://s.jina.ai`): a fixed number of **tokens per request**, "starting from 10,000 tokens" → unit = per-request token credits.
- **Is the rate a named constant with provenance?** Yes: `JINA_SEARCH_TOKENS_PER_REQUEST = 10_000`, `JINA_TOKEN_USD_PER_1M = 0.05`, with the page URL + capture date (`2026-09-25T13:16:42Z`) + quoted figure in the comment.
- **Does the pure function convert a search to bounded USD?** Yes: `estimate_jina_search_cost(10_000)` = `10_000 × 0.05 / 1_000_000` = **$0.0005**. No clock, no network, no key.
- Capture URL + figure + unit quoted in `SG-124_verify.log` §1; the page's own pack-price source quoted too.

## G1 — constant + estimator + seen-to-fail
- Constant + estimator live in `jina.py` beside the request constants; no new import (`test_module_adds_no_served_path_import` proves no `app.api`/`app.models`/`app.services.providers`/`app.db` import).
- **Seen-to-fail (PG-EV-01):** `estimate_jina_search_cost(-1)` → `ValueError: negative_token_count: -1 tokens cannot be priced`. A perturbed-constant control (`JINA_TOKEN_USD_PER_1M=0.02`) makes the hand-computed assertion red (`got=0.0002`, expected `0.0005`) — the arithmetic, not the docstring, is the proof.

## G2 — tests + suite + empty diffs
- **FAIL-pre** (new test against immutable BASE in isolated worktree `/tmp/opencode/sg124-base`): `4 failed, 1 passed` (`AttributeError` for the 4 symbol-bearing tests; the import-surface test already passes on base). Raw in `SG-124_verify.log` §2.
- **PASS-post** (candidate): `5 passed`. Raw in §3.
- **Targeted** (every test file referencing `jina`): `111 passed`. Raw in §4.
- **Suite candidate:** `2 failed, 598 passed` (31.43s of 600s). **Suite base:** `2 failed, 593 passed` (31.39s). Same two reds = `tests/test_signals.py::test_generated_codes_…` and `::test_ocr_has_text_boxes_…` (OCR/barcode environment, **base-proved**). Raw in §5a/§5b.
- **ruff:** `All checks passed!`. **mypy app:** `Found 41 errors in 9 files (checked 90 source files)` on both base and candidate — no new errors; `jina.py` is not among the 9. Raw in §6/§7.
- **Empty served-path diffs:** `git diff BASE -- backend/app/api backend/app/models backend/app/services/providers backend/app/services/enrich/{snapshots,synthesize,client,scoring,__init__}.py backend/app/main.py backend/app/config.py` is **empty**; existing test files diff is **empty**; only `jina.py` + the new test changed. Raw in §8.

## Acceptance criteria check (PG-SC-09)
- Source / define / estimate — all three answered above; every criterion could fail (fail-pre red, adversarial raise, perturbed-constant red). **No vacuous pass**: the estimator is pinned by hand-computed `$0.0005`, not by its own docstring.
- No live call, no key touched, no served-path hunk; zero metered spend.

## Actual versus budget (units: seconds, live clock UTC; early legs approximate)
| Leg | Actual | Budget |
|---|---|---|
| G0 vendor sourcing/capture | ~180s (page had moved; extra keyless GETs) | 120s ordinary — **over** |
| G0 grep + G1 impl + adversarial | ~40s | 120s |
| G2 fail-pre/pass-post/suite/ruff/mypy | ~132s (suites 31.4s each) | 600s suite bound |
| G2 targeted + commit | ~28s | 600s |
| G3 files + receipt | from ~13:21:50Z | 600s overall |

No command was killed or timed out. The G0 leg exceeded the 120s ordinary bound because the named page had moved and its SPA sources pack prices from a second URL; reported as a deviation.

## Receipt (note on `refs/notes/storagegenie-coder-reports`) — pasted verbatim
<!--RECEIPT-SHOW-->
note=yes

## UNCLEAR
- **FIRST READ:** whether the vendor page would state a clean USD rate (it states tokens, not USD) and whether "enrich/ has no cost symbol" was literal (it is not — `synthesize.py` has one). Both were read, not assumed.
- **DURING EXECUTION:** the page moved and showed the Search cost in tokens only; I converted via the page's own quoted top-up pack. Which pack is "the" credit price is not stated, so I took the conservative higher of the two currently-offered packs and flagged the spread (F-SG124-3).
- **REMAINING:** the Jina rate is defined but **unwired** (by design) — the estimator is not yet consumed by the snapshot writer, `provider_call` ledger, or the enrich cap; that is the retention/wiring slice. The pack-price spread and the "starting from" floor (F-SG124-4) should be re-checked when wiring.
