import datetime
import uuid

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    import uuid_utils  # type: ignore

    def new_id() -> str:
        return str(uuid_utils.uuid7())
except ImportError:

    def new_id() -> str:
        try:
            return str(uuid.uuid7())  # type: ignore[attr-defined]
        except AttributeError:
            return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
