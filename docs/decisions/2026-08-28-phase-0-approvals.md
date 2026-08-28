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
