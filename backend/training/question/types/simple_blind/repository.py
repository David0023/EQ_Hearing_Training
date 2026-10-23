from sqlalchemy.ext.asyncio import AsyncSession
from training.question.types.simple_blind.model import SimpleBlindQuestion

async def record_answer(
    db: AsyncSession,
    question: SimpleBlindQuestion,
    *,
    user_frequency: float,
    user_gain: float,
    flush: bool=False
) -> SimpleBlindQuestion:
    """Persist the type-specific answer values."""
    question.user_frequency = user_frequency
    question.user_gain = user_gain

    if flush:
        await db.flush()
    return question

