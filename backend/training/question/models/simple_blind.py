from sqlalchemy import CheckConstraint, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class SimpleBlindQuestion(Base):
    """Simple blind question data, kept separate from shared question state."""

    __tablename__ = "simple_blind_questions"

    training_question_id: Mapped[int] = mapped_column(
        ForeignKey("training_questions.id", ondelete="CASCADE"), primary_key=True
    )
    target_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    target_gain: Mapped[float] = mapped_column(Float, nullable=False)
    user_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_gain: Mapped[float | None] = mapped_column(Float, nullable=True)

    training_question: Mapped["TrainingQuestion"] = relationship(back_populates="simple_blind")

    __table_args__ = (
        CheckConstraint("target_frequency > 0", name="ck_simple_blind_target_frequency_positive"),
    )
