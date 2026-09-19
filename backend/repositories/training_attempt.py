from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.training_attempt import TrainingAttempt

async def get_one_training_attempt(db: AsyncSession, **kwargs) -> TrainingAttempt | None:
    query = select(TrainingAttempt).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_training_attempts(db: AsyncSession, **kwargs) -> list[TrainingAttempt]:
    query = select(TrainingAttempt).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalars().all()

async def create_training_attempt(
    db: AsyncSession, 
    training_attempt: TrainingAttempt
) -> TrainingAttempt:
    db.add(training_attempt)
    try:
        await db.commit()
        await db.refresh(training_attempt)
        return training_attempt
    except Exception as e:
        await db.rollback()
        raise e