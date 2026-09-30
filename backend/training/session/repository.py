from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from training.session.model import TrainingSession

async def get_one(
    db: AsyncSession, *conditions, lock: bool = False, load_questions: bool = False,
) -> TrainingSession | None:
    """Return one training session matching the given model fields."""
    query = select(TrainingSession).where(*conditions).order_by(TrainingSession.id.asc()).limit(1)
    if lock:
        query = query.with_for_update()
    if load_questions:
        query = query.options(selectinload(TrainingSession.training_questions))
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_many(db: AsyncSession, *conditions) -> list[TrainingSession]:
    """Return all training sessions matching the given model fields."""
    query = select(TrainingSession).where(*conditions)
    result = await db.execute(query)
    return result.scalars().all()

async def create(
    db: AsyncSession,
    training_session: TrainingSession,
    flush: bool = False,
) -> TrainingSession:
    """Persist and return a training session."""
    db.add(training_session)
    if flush:
        await db.flush()
        await db.refresh(training_session)
    return training_session

async def update(
    db: AsyncSession,
    session: TrainingSession,
    flush: bool = False,
    **kwargs
) -> TrainingSession:
    """Update and return a training session.

    Raises:
        ValueError: If an unsupported field is provided.
    """
    allowed_fields = {
        "completed_at",
        "session_status"
    }

    invalid_fields = set(kwargs) - allowed_fields

    if invalid_fields:
        raise ValueError(
            f"Cannot update fields: {', '.join(sorted(invalid_fields))}"
        )

    for field, value in kwargs.items():
        setattr(session, field, value)
    if flush:
        await db.flush()
        await db.refresh(session)
    return session

async def delete_this(
    db: AsyncSession,
    session: TrainingSession | None,
    flush: bool = False
) -> bool:
    """Delete given training session"""
    if not session:
        return False
    await db.delete(session)
    if flush:
        await db.flush()
    return True