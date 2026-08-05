from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.company import Base


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    audit_id: Mapped[int] = mapped_column(
        ForeignKey(
            "audits.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    global_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    strengths: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    weaknesses: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    opportunities: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    recommended_offer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )