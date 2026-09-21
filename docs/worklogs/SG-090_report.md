# SG-090 — SG-085 failure probe: read-only diagnosis of the 129s exit-1 with zero commits

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `9a90c5bc2cbba49b681a58a096749c894715d017` (`SG-090 packet: read-only probe of SG-085 129s exit-1 (D107 L3, D104 pattern)`)
**WORK_HEAD:** `4260c5faa16c40daee46114f0b66cbbca970bb96` (docs commit carrying this report; the post-note, docs-only receipt commit is HEAD after it).
**Contract:** recorded `0.28.2` == published `0.28.2`; source `/home/andrei/storagegenie-contract/VERSION` (host checkout state).
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`; read from provider metadata — SG-090 dispatch log header `> build · deepseek-v4.1-flash`; **argv carries no `--model`**, model is the CLI default) · effort `medium` (process argv `/proc/560765/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`).
**Spend (real $):** `$0.000000` actual — zero metered provider calls. Containment per `PG-PR-04`: nothing live exists to contain; no pipeline, no unit, no provider was started by this slice.
**Autonomy:** `L2` slice (1 retry available; not used).
**Guards:** `PG-EV-02` · `PG-EV-05` · `PG-SC-05` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NOTHING live).

D107 read-only probe (D104 / SG-084 precedent). Role guard honoured: the Coder ran **no dispatch verb for any ID**,
started/polled/retried **no unit**, made no launch change, no `--force`, no re-trigger. Root of SG-085's failure is
established below; verdict is **GO** for re-firing `SG-085 --force`.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on 2026-09-21 host | Verdict |
|---|---|---|
| `SG-085` ran ~129s, committed NOTHING, tree clean | `elapsed=129s`, `P1_moved=FAIL count=0`, `files: count=0`, `P6_dirty=PASS dirty=no`, `START==END==ef029d0` | **confirmed** |
| "unit failed with `result=no_receipt exit=1`" | `P5_receipt=FAIL`; `P3_note=FAIL note=no`; `negative_receipt=published` | **confirmed (positive receipt absent)** |
| `docs/packets/SG-085-*.md` resolves to exactly one file | `ls -1 docs/packets/SG-085-*.md \| wc -l` → `1` (`SG-085-eval-hardening.md`, 11.4K) | **confirmed** |
| `ef029d0` reachable in host history | `git merge-base --is-ancestor ef029d0 HEAD` → true ("ef029d0 IS ancestor of HEAD") | **confirmed** |
| OpenCode CLI = `1.18.31` (AGENTS table, `VPS.md` re-measured 2026-09-17) | `opencode --version` → `1.17.19` (exit 0; binary `/usr/local/bin/opencode`, mtime Jul 13 19:06) | **difference — F1** |
| SG-085 died "before any work" (SG-084-style framing not claimed here) | SG-085 lane log shows real recon + baseline runs (pytest `2 failed, 356 passed`, `eval/run.py` baseline, ruff, mypy) before the upstream error | **difference — F2 (work happened, still zero commits)** |

## G0 — packet + base resolution (could the slice run at all?)

- Packet exactly-one, raw:
  ```
  $ ls -1 docs/packets/SG-085-*.md | wc -l
  1
  docs/packets/SG-085-eval-hardening.md  11.4K
  ```
- Dispatch-params head (verbatim, first lines of `docs/packets/SG-085-eval-hardening.md`):
  ```
  # SG-085 — eval runner outgrows its single-corpus hardwire: manifest selector + frozen baselines (opencode, medium)

  **Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
  coder: opencode
  effort: medium
  ```
- Reachability (ancestor form, never `HEAD ==`, `PG-IC-07`):
  ```
  $ git merge-base --is-ancestor ef029d0 HEAD && echo "ef029d0 IS ancestor of HEAD" || echo "ef029d0 NOT ancestor of HEAD"
  ef029d0 IS ancestor of HEAD
  $ git rev-parse HEAD
  9a90c5bc2cbba49b681a58a096749c894715d017
  ```
  `ef029d0` is the parent of the SG-090 packet commit and is an ancestor of the checked-out HEAD. The slice COULD run.

## G1 — unit journal (what killed it?)

Bound used: 120s ordinary; the journal is short (56 lines total) and returned well within bound — no kill.

Raw journal, full (56 lines; `journalctl --no-pager -u dispatch-storagegenie@SG-085.service`):
```
Sep 21 16:46:34 ubuntu run-coder[556291]: contract_sync=refresh version=0.28.2
Sep 21 16:48:42 ubuntu run-coder[556291]: DISPATCH_RESULT id=SG-085 coder=opencode exit=1 head=ef029d0ec1e0f8eae60cf85e464469612a2478c6 note=no moved=no rewrite=no dirty=no elapsed=129s budget=2100s
Sep 21 16:48:46 ubuntu run-coder[556291]: restart_request=none
Sep 21 16:48:46 ubuntu run-coder[556291]: AUDIT id=SG-085
Sep 21 16:48:46 ubuntu run-coder[556291]: START=ef029d0ec1e0f8eae60cf85e464469612a2478c6
Sep 21 16:48:46 ubuntu run-coder[556291]: END=ef029d0ec1e0f8eae60cf85e464469612a2478c6
Sep 21 16:48:46 ubuntu run-coder[556291]: contract=0.28.2
Sep 21 16:48:46 ubuntu run-coder[556291]: model=cli-default
Sep 21 16:48:46 ubuntu run-coder[556291]: effort=medium
Sep 21 16:48:46 ubuntu run-coder[556291]: tokens_total=unknown
Sep 21 16:48:46 ubuntu run-coder[556291]: P1_moved=FAIL count=0
Sep 21 16:48:46 ubuntu run-coder[556291]: P2_rewrite=PASS behind=0
Sep 21 16:48:46 ubuntu run-coder[556291]: P3_note=FAIL note=no
Sep 21 16:48:46 ubuntu run-coder[556291]: P5_receipt=FAIL
Sep 21 16:48:46 ubuntu run-coder[556291]: P6_dirty=PASS dirty=no
Sep 21 16:48:46 ubuntu run-coder[556291]: negative_receipt=published
Sep 21 16:48:46 ubuntu run-coder[556291]: restart_marker_committed=PASS
Sep 21 16:48:46 ubuntu run-coder[556291]: report_cited_missing=SKIPPED reason=p5_not_pass
Sep 21 16:48:46 ubuntu run-coder[556291]: advisory_failed=P1_moved,P3_note
Sep 21 16:48:46 ubuntu run-coder[556291]: sql_touched=no
Sep 21 16:48:46 ubuntu run-coder[556291]: product_touch=no
Sep 21 16:48:46 ubuntu run-coder[556291]: files: count=0
Sep 21 16:48:46 ubuntu run-coder[556291]: log_tail:
Sep 21 16:48:46 ubuntu run-coder[556291]:   fixture sg029-09-no-date-visible-cosmetics: score=1.000 needs=1 unknowns=1 items=1.00
Sep 21 16:48:46 ubuntu run-coder[556291]:   fixture sg029-10-partial-label-cosmetics: score=1.000 needs=1 unknowns=1 items=1.00
Sep 21 16:48:46 ubuntu run-coder[556291]:   field_accuracy=0.833 over 10 fixtures
Sep 21 16:48:46 ubuntu run-coder[556291]:   unknown_rate=4/7=0.571
Sep 21 16:48:46 ubuntu run-coder[556291]:   correction_rate=0/6=0.000 (audit_event plugin.assertion.write rows=6)
Sep 21 16:48:46 ubuntu run-coder[556291]:
Sep 21 16:48:46 ubuntu run-coder[556291]:   $ cd /home/andrei/StorageGenie/backend && echo "=== ruff BASE ==="; ...
Sep 21 16:48:46 ubuntu run-coder[556291]:   === ruff BASE ===
Sep 21 16:48:46 ubuntu run-coder[556291]:   All checks passed!
Sep 21 16:48:46 ubuntu run-coder[556291]:   RUFF_EXIT=0
Sep 21 16:48:46 ubuntu run-coder[556291]:   === mypy BASE ===
Sep 21 16:48:46 ubuntu run-coder[556291]:   tests/test_postgres_dialect.py: error: Source file found twice under different module names: "test_postgres_dialect" and "tests.test_postgres_dialect"
Sep 21 16:48:46 ubuntu run-coder[556291]:   Found 1 error in 1 file (errors prevented further checking)
Sep 21 16:48:46 ubuntu run-coder[556291]:   MYPY_EXIT=2
Sep 21 16:48:46 ubuntu run-coder[556291]:   $ cd /home/andrei/StorageGenie && rtk grep -rn "mypy" docs/worklogs/SG-080_verify.log ...
Sep 21 16:48:46 ubuntu run-coder[556291]:   Error: Upstream request failed: [server_error] Upstream response was not valid JSON
```
(Full untruncated journal in `docs/worklogs/SG-090.log`.)

- **`run_coder=fail reason=` presence/absence:** raw count `journalctl ... | grep -c "run_coder=fail"` → `0`. **ABSENT.** The only
  `reason=` line in the journal is `report_cited_missing=SKIPPED reason=p5_not_pass`, which is the receipt publisher's own
  skip reason, not a coder-process failure line. The journal names no runner-side fault.
- The journal's final line is the LLM provider's own error, confirming **upstream-side death**, not packet fetch, not worktree
  dirt, not lane tooling: `Error: Upstream request failed: [server_error] Upstream response was not valid JSON`.

## G2 — CLI smoke (does the Coder start?)

Decided probe: documented `--version` (supported; exit 0). Bound: 120s; returned immediately.
```
$ timeout 120 opencode --version
1.17.19
exit=0
```
CLI starts. Binary `/usr/local/bin/opencode`, `-rwxr-xr-x root root 189245568 Jul 13 19:06`.

## G3 — launcher artifact (what exactly ran?)

Path hypothesis verified: `output/dispatch/SG-085.launcher.sh` exists (`700`, 215B). Exact `opencode` argv:
```
#!/usr/bin/env bash
set -euo pipefail
cd /home/andrei/StorageGenie
PROMPT_FILE=docs/packets/SG-085-eval-hardening.md
exec opencode run --auto --dir /home/andrei/StorageGenie --variant medium "$(cat "$PROMPT_FILE")"
```
Provider/model banner in the lane log (`output/dispatch/SG-085.log:2`):
```
> build · deepseek-v4.1-flash
```
The lane log's last line (`output/dispatch/SG-085.log:1494`) is:
```
Error: Upstream request failed: [server_error] Upstream response was not valid JSON
```
Both the launcher and the lane log were readable from the confinement — no refusal, nothing `unanswered`.

## G4 — verdict: GO (re-fire)

**GO** — all three required conditions hold, each with quoted evidence:
1. **Packet resolved** — exactly one (`SG-085-eval-hardening.md`), dispatch head quoted; `ef029d0` an ancestor of HEAD (G0).
2. **CLI starts** — `opencode --version` → `1.17.19`, exit 0 (G2).
3. **Transient-shaped death, all machinery healthy** — the journal and lane log both end on the upstream provider's
   `[server_error] Upstream response was not valid JSON`; no `run_coder=fail reason=`, no OOM/kill signal, no dirty tree,
   no auth/token error, no packet/tooling fault (G1/G3). The Coder got through substantial work (pytest, `eval/run.py`,
   ruff, mypy) before the provider failed mid-turn; zero commits is the natural consequence of an interrupted turn, not a
   persistent product defect.

**Fix home:** none required. Re-fire `SG-085 --force` (replay guard open, negative receipt `note=no`). The re-fire is the
destination; `D104` covers conditional spend. (F1 CLI-version difference is noted below; it is not the failure root — the
CLI on this host starts and runs.)

## Findings / issues (including out of scope)

- **F1 — CLI version drift.** `opencode --version` = `1.17.19` here, while `AGENTS.md` / `VPS.md` state `1.18.31`
  (re-measured 2026-09-17). Either the note is stale or the binary was replaced/downgraded (binary mtime `Jul 13 19:06`).
  Not the SG-085 failure root (the same CLI started and ran for 129s), but the config-table value is now wrong relative to
  the measured host. Destination: a future `VPS.md` re-measure / config-table correction slice.
- **F2 — SG-085 did real work before dying.** Unlike the SG-084/SG-080 case ("recon then provider fail"), SG-085's lane log
  shows baseline test/lint/type runs and an `eval/run.py` baseline. The packet's premise only claimed "ran 129s, committed
  nothing, tree clean" — that is confirmed; the "before any work" framing was not claimed by this packet, so no correction
  to the packet, but the record should not be read as a zero-work death.
- **F3 — no `run_coder=fail reason=` line exists at all** on the SG-085 unit. The lane's failure taxonomy is carried only
  by `DISPATCH_RESULT ... exit=1` plus the raw provider error. This is expected composition but worth stating so a future
  probe does not read its absence as a missing-evidence defect.
- **Non-vacuous check:** G0's exactly-one packet count ran against the real glob (`wc -l` → `1`, actual filename printed);
  G1's absence claim is a raw `grep -c` → `0` against the real journal, not a scoped-narrow grep; G2 invoked the real CLI
  and got a real version string; G3 quoted the real launcher file and real log lines. No criterion passed vacuously.

## Receipt note on the notes ref

**Zero-commit projection:** this probe DOES commit (the report + log), so the positive-receipt path is taken; the negative
path is not needed.

Work was pushed to `automation` (`9a90c5b..4260c5f`). Note added on WORK_HEAD `4260c5f` (bound 120s, exit 0) and the
notes ref pushed (`372e770..b3f6273`, bound 300s, exit 0). Verification fetched the refspec explicitly into a MAPPED local
name `refs/notes/storagegenie-coder-reports-sg090-verify` (`* [new ref]`, exit 0) and ran `show` on the mapped ref:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg090-verify show 4260c5faa16c40daee46114f0b66cbbca970bb96
Dispatch-ID: SG-090 | Report: docs/worklogs/SG-090_report.md | Work-HEAD: 4260c5faa16c40daee46114f0b66cbbca970bb96
show_exit=0
```

No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.

note=yes

## UNCLEAR

- **FIRST READ:** the packet's `G0` said "quote its dispatch-params head" and the premise table said `SG-085-*.md`; the
  actual file is `SG-085-eval-hardening.md` (not the probe-suffix pattern used by `SG-090-*`), which is fine, but the
  naming asymmetry between build slices and probe slices is a pattern worth a future note.
- **DURING EXECUTION:** `journalctl` is readable but emits the "not seeing messages from other users and the system" hint;
  the unit journal is nonetheless complete (56 lines, ends on the provider error). If system-journal confinement ever
  truncates, the probe's G1 would silently lose the tail — flag for a future probe to assert line-count reasonableness.
- **REMAINING:** `SG-085` re-fire may hit the same transient provider error (`[server_error]` invalid JSON). That is exactly
  what `D104` conditional spend covers; if a second re-fire dies identically, the next probe should escalate from
  "transient-shaped" to "persistent provider-side" and name the provider/credential owner.
