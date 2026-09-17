# SG-055 — enablement probe: key + consent + restart check, read-only

**Dispatch-ID:** SG-055 · **Coder:** opencode · **Effort:** `low` (read from process args: `/proc/1384941: opencode run --auto --dir /home/andrei/StorageGenie --variant low …`) · **Model:** `unknown` (no model id on argv; the CLI default IS the model and is omitted per policy — never read from an identity line).
**Contract:** 0.27.0 (recorded == published payload == SG-049 receipt echo; packet states it). **Spend:** **real $0.000000** actual vs $0 bound — zero provider calls.
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** none. No DB touched, not even arithmetically. Read-only service/container probes only.

- **BASE REF requested:** `origin/automation`; **resolved commit:** `3b41d88e82791cfdc67fa7e90afe92c8412ad849` (`M31 compose env_file path correction (G-O4 record)`).
- **WORK_HEAD:** the commit carrying these three worklogs — stated in the delivery message (it cannot be stated inside a file that is itself part of that commit, same as SG-048/SG-049/SG-053/SG-054). The receipt note is attached to it LAST; no commit follows.
- **Run identity:** this is **run-2** of SG-055. Run-1 (`1e0f5b3`, rated 98 at `79c831f`) returned STOP-as-SUCCESS with gate legs (a) and (c) false because `SG_CONSENT` was not visible to the backend. Run-2 measures the tree **after** the owner's enablement and the `M31` compose `env_file` path correction.

## 1. G1 — the four establishments, READ-ONLY, quoted FIRST (both outcomes handled)

Raw outputs in `docs/worklogs/SG-055_verify.log` §V2. Every property is quoted, never a bare exit code.

**(a) served consent JSON — `GET /v1/settings/ai` (loopback):**
```
{"provider_id":"fake","model_id":"deepseek-v4-flash-vision-exp","allowed_model_ids":["deepseek-v4-flash-vision-exp"],"consent":true,"per_job_cap":null,"monthly_cap":null,"prompt_category":"food"}
```
→ `consent` = **true**.

**(b) provider key EXISTS — existence-only probe from INSIDE `storagegenie-backend-1` (boolean + length; zero key bytes):**
```
opencode_api_key_present= True
key_len= 67
consent= True
provider_id= fake
```
→ key present = **true**, len **67**. **No key byte was printed, logged, quoted, or committed.** `docker compose config` was **never run** (`PG-SC-05`).

**(c) `ai_status()`-equivalent — same container:**
```
ai_status= (True, 'enabled')
```
→ enabled for the configured provider (`provider_id=fake`).

**(d) backend container post-restart — read-only `docker inspect`:**
```
StartedAt=2026-09-17T11:45:59.396847235Z Image=sha256:4f338b356945f9a8f960ecd3f50a3890a7c2b6d536ea4312c4f66e25e2f78f5e ImageID=sha256:4f338b356945f9a8f960ecd3f50a3890a7c2b6d536ea4312c4f66e25e2f78f5e
```
`docker ps` at probe time: `Up 46 seconds (healthy)`, `127.0.0.1:8003->8000/tcp`. Wall clock at probe: `2026-09-17T11:46:48Z` — the container started ~49 s earlier and `consent=true` is served live.

**Load-bearing reasoning:** live settings come from env at process start (SG-031: a restart drops overrides). `consent=true` served live **proves** the restart took effect; a served `consent=false` would be a STOP no matter what `StartedAt` said. Supporting health read: `{"status":"ok","db":"ok","storage":"ok"}`.

**VERDICT: GO** — all of (a)+(b)+(c) true, (d) consistent. The SG-049 live leg may be re-dispatched.

## 2. Starting tree (clean expected; dirt = STOP first)

```
$ git status --porcelain          # (empty)
$ git branch --show-current       # automation
$ git rev-parse HEAD ; git rev-parse origin/automation
3b41d88e82791cfdc67fa7e90afe92c8412ad849
3b41d88e82791cfdc67fa7e90afe92c8412ad849
```
Clean and level — no STOP. **No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.**

## 3. Premises re-verified in-slice (quoted reads, `PG-IC-09`)

- **Endpoint path** — `GET /v1/settings/ai` returns JSON; bare `GET /settings/ai` returns `200 text/html` (SPA fallback). Matches `docs/worklogs/SG-049_report.md:36`.
- **Container name** — `docker ps` → `storagegenie-backend-1`; port `127.0.0.1:8003->8000/tcp` (`docker-compose.yml:8`). Matches SG-049.
- **Notes ref** — `git ls-remote origin 'refs/notes/storagegenie-coder-reports'` → `3d897a4d1f86f567b3e5b8f694173cf32c07bbe3`. Exists.
- **SG-049 observed state** (`docs/worklogs/SG-049_report.md:17-28`): `provider_id=fake`, key len 67, `consent=false`. Run-2: `provider_id=fake` and key len 67 **unchanged**; `consent` has flipped `false → true` — exactly the enablement the owner performed. Consistent, not contradicted.
- **`provider_id=fake`** is a label, not grounds to stop (packet explicit); the gate is consent + key + `ai_status`, all true.

## 4. `PG-SC-09` — name-the-world (GO here, live leg could still STOP)

The world where this probe reports GO yet the SG-049 live leg still STOPs: the key is **present but invalid at call time** (revoked, wrong scope, insufficient credit), or the **env is rotated between this probe and the leg**. This probe reads presence + length + consent, never validity against the provider. The slice still ships because the live leg **re-runs G0 itself**: it re-checks `consent`, key presence, and `ai_status`, then makes its own admission decision and ledger row. This probe **prices the surprise down** (rules out the "owner forgot the env / didn't restart" failure mode, which run-1 proved was real) but **never removes the gate** — the live leg remains the authority.

## 5. Secret gate (0 hits required; `key_len=` integer line excluded)

Two gates over the three worklogs (`docs/worklogs/SG-055_verify.log` §V5):

- **(a) secret-shaped patterns** (`sk-…`, `Bearer …`, `xox…`, `AIza…`, `PRIVATE KEY` blocks): **0 hits** (grep exit 1, no output).
- **(b) completeness cross-check** over every `[A-Za-z0-9_+/-]{40,}` token: the naive grep matches only benign pure-hex classes (git object IDs `3b41d88…`/`3d897a4…`, sha256 image digest `4f338b…`) **plus one benign literal** — the git ref name `refs/notes/storagegenie-coder-reports-remote` (4 occurrences in `SG-055_verify.log`). After classifying that known ref name out: **`suspicious_non_hex_long_tokens = 0`**. The `key_len=` integer line is excluded by rule. Raw lines quoted in §V5.

No key byte anywhere. `docker compose config` never run; no `.env` read.

## 6. Constraints / hygiene

- **Scope ceiling respected:** diff outside `docs/worklogs` is empty (`git diff --stat -- backend frontend prompts eval tests docker-compose.yml .env` → empty). Only the three worklogs are staged.
- **Reads only:** `curl` loopback + `docker exec`/`inspect` read-only; no other runtime launched (`PG-IC-01`).
- **No migration, no dependency change, no provider call, no push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`, no ignored file staged.**
- **Test scope:** no code change → full sweep WAIVED per `PG-DP-02`; substitute = the four quoted live reads in §1, each pasting raw output (`PG-EV-01`). No vacuous pass: every criterion carries a quoted property, not a skipped gate.

## 7. Budget (actual vs cap, units)

| Leg | Actual | Cap |
|---|---|---|
| V0/V1 recon + premise reads | ~10 s | 120 s (ordinary) |
| V2 four live reads + control | ~5 s | 120 s |
| V3 process-arg read | <1 s | 120 s |
| V5 secret gate | ~2 s | 120 s |
| V6 worklog commit + note add | ~5 s | 120 s |
| V6 notes push + mapped-fetch verify | ~15 s | 300 s |
| **Overall wall-clock** | **~75 s** | 600 s early-close / 900 s overall |

No command was killed; no command approached its bound. Real metered spend: **$0.000000 actual vs $0 bound** (zero calls).

## 8. Receipt note

Work is pushed to `automation` with the worktree clean (`CO-55`). **No** push to `storagegenie-evidence`, **no** `{{RECEIPT_CMD}}`. A note is added on WORK_HEAD under `refs/notes/storagegenie-coder-reports`, pushed, then verified against an explicitly fetched, **mapped** refspec (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-remote`, then `git notes --ref=refs/notes/storagegenie-coder-reports-remote show <WORK_HEAD>`). Per the SG-048/SG-049/SG-053/SG-054 convention, that `show` output is pasted verbatim **in the delivery message** — it cannot live inside this file, which is itself the noted commit. `note=yes`.

## Findings / deviations

- **F-SG055-1 (premise correction, minor):** the packet's context says the owner "restarted the backend"; the observable is consistent (container `StartedAt=2026-09-17T11:45:59Z`, `Up 46 seconds` at probe). The `M31 compose env_file path correction` (`3b41d88`) is the in-history change that makes `SG_CONSENT` visible to the backend — run-1's STOP was structural (env not loaded), not an owner omission. Reported for the rating row.
- **F-SG055-2 (run identity):** this is SG-055 run-2; run-1's STOP-as-SUCCESS and its rating 98 remain valid in history. No SG-049 work is re-done here.
- **Out of scope, flagged:** the live leg's own admission/ledger is the only authority on key validity (`PG-SC-09` §4).

## UNCLEAR

- **FIRST READ:** whether a GO here expects no worklog rewrite of run-1's STOP content. I read "worklog" as per-run current state, so the three files now describe run-2 (GO) while the delivery message notes run-1 remains in history. A ruling is owed if per-run worklogs should instead append.
- **DURING EXECUTION:** none blocking. `provider_id=fake` is unchanged from SG-049 and is explicitly not stop-grounds; I proceeded on consent + key + `ai_status` only.
- **REMAINING:** whether the SG-049 live leg should now be re-dispatched (Architect/owner call), and whether "fake" provider id is intended for the eventual live leg or is itself a remaining provision step.
