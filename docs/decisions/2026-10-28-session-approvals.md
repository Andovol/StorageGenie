# 2026-10-28 — W1's image half, the row-11 polish, and the close (D3, D4, D5)

Owner's starter directive, quoted (2026-10-28, this chat):

> Next action: check Launcher #97. If the desk has restarted the runtime, run SG-255 (no code change): the image proof (2 passed, 0 skipped), the gate pass twice, the wrong-image control, the whole-suite/mount trial, then the A-vs-D verdict. If #97 is still open, run the row-11 polish (an opened date cannot yet be edited or cleared once set) and re-check #97 at the next start.

> Decided this session, not derivable from the code: the 0.53.0 adoption was the dispatch gate; W1 was approved at L3; the Docker restart is a Launcher-desk item, not a decision taken here; no app deploy was owed.

> How the owner wants it: plain-language reports, the roadmap position with each one, one decision at a time, and no question carried inside a starter.

## D3 — SG-255: finish W1's image half

**Do:** on the owner's instruction above, check Launcher #97 and run SG-255 if the desk had fixed the runtime. The desk's reply says the lane's rootless `docker.service` was restarted on 2026-10-27 23:50 Bucharest (D544, owner-approved): server 29.9.2, `docker run --rm busybox true` rc 0, the app container came back by itself (same ID `a831fbd0`, image `e8c73735`), `/v1/health` 200; keep `DOCKER_CONFIG` until the root-owned `~/.docker` is fixed in the engine arc. SG-255 was dispatched and audited **97**; W1 is complete — image proof 2 passed / 0 skipped, `make backend-test` rc 0 twice, the wrong-image control fails for busybox's own reason, the whole-suite image trial reds so **A is rejected and D stands**; no app deploy was owed.

## D4 — the row-11 polish plan

Owner's exact approval: **"D4 - approved"** (2026-10-28).

**The approved plan:** an opened date becomes editable and clearable. Clearing supersedes the active accepted `opened_date` assertion with a new accepted assertion holding JSON `null` through the existing `_write_assertion` path, so the old date stays in the superseded assertion and the audit row is written; a clear with no active date writes nothing. A `POST .../opened/clear` route reuses the existing plugin/asset/household guards. The Opened countdown section gets Edit and Clear on a dated row; the no-date form is unchanged. One work slice, then its own deploy rider; no migration.

**Outcome:** SG-256 audited **96** (backend 748 passed / 2 deselected / 0 failed plus the image proof; frontend 310 passed; FAIL-then-PASS committed). SG-257 audited **98** and served it live: container `40bee778` from image `b2c42abd`, one recreate, no migration, the served runtime diff exactly `api/v1/plugins.py` + `plugins/expiry_tracker.py`, the JS bundle changed, the 29-table census identical, health 200. **The live clear/edit was not exercised** — it would write the owner's data; the first real clear awaits the owner's use. Release record `docs/releases/2026-10-28-sg256.md`, tag `release-2026-10-28-sg256`.

## D5 — close the session

Owner's exact instruction: **"D5 - close now"** (2026-10-28).

The close is `CLOSE_COMPLETE`; the release is live and recorded; no approved work remains. The next choices each need the owner's word: the household-and-document half of row 11; W3; W4; W5; row 14's deferred work. The next session brings one recommendation in one message.
