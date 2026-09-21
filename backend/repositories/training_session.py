from sqlalchemy import select, delete
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

async def upate(
    db: AsyncSession,
    session: TrainingSession,
    **kwargs
) -> TrainingSession:
    allowed_fields = {
        "completed_at"
    }

    invalid_fields = set(kwargs) - allowed_fields
    
    if invalid_fields:
        raise ValueError(
            f"Cannot update fields: {', '.join(sorted(invalid_fields))}"
        )

    try:
        for field, value in kwargs.items():
            setattr(session, field, value)
        await db.commit()
        await db.refresh(session)
        return session
    except Exception as e:
        await db.rollback()
        raise e

async def delete_one(
    db: AsyncSession,
    *conditions
) -> int:
    query = select(TrainingSession).where(*conditions).order_by(TrainingSession.id.asc())
    result = await db.execute(query)
    session = result.scalars().first()
    if session is None:
        return 0

    try:
        await db.delete(session)
        await db.commit()
        return 1
    except Exception as e:
        await db.rollback()
        raise e

async def delete_many(
    db: AsyncSession,
    *conditions
) -> int:
    query = delete(TrainingSession).where(*conditions)
    try:
        result = await db.execute(query)
        await db.commit()
        return result.rowcount or 0
    except Exception as e:
        await db.rollback()
        raise e