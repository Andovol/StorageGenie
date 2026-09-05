# StorageGenie — project configuration

> **Canonical for this repo. `CLAUDE.md` is a one-line adapter `@AGENTS.md` — edit here, never there.**
> Rule-set version this project records: **0.17.2** (`C:\Coding\Claude\Launcher\VERSION` @ `0.17.2`, global `RULES.md` installed byte-identical).

## Configuration table — the single source of every project value

| Field | Value | Notes |
|---|---|---|
| **Workspace** | `C:\Coding\OpenCode\StorageGenie` (local) → `/home/andrei/StorageGenie` (VPS) | Local is `automation` branch, VPS is `andrei@87.106.66.242:2222:/home/andrei/StorageGenie` — `reference/vps-info.md` is authority |
| **Repository** | `Andovol/StorageGenie` (`git@github.com:Andovol/StorageGenie.git`) | Create if absent; default branch `automation`, evidence ref `refs/heads/storagegenie-evidence` (per `CO-86`) |
| **Host** | `87.106.66.242:2222` (`ubuntu`, `andrei`) | `reference/vps-info.md:27-28` — pin against `[87.106.66.242]:2222` in `~/.ssh/known_hosts` |
| **Host project path** | `/home/andrei/StorageGenie` | Owner directive `m0045` — use this folder |
| **Credential reference** | `~/.ssh/storagegenie-architect-dispatch` (ed25519, `~/.ssh/storagegenie-architect-dispatch.pub` on host forced-command) + unrestricted `C:\Users\popes\Desktop\key_Andrei.ppk` (Launcher-only, provisioning) | Naming `<project>-architect-dispatch` per `PROVISIONING.md:129` — private never on host |
| **Coder** | `codex` (SELECTED from `global/CODERS.md` — `codex exec --sandbox danger-full-access [-m <model>] [-c model_reasoning_effort=<effort>] -C <workdir> < <prompt-file>`) | Owner directive `m0106` — codex high until countermanded; supersedes `m0083` (`codex` → `grok`, kept as history). `G-O2` — packet says "the Coder", config names it. Allowed effort `low|medium|high|xhigh` (`medium` default; `xhigh` valid on the `0.18.1` runner — the old wrapper's `max` was the drift) |
| **Dispatch verb** | `SG-<nnn> <coder> [effort]` (2-6 tokens, e.g. `SG-001 codex medium`) | ID prefix `SG-` for StorageGenie. Transitional (`ISS-77`): keep params in verb until the `0.18.1` runner parses the short form |
| **Harness** | OpenCode — **Class 4** | `HARNESSES.md` — the Class 2 `prompt_async` path is DOCUMENTED with addressing unverified, so this harness operates as Class 4 until a wake probe observes a resume. Checks run the status verb, never the trigger log (`DISPATCH.md` §2c) |
| **Wrapper** | `/opt/storagegenie-dispatch/dispatch_coder.sh` (`root:root 755`, outside project tree) | Per `PROVISIONING.md:132-142` four fixes — outside `ReadWritePaths`, explicit `PATH`, `ReadWritePaths=~/.codex + ~/.grok`, enumerate `InaccessiblePaths` at dispatch time |
| **Model policy** | No model id sent; CLI default IS model | Per `CODERS.md` Effort section — effort chosen per slice and recorded, model omitted |
| **Packet directory** | `docs/packets` (committed, pushed) | `DISPATCH.md:29` — unpushed packet fails as `packet_missing` |
| **Autonomy** | `L2` (slice autonomy, 1 retry, per `ARCHITECT.md:78-88`) — escalates to `L3` only after clean stage | State the level in approval message |
| **Values bindings** | See Values table below — every `{{NAME}}` the contract uses is bound there | `CO-08` stop if unbound |

## Values table — every `{{NAME}}` the Coder contract reads

| `{{NAME}}` | Bound value | Source |
|---|---|---|
| `{{WORKLOG_DIR}}` | `docs/worklogs` | Coder worklog per slice (`CO-57`) |
| `{{HEALTH_CMD}}` | `curl -s http://localhost:8000/v1/health` (fallback `python3 -c "from fastapi.testclient import TestClient; from app.main import app; print(TestClient(app).get('/v1/health').json())"`) | `ARCHITECT.md` health probe |
| `{{RECEIPT_CMD}}` | `/opt/storagegenie-dispatch/finalize_dispatch_report.sh` | Wrapper + receipt publisher (`root:root 755`) — `refs/heads/storagegenie-evidence`, header `contract_sync=refresh version=0.17.2` (per `ARCHITECT.md:14` `DISPATCH.md:42-50`) |
| `{{PROD_DB}}` | `not applicable` — Phase 0 is SQLite local (`sqlite:////data/db/storagegenie.db`) + `storage_data:/data/storage` | `blueprint.md:14` local-first; `CODER_PRODUCTION.md` not bound until datastore declared |
| `{{TEST_DB}}` | `not applicable` | Same — tests use `TestClient` + temp SQLite |
| `{{DEFAULT_BRANCH}}` | `automation` | Current branch (`git branch --show-current`) — evidence `storagegenie-evidence` |
| `{{DISPATCH_KEY}}` | `~/.ssh/storagegenie-architect-dispatch` | Layer A — forced-command at `andrei@87.106.66.242:2222` |
| `{{HOST}}` | `87.106.66.242` | `vps-info.md:28` |
| `{{HOST_SSH_PORT}}` | `2222` | `vps-info.md:28` |
| `{{HOST_USER}}` | `andrei` | `vps-info.md:15` |

`{{NAME}}` not listed is a `CO-08` STOP — never guess, never use placeholder literally.

## Method routing — what loads, when

`ARCHITECT.md` before planning/packet/dispatch/audit/rating/touching state · `PACKET.md` before writing a packet · `DISPATCH.md` before dispatching · `CLOSE.md` before closing · `LEDGER.md` before rating · `RATIONALE.md` before changing a rule

Coder reads read-only copy on host (`/opt/storagegenie-dispatch/` + global `CODER.md` + `lang/python.md`) — never from repo (cutover pattern; the copy's version tracks the adopted rule set).

## Project narrowings of global rules — may narrow, never contradict (`G-P2`)

- **Budget:** `G-A8` — 20 MB upload cap (`backend/app/config.py:11`) is a security hard cap with visible `413` truncation, not a silent guideline.
- **Duplicate:** `docs/decisions/2026-08-28-phase-0-approvals.md:33-41` Launcher block duplicates `G-O1`, `G-P2`, `G-C1` — keep global, project copy is a pointer not a second copy.
- **Sensitive surfaces (`G-K3`) — declared per `PRODUCTION.md` trigger:** evidence store (`/data/storage` + `backend/data/storage`), SQLite DB (`/data/db/storagegenie.db`), dispatch host/credential. Every decision touching any goes to owner individually (`G-K2`) at every autonomy level. A surface not listed is "not declared", never "safe".
- **Restart allowlist:** `docker-compose.yml:19,37` `restart: unless-stopped` both services — `PRODUCTION.md:restart` binding if declared.
- **Health:** `G-T9` — `GET /v1/health` proves DB+storage; Coder runs `{{HEALTH_CMD}}` start+end per `CO-92` and reports delta.

## What this repo already owns — conserved on cutover (`ONBOARDING.md` conversion)

Pinned pre-conversion state `26e9e8b` (local `automation` head `26e9e8b→9f1cc09→d43d793→74d066b→ad20dc0→bad8bff:550b35c`). Disposition `m0064` — 40 obligations dispositioned `keep`/`covered`/`retire`, zero `CONFLICT`. New obligations start here.

## Loading

- Session start: this file + global `RULES.md` (via `~/.config/opencode/AGENTS.md`) + `STATE.md:1` RESUME.
- Before packet: `PACKET.md`; before dispatch: `DISPATCH.md` (+ `PRODUCTION.md:1` because host + SQLite are live).
- Never copy shared contract into repo — project holds only values and narrowings.
