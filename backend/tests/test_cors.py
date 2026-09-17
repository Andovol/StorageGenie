from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.main import app as default_app


def create_app_with_cors(cors_origins_str: str) -> FastAPI:
    app = FastAPI()
    origins = [o.strip() for o in cors_origins_str.split(",") if o.strip()]
    allow_credentials = "*" not in origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def test_default_cors_with_explicit_origin() -> None:
    client = TestClient(default_app)
    response = client.get("/v1/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_blocks_untrusted_origin_when_explicit_origins_configured() -> None:
    client = TestClient(default_app)
    response = client.get("/v1/health", headers={"Origin": "https://evil.com"})
    assert "access-control-allow-origin" not in response.headers


def test_cors_disallows_credentials_when_wildcard_configured() -> None:
    app = create_app_with_cors("*")
    client = TestClient(app)
    response = client.get("/v1/health", headers={"Origin": "https://evil.com"})
    assert response.headers.get("access-control-allow-origin") == "*"
    assert response.headers.get("access-control-allow-credentials") is None
