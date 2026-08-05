from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from backend.models.company import Base


class Writer(Base):

    __tablename__ = "writers"

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
        index=True,
    )

    audit_id: Mapped[int] = mapped_column(
        ForeignKey(
            "audits.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    score_id: Mapped[int] = mapped_column(
        ForeignKey(
            "scores.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    email_subject: Mapped[str] = mapped_column(
        Text,
    )

    email_body: Mapped[str] = mapped_column(
        Text,
    )

    commercial_offer: Mapped[str] = mapped_column(
        Text,
    )

    call_to_action: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )