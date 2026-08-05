from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.company import Base


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    website: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    http_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    technical_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    page_title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    meta_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    observations: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    ai_analysis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )