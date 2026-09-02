from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.assets import router as assets_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.exports import router as export_router
from app.api.v1.health import router as health_router
from app.api.v1.households import router as households_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.review_tasks import router as review_tasks_router
from app.api.v1.users import router as users_router
from app.config import settings

app = FastAPI(title="StorageGenie", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
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


@app.get("/")
def root():  # type: ignore[no-untyped-def]
    return {"name": "StorageGenie", "version": "0.1.0"}
