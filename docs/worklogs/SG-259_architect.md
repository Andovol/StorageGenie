# SG-259 architect note — close-deploy rider for SG-258 (L3; launch record)

Stage: the household-and-document stage, approved by the owner on 2026-10-30 (`"d6 - approved"`, D6 in `docs/decisions/2026-10-30-session-approvals.md`). SG-258 is the work slice (audited 93); SG-259 is the rider.

Planned envelope: `SG-259 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (the project's standing model policy; settings ride the trigger, never the packet).

Packet: `docs/packets/SG-259-close-deploy-rider-for-sg258.md` (commit `df6dc56`, pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ≈450 s, from SG-257's actual 451 s (one build, one recreate, full verify) plus SG-258's engine/frontend-layer rebuild and the taxonomy check; this lane's recent actuals are 451 s (SG-257), 540 s (SG-256) and 1125 s (SG-258).

Version chain: recorded `0.56.0` == published payload `contract-v0.56.0` == host `0.56.0` (the SG-258 receipt echo) == the echo the report must carry. `rules_check.sh` this session: CLEAN ×3, VERSION CURRENT 0.56.0.

Checklist (`DISPATCH.md` §2): scope = the owner-approved D6 rider · packet committed + pushed before the trigger (`df6dc56`) · worktree clean · no dispatch in flight (`job_list` shows no running job — the SG-260/SG-261/SG-258 records are exited; SG-258 done; SG-261 inactive) · nothing pushed while running · `PB-1`–`PB-6` cited · receipt = notes ref `refs/notes/storagegenie-coder-reports` + `Work-HEAD`, read back from the fetched remote ref.

Production basis (`G-K2`/`G-K3`): the host, the app database and the live service are declared sensitive surfaces. **The owner's D6 approval covers this rider** (the stage's SG-259), and the packet is the written plan for it. The rider makes **one build and one recreate** of the backend container from the approved tree; **no migration**; the app database is opened **read-only** for the schema head and the 29-table census, with every count required identical; **no production row is written**; the new classification/date/clear controls are **not exercised live** (that would write the owner's data); no provider call, no key or `.env` read, $0. Health is read at the start, six times after the recreate and at the end. The release record and its tag are written by the Architect after this slice is audited, from the rider's evidence.

Design calls SG-259 inherits (recorded so the next session does not re-derive them): the served runtime diff must be exactly the three SG-258 backend files (`expiry_tracker.py`, `plugins.py`, `expiry_engine.py`); the frontend JS bundle must change (the classification control, the form and the Expiry page label) while the index/CSS may not; the served code, bundle and taxonomy are grepped from the served artifact, not the worktree; the live classification/date/clear is proven by the served bytes, not by a data write; the census is the production-safety proof. SG-258's three fix-queued findings (the `ReviewPage` form's data, the reverse-move task limbo, the `accepted`-with-no-date copy) are the **next stage**, not this rider; this rider serves the rated code as it stands.
