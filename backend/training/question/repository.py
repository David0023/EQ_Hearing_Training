from typing import NamedTuple
from sqlalchemy import select, delete, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from training.question.model import TrainingQuestion

async def get_one(
    db: AsyncSession, *conditions, lock: bool = False
) -> TrainingQuestion | None:
    """Return one training question matching the given model fields.

    Args:
        db: The database session to use.
        *conditions: WHERE clause for SQL
        lock: lock the given row

    Returns:
        The matching question, or None if no question matches.
    """
    query = (
        select(TrainingQuestion)
        .where(*conditions)
        .order_by(TrainingQuestion.id.asc())
        .limit(1)
    )
    if lock:
        query = query.with_for_update()
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_all(
    db: AsyncSession, *conditions, lock: bool = False
) -> list[TrainingQuestion]:
    """Return all training questions matching the given model fields.

    Args:
        db: The database session to use.
        *conditions: WHERE clause for SQL
        lock: lock the given row

    Returns:
        A list of matching questions.
    """
    query = select(TrainingQuestion).where(*conditions).order_by(TrainingQuestion.id.asc())
    if lock:
        query = query.with_for_update()
    result = await db.execute(query)
    return result.scalars().all()


class SessionStatistics(NamedTuple):
    answered_count: int
    correct_count: int

async def get_session_statistics(
    db: AsyncSession, session_ids: list[int]
) -> dict[int, SessionStatistics]:
    """Return answered and correct question counts by session ID."""
    if not session_ids:
        return {}

    query = (
        select(
            TrainingQuestion.training_session_id,
            func.sum(case((TrainingQuestion.is_answered.is_(True), 1), else_=0)),
            func.sum(case((TrainingQuestion.is_correct.is_(True), 1), else_=0)),
        )
        .where(TrainingQuestion.training_session_id.in_(session_ids))
        .group_by(TrainingQuestion.training_session_id)
    )
    result = await db.execute(query)
    return {
        session_id: SessionStatistics(answered_count=int(answered), correct_count=int(correct))
        for session_id, answered, correct in result.all()
    }


async def create(
    db: AsyncSession,
    training_question: TrainingQuestion,
    flush: bool = False,
) -> TrainingQuestion:
    """Persist and return a training question.

    Args:
        db: The database session to use.
        training_question: The question to persist.

    Returns:
        The persisted training question.
    """
    db.add(training_question)
    if flush:
        await db.flush()
        await db.refresh(training_question)
    return training_question

async def update(
    db: AsyncSession,
    training_question: TrainingQuestion,
    flush: bool = False,
    **kwargs
) -> TrainingQuestion:
    """Update and return a training question.

    Args:
        db: The database session to use.
        training_question: The question to update.
        **kwargs: Allowed field names and their new values.

    Returns:
        The updated training question.

    Raises:
        ValueError: If an unsupported field is provided.
    """
    allowed_fields = {
        "user_frequency",
        "user_gain",
        "is_correct",
        "is_answered",
        "answered_at",
    }
    invalid_fields = set(kwargs) - allowed_fields
    if invalid_fields:
        raise ValueError(
            f"Cannot update fields: {', '.join(sorted(invalid_fields))}"
        )

    for field, value in kwargs.items():
        setattr(training_question, field, value)

    if flush:
        await db.flush()
        await db.refresh(training_question)
    return training_question

async def delete_these(
    db: AsyncSession,
    *conditions,
    flush: bool = False,
    count: int = 1,
) -> int:
    """Delete given amount of training questions matching the conditions.

    Args:
        db: The database session to use.
        *conditions: SQLAlchemy conditions used to select questions.

    Returns:
        The number of deleted questions.
    """
    matching_ids = (
        select(TrainingQuestion.id)
        .where(*conditions)
        .order_by(TrainingQuestion.id.asc())
        .limit(count)
    )
    query = delete(TrainingQuestion).where(TrainingQuestion.id.in_(matching_ids))
    result = await db.execute(query)
    if flush:
        await db.flush()
    return result.rowcount or 0
