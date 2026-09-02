from pathlib import Path

from app.config import settings


def storage_path_for(sha256: str, ext: str, household_id: str) -> Path:
    return Path(settings.storage_root) / household_id / sha256[:2] / f"{sha256}{ext}"


def thumbnail_path(storage_key: str, size: int) -> Path:
    p = Path(settings.storage_root) / storage_key
    return p.with_name(f"{p.stem}_thumb{size}{p.suffix}")


def get_path(storage_key: str) -> Path:
    return Path(settings.storage_root) / storage_key


def absolute_path(storage_key: str) -> Path:
    return get_path(storage_key)


def storage_path(storage_key: str) -> Path:
    return get_path(storage_key)


def ensure_storage_root() -> None:
    Path(settings.storage_root).mkdir(parents=True, exist_ok=True)
