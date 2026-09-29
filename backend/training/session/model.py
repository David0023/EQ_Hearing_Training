from datetime import datetime
from sqlalchemy import DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from training.enums import QuestionType, SessionStatus

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    # Training session set values
    num_question: Mapped[int] = mapped_column(nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
            SQLEnum(QuestionType),
            nullable=False,
        )
    min_frequency: Mapped[float] = mapped_column(nullable=False)
    max_frequency: Mapped[float] = mapped_column(nullable=False)
    gain_level: Mapped[float] = mapped_column(nullable=False)


    # Session status values
    session_status: Mapped[SessionStatus] = mapped_column(
        SQLEnum(SessionStatus),
        nullable=False,
        default=SessionStatus.IN_PROGRESS
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="training_sessions")

    training_questions: Mapped[list["TrainingQuestion"]] = relationship(
        back_populates="training_session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            "gain_level > 0", name="check_gain_positive"
        ),
        CheckConstraint(
            "min_frequency <= max_frequency", name="check_min_lesser_or_equal_than_max"
        )
    )
