"""Add gain blind question storage.

Revision ID: 8d4e2a1c7b90
Revises: 2c1f7f9d4a20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d4e2a1c7b90"
down_revision: Union[str, Sequence[str], None] = "2c1f7f9d4a20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'GAIN_BLIND'")
    op.create_table(
        "gain_blind_questions",
        sa.Column(
            "training_question_id",
            sa.Integer(),
            sa.ForeignKey("training_questions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("frequency", sa.Float(), nullable=False),
        sa.Column("target_gain", sa.Float(), nullable=False),
        sa.Column("user_gain", sa.Float(), nullable=True),
        sa.CheckConstraint("frequency > 0", name="ck_gain_blind_frequency_positive"),
    )


def downgrade() -> None:
    op.drop_table("gain_blind_questions")
    # PostgreSQL does not support removing an enum value safely.
