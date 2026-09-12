# ADR-010: Guardrail Stage-0 rollout (mandatory human confirmation)

- Status: accepted for Phase 2
- Date: 2026-09-12
- Slice: SG-025

## Decision

Guardrails roll out at Stage 0: every AI-proposed catalog change requires
mandatory human confirmation before it takes effect, and there is no dosage
(or any other) automation in this stage (owner decision F4). The provider
seam built this slice carries no auto-apply path: the fake double returns
`needs_evidence` where evidence is insufficient, the router has no
auto-confirm flag, and ledger rows record proposals — never approvals.

## Existing pins

- `backend/app/services/providers/fake.py` — `needs_evidence` shape models
  the insufficient-evidence outcome explicitly.
- `backend/app/services/providers/router.py` — no confirmation bypass exists;
  adding one requires a new ADR, not a config flag.
- `backend/app/models/provider_call.py` — `error_state` plus the output
  payload preserve what the provider proposed for later human review
  (production reader arrives SG-028).

## Consequences

Any slice introducing auto-apply, auto-confirm, or dosage automation without
a superseding ADR is a STOP, never a redesign-in-place. Stage promotion is an
owner decision with its own ADR.
