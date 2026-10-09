# StorageGenie — project configuration

> **Canonical for this repo. `CLAUDE.md` is a one-line adapter `@AGENTS.md` — edit here, never there.**
> Rule-set version this project records: **0.44.1** (D-1009-1 adoption 2026-10-09: checkouts `0989384` (0.41.0) + `bf68d23` (0.42.0) + `3b5ab73` (0.43.0) + `1cd0756` (0.44.0) + `04a4b53` (0.44.1) oldest-first; delta = 0.41.0 `rules_check.sh` (D339) + report trim (D351/D345/D346) + `CO-53` prefix (D341) + `CO-102`/`CO-40` + `G-M6`/`G-M8` tighten + 0.42.0 ARCHITECT slim (§7→DISPATCH §7, D365) + `G-T6`/`PG-EV-14`/`PG-SC-13` + 0.43.0 shared-runner-only (D373) + `G-A7` merge-note + lane-actual durations + 0.44.0 `G-M5` new decision shape (D388) + probe byte-check (D385) + lane allowlist (D387) + 0.44.1 VERSION-only (`RULES.md` unchanged); installed `F2565B1C…` = payload `RULES.sha256` at 0.44.1 — clean; supersedes `0.40.0`).

## Configuration table — the single source of every project value

| Field | Value | Notes |
|---|---|---|
| **Workspace** | `C:\Coding\OpenCode\StorageGenie` (local) → `/home/andrei/StorageGenie` (VPS) | Local is `automation` branch, VPS is `andrei@87.106.66.242:2222:/home/andrei/StorageGenie` — `VPS.md` (contract `.rules-cache/`) is the host authority |
| **Repository** | `Andovol/StorageGenie` (`git@github.com:Andovol/StorageGenie.git`) | Create if absent; default branch `automation`, evidence ref `refs/heads/storagegenie-evidence` (per `CO-86`) |
| **Host** | `87.106.66.242:2222` (`ubuntu`, `andrei`) | `VPS.md` F2 — pin against `[87.106.66.242]:2222` in `~/.ssh/known_hosts` |
| **Host project path** | `/home/andrei/StorageGenie` | Owner directive `m0045` — use this folder |
| **Credential reference** | `~/.ssh/storagegenie-architect-dispatch` (ed25519, `~/.ssh/storagegenie-architect-dispatch.pub` on host forced-command) + unrestricted `C:\Users\popes\Desktop\key_Andrei.ppk` (Launcher-only, provisioning) | Naming `<project>-architect-dispatch` per `PROVISIONING.md:129` — private never on host |
| **Coder** | `opencode` (SELECTED from `CODERS.md` — `opencode run --auto --dir <workdir> [--variant <effort>] <prompt-text>`, prompt travels on argv) | Owner directive `D29` (2026-09-11) — opencode going forward; supersedes `m0106` (codex high, kept as history). `G-O2` — packet says "the Coder", config names it. Effort `low|high|max` for opencode (lane refuses `medium`/`xhigh` by name) → `--variant` (explicit `high` on every trigger per D120/D15, uncalibrated per `G-A9`; the Coder default `max` is NOT taken — stated explicitly so no silent drift). Catalogue `coder_models.tsv` (0.44.1, re-measured 2026-10-08): `high` listed for `opencode-go/deepseek-v4.1-flash` — engine-checked strictly, trigger effort (D266/D302). Hard ceiling: packet file stays far under the 128 KiB single-argv limit. Provider partially unproven (`ISS-6`); entry-point run-2 owed (`ISS-7`) |
| **Dispatch verb** | `SG-<nnn> [coder= model= effort=] [--status\|--attach\|--force\|--quarantine]` (e.g. `SG-021 coder=opencode effort=high`) | ID prefix `SG-` for StorageGenie. Settings ride the trigger, any subset (D302) — the packet carries the task only; a packet `coder:`/`model:`/`effort:` line is refused `packet_settings_retired`. `--force` bypasses replay guard only, `--quarantine` per `DISPATCH.md` §2 (D331), packet resolves `$ID.md\|$ID-*.md` exactly-one |
| **Harness** | OpenCode — background dispatches ride `job_spawn` (wake on exit), status verb only for re-attach checks, never the trigger log (`DISPATCH.md` §2c) | Owner directive 2026-09-12: use the `job_spawn` spawner for background dispatch (supersedes the Start-Process + blocking-wait chunking) |
| **Wrapper** | `/usr/local/bin/dispatch` (forced command `DISPATCH_CONF=/etc/dispatch/storagegenie.conf /usr/local/bin/dispatch`; `run-coder` takes settings from the dispatch command → lane conf → Coder default, packet settings refused per D302) | Measured 2026-09-21 by SG-071 (journal + launch artifact); supersedes the stale `/opt/storagegenie-dispatch/dispatch_coder.sh` path (legacy grok-codex-only whitelist, never reads the opencode coder) |
| **Model policy** | No model id sent on the trigger (contract-legal subset, D302); an omitted model resolves via lane conf, then the Coder default `opencode-go/deepseek-v4.1-flash` (proven live SG-120) | Effort named explicitly per slice because the Coder default `max` differs from calibrated `high` (D120/D15); model omitted because the default already resolves to what runs |
| **Packet directory** | `docs/packets` (committed, pushed) | `DISPATCH.md:49` — unpushed packet fails as `packet_missing` |
| **Autonomy** | `L2` (slice autonomy, 1 retry, per `ARCHITECT.md:60-72` §6) — escalates to `L3` only after clean stage | State the level in approval message |
| **Close-out** | Live deploy (rebuild + one recreate + verify) before every session close | Standing owner directive 2026-09-28 ("Always do a live deploy before session close", `G-O4` record) — the rider runs as a dispatched slice and is reported; unrated or blocked work stops the deploy, never ships silently |
| **Values bindings** | See Values table below — every `{{NAME}}` the contract uses is bound there | `CO-08` stop if unbound |

## Values table — every `{{NAME}}` the Coder contract reads

| `{{NAME}}` | Bound value | Source |
|---|---|---|
| `{{WORKLOG_DIR}}` | `docs/worklogs` | Coder worklog per slice (`CO-57`) |
| `{{HEALTH_CMD}}` | `curl -s http://127.0.0.1:8003/v1/health` (fallback `python3 -c "from fastapi.testclient import TestClient; from app.main import app; print(TestClient(app).get('/v1/health').json())"`) | `ARCHITECT.md` health probe |
| `{{RECEIPT_CMD}}` | notes-ref receipt (live lane mechanism) | Note on `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: <ID> | Report: <path>` (+ `Work-HEAD`), read back on remote by mapped fetch (SG-092/SG-156 precedent); legacy `/opt/storagegenie-dispatch/finalize_dispatch_report.sh` (v0.17.2 evidence-ref) refused `candidate_not_remote` on this lane — retired 2026-10-09 (F-SG156-1) |
| `{{PROD_DB}}` | `not applicable` — Phase 0 is SQLite local (`sqlite:////data/db/storagegenie.db`) + `storage_data:/data/storage` | `blueprint.md:14` local-first; `CODER_PRODUCTION.md` not bound until datastore declared |
| `{{TEST_DB}}` | `not applicable` | Same — tests use `TestClient` + temp SQLite |
| `{{DEFAULT_BRANCH}}` | `automation` | Current branch (`git branch --show-current`) — evidence `storagegenie-evidence` |
| `{{DISPATCH_KEY}}` | `~/.ssh/storagegenie-architect-dispatch` | Layer A — forced-command at `andrei@87.106.66.242:2222` |
| `{{HOST}}` | `87.106.66.242` | `VPS.md` F2 |
| `{{HOST_SSH_PORT}}` | `2222` | `VPS.md` F2 |
| `{{HOST_USER}}` | `andrei` | `VPS.md` F2 + dispatch key binding |

`{{NAME}}` not listed is a `CO-08` STOP — never guess, never use placeholder literally.

## Method routing — what loads, when

`ARCHITECT.md` before planning/packet/dispatch/audit/rating/touching state · `PACKET.md` before writing a packet · `DISPATCH.md` before dispatching · `CLOSE.md` before closing · `LEDGER.md` before rating · `RATIONALE.md` before changing a rule · `VPS.md` before planning anything on the shared VPS (a web page, a hostname, a port, a database, heavy work)

Coder reads read-only copy on host (`/opt/storagegenie-dispatch/` + global `CODER.md` + `lang/python.md`) — never from repo (cutover pattern; the copy's version tracks the adopted rule set).

## Project narrowings of global rules — may narrow, never contradict (`G-P2`)

- **Budget:** `G-A8` — 20 MB upload cap (`backend/app/config.py:20`; corrected 2026-09-17 by SG-061 — was `:11`) is a security hard cap with visible `413` truncation, not a silent guideline.
- **Duplicate:** `docs/decisions/2026-08-28-phase-0-approvals.md:33-41` Launcher block duplicates `G-O1`, `G-P2`, `G-C1` — keep global, project copy is a pointer not a second copy.
- **Sensitive surfaces (`G-K3`) — declared per `PRODUCTION.md` trigger:** evidence store (`/data/storage` + `backend/data/storage`), SQLite DB (`/data/db/storagegenie.db`), dispatch host/credential. Every decision touching any goes to owner individually (`G-K2`) at every autonomy level. A surface not listed is "not declared", never "safe".
- **Restart allowlist:** `docker-compose.yml:19,37` `restart: unless-stopped` both services — `PRODUCTION.md:restart` binding if declared.
- **Health:** `G-T9` — `GET /v1/health` proves DB+storage; Coder runs `{{HEALTH_CMD}}` start+end per `CO-92` and reports delta.

## What this repo already owns — conserved on cutover (`ONBOARDING.md` conversion)

Pinned pre-conversion state `26e9e8b` (local `automation` head `26e9e8b→9f1cc09→d43d793→74d066b→ad20dc0→bad8bff:550b35c`). Disposition `m0064` — 40 obligations dispositioned `keep`/`covered`/`retire`, zero `CONFLICT`. New obligations start here.

## Loading

- Session start: `G-L1` version check FIRST (run `bash .rules-cache/rules_check.sh` per D339 and write its output down; never checkout-vs-stamp, M3), then this file + `.rules-cache/` (contract `contract-v0.44.1`) + `STATE.md:1` RESUME.
- Before packet: `PACKET.md`; before dispatch: `DISPATCH.md` (+ `PRODUCTION.md:1` because host + SQLite are live).
- Never copy shared contract into repo — project holds only values and narrowings.
