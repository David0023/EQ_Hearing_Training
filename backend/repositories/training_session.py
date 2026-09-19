from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.training_session import TrainingSession

async def get_one(db: AsyncSession, **kwargs) -> TrainingSession | None:
    query = select(TrainingSession).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_one_with_questions(
        db: AsyncSession, **kwargs
) -> TrainingSession | None:
    query = (
        select(TrainingSession)
        .options(selectinload(TrainingSession.training_questions))
        .filter_by(**kwargs)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_many(db: AsyncSession, **kwargs) -> list[TrainingSession]:
    query = select(TrainingSession).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalars().all()

async def create(
    db: AsyncSession, 
    training_session: TrainingSession
) -> TrainingSession:
    db.add(training_session)
    try:
        await db.commit()
        await db.refresh(training_session)
        return training_session
    except Exception as e:
        await db.rollback()
        raise e