# Phase 0 — Foundation (Generic Core, Manual Only) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a local-first generic asset catalog where two household users can manually create assets, attach immutable photo evidence (SHA-256 + thumbnails), browse/search catalog, view assertion provenance on asset detail, and export a consistent backup — with no LLM/OCR/barcode dependency.

**Architecture:** Modular monolith: FastAPI + SQLAlchemy (SQLite WAL) + Alembic migrations expose `/v1/*` API; local filesystem evidence store outside web root accessed only via service layer; React + Vite + TypeScript frontend consumes API; durable `job`/`review_task` tables scaffolded but not executed (Phase 1 activates workers). All writes audited; evidence immutable; plugin contract not needed until Phase 1.

**Tech Stack:** Python 3.12 + FastAPI 0.110+ + Pydantic v2 + SQLAlchemy 2.0 + Alembic + SQLite (WAL) + Pillow 10+ + Uvicorn; Node 20 + React 18 + TypeScript 5 + Vite 5 + React Router + TanStack Query; Docker Compose; pytest + httpx TestClient; ruff + mypy + eslint+prettier

## Global Constraints

- Evidence before inference: every photo is immutable evidence; AI fields are assertions — even manual fields go through assertion path where provenance applies (blueprint §1.3).
- Generic core, vertical plugins: no `expiry`, `food`, `medicine` columns in core tables; Phase 0 must not add them (§1.3, §4.1).
- Human-in-the-loop invariant: not enforced by code in Phase 0 (no AI suggestions yet) but assertion `review_state` enum must support `proposed→accepted→rejected/superseded/needs_evidence` (§4.4).
- Never fabricate an expiry date: no expiry logic in Phase 0 at all; do not add expiry columns or guessing fallbacks (§1.3, §9.3).
- Local-first, provider-flexible: no hard dependency on any LLM/vision provider; no provider keys in repo or frontend (§1.3, §12.2).
- SQLite WAL for MVP, Postgres-compatible schema (no SQLite-only types that block migration) (§3.2).
- Original evidence immutable; derived files regenerable (§3.3).
- Every write audited via `audit_event` (§3.3, §4.2).
- Plugins cannot write core tables directly — enforce via service layer, not direct ORM writes from future plugin code (§3.3).
- Opaque IDs: UUIDv7 (or ULID) — never sequential integers exposed (§7).
- Idempotency keys on mutable POSTs, cursor pagination, RFC 9457 problem details, `provenance`/`confidence` on views, optimistic concurrency via `version`/`ETag` — scaffold in Phase 0, enforce where trivial, document deferrals (§7).

---

## File Structure (proposed)

```
StorageGenie/
├── docker-compose.yml
├── Makefile
├── .gitignore
├── README.md
├── docs/
│   ├── adr/
│   │   ├── ADR-001-local-first-storage.md
│   │   └── ADR-002-evidence-provenance.md
│   └── superpowers/plans/2026-08-28-phase-0-foundation.md  (this plan)
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── household.py
│   │   │   ├── user.py
│   │   │   ├── asset.py
│   │   │   ├── evidence.py
│   │   │   ├── assertion.py
│   │   │   ├── job.py
│   │   │   ├── review_task.py
│   │   │   └── audit_event.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── household.py
│   │   │   ├── user.py
│   │   │   ├── asset.py
│   │   │   ├── evidence.py
│   │   │   ├── assertion.py
│   │   │   ├── job.py
│   │   │   ├── review_task.py
│   │   │   └── common.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── evidence_service.py
│   │   │   ├── asset_service.py
│   │   │   ├── assertion_service.py
│   │   │   └── audit_service.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── households.py
│   │   │       ├── users.py
│   │   │       ├── assets.py
│   │   │       ├── evidence.py
│   │   │       ├── imports.py
│   │   │       └── health.py
│   │   └── storage/
│   │       ├── __init__.py
│   │       └── local_store.py
│   └── tests/
│       ├── conftest.py
│       ├── test_health.py
│       ├── test_households.py
│       ├── test_assets_crud.py
│       ├── test_evidence_upload.py
│       ├── test_assertions.py
│       ├── test_audit.py
│       └── test_export.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/client.ts
        ├── api/types.ts
        ├── routes/
        │   ├── CatalogPage.tsx
        │   ├── AssetDetailPage.tsx
        │   ├── CapturePage.tsx
        │   └── SettingsPage.tsx
        ├── components/
        │   ├── AssetCard.tsx
        │   ├── AssetForm.tsx
        │   ├── EvidenceGallery.tsx
        │   └── ProvenanceBadge.tsx
        └── hooks/
            └── useAssets.ts
```

---

### Task 1: Monorepo Scaffolding, Docker Compose, CI, Linting, Local Data Dirs

**Files:**
- Create: `docker-compose.yml`
- Create: `Makefile`
- Create: `.gitignore`
- Create: `backend/pyproject.toml`
- Create: `frontend/package.json`
- Create: `backend/Dockerfile`, `frontend/Dockerfile`

**Interfaces:**
- Consumes: nothing (bootstrap)
- Produces: `make dev`/`make test` commands; `docker compose up` runs backend+frontend; CI runs lint+test

- [ ] **Step 1: Write failing test — repo boots**

```python
# backend/tests/test_health.py (placeholder before backend exists)
def test_scaffold_exists():
    import pathlib
    assert pathlib.Path("backend/app/main.py").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_health.py -v`
Expected: FAIL — file not found

- [ ] **Step 3: Create monorepo scaffolding**

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./backend:/app
      - storage_data:/data/storage
      - ./data/db:/data/db
    environment:
      - DATABASE_URL=sqlite:////data/db/storagegenie.db
      - STORAGE_ROOT=/data/storage
      - HOUSEHOLD_DEFAULT_ID=seed-household-id
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    volumes: ["./frontend:/app", "/app/node_modules"]
    command: npm run dev -- --host 0.0.0.0 --port 5173
volumes:
  storage_data:
```

```toml
# backend/pyproject.toml (excerpt)
[project]
name = "storagegenie-backend"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.110","uvicorn[standard]","sqlalchemy>=2.0","alembic","pydantic>=2.0","pydantic-settings","pillow>=10","python-multipart","httpx"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
```

```makefile
# Makefile
dev:
	docker compose up --build
test:
	cd backend && pytest -q
lint:
	cd backend && ruff check . && mypy app
```

```gitignore
# .gitignore
data/db/*.db
data/storage/
.env
__pycache__/
node_modules/
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_health.py -v`
Expected: PASS after creating `backend/app/main.py` placeholder in next task

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml Makefile .gitignore backend/pyproject.toml
git commit -m "chore: scaffold monorepo, docker compose, lint config"
```

---

### Task 2: FastAPI Skeleton, Config, Health Endpoint, DB Session Wiring

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`
- Create: `backend/app/api/v1/health.py`
- Create: `backend/app/api/deps.py`

**Interfaces:**
- Consumes: Task 1 docker/compose
- Produces: `GET /v1/health` → `{status:"ok", db:"ok"|"error", storage:"ok"}`; `get_db()` dependency yields `Session`; `settings: Settings` singleton

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

def test_health_ok():
    c = TestClient(app)
    r = c.get("/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_health.py::test_health_ok -v`
Expected: FAIL — app not defined

- [ ] **Step 3: Implement minimal FastAPI + health**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/db/storagegenie.db"
    storage_root: str = "./data/storage"
    api_prefix: str = "/v1"
    idempotency_header: str = "Idempotency-Key"
settings = Settings()

# backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
class Base(DeclarativeBase): pass
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# backend/app/api/v1/health.py
from fastapi import APIRouter
router = APIRouter()
@router.get("/health")
def health(): return {"status": "ok", "db": "ok", "storage": "ok"}

# backend/app/main.py
from fastapi import FastAPI
from app.api.v1.health import router as health_router
app = FastAPI(title="StorageGenie")
app.include_router(health_router, prefix="/v1")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_health.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/main.py backend/app/config.py backend/app/db.py backend/app/api/v1/health.py backend/app/api/deps.py backend/tests/test_health.py
git commit -m "feat: fastapi skeleton and health endpoint"
```

---

### Task 3: Core Schema — Household, User, Base Mixins, Alembic, Seed

**Files:**
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/household.py`
- Create: `backend/app/models/user.py`
- Create: `backend/alembic/env.py`, `backend/alembic.ini`, `backend/alembic/script.py.mako`
- Create: `backend/alembic/versions/001_core_household_user.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Consumes: Task 2 `Base`, `engine`
- Produces: Tables `household(id PK UUIDv7, name, created_at)`, `user(id PK, household_id FK, display_name, email, created_at)` with FK → household; `alembic upgrade head` creates them; seed creates default household+2 users

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_households.py
from app.db import SessionLocal
from app.models.household import Household
def test_household_create():
    db = SessionLocal()
    h = Household(name="Test Household")
    db.add(h); db.commit(); db.refresh(h)
    assert h.id is not None
    assert h.name == "Test Household"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_households.py -v`
Expected: FAIL — table not exists / model missing

- [ ] **Step 3: Implement models + migration**

```python
# backend/app/models/base.py
import uuid, datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from app.db import Base
def new_id() -> str: return str(uuid.uuid7()) if hasattr(uuid,"uuid7") else str(uuid.uuid4())
class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# backend/app/models/household.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.db import Base
from app.models.base import TimestampMixin, new_id
class Household(TimestampMixin, Base):
    __tablename__ = "household"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

# backend/app/models/user.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from app.db import Base
from app.models.base import TimestampMixin, new_id
class User(TimestampMixin, Base):
    __tablename__ = "user"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, unique=True)
```

Alembic `env.py` imports `Base` and `models` for autogenerate; `001` creates household+user with FK and indexes.

- [ ] **Step 4: Run test to verify it passes**

Run: `alembic upgrade head; if ($?) { pytest backend/tests/test_households.py -v }`
Expected: PASS; `sqlite3 data/db/storagegenie.db ".tables"` shows `household`, `user`

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/ backend/alembic/ backend/alembic.ini
git commit -m "feat: household/user schema and initial migration"
```

---

### Task 4: Core Schema — Asset, Evidence, Assertion, AuditEvent, Job, ReviewTask

**Files:**
- Create: `backend/app/models/asset.py`
- Create: `backend/app/models/evidence.py`
- Create: `backend/app/models/assertion.py`
- Create: `backend/app/models/audit_event.py`
- Create: `backend/app/models/job.py`
- Create: `backend/app/models/review_task.py`
- Create: `backend/alembic/versions/002_core_catalog.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Consumes: Task 3 Base/mixins
- Produces: Tables per blueprint §4.2 (subset for Phase 0); all FKs indexed; `asset.household_id` enforces scoping; `evidence.sha256` unique+indexed; `assertion.review_state` enum; `audit_event` append-only

Schema decisions (ADR-002):
- `asset`: id PK, household_id FK, display_name, asset_type (enum: equipment/component/consumable/product/document/collection/container/unknown), status (enum DRAFT/PENDING_REVIEW/ACTIVE/ARCHIVED/DISPOSED/REJECTED/MERGED), quantity numeric, unit string, condition string, version int optimistic lock, created_at/updated_at
- `asset_location`, `identifier`, `classification`, `lifecycle_event`, `observation`, `asset_relation` **deferred** to Phase 1/4 — document in ADR as recipe, not Phase 0 tables (keeps Phase 0 slice small; avoids premature JSON junk drawer per Risk table)
- `evidence`: id PK, sha256 unique(64 hex), media_type, storage_key, original_filename, captured_at, source_kind, size_bytes, household_id FK (for scoping), created_at
- `asset_evidence` join table (asset_id, evidence_id, created_at) — many-to-many so one photo can back multiple assets after split/merge
- `assertion`: id PK, asset_id FK, field_path (e.g. `display_name`, `quantity`, `notes`; no expiry fields in Phase 0), value_json (TEXT JSON), source_type (user/manual/ai_vision — only user in Phase 0), confidence nullable, review_state enum, source_evidence_ids JSON, model JSON nullable, created_at
- `audit_event`: id PK, actor, action, entity_type, entity_id, before_json, after_json, timestamp, household_id
- `job`: id PK, job_type, state enum (CREATED/VALIDATING/NORMALIZING/EXTRACTING/ANALYZING/BUILDING/DEDUPLICATING/AWAITING_REVIEW/COMMITTING/COMPLETED/FAILED/CANCELLED/RETRYING), idempotency_key unique, config_snapshot JSON, household_id, created_at
- `review_task`: id PK, task_type, priority, subject_ref (asset/candidate/job id), proposed_change JSON, status enum (open/resolved/rejected), household_id

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_assets_crud.py (excerpt)
def test_asset_requires_household_fk(db):
    from app.models.asset import Asset
    import pytest, sqlalchemy.exc
    a = Asset(display_name="Screwdriver", household_id="nonexistent")
    db.add(a)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.commit()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_assets_crud.py::test_asset_requires_household_fk -v`
Expected: FAIL — table missing

- [ ] **Step 3: Implement models + migration 002**

```python
# backend/app/models/asset.py (excerpt)
class Asset(TimestampMixin, Base):
    __tablename__ = "asset"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(300), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")
    quantity: Mapped[float | None] = mapped_column(nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
```

```python
# backend/app/models/evidence.py
class Evidence(TimestampMixin, Base):
    __tablename__ = "evidence"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(ForeignKey("household.id"), nullable=False, index=True)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    source_kind: Mapped[str] = mapped_column(String(50), nullable=False, default="upload")
    size_bytes: Mapped[int] = mapped_column(nullable=False)
```

(Analogous for assertion/audit/job/review_task; join table `asset_evidence` with composite PK.)

- [ ] **Step 4: Run test to verify it passes**

Run: `alembic upgrade head; if ($?) { pytest backend/tests/test_assets_crud.py -v }`
Expected: PASS; FK violation raised when `household_id` invalid

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/asset.py backend/app/models/evidence.py backend/app/models/assertion.py backend/app/models/audit_event.py backend/app/models/job.py backend/app/models/review_task.py backend/alembic/versions/002_core_catalog.py
git commit -m "feat: core catalog schema — asset, evidence, assertion, audit, job, review_task"
```

---

### Task 5: Evidence Storage Service — SHA-256, Immutable Original, Thumbnails, Local FS

**Files:**
- Create: `backend/app/storage/local_store.py`
- Create: `backend/app/services/evidence_service.py`
- Modify: `backend/app/config.py` (add thumbnail sizes, allowed MIME types, max bytes)

**Interfaces:**
- Consumes: `settings.storage_root`, `Pillow`
- Produces:
  - `evidence_service.store_evidence(file_bytes, original_filename, media_type, household_id, db) -> Evidence` — computes SHA-256 before any expensive work, checks idempotency via `sha256` unique, writes original to `<storage_root>/<household_id>/<sha256[:2]>/<sha256>.<ext>` outside web root, generates thumbnails `256` and `512` via derived files, creates `Evidence` row atomically
  - `local_store.get_path(storage_key) -> Path` (authenticated serving only via API)
  - `local_store.thumbnail_path(storage_key, size) -> Path`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_evidence_upload.py
def test_evidence_sha256_and_idempotent(tmp_storage, db, household):
    from app.services.evidence_service import store_evidence
    data = b"fake-image-bytes"
    e1 = store_evidence(data, "photo.jpg", "image/jpeg", household.id, db)
    e2 = store_evidence(data, "photo_copy.jpg", "image/jpeg", household.id, db)
    assert e1.id == e2.id
    assert e1.sha256 == e2.sha256
    assert e1.storage_key == e2.storage_key

def test_evidence_thumbnail_exists(tmp_storage, db, household):
    from pathlib import Path
    from app.services.evidence_service import store_evidence
    from app.storage.local_store import thumbnail_path
    from PIL import Image
    import io
    img = Image.new("RGB", (100, 100), "red")
    buf = io.BytesIO(); img.save(buf, format="JPEG"); data = buf.getvalue()
    e = store_evidence(data, "red.jpg", "image/jpeg", household.id, db)
    assert Path(thumbnail_path(e.storage_key, 256)).exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_evidence_upload.py -v`
Expected: FAIL — service not implemented

- [ ] **Step 3: Implement storage + service**

```python
# backend/app/storage/local_store.py
from pathlib import Path
from app.config import settings
def storage_path_for(sha256: str, ext: str, household_id: str) -> Path:
    return Path(settings.storage_root) / household_id / sha256[:2] / f"{sha256}{ext}"
def thumbnail_path(storage_key: str, size: int) -> Path:
    p = Path(settings.storage_root) / storage_key
    return p.with_name(f"{p.stem}_thumb{size}{p.suffix}")

# backend/app/services/evidence_service.py
import hashlib, io, mimetypes
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from PIL import Image
from app.models.evidence import Evidence
from app.storage.local_store import storage_path_for
def store_evidence(file_bytes: bytes, original_filename: str, media_type: str, household_id: str, db: Session) -> Evidence:
    sha = hashlib.sha256(file_bytes).hexdigest()
    existing = db.query(Evidence).filter_by(sha256=sha).first()
    if existing: return existing
    ext = Path(original_filename).suffix or mimetypes.guess_extension(media_type) or ".bin"
    rel = f"{household_id}/{sha[:2]}/{sha}{ext}"
    abs_path = Path(thumbnail_path.__module__)  # placeholder
    # write original
    full = Path(settings.storage_root) / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_bytes(file_bytes)
    # thumbnails (best-effort for non-images)
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img = ImageOps.exif_transpose(img)
        for size in (256, 512):
            thumb = img.copy(); thumb.thumbnail((size, size))
            tp = full.with_name(f"{full.stem}_thumb{size}{full.suffix}")
            thumb.save(tp)
    except Exception: pass
    ev = Evidence(household_id=household_id, sha256=sha, media_type=media_type, storage_key=rel, original_filename=original_filename, size_bytes=len(file_bytes))
    db.add(ev); db.commit(); db.refresh(ev)
    return ev
```

(Actual impl handles EXIF orientation via `ImageOps.exif_transpose`, validates `media_type` by file signature, enforces `MAX_UPLOAD_BYTES=20MB`, and catches IntegrityError race.)

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_evidence_upload.py -v`
Expected: PASS; duplicate upload returns same row; thumbnail file exists for image

- [ ] **Step 5: Commit**

```bash
git add backend/app/storage/local_store.py backend/app/services/evidence_service.py backend/tests/test_evidence_upload.py
git commit -m "feat: immutable evidence storage with SHA-256 and thumbnails"
```

---

### Task 6: Audit Service + Automatic Audit Writes on Asset/Evidence/Assertion Mutations

**Files:**
- Create: `backend/app/services/audit_service.py`
- Modify: `backend/app/services/asset_service.py` (add audit calls)
- Modify: `backend/app/services/evidence_service.py` (add audit call)

**Interfaces:**
- Consumes: `audit_event` model, `Session`
- Produces: `audit_service.record(db, actor, action, entity_type, entity_id, before, after, household_id) -> AuditEvent`; every asset create/update/delete and evidence attach writes an audit row in same transaction

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_audit.py
def test_asset_create_writes_audit(db, household):
    from app.services.asset_service import create_asset
    a = create_asset(db, household.id, {"display_name": "Hammer", "asset_type": "equipment"}, actor="test")
    from app.models.audit_event import AuditEvent
    ev = db.query(AuditEvent).filter_by(entity_type="asset", entity_id=a.id).first()
    assert ev is not None
    assert ev.action == "asset.create"
    assert ev.after["display_name"] == "Hammer"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_audit.py -v`
Expected: FAIL — no audit row

- [ ] **Step 3: Implement audit service and wire into asset_service**

```python
# backend/app/services/audit_service.py
from sqlalchemy.orm import Session
from app.models.audit_event import AuditEvent
import datetime
def record(db: Session, *, actor: str, action: str, entity_type: str, entity_id: str, before: dict | None, after: dict | None, household_id: str):
    ev = AuditEvent(actor=actor, action=action, entity_type=entity_type, entity_id=entity_id, before_json=before, after_json=after, household_id=household_id, timestamp=datetime.datetime.utcnow())
    db.add(ev)
    return ev
```

In `asset_service.create_asset`/`update_asset`, call `audit_service.record(...)` before commit; use same transaction so rollback covers both.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_audit.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/audit_service.py backend/app/services/asset_service.py backend/tests/test_audit.py
git commit -m "feat: audit trail for asset and evidence mutations"
```

---

### Task 7: Household & User API Endpoints

**Files:**
- Create: `backend/app/schemas/household.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/api/v1/households.py`
- Create: `backend/app/api/v1/users.py`
- Modify: `backend/app/main.py` (register routers)

**Interfaces:**
- Consumes: household/user models
- Produces:
  - `GET /v1/households` → list (household-scoped;Phase 0 returns seeded household)
  - `POST /v1/households` (idempotent via `Idempotency-Key`)
  - `GET /v1/households/{id}` / `PATCH /v1/households/{id}`
  - `GET /v1/households/{hid}/users` / `POST /v1/households/{hid}/users`
  - All responses include `id`, `name`/`display_name`, `created_at`; errors use RFC 9457 `{"type","title","status","detail"}`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_households.py (add)
def test_create_household_via_api(client, db):
    r = client.post("/v1/households", json={"name": "Popescu"}, headers={"Idempotency-Key": "k1"})
    assert r.status_code == 201
    r2 = client.post("/v1/households", json={"name": "Popescu"}, headers={"Idempotency-Key": "k1"})
    assert r2.status_code == 201
    assert r.json()["id"] == r2.json()["id"]  # idempotent
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_households.py::test_create_household_via_api -v`
Expected: FAIL — route 404

- [ ] **Step 3: Implement schemas + routers**

```python
# backend/app/schemas/household.py
from pydantic import BaseModel
class HouseholdCreate(BaseModel): name: str
class HouseholdOut(BaseModel): id: str; name: str; created_at: str
    model_config = {"from_attributes": True}

# backend/app/api/v1/households.py
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.household import Household
router = APIRouter()
@router.post("/households", status_code=201)
def create_household(payload: HouseholdCreate, db: Session = Depends(get_db), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    # check idempotency via job/idempotency table or simple lookup; Phase 0: in-memory or audit lookup
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_households.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/household.py backend/app/schemas/user.py backend/app/api/v1/households.py backend/app/api/v1/users.py
git commit -m "feat: household and user API with idempotency"
```

---

### Task 8: Evidence Upload & Retrieval API

**Files:**
- Create: `backend/app/api/v1/evidence.py`
- Create: `backend/app/schemas/evidence.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `evidence_service.store_evidence`, `local_store`
- Produces:
  - `POST /v1/evidence` multipart `file`, `household_id` query → `201 {id, sha256, storage_key, media_type, size_bytes}` (idempotent by sha256)
  - `GET /v1/evidence/{id}` → metadata + `download_url` (authenticated, not direct FS path)
  - `GET /v1/evidence/{id}/file` → streams original with `Content-Type`; checks household scoping
  - `GET /v1/evidence/{id}/thumb/{size}` → thumbnail

- [ ] **Step 1: Write failing test**

```python
def test_upload_evidence_via_api(client, household):
    with open("tests/fixtures/red.jpg","rb") as f:
        r = client.post(f"/v1/evidence?household_id={household.id}", files={"file": ("red.jpg", f, "image/jpeg")})
    assert r.status_code == 201
    assert "sha256" in r.json()
    # duplicate upload second time returns same id
    with open("tests/fixtures/red.jpg","rb") as f:
        r2 = client.post(f"/v1/evidence?household_id={household.id}", files={"file": ("red.jpg", f, "image/jpeg")})
    assert r2.json()["id"] == r.json()["id"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_evidence_upload.py::test_upload_evidence_via_api -v`
Expected: FAIL — 404

- [ ] **Step 3: Implement endpoint**

```python
# backend/app/api/v1/evidence.py
from fastapi import APIRouter, UploadFile, Depends, Query
from app.db import get_db
from app.services.evidence_service import store_evidence
router = APIRouter()
@router.post("/evidence", status_code=201)
async def upload_evidence(file: UploadFile, household_id: str = Query(...), db=Depends(get_db)):
    data = await file.read()
    if len(data) > 20*1024*1024: raise HTTPException(413, detail="File too large")
    ev = store_evidence(data, file.filename or "upload", file.content_type or "application/octet-stream", household_id, db)
    return {"id": ev.id, "sha256": ev.sha256, "storage_key": ev.storage_key, "media_type": ev.media_type, "size_bytes": ev.size_bytes}
```

Add signature-based MIME check (magic bytes for JPEG/PNG/WebP/PDF) and reject mismatches with 422 RFC9457.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_evidence_upload.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/evidence.py backend/app/schemas/evidence.py
git commit -m "feat: evidence upload and retrieval API"
```

---

### Task 9: Manual Asset CRUD API (Household-Scoped) + Evidence Linking

**Files:**
- Create: `backend/app/schemas/asset.py`
- Create: `backend/app/services/asset_service.py`
- Create: `backend/app/api/v1/assets.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `asset`, `evidence`, `asset_evidence`, `assertion`, `audit_service`
- Produces:
  - `POST /v1/assets?household_id=` → create asset (manual); body `{display_name, asset_type, status, quantity, unit, condition, evidence_ids[]}`; writes assertions for each field with `source_type=user, review_state=accepted`; links evidence via join; audit in same transaction; `Idempotency-Key` supported
  - `GET /v1/assets?household_id=&q=&asset_type=&status=&cursor=&limit=` → cursor-paginated list (opaque cursor = base64(last_id:created_at)), `limit` default 20 max 100
  - `GET /v1/assets/{id}?household_id=` → detail with `evidence[]`, `assertions[]`, `audit_events[]`
  - `PATCH /v1/assets/{id}` → partial update; increments `version`; 409 on `If-Match` mismatch (optimistic concurrency)
  - `DELETE /v1/assets/{id}` → soft via status=ARCHIVED or hard delete per policy (ADR: soft by default in Phase 0)

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_assets_crud.py
def test_create_asset_manual(client, household, evidence):
    r = client.post(f"/v1/assets?household_id={household.id}", json={"display_name": "Drill", "asset_type": "equipment", "evidence_ids": [evidence.id]}, headers={"Idempotency-Key": "a1"})
    assert r.status_code == 201
    aid = r.json()["id"]
    r2 = client.get(f"/v1/assets/{aid}?household_id={household.id}")
    assert r2.json()["display_name"] == "Drill"
    assert len(r2.json()["evidence"]) == 1
    assert any(a["field_path"]=="display_name" and a["review_state"]=="accepted" for a in r2.json()["assertions"])

def test_asset_list_pagination(client, household):
    for i in range(3): client.post(f"/v1/assets?household_id={household.id}", json={"display_name": f"Item {i}"})
    r = client.get(f"/v1/assets?household_id={household.id}&limit=2")
    assert len(r.json()["items"]) == 2
    assert "next_cursor" in r.json()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_assets_crud.py -v`
Expected: FAIL — routes missing

- [ ] **Step 3: Implement service + router**

```python
# backend/app/services/asset_service.py (excerpt)
def create_asset(db, household_id, payload, actor="api", idempotency_key=None):
    # check idempotency: if key exists in audit/idempotency table return existing
    asset = Asset(household_id=household_id, display_name=payload["display_name"], asset_type=payload.get("asset_type","unknown"))
    db.add(asset); db.flush()
    for field in ("display_name","asset_type","quantity","unit","condition"):
        if field in payload and payload[field] is not None:
            db.add(Assertion(asset_id=asset.id, field_path=field, value_json=json.dumps(payload[field]), source_type="user", review_state="accepted"))
    if payload.get("evidence_ids"):
        for eid in payload["evidence_ids"]:
            db.execute(asset_evidence.insert().values(asset_id=asset.id, evidence_id=eid))
    audit_service.record(db, actor=actor, action="asset.create", entity_type="asset", entity_id=asset.id, before=None, after=payload, household_id=household_id)
    db.commit(); db.refresh(asset); return asset
```

Cursor pagination: `WHERE (created_at, id) < (cursor_created_at, cursor_id) ORDER BY created_at DESC, id DESC LIMIT ?+1`

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_assets_crud.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/asset.py backend/app/services/asset_service.py backend/app/api/v1/assets.py
git commit -m "feat: manual asset CRUD with household scoping and evidence links"
```

---

### Task 10: Assertion Provenance Display + PATCH via Assertions + Lifecycle Scaffolding

**Files:**
- Modify: `backend/app/schemas/asset.py` (add assertion view)
- Modify: `backend/app/services/assertion_service.py`
- Modify: `backend/app/api/v1/assets.py` (PATCH, attach evidence endpoint)
- Create: `backend/tests/test_assertions.py`

**Interfaces:**
- Consumes: Tasks 4,9
- Produces:
  - `GET /v1/assets/{id}` now returns `assertions: [{field_path, value, source_type, confidence, review_state, source_evidence_ids, model, created_at}]` sorted by `field_path`
  - `PATCH /v1/assets/{id}` creates new `superseded` chain: old assertion → `superseded`, new → `accepted`; audit records both
  - `POST /v1/assets/{id}/evidence` attach additional evidence after creation

- [ ] **Step 1: Write failing test**

```python
def test_patch_creates_new_assertion_and_supersedes_old(client, household):
    a = client.post(f"/v1/assets?household_id={household.id}", json={"display_name": "Box"}).json()
    client.patch(f"/v1/assets/{a['id']}?household_id={household.id}", json={"display_name": "Box v2"}, headers={"If-Match": "1"})
    detail = client.get(f"/v1/assets/{a['id']}?household_id={household.id}").json()
    vals = [x for x in detail["assertions"] if x["field_path"]=="display_name"]
    assert any(v["review_state"]=="superseded" for v in vals)
    assert any(v["review_state"]=="accepted" and v["value"]=="Box v2" for v in vals)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_assertions.py -v`
Expected: FAIL — superseded not implemented

- [ ] **Step 3: Implement assertion chaining + PATCH**

```python
# backend/app/services/assertion_service.py
def upsert_assertion(db, asset_id, field_path, value, actor, household_id, source_evidence_ids=None):
    prev = db.query(Assertion).filter_by(asset_id=asset_id, field_path=field_path, review_state="accepted").first()
    if prev: prev.review_state = "superseded"
    new = Assertion(asset_id=asset_id, field_path=field_path, value_json=json.dumps(value), source_type="user", review_state="accepted", source_evidence_ids=source_evidence_ids)
    db.add(new)
    return new
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_assertions.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/assertion_service.py backend/tests/test_assertions.py backend/app/api/v1/assets.py
git commit -m "feat: assertion provenance and supersession on patch"
```

---

### Task 11: Catalog Search (Simple Filter), Export Manifest, Job/ReviewTask Stubs

**Files:**
- Create: `backend/app/api/v1/exports.py`
- Modify: `backend/app/api/v1/assets.py` (search filters)
- Create: `backend/tests/test_export.py`
- Create: `backend/tests/test_search.py`

**Interfaces:**
- Consumes: asset model, evidence
- Produces:
  - `GET /v1/assets` supports `q` (ILIKE on display_name), `asset_type`, `status`, `has_evidence` filters — FTS5 deferred to Phase 4 (documented)
  - `GET /v1/export?household_id=` → `{household, assets[], evidence_manifest: [{id, sha256, storage_key, size_bytes}], assertions, audit_events, exported_at}` JSON; evidence files not streamed here — manifest allows verification; `Content-Disposition: attachment`
  - `GET /v1/jobs` / `GET /v1/review-tasks` stubs returning empty paginated lists (schema ready, no worker writes yet)

- [ ] **Step 1: Write failing test**

```python
def test_search_by_name(client, household):
    client.post(f"/v1/assets?household_id={household.id}", json={"display_name": "UniqueHammer123"})
    client.post(f"/v1/assets?household_id={household.id}", json={"display_name": "Screw"})
    r = client.get(f"/v1/assets?household_id={household.id}&q=UniqueHammer")
    assert len(r.json()["items"]) == 1

def test_export_manifest(client, household):
    a = client.post(f"/v1/assets?household_id={household.id}", json={"display_name": "ExportMe"}).json()
    r = client.get(f"/v1/export?household_id={household.id}")
    assert r.status_code == 200
    j = r.json()
    assert any(x["id"]==a["id"] for x in j["assets"])
    assert "evidence_manifest" in j
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_search.py backend/tests/test_export.py -v`
Expected: FAIL — filters/export missing

- [ ] **Step 3: Implement filters + export**

```python
# backend/app/api/v1/assets.py (search excerpt)
q = db.query(Asset).filter(Asset.household_id==household_id)
if q_param: q = q.filter(Asset.display_name.ilike(f"%{q_param}%"))
if asset_type: q = q.filter(Asset.asset_type==asset_type)
```

```python
# backend/app/api/v1/exports.py
@router.get("/export")
def export_catalog(household_id: str, db=Depends(get_db)):
    assets = db.query(Asset).filter_by(household_id=household_id).all()
    evidence = db.query(Evidence).filter_by(household_id=household_id).all()
    return {"household_id": household_id, "assets": assets, "evidence_manifest": [{"id":e.id,"sha256":e.sha256,"storage_key":e.storage_key} for e in evidence], "exported_at": datetime.utcnow().isoformat()}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_search.py backend/tests/test_export.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/exports.py backend/tests/test_export.py backend/tests/test_search.py
git commit -m "feat: catalog search filters and export manifest"
```

---

### Task 12: Frontend Scaffold — Vite + React + Router + TanStack Query + API Client

**Files:**
- Create: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/index.html`
- Create: `frontend/src/main.tsx`, `frontend/src/App.tsx`
- Create: `frontend/src/api/client.ts`, `frontend/src/api/types.ts`
- Create: `frontend/src/routes/CatalogPage.tsx` (placeholder), `frontend/src/routes/AssetDetailPage.tsx` (placeholder)

**Interfaces:**
- Consumes: backend `/v1/*` (CORS)
- Produces: `npm run dev` serves on :5173 with proxy to backend :8000; `apiClient.get/post/patch` wraps fetch with household_id injection and RFC9457 error parsing; `App.tsx` with nav Inbox/Capture/Catalog/Settings (Phase 0 shows Catalog+Capture+Detail)

- [ ] **Step 1: Write failing test (frontend smoke)**

```typescript
// frontend/src/api/client.test.ts
import { buildUrl } from "./client"
test("buildUrl injects household_id", () => {
  expect(buildUrl("/v1/assets", { household_id: "h1" })).toContain("household_id=h1")
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test` in frontend
Expected: FAIL — module missing

- [ ] **Step 3: Implement scaffold**

```typescript
// frontend/src/api/client.ts
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000"
export function buildUrl(path: string, params: Record<string,string>) {
  const u = new URL(BASE + path)
  Object.entries(params).forEach(([k,v]) => u.searchParams.set(k, v))
  return u.toString()
}
export async function apiGet<T>(path: string, params: Record<string,string> = {}): Promise<T> {
  const r = await fetch(buildUrl(path, params))
  if (!r.ok) throw await r.json() // RFC9457
  return r.json()
}
```

```json
// frontend/package.json (excerpt)
{"dependencies": {"react":"^18","react-dom":"^18","react-router-dom":"^6","@tanstack/react-query":"^5"}, "devDependencies": {"vite":"^5","typescript":"^5","vitest":"^1"}}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test` / `npm run build`
Expected: PASS; `curl http://localhost:5173` serves (when docker up)

- [ ] **Step 5: Commit**

```bash
git add frontend/package.json frontend/vite.config.ts frontend/tsconfig.json frontend/src/
git commit -m "feat: frontend scaffold with Vite, router, query, api client"
```

---

### Task 13: Catalog UI — Grid/Table, Filters, Pagination, Household Scoping

**Files:**
- Modify: `frontend/src/routes/CatalogPage.tsx`
- Create: `frontend/src/components/AssetCard.tsx`
- Create: `frontend/src/hooks/useAssets.ts`
- Modify: `frontend/src/api/types.ts`

**Interfaces:**
- Consumes: `GET /v1/assets` (Task 9/11), `GET /v1/households`
- Produces: Catalog page with household selector (default seeded household), `q` search box, type/status filters, cursor pagination (Load more), grid cards showing thumbnail, display_name, asset_type, evidence count, verification badge (count of `accepted` assertions)

- [ ] **Step 1: Write failing test (component)**

```typescript
// frontend/src/components/AssetCard.test.tsx
import { render, screen } from "@testing-library/react"
import { AssetCard } from "./AssetCard"
test("renders display_name and type", () => {
  render(<AssetCard asset={{ id:"1", display_name:"Hammer", asset_type:"equipment", status:"ACTIVE", evidence:[] }} />)
  expect(screen.getByText("Hammer")).toBeInTheDocument()
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test` in frontend
Expected: FAIL — component missing

- [ ] **Step 3: Implement hook + page**

```typescript
// frontend/src/hooks/useAssets.ts
import { useQuery } from "@tanstack/react-query"
import { apiGet } from "../api/client"
export function useAssets(household_id: string, q: string, cursor?: string) {
  return useQuery({ queryKey: ["assets", household_id, q, cursor], queryFn: () => apiGet("/v1/assets", { household_id, q, cursor: cursor||"", limit:"20" }) })
}
```

CatalogPage: household dropdown → `useAssets`; search input debounced 200ms; grid; each card links to `/assets/:id?household_id=`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/routes/CatalogPage.tsx frontend/src/components/AssetCard.tsx frontend/src/hooks/useAssets.ts
git commit -m "feat: catalog UI with search, filters, pagination"
```

---

### Task 14: Asset Detail, Manual Create, Evidence Attach — Full Provenance Display

**Files:**
- Modify: `frontend/src/routes/AssetDetailPage.tsx`
- Create: `frontend/src/routes/CapturePage.tsx`
- Create: `frontend/src/components/EvidenceGallery.tsx`
- Create: `frontend/src/components/ProvenanceBadge.tsx`
- Create: `frontend/src/components/AssetForm.tsx`

**Interfaces:**
- Consumes: `GET /v1/assets/{id}`, `POST /v1/assets`, `PATCH /v1/assets/{id}`, `POST /v1/evidence`, `POST /v1/assets/{id}/evidence`
- Produces:
  - AssetDetail: canonical fields, evidence timeline (thumbnails → full file on click via `/evidence/{id}/file`), identifiers section (empty in Phase 0), assertion table with field_path/value/source_type/review_state/confidence/evidence links, audit history, edit button, attach evidence button
  - Capture/Manual Create: form `display_name*`, `asset_type`, `quantity/unit/condition`, drag-drop file upload (previews SHA), evidence upload via `POST /v1/evidence` then `POST /v1/assets` with `evidence_ids`; success navigates to detail
  - ProvenanceBadge: `accepted` green, `proposed` amber, `needs_evidence` grey — Phase 0 only shows `accepted`/`superseded`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/components/ProvenanceBadge.test.tsx
import { render, screen } from "@testing-library/react"
import { ProvenanceBadge } from "./ProvenanceBadge"
test("accepted is green", () => {
  render(<ProvenanceBadge state="accepted" />)
  expect(screen.getByText("accepted")).toHaveClass("badge-green")
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL — component missing

- [ ] **Step 3: Implement components + pages**

```typescript
// frontend/src/components/ProvenanceBadge.tsx
export function ProvenanceBadge({ state }: { state: string }) {
  const cls = state==="accepted"?"badge-green": state==="proposed"?"badge-amber":"badge-grey"
  return <span className={cls}>{state}</span>
}
// frontend/src/components/EvidenceGallery.tsx
export function EvidenceGallery({ evidence }: { evidence: { id: string, thumbUrl: string, fileUrl: string }[] }) {
  return <div className="gallery">{evidence.map(e => <a key={e.id} href={e.fileUrl} target="_blank"><img src={e.thumbUrl} /></a>)}</div>
}
```

AssetDetail fetches `useQuery(["asset", id])`; renders `assertions` table; CapturePage uses `useMutation` for upload→create flow with `Idempotency-Key: crypto.randomUUID()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/routes/AssetDetailPage.tsx frontend/src/routes/CapturePage.tsx frontend/src/components/EvidenceGallery.tsx frontend/src/components/ProvenanceBadge.tsx frontend/src/components/AssetForm.tsx
git commit -m "feat: asset detail with provenance and manual capture flow"
```

---

### Task 15: Phase 0 Exit Verification — Manual Catalog → Attach → Search → Export Round-Trip

**Files:**
- Create: `backend/tests/test_phase0_e2e.py`
- Create: `docs/adr/ADR-001-local-first-storage.md`
- Create: `docs/adr/ADR-002-evidence-provenance.md`
- Modify: `README.md` (add Phase 0 run instructions)

**Interfaces:**
- Consumes: all prior tasks
- Produces: E2E test that satisfies exit condition: `manually catalog an item, attach source photos, search it, export a consistent backup`; ADRs; README runbook

- [ ] **Step 1: Write failing E2E test**

```python
# backend/tests/test_phase0_e2e.py
def test_phase0_exit_condition(client, household):
    # 1. create asset manually
    r = client.post(f"/v1/assets?household_id={household.id}", json={"display_name": "E2E Hammer", "asset_type": "equipment"})
    assert r.status_code == 201; aid = r.json()["id"]
    # 2. upload evidence and attach
    import io
    from PIL import Image
    img = Image.new("RGB", (50,50), "blue"); buf = io.BytesIO(); img.save(buf, format="JPEG")
    r2 = client.post(f"/v1/evidence?household_id={household.id}", files={"file": ("blue.jpg", buf.getvalue(), "image/jpeg")})
    eid = r2.json()["id"]
    r3 = client.post(f"/v1/assets/{aid}/evidence?household_id={household.id}", json={"evidence_ids": [eid]})
    assert r3.status_code == 200
    # 3. search it
    r4 = client.get(f"/v1/assets?household_id={household.id}&q=E2E Hammer")
    assert any(x["id"]==aid for x in r4.json()["items"])
    # 4. export and verify manifest contains asset+evidence
    r5 = client.get(f"/v1/export?household_id={household.id}")
    assert any(a["id"]==aid for a in r5.json()["assets"])
    assert any(e["id"]==eid for e in r5.json()["evidence_manifest"])
    # 5. detail shows provenance
    r6 = client.get(f"/v1/assets/{aid}?household_id={household.id}")
    assert any(a["field_path"]=="display_name" for a in r6.json()["assertions"])
```

- [ ] **Step 2: Run test to verify it fails (before wiring attach endpoint)**

Run: `pytest backend/tests/test_phase0_e2e.py -v`
Expected: FAIL if `POST /assets/{id}/evidence` not yet wired

- [ ] **Step 3: Implement missing glue + ADRs**

Wire `POST /v1/assets/{id}/evidence` if not already; write ADRs:

```markdown
# ADR-001: Local-first storage (SQLite WAL + local FS)
- Decision: SQLite WAL + local FS outside web root for Phase 0; Postgres+S3 via same SQLAlchemy/Alembic path later.
- Rationale: two users, operability over scale; WAL allows concurrent reads.
- Migration: `DATABASE_URL` switch + `STORAGE_ROOT` s3 prefix; no SQLite-only DDL.

# ADR-002: Evidence and provenance model
- Decision: immutable evidence + assertions with review_state + asset_evidence join + audit_event.
- Deferred: observation, identifier, classification, location, lifecycle_event, asset_relation to Phase 1/4 (recipe documented, not table).
```

Update `README.md` with `docker compose up`, `alembic upgrade head`, seeded household `Popescu` with 2 users.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q`
Expected: all PASS (health, households, assets, evidence, assertions, audit, search, export, e2e)

Run: `npm test` in frontend
Expected: PASS

Manual check: `docker compose up` → create asset via UI → attach photo → search → export JSON → verify `storage_key` file exists on disk and thumbnail loads

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_phase0_e2e.py docs/adr/ README.md
git commit -m "test: phase 0 exit E2E and ADRs"
```

---

## Decisions & Open Questions for Andrei (require human input before coding)

1. **Table scope for Phase 0** — Include only `household/user/asset/evidence/asset_evidence/assertion/audit_event/job/review_task` now, defer `observation/identifier/classification/location/lifecycle_event/asset_relation/job_step` to later phases? Recommendation: defer to keep Phase 0 slice small; they add no value without OCR/AI. Confirm.
2. **ID scheme** — UUIDv7 (time-ordered) vs UUIDv4? Blueprint says UUIDv7/ULID. Python 3.12 `uuid.uuid7` not yet stable; fallback to `uuid7` package or ULID? Recommendation: `ulid-py` or `uuid-utils` for UUIDv7. Confirm.
3. **Household scoping without auth** — Phase 0 has no auth. Use `?household_id=` query param + seeded default household selector in UI? Recommendation: yes, query param, UI remembers last household in localStorage. Confirm.
4. **Evidence MIME allowlist** — Accept JPEG/PNG/WebP/HEIC/PDF in Phase 0 or subset? HEIC requires `pillow-heif`. Recommendation: JPEG/PNG/WebP/PDF in Phase 0; HEIC in Phase 1 when conversion path needed. Confirm.
5. **Thumbnail spec** — 256 and 512 px, JPEG, EXIF-transposed, stored as derived files `*_thumb{size}.jpg`? Confirm.
6. **Search scope** — Simple `ILIKE` on `display_name` + filters in Phase 0; FTS5 in Phase 4? Confirm deferral.
7. **Export format** — JSON manifest + evidence files on disk (zip download later)? Phase 0 returns JSON manifest only; zip streaming in Phase 5 hardening? Confirm.
8. **Soft vs hard delete** — Phase 0 `DELETE /assets/{id}` sets `status=ARCHIVED` vs row delete? Recommendation: soft (ARCHIVED) to preserve audit. Confirm.
9. **Idempotency storage** — Dedicated table vs reuse `audit_event` lookup? Recommendation: dedicated `idempotency_key` table with TTL 24h; simplest for Phase 0. Confirm.
10. **Frontend household seed** — Name "Popescu Household" with users Andrei + wife? Confirm names/emails.
11. **Version/ETag** — Enforce `If-Match: <version>` on PATCH from day one or log warning only? Recommendation: enforce (409 on mismatch) — cheap and prevents lost updates for two users. Confirm.

---

## Risks Flagged (no action needed pre-Phase 0, but tracked)

- HEIC/HEIF without conversion will fail EXIF/thumbnail step — quarantine path in Phase 1, not needed for manual JPEG/PNG flow.
- SQLite FK enforcement disabled by default — `PRAGMA foreign_keys=ON` must be set in `db.py` engine connect args.
- `file.read()` into memory for SHA-256 — cap at 20MB; streaming hash later if large PDFs needed.
- Cursor pagination with `created_at` ties — need stable secondary sort on `id` to avoid duplicates.

## Test Plan Summary

- **Unit:** SHA-256/idempotent dedup, thumbnail EXIF, assertion supersession, audit write, pagination cursor encode/decode, idempotency key reuse, RFC9457 error shape
- **Integration (TestClient + temp SQLite + temp storage dir):** household CRUD, asset CRUD + evidence link, evidence upload dedup, search filters, export manifest consistency, PATCH version conflict 409, file serving authz by household_id
- **E2E (single test):** exit condition — create → attach → search → export → detail provenance
- **Frontend (Vitest + Testing Library):** AssetCard, ProvenanceBadge, Catalog filter, form validation (display_name required)
- **Manual:** `docker compose up` → UI: create hammer with 2 photos → detail shows 2 evidence + assertions → catalog search "hammer" <300ms → export JSON contains both → restart container → data persists (volume)

## What Is Explicitly NOT in Phase 0

LLM/vision calls, OCR, barcode/QR, perceptual hash, semantic/vector search, image generation, authentication, Expiry Tracker plugin (taxonomy, expiry dates, notifications, planning/chat agents), background workers/Redis/Celery, FTS5, PostgreSQL/S3 profile. Any of these appearing in a PR is out-of-scope for this phase.

