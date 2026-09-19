from datetime import datetime
from sqlalchemy import DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.enums import QuestionType

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    question_type: Mapped[QuestionType] = mapped_column(
        SQLEnum(QuestionType),
        nullable=False,
    )

    min_frequency: Mapped[float] = mapped_column(nullable=False)
    max_frequency: Mapped[float] = mapped_column(nullable=False)
    gain_level: Mapped[float] = mapped_column(nullable=False)
    

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

    training_attempts: Mapped[list["TrainingAttempt"]] = relationship(
        back_populates="training_session",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "gain_level > 0", name="check_gain_positive"
        ),
        CheckConstraint(
            "min_frequency <= max_frequency", name="check_min_lesser_or_equal_than_max"
        )
    )