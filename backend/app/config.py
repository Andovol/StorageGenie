from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings. Phase 2 additions (SG-027) are named settings only.

    Cloud use stays OFF until selected: the provider id defaults to the
    deterministic fake double, both cost caps default to None (uncapped) per
    F2 (owner 2026-09-11: "no caps at first, we will re-evaluate later."), and
    consent defaults to False. Every value is env-overridable; nothing binds
    silently. The window that logs a bound cap is the provider (SG-027 G2).
    """

    database_url: str = "sqlite:///./data/db/storagegenie.db"
    storage_root: str = "./data/storage"
    api_prefix: str = "/v1"
    idempotency_header: str = "Idempotency-Key"
    household_default_name: str = "Popescu Household"
    cors_origins: str = "http://localhost:5173"
    max_upload_bytes: int = 20 * 1024 * 1024
    max_image_pixels: int | None = None
    exif_timestamps_enabled: bool = False
    dhash_near_threshold: int = 10
    thumbnail_sizes: list[int] = [256, 512]
    allowed_mime_types: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/tiff",
        "image/heic",
        "image/heif",
        "application/pdf",
    ]

    sg_provider_id: str = "fake"
    sg_model_id: str = "deepseek-v4-flash-vision-exp"
    opencode_api_key: str | None = None
    # SG-097: Jina Search fallback key (Enrich). Declared so the settings seam
    # reads it; the JINA_API_KEY process environment remains the fallback.
    jina_api_key: str | None = None
    sg_per_job_cap: float | None = None
    sg_monthly_cap: float | None = None
    sg_consent: bool = False
    # SG-028: confidence gate for AI auto-accept of low-risk fields. Every
    # gated field (identifier/expiry/expiry_date/condition/lot) is always
    # routed to review regardless of this value. Uncalibrated per G-A9.
    sg_confidence_threshold: float = 0.9
    # SG-028: selectable extraction prompt category ("food" default; "medicine").
    sg_prompt_category: str = "food"
    # SG-113 dormancy gate: the location-tree routes and the asset-detail
    # `locations[]` read are inert until the production migration lands. The
    # flag flips ONLY with the owner's migrate + flip + recreate word.
    sg_locations_enabled: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
