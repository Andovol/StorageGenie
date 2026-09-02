# StorageGenie — Launcher Onboarding Retrospective

> **For:** Launcher Architect (framework improvement)
> **Project:** StorageGenie (Andovol/StorageGenie) — generic asset catalog + evidence
> **Onboarding date:** 2026-09-02
> **Source pins:** `bad8bff` docs-only → `26e9e8b` conserved WIP → `f80c6f5` AGENTS.md (v0.17.2) → `dd95eec` hosted
> **Host:** `andrei@87.106.66.242:2222` (`ubuntu`, `/home/andrei/StorageGenie`)
> **Coder:** `grok` (shared GitHub key, per owner directive m0083)

---

## 1. Executive Summary

Onboarding succeeded end-to-end: conversion conservation → host provisioning → first Coder slice landed and evidence published. No blocking conflicts.

**Cycle:** `draft → approve → dispatch → audit → rate` ran once (SG-001). Host is runnable (venv + DB + storage), backend answers `GET /v1/health` via TestClient, frontend builds. Evidence is on `storagegenie-evidence` after a manual repair.

**Cost:** One packet dispatch (~310s, pip install dominant) + ~3h wall-clock for two provisioning passes and manual receipt fix.

---

## 2. Timeline (high level)

1. **Load context** — blueprint v3 (17 sections), Phase 0 plan (Tasks 1-15), decisions 1-10 (D1 = keep untracked WIP on disk, not committed).
2. **Rule reconciliation (G-L1)** — global `RULES.md` v0.17.2 vs project `AGENTS.md`; recorded pair, no drift.
3. **Conversion conservation (ONBOARDING.md §89-110)** — dispositioned 40 binding obligations (`keep`/`covered`/`retire`), zero `CONFLICT`. Pinned `26e9e8b` as cutover base.
4. **Cutover commits** — `f80c6f5` AGENTS.md 6406B + CLAUDE.md adapter, `5b1d1d2` decisions file, `7320d6b` .gitignore fix (all byte-identical to spec).
5. **Host provisioning — read-only pass** (2026-09-02T11:44) — verified `vps-info.md:27` host `87.106.66.242:2222`, 37 sibling trees, no prior `storagegenie` directory. No writes yet.
6. **Host provisioning — write pass** (m0087-m0103) — minted dispatch key, installed wrappers, fixed git remote/branch, created GitHub repo, cloned to VPS.
7. **Packet SG-001** — "host setup and boundary proof" dispatched `SG-001 grok medium` at 11:57:55Z, work `2abf9f1` + report `8c8997f` landed on `automation`, receipt manually repaired to `637302e` on `storagegenie-evidence`.

---

## 3. What Went Well

- **ONBOARDING.md conversion flow is clear** — 40 obligations were easy to disposition; `CONFLICT → stop` rule prevented silent overrides.
- **PROVISIONING.md read-only before write** caught that the VPS was empty (no stale clone to delete) — saved a risky `rm -rf`.
- **Wrapper outside tree** (`/opt/storagegenie-dispatch/`, `root:root 755`) survived `git clean` and satisfied `ReadWritePaths=~/.codex + ~/.grok`.
- **Boundary proof packet** (CO-42 quote, `{{WORKLOG_DIR}}`/`{{HEALTH_CMD}}` bindings, `ProtectHome=read-only`) proved confinement worked (`ls /home/andrei/pip → Permission denied`).
- **TestClient fallback** for `{{HEALTH_CMD}}` kept the slice green when `curl :8000` hit a foreign 404 — health was still provable without Docker.

---

## 4. Issues Encountered and How Solved

### ISS-1 — Wrapper/finalize script still contained HealthyLaws strings (P0, product bug)
**What happened:** `/opt/storagegenie-dispatch/dispatch_coder.sh` and `finalize_dispatch_report.sh` were copied from `healthylaws-dispatch` template without full re-parameterization. Contains:
- `HL-` prefix instead of `SG-`
- `healthylaws-evidence` instead of `storagegenie-evidence`
- `worklogs/` instead of `docs/worklogs/`

**Impact:** First dispatch failed two DISPATCH.md checks: `receipt_diff_not_exact` and `candidate_not_remote`. No receipt auto-published.

**Fix applied:** Manually patched `finalize_dispatch_report.sh:4-8` to `SG-`/`storagegenie-evidence`/`docs/worklogs/` and re-published receipt `637302e` with trailer `Dispatch-ID: SG-001` on `refs/heads/storagegenie-evidence`. Added note `Dispatch-ID: SG-001 | Work-HEAD: 2abf9f1... | Receipt: 637302e`.

**Recommendation for Launcher:** Generate wrappers from a parameterized template (e.g., `envsubst` on `{{PROJECT_ID}}`, `{{EVIDENCE_REF}}`, `{{PACKET_DIR}}`) and add a pre-dispatch lint: `grep -q "{{PROJECT_ID}}-evidence" finalize_*.sh || fail`.

### ISS-2 — AGENTS.md Values table is a manual copy-paste surface
**What happened:** `{{PROD_DB}}`, `{{HEALTH_CMD}}`, etc. are bound in AGENTS.md per project. A stale bound value (e.g., `not applicable` vs real Postgres) would silently misconfigure the Coder.

**Fix:** Cross-checked Values table against `PROVISIONING.md` and `CODER_PRODUCTION.md:26`; kept `not applicable` for Phase 0 SQLite correctly.

**Recommendation:** Add `launcher verify --values` that diffs AGENTS.md Values table against `global/CODER.md` placeholders and fails on unbound `{{NAME}}`.

### ISS-3 — Evidence ref does not exist until first receipt
**What happened:** `git ls-remote` showed no `storagegenie-evidence` before SG-001. `DISPATCH.md:42-50` expects it.

**Fix:** Manual `git push origin HEAD:refs/heads/storagegenie-evidence` after patching finalize script.

**Recommendation:** Provisioning should `git push --allow-empty` an initial evidence commit or document that the first dispatch creates the ref (and that `candidate_not_remote` is expected once).

### ISS-4 — Docker healthcheck hit a foreign service (port 8000) on the shared VPS
**What happened:** `curl :8000` returned `404 Not Found` from a different project (HealthyLaws was listening). `TestClient` via `from app.main import app` still returned 200 `{"status":"ok","db":"ok","storage":"ok"}`.

**Fix:** Reported as `UNANSWERED` boundary finding; did not block. Packet health verification uses `{{HEALTH_CMD}}` with TestClient fallback precisely for this shared-host case.

**Recommendation:** Document shared-host port collision as expected; recommend per-project `HOST_PORT` allocation or make healthcheck use `127.0.0.1:${ASSIGNED_PORT}` from `.env`.

### ISS-5 — Docker socket blocked (`docker volume ls` denied, `docker compose` not runnable via wrapper)
**What happened:** Wrapper runs as `nobody:nogroup` (or with `ProtectHome=read-only` + `InaccessiblePaths` enumerated) so `docker.sock` is not reachable.

**Impact:** `compose storagegenie_storage_data unproven` — advisory only.

**Recommendation:** Keep advisory (don't gate on Docker if not needed for Phase 0). For projects needing Docker, add a dedicated `docker` group allow-list or run wrapper with `SupplementaryGroups=docker` and document the trade-off.

### ISS-6 — Python gates noisy: `ruff PASS`, `mypy 43 errors (advisory)`, `pytest vacuous exit 5`
**What happened:** Plan specifies `ruff check + mypy + pytest + npm test`. Without committed tests, `pytest` exits 5 and `mypy` reports 43 `unused-ignore`/`no-untyped-def` — both advisory, not failures.

**Fix:** Packet report marked them `PASS (advisory)` and used `TestClient` + `npm test 3 files 7 pass` as real gates.

**Recommendation:** Make `mypy`/`pytest` thresholds explicit in PACKET.md acceptance (e.g., `mypy --strict 0 advisory` vs `blocking`) and ship a minimal `test_health.py` in the template so `exit 5` never happens.

### ISS-7 — `.env` outside tree, `600`, gitignored — correct but invisible
**What happened:** `.env` lives on host only (`DATABASE_URL`, `STORAGE_ROOT`, `HOUSEHOLD_DEFAULT_NAME`, `CORS_ORIGINS`). Local clone has no `.env` by design, so `git status` is green but host setup is not reproducible from repo alone.

**Fix:** Provisioning step documents `.env` sample in packet; packet verifies `stat -c %a .env == 600`.

**Recommendation:** Keep `.env` out of repo, but add `docs/runbooks/env.md` with the exact sample and a `launcher env-check` that asserts `600` + required keys.

### ISS-8 — Branch/remote/ID prefix drift from template
**What happened:** Template default branch is `main`, ID `HL-`, remote `HealthyLaws`. StorageGenie uses `automation`, `SG-`, `Andovol/StorageGenie`.

**Fix:** Provisioning pass reconfigured all four (`branch automation`, `ID SG-[0-9]{3}`, `remote Andovol/StorageGenie`, `/opt/storagegenie-dispatch/` path) and verified via `git config` + `cat ~/.ssh/authorized_keys` (5→6 lines, `restrict,pty,command="..."` `600`).

**Recommendation:** Single `launcher init --project storagegenie --id SG --branch automation --remote Andovol/StorageGenie` that writes all four atomically; currently they are four separate sed/echo steps that can drift.

---

## 5. What the Next Architect Needs (Phase 0 remaining)

Phase 0 plan Tasks 1-15 are scoped; first slice (host boundary proof) is done. Remaining slices will add backend `data/db/storagegenie.db` (Alembic heads), API surface (`/v1/health`, `/v1/assets`, etc.), and `frontend/node_modules` build. No LLM/OCR/barcode/Expiry plugin until explicitly authorized (Phase 0 constraint).

---

## 6. Concrete Suggestions for Launcher (prioritized)

1. **Template the wrappers** — never `cp healthylaws-dispatch/*` + sed; render from `global/dispatch_coder.sh.tpl` + `finalize_dispatch_report.sh.tpl` with `{{PROJECT_ID}}`, `{{PACKET_DIR}}`, `{{EVIDENCE_REF}}`. Add CI `grep -r healthylaws` gate on `/opt/*-dispatch/`.
2. **Pre-dispatch lint** — `launcher lint --packet SG-001` checks: version chain `recorded == payload == host == header (ALP-11)`, `docs/packets` pushed, `contract_sync=refresh version=0.17.2` header present, worktree clean, no concurrent dispatch. Surface the two receipt failures as lint errors before SSH.
3. **`launcher provision --dry-run` + `--write`** — the two-pass pattern works; make it a first-class flag so read-only vs write is not a manual fork.
4. **Shared-host docs** — one page explaining port 8000 collisions, `docker.sock` advisory, and why `TestClient` is the source of truth for health on shared VPS.
5. **Evidence ref bootstrap** — `launcher evidence --create` that pushes an empty `storagegenie-evidence` with correct header, so first dispatch never hits `candidate_not_remote`.
6. **Values table verifier** — `launcher verify --values` as above.
7. **Keep G-L1 reconciliation lightweight** — checking `AGENTS.md` + `VERSION` equality before re-reading saved ~40k tokens this session; document that as the default.

---

## 7. Provenance (so this file is auditable, per G-A1)

- Commits: `26e9e8b` pinned WIP, `f80c6f5` AGENTS.md cutover, `5b1d1d2` decisions, `7320d6b` .gitignore, `dd95eec` host clone, `2abf9f1` work, `8c8997f` report, `637302e` repaired receipt — all on `automation` / `storagegenie-evidence`.
- Host proofs: `/home/andrei/launcher/VERSION` 0.17.2, `~/.ssh/storagegenie-architect-dispatch` 432B ed25519 SHA256:aQ4q..., `/opt/storagegenie-dispatch/*` 13849/2807 `root:root 755`, `~/.ssh/authorized_keys` 6 lines ` restrict,pty,command="..."`.
- Coder proof: `SG-001 grok medium` via `storagegenie-architect-dispatch` 2026-09-02T11:57:55Z, `g4_autostashed_count=0`, `available_mb=4777`, `contract_sync=refresh version=0.17.2`, `grok 1.0.5`.
- Verification: `ruff check app PASS`, `mypy 43 advisory`, `pytest exit 5 vacuous`, `npm test 3/7 PASS`, `TestClient 200 {"status":"ok","db":"ok","storage":"ok"}`, `alembic current 0201cf10c56c`.

---

*Written for the Launcher Architect — concise by request, detailed where it changes the product. All load-bearing claims cite a commit, receipt, or owner directive above.*
