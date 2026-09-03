# StorageGenie — State

## RESUME HERE

**Version:** `0.17.2` (`C:\Coding\Claude\Launcher\VERSION` @ `0.17.2`, global `RULES.md` byte-identical)
**Branch:** `automation` (default), evidence ref `refs/heads/storagegenie-evidence`, remote `Andovol/StorageGenie`
**Host:** `andrei@87.106.66.242:2222` → `/home/andrei/StorageGenie` (ubuntu, VPS, `reference/vps-info.md` is authority)
**Status:** Onboarded. First Coder slice landed. Host is runnable. Evidence published (with manual repair).

**What is live:**
- `f80c6f5` AGENTS.md cutover (6406B, 0.17.2) + CLAUDE.md adapter, `5b1d1d2` decisions, `7320d6b` .gitignore — all pushed.
- Host provisioned: dispatch key `~/.ssh/storagegenie-architect-dispatch` (ed25519 432B), wrapper `/opt/storagegenie-dispatch/` (13849 + 2807, outside tree, `root:root 755`), `authorized_keys` 6 lines `restrict,pty,command=...`, GitHub repo `Andovol/StorageGenie` created, cloned to `/home/andrei/StorageGenie` (`automation`).
- Packet SG-001 `docs/packets/SG-001-host-setup-and-boundary-proof.md` + work `2abf9f1` + report `8c8997f` on `origin/automation`. Receipt `637302e` on `storagegenie-evidence` (`Dispatch-ID: SG-001`, manually repaired — see § Findings).
- Host artifacts (gitignored): `.env` 600, `venv` fastapi 0.141.1, `data/db/storagegenie.db` alembic `0201cf10c56c`, `storage_data:/data/storage`.
- Verification: `ruff PASS`, `mypy 43 advisory`, `pytest vacuous exit 5`, `npm 3 files 7 pass`, `TestClient 200 {"status":"ok","db":"ok","storage":"ok"}`. `curl :8000` hits foreign 404 (shared host), `docker volume ls` denied — both UNANSWERED/advisory.

**What is in flight:** Nothing. No dispatch, no open PR, no background job.

**Next step (exact):** Phase 0 build. Tasks 1-15 in `docs/superpowers/plans/2026-08-28-phase-0-foundation.md` — Tasks 12-14 (frontend) already have WIP on disk (see D1 below), verify/repair via Coder slices. Next packet: SG-002 — re-dispatch with repaired wrapper to prove receipt auto-publishes; then Phase 0 core slices. Owner to approve slice scope before dispatch (G-C1, `G-O1`).

**Decisions not derivable from code:**
- `D1` (2026-08-28, quote m0100 "keep the code for now"): untracked Phase 0 WIP kept on disk, not committed — `backend/` FastAPI/SQLAlchemy/Alembic + `frontend/` Vite/React + `backend/data/db/storagegenie.db` (migration `0201cf10`). Pin `26e9e8b` conserved; 40 obligations `keep/covered/retire`, zero CONFLICT (disposition `m0064`).
- Owner directives: `m0045` VPS folder `/home/andrei/StorageGenie`; `m0083` Coder `grok` + shared GitHub key (selectable per slice via `CODERS.md`); Phase 0 only — no LLM/OCR/barcode/Expiry plugin until authorized.

**How owner wants work done (differs from defaults):** High-level overview in chat; full technical detail on disk. Coder does all build/deploy on VPS (`G-O1`). Confirm before any ambiguous/destructive act (`G-C1`). `My recommendation` always bold in owner-facing text (owner formatting directive m0072).

---

## Findings to carry forward (project-relevant, not just Launcher)

- **Wrapper template bug (repaired):** `finalize_dispatch_report.sh` shipped with `HL-/healthylaws-evidence/worklogs` instead of `SG-/storagegenie-evidence/docs/worklogs` — patched to `SG-`/`storagegenie-evidence`/`docs/worklogs` (`/opt/storagegenie-dispatch/finalize_dispatch_report.sh:4-8`). If wrapper is reinstalled from template, re-check these three strings before next dispatch.
- **Foreign :8000 / docker sock:** Shared VPS — `curl :8000` returns foreign `Not Found 404`, `docker volume ls` denied (`nobody:nogroup` vs `root:root` uid remap). Not blocking; health via `{{HEALTH_CMD}}` TestClient fallback is source of truth. Next slice should allocate per-project `HOST_PORT` or document collision as expected.
- **Gates:** `mypy 43` advisory (unused-ignore/no-untyped-def), `pytest exit 5` vacuous — real gates are `ruff` + `TestClient` + `npm test`. Add `backend/tests/test_health.py` to make pytest non-vacuous.
- **Evidence store/DB are G-K3 sensitive surfaces** (`/data/storage`, `/data/db/storagegenie.db`, host/credential) — every decision touching them needs owner sign-off individually, per `AGENTS.md`.
- **Phase 0 WIP on disk** (D1): `backend/app/models/base.py`, `evidence_service.py`, `api/v1/exports.py`, etc. already contain Tasks 2-14 code. Next Coder slices should verify/repair against plan, not rebuild from scratch. Git status clean except `docs/launcher-onboarding-feedback.md` (this close commits it).

---

## History (recent, terse)

- `637302e` — receipt SG-001 (manual, `storagegenie-evidence`, `Dispatch-ID: SG-001 | Work-HEAD: 2abf9f1`)
- `8c8997f` — report SG-001 (90 lines, boundary proof)
- `2abf9f1` — work SG-001 (84 lines, host setup)
- `5602ec2` — packet SG-001 pushed
- `dd95eec→f80c6f5` — provisioning + cutover (AGENTS.md 0.17.2, decisions, .gitignore, remote wiring)

Full onboarding narrative: `docs/launcher-onboarding-feedback.md` (for Launcher Architect).
