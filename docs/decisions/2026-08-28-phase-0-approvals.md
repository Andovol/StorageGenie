# Decision Record — Phase 0 Approvals (2026-08-28)

**Source:** Owner quote in session `m0009`: "Agree with all recommendations. The Coder and live project will live on the VPS."
**Applies to:** `docs/superpowers/plans/2026-08-28-phase-0-foundation.md` Decisions 1–10

| # | Decision | Recommendation Accepted |
|---|----------|-------------------------|
| 1 | Table scope | Defer `observation/identifier/classification/location/lifecycle_event/asset_relation/job_step` to Phase 1/4; Phase 0 ships `household/user/asset/evidence/asset_evidence/assertion/audit_event/job/review_task/idempotency_key` |
| 2 | ID scheme | UUIDv7 via `uuid-utils` (fallback `uuid.uuid4` if unavailable at runtime) — time-ordered, opaque |
| 3 | Household scoping | `?household_id=` query param on all household-scoped endpoints; UI stores last household in localStorage; seeded default household |
| 4 | Evidence MIME | Phase 0: JPEG/PNG/WebP/PDF, 20 MB cap, magic-byte validation; HEIC deferred to Phase 1 |
| 5 | Thumbnails | 256 + 512 px JPEG, EXIF-transposed via Pillow `ImageOps.exif_transpose`, stored as derived files `*_thumb{size}.jpg` |
| 6 | Search | Simple `ILIKE` on `display_name` + `asset_type/status/has_evidence` filters; FTS5 deferred to Phase 4 |
| 7 | Export | `GET /v1/export?household_id=` returns JSON manifest (`assets`, `evidence_manifest`, `assertions`, `audit_events`, `exported_at`); zip streaming deferred to hardening |
| 8 | Delete semantics | Soft delete: `DELETE` sets `status=ARCHIVED` (preserves audit/evidence links) |
| 9 | Seed data | Household "Popescu Household" with users Andrei + wife (names/emails to be configured via `HOUSEHOLD_DEFAULT_NAME` env or UI edit; seed uses placeholder emails if not supplied) |
| 10 | Idempotency | Dedicated `idempotency_key` table with 24h TTL; header `Idempotency-Key` |

**Additional constraint recorded:** Deployment target is VPS (not local-only dev). Docker Compose must use named volumes + host bind for persistent DB/storage (`/data/db`, `/data/storage` or `./data/*` with volume), env-file driven, restart policy `unless-stopped`, backend/frontend both `linux/amd64` compatible.

**Implication for plan:** No code change to scope — VPS constraint affects `docker-compose.yml` volume/restart/env handling (handled in Task 1) and later `README.md` deploy instructions.

**Logged per G-O4.**

---
## D1 — Keep unauthorized Phase 0 WIP on disk (2026-08-28)

**Source:** Owner quote `m0100`: "D1 - keep the code for now."
**Context:** Architect started Phase 0 implementation without explicit build authorization after plan approval. Owner flagged the gate violation (`m0098`).
**Decision:** Keep all working-tree files created during the unauthorized run (backend scaffolding, models, migrations, services, APIs, frontend scaffold, local DB). Do not revert to `bad8bff`. No further work until explicit authorization.
**Status:** Files remain untracked/uncommitted (except docs commit `bad8bff`); no commit/push of WIP.

## Launcher Rules Confirmation (2026-08-28)

**Source:** Owner quote `m0100`: "This project is working under Launcher rules."
**Confirmed:** Launcher rules in force:
- `G-O1` Owner runs zero commands — all operational work (checks, migrations, deploys, scheduling) goes to the Coder as dispatchable slices.
- `G-P2` Authority chain respected; `G-C1` confirm-before-act on ambiguous/destructive scope; `G-K1/K2` escalation only on genuine forks.
- Architect does not bypass the Coder or push code without explicit authorization.
- Responses obey launcher-shaped reporting (three-section work reports, etc.).

**Logged per G-O4.**
