# SG-061 report — read-only host check: nginx upload cap on the public entry

- **Dispatch-ID:** SG-061
- **Coder / effort:** `opencode` / `medium` (read from process arguments: `/proc/1629605/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --variant medium ...`)
- **Model:** `unknown` — no model id on argv; the lane sends no model id and the CLI default *is* the model (`AGENTS.md` Model policy). Not read from any identity line.
- **BASE (requested ref):** `origin/automation`
- **BASE (resolved commit):** `f2bcf5522e94ae44cff2bd0e06b2953851944ec9` (= start HEAD; worktree clean at start)
- **WORK_HEAD:** `__WORK_HEAD__`
- **Work dir:** `/home/andrei/StorageGenie`; origin `git@github.com:Andovol/StorageGenie.git`
- **Spend (real $):** $0.000000 actual vs $0 bound (zero provider calls)
- **Contract echo:** `0.28.2` — read from `AGENTS.md:4` and `STATE.md:5`. The host-side coder contract copy at `CONTRACT_DIR=/home/andrei/launcher` (`dispatch_coder.sh:11`) is **not readable by this account** (Permission denied); the wrapper's `contract_version()` echo is therefore **UNANSWERED** (not guessed). The `0.28.2` recorded in-repo is what was read.

## Answer in one line

**GREEN — the desk 25M ask was already applied on-box.** The site file serving the public entry sets `client_max_body_size 25M`, which is ≥ the app's 20 MiB cap, so **uploads up to 20 MiB are accepted**; only bodies > 25 MiB die at the nginx gate (413) before the app sees them, and bodies > 20 MiB up to 25 MiB pass nginx but are rejected by the app itself (413).

## G1 — the vhost (read-only)

- **Site file:** `/etc/nginx/sites-available/storagegenie` — the ONE file with `server_name storagegenie.dynv6.net` for the public entry.
  - `storagegenie:2: server_name storagegenie.dynv6.net;`
  - `storagegenie:7: proxy_pass http://127.0.0.1:8003;`
- **Enabled link confirmed:** `/etc/nginx/sites-enabled/storagegenie -> /etc/nginx/sites-available/storagegenie` (`readlink -f` resolves to the same file).
- **Named-world / collision ruled out (PG-SC-09):**
  - grep for `storagegenie.dynv6.net` hits **only** `sites-available/storagegenie` and its backup `storagegenie.bak-20260917T101347Z` (a non-enabled `.bak`, not a symlink). No second enabled block claims the name.
  - `default_server` appears only in `/etc/nginx/sites-available/default` (port 80), which is **not** symlinked in `sites-enabled`; no 443 `default_server` exists anywhere. A request to `storagegenie.dynv6.net:443` therefore selects the block above on `server_name`/SNI — it cannot fall through to another block.
  - Net: identification is conclusive; no unanswered attribution step.
- `auth_basic "StorageGenie Restricted"` + `/etc/nginx/htpasswd-storagegenie` present (reported as a fact; contents never read).

## G2 — effective upload cap (read-only)

- **Set-line, quoted:** `/etc/nginx/sites-available/storagegenie:3:    client_max_body_size 25M;`
- No host-wide value exists as a fallback concern: `/etc/nginx/nginx.conf` `http{}` has **no** `client_max_body_size` (include lines only), and the readable `conf.d/*.conf` files (`map_tuning.conf`, `personalmemory-rates.conf`) do not set it. The site's own `25M` overrides any inherited http-level value anyway.
- Site include followed one level: `/etc/letsencrypt/options-ssl-nginx.conf` — SSL parameters only, **no** `client_max_body_size`.
- **Effective cap = 25M = 25 × 1024 × 1024 = 26,214,400 bytes (25 MiB).**
- Backup confirms this is a *recent on-box change*: `storagegenie.bak-20260917T101347Z` (dated 2026-09-17T10:13:47Z) **lacks** the line; the live file has it. The desk ask from `#34` (2026-09-16) was applied on-box since.
- Finding (not an obstacle): `grep -rn client_max_body_size /etc/nginx/` also reports `Permission denied` on `/etc/nginx/conf.d/personalmemory-auth.conf` (and on `htpasswd-storagegenie`). The denied config is host-`http`-scoped; even if it set a cap, the server-level `25M` in the storagegenie block wins. So the effective cap is determined without it.

## G3 — verdict against the app (in-tree, read-only on host)

- **App cap line, quoted:** `backend/app/config.py:20:    max_upload_bytes: int = 20 * 1024 * 1024` → **20 MiB = 20,971,520 bytes**.
  - **Finding (packet premise drift):** the packet hypothesized this at `config.py:11`; it is actually at `config.py:20` (same value). `STATE.md:175` also cites the stale `config.py:11`. Value premise holds; line number does not.
- Enforcement + visible 413 confirmed in-tree: `backend/app/services/evidence_service.py:142-144` raises `UploadTooLargeError` over `max_upload_bytes`; `backend/app/api/v1/evidence.py:53` maps it to `HTTPException(status_code=413)`.
- **Verdict (one sentence):** Against the real on-box nginx config (`/etc/nginx/sites-available/storagegenie` on `87.106.66.242`, not a template or local stand-in — `PG-SC-12`), the public entry **ACCEPTS upload bodies of 0–20 MiB**, rejects **20–25 MiB** at the app with 413, and rejects **> 25 MiB** at nginx with 413 before the app is reached.
- No cap design proposed or applied — that is the desk's filed request.

## Non-mutating compliance (PG-PR-01)

Command classes run on the host: `ls`, `cat` (config structure lines only), `readlink`, `grep -rn`, `diff`, `find`, `ps`, `date`, `tr`, `nginx -v` (version print only), and git read-only (`status`, `rev-parse`, `branch`, `remote`, `log`, `fetch`). **No** sudo, **no** write/edit, **no** `nginx -t`/reload/restart, **no** service or container operation, **no** upload/HTTP request that could create rows, **no** credential or htpasswd content quoted, **no** `docker compose config`. Prod DB untouched; no migration; no deploy; nothing pushed to `storagegenie-evidence`.

## Tree / diff

Repo diff = `docs/worklogs/SG-061.log`, `SG-061_report.md`, `SG-061_verify.log` — **only** (scope ceiling honoured). Starting tree was clean; no vacuous pass (the cap was read from the live file and its presence confirmed by a diff against the pre-change backup).

## Receipt note on the notes ref

```
__NOTE_SHOW__
```

note=yes

## UNCLEAR

- **FIRST READ:** the packet expected the app cap at `backend/app/config.py:11`; the live file has it at `:20`. Same value, different line — treated as a finding, not bent to the packet.
- **DURING EXECUTION:** the host-side coder contract copy (`/home/andrei/launcher`, `CONTRACT_DIR`) is unreadable by this account, so the wrapper's own version echo could not be captured; also `grep` hit a `Permission denied` on `/etc/nginx/conf.d/personalmemory-auth.conf` (harmless — server-level 25M wins).
- **REMAINING:** none for this slice's question — the cap is measured and the desk ask is confirmed applied. Open outside scope: the in-repo `STATE.md:175`/packet reference to `config.py:11` is stale and could be corrected by a future docs slice; the 20 MiB app cap vs 25 MiB nginx headroom comparison is a desk/owner design matter, not measured here.
