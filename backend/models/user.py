from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base, TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String, nullable=False)
