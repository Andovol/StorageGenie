# SG-184 — Verification clean; waiver recommended (no product change to bless)

Immutable audit: base `df1b5c825226676c0d9231b8f3938c61140e5811` → evidence work `04e80b52e29f4b08d7d4e98989af770b11ff8f6c` (six logs) → report `7d68408ee90942bd714d131cd5c8f15b79764960`. Forced-command status at dispatch end: `result=done id=SG-184 exit=0`; status verb after: `result=reject reason=replay id=SG-184` (correct: receipt already published, no `--force`). Mapped notes fetch read the receipt: Dispatch-ID SG-184, report path, Work-HEAD `7d68408e`, Product-HEAD `df1b5c8` zero product diff, settings envelope-sourced (command). Local pulled `--ff-only` to the exact Work-HEAD. Scope diff `df1b5c8..7d68408`: seven `docs/worklogs/SG-184*` files, 477 insertions, zero deletions; no product/test/config/lockfile/schema change.

Holistic rating: **96/100**, no flag. Contract 0.47.0 echoed with sha match (`49338e39a574…`).

## Functional evidence accepted

- Failpre in transient `/tmp` worktree (pre-`0b42e7d` bytes, HEAD tests): the identical four SG-175 discriminating failures, 6 controls passing (`SG-184_failpre.log` tails verified). Passpost on HEAD: 10 passed. BEFORE derived at the pre-repair bytes with the loader named (`PG-SC-12`).
- UI on HEAD: 18 passed; wrong-input control in the worktree fails 1 | passes 18 — the gate can fail (`PG-EV-01`).
- Probe re-run unchanged: `PROBE_OK`, 52 checks, negative controls rejecting on the real reader; prod DB hash unchanged.
- Served baseline: real GET bodies (status AND body) showing the OLD shape with 8/8 tasks resolved; served bundle hash == pre-repair record. The vacuous open-task branch was declared loudly per `PB-3`, not substituted.
- Protocol: no privileged operation attempted anywhere (known-denied Docker listing excluded up front) → no denial → no `PB-2` stop. Elapsed ≈360 s of 2100 s; no bound hit; no watcher; health delta none.

## Findings and dispositions

| Issue ID | Finding / evidence | Status / destination |
|---|---|---|
| ISS-SG184-A1 | Packet cited the decision gate at `candidates.py:52`; the `if` is at :50, `raise` at :51. Coder corrected in FIRST READ. | Trivial packet cite; RESOLVED in-report, −1. Attribution: packet. |
| ISS-SG184-A2 | G3's open-task production GET un-capturable (8/8 tasks resolved). Coder declared vacuity, carried proof via disposable failpre. | Benign premise gap; RESOLVED by `PB-3` handling, −2. Attribution: packet. No new rule: premises about live data go stale (`G-A5`), already covered. |
| FIRST READ corrections | Both of the above disclosed by the Coder before execution. | No hidden mismatch; supports the score. |
| REMAINING waiver | SG-175 `FLAG:SAFETY` hold; this slice REQUESTS, never grants. | OPEN → owner decision D13 (recommendation below). |
| REMAINING unserved | Merged code still UNSERVED; serving is a later rider. | FIX QUEUED — rider gated on D13. |
| REMAINING SG-176/177/178 + STILL-UNREPAIRED | Untouched by design. | Original grants / STATE ordered work stand. |

## Waiver recommendation

Recommend the owner GRANT the SG-175 `FLAG:SAFETY` waiver for serving-rider purposes: the merged bytes are now re-proved from scratch with discriminating fail-then-pass on both layers, a shown-failing control gate, a measured probe with negative controls, and a protocol-clean run (nothing privileged attempted). The breach lesson — optional reads also STOP — was encoded in this packet and observably followed. The grant remains the owner's (D13), never inferred.

Elapsed 360 s vs expected ~600 s (derived from SG-182's 585 s): under, no loop. Harness context-size reading unavailable; no conclusion made.
