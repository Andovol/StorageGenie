# StorageGenie — project configuration

> Canonical for this repo. `CLAUDE.md` only points here — edit here, never there.
> Rule-set version recorded here: 0.56.0. Past version notes, old values, and decision numbers moved to `docs/decisions/2026-10-23-agents-plain-language-history.md`.

Slices are numbered with the prefix SG, which stands for StorageGenie (for example SG-1, SG-2). Autonomy L3 means the owner approves a stage (a named set of slices toward one outcome); inside it the Architect packets, dispatches, audits and rates without asking, and the builder owns retries inside each slice.

## Configuration table — every project value in one place

| Field | Value | Why |
|---|---|---|
| **Workspace** | `C:\Coding\OpenCode\StorageGenie` on this computer, `/home/andrei/StorageGenie` on the server | This computer holds the `automation` branch; the server holds the live app. The server guide in the shared contract is the authority on host details. |
| **Repository** | `Andovol/StorageGenie` | One place holds the code. The main work branch is `automation`. |
| **Host** | `87.106.66.242`, port `2222`, user `andrei` | This is the computer that runs the live app. |
| **Host project path** | `/home/andrei/StorageGenie` | The owner chose this folder on the server. |
| **Credential** | `~/.ssh/storagegenie-architect-dispatch` on this computer, plus a provisioning key kept on the owner's desk | The first key is the only key the dispatch uses. It can only run the dispatch command on the server and cannot open a shell. |
| **Coder** | `opencode`, run as `opencode run --auto --dir <work folder> [--variant <effort>] <task text>` | The owner chose this builder going forward. The task text travels on the command line. Effort is always stated on the trigger and stays far under the command-line size limit. |
| **Dispatch verb** | `SG-<number> [coder=... model=... effort=...] [agent=...] [--status\|--attach\|--force\|--quarantine]` | This is the single command that starts a slice. Settings ride on the trigger; the task file itself carries only the task. `--force` replays a finished slice; `--quarantine` isolates a broken run. |
| **Harness** | Server runs in the background and wakes this session when done | Background runs never block the planning chat. Status checks only re-attach; they never carry the task. |
| **Wrapper** | `/usr/local/bin/dispatch` on the server | This is the only entry point the server key can run. It picks settings from the trigger command first. |
| **Model policy** | Every trigger states the model and effort explicitly, currently `model=opencode-go/deepseek-v4.1-flash effort=max` | Stating both on every trigger stops silent drift between slices. |
| **Second opinion** | `coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh`, dispatched with `agent=plan` | The contract's default, resolved for this project: the Architect runs on `opencode-go/minimax-m3.1-flash`, so the reviewer must not be that model, and the slice builder must not be the reviewer either. |
| **Packet directory** | `docs/packets` | Task files are committed and pushed, so the server always reads what this computer sent. |
| **Autonomy** | L3 | The owner approves a stage — a named set of slices toward one outcome, stated in the approval message. Inside the stage the Architect packets, dispatches, audits and rates each slice without asking. The builder owns one retry inside a slice and returns after that. A stage boundary is a new approval. |
| **Close-out** | Deploy every app-changing slice as its own slice, right after it is rated, and deploy the live app before every close | The owner asks for a live check at every close. Work that is unrated or blocked stops the deploy instead of shipping silently. |
| **Values bindings** | See the table below | The coder contract uses placeholders in double braces. Every placeholder it reads must have a value here, or the run stops. Never guess a value. |

## Values table — what each placeholder means

| Placeholder | Value | Why |
|---|---|---|
| `{{WORKLOG_DIR}}` | `docs/worklogs` | Each slice writes its work log here. |
| `{{HEALTH_CMD}}` | `curl -s http://127.0.0.1:8003/v1/health` | This probe proves the database and storage answer. The builder runs it at the start and end and reports the change. |
| `{{RECEIPT_CMD}}` | Notes-based receipt on the server | The builder leaves a note on the report that states the slice number and the report path, read back from the server. |
| `{{PROD_DB}}` | Local files only — app database `sqlite:////data/db/storagegenie.db` plus storage folder `storage_data:/data/storage` | Phase zero runs on the local computer with no separate production database. |
| `{{TEST_DB}}` | Local test database only | Tests use a temporary database, never the live one. |
| `{{DEFAULT_BRANCH}}` | `automation` | Work starts here; evidence lives on its own branch. |
| `{{DISPATCH_KEY}}` | `~/.ssh/storagegenie-architect-dispatch` | The only key the dispatch uses. |
| `{{HOST}}` | `87.106.66.242` | The live computer. |
| `{{HOST_SSH_PORT}}` | `2222` | The port the live computer listens on. |
| `{{HOST_USER}}` | `andrei` | The account that runs the live app. |

A placeholder with no value here stops the run.

## Method routing — what to read, and when

- Before planning, writing a task, dispatching, auditing, rating, or touching project state: read the architect guide.
- Before writing a task file: read the packet guide.
- Before dispatching: read the dispatch guide (plus the production guide, because the host and database are live).
- Before closing: read the close guide.
- Before rating: read the ledger guide.
- Before bringing the owner any 🟠 or 🔴 decision item: **run** the second opinion (two phases), not only read its guide. See the project rule below.
- Before changing a rule: read the reasoning guide.
- Before planning anything on the shared server: read the server guide.

The coder reads its own copy on the server and never reads from this repo.

## Project rules — small additions to the shared rules

- **Upload cap:** 20 megabytes in `backend/app/config.py` is a hard security limit. A larger upload gets a too-large answer, never a silent cut.
- **No second copies:** where this repo repeats a shared rule, the shared rule wins and this copy is only a pointer.
- **Sensitive areas:** the stored photos and files, the app database, and the dispatch key and host. Every plan touching one goes to the owner alone, at every autonomy level. An area not listed here is not declared safe — it is simply not declared.
- **Restart:** both app services restart on their own unless stopped.
- **Health:** the health address proves database plus storage. The builder runs the health probe at start and end.
- **Second opinion before the owner** (owner, 2026-10-24): every 🟠 or 🔴 decision item goes through the two-phase second opinion **before** the owner sees it, and so does a 🟡 item whose subject is the live host, the dispatch key, the app database, or the owner's own data. Never for 🔵. The review runs on the project's own lane with `agent=plan`; the review ID and the disposition go into the decision item and into `docs/reviews/review-ledger.md`.

## What this repo already owns

Pinned state from before onboarding lives in git history and the history file named at the top. Forty old obligations were sorted once; none conflicted. New work starts here.

## Loading

- At session start, check versions first with the one contract command, then read this file, the contract cache, and the resume block in `STATE.md`.
- Before a task file, read the packet guide; before dispatch, read the dispatch guide plus the production guide.
- Never copy shared contract files into this repo — this file holds only values and small additions.
