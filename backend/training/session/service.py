from sqlalchemy.ext.asyncio import AsyncSession
from training.enums import QuestionType
from training.session.model import TrainingSession
from training.session import repository
from training.domain.info import validate_frequency, validate_gain

class SessionCreationException(Exception):
    pass

async def create_training_session(
    db: AsyncSession,
    user_id: int,
    question_type: QuestionType,
    min_frequency: float,
    max_frequency: float,
    gain_level: float
) -> TrainingSession:
    """Validate training settings and create a training session.

    Raises:
        SessionCreationException: If a frequency or gain setting is invalid.
    """
    if not (validate_frequency(min_frequency) and validate_frequency(max_frequency)):
        raise SessionCreationException("Invalid Frequency Option")
    if min_frequency > max_frequency:
        raise SessionCreationException("Invalid Frequency Range")
    if not validate_gain(gain_level):
        raise SessionCreationException("Invalid Gain Level")
    session = TrainingSession(
        user_id=user_id,
        question_type=question_type,
        min_frequency=min_frequency,
        max_frequency=max_frequency,
        gain_level=gain_level
    )
    return await repository.create(db, session)
