# Roadmap-finish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the StorageGenie roadmap via one L3 slice chain: six fixes, hue verdict, scheduled Context Scene resume, close-out deploy.

**Architecture:** Architect packetizes each slice in order; Coder executes via `job_spawn` dispatch; Architect audits, rates, chains. One retry per slice; any STOP-gate halts the chain with a decision.

**Tech Stack:** Python/FastAPI backend, React/Vite frontend, SQLite + FTS5, alembic, opencode Coder at `high` effort (model omitted, resolves to `deepseek-v4.1-flash`).

## Global Constraints

- Contract `0.40.0`; triggers `job_spawn`-only with covering caps (2400s; lane `RUN_BUDGET_S=2100`).
- `opencode`/`high` explicit every trigger; model omitted per standing policy.
- Slices own their refresh per D145 (rebuild + one recreate + verify where served code changes).
- `STATE.md` is the single source of next-slice scope; ratings in `docs/ratings.md`; packets in `docs/packets` (committed + pushed before dispatch).
- EROFS sandbox: container-exec is the writable path. Jina gate inert until `SG_MONTHLY_CAP` set. `sg026`-freeze stays retired (D18).
- Adaptation note: tasks below are dispatch slices, not inline code steps — each task's implementer is the Coder reading its packet, so steps name scope + acceptance + guards instead of pasting implementation code the Architect must not invent.

---

### Task 1: SG-142 cap-join fix

**Files:**
- Modify: `backend/app/services/providers/reader.py` (`_recorded_spend`, ~line 270)
- Test: `backend/tests/test_sg132_jina_ledger_wiring.py`, `backend/tests/test_sg125_ledger_retention.py`
- Read first: `backend/app/api/v1/enrich.py:80-100` (monthly gate consumer of the figure)

**Interfaces:**
- Consumes: live spend figure currently reads 0.0067 vs 0.0104 true (`F-SG132-5`: inner join over `Job` ignores `None`-job rows).
- Produces: corrected month-boxed spend reader both gates consume; exact delta quoted live.

- [ ] **Step 1: Packetize** — write `docs/packets/SG-142-cap-join.md` (0.40.0 echo; fail-pre test proving `None`-job rows uncounted; fix; suite + lint + typecheck + secret gates; no refresh unless served code changes), commit, push.
- [ ] **Step 2: Dispatch** — `SG-142` via `job_spawn` array form, covering cap.
- [ ] **Step 3: Audit + rate** — raw-byte grounding; row in `docs/ratings.md`; disposition `F-SG132-5`.
- [ ] **Step 4: Chain or halt** — green continues to Task 2; STOP-gate returns with a decision.

### Task 2: SG-143 extraction remainder (className-prop word carried)

**Files:**
- Modify: `frontend/src/components/HouseholdSelector.tsx` (add `className` passthrough prop — the API change SG-138 declined), `frontend/src/routes/CapturePage.tsx`, `frontend/src/routes/InboxPage.tsx`, `frontend/src/routes/CatalogPage.tsx` or `frontend/src/components/shell/CatalogToolbar.tsx` (whichever the packet verifies)
- Test: `frontend/src/components/HouseholdSelector.test.tsx`, `frontend/src/routes/theme-adoption.test.tsx:219-228`, `frontend/src/routes/InboxPage.test.tsx:75-81`
- Read first: `docs/worklogs/SG-138_report.md:33-77` (F-2/F-3 blocked-page analysis), `SG-138 (g) recommendation:134-139`

**Interfaces:**
- Consumes: shipped subset (Chat/Planning ported verbatim); three blocked pages (Capture/Inbox themed-class regression, Catalog select in toolbar).
- Produces: all three pages through the shared selector with themed class preserved; full frontend suite green.

- [ ] **Step 1: Packetize** — state the className-prop API choice explicitly (L3 carries the word); equivalence mapping per page; full vitest + eslint gates.
- [ ] **Step 2: Dispatch** — `SG-143` via `job_spawn`, covering cap.
- [ ] **Step 3: Audit + rate** — mapping table verified against shipped code; disposition `F-SG138-1`.
- [ ] **Step 4: Chain or halt.**

### Task 3: SG-144 runbook-command guard

**Files:**
- Modify: `README.md` runbook command strings ONLY if drifted (else byte-identical) + new guard test (expected home: `backend/tests/test_backup_drill.py` or beside it — VERIFY the file on the target, never inherit the path)
- Read first: `README.md:26,33-34,63-65,121-136` (backup command strings), `backend/scripts/backup_restore_drill.py` (SG-086 runbook form), `docs/worklogs/SG-126_report.md:85-110`, `docs/backlog.md:12`
- Correction 2026-09-29: no wording subtask — `F-SG140-2` is a queue-list premise delta (`SG-140_report.md:130`), not a wording task; retired pre-dispatch.
- Create: runbook-command guard test pinning command strings to live paths (instances: SG-126 doubled `/_data`, `F-SG131-1`)
- Read first: `docs/worklogs/SG-126_report.md:85-110`, `docs/backlog.md:12`

**Interfaces:**
- Consumes: wording premise verified at packetize time (never inherited); runbook drift instances.
- Produces: wording corrected; guard green with a seen-to-fail leg (mutated command string trips it).

- [ ] **Step 1: Packetize** — guard shape named (pins README command strings to the SG-086 runbook form, seen-to-fail leg required); drift repaired only if the strings drifted.
- [ ] **Step 2: Dispatch** — `SG-144` via `job_spawn`, covering cap.
- [ ] **Step 3: Audit + rate** — dispositions `F-SG126-3` (+ wording family).
- [ ] **Step 4: Chain or halt.**

### Task 4: SG-145 lane items (`--sql` fts limit + host `gh` auth)

**Files:**
- Verify at packetize time: `--sql` offline path (fts surface) + host `gh` auth state (`gh` unauthenticated on host per standing thread)
- Test: affected-tests only per `CO-101`

**Interfaces:**
- Consumes: two lane limitations, each small and independent.
- Produces: `--sql` fts limit resolved or scoped with evidence; `gh` auth either repaired or returned as owner-relay need (desk boundary).

- [ ] **Step 1: Packetize** — probe-first shape; if `gh` needs owner action, packet states the relay ask instead of a fix.
- [ ] **Step 2: Dispatch** — `SG-145` via `job_spawn`, covering cap.
- [ ] **Step 3: Audit + rate.**
- [ ] **Step 4: Chain or halt.**

### Task 5: Hue verdict (owner, no slice)

**Files:** none — screenshots only.

- [ ] **Step 1: Capture fresh screenshots** post-deploy of Inbox/Capture/Catalog.
- [ ] **Step 2: Owner gives keep/change verdict** — closes the dark-link hue item with no dispatch.

### Task 6: Context Scene resume word + close-out deploy

**Files:** close-out rider touches served code only via rebuild/recreate.

- [ ] **Step 1: Name the resume word** — date + entry condition (D7 model pick, D4 second provider, D132 §1.4 reopen).
- [ ] **Step 2: Close-out deploy slice** — rebuild + exactly one recreate + verify (health ×6, gate, alembic, counts delta), zero product hunks expected.
- [ ] **Step 3: Audit + rate** — image id recorded; pile confirmed zero.
- [ ] **Step 4: Close** — tree clean + pushed; END filed on `Andovol/Launcher#62`; starter handed.
