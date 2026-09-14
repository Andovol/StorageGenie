"""SG-031 safe AI settings surface.

GET exposes the effective AI settings subset ONLY. The provider key is named
nowhere on this response path (exclusion by rule), so it cannot be serialized
or logged. PUT sets a process-side runtime model selection from a server-side
whitelist of tested models; an unknown id is an enforced 422 and changes
nothing. A backend restart drops the override back to the env default.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.providers.reader import effective_model_id, set_runtime_model_id

router = APIRouter()

# Tested models only. Metered-run evidence in the tree covers exactly one model:
# `deepseek-v4-flash-vision-exp` (SG-027 spike + shipped default; the SG-029
# baseline records all 7 metered calls on it). The packet's other premise id
# without the `-vision-exp` suffix appears in no metered run — only the Coder
# lane model `deepseek-v4.1-flash` does — and is not a vision path, so it is
# excluded (premise correction F-SG031-1).
ALLOWED_MODEL_IDS: tuple[str, ...] = ("deepseek-v4-flash-vision-exp",)


class AiSettingsOut(BaseModel):
    provider_id: str
    model_id: str
    allowed_model_ids: list[str]
    consent: bool
    per_job_cap: float | None
    monthly_cap: float | None
    prompt_category: str


class AiSettingsUpdate(BaseModel):
    model_id: str


def _read_safe_settings() -> AiSettingsOut:
    return AiSettingsOut(
        provider_id=settings.sg_provider_id,
        model_id=effective_model_id(),
        allowed_model_ids=list(ALLOWED_MODEL_IDS),
        consent=settings.sg_consent,
        per_job_cap=settings.sg_per_job_cap,
        monthly_cap=settings.sg_monthly_cap,
        prompt_category=settings.sg_prompt_category,
    )


@router.get("/settings/ai", response_model=AiSettingsOut)
def get_ai_settings() -> AiSettingsOut:
    return _read_safe_settings()


@router.put("/settings/ai", response_model=AiSettingsOut)
def update_ai_settings(payload: AiSettingsUpdate) -> AiSettingsOut:
    if payload.model_id not in ALLOWED_MODEL_IDS:
        raise HTTPException(status_code=422, detail=f"unsupported model id: {payload.model_id}")
    set_runtime_model_id(payload.model_id)
    return _read_safe_settings()
