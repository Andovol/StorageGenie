---
type: provisioning-request
status: proposed
values: measured
from: StorageGenie
raised: 2026-09-14
---

## Request — web exposure for StorageGenie (`VPS.md` S1)

Give this project's web app a public HTTPS hostname through the host standard (S1):
one nginx site file proxying the hostname to the app's loopback port, `nginx -t` +
reload, a `certbot --nginx` certificate, and an nginx-level login (S3) — the app has
no login of its own.

**The values S1 asks a request to name, plus the login answer:**

```
PORT='8003'
HOSTNAME='storagegenie.dynv6.net'
APP_HAS_OWN_LOGIN='no'
```

**Proxy target:** the hostname to `127.0.0.1:8003` — the app publishes on loopback
only and serves both its JSON API (`/v1/*`) and its built UI on that one port (S1
item 1, S4).

**Login:** per S3 the page shows private household data, so it takes an nginx-level
login (`auth_basic` preferred). The credentials are the owner's to supply — please
state in what form you want them; never in this issue.

**Current state, measured 2026-09-14 before this filing:**

- The app runs on the host: compose project `storagegenie`, one service,
  `127.0.0.1:8003:8000`, `restart: unless-stopped`, healthy.
- Health by value: `{"status":"ok","db":"ok","storage":"ok"}` at `127.0.0.1:8003`.
- Listener proof: `ss -ltnp` shows `127.0.0.1:8003` only; nothing bound on `0.0.0.0`.
- The UI is a production build served same-origin by the app — no dev server, no
  second proxy, no tunnel.
- Memory: ~86 MiB (`docker stats --no-stream`), well inside the host budget (S6).
- DNS: `storagegenie.dynv6.net` already resolves to `87.106.66.242` (verified from
  the owner's workstation 2026-09-14). Noted because S2 left "must a new hostname be
  told to the updater?" open — it needed no telling here.

**Why this is a request and not project work:** the site file, reload, certificate
and login all need `sudo` on the shared host, and S1 assigns those steps to Launcher;
no project-side fix exists. The owner approves the host write when you take it up.

**Out of scope:** any change to the app, its compose file, its database, or any other
project's site, service, container or database.
