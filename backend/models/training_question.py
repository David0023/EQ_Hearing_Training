from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class TrainingQuestion(Base):
    __tablename__ = "training_questions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    target_frequency: Mapped[float] = mapped_column(nullable=False)
    target_gain: Mapped[float] = mapped_column(nullable=False)
    
    user_frequency: Mapped[float] = mapped_column(nullable=True)
    user_gain: Mapped[float] = mapped_column(nullable=True)

    is_answered: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_correct: Mapped[bool] = mapped_column(nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(
                DateTime(timezone=True),
                nullable=True
    )

    training_session_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    training_session: Mapped["TrainingSession"] = relationship(
        back_populates="training_questions"
    )

    __table_args__ = (
            CheckConstraint(
                "NOT is_answered OR is_correct IS NOT NULL", name="ck_answered_requires_correct"
            ),
        )