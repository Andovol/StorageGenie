# SG-121 — Non-empty activation probe: do the G3+G4 surfaces answer against real rows

**Dispatch-ID:** SG-121
**Coder / effort:** `opencode` / effort **`high`** — read from the process arguments
(`pgrep -af "opencode run"` → `opencode run --auto --dir /home/andrei/StorageGenie --variant high # SG-121 …`).
**MODEL:** `opencode-go/deepseek-v4.1-flash` — read from provider metadata
`/home/andrei/.local/state/opencode/model.json` `recent[0]` (`{"providerID":"opencode-go","modelID":"deepseek-v4.1-flash"}`);
the argv carries no `--model`, so the CLI default is the model. Not taken from a system-prompt identity line.
**Work dir:** `/home/andrei/StorageGenie` · **branch** `automation` · **remote** `git@github.com:Andovol/StorageGenie.git`.
**BASE REF:** `origin/automation` → **BASE_RESOLVED:** `cc0a27c32fac557412a0ffb15b8aad797f55310e`
(== start HEAD; two fields, never one).
**WORK_HEAD:** `f1c8b67512e2a265bef701028a8415416d8e0e36` (the work commit that carries this worklog set).
**DATABASE:** live, READ-ONLY · **Restart:** none · **Deploy:** none · **Container actions:** none
(read-only `docker exec` probes only).
**Autonomy:** L2 slice (packet); 1 retry available, not used.
**Spend (real $):** **$0.000000** actual vs $0 bound — zero metered provider calls.
**Coder process start:** 2026-09-25T12:37:04Z (live shell clock).

**Contract echo (verbatim, source path):** recorded **`0.37.0`** == published **`0.37.0`** —
source `/home/andrei/storagegenie-contract/VERSION` = `0.37.0`; contract HEAD
`1acd7730e5fa6de5b7403aacce71207e9946461d` (== packet's `1acd773`); installed `RULES.md` sha256
`18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`.
The repo's `.rules-cache/` directory is **absent** on this host (F-SG121-1), the standing observation
of SG-062/SG-078/SG-099/SG-104..120; the host checkout above is the authority.

## G0 — capability + census (before anything moved)

Quoted exact in `SG-121_verify.log`. Summary:

- `docker ps`: `storagegenie-backend-1  Up 2 hours (healthy)  127.0.0.1:8003->8000/tcp`.
- health exact: `{"status":"ok","db":"ok","storage":"ok"}`.
- **gate:** `GET /v1/locations` with no `household_id` → **HTTP 422** (`missing household_id`); with the
  live id → **HTTP 200**. The flag dependency is the gate and it passed (the handler is reached; not 404).
  There is **no 301/401 auth/redirect gate** on these routes — the packet's "gate 301/401" hypothesis was
  **not observed** (F-SG121-2), reported rather than bent.
- `alembic current` → `20260924_sg114_relation (head)` — **matches** the packet hypothesis.
- table set: 28 tables, `location` + `asset_location` + `asset_relation` all present — **matches**
  the SG-115 hypothesis.
- census (queries in verify log):
  `SELECT count(*) FROM location` → **0**; `asset_location` → **0**; `asset_relation` → **0**.
  `household` COUNT **1**, live id `01a0a029-1477-7ca0-b200-bce78a96c679`; `asset` COUNT **6**, all under
  that household; probe asset `01a0a467-eb0e-7b83-a227-af122dc9268b`. **Every live id came from a quoted
  SELECT — none guessed.**

**Hypothesis misses (stated, never bent):** (1) `.rules-cache/` absent (F-SG121-1); (2) gate is 422, not
301/401 (F-SG121-2); (3) `STATE.md:2` still reads `contract 0.36.0` while `AGENTS.md:4` + the host
contract record `0.37.0` adopted (F-SG121-3, STATE not writable here). All other G0 hypotheses held.

## G1 — locations legs (real routes, real bodies)

- `GET /v1/locations?household_id=01a0a029-…` → **HTTP 200**, body exactly `{"items":[]}`. **Zero rows.**
  The conditional "GET one location by id" leg is therefore **N/A — there is no id to fetch** (not an
  error, not skipped).
- `GET /v1/assets/01a0a467-…?household_id=01a0a029-…` → **HTTP 200**; the `locations` key is **present and
  `[]`** (not absent, not row-bearing). Presence proves SG-115's flag is ON live; emptiness is the verdict
  discriminator.

## G2 — relations legs (same discipline)

- `GET /v1/assets/01a0a467-…/relations?household_id=01a0a029-…` → **HTTP 200**, body exactly `{"items":[]}`.
  **Zero rows**; the "narrowest row-bearing fragment" leg is **N/A — no row exists**.
- Asset detail (same body as G1) → the `relations` key is **present and `[]`** (not absent, not row-bearing).

Route paths were verified in source, not assumed: `locations.py:125`, `relations.py:102`,
`assets.py:377`, and the conditional detail keys at `assets.py:169-185`.

## G3 — verdict (exactly one line)

**ACTIVATED-EMPTY — all five read legs returned HTTP 200 but zero rows everywhere counted (`location`/`asset_location`/`asset_relation` all COUNT 0, `{"items":[]}` on both list routes, `locations:[]`/`relations:[]` on detail), so non-empty activation proof is still owed.**

**Seeding follow-up (outline only — implemented nowhere here).** A future slice under its own D-word
(a write is required, D16) should create the minimum rows through the **real write routes** — never raw
SQL: `POST /v1/locations?household_id=<id> {"name":"Kitchen"}`, then
`POST /v1/assets/<asset>/locations {"location_id":…}`, then
`POST /v1/assets/<a>/relations {"to_asset_id":<b>,"relation_type":"related_to"}` — then re-run the exact
G1/G2 GETs above and quote a non-empty body. One-line reason it is owed: a 200 against an empty table
evidences ACTIVATED-EMPTY, never non-empty activation.

## No vacuous pass

- Every executed GET is quoted with status + body (`{"items":[]}`, `{"items":[]}`, and the detail tail
  `"locations":[],"relations":[]`); no criterion passed on an empty or narrowly scoped grep.
- The zero counts are **globally** zero (`SELECT count(*)`, no household filter), so the emptiness is not
  an artifact of picking the wrong household.
- The conditional "by-id" legs are named **N/A** with the reason (no rows), not silently omitted.
- The verdict is ACTIVATED-EMPTY precisely because a 200 alone was **not** taken as activation proof.

## Scope ceiling

`git status --porcelain` before commit 1 shows exactly the three `docs/worklogs/SG-121.*` files. No route
write, no DB write/DDL, no code/tests/prompts/compose/`.env`/migrations/STATE/AGENTS write. No build, no
container action beyond read-only `docker exec`. Nothing pushed to `storagegenie-evidence`;
`{{RECEIPT_CMD}}` not invoked. No seeding, no flag change, no recreate.

## Receipt (notes ref)

Commit 1 (work) = `f1c8b67512e2a265bef701028a8415416d8e0e36`, pushed to `automation` (`cc0a27c..f1c8b67`).
Note anchored on `WORK_HEAD`; worktree clean. Pasted verbatim from the **fetched mapped ref**
(`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg121-verify`):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show f1c8b67512e2a265bef701028a8415416d8e0e36
error: no note found for object f1c8b67512e2a265bef701028a8415416d8e0e36.
pre_show_exit=1                                   # no existing note -> refusal guard did not fire

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-121 | Report: docs/worklogs/SG-121_report.md | Work-HEAD: f1c8b67512e2a265bef701028a8415416d8e0e36" f1c8b67512e2a265bef701028a8415416d8e0e36
add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   9e5056a..c717e11  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg121-verify
ok fetched (1 new refs)
fetch_exit=0

$ git notes --ref=refs/notes/sg121-verify show f1c8b67512e2a265bef701028a8415416d8e0e36
Dispatch-ID: SG-121 | Report: docs/worklogs/SG-121_report.md | Work-HEAD: f1c8b67512e2a265bef701028a8415416d8e0e36
show_exit=0
```

note=yes

## Budget (actual vs bound, units)

| Leg | Actual | Bound | Units |
|---|---|---|---|
| Recon + contract + G0 census | ~60 | 60/command | s |
| G1+G2 route GETs (4 calls) | ~3 | 60/command | s |
| G4 worklog writes | ~20 | 60/command | s |
| Commit + push + notes + mapped verify | ~90 | 300 | s |
| **Slice total (process start → close)** | **~300** | **~300 expected** | **s** |

Every command returned within its stated bound; **no command was killed, nothing hung**. Actual is a
wall-clock reading from the live shell clock (`date -u`), uncalibrated per `G-A9`. Spend $0.000000.

## UNCLEAR

- **FIRST READ:** the tree's live data is **entirely empty** for the G3+G4 surfaces — all three tables
  `COUNT 0` — so the packet's question ("do the surfaces answer against NON-EMPTY data") is answered
  *no* by construction, not by a bug: ACTIVATED-EMPTY. The packet's "gate 301/401" hypothesis is also not
  what this tree does (the flag gate yields 422/200, never 301/401); both stated as findings F-SG121-2/3.
- **DURING EXECUTION:** no probe was denied and nothing hung; the only blocker to a non-empty verdict is
  the absence of data, which the standing lines forbid me to create. `.rules-cache/` is absent (standing)
  so the contract echo comes from `/home/andrei/storagegenie-contract/`.
- **REMAINING:** non-empty activation proof is still owed and needs a **seeding slice under its own
  D-word** (outline above, the real write routes, never raw SQL). F-SG121-1 (`/.rules-cache` absent,
  standing) · F-SG121-2 (packet gate hypothesis 301/401 vs observed 422/200) · F-SG121-3 (`STATE.md:2`
  reads 0.36.0 while `AGENTS.md:4` + host contract read 0.37.0 — the Architect's write, not mine).
