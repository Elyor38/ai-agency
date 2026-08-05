"""ajout table scores

Revision ID: 1c257cc9f081
Revises: 5ba84a3fb53a
Create Date: 2026-08-05 14:47:43.479868
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "1c257cc9f081"
down_revision: Union[str, Sequence[str], None] = "5ba84a3fb53a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scores",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "audit_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "global_score",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "strengths",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "weaknesses",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "opportunities",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "recommended_offer",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "summary",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["audit_id"],
            ["audits.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_scores_audit_id"),
        "scores",
        ["audit_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_scores_company_id"),
        "scores",
        ["company_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_scores_id"),
        "scores",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_scores_id"),
        table_name="scores",
    )

    op.drop_index(
        op.f("ix_scores_company_id"),
        table_name="scores",
    )

    op.drop_index(
        op.f("ix_scores_audit_id"),
        table_name="scores",
    )

    op.drop_table("scores")