# SG-155 — Scene T0: OpenRouter client seam + catalogue/envelope proof, read-only $0

## RECOVERED CODER REPORT — authored by the SG-156 recovery run from first-hand re-verification

**Dispatch:** SG-155 (original work, commit `461c96f`) — recovered by SG-156.
**Coder of the original run:** opencode · **Model:** `opencode-go/deepseek-v4.1-flash` · **Effort:** `high`
(process arguments of the original run, committed in `docs/worklogs/SG-155.log:3-4`: `/proc/1598239/cmdline` =
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high`;
engine `bash /usr/local/lib/dispatch/run-coder SG-155`).
**Authorship (honest):** this file was written 2026-10-09T14:16Z by the **SG-156** recovery run (opencode, same
model, effort `max`) — the original SG-155 process was killed at `elapsed=budget=2100s` in its receipt phase
before writing any report. Every load-bearing fact below is either a committed byte at `461c96f` or first-hand
output of SG-156's re-verification (`docs/worklogs/SG-156_verify.log`, `docs/worklogs/SG-156_t0recheck.log`);
the SG-156 packet's summary was used as hypotheses only, each re-checked.
**BASE ref requested:** `automation` → **resolved base:** `442d85b` (SG-155 packet commit = SG-155 start HEAD;
the SG-155 run's push was `442d85b..461c96f`).
**WORK_HEAD:** `461c96f55ab81dafa13f8dd08560e3007ec66815` (`461c96f`).
**Contract echo:** `0.44.1` — recorded in `AGENTS.md` at `461c96f`; host checkout
`/home/andrei/storagegenie-contract/VERSION` = `0.44.1`; `RULES.md` sha256
`f2565b1cb289cff8ddb03dfeeefcec1a02e615fa6c54d940933be48eb4f99d4f` == payload `RULES.sha256` (re-read by SG-156).
**Type:** read-only T0 client seam + live catalogue/envelope proof. No served-code change, no datastore, no
restart, no migration, no deploy. **Production writes: 0. Spend: $0.000000.**

---

## What the slice delivered (all re-verified by SG-156 against `461c96f`)

### G1 — client seam (`backend/app/services/scene/`)

`__init__.py` (7 lines, package docstring) + `openrouter.py` (**188 lines** — SG-156 `wc -l` confirmed 188).
- `OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"`, `SCENE_ENDPOINT_URL = .../api/v1/chat/completions`.
- `resolve_openrouter_key(explicit=None)`: explicit > `settings.openrouter_api_key` > env > `None` (Jina seam
  shape, `services/enrich/` precedent).
- `build_scene_request(photo_ref, brief, image_model, orchestrator, *, spend_cap_usd=None)`: returns the exact
  sendable dict (`method/url/headers/json`); `tool_choice: "required"`, exactly one
  `openrouter:image_generation` tool, `max_tool_calls: 1`, T0-PINNED `stop_server_tools_when`; headers carry
  **no** `Authorization` (key added at send time only); photo enters as message `image_url` content, never as
  query text.
- Loud refusal constructors `missing_key() / refused_consent() / over_cap(...)` → `SceneRefusal` values, never
  exceptions (`PG-SC-03`).

### G2 — config + example env

`backend/app/config.py` +7 lines: `openrouter_api_key: str | None = None` and `sg_scene_cap: float | None =
None` (both off-by-default, jina-field comment shape). `.env.example` +1 line: `OPENROUTER_API_KEY=` (name
only, never a value). Byte-verified by SG-156 at `461c96f`.

### G3 — live legs T0a/T0b, $0, read-only (re-confirmed fresh by SG-156)

- **T0a** `GET https://openrouter.ai/api/v1/models` — 12 image-output entries: **10 real image-generation
  models** + 2 `openrouter/auto*` router pseudo-models; per-model pricing verbatim in `SG-155_t0live.log`.
- **T0b** `GET https://openrouter.ai/openapi.json` — `stop_server_tools_when` = array (`minItems: 1`) of five
  discriminated condition types: `step_count_is`, `has_tool_call`, `max_tokens_used`, `max_cost`,
  `finish_reason_is`; and the reference-image answer: the server tool "generates images from text prompts",
  its config accepts all image_config params + a `model` field, and `input_references` is declared only on the
  standalone `ImageGenerationRequest` → on the chat-completions server-tool path the tool is
  **text-prompt-only** (the asset is carried by orchestrator vision).
- SG-156 re-fetch (2026-10-09T14:13–14:16Z): slugs, prices, 5 stop types and the reference-image answer all
  **MATCH** (`docs/worklogs/SG-156_t0recheck.log`, verdict line) — no drift.

### G4 — gates (original evidence committed; re-run by SG-156)

- Fail-pre: collection error `ModuleNotFoundError: No module named 'app.services.scene'`
  (`docs/worklogs/SG-155_failpre.log`, committed) → Pass-post: 12 passed (`docs/worklogs/SG-155_passpost.log`).
- Full suite (original): `2 failed, 661 passed in 33.65s` (`docs/worklogs/SG-155_verify.log`) — the two reds are
  the `test_signals` environment class (pyzbar/libzbar and tesseract absent).
- ruff clean; mypy `41 errors in 9 files`, **none in `app/services/scene`** (delta 0).

---

## T0-PINNED for T1b (verbatim; re-confirmed fresh 2026-10-09T14:13–14:16Z)

Image-output models (10 real + 2 router pseudo), `image_output` price per unit:

| slug | image_output |
|---|---|
| `google/gemini-2.5-flash-image` | 0.00003 |
| `google/gemini-3-pro-image` | 0.00012 |
| `google/gemini-3-pro-image-preview` | 0.00012 |
| `google/gemini-3.1-flash-image` | 0.00006 |
| `google/gemini-3.1-flash-image-preview` | 0.00006 |
| `google/gemini-3.1-flash-lite-image` | 0.00003 |
| `google/gemini-nano-banana-2.1` | 0.00003 |
| `openai/gpt-5-image` | 0.00004 |
| `openai/gpt-5-image-mini` | 0.000008 |
| `openai/gpt-5.4-image-2` | 0.00003 |

`openrouter/auto` and `openrouter/auto-beta` are router pseudo-models, not image models.

Stop conditions (required fields): `step_count_is:{step_count:int}` · `has_tool_call:{tool_name:str}` ·
`max_tokens_used:{max_tokens:int}` · `max_cost:{max_cost_in_dollars:number}` ·
`finish_reason_is:{reason:str}`. Any condition firing halts the loop (OR), and when set the array overrides
`max_tool_calls`.

Reference image: **text-prompt-only** on the server-tool path (unchanged).

Orchestrator candidates (10, same values as SG-155, all MATCH on re-fetch): `inclusionai/ling-3.0-flash-vl`
0.000000021/0.0000000616 · `qwen/qwen3.7-flash` 0.00000003/0.00000013 · `google/gemma-3-12b-it`
0.00000005/0.00000015 · `openai/gpt-5-nano` 0.00000005/0.0000004 · `amazon/nova-lite-v1`
0.00000006/0.00000024 · `qwen/qwen3.5-flash-02-23` 0.000000065/0.00000026 · `bytedance-seed/seed-1.6-flash`
0.000000075/0.0000003 · `nex-agi/nex-n2.5-pro` 0.000000075/0.00000025 · `prism-ml/ternary-bonsai-2-27b`
0.000000075/0.0000005 · `google/gemma-3-27b-it` 0.00000008/0.00000045.

---

## Judgments (decisions embodied in the delivered code, endorsed on re-verification)

- Stop conditions: `step_count_is: 1` is always present (one render per request); `max_cost` is appended only
  when a cap resolves (explicit arg > `sg_scene_cap`) — policy value, not hardcoded; uncapped by default.
- The key enters at send time only; a test serializes the built request with the env key set and proves the key
  material is absent (`test_builder_carries_no_key_material`).
- Image model and orchestrator are parameters — config, not code (D7 swaps names).
- Photo enters as image content; a test proves it never enters the text part
  (`test_photo_never_enters_the_text_part`).

## Money

$0.000000. The only network activity in the slice: two public, keyless GETs (catalogue + OpenAPI). No
Authorization header sent (0 on both, re-verified), no chat/render call, no key needed or used.

## Original-run death and receipt status (why this file exists)

Killed by the engine at `elapsed=budget=2100s` (`killed=term`) while writing logs/report; the work commit and
push had already completed. No `Dispatch-ID` receipt exists for SG-155; the notes ref
`refs/notes/storagegenie-coder-reports` carries only the engine's kill-path note `Partial-Receipt-ID: SG-155`
(never a positive receipt — the origin of the `FLAG:TRUST` on SG-155's rating). SG-156 wrote this report and
published its own `Dispatch-ID: SG-156` receipt referencing this verification.

---

## UNCLEAR

- **FIRST READ:** whether "two shortlist slugs" in the SG-155 packet meant a 2-model shortlist or the whole
  image-model list. Resolved by recording the full list (10 real + 2 routers) with prices; T1b gets the full
  table, so either reading is satisfied.
- **DURING EXECUTION (this recovery):** the packet's premise `suite 2/649→2/661` — only the `2/661` side is
  evidenced in committed logs; the 649 base count is not reproduced by any committed byte (a collection-error
  fail-pre log carries no total). SG-156's own re-run gives `2 failed / 661 passed`, consistent with the
  post-state. No action owed; flagged for premise precision.
- **REMAINING:** none for SG-155's T0 scope. Downstream: T1b (SG-158) consumes the T0-PINNED block above; the
  comparison slice (SG-157) re-runs this T0 scope on the queued coder/model/effort.
