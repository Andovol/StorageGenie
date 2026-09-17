import os
import tempfile
from pathlib import Path

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-provider-gateway-tests-"))
TEST_STORAGE_ROOT = TEST_ROOT / "storage"
TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)

import json  # noqa: E402

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.db import Base  # noqa: E402
from app.models.provider_call import ProviderCall  # noqa: E402
from app.services.providers.fake import FakeProvider  # noqa: E402
from app.services.providers.protocols import ProviderResult  # noqa: E402
from app.services.providers.router import (  # noqa: E402
    BudgetExceededError,
    ProviderError,
    ProviderRouter,
    RouterConfig,
)


@pytest.fixture
def ledger_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'provider.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr("app.config.settings.storage_root", str(tmp_path / "storage"))
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _valid_router(primary: FakeProvider, fallback: FakeProvider | None = None) -> ProviderRouter:
    registry = {primary.provider_id: primary}
    fallback_id = None
    if fallback is not None:
        registry[fallback.provider_id] = fallback
        fallback_id = fallback.provider_id
    config = RouterConfig(
        provider_id=primary.provider_id,
        fallback_id=fallback_id,
        json_strict=True,
        cost_budget=10.0,
        retryable_errors=frozenset({"outage", "timeout", "rate_limited"}),
    )
    return ProviderRouter(config=config, registry=registry)


def test_router_picks_configured_provider() -> None:
    primary = FakeProvider(mode="valid", provider_id="fake-primary")
    fallback = FakeProvider(mode="valid", provider_id="fake-fallback")
    router = _valid_router(primary, fallback)

    assert router.resolve("fake-primary") is primary
    result = router.execute("extract_text", "img-1", estimated_cost=1.0)

    assert isinstance(result, ProviderResult)
    assert result.model_id == "fake-model-1"
    assert primary.invocations == 1
    assert fallback.invocations == 0


def test_fallback_fires_on_retryable_error_only() -> None:
    primary = FakeProvider(mode="outage_retryable", provider_id="fake-primary")
    fallback = FakeProvider(mode="valid", provider_id="fake-fallback")
    router = _valid_router(primary, fallback)

    result = router.execute("extract_text", "img-1", estimated_cost=1.0)

    assert result.normalized_output["text"] == "fake-text"
    assert primary.invocations == 1
    assert fallback.invocations == 1

    # Non-retryable surfaces: no fallback, error propagates.
    bad_primary = FakeProvider(mode="invalid_json_once", provider_id="bad-primary")
    bad_fallback = FakeProvider(mode="valid", provider_id="bad-fallback")
    bad_router = _valid_router(bad_primary, bad_fallback)
    with pytest.raises(ProviderError):
        bad_router.execute("extract_text", "img-1", estimated_cost=1.0)
    assert bad_primary.invocations == 1
    assert bad_fallback.invocations == 0


def test_ledger_row_per_call_carries_section_33_fields(ledger_db: Session) -> None:
    primary = FakeProvider(mode="valid", provider_id="fake-primary")
    router = _valid_router(primary)

    result = router.execute("embed", "hello", estimated_cost=0.5)

    row = ProviderCall(
        provider="fake-primary",
        model=result.model_id,
        prompt_template_version="fake-prompt-v1",
        input_hashes=json.dumps({"text_sha256": "abc123"}),
        output_payload=json.dumps(result.raw_payload),
        cost=result.cost,
        usage_json=json.dumps(result.usage),
        latency_ms=result.latency_ms,
        error_state=None,
        job_id=None,
    )
    ledger_db.add(row)
    ledger_db.commit()

    read_back = ledger_db.query(ProviderCall).filter_by(provider="fake-primary").one()
    assert read_back.model == "fake-model-1"
    assert read_back.prompt_template_version == "fake-prompt-v1"
    assert json.loads(read_back.input_hashes or "{}") == {"text_sha256": "abc123"}
    assert json.loads(read_back.output_payload or "{}") == result.raw_payload
    assert read_back.cost == result.cost
    assert json.loads(read_back.usage_json or "{}") == result.usage
    assert read_back.latency_ms == result.latency_ms
    assert read_back.error_state is None
    assert read_back.job_id is None
    assert read_back.created_at is not None
    assert read_back.updated_at is not None


def test_budget_exceeded_refuses_precall_with_zero_invocations() -> None:
    primary = FakeProvider(mode="valid", provider_id="fake-primary")
    fallback = FakeProvider(mode="valid", provider_id="fake-fallback")
    config = RouterConfig(
        provider_id="fake-primary",
        fallback_id="fake-fallback",
        json_strict=True,
        cost_budget=1.0,
        retryable_errors=frozenset({"outage"}),
    )
    router = ProviderRouter(config=config, registry={primary.provider_id: primary, fallback.provider_id: fallback})

    with pytest.raises(BudgetExceededError):
        router.execute("extract_text", "img-1", estimated_cost=5.0)

    assert primary.invocations == 0
    assert fallback.invocations == 0


def test_router_consumes_estimate_and_shadows_adapter_guard() -> None:
    """Pin the SG-060 split in executable form (no network, no key, no adapter).

    A local recording double stands in for a provider, so the test proves the
    two halves of the documented behaviour directly:

    (a) over budget, `router.execute` refuses at the router with ZERO provider
        invocations; and
    (b) in budget, the router consumes `estimated_cost` for that check and does
        NOT forward it (only `*args, **kwargs` travel), so the provider sees the
        `estimated_cost` default 0.0 — the adapter-level guard is shadowed on
        the routed path and enforces direct invocations only.

    This sits beside `test_budget_exceeded_refuses_precall_with_zero_invocations`
    because it is the same router concern; the recording double is what makes
    the shadowing (b) observable, which `FakeProvider` does not expose.
    """

    class _RecordingProvider:
        provider_id = "recording-primary"

        def __init__(self) -> None:
            self.invocations = 0
            self.seen_estimates: list[float] = []

        def extract_text(
            self, text: str, prompt: str = "", *, estimated_cost: float = 0.0
        ) -> ProviderResult:
            self.invocations += 1
            self.seen_estimates.append(estimated_cost)
            return ProviderResult(
                normalized_output={"text": "recorded", "source": text},
                raw_payload={"recording": True},
                request_id="recording-1",
                usage={},
                cost=0.0,
                model_id="recording-model",
                latency_ms=0.0,
            )

    provider = _RecordingProvider()
    router = ProviderRouter(
        config=RouterConfig(
            provider_id=provider.provider_id,
            fallback_id=None,
            json_strict=True,
            cost_budget=1.0,
            retryable_errors=frozenset({"outage"}),
        ),
        registry={provider.provider_id: provider},
    )

    with pytest.raises(BudgetExceededError):
        router.execute("extract_text", "over-budget", estimated_cost=5.0)
    assert provider.invocations == 0, "router refusal must precede any provider invocation"

    result = router.execute("extract_text", "in-budget", estimated_cost=0.5)
    assert result.normalized_output["text"] == "recorded"
    assert provider.invocations == 1
    assert provider.seen_estimates == [0.0], (
        "router consumes the estimate; the adapter receives only its default"
    )


def test_all_four_fake_shapes_green() -> None:
    valid = FakeProvider(mode="valid", provider_id="fake-valid")
    assert valid.extract_text("img-1").normalized_output["text"] == "fake-text"

    flaky = FakeProvider(mode="invalid_json_once", provider_id="fake-flaky")
    with pytest.raises(ProviderError):
        flaky.extract_text("img-1")
    recovered = flaky.extract_text("img-1")
    assert recovered.normalized_output["text"] == "fake-text"

    needs = FakeProvider(mode="needs_evidence", provider_id="fake-needs")
    needs_result = needs.extract_items(b"img-1", "prompt")
    assert needs_result.normalized_output["needs_evidence"] is True

    outage = FakeProvider(mode="outage_retryable", provider_id="fake-outage")
    with pytest.raises(ProviderError) as exc_info:
        outage.extract_text("img-1")
    assert exc_info.value.kind == "outage"
