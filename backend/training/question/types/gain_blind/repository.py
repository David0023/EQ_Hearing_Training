from sqlalchemy.ext.asyncio import AsyncSession
from training.question.types.gain_blind.model import GainBlindQuestion

async def record_answer(
    db: AsyncSession,
    question: GainBlindQuestion,
    *,
    user_gain: float,
    flush: bool=False
) -> GainBlindQuestion:
    """Persist the type-specific answer values."""
    question.user_gain = user_gain

    if flush:
        await db.flush()
    return question

