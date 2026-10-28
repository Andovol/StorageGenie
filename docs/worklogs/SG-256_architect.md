# SG-256 architect note — row-11 polish: edit and clear an opened date (L3; launch record)

Stage: roadmap row 11, approved as an L3 stage on 2026-10-24 (D-1024-8), with the polish plan approved by the owner on 2026-10-28 (`"D4 - approved"`, recorded as D4 in `STATE.md`). The stage's work slice is SG-256; its own deploy rider is SG-257.

Planned envelope: `SG-256 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (the project's standing model policy; settings ride the trigger, never the packet).

Packet: `docs/packets/SG-256-row11-opened-date-edit-clear.md` (commit `fddda80`, pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ≈300 s, bracketed from this lane's recent actuals (149, 398, 447, 569 s); the backend host suite (~65 s), the frontend suite, the image proof and the new tests dominate.

Version chain: recorded `0.53.0` == published payload `contract-v0.53.0` == host `0.53.0` (the SG-255 receipt echo) == the echo the report must carry. `rules_check.sh` this session: CLEAN ×3, VERSION CURRENT 0.53.0.

Checklist (`DISPATCH.md` §2): scope = the owner-approved D4 plan · packet committed + pushed before the trigger (`fddda80`) · worktree clean · no dispatch in flight (`SG-256 --status` checked before the trigger) · nothing pushed while running · `PB-1`–`PB-6` cited · receipt = notes ref `refs/notes/storagegenie-coder-reports` + `Work-HEAD`, read back from the fetched remote ref.

Production basis (`G-K2`/`G-K3`): the app database and the live host are declared sensitive surfaces. **This slice writes neither:** no production database is opened or written; the tests use temporary SQLite; no host, package, service, container or provider action; $0. The feature's production writes happen only when the owner uses the new controls after the rider. The deploy is **not** in this slice; SG-257 is the rider, and it is where the live container is recreated.

Design calls SG-256 inherits (recorded so the next session does not re-derive them): clearing is represented by a **null active assertion** written through the one `_write_assertion` path — the previous date is `superseded`, the history and the `plugin.assertion.write` audit row stay, and the read path already treats a non-string value as none; a **POST** clear route, never DELETE; the clear with no active date is a **no-op** (no row, no audit row); the UI gets Edit and Clear on a dated row with no confirmation modal (one item, reversible, history kept); the deploy is the separate rider.
