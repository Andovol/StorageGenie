"""SG-181 path-mapping probe — preserve the PB-1 path correction as raw evidence.

Read-only against a disposable env; no writes, no DB rows. Shows the guessed
expiry paths are absent while the real router lives at /v1/plugins/expiry-tracker.

Run:
  cd /tmp/opencode && PYTHONPATH=<repo>/backend <repo>/backend/venv/bin/python \
      <repo>/docs/worklogs/SG-181_probe_paths.py
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg181-paths-"))
os.environ["DATABASE_URL"] = f"sqlite:///{TEMP_ROOT}/storagegenie.db"
os.environ["STORAGE_ROOT"] = str(TEMP_ROOT / "storage")
Path(os.environ["STORAGE_ROOT"]).mkdir()

from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.create_all(engine)

client = TestClient(app)
observations = []
for method, path in [
    ("POST", "/v1/assets/does-not-exist/classification"),
    ("GET", "/v1/assets/does-not-exist/classification"),
    ("GET", "/v1/status"),
    ("GET", "/v1/expiry/status"),
    ("POST", "/v1/plugins/expiry-tracker/assets/does-not-exist/classification"),
    ("GET", "/v1/plugins/expiry-tracker/status"),
]:
    r = client.request(method, path, params={"household_id": "no-such-household"})
    observations.append({"method": method, "path": path, "status": r.status_code, "body": r.text[:160]})
    print(json.dumps(observations[-1]))
print(json.dumps({"observations": observations}, indent=2))
