from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DB Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pronunciation_checker"

    # Security Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)
    ALGORITHM: str = "HS256"

settings = Settings()
