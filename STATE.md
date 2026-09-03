# StorageGenie — State

## RESUME HERE

**Version:** `0.17.2` (`C:\Coding\Claude\Launcher\VERSION` @ `0.17.2`, global `RULES.md` byte-identical)
**Branch:** `automation` (default), evidence ref `refs/heads/storagegenie-evidence`, remote `Andovol/StorageGenie`
**Host:** `andrei@87.106.66.242:2222` → `/home/andrei/StorageGenie` (ubuntu, VPS, `reference/vps-info.md` is authority)
**Status:** SG-007 landed and rated 98. Pure verify slice: zero product repair justified — full asset CRUD, cursor pagination round-trip, supersession chain, 403/404/409 paths all proved by 3 committed test modules (suite 14 passed). Receipt `d43f4c1` (`Dispatch-ID: SG-007`) auto-published; parent/trailer verified. Empirical ssh test settled it: session still Running at receipt — receipt commit is the done-signal. No dispatch in flight. Next: SG-008 (search/export manifest, Task 11) or Launcher relay send.
- Queued finding (mypy advisory, from SG-007 report): `backend/app/services/evidence_service.py:95` assignment-type error — destination: next slice touching that file.

**What is live:**
- `f80c6f5` AGENTS.md cutover (6406B, 0.17.2) + CLAUDE.md adapter, `5b1d1d2` decisions, `7320d6b` .gitignore — all pushed.
- Host provisioned: dispatch key `~/.ssh/storagegenie-architect-dispatch` (ed25519 432B), wrapper `/opt/storagegenie-dispatch/` (13849 + 2807, outside tree, `root:root 755`), `authorized_keys` 6 lines `restrict,pty,command=...`, GitHub repo `Andovol/StorageGenie` created, cloned to `/home/andrei/StorageGenie` (`automation`).
- Packet SG-001 `docs/packets/SG-001-host-setup-and-boundary-proof.md` + work `2abf9f1` + report `8c8997f` on `origin/automation`. Receipt `637302e` on `storagegenie-evidence` (`Dispatch-ID: SG-001`, manually repaired — see § Findings).
- Host artifacts (gitignored): `.env` 600, `venv` fastapi 0.141.1, `data/db/storagegenie.db` alembic `0201cf10c56c`, `storage_data:/data/storage`.
- Verification: `ruff PASS`, `mypy 43 advisory`, `pytest vacuous exit 5`, `npm 3 files 7 pass`, `TestClient 200 {"status":"ok","db":"ok","storage":"ok"}`. `curl :8000` hits foreign 404 (shared host), `docker volume ls` denied — both UNANSWERED/advisory.
- SG-002 (grok ×2): zero artifacts — external grok outage, owner-confirmed (see Decisions). No commits.
- SG-003 (codex medium): work `fb9546d` + `c8c58e3`, rated 82 packet-attributed (G5 omitted evidence-prefill push). Receipt blocked `candidate_not_remote` — honestly STOPped per `CO-54`.
- SG-004 (codex medium): work `90c4cab` + merge `ec4254f` (CO-54-compliant prefill, content-neutral) + `c0a14ee`; receipt `3294091` auto-published, all five properties independently verified (parent/trailer/diff/remote-head/notes). Rated 96. Wrapper P5 `FAIL` on it was the stale-literal false negative, since repaired.
- Ratings filed: `docs/ratings.md` (SG-003 82 packet, SG-004 96 coder, SG-005 97 no-deduction). Packets SG-002…SG-005 committed. `automation` @ `4532f27`, evidence @ `c3ea843`.
- SG-005 (codex high): work `324857c` (truthful health + 503, `test_health.py` 3 pass, ruff clean, lockfile + digest-pinned base, busy_timeout 5000) + merge `4532f27` (CO-54 prefill, also restored SG-004 report onto automation); receipt `c3ea843` auto-published (parent/trailer/tip verified). Rated 97. Dispatch fired once at gate (`g2b_divergence_refused` — publisher had left host on evidence branch), recovered via owner-run reset to `535a2d3`, re-trigger accepted.

- SG-006 (codex high): work `6d57bc2` (strict signature/MIME validation, dynamic bomb guard with named `max_image_pixels` setting, EXIF-free derivatives byte-proved, atomic tmp cleanup, dead-code removal, 8 committed tests incl. crafted-dimension PNG + fail-then-fix log) + merge `2d70e28` (CO-54 prefill, also restored SG-005 report onto automation); receipt `3bc9e61` auto-published (parent/trailer/tip verified). Rated 98. Waited in-turn per owner directive; detached trigger worked cleanly.

**What is in flight:** SG-007 dispatch BLOCKED at wrapper gate — `DISPATCH_REJECTED g2b_divergence_refused` again (SG-006's publisher left the host worktree on the evidence line, same defect as SG-005; relay still unsent to Launcher). No retry burned. Own miss: the refusal was visible in the trigger log after 45 s but the wait ran the full 32 min — procedure now gates the wait on trigger acceptance within 60 s. Packet `89dbf72` pushed and valid; re-trigger after host reset to `89dbf72`.
- Standing dispatch procedure (owner directive, verified 2026-09-03: a 240 s blocking call survives): dispatch turns are sequential bounded blocking waits IN-TURN until receipt or budget — no fire-and-forget, no between-turn polling, no dormant gaps. Trigger detached (`Start-Process` + log), then blocking wait loop (sleep + fetch + receipt check) inside the turn.

**Decisions not derivable from code:**
- `D1` (2026-08-28, quote m0100 "keep the code for now"): untracked Phase 0 WIP kept on disk, not committed — `backend/` FastAPI/SQLAlchemy/Alembic + `frontend/` Vite/React + `backend/data/db/storagegenie.db` (migration `0201cf10`). Pin `26e9e8b` conserved; 40 obligations `keep/covered/retire`, zero CONFLICT (disposition `m0064`).
- Owner directives: `m0045` VPS folder `/home/andrei/StorageGenie`; `m0083` Coder `grok` + shared GitHub key (selectable per slice via `CODERS.md`); Phase 0 only — no LLM/OCR/barcode/Expiry plugin until authorized.
- `m0050` grok outage (quote: "Grok is down, thats why its not working.") — SG-002 diagnosis basis; slices moved to codex.
- `m0072` formatting (quote: "Always put "My recommendation" text in bold, so I can easily see it.")
- `m0106` next-session coder/effort (quote: "We will continue with Codex on High.") — SG-005+ run codex high until countermanded.
- `m0015` blueprint suggestions verdict (quote: "No to UV3 and UV6, I don't like that directions." + "Okay to all other suggestions."): UV-3 (barcode-first ordering) and UV-6 (static dosage guardrails) REJECTED — plan order and §10 stand unchanged. UV-1/UV-2/UV-4/UV-5 + BM-1…BM-8 ACCEPTED as backlog/ADR input; tech-stack question asked next.
- `m0019` tech-stack verdict (quote: "Okay to all items."): TS-1…TS-5 ACCEPTED. Cap directive: prefer dynamic/config-driven limits over silent hard caps — every limit a named setting, logged when it binds, visible reject, no magic numbers (aligns `G-A8`; softens AGENTS.md 20 MB hard-cap narrowing — 20 MB stays as configured default with visible 413, adjustable via env).
- Register: `docs/decisions/2026-09-03-accepted-optimizations.md` — all accepted UV/BM/TS items with use case + source + slice assignment; UV-3/UV-6 recorded rejected; blueprint v3 itself unchanged.
- Owner directive 2026-09-03 (quotes: "Dec1 - ok, but please make sure you follow the new process for dispatch that you mentioned." + "you can do a cross-project handoff directly to the Launcher folder."): SG-006 APPROVED under Codex High L2 with the detached-dispatch process (Start-Process + log file, never Start-Job); cross-project Launcher handoff AUTHORIZED as files into the Launcher tree. (Not tagged `m0083` — that ID is already the `m0083` Coder-grok directive above; collision avoided.)
- `m0025` SG-005 APPROVED (quote: "Yes, approved.") — foundation verify/repair, Codex High, L2, with TS-1/TS-4/TS-5 + BM-3/BM-5 folded in. Packet + dispatch authorized.
- SG-005 dispatch RUNNING (re-trigger accepted after host reset to `535a2d3`; first `high` passed the effort gate — wrapper echoed `contract_sync=refresh version=0.17.2`). Watch condition: commit with `Dispatch-ID: SG-005` on `storagegenie-evidence`, then pull + audit the diff.
- Prevention relay drafted: `docs/launcher-relay/2026-09-03-publisher-restore-branch.md` (publisher must restore worktree branch after publishing; `g2b` stays). UNSENT — send with the Launcher batch after SG-005 lands; nothing commits/pushes to `automation` mid-flight.

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
