# Desk relay: dispatch trigger holds the SSH channel for the full unit run (StorageGenie)

**Status:** investigation complete, relay ready. Filed file-only per PROPOSING.md (titles checked, no duplicate of #30/#42/#49/#53/#54).
**Lane:** StorageGenie (`andrei@87.106.66.242:2222`, forced-command `/usr/local/bin/dispatch`, conf `/etc/dispatch/storagegenie.conf`).
**Impact:** workflow-only — no work lost, every unit ran; each dispatch costs a dead wait (120s, then 600s) plus a status-verb round trip. Hypotheses H1/H2 below are stated as hypotheses (`G-A4`); facts carry provenance.

## Observed timeline (all times 2026-09-22, UTC; local trigger cap killed each hung call)

| Trigger (local job) | Verb | Local result | Unit outcome (server side) |
|---|---|---|---|
| (prior session) SG-081 attempt 1 | `SG-081` | exit 2 fast, `effort_unsupported_value_opencode_medium` | refused pre-Coder, instant |
| (prior session) SG-081 attempt 2 | `SG-081` | exit 1 fast, no reason | ran 4s, transient upstream invalid-JSON, negative receipt |
| `34650b01` | `SG-092` | **hung 120s, zero bytes, killed by cap** | ran to `done`, work `7c287cc`, positive receipt |
| `2ba837d4` | `SG-081 --force` | **hung 120s, zero bytes, killed by cap** | ran 559s to `done`, work `897894d`, positive receipt |
| `27c2311d` | `SG-082 --force` (+ ssh keepalives, cap 600s) | **hung 600s, zero bytes, killed by cap** | still `activating` at elapsed 608s when checked |
| all `--status` verbs (5×) | `SG-0xx --status` | exit 0 fast with valid `result=` lines | n/a (read path, always answers) |

**Rule extracted:** fast-finishing units return fast; every unit running longer than the local cap hangs the trigger until the cap kills it. No slow unit has returned a trigger line since the morning of 2026-09-22.

## Changelog window (contract tag notes = provenance)

- **2026-09-21 daytime:** SG-085 (129s), SG-088 (221s), SG-066 (299s) triggers all RETURNED (`result=no_receipt`). Engine predates v0.29.0 install.
- **2026-09-21 20:09Z — engine v0.29.0 installed** (0.29.1 tag note, `D247`): kill machinery, partial receipts, `TimeoutStopSec=60`, idle kill. No documented trigger-wait change.
- **2026-09-22 07:55Z — engine v0.29.1 installed** (0.29.2 tag note, `D250`): LNR-058/LNR-059 settle-wait rework — the trigger path now reads `ActiveState` alongside `Result` and, for a unit deemed running, **waits for the stop to finish** (bounded by the unit's own `TimeoutStopUSec`, or a named 10s constant). Adoption note: *"The trigger may wait up to the unit's stop window before printing."*
- 0.30.0's run-coder changes (LNR-065/066) are **source-only, not installed** — excluded.
- **Onset window: 2026-09-21 ~17:46Z → 2026-09-22 morning** — exactly the two installs above.

## Candidate mechanisms (ranked)

- **H1 (prime): the trigger path blocks until the unit settles, with a bound far longer than documented.** The documented bounds (10s settle fallback, 60s stop window, lane `TimeoutStopUSec=1min`) do NOT explain a 600s hang — so either a longer undocumented wait exists on the trigger path, or the wait keys off full unit completion (budget 2100s). Related systemd shape: for `Type=oneshot`, a synchronous `systemctl start` blocks until the process exits or `TimeoutStartUSec` (lanes read `TimeoutStartUSec=1h` in recent notes) — if the trigger starts the unit synchronously, every slow slice hangs by construction while refused/fast-dead slices return instantly. Matches ALL rows above.
- **H2 (weakened): network idle-drop (#32 shape).** Earlier plausible, now demoted: 600s with `ServerAliveInterval=60` still delivered zero bytes while the unit was healthy, and the `--status` path over the same transport never fails. A drop would not discriminate by code path.
- Excluded: `job_spawn` spawner (array spawns + wakes work; string-form ENOENT is by-design no-shell exec, separately reported and answered).

## Discriminating checks requested from the desk

1. Does the trigger path issue a synchronous unit start (no `--no-block`), and what `TimeoutStartUSec` does the storagegenie lane read (`systemctl show dispatch-storagegenie@<id> -p TimeoutStartUSec`)?
2. Correlate job `27c2311d`'s trigger window against the SG-082 unit's journal: when did the trigger print (if ever) relative to unit start/finish?
3. If H1 confirms: print the accept line (`result=…`) immediately at dispatch and do all settle-waiting server-side (or document the blocking contract so callers set caps ≥ budget).

## Workaround in use (StorageGenie)

Triggers fired with long caps purely as a delivery vehicle; the result line is treated as always-lost and every dispatch is re-attached via `--status` + notes-ref receipt check (DISPATCH.md §2 failure semantics — never the trigger log). Request: no lane-side fix needed; this relay asks only for the trigger contract to be prompt or documented.
