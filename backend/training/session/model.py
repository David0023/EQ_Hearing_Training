from datetime import datetime
from sqlalchemy import DateTime, func, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from training.enums import SessionStatus

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    num_questions: Mapped[int] = mapped_column(nullable=False)
    # The plan contains one or more question-type blocks. Keeping the type in
    # each block lets a future session mix types without making the session a type.
    config: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )

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

    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True # To sort with recent options
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
        order_by="TrainingQuestion.sequence",
    )
