from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from training.session.model import TrainingSession

async def get_one(
    db: AsyncSession, *conditions, lock: bool = False
) -> TrainingSession | None:
    """Return one training session matching the given model fields."""
    query = select(TrainingSession).where(*conditions).order_by(TrainingSession.id.asc()).limit(1)
    if lock:
        query = query.with_for_update()
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_one_with_questions(
        db: AsyncSession, **kwargs
) -> TrainingSession | None:
    """Return one training session with its training questions loaded."""
    query = (
        select(TrainingSession)
        .options(selectinload(TrainingSession.training_questions))
        .filter_by(**kwargs)
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_many(db: AsyncSession, **kwargs) -> list[TrainingSession]:
    """Return all training sessions matching the given model fields."""
    query = select(TrainingSession).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalars().all()

async def create(
    db: AsyncSession,
    training_session: TrainingSession
) -> TrainingSession:
    """Persist and return a training session."""
    db.add(training_session)
    try:
        await db.commit()
        await db.refresh(training_session)
        return training_session
    except Exception as e:
        await db.rollback()
        raise e

async def update(
    db: AsyncSession,
    session: TrainingSession,
    **kwargs
) -> TrainingSession:
    """Update and return a training session.

    Raises:
        ValueError: If an unsupported field is provided.
    """
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

async def delete_this(
    db: AsyncSession,
    session: TrainingSession | None
) -> bool:
    """Delete given training session"""
    if not session:
        return False
    try:
        await db.delete(session)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e

async def delete_one(
    db: AsyncSession,
    *conditions
) -> int:
    """Delete the first matching training session by ascending ID."""
    query = select(TrainingSession).where(*conditions).order_by(TrainingSession.id.asc()).limit(1)
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
    *conditions,
    lock: bool = False
) -> int:
    """Delete all training sessions matching the conditions."""
    query = delete(TrainingSession).where(*conditions)
    if lock:
        query = query.with_update
    try:
        result = await db.execute(query)
        await db.commit()
        return result.rowcount or 0
    except Exception as e:
        await db.rollback()
        raise e
