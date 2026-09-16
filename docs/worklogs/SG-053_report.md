SG-053 report — production deploy with blessed row counts (opencode, medium)

**Status: GREEN — the D70 mutation ran; the new tree is proven live; blessed rows untouched.**

## Header

- **Work dir:** `/home/andrei/StorageGenie` (as on host).
- **Origin remote:** `git@github.com:Andovol/StorageGenie.git`.
- **BASE REF requested:** `origin/automation`; **resolved commit:** `0bd31efdc2b8985d461822ad672363bd9ba2c9ff`
  (`L3 batch: SG-052 rating 96 + M25 + SG-053 packet (D70)`). `HEAD == origin/automation` at start; worktree
  clean (`## automation...origin/automation` only).
- **WORK_HEAD:** the commit carrying these worklogs (stated in the delivery message; it cannot be stated inside
  a file that is itself part of that commit). The receipt note is attached to it LAST, no commit after.
- **Model / effort (from process arguments, `CO-78`):** effort = `medium` (`opencode run --auto --dir
  /home/andrei/StorageGenie --variant medium <packet>`, pid 750944, started 2026-09-16T17:09:26Z);
  **model = `unknown`** — the packet omits it by policy (CLI default is the model) and no model id is present in
  argv or any model env var. Not read from any identity line.
- **Contract:** 0.27.0 (packet header; `STATE.md:1`). The `.rules-cache/` contract checkout is absent from this
  working tree (same condition SG-051/SG-052 reported), so the `G-L1` fetch/hash check could not be run locally;
  packet header + `STATE.md:1` are the version evidence.

## What happened

1. **G1 (before-state, read-only).** Tree clean and `HEAD == origin/automation == 0bd31ef`. Stack `Up 2 days
   (healthy) [8003]`, running image `sha256:56968d428c4c…` (SG-041), health
   `{"status":"ok","db":"ok","storage":"ok"}`, served asset `/assets/index-khM4mS2k.js`. DB read-only:
   `alembic_version == 20260914_sg035_foundations == head`, no pending migration. **Blessed counts matched
   exactly:** household=1 (Popescu Household seed), user=2, asset=1 (Toothpaste), evidence=1 (upload),
   assertion=3 (all `source_type=user`), audit_event=3 (`evidence.create`, `asset.create`, `asset.accepted`).
   Gate passed → proceed.
2. **G2 (D69+D70 mutation).** `BUILDX_CONFIG=/home/andrei/StorageGenie/.cache docker compose up --build -d`.
   Build TEXT verdict `Image storagegenie-backend Built`; new image `sha256:86f7436d5a61…`. One idempotent
   re-`up -d` → `Container storagegenie-backend-1 Running`, same container Id/StartedAt, `RestartCount=0`
   (no restart loop, `PG-DP-04`).
3. **G3 (proven live by value).** Health exact; served asset now `/assets/index-CuxlcH9v.js` (≠ before);
   wardrobe markers `sg-theme`, `Product results`, `Import assets` found in the served bundle; 8003 loopback-only;
   nginx gate 301 (http) / 401 (https); wrong-expectation check shown failing (`PG-EV-01`).
4. **G4.** Three worklogs; receipt note last; delivery message carries the pasted `show` output.

## Rationale for the blessed-row call

The rebuild is **DB-neutral**: SQLite is bind-mounted (`docker-compose.yml:11 ./data/db:/data/db`), the
`backend/Dockerfile` CMD is a bare `uvicorn` with no entrypoint migrate/seed, and the app has no lifespan write
(SG-052 F-SG052-3, re-confirmed). Post-deploy read-only re-count was identical to pre-deploy. So the blessed
rows were never at risk from the restart; the gate existed to catch rogue state, and the measured set is the
owner's own directed live pass (D70), now stated explicitly.

## Guards invoked — disposition

| Guard | Disposition |
|---|---|
| `PG-EV-01` gate-seen-failing | MET. In the same command block, the deliberate wrong expectation (old hash `index-khM4mS2k.js` still served) FAILED as required (`exit 1`), raw in `SG-053_verify.log`. |
| `PG-EV-02` artifact-exists | MET. The artifacts checked are the SERVED responses (index bytes, `/assets/index-CuxlcH9v.js` bundle, health JSON) — never an exit code. |
| `PG-EV-05` property-not-command | MET. Values stated: health JSON, asset hash before/after, marker strings, listener addresses, count table. |
| `PG-EV-08` before-observable | MET. Before state (tree, stack, listeners, health, asset hash, image id, DB counts + alembic) captured raw and committed. |
| `PG-EV-09` both-runs-committed | MET. Before and after captures both raw in `SG-053_verify.log` (asset-hash pair `index-khM4mS2k.js` → `index-CuxlcH9v.js`). |
| `PG-SC-10` no-ignored-commit | MET. Only `docs/worklogs/SG-053*` added; `.cache/`, `data/`, `.env` remain ignored and unstaged. |
| `PG-IC-01` cross-product | MET. G1 reads, G2 stack commands, G3 served observables, G4 worklogs. No new exclusion issued. |
| `PG-IC-08` expectation-bounds | MET (both directions). Exact equality on all six tables; an under- and an over-count would each have stopped the slice. |
| `PG-IC-09` premises-live | MET. Every packet premise re-checked live; no-migration premise confirmed true; two environment findings raised (F-SG053-1/2). |
| `PG-PR-01` capability-model | MET. Coder ran only the compose build/up/re-up authority (D69+D70); no role escalation; no dispatch verb run. |
| `PG-PR-03` denied-is-stop | MET. No privileged op was attempted or denied mid-slice; the pre-slice `sudo -n` probe is reported, not routed around. |
| `PG-PR-04` how-code-goes-live | MET. Code goes live exactly by image rebuild + container recreate via the compose stack; no other path. |
| `PG-PR-06` runtime-vs-budget | MET. Per-leg timings below; well inside every bound. |
| `PG-PR-10` which-db-and-grant | MET. Local SQLite `sqlite:////data/db/storagegenie.db`, read-only probes only; no grant required, none used. |
| `PG-DP-01` delivery-by-delivery-path | MET. Delivery is the compose stack on the host (image + container), then git worklogs. |
| `PG-DP-04` two-consecutive-runs | MET (this slice's within-slice form). Second `up -d` produced no recreate/restart. (The cross-slice run-2 green remains for the Architect to track.) |

## Findings

- **F-SG053-1 (foreign listener, pre-existing, out of scope).** The G1 `ss` probe showed a FOREIGN
  `0.0.0.0:8000` uvicorn (404 at `/`); by the G3 probe the same port read `127.0.0.1:8000`. It is not ours —
  our compose publishes `127.0.0.1:8003:8000` only (`docker-compose.yml:8`) and our listener is
  `rootlesskit pid=3814163`. Shared-VPS foreign service; no action taken, reported so the Architect can see it.
- **F-SG053-2 (external hostname does not resolve on-box).** `getent hosts storagegenie.dynv6.net` → rc=2;
  `curl` → `(6) Could not resolve host`. The packet's literal `curl https://storagegenie.dynv6.net/v1/health`
  step is therefore not runnable from inside the host as written. The equivalent proof against the **same nginx
  vhost** was taken via the loopback address with `Host: storagegenie.dynv6.net`: http → `301` with
  `Location: https://storagegenie.dynv6.net/v1/health`; https → `401` with
  `www-authenticate: Basic realm="StorageGenie Restricted"`. nginx was not touched.
- **F-SG053-3 (G1 instruction "expect `127.0.0.1:8003` only").** Taken literally this is false on this shared
  VPS (dozens of unrelated listeners). It is true in the intended sense: the only listener this project owns is
  `127.0.0.1:8003`. Stated so the phrase is not read as a failed gate.
- **F-SG053-4 (no-migration premise).** Confirmed true: version-file chain ends at
  `20260914_sg035_foundations`, which equals the DB's `alembic_version`. No pending migration.

## Live-state ledger

- **Image id old → new:** `sha256:56968d428c4cf446a99b82481a0b6ce9e4c040c32e1094729fc6e150374d3e05`
  (SG-041, created 2026-09-14T13:43:40Z) → `sha256:86f7436d5a61ae35cf58ed470de17b0ae196f710e466d3d050099565601d9d92`
  (built 2026-09-16T17:10:57Z). Container `244465492ac0`, `RestartCount=0`, memory 70.63MiB / 7.688GiB.
- **DB writes:** **zero** — read-only `file:…?mode=ro` probes only; counts and alembic head identical before/after.
- **Live spend:** `$0` metered; AI OFF (`SG_CONSENT=false` not exercised), no provider calls.
- **Network:** registry pulls for the build (node/python bases, apt, pip, npm) + loopback app API checks. No external calls.
- **Product diff:** none (`git diff --stat` empty). **Ignored files staged:** none. **`storagegenie-evidence` push:** none.

## Budget — actual vs bound (per leg)

| Leg | Bound | Actual | Under |
|---|---|---|---|
| G1 pre-state + blessed counts | 120 s | ~68 s | yes |
| migrate-check (read-only alembic + chain) | 300 s | ~3 s | yes |
| G2 build + up | 1800 s | ~16 s (build+up) + ~5 s (re-up) | yes |
| G3 live proof + gate + gate-failure | 120 s | ~30 s | yes |
| G4 worklog + commit + receipt | (overall) | ~180 s | yes |
| Early-close | 2100 s | not reached | yes |
| Overall | 2700 s | ~360 s | yes |

## Acceptance criteria — honest status

- Starting tree clean / `HEAD == origin/automation` (audited tip): **PASS**.
- Blessed counts compared exactly (equal → proceed); no-migration-need proven; pre-state health + hash + listeners quoted: **PASS**.
- Post-change health exact JSON; new asset hash ≠ pre-state; markers quoted from served bytes; loopback-only;
  gate 301/401; second `up -d` no restart; memory sample: **PASS**.
- Gate seen failing (wrong expectation); artifact is the served response; properties stated as values: **PASS**.
- No product-file diff; no DB write; no ignored file staged; no `storagegenie-evidence` push; **no vacuous pass**:
  **PASS**. The wrong-expectation check was a real, executed check that really failed; the before/after pair is a
  real hash change; the count comparison was exact six-table equality, not an empty set.

## Receipt (note on the coder-reports notes ref)

Worklogs committed and pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`; no
`{{RECEIPT_CMD}}` (this packet's M20-corrected block). The note is attached to WORK_HEAD **LAST** (no commit
after it, per the established flow) with its first line carrying both `Dispatch-ID:` and `Report:` (`CO-97`);
the notes ref is pushed explicitly to `origin`; the refspec is fetched explicitly (`<ref>:<ref>`, M21 — a bare
fetch never updates a notes ref); and the executed
`git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` output is pasted verbatim in the
delivery message (it cannot live inside this file, which is itself part of the noted commit). If that `show`
output is absent from the delivery, this step was not executed and must be called out loudly. Final line:
`note=yes`.

## (d) UNCLEAR

- **FIRST READ:** whether "expect `127.0.0.1:8003` only" meant the whole host listener table or only this
  project's port. The full table has dozens of unrelated listeners on this shared VPS; I read it as
  project-scoped (8003 loopback-only) and stated the literal reading loudly (F-SG053-3) rather than bending the
  observation.
- **DURING EXECUTION:** whether a foreign `0.0.0.0:8000` seen at the G1 probe should itself stop the slice
  (the packet's G3 wording says no `0.0.0.0` listener for 8000). I judged it out-of-scope foreign state: it is
  not bound by this compose file, it had already moved to `127.0.0.1:8000` by the after-probe, and touching it
  would exceed the write authority. Reported as F-SG053-1 for the Architect.
- **REMAINING:** (1) the cross-slice `PG-DP-04` second **consecutive** green (a future independent run) is still
  owed; (2) F-SG053-2 — the public hostname does not resolve from inside the host, so every packet's on-box
  `curl https://storagegenie.dynv6.net/...` step needs either an external vantage point or the loopback
  `Host:`-header form written into the packet; (3) the `.rules-cache/` contract checkout is absent from this
  tree, so the `G-L1` fetch/hash version check could not be run locally.
