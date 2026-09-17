# SG-055 — enablement probe: key + consent + restart check, read-only

**Dispatch-ID:** SG-055 · **Coder:** opencode · **Effort:** `low` (read from process args: `/proc/1375168: opencode run --auto --dir /home/andrei/StorageGenie --variant low …`) · **Model:** `unknown` (no model id on argv; the CLI default IS the model and is omitted per policy — never read from an identity line).
**Contract:** 0.27.0 (recorded == published payload == SG-049 receipt echo). **Spend:** **$0.000000** metered (zero provider calls).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** none. No DB touched, not even arithmetically. All checks are reads of the running service or the container runtime.

- **BASE REF requested:** `origin/automation`; **resolved commit:** `273321c0388e1a6507b6af149007759d2a84d514` (`SG-055 packet (enablement probe, read-only, D76 chain)`).
- **WORK_HEAD:** the commit carrying these three worklogs — stated in the slice delivery report (it cannot be stated inside a file that is itself part of that commit, same as SG-048/SG-049/SG-053/SG-054). The receipt note is attached to it LAST; no commit follows.
- **Slice wall-clock:** start `2026-09-17T11:35:06Z`; close `2026-09-17T11:35:34Z` (~28 s vs 900 s overall / 600 s early-close).

## 1. G1 — the four establishments, read-only, QUOTED FIRST (both outcomes handled)

**(a) served consent JSON — `GET /v1/settings/ai` (loopback 8003):**

```
$ curl -s --max-time 10 -w '\nHTTP=%{http_code}\n' http://localhost:8003/v1/settings/ai
{"provider_id":"fake","model_id":"deepseek-v4-flash-vision-exp","allowed_model_ids":["deepseek-v4-flash-vision-exp"],"consent":false,"per_job_cap":null,"monthly_cap":null,"prompt_category":"food"}
HTTP=200
```

Premise re-verified: bare `/settings/ai` serves the SPA HTML, never JSON; the `/v1` prefix is required (`config.py:16`). Both probed (verify log [V7]).

**(b) provider key EXISTS — existence-only from inside the backend container (boolean + length; ZERO key bytes):**

```
$ docker exec storagegenie-backend-1 python -c "from app.config import settings; k=getattr(settings,'opencode_api_key',None); print('opencode_api_key_present=', bool(k)); print('key_len=', len(k) if k else 0)"
opencode_api_key_present= True
key_len= 67
```

No key byte was printed, logged, quoted, or committed; `docker compose config` was never run (`PG-SC-05`).

**(c) `ai_status()`-equivalent — configured provider enabled?:**

```
$ docker exec storagegenie-backend-1 python -c "from app.services.providers.reader import ai_status; print('ai_status=', ai_status())"
ai_status= (False, 'consent_disabled')
```

**(d) backend container post-restart — `StartedAt` + image ID (read-only `docker inspect`):**

```
$ docker inspect -f '{{.Name}} StartedAt={{.State.StartedAt}} Status={{.State.Status}} Image={{.Config.Image}} ImageID={{.Image}}' storagegenie-backend-1
/storagegenie-backend-1 StartedAt=2026-09-16T19:55:23.663139387Z Status=running Image=storagegenie-backend ImageID=sha256:4f338b356945f9a8f960ecd3f50a3890a7c2b6d536ea4312c4f66e25e2f78f5e
```

**Load-bearing reasoning:** live settings come from env at process start (SG-031: a restart drops overrides), so `consent=true` served live would PROVE the restart. Here `consent=false` is served live, and the running process environment carries **no `SG_CONSENT` variable at all**:

```
$ docker exec storagegenie-backend-1 sh -c 'printenv | grep -i consent || echo "NO_CONSENT_ENV_VAR"'
NO_CONSENT_ENV_VAR
```

`consent=false` therefore means STOP regardless of `StartedAt`.

**Outcome: STOP-as-SUCCESS.** Establishments (a) and (c) are FALSE. The key exists (b) but consent is not present in the live process, so the owner's asserted enablement pre-step (`.env` key + `SG_CONSENT=true` + restart) is not visible to the running backend. No provider call was made and zero bytes touched a metered endpoint. **Stopping here is the designed successful outcome for a STOP gate, not a failure.**

## 2. G1 both-outcome handling and `PG-SC-09` named world

- GO (all of a+b+c true) → verdict GO for the SG-049 live leg. Not reached.
- STOP (any false) → this report: STOP-as-SUCCESS via the `BLOCKED:` commit path.
- **`PG-SC-09` named world:** the probe could report GO while the live leg still STOPs if the key is present at probe time but rejected at call time (invalid/expired credential), or if the env is rotated between probe and leg (restart back to `consent=false`). This slice still ships because the SG-049 live leg re-runs its own G0 gate itself; this probe only prices the surprise down — it never removes the gate.
- **Not grounds to stop** (per packet): the `provider_id=fake` label value alone; the key length differing from 67 (here it matches at 67); the frontend container being exited (`storagegenie-frontend-1 Exited (0) 5 days ago` — the backend serves the SPA); the runner's `report_missing` classifier (desk-side, Launcher#42). Receipts are verified by mapped notes-ref fetch, never by the status verb.

## 3. Starting tree

```
$ git status --porcelain          # (empty)
$ git branch --show-current       # automation
$ git rev-parse HEAD ; git rev-parse origin/automation
273321c0388e1a6507b6af149007759d2a84d514
273321c0388e1a6507b6af149007759d2a84d514
```

Clean; dirt would have been a STOP. Both refs identical at start.

## 4. Premises re-verified (`PG-IC-09`)

| Premise (from `docs/worklogs/SG-049_report.md:17-28`) | Observed | Status |
|---|---|---|
| JSON read is `GET /v1/settings/ai` (bare serves SPA) | `/v1/...` JSON 200; bare HTML 200 | confirmed |
| Key probed from inside `storagegenie-backend-1` (bool+len only) | `True`, `67` | confirmed |
| `ai_status()` read via `reader.ai_status` | `(False, 'consent_disabled')` | confirmed |
| Health is `GET /v1/health` | `{"status":"ok","db":"ok","storage":"ok"}` on 8003 | confirmed |
| SG-049 observed `provider_id=fake`, len 67, `consent=false` | identical now | confirmed |

**Deviation found:** the packet/`{{HEALTH_CMD}}` names port 8000; the running map is `127.0.0.1:8003->8000/tcp` and 8000 answers `Not Found`. Reported, not bent.

## 5. Acceptance criteria

- G1 quoted read-only first with both outcomes: yes; verdict STOP-as-SUCCESS via `BLOCKED:` commit.
- Starting tree quoted (clean): yes. SG-049 premises re-verified in-slice with quoted reads: yes.
- Four properties as PROPERTIES (`PG-EV-02`,`PG-EV-05`): served consent JSON, key boolean+length (zero bytes), `ai_status()` tuple, `StartedAt`+image — no bare exit code stands alone.
- Secret gate (`docs/worklogs/SG-055_verify.log` [V8]): gate (a) secret-shaped patterns → 0 hits; gate (b) completeness cross-check over every ≥40-char token → `suspicious_non_hex_long_tokens = 0` (a naive long-token grep matches benign git/sha/notes hex, so those classes are classified out and shown, not silently dropped). `docker compose config` never run; zero provider calls; no migration; nothing pushed to `storagegenie-evidence`; no ignored file staged; no vacuous pass — the failing gate emitted its raw output (`PG-EV-01`).
- Cross-product (`PG-IC-01`): no blanket exclusion issued. G1's STOP shares no condition with any remediation step — stops win (`PG-IC-03`).
- Test scope: no code changes, no suite run; full sweep explicitly WAIVED (`PG-DP-02`), substitute = the four quoted live reads in §1.

## 6. Receipt

- Work pushed to `automation`; no push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.
- Note added on `WORK_HEAD` (120s bound), notes ref pushed (300s bound), then fetched into a
  mapped local name and listed/grep'd; the executed `git notes --ref=… show <WORK_HEAD>`
  output is pasted verbatim in the slice delivery report (the note cannot be committed into
  the file that defines its own WORK_HEAD). Final delivery line `note=yes`.

## 7. UNCLEAR

- **FIRST READ:** the asserted `SG_CONSENT=true` + restart is not visible in the running
  backend (`consent=false`; no `SG_CONSENT` in the process env).
- **DURING EXECUTION:** canonical loopback port is 8003, not the packet's/`{{HEALTH_CMD}}`'s
  8000; 8000 returns `Not Found`. Apparent stale binding.
- **REMAINING:** whether the host `.env` actually carries `SG_CONSENT=true` (out of scope to
  read) and, if so, why the process did not load it — owner reconciliation owed.
