from datetime import datetime
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class TrainingAttempt(Base):
    __tablename__ = "training_attempts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    target_frequency: Mapped[float] = mapped_column(nullable=False)
    target_gain: Mapped[float] = mapped_column(nullable=False)
    
    user_frequency: Mapped[float] = mapped_column(nullable=False)
    user_gain: Mapped[float] = mapped_column(nullable=False)
    response_time_ms: Mapped[float] = mapped_column(nullable=False)

    answered_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True),
                server_default=func.now(),
                nullable=False
    )

    training_session_id: Mapped[int] = mapped_column(ForeignKey("training_sessions.id"))
    training_session: Mapped["TrainingSession"] = relationship(back_populates="training_attempts")