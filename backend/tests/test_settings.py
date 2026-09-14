"""SG-031: safe AI settings endpoint + runtime model override (offline, zero network).

G1: the endpoint exposes only the safe AI subset. The provider key is excluded by
RULE (it is named nowhere on the response path) and proven absent from every byte
of the response. PUT enforces a server-side whitelist of tested models; an unknown
id is an enforced 422 with the selection unchanged. G2: the reader resolves the
process-side override when it builds the effective provider, so the model recorded
on a call equals the selection. Every gate is in-process: no key read (a test
sentinel string only), no network, $0.
"""

from __future__ import annotations

import io
import json
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

SETTINGS_TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-settings-tests-"))
SETTINGS_TEST_STORAGE_ROOT = SETTINGS_TEST_ROOT / "storage"
SETTINGS_TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{SETTINGS_TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(SETTINGS_TEST_STORAGE_ROOT)

from app.config import settings  # noqa: E402
from app.db import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Evidence, Household  # noqa: E402
from app.models.provider_call import ProviderCall  # noqa: E402
from app.services import job_service  # noqa: E402
from app.services.providers import opencode_go  # noqa: E402
from app.services.providers import reader as reader_mod  # noqa: E402

ALLOWED_MODEL = "deepseek-v4-flash-vision-exp"
# The packet's second premise id. The tree/ratings carry no metered run for it
# (only the Coder lane model `deepseek-v4.1-flash`); correcting the premise to
# tested-models-only drops it, and this test proves the endpoint rejects it.
UNPROVEN_MODEL = "deepseek-v4-flash"
ENV_DEFAULT_SENTINEL = "env-default-model-sentinel"
SENTINEL_KEY = "sk-SENTINEL-KEY-MUST-NEVER-APPEAR"
SAFE_FIELDS = {
    "provider_id",
    "model_id",
    "allowed_model_ids",
    "consent",
    "per_job_cap",
    "monthly_cap",
    "prompt_category",
}


def _route_module():  # type: ignore[no-untyped-def]
    import importlib

    return importlib.import_module("app.api.v1.settings")


def _clear_override() -> None:
    reader_mod.set_runtime_model_id(None)


def _jpeg_bytes() -> bytes:
    img = Image.new("RGB", (16, 16), "blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def settings_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "settings.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    _clear_override()
    household = Household(name="Settings Household")
    session.add(household)
    session.commit()
    evidence = Evidence(
        household_id=household.id,
        sha256="c" * 64,
        storage_key="settings/milk.jpg",
        media_type="image/jpeg",
        original_filename="milk.jpg",
        source_kind="upload",
        size_bytes=64,
    )
    session.add(evidence)
    session.commit()
    path = storage_root / evidence.storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_jpeg_bytes())
    try:
        yield session, household.id, evidence.id
    finally:
        _clear_override()
        session.close()
        engine.dispose()


def test_get_exposes_only_safe_subset_and_no_key_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "opencode_api_key", SENTINEL_KEY)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)
    _clear_override()

    with TestClient(app) as client:
        response = client.get("/v1/settings/ai")

    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == SAFE_FIELDS
    assert body["provider_id"] == "fake"
    assert body["model_id"] == settings.sg_model_id
    assert body["allowed_model_ids"] == [ALLOWED_MODEL]
    assert body["consent"] is False
    assert body["per_job_cap"] is None and body["monthly_cap"] is None
    assert body["prompt_category"] == "food"
    raw = response.content.decode()
    assert SENTINEL_KEY not in raw
    assert SENTINEL_KEY not in response.text
    assert "opencode_api_key" not in raw


def test_response_path_never_names_the_key_rule_exclusion() -> None:
    source = Path(_route_module().__file__).read_text(encoding="utf-8")
    assert "opencode_api_key" not in source
    assert "SENTINEL-KEY-MUST-NEVER-APPEAR" not in source


def test_put_unknown_model_is_422_and_selection_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "sg_model_id", ENV_DEFAULT_SENTINEL)
    _clear_override()
    with TestClient(app) as client:
        rejected = client.put("/v1/settings/ai", json={"model_id": UNPROVEN_MODEL})
        assert rejected.status_code == 422, rejected.text
        assert rejected.headers["content-type"].startswith("application/problem+json")
        after = client.get("/v1/settings/ai")
    assert after.json()["model_id"] == ENV_DEFAULT_SENTINEL


def test_put_listed_model_then_get_reflects_it(monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "sg_model_id", ENV_DEFAULT_SENTINEL)
    _clear_override()
    with TestClient(app) as client:
        accepted = client.put("/v1/settings/ai", json={"model_id": ALLOWED_MODEL})
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["model_id"] == ALLOWED_MODEL
        get_after = client.get("/v1/settings/ai")
    assert get_after.json()["model_id"] == ALLOWED_MODEL


def test_restart_resets_to_env_default(monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "sg_model_id", ENV_DEFAULT_SENTINEL)
    _clear_override()
    with TestClient(app) as client:
        client.put("/v1/settings/ai", json={"model_id": ALLOWED_MODEL})
        assert client.get("/v1/settings/ai").json()["model_id"] == ALLOWED_MODEL
    # The override is process-side state and nothing else; a backend restart drops
    # it, which is exactly this reset.
    _clear_override()
    with TestClient(app) as client:
        assert client.get("/v1/settings/ai").json()["model_id"] == ENV_DEFAULT_SENTINEL


def _valid_provider_body(model: str) -> dict[str, object]:
    content = json.dumps(
        {
            "items": [
                {
                    "name": "Milk",
                    "expiry_date": None,
                    "date_type": None,
                    "lot": None,
                    "confidence": 1.0,
                    "uncertainty_reasons": [],
                }
            ],
            "unknowns": [],
            "needs_evidence": False,
        }
    )
    return {
        "id": "settings-request-1",
        "model": model,
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def test_reader_resolves_override_and_records_selected_model(
    settings_env, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = settings_env
    captured: dict[str, str] = {}

    def fake_post(self, payload):  # type: ignore[no-untyped-def]
        captured["model"] = payload["model"]
        return _valid_provider_body(str(payload["model"]))

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", fake_post)
    monkeypatch.setattr(settings, "sg_provider_id", "opencode-go")
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "opencode_api_key", SENTINEL_KEY)
    monkeypatch.setattr(settings, "sg_model_id", ENV_DEFAULT_SENTINEL)
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)
    _clear_override()

    with TestClient(app) as client:
        selected = client.put("/v1/settings/ai", json={"model_id": ALLOWED_MODEL})
        assert selected.status_code == 200, selected.text

    job = job_service.create_job(session, household_id, [evidence_id])
    output = reader_mod.run_ai_extraction(session, job)
    session.flush()

    # The env default differs from the selection, so equality proves resolution.
    assert ENV_DEFAULT_SENTINEL != ALLOWED_MODEL
    assert captured["model"] == ALLOWED_MODEL
    assert output["model"] == ALLOWED_MODEL
    rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
    assert rows and all(row.model == ALLOWED_MODEL for row in rows)
    assert SENTINEL_KEY not in json.dumps(captured)


def test_reader_env_default_is_used_without_override(
    settings_env, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = settings_env
    captured: dict[str, str] = {}

    def fake_post(self, payload):  # type: ignore[no-untyped-def]
        captured["model"] = payload["model"]
        return _valid_provider_body(str(payload["model"]))

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", fake_post)
    monkeypatch.setattr(settings, "sg_provider_id", "opencode-go")
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "opencode_api_key", SENTINEL_KEY)
    monkeypatch.setattr(settings, "sg_model_id", ENV_DEFAULT_SENTINEL)
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)
    _clear_override()

    job = job_service.create_job(session, household_id, [evidence_id])
    output = reader_mod.run_ai_extraction(session, job)
    session.flush()

    assert captured["model"] == ENV_DEFAULT_SENTINEL
    assert output["model"] == ENV_DEFAULT_SENTINEL
    rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
    assert rows and all(row.model == ENV_DEFAULT_SENTINEL for row in rows)
