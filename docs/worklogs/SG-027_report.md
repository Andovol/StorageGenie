# SG-027 report — STOP: vision spike RED (wrong-schema), no adapter built

**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`,
**BASE** start HEAD `bcb59231ea96e46707c3363a1216ae0404daa80d` (ref `automation`, two fields as required).
**Model/effort per CO-78 from process arguments:** model `unknown` (env probe: `CODER=opencode`, `OPENCODE=1`, `OPENCODE_PID=1845563`; no model id anywhere in env/process metadata; ps grep empty — quoted, not guessed), effort `medium` (packet `coder:`/`effort:` head as dispatched).

## Verdict

G0 is RED, subtype **wrong-schema**: the single live call returned HTTP 200 with non-zero usage and JSON content, but the content does **not** validate through SG-026 `ExtractionOutput`. Per the packet (`Any other outcome (.../wrong-schema/...) = STOP`) and `PG-IC-03` stop-wins, the slice STOPS here: no adapter, no config change, no second live call, no model-hunt. `BLOCKED` commit + push + notes-ref note ship the evidence (`PG-EV-03`).

## What the vendor proved and did not prove (one live call, quoted)

- Endpoint facts re-verified live (`PG-IC-09`), not inherited: `POST https://opencode.ai/zen/go/v1/chat/completions` answers **HTTP 200** in **7.1s** for model `deepseek-v4-flash-vision-exp` with raw httpx, `stream: false`, `response_format {"type":"json_object"}`, identity headers (own `User-Agent` + ONE stable `x-opencode-session=storagegenie-sg027-run1`), `max_tokens 2000`. Auth scheme `Authorization: Bearer <key from backend env>` accepted (no 401/403).
- `usage` non-zero: `{"prompt_tokens": 868, "completion_tokens": 1361, "total_tokens": 2229, ...}` with 1232 reasoning tokens. Cost estimate recorded 0 (rate table has no entry; estimate, NOT billed truth).
- Vision works: the model read the synthetic label correctly (`Harvest Oats 500g`, `2027-03-15`, `best_before`, confidence 0.9 with two honest uncertainty reasons about the blurred lot region) and honored the unknowns *concept* — but with a **non-schema field**: content (scrubbed, no key material) was:

```json
{"items": [{"name": "Harvest Oats 500g", "expiry_date": "2027-03-15", "date_type": "best_before", "lot": null, "confidence": 0.9, "uncertainty_reasons": ["torn/partial print region: lot code obscured", "occlusion of the lot field prevents any legible reading"]}], "unknowns": ["items.0.lot"], "needs_evidence": false}
```

- Validation failure (quoted): `1 validation error for ExtractionOutput / items.0.lot / Extra inputs are not permitted [extra_forbidden]`. `finish_reason=stop`, so this is not truncation — the model invents a `lot` field the strict schema forbids.
- Redaction proof (pre-send, quoted): `format=PNG bytes=8354 exif_tags=0 gps_present=False` on the exact buffer sent. No EXIF/GPS left the machine; no personal image exists in this slice by construction.

## Why STOP instead of adapting

The failure sits in model schema discipline, not transport: a sanitizer or a retry could plausibly close it, but both are work the packet forbids building on a red spike ("nothing below starts on a red spike"; "never a workaround, never a second live call"). The Phase 2 premise returns to the owner with vendor evidence attached: either the prompt/schema side constrains the extra field (SG-026-side decision), the adapter strips/forbids it (SG-027 re-fire with amended GREEN bar), or the provider is rescoped. That is an owner decision, not a coder redesign (`dispute is a STOP, never a redesign`).

## Gates detail

- G1: starting tree clean (porcelain empty, quoted in log); baseline suite 75 passed / 3 failed with base-run proof (2 decoder env-reds as known + 1 alembic CWD artifact, none new, none touching sg025); Q2 count 1, value untouched.
- G3 PRE leg only: 10 offline gates written first (`backend/tests/test_opencode_go.py`), run pre-adapter: **10 failed** (`ModuleNotFoundError`, quoted raw in verify log). POST leg deliberately unrun — no adapter exists on a red spike, and claiming a pass would be vacuous (loudly stated, not reported).
- No SDK grep / header-value grep gates apply: `opencode_go.py` was never created. `OPENCODE_API_KEY` appears in zero repo lines (key lived only in `.env` + the /tmp spike script, both uncommitted).
- Live-state ledger: DB none, services none, restarts none; spend = 1 call (model, 7.1s, 868/1361/2229, estimate 0).

## Disagreements / findings beyond scope

1. Packet timeout text (`180s call / 60s wrapper`) is self-contradictory as a bound pair (wrapper shorter than call); the spike used a single 180s call timeout. Destination: next SG-027 re-fire packet.
2. Baseline suite from repo root carries a third red (alembic CWD artifact) beyond the "2 decoder env-reds known" premise — environmment/harness shape, not code. Destination: none (quoted as base-run proof); future packets may scope suite runs to `backend/`.
3. The `needs_evidence=false`-with-non-empty-unknowns combination the model returned is schema-legal but prompt-questionable (food prompt ties the flag to null `expiry_date`; here the date was legible, so `false` is defensible — recorded, not disputed).

## UNCLEAR lines

- FIRST READ: whether `Authorization: Bearer` (vs another scheme) is the documented GO auth — the relay never stated a scheme; Bearer was assumed and empirically accepted (200, no 401/403).
- DURING EXECUTION: whether GREEN's "unknowns honored" parenthetical could stretch to cover a semantically-honest-but-off-schema unknowns entry — I read it strictly (schema validation is the bar) and stopped.
- REMAINING: who owns the `lot`-field decision on re-fire (prompt forbids it harder, schema tolerates/strips it, or adapter pre-validates) — owner call before any SG-027 attempt-2.
