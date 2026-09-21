from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DB Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pronunciation_checker"

    # Security Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

settings = Settings()