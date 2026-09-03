# StorageGenie — State

## RESUME HERE

**Version:** `0.17.2` (`C:\Coding\Claude\Launcher\VERSION` @ `0.17.2`, global `RULES.md` byte-identical)
**Branch:** `automation` (default), evidence ref `refs/heads/storagegenie-evidence`, remote `Andovol/StorageGenie`
**Host:** `andrei@87.106.66.242:2222` → `/home/andrei/StorageGenie` (ubuntu, VPS, `reference/vps-info.md` is authority)
**Status:** Pipeline proven end-to-end. Receipt `3294091` (`Dispatch-ID: SG-004`) auto-published with zero manual repair. Wrapper repaired twice (finalize re-parameterization verified; `receipt_valid` literal + effort gate fixed on host). No dispatch in flight. Next session opens with inception blueprint review, then Phase 0 build under Codex High.

**What is live:**
- `f80c6f5` AGENTS.md cutover (6406B, 0.17.2) + CLAUDE.md adapter, `5b1d1d2` decisions, `7320d6b` .gitignore — all pushed.
- Host provisioned: dispatch key `~/.ssh/storagegenie-architect-dispatch` (ed25519 432B), wrapper `/opt/storagegenie-dispatch/` (13849 + 2807, outside tree, `root:root 755`), `authorized_keys` 6 lines `restrict,pty,command=...`, GitHub repo `Andovol/StorageGenie` created, cloned to `/home/andrei/StorageGenie` (`automation`).
- Packet SG-001 `docs/packets/SG-001-host-setup-and-boundary-proof.md` + work `2abf9f1` + report `8c8997f` on `origin/automation`. Receipt `637302e` on `storagegenie-evidence` (`Dispatch-ID: SG-001`, manually repaired — see § Findings).
- Host artifacts (gitignored): `.env` 600, `venv` fastapi 0.141.1, `data/db/storagegenie.db` alembic `0201cf10c56c`, `storage_data:/data/storage`.
- Verification: `ruff PASS`, `mypy 43 advisory`, `pytest vacuous exit 5`, `npm 3 files 7 pass`, `TestClient 200 {"status":"ok","db":"ok","storage":"ok"}`. `curl :8000` hits foreign 404 (shared host), `docker volume ls` denied — both UNANSWERED/advisory.
- SG-002 (grok ×2): zero artifacts — external grok outage, owner-confirmed (see Decisions). No commits.
- SG-003 (codex medium): work `fb9546d` + `c8c58e3`, rated 82 packet-attributed (G5 omitted evidence-prefill push). Receipt blocked `candidate_not_remote` — honestly STOPped per `CO-54`.
- SG-004 (codex medium): work `90c4cab` + merge `ec4254f` (CO-54-compliant prefill, content-neutral) + `c0a14ee`; receipt `3294091` auto-published, all five properties independently verified (parent/trailer/diff/remote-head/notes). Rated 96. Wrapper P5 `FAIL` on it was the stale-literal false negative, since repaired.
- Ratings filed: `docs/ratings.md` (SG-003 82 packet, SG-004 96 coder). Packets SG-002/003/004 committed. `automation` @ `54172ca`, evidence @ `3294091`.

**What is in flight:** Nothing. No dispatch, no open PR, no background job.

**Next step (exact):** New session: (1) review the inception blueprint (`inception/`), (2) then first Phase 0 slice SG-005 under Codex High (owner directive m0106). G-C1 approval before dispatch; Coder builds on VPS (`G-O1`). Note: wrapper now accepts `high` (code-verified, first `high` dispatch is the functional proof); packet must still carry the G5-prefill block verbatim.

**Decisions not derivable from code:**
- `D1` (2026-08-28, quote m0100 "keep the code for now"): untracked Phase 0 WIP kept on disk, not committed — `backend/` FastAPI/SQLAlchemy/Alembic + `frontend/` Vite/React + `backend/data/db/storagegenie.db` (migration `0201cf10`). Pin `26e9e8b` conserved; 40 obligations `keep/covered/retire`, zero CONFLICT (disposition `m0064`).
- Owner directives: `m0045` VPS folder `/home/andrei/StorageGenie`; `m0083` Coder `grok` + shared GitHub key (selectable per slice via `CODERS.md`); Phase 0 only — no LLM/OCR/barcode/Expiry plugin until authorized.
- `m0050` grok outage (quote: "Grok is down, thats why its not working.") — SG-002 diagnosis basis; slices moved to codex.
- `m0072` formatting (quote: "Always put "My recommendation" text in bold, so I can easily see it.")
- `m0106` next-session coder/effort (quote: "We will continue with Codex on High.") — SG-005+ run codex high until countermanded.

**How owner wants work done (differs from defaults):** High-level overview in chat; full technical detail on disk. Coder does all build/deploy on VPS (`G-O1`). Confirm before any ambiguous/destructive act (`G-C1`). Batch file edits into few section-sized replacements, not many line-level ones (owner efficiency directive m0113). `My recommendation` always bold in owner-facing text (quote m0072: "Always put "My recommendation" text in bold, so I can easily see it.").

---

## Findings to carry forward (project-relevant, not just Launcher)

- **Wrapper template bug (repaired):** `finalize_dispatch_report.sh` shipped with `HL-/healthylaws-evidence/worklogs` instead of `SG-/storagegenie-evidence/docs/worklogs` — patched to `SG-`/`storagegenie-evidence`/`docs/worklogs` (`/opt/storagegenie-dispatch/finalize_dispatch_report.sh:4-8`). If wrapper is reinstalled from template, re-check these three strings before next dispatch.
- **Wrapper audit false negative (REPAIRED SG-004 day):** `dispatch_coder.sh` `receipt_valid()` compared the receipt diff against hardcoded `worklogs/<ID>_report.md` instead of this project's `docs/worklogs` — repaired to `docs/worklogs/${id}_report.md` (`:106`, backup `/opt/storagegenie-dispatch/dispatch_coder.sh.bak-SG004`, `bash -n` clean, mode `root:root 755` preserved). SG-004 `3294091` was already substantively valid; the repair un-breaks P5 for future slices.
- **Wrapper effort gate relaxed (owner directive, SG-004 day):** line 37 enforced medium-only (`effort_not_approved`); replaced with default-to-medium so parsed `low|medium|high|max` all pass. Owner explicitly wants non-medium efforts available (asked High). Next `high` dispatch is the functional proof.
- **Foreign :8000 / docker sock:** Shared VPS — `curl :8000` returns foreign `Not Found 404`, `docker volume ls` denied (`nobody:nogroup` vs `root:root` uid remap). Not blocking; health via `{{HEALTH_CMD}}` TestClient fallback is source of truth. Next slice should allocate per-project `HOST_PORT` or document collision as expected.
- **Gates:** `mypy 43` advisory (unused-ignore/no-untyped-def), `pytest exit 5` vacuous — real gates are `ruff` + `TestClient` + `npm test`. Add `backend/tests/test_health.py` to make pytest non-vacuous.
- **Evidence store/DB are G-K3 sensitive surfaces** (`/data/storage`, `/data/db/storagegenie.db`, host/credential) — every decision touching them needs owner sign-off individually, per `AGENTS.md`.
- **Phase 0 WIP on disk** (D1): `backend/app/models/base.py`, `evidence_service.py`, `api/v1/exports.py`, etc. already contain Tasks 2-14 code. Next Coder slices should verify/repair against plan, not rebuild from scratch.
- **Effort vocabulary drift (OPEN, trivial):** `AGENTS.md` promises `xhigh`; wrapper shape is `max`. Harmless until someone dispatches either token — then it rejects. Fix with next AGENTS.md touch.
- **Queued for owner approval (not applied):** shared-proposal relay for the template-drift class (`receipt_valid` literal + finalize re-parameterization + `max`/`xhigh`); Launcher repo untouched this session.

---

## History (recent, terse)

- `54172ca` — state: wrapper P5 + effort-gate repairs recorded
- `326db08` — ratings: SG-004 row (96, coder)
- `3294091` — receipt SG-004 (auto, `storagegenie-evidence`, `Dispatch-ID: SG-004 | Work-HEAD: c0a14ee`)
- `c0a14ee` — work SG-004 (+ merge `ec4254f` evidence prefill, + `90c4cab`)
- `31e6b7d` — packet SG-004 + bold-recommendation state tweak
- `82ef49c` — ratings: SG-003 row (82, packet)
- `c8c58e3` — work SG-003 (`fb9546d` + blocker record, codex)
- `6831e94` — packet SG-003 (codex, grok outage)
- `ed62f54` — packet SG-002 (wrapper receipt proof)
- `637302e` — receipt SG-001 (manual, `storagegenie-evidence`, `Dispatch-ID: SG-001 | Work-HEAD: 2abf9f1`)

Full onboarding narrative: `docs/launcher-onboarding-feedback.md` (for Launcher Architect).
