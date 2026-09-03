from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/db/storagegenie.db"
    storage_root: str = "./data/storage"
    api_prefix: str = "/v1"
    idempotency_header: str = "Idempotency-Key"
    household_default_name: str = "Popescu Household"
    cors_origins: str = "http://localhost:5173"
    max_upload_bytes: int = 20 * 1024 * 1024
    max_image_pixels: int | None = None
    thumbnail_sizes: list[int] = [256, 512]
    allowed_mime_types: list[str] = ["image/jpeg", "image/png", "image/webp", "application/pdf"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
