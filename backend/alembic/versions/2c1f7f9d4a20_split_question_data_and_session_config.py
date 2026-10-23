"""Store session plans as JSONB and split simple blind question data.

Revision ID: 2c1f7f9d4a20
Revises: 763944a1de7a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "2c1f7f9d4a20"
down_revision: Union[str, Sequence[str], None] = "55ec36684cba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "training_sessions",
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.execute("""
        UPDATE training_sessions
        SET config = jsonb_build_object(
            'question_plan', jsonb_build_array(jsonb_build_object(
                'question_type', lower(question_type::text),
                'count', num_questions,
                'settings', jsonb_build_object(
                    'min_frequency', min_frequency,
                    'max_frequency', max_frequency,
                    'min_gain', gain_level,
                    'max_gain', gain_level
                )
            ))
        )
    """)
    op.alter_column("training_sessions", "config", nullable=False)
    op.drop_constraint("check_gain_positive", "training_sessions", type_="check")
    op.drop_constraint(
        "check_min_lesser_or_equal_than_max", "training_sessions", type_="check"
    )
    op.add_column(
        "training_questions",
        sa.Column("sequence", sa.Integer(), nullable=True),
    )
    op.add_column(
        "training_questions",
        sa.Column(
            "question_type",
            postgresql.ENUM("SIMPLE_BLIND", name="questiontype", create_type=False),
            nullable=True,
        ),
    )
    op.execute("""
        UPDATE training_questions q
        SET sequence = ranked.sequence,
            question_type = s.question_type
        FROM (
            SELECT id, row_number() OVER (
                PARTITION BY training_session_id ORDER BY id
            ) AS sequence
            FROM training_questions
        ) ranked,
        training_sessions s
        WHERE q.id = ranked.id AND q.training_session_id = s.id
    """)
    op.alter_column("training_questions", "sequence", nullable=False)
    op.alter_column("training_questions", "question_type", nullable=False)
    op.create_index(
        "ix_training_questions_sequence", "training_questions", ["sequence"]
    )
    op.drop_column("training_sessions", "question_type")
    op.drop_column("training_sessions", "min_frequency")
    op.drop_column("training_sessions", "max_frequency")
    op.drop_column("training_sessions", "gain_level")

    op.create_table(
        "simple_blind_questions",
        sa.Column(
            "training_question_id",
            sa.Integer(),
            sa.ForeignKey("training_questions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("target_frequency", sa.Float(), nullable=False),
        sa.Column("target_gain", sa.Float(), nullable=False),
        sa.Column("user_frequency", sa.Float(), nullable=True),
        sa.Column("user_gain", sa.Float(), nullable=True),
        sa.CheckConstraint(
            "target_frequency > 0",
            name="ck_simple_blind_target_frequency_positive",
        ),
    )
    op.execute("""
        INSERT INTO simple_blind_questions (
            training_question_id, target_frequency, target_gain,
            user_frequency, user_gain
        )
        SELECT id, target_frequency, target_gain, user_frequency, user_gain
        FROM training_questions
    """)
    op.drop_column("training_questions", "target_frequency")
    op.drop_column("training_questions", "target_gain")
    op.drop_column("training_questions", "user_frequency")
    op.drop_column("training_questions", "user_gain")


def downgrade() -> None:
    raise NotImplementedError(
        "This schema split cannot be safely downgraded without choosing a single "
        "session question type and collapsing question-specific settings."
    )
