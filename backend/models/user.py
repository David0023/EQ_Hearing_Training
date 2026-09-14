from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String, nullable=True)

    training_sessions: Mapped[list["TrainingSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
