from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from training.enums import QuestionType


class TrainingQuestion(Base):
    """Type-independent question state and ordering within a session."""

    __tablename__ = "training_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    training_session_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(SQLEnum(QuestionType), nullable=False)
    is_answered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    training_session: Mapped["TrainingSession"] = relationship(back_populates="training_questions")
    simple_blind: Mapped["SimpleBlindQuestion | None"] = relationship(
        back_populates="training_question", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (
        CheckConstraint(
            "NOT is_answered OR is_correct IS NOT NULL",
            name="ck_answered_requires_correct",
        ),
    )
