# SG-099 — Enrich synthesis prompt + non-catalogue caller (report)

**Dispatch-ID:** SG-099
**Coder / effort:** `opencode` / `high` (read from process arguments: `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`) — **model: cli-default** (no model id sent; omitted per policy; read from process args, never the system-prompt identity line).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE (requested ref `origin/automation` resolved):** `75ee1fc410740ce069f648e1aa1445f42f18c0f1`
**WORK_HEAD:** `0edcb89d545d265617a6546f3a3f950dcea6edf7` · **Report:** `docs/worklogs/SG-099_report.md`
**Contract echo (verbatim):** `0.33.0` — recorded in `STATE.md:4` (`**Version:** \`0.33.0\` (D129 adoption 2026-09-23: checkouts \`e8f8113\` + \`999e94c\` + \`b232b84\` oldest-first, installed \`18de7fd7…\` = payload at all versions — clean)`) and `AGENTS.md:4` (`Rule-set version this project records: **0.33.0**`). Published-side re-hash **UNEXECUTED**: `.rules-cache/` is absent on this host (gitignored, launcher-populated) and `origin` carries no `contract*` ref — see F-SG099-3.
**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). No migration: `models/` + `alembic/` diff empty.
**Spend (real $):** **$0.00135585 quoted** for the captured live leg (leg 2) + **one unquantified billed leg** (leg 1, usage present but body not retained) ≈ **$0.0027 worst-case actual**, versus the **$0.05** per-call bound and the **$0.05** one-call bound (`PG-IC-04`). Both legs were rejected by the adapter's empty-content guard and wrote **no** `ProviderCall` row. No other metered resource touched.

---

## Result in one line

The offline slice is **complete and green** (frozen prompt + non-catalogue caller + fail-then-pass tests + gates); the **live acceptance leg is NOT MET** — the configured metered TEXT path cannot complete with the default model because reasoning tokens exhaust `DEFAULT_MAX_TOKENS=2000` and the adapter rejects the empty content (named finding **F-SG099-1**). Production was never touched; all other criteria hold.

## G0 — consent / key-name gate: **GREEN** (gate open; live attempted)

- `reader.ai_status()` → `(True, 'enabled')`; `settings.sg_provider_id = opencode-go`; `OPENCODE_API_KEY` present (NAME only; `.env` key NAMES: `DATABASE_URL`, `STORAGE_ROOT`, `HOUSEHOLD_DEFAULT_NAME`, `CORS_ORIGINS`, `OPENCODE_API_KEY`, `SG_CONSENT`, `SG_PROVIDER_ID`, `JINA_API_KEY` — no value printed, logged, quoted or committed).
- The gate was open, so the live leg ran. It failed for a **provider/model configuration reason**, not a closed gate.

## G1 — frozen synthesis prompt: **MET**

- New `backend/app/services/providers/prompts/enrich-synthesis-v1.md`, `sha256=cb6b6890737f6dc9ad07af5a2b38381091bdb3317027a8656c8bf6ef79ba320d`, front matter `template_version: enrich-synthesis-v1`.
- Rules frozen: every fact cites `source_url` + `retrieved_at`; transcribe-only, never infer; brand-absent input must emit no brand fact; conflicts resolve **label-wins-visible** (restated, not re-decided); output is exactly one JSON object.
- **v1–v4 byte-identical:** `git diff --stat -- backend/app/services/providers/prompts/` → empty (all `extract-food/medicine/cosmetics-v1..v4.md` untouched; the only new file is the synthesis prompt). Raw in R-GATES.
- Question answered: *is the synthesis contract frozen and honest?* Yes — versioned file, loader reads the file itself, attribution + no-guess rules explicit.

## G2 — non-catalogue caller: **MET (unwired library)**

- New `backend/app/services/enrich/synthesize.py`:
  - calls `extract_text` **directly**; purity test proves the source contains no `build_catalog` and no `app.services.chat` import and exposes no `respond` (`PG-SC-12`);
  - consent refusal via `reader.ai_status()` **before any invocation** (`SynthesisRefusedError`, 0 invocations, 0 ledger rows);
  - per-call cap refusal: worst-case `estimate_text_cost` over `SYNTHESIS_PER_CALL_CAP_USD=0.05` raises `BudgetExceededError` **before any invocation** (seen-to-fail, 0 invocations); the estimate is also forwarded to `extract_text` so the adapter's own direct guard binds;
  - writes exactly **one** `ProviderCall` row (provider/model/template_version/input-hash/output/usage/cost/latency, `job_id=None`) on the caller's session; the synthesis is **RETURNED, never persisted** (`PG-SC-02` — consumption/endpoint/persistence is the next slice, said explicitly);
  - parses the answer into `SynthesisFact(field, value, source_url, retrieved_at)` and **refuses** a fact missing any attribution (`SynthesisFormatError`) and an invented brand from brand-absent input (`SynthesisGroundingError`).
- Question answered: *does the caller reach the metered path without the catalogue?* Yes, by construction and by test.

## G3 — tests + gates: **offline MET; live NOT MET**

- New `backend/tests/test_sg099_synthesis.py` — 16 tests, all driving the REAL prompt + REAL caller/parser through the reader seam with a scripted text provider (no network).
- **Fail-then-pass raw:** fail-pre = collection `ImportError: cannot import name 'synthesize'` (module absent, `exit=2`); pass-post = `16 passed in 0.91s`. Both raw in R-FAILPRE / R-PASSPOST.
- **Seen-to-fail (`PG-EV-01`):** missing `retrieved_at`/any attribution key → `SynthesisFormatError`; non-JSON answer → `SynthesisFormatError`; invented brand on brand-absent input → `SynthesisGroundingError`; consent-off and over-cap both 0 invocations.
- **Request shape (`PG-EV-04`):** `provider.texts[0] == build_synthesis_input(...)` (derived from the real builder, not re-typed) and `provider.prompts[0] == load_synthesis_prompt()`; fixture-derived needles (`Jacobs Cronat Gold instant coffee`, `Coffee`, `3274080005003`, `mega-image.ro`, `Cafea macinata`) and all four attribution slots (`OFF_URL/OFF_AT/JINA_URL/JINA_AT`) present; text only (no base64/image/key/Authorization).
- **Inputs:** committed `tests/fixtures/enrich/off_hit.json` + `jina_hit.json` (`PG-EV-07`). **Brand-absent** input is derived from the committed `off_hit.json` by removing `brands` (no committed brand-absent fixture exists — F-SG099-2), a deterministic transform, disclosed.
- **Gates:** ruff clean (new files); mypy `41 → 41` errors, delta **0** (checked 81 → 82 files); secret-pattern grep over changed files **0 real** (`sk-…`/`Bearer`/`AKIA`/`_API_KEY=`); full suite **2 failed, 486 passed** — the 2 failures are the known decoder env reds (`test_signals.py` pyzbar + tesseract absent), **stash-proved** at clean HEAD.
- **Live leg:** see below.
- Question answered: *does it work for real, once, within budget?* Offline yes; **live no** (F-SG099-1).

### The one live leg (60s bound each): attempted, rejected upstream

Ran the REAL caller → REAL `OpenCodeGoProvider.extract_text` (no fake), temp SQLite DB `/tmp/opencode/sg099/live.db`, `DATABASE_URL` overridden to the temp path before import.

- **Leg 1** (authorized first call): HTTP 200 body reached the adapter, `guard_usage` passed (usage non-zero → billed) then `guard_content` raised `ProviderError: provider returned empty content (empty-200 reject)`. Zero commits, clean tree. Body not retained on leg 1 (no recorder) — cost unquantified (F-SG099-5).
- **Leg 2** (the **one L3 retry**, transient class `invalid_json`, zero commits + clean tree, SG-084/090/091 precedent): identical failure; raw body captured (diagnostic `_post` wrapper only — the real network/parse ran):

  ```json
  {"id":"391bafc8-c207-4201-8212-42c95ae94f26","model":"deepseek-v4-flash-vision-exp",
   "choices":[{"finish_reason":"length","message":{"role":"assistant","content":"",
   "reasoning_content":"We need output JSON only. …"}}],
   "usage":{"prompt_tokens":1039,"completion_tokens":2000,"total_tokens":3039,
   "completion_tokens_details":{"reasoning_tokens":2000}}}
  ```

  `finish_reason="length"`, `content=""`, all **2000** completion tokens consumed by `reasoning_content`. Cost from the body's usage: `(1039×0.15 + 2000×0.60)/1e6 = **$0.00135585**`. No third call was made (retry spent; the failure is deterministic, not transient).
- **Production counts identical before/after:** `provider_call 17 / job 7 / candidate 6 / assertion 28 / asset 6` both times (read-only `mode=ro`). Temp DB only; production never opened.

## F-SG099-1 — **FINDING (blocks the live acceptance; needs an Architect/owner decision)**

The configured metered TEXT path is **unusable with the default model** `deepseek-v4-flash-vision-exp` and `DEFAULT_MAX_TOKENS=2000` (`backend/app/services/providers/opencode_go.py:36,190`): it is a reasoning model, so `reasoning_content` consumes the whole completion budget and `content` is empty; `guard_content` (`:71`) rejects the empty-200. Consequences: (a) the synthesis live leg cannot succeed within this slice's ceiling; (b) the empty-200 path is **billed but unledgered** — `guard_content` raises without attaching accounting, so no `ProviderCall` row records the spend (the vision SG-029 path happened to leave 885/1139 tokens for content; this synthesis prompt does not). **Recommended (out of this slice's scope):** raise `max_tokens` for text turns, select a non-reasoning text model for `extract_text`, and/or attach body accounting on the empty-content path. The Arc A live-re-confirm slices depend on this.

## F-SG099-2 — no committed brand-absent fixture

No fixture under `tests/fixtures/enrich/` is brand-absent, so the `PG-SC-07` test derives one from committed `off_hit.json` (removing `brands`). Disclosed; not a hand-authored blob.

## F-SG099-3 — contract published-side re-hash unexecuted

`.rules-cache/` is absent on this host (gitignored, launcher-populated) and `origin` carries no `contract*` ref, so the G-L1 published-side hash could not be recomputed. Recorded `0.33.0` echoed verbatim from `STATE.md:4` + `AGENTS.md:4`; the Architect's 2026-09-23 G-L1 clean is taken as the published side.

## F-SG099-4 — M45 existing-file touch (disclosed, minimal, root-caused)

`backend/tests/test_privacy_audit.py` `test_g2_web_senders_are_the_two_researched_sources` enumerates every app file whose lines name `jina`. The new `services/enrich/synthesize.py` legitimately consumes the Jina payload, so the allow-set was extended with it (and the docstring updated) — exactly the SG-082/097/098 precedent the test itself documents. Failing-test proof: full suite before the edit showed `3 failed` including this test; after, only the 2 known decoder reds remain. No other existing file touched.

## F-SG099-5 — leg 1 raw body not retained

The diagnostic `_post` recorder was added only for the retry, so leg 1's body (and exact cost) was not captured. Usage was present (billed), but the amount is unquantified. Reported rather than guessed.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| Frozen prompt exists with version | **MET** | `enrich-synthesis-v1.md`, loader test |
| v1–v4 byte-identical | **MET** | empty `git diff` over prompts dir |
| Caller invokes `extract_text` directly; consent + cap refusals seen-to-fail | **MET** | 16 tests, purity test |
| Output attributed per fact; brand never guessed when absent | **MET** | attribution + `SynthesisGroundingError` tests |
| Request-shape pins the exact cross-boundary payload | **MET** | `texts[0] == build_synthesis_input(...)` |
| Tests fail-pre/pass-post both committed raw | **MET** | R-FAILPRE / R-PASSPOST |
| Gates green (ruff clean, mypy delta 0, secret 0, suite modulo 2 known reds) | **MET** | R-GATES, R-STASHPROOF |
| ONE live call within $0.05 on temp DB with quoted actuals | **NOT MET** | 2 legs, both empty-200; quoted $0.00135585; F-SG099-1 |
| Production counts identical before/after | **MET** | 17/7/6/28/6 both times |
| No vacuous pass | **MET** | see below |

**Vacuous-pass check (`PG-EV-01`, loudly):** no criterion passed vacuously. The fail-pre genuinely failed (collection error); the request-shape test reads the real builder's output and the seam's received text; the refusal tests assert `invocations == 0` and `ProviderCall == 0` (not merely a raised exception); the attribution/brand tests feed deliberately-wrong inputs and assert the named exceptions in the same passing run; the live criterion is reported **NOT MET**, not papered over. **Where this slice is weaker than it looks:** the live metered path is proven broken, so `synthesize` has never completed against the real provider — the returned-attribution path is proven offline only.

## Cross-product / privacy (`PG-IC-01`, `PG-SC-05`)

No criterion demands persistence, endpoint wiring, deploy, restart, container acts, or a second metered call beyond the authorized retry. Only TestClient + host commands were run; no image pulled/run. Fixture TEXT only; key NAMES only; `docker compose config` never run. No fixed dates in code — the live leg read the clock; test attribution strings are sample data.

## Report note on the notes ref (receipt)

Work pushed to `automation` (`75ee1fc..0edcb89`), worktree clean. Note added on `WORK_HEAD`, notes ref pushed, and verified against the **fetched, mapped** ref. Executed, verbatim:

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   75ee1fc..0edcb89  automation -> automation

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-099 | Report: docs/worklogs/SG-099_report.md | Work-HEAD: 0edcb89d545d265617a6546f3a3f950dcea6edf7" 0edcb89d545d265617a6546f3a3f950dcea6edf7
note added exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   1f14dd5..a8aec13  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-fetched

$ git notes --ref=refs/notes/storagegenie-coder-reports-fetched show 0edcb89d545d265617a6546f3a3f950dcea6edf7
Dispatch-ID: SG-099 | Report: docs/worklogs/SG-099_report.md | Work-HEAD: 0edcb89d545d265617a6546f3a3f950dcea6edf7
```

No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. The final tip (the docs-only receipt commit) is dual-annotated too (note-anchor inoculation, SG-092 precedent). `note=yes`.

---

## UNCLEAR

- **FIRST READ:** every packet premise about the tree held (paths `opencode_go.py:326`, `chat/service.py:286/310/325`, `reader.py:100` all confirmed). The one premise that did not survive contact was the implicit assumption that the metered TEXT path works with the configured model — it does not (F-SG099-1). I read the ceiling as binding over any adapter/model fix, so I shipped the offline slice and reported the live leg, rather than editing `opencode_go.py` on a live-call failure alone.
- **DURING EXECUTION:** the first live call's empty-200 was the signal that this is a model/max-tokens problem, not a caller problem; the authorized retry confirmed it deterministically (`finish_reason="length"`, `reasoning_tokens=2000`, `content=""`). The M45 privacy-audit allow-set collision was self-caught by the full suite and fixed minimally. The absence of a committed brand-absent fixture forced a disclosed derivation.
- **REMAINING:** a decision on F-SG099-1 (raise `max_tokens` for text / choose a non-reasoning text model / handle `reasoning_content` + ledger the empty-200), then re-run the one live leg; endpoint + persistence consumption of the returned synthesis (`PG-SC-02`); a committed brand-absent fixture; `.env.example`/docs for the text model; the published-side G-L1 hash when `.rules-cache/` is populated.
