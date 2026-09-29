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
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
            "Idempotency-Key",
            "If-Match",
        ],
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


def test_cors_preflight_lockdown() -> None:
    """One coherent preflight over the real middleware: methods exact-set, headers
    include If-Match, disallowed method (TRACE) and disallowed header both refused."""
    client = TestClient(default_app)

    allowed = client.options(
        "/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "Content-Type, Idempotency-Key, If-Match",
        },
    )
    assert allowed.status_code == 200
    allowed_methods = allowed.headers.get("access-control-allow-methods", "")
    methods_list = {m.strip() for m in allowed_methods.split(",") if m.strip()}
    assert methods_list == {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
    allowed_headers = allowed.headers.get("access-control-allow-headers", "")
    headers_list = {h.strip().lower() for h in allowed_headers.split(",") if h.strip()}
    assert {"content-type", "idempotency-key", "if-match"} <= headers_list
    assert "*" not in headers_list

    disallowed_method = client.options(
        "/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "TRACE",
        },
    )
    assert disallowed_method.status_code == 400
    assert disallowed_method.text == "Disallowed CORS method"

    disallowed_header = client.options(
        "/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "X-Evil-Header",
        },
    )
    assert disallowed_header.status_code == 400
    assert disallowed_header.text == "Disallowed CORS headers"
