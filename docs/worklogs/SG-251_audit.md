# SG-251 audit — SG-250 served live; the served bytes are exactly its thirteen runtime files; rated 97

**Receipt verified:** the notes ref `refs/notes/storagegenie-coder-reports` was fetched explicitly (`87f9200..e8dde49`) and the slice's receipt transcript is committed at `docs/worklogs/SG-251_receipt.log`. Trigger returned `result=done id=SG-251 exit=0`. The commit carrying the report is `b0c2272`, the receipt commit `b58846f`, both on `origin/automation`; the report's last line is `Verification: PASS`. Base resolved: `21b79d6` (the commit the slice started from).

**Diff verified (base `21b79d6` → `b58846f`):** eleven `docs/worklogs/SG-251*` files only — **zero** product, config, schema, migration, dependency or test bytes. Terminal class **NO PRODUCT CHANGE**; one image build and one backend recreate, as the standing rider does. **$0.000000**, zero provider calls, no key value read, printed, hashed, stored or transmitted, no `.env` file opened.

## The serve

- **G0** — the lane socket `/run/dispatch-storagegenie-SG-251/docker.sock` was exported and `docker version` printed a **Server** block (29.6.2, API 1.55, rc=0) before any docker mutation. One earlier `docker version` on the default endpoint failed with `permission denied` and changed nothing (I1, disclosed).
- **G1** — one build (rc=0, 18 s of 600 s) and one recreate (rc=0, 1 s of 120 s). New container **`a831fbd0f8d2…c19c2c1`**, image **`sha256:e8c7373577f9…543d4ec3`**, `Cmd ["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, RestartCount 0, running/healthy. **No migration** — head `20261023_sg233_reminder` before and after. Health 200 `{"status":"ok","db":"ok","storage":"ok"}` at the start, six times after the recreate and at the end.
- **The runtime diff is exactly SG-250's thirteen runtime files** (the 14th, `backend/eval/run.py`, is not runtime): the set diff against SG-250's commit is `extra=0, missing=0`, and the post-build served tree equals the worktree (100/100 Python files, `diff` rc=0).
- **The frontend bundle is byte-identical** before and after — `index.html` `cec37cf5…` 944 B, `index-C07VbG0m.css` `c3b58cda…` 4535 B, `index-CWp6nYu6.js` `fe7dff6e…` 326217 B, each `cmp` rc=0.
- **All 29 table counts identical** before and after (32 census lines, `diff` rc=0), including **`provider_call=39`** — the table this slice's change writes to. The SQLite main-file sha moved `acf11596…` → `e4107437…` at the same size (765952 B): the old container's stop checkpointed committed WAL pages, the same behaviour SG-239 and SG-241 measured. No row changed.

## The absence proofs, with their control (the load-bearing part)

From the **served image's own files** (the tree extracted with `docker create` + `docker cp`, nothing executed): `estimate_call_cost|estimate_cost` absent from the served `providers/opencode_go.py`; `cost_budget` absent from the served `providers/router.py`, whose `execute` signature carries no cost argument; `_estimate_call|_recorded_spend` absent from the served `providers/reader.py`; `sg_per_job_cap|sg_monthly_cap` absent from the served `config.py` — every grep rc=1. **The control is the pre-SG-250 blob** (`d0a87c6^`), where all five symbols are present at their old lines (`estimate_call_cost` 151, the caps 48/49, `cost_budget` 35, `_estimate_call`/`_recorded_spend` 233/270): a check that could have found nothing, proved against something that has everything.

**The cost line is live in the served bytes** — `_log_call` emits `logger.info("provider call: provider=%s model=%s operation=%s status=%s cost=%.8f input_tokens=%d output_tokens=%d latency_ms=%s", …)` (`opencode_go.py:165-168`), and `compute_cost(usage)` prices the response's **real** token counts after the call (`:140-151`), stored as `cost = compute_cost(usage)` in the `ProviderResult` (`:293-300`). The startup log carries no configuration error and no traceback; the only "error" match is the daily pass line's own `errors=0` (I8, recorded).

## G4 — the answer to the open question

**The served registry holds `provider_ids=fake,opencode-go` (count 2), `effective_provider_id=opencode-go`, `ai_status_reason=enabled`** — so **the served app is in the real-provider case**: the next authorised real photo read will emit the new cost line. The ids were read by executing the served image's own `provider_registry()` inside the running container under the container's own environment; the helper printed **names and booleans only**, and `/app/.env` is absent from the image, so no `.env` file was opened.

**And the honest limit is kept:** the cost line's live appearance is **NOT claimed** — no provider call was made and none was simulated, and the line appears only when a real `opencode-go` call runs the `_log_call` path. The log correctly shows no cost line until then.

## The findings (eleven, all disclosed)

**I1** the first `docker version` ran before the socket export (denied, no effect). **I2** the pre-serve image `97ced17c…` **disappeared from the daemon inside the build/recreate window** and the cause is **not established**; the pre-state evidence was captured before the build, and the absence control was taken from the pre-SG-250 git blob instead. **I3** the packet's "fourteen product files" is 13 runtime plus one non-runtime file — the packet's own G2 list said so; set equality proved. **I4** the repo `AGENTS.md` labels rule-set `0.52.0` while the live contract is `0.53.0` — the slice followed the live contract and echoed it; correcting the label is outside its ceiling. **I5** two defects in its own first pre-state block (a 2181-file diff where the served tree is 100 files; a `docker exec` without `-i` that printed nothing) — both corrected and recorded, no stale value used. **I6** the build was **not** fully cache-satisfied (`COPY backend/` and the editable install re-ran) and the image was checked anyway. **I7** the WAL-checkpoint sha move. **I8** the error scan's single false positive. **I9** G4's method stated exactly. **I10** `ai_status` returns `enabled`. **I11** the remote `automation` branch advanced during the slice (`21b79d6` → `7ba4347`, a STATE.md-only commit); the first push was rejected non-fast-forward, and the still-unpublished docs-only commit was rebased onto `7ba4347` and pushed — the product tree verified is still `21b79d6`'s and is unchanged by that commit.

**No flag:** no safety breach (one build, one recreate, **zero** rows written, zero migrations, zero provider calls, $0, no key read) and no trust breach (eleven findings, one of them an unexplained cause, stated as unexplained rather than smoothed).

**Holistic: 97/100, no flag.** The rider did what a rider must: serve exactly once, prove the served bytes are the audited slice's bytes **with a control that could have failed**, answer the open question about the served registry, and refuse to claim the observable it did not produce. `deduction_attribution`: **mixed** — packet (it wrote "fourteen product files" where the runtime set is thirteen, and its G2 list already said so) and environment (the pre-serve image vanished from the daemon inside the build window, cause not established).

### Dispositions

| Item | Status |
|---|---|
| SG-250 served live, with its cost behaviour | **RESOLVED** — container `a831fbd0…`, image `e8c73735…`, healthy, no migration, 29 counts identical including `provider_call=39` |
| The served bytes are SG-250's and nothing else | **RESOLVED** — 13 runtime files, set diff extra=0/missing=0, served tree = worktree, frontend byte-identical |
| The prediction and the caps are gone from the **served** code | **RESOLVED** — five absences proved with a control that still contains them |
| The served app's provider case (the open question from SG-250's audit) | **RESOLVED** — `provider_ids=fake,opencode-go`, effective provider `opencode-go`, `ai_status=enabled`: the next authorised real call emits the cost line |
| The cost line's live appearance | **NOT CLAIMED** — it needs a real provider call; no call was made and none was simulated |
| The repo's rule-set label (0.52.0) vs the live contract (0.53.0) | **OPEN** — the adoption decision is the owner's (D-502); the named delta is in the close report |
| The pre-serve image's disappearance from the daemon | **OPEN, cause not established** — recorded, not smoothed; the evidence was captured before the build |
| SG-251 receipt + rating row | **RESOLVED** — receipt transcript committed; this row and this audit committed this turn |
