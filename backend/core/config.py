from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DB Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/eq_hearing_training"

    # Security Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)
    ALGORITHM: str = "HS256"
    FRONTEND_ORIGINS: list[str] = ["http://localhost:5173"]
    COOKIE_SECURE: bool = True

settings = Settings()
