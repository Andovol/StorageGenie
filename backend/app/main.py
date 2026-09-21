import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api.v1.analytics import router as analytics_router
from app.api.v1.assets import router as assets_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.chat import router as chat_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.exports import router as export_router
from app.api.v1.health import router as health_router
from app.api.v1.households import router as households_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.planning import router as planning_router
from app.api.v1.plugins import router as plugins_router
from app.api.v1.review_tasks import router as review_tasks_router
from app.api.v1.settings import router as settings_router
from app.api.v1.users import router as users_router
from app.config import settings

app = FastAPI(title="StorageGenie", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
allow_credentials = "*" not in origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _problem_response(status: int, detail: str, title: str | None = None) -> JSONResponse:
    title = title or {400: "Bad Request", 403: "Forbidden", 404: "Not Found", 409: "Conflict", 413: "Payload Too Large", 422: "Unprocessable Entity"}.get(
        status, "Error"
    )
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail}
    return JSONResponse(status_code=status, content=body, media_type="application/problem+json")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:  # type: ignore[no-untyped-def]
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return _problem_response(exc.status_code, detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # type: ignore[no-untyped-def]
    return _problem_response(422, str(exc))

app.include_router(health_router, prefix="/v1")
app.include_router(households_router, prefix="/v1")
app.include_router(users_router, prefix="/v1")
app.include_router(evidence_router, prefix="/v1")
app.include_router(assets_router, prefix="/v1")
app.include_router(export_router, prefix="/v1")
app.include_router(jobs_router, prefix="/v1")
app.include_router(review_tasks_router, prefix="/v1")
app.include_router(candidates_router, prefix="/v1")
app.include_router(chat_router, prefix="/v1")
app.include_router(plugins_router, prefix="/v1")
app.include_router(planning_router, prefix="/v1")
app.include_router(analytics_router, prefix="/v1")
app.include_router(settings_router, prefix="/v1")


def _static_root() -> Path:
    """Directory holding the built UI. Default is the path baked into the image."""
    return Path(os.environ.get("SG_STATIC_DIR", "/app/static"))


def _static_file(full_path: str) -> Path | None:
    """Return the requested asset, else the SPA entrypoint, else None."""
    root = _static_root().resolve()
    candidate = (root / full_path).resolve()
    if full_path and candidate.is_file() and candidate.is_relative_to(root):
        return candidate
    index = root / "index.html"
    return index if index.is_file() else None


@app.get("/")
def root() -> Response:
    index = _static_root() / "index.html"
    if index.is_file():
        return FileResponse(index, media_type="text/html")
    return JSONResponse(content={"name": "StorageGenie", "version": "0.1.0"})


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str) -> Response:
    """Serve the built UI for client-side routes; never shadow the JSON API."""
    if full_path == "v1" or full_path.startswith("v1/"):
        return _problem_response(404, f"Not Found: /{full_path}")
    served = _static_file(full_path)
    if served is None:
        return _problem_response(404, f"Not Found: /{full_path}")
    return FileResponse(served)
