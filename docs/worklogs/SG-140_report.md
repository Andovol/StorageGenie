SG-140 — Close-out deploy rider: serve everything landed (rebuild + one recreate + verify)

**BLOCKED — the rebuild cannot produce a servable image at BASE without a product-file edit, which this rider forbids.**

Settings (CO-78, from process arguments / provider metadata — never the identity line): coder `opencode`; **model `opencode-go/deepseek-v4.1-flash`** and **effort `high`** from process argv `/proc/140779/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high`. **Spend: real $0.000000 USD** (zero metered calls).
Work dir `/home/andrei/StorageGenie`; origin `git@github.com:Andovol/StorageGenie.git`.
**BASE** (`origin/automation` requested; resolved): `133c25205491e109b72310b04fa49b4a1f7bc6f2` · **WORK_HEAD:** `649416469fb2fddb63e95fec4890313cbb127e3c` (the BLOCKED worklogs commit; receipt-note target; this report lives in the following worklog commit, so it does not carry its own hash — CO-55b).
Gates: **DATABASE** read-only (`alembic current` + mode=ro row counts; no write) · **Restart** none (zero recreates) · **Deploy** none (build failed first). Role guard held (Coder only; no dispatch verb, no unit started/polled).
Contract echo `0.40.0` verbatim; source path `/home/andrei/storagegenie-contract/VERSION` (host link echoed by SG-138).

## G0 — nothing to serve but the queue (reads only): PASS

- Empty product diff vs BASE at start — **quoted empty** (`git diff --stat/--name-only origin/automation...HEAD` → no output), worktree clean (`git status --porcelain` empty).
- `alembic current` head **quoted**: `20260924_sg114_relation (head)` — **equals the packet's expectation**; `backend/alembic/versions/` newest file is `20260924_sg114_relation.py`, so no migration landed since the last image. No upgrade run.
- Pre-rider baseline: image `sha256:ca29a3dc9a07` (created 2026-09-25, the SG-132-era image — SG-135..139 are indeed **unserved**); container `40a117eaff0c…` Up 2 days (healthy); health exact-shape ×2 = `{"status":"ok","db":"ok","storage":"ok"}` HTTP 200; served entry references `/assets/index-DXSEg7CT.js` (**sha256 `f435cbc1…`**, 318414 bytes).
  - **Finding (premise vs tree):** the packet presupposes a *served frontend* as a running service. Only `storagegenie-backend-1` runs. The production UI is **baked into the backend image** (`backend/Dockerfile:20`, `COPY --from=frontend-build /ui/dist ./static`; the compose `frontend` service is `profiles: ["dev"]` and its container `1aabf2905704` has been Exited 2 weeks). A single backend recreate therefore ships both API and UI — the packet's single-recreate authorisation is sufficient.
- Gate baseline quoted: `http:80 Host=storagegenie.dynv6.net → 301 https://storagegenie.dynv6.net/`; `https:443 → 401`.

## G1 — rebuild + ONE recreate + verify: **STOPPED at rebuild** (no recreate)

- **Rebuild FAILED** (300s bound; 8s actual): `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` → stage `frontend-build 6/6 RUN npm run build` (`tsc && vite build`) exit code 2. Image **unchanged** (`ca29a3dc9a07`).
- **Exactly ONE recreate was NOT performed** — and correctly so: the packet's order is rebuild THEN recreate (`PG-PR-04`); recreating the stale image would serve none of the landed queue and would burn the single authorised restart (`PG-PR-10`) for nothing.
- Post-failure safety (no production mutation): container id **unchanged** `40a117eaff0c…`, `RestartCount=0`, health ×2 still `{"status":"ok","db":"ok","storage":"ok"}` 200, worktree clean, `alembic current` still `20260924_sg114_relation (head)`, read-only counts unchanged.

**Root cause (product defect, not environment).** Commit `0cd1c35` (google-labs-jules[bot], 2026-09-28T13:53:55Z) *"test: add unit tests for WebAlternates component"*, merged via `973009c "Merge PR #18 into automation"` — one of **SG-135's 11 merges**. It added `frontend/src/components/WebAlternates.test.tsx` with literals at lines 59/74/79 omitting required `WebAlternate` props. `frontend/src/api/types.ts:144-150` types `source_type`/`source_url`/`retrieved_at` as **required** (`string | null`), `frontend/tsconfig.json` `include: ["src"]` typechecks `*.test.tsx`, and `package.json` build is `tsc && vite build`. Hence the served frontend build was broken by the landed queue and was never caught because no slice rebuilt after the merge. The three TS2739 errors are quoted verbatim in `SG-140_verify.log`.

**Why STOP and not fix.** The fix is a one-line product-file edit (`WebAlternates.test.tsx` or the type), but this rider's scope ceiling is explicit: *any product-file write is a STOP*. Routing around it (`--noEmitOnError`, editing the Dockerfile/tsconfig, hand-building a non-reproducible image) is out of scope. The packet's premise *"serve everything landed"* is falsified by the queue itself.

## G2 — worklog and report

`docs/worklogs/SG-140.log`, `SG-140_report.md`, `SG-140_verify.log` (G0 proofs, image/container ids, health ×2 baseline + post-fail, gate, alembic before==after unchanged, read-only counts, bundle hash, smoke, full build error). First token `SG-140`. No secret in any committed artifact (`CO-100`).

### Actual-versus-budget per goal (units)
| Goal | Budget | Actual | Note |
|---|---|---|---|
| G0 reads | ≤120s ordinary | ~40s | diff/head/ids/health/bundle/gate/counts |
| G1 rebuild | ≤300s | **8s** (failed) | `npm run build` exit 2 |
| G1 recreate | ≤300s | **0s** | not performed (correctly withheld) |
| G2 worklogs | ≤120s ordinary | ~60s | 3 files |
| Overall | ≤2400s | well under | no command killed, no hang |
| Spend | $0.000000 USD | **$0.000000 USD** | zero metered calls |

### Official guards (reviewer copies to the rating row)
`PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-PR-10` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09`.

### Receipt note (M20-corrected block)
```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   133c252..6494164  automation -> automation
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-140 | Report: docs/worklogs/SG-140_report.md | Work-HEAD: 649416469fb2fddb63e95fec4890313cbb127e3c" \
    649416469fb2fddb63e95fec4890313cbb127e3c
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   d31d645..a39494b  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg140-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg140-fetched
$ git notes --ref=refs/notes/sg140-fetched show 649416469fb2fddb63e95fec4890313cbb127e3c
Dispatch-ID: SG-140 | Report: docs/worklogs/SG-140_report.md | Work-HEAD: 649416469fb2fddb63e95fec4890313cbb127e3c
```
The final-tip dual-annotation (note-anchor inoculation, SG-092 precedent) and its fetched `show` output are pasted in `SG-140.log` (`note=yes`).

### No vacuous pass — stated loudly
- No recreate happened, so no container-id change, health ×6, moved bundle hash, or post-recreate smoke can be reported. Those criteria are **UNMET, not passed** (a recreate counted by `RestartCount` would evidence nothing anyway, M42).
- The only "criterion" that could pass vacuously here is the empty product diff; it is quoted empty with both `--stat` and `--name-only`, and the worktree remained clean after the failed build.
- The blocker itself is proven by a **reproduced non-zero build exit with quoted TS2739 compiler output**, not by assertion.

### Issues / disagreements (including outside this slice's scope)
- **F-SG140-1 (blocking):** SG-135 shipped a frontend test that breaks the production typecheck (`tsc && vite build`). A one-line product fix is required before any close-out deploy can succeed.
- **F-SG140-2:** the served UI lives only inside the backend image; the compose `frontend` service is a dev-profile leftover (exited 2 weeks). Worth reconciling with `AGENTS.md`/`VPS.md` language that implies a served frontend service.
- **F-SG140-3:** no read-only API exposes provider-call row counts, so G1's "live counts" were taken via a direct `mode=ro` SQLite SELECT. The packet's DATABASE line says "none read or written beyond `alembic current`"; I judged a read-only count (explicitly demanded by G1, and "reads include container exec probes") the lesser conflict and disclosed it. A G1 count criterion and a no-DB-read constraint cannot both hold strictly.

### UNCLEAR
- **FIRST READ:** Whether the packet's "served JS bundle hash (frontend changed since last image — EXPECT the post bundle to differ)" accounted for the fact that the **build itself fails** at BASE; the claim that the queue is merely "unserved" overlooked that the queue is also **unbuildable**.
- **DURING EXECUTION:** How to reconcile G1's mandatory "live counts delta == 0" with the DATABASE line's "none read ... beyond `alembic current`". Chose a read-only count and disclosed the conflict (F-SG140-3).
- **REMAINING:** Whether the owner wants the Coder to take a controlled, explicitly-authorised product fix (the one-line `WebAlternates.test.tsx`/type correction) as a separate slice, or whether SG-135 is to be amended/rated down, before the close-out deploy is re-dispatched.
