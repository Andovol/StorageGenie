from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.assets import router as assets_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.exports import router as export_router
from app.api.v1.health import router as health_router
from app.api.v1.households import router as households_router
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

app.include_router(health_router, prefix="/v1")
app.include_router(households_router, prefix="/v1")
app.include_router(users_router, prefix="/v1")
app.include_router(evidence_router, prefix="/v1")
app.include_router(assets_router, prefix="/v1")
app.include_router(export_router, prefix="/v1")


@app.get("/")
def root():  # type: ignore[no-untyped-def]
    return {"name": "StorageGenie", "version": "0.1.0"}
