from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.training_question import TrainingQuestion

async def get_one(db: AsyncSession, **kwargs) -> TrainingQuestion | None:
    query = select(TrainingQuestion).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_many(db: AsyncSession, **kwargs) -> list[TrainingQuestion]:
    query = select(TrainingQuestion).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalars().all()

async def create(
    db: AsyncSession, 
    training_question: TrainingQuestion
) -> TrainingQuestion:
    db.add(training_question)
    try:
        await db.commit()
        await db.refresh(training_question)
        return training_question
    except Exception as e:
        await db.rollback()
        raise e