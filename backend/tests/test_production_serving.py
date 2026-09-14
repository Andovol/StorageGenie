"""SG-041: production exposure shape — the built UI is served by the app.

The static root is resolved per request from ``SG_STATIC_DIR`` (image default
``/app/static``), so the fixture below proves the served response without a
real image build.  These tests never touch the database.
"""
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

INDEX_HTML = (
    "<!DOCTYPE html><html><head><title>StorageGenie</title></head>"
    '<body><div id="root"></div>'
    '<script type="module" src="/assets/index-test.js"></script></body></html>'
)


def _built_ui(tmp_path: Path) -> Path:
    root = tmp_path / "static"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (root / "assets" / "index-test.js").write_text("console.log('built');", encoding="utf-8")
    return root


def test_root_serves_built_index(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SG_STATIC_DIR", str(_built_ui(tmp_path)))

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<div id="root"></div>' in response.text


def test_spa_fallback_serves_built_index(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SG_STATIC_DIR", str(_built_ui(tmp_path)))

    with TestClient(app) as client:
        response = client.get("/catalog/whatever")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<div id="root"></div>' in response.text


def test_hashed_asset_is_served(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SG_STATIC_DIR", str(_built_ui(tmp_path)))

    with TestClient(app) as client:
        response = client.get("/assets/index-test.js")

    assert response.status_code == 200
    assert response.text == "console.log('built');"


def test_v1_unknown_route_is_problem_json_never_html(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SG_STATIC_DIR", "/nonexistent-static-root")

    with TestClient(app) as client:
        response = client.get("/v1/this-route-does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert "html" not in response.headers["content-type"]
    assert response.json()["status"] == 404


def test_openapi_and_docs_still_work(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SG_STATIC_DIR", "/nonexistent-static-root")

    with TestClient(app) as client:
        docs = client.get("/docs")
        openapi = client.get("/openapi.json")

    assert docs.status_code == 200
    assert openapi.status_code == 200
    assert "/v1/health" in openapi.json()["paths"]


def test_absent_static_root_still_starts_and_serves_v1(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("SG_STATIC_DIR", str(tmp_path / "not-built"))

    with TestClient(app) as client:
        unknown_v1 = client.get("/v1/this-route-does-not-exist")
        root = client.get("/")

    assert unknown_v1.status_code == 404
    assert unknown_v1.headers["content-type"].startswith("application/problem+json")
    assert root.status_code == 200
    assert root.headers["content-type"].startswith("application/json")
    assert root.json() == {"name": "StorageGenie", "version": "0.1.0"}
