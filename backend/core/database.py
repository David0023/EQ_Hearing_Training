from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models.base import Base

from core.config import settings

# SQL Alchemy engine for postgresql
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

# Class for creating new sessions
SessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)