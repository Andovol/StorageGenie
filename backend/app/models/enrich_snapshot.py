from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class EnrichSnapshot(TimestampMixin, Base):
    """Append-only row for one enrichment source fetch (SG-100).

    One row per fetch, verbatim. There is NO update path: a correction is a
    NEW row. A degraded fetch records its named ``no_result_reason`` instead of
    being dropped. ``source`` is ``"off"`` or ``"jina"``; ``raw_body`` is the
    verbatim raw body (canonical JSON text) and ``raw_text`` the quoted text a
    degraded fetch carries.
    """

    __tablename__ = "enrich_snapshot"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    request_url: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_at: Mapped[str] = mapped_column(String(64), nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    no_result_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
