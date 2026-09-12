# ADR-007: Provider privacy (consent, GPS strip, key custody, retention)

- Status: accepted for Phase 2
- Date: 2026-09-12
- Slice: SG-025

## Decision

Both users are in scope for AI-assisted cataloging (owner decision F3), with
GPS-default-strip: location metadata is stripped from provider-bound payloads
by default. The provider API key lives in the host `.env` (mode 600) and is
never in the repo, logs, or packets — this slice proves the rule by probing
only presence/count (`grep -c '^OPENCODE_API_KEY=' .env`), never content.
Provider inputs are hashed into the ledger (`input_hashes`); the full output
payload is retained per §3.3 alongside provider, model, prompt-template
version, cost/usage, latency, and error state.

## Existing pins

- `backend/app/models/provider_call.py` — `ProviderCall` ledger model
  (provider, model, prompt-template version, input hashes, output payload,
  cost/usage, latency, error state, nullable job FK; `TimestampMixin` +
  `new_id` per `audit_event.py`/`job.py` pattern).
- `backend/alembic/versions/20260912_sg025_provider_call.py` — ledger table
  migration (upgrade/downgrade proven on temp SQLite this slice).
- G1 Q2 probe of this slice: count quoted, value never printed, logged, or
  committed — a secret literal anywhere in tree/logs is a FAIL.

## Consequences

SG-027+ adapters read the key from host `.env` at runtime only. Any GPS
passthrough to a provider, any key material in repo/logs, or any unledgered
call is a privacy defect with a destination. Retention policy for ledger rows
is decided no later than the production-datastore slice.
