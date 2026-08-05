"""synchronisation table companies

Revision ID: 7be343275653
Revises: 1c257cc9f081
Create Date: 2026-08-05 16:46:02.291294
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7be343275653"
down_revision: Union[str, Sequence[str], None] = "1c257cc9f081"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column(
            "sector",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="new",
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.alter_column(
        "companies",
        "website",
        existing_type=sa.String(length=255),
        type_=sa.String(length=500),
        existing_nullable=True,
    )

    op.alter_column(
        "companies",
        "city",
        existing_type=sa.String(length=100),
        type_=sa.String(length=150),
        existing_nullable=True,
    )

    op.alter_column(
        "companies",
        "name",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.create_index(
        op.f("ix_companies_id"),
        "companies",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_companies_id"),
        table_name="companies",
    )

    op.alter_column(
        "companies",
        "name",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    op.alter_column(
        "companies",
        "city",
        existing_type=sa.String(length=150),
        type_=sa.String(length=100),
        existing_nullable=True,
    )

    op.alter_column(
        "companies",
        "website",
        existing_type=sa.String(length=500),
        type_=sa.String(length=255),
        existing_nullable=True,
    )

    op.drop_column("companies", "created_at")
    op.drop_column("companies", "notes")
    op.drop_column("companies", "status")
    op.drop_column("companies", "sector")