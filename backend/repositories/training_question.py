from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.training_question import TrainingQuestion

async def get_one(db: AsyncSession, *conditions) -> TrainingQuestion | None:
    """Return one training question matching the given model fields.

    Args:
        db: The database session to use.
        **kwargs: TrainingQuestion field names and values used as filters.

    Returns:
        The matching question, or None if no question matches.
    """
    query = select(TrainingQuestion).where(*conditions).order_by(TrainingQuestion.id.asc())
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_many(db: AsyncSession, **kwargs) -> list[TrainingQuestion]:
    """Return all training questions matching the given model fields.

    Args:
        db: The database session to use.
        **kwargs: TrainingQuestion field names and values used as filters.

    Returns:
        A list of matching questions.
    """
    query = select(TrainingQuestion).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalars().all()

async def create(
    db: AsyncSession, 
    training_question: TrainingQuestion
) -> TrainingQuestion:
    """Persist and return a training question.

    Args:
        db: The database session to use.
        training_question: The question to persist.

    Returns:
        The persisted training question.
    """
    db.add(training_question)
    try:
        await db.commit()
        await db.refresh(training_question)
        return training_question
    except Exception as e:
        await db.rollback()
        raise e

async def update(
    db: AsyncSession, 
    training_question: TrainingQuestion,
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
        "",
        "is_answered",
        "answered_at",
    }
    invalid_fields = set(kwargs) - allowed_fields
    if invalid_fields:
        raise ValueError(
            f"Cannot update fields: {', '.join(sorted(invalid_fields))}"
        )

    try:
        for field, value in kwargs.items():
            setattr(training_question, field, value)
        await db.commit()
        await db.refresh(training_question)
        return training_question
    except Exception as e:
        await db.rollback()
        raise e

async def delete_one(
    db: AsyncSession,
    *conditions
) -> int:
    """Delete the first matching training question by ascending ID.

    Args:
        db: The database session to use.
        *conditions: SQLAlchemy conditions used to select the question.

    Returns:
        1 if a question was deleted, otherwise 0.
    """
    query = select(TrainingQuestion).where(*conditions).order_by(TrainingQuestion.id.asc())
    result = await db.execute(query)
    training_question = result.scalars().first()
    if training_question is None:
        return 0

    try:
        await db.delete(training_question)
        await db.commit()
        return 1
    except Exception as e:
        await db.rollback()
        raise e

async def delete_many(
    db: AsyncSession,
    *conditions
) -> int:
    """Delete all training questions matching the conditions.

    Args:
        db: The database session to use.
        *conditions: SQLAlchemy conditions used to select questions.

    Returns:
        The number of deleted questions.
    """
    query = delete(TrainingQuestion).where(*conditions)
    try:
        result = await db.execute(query)
        await db.commit()
        return result.rowcount or 0
    except Exception as e:
        await db.rollback()
        raise e