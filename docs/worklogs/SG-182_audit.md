# SG-182 — Custody valid; operations verified on synthetic state, consolidation complete, 96 no flag

## Receipt and independence

Trigger `SG-182 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` via background SSH (`job cf126f2f`); wake carried `result=done exit=0`. Status verb read once after: `result=done id=SG-182 inactive`. Mapped notes receipt (explicit refspec fetch): first line `Dispatch-ID: SG-182 | Report: docs/worklogs/SG-182_report.md`, Work-HEAD `1c8317bb81cea71fe4e04b1562979a7afbcb164a`, Base `d0591dc83810e987f656894a037dda8f633e208b` (SG-181 audit commit, clean at dispatch), Settings envelope-sourced, Contract 0.47.0 echoed. Pulled `--ff-only` to `1c8317b`. Base→candidate diff is fifteen `docs/worklogs/SG-182*` artifacts only (3 probes, paired failed+green run logs, focused-tests/mypy/ruff/vite/served-identity logs, worklog, consolidation, report) — no product/config/test/lockfile/schema/migration/operator change. Failed runs preserved under new paths, nothing overwritten: the SG-181 recurrence lever held.

## Independent verification (bodies and logs read)

| Claim | Check | Result |
|---|---|---|
| F-SG182-1 guard direction | `backend/scripts/backup_restore_drill.py` `_guard` rejects `resolved == work` and `work in resolved.parents` (prod-inside-work) with a message naming the opposite geometry; no `resolved in work.parents` case | CONFIRMED bounded defect; drill deliberately not run on that shape; twin search (1 class count) sane |
| F-SG182-2 real drill | G1 log tail: 22 checks 0 fails, WAL-resident rows captured, byte-equal restore, same-length corruption changes sha while `integrity_check=ok` | VERIFIED on synthetic state; hash-not-names/sizes lesson strengthens F-SG180-3 framing |
| F-SG182-3 migration | 16 checks 0 fails quoted; single head `20260924_sg114_relation`, 11 revisions, real upgrade, env override effective (ini-path DB absent), real readers 200 | VERIFIED disposable; FIRST READ packet correction (line 3 not 23) honest |
| F-SG182-5 served identity | Served CSS hash in identity log line 6 == fresh-build CSS in vite log (`index-DO0gjGV6.css`, 3.91 kB); served JS differs (`CYyuxefG` vs fresh `DRTd3YaC`); worklog states equality explicitly | CONFIRMED read-only observation; production schema at head via mode=ro read; container image stays UNVERIFIED |
| F-SG182-6 mypy red | Committed log tail: `Found 41 errors in 9 files (checked 92 source files)`; introducing commit NOT claimed (CO-37) | OPEN quality-gate item, honestly scoped |
| Gates/tests | tsc rc=0, vite rc=0 scratch outDir, ruff rc=0, focused nodes 6 passed (`6 passed in 0.10s` in log) | Green where claimed; red where red |
| Contract/health/budget | Host 0.47.0 + payload equality Coder-measured, tag peel still open (retained limitation); START→END health identical (lever held); 585s of 2100, no bound hit, no hang, no watcher | Stated limits, no overclaim |
| Isolation | Production contact = GETs + mode=ro sqlite reads only; scratch containment verified + cleaned; no installs, no provider calls, no Docker attempt (hence no denial, nothing routed around) | No breach |

Consolidation `SG-182_consolidation.md` read whole: SC-01..15/CX-01..08 mapped with exercised-vs-source-only separation, category split (approved-broken / disconnected / API-only / deferred / unverified / new-scope), rejected book retained, 3-way plan comparison with verdict, UI plan without pictures/packages, R1–R8 slices with undo/acceptance/permission boundary, UNVERIFIED limits, close dependency. W3C criteria named in prose, links not carried over — immaterial, noted, no deduction. Nothing in it contradicts the audited evidence; statuses match SG-173..181 audits.

## Verdict

All four acceptance lines hold: A1 real disposable controls with actual consumers; A2 complete mapping with explicit non-inference (`.github` absence left UNVERIFIED, remote CI not denied); A3 dependency-ordered plan with simpler-alternative comparison and preserved grants/holds; A4 identities/health/budget/FIRST READ/DURING/REMAINING with exact destinations. No safety or scope breach, no material mismatch, no needless loops (2 probe reruns are verification_attempts with preserved failures).

Architect judgement **96, no flag**. Nothing deducted: deduction_attribution empty. Below-95 procedure not triggered; no lever owed (the SG-181 lever was already bound by this packet and observably honoured). Owner impact: Coder worker 585s of lane 2100s (Coder-reported box clock; engine exact per runner record); cost and context-size readings unavailable. Register merge performed this turn (REC-ISS06/07/10/29/30/31 matured in place; REC-ISS34..40 added; CURRENT SG-182 boundary paragraph) so the canonical file owns every finding once.

## Dispositions

D1 register merge → done here (consolidation remains the working input, register the owner). D2 owner decisions → register/backlog + owner: R1 SG-175 hold, F-SG181-1 repair grant, F-SG181-3/4/6/7/8 + F-SG180-8/11 semantics, per-field/concurrency scope, R8 design, R5 release. D3 F-SG182-1 operator fix → R7 proposal, own grant, no production run. D4 mypy red → register quality item, owner prioritises. D5 UNVERIFIED limits → consolidated plan limits, no grant widening. D6 standing close conflict → CLOSE_BLOCKED stands until R1 disposition or owner waiver; this audit performs no deploy and grants none.
