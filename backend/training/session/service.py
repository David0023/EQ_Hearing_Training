from sqlalchemy.ext.asyncio import AsyncSession
from training.enums import QuestionType
from training.session.model import TrainingSession
from training.session import repository
from training.domain.info import validate_frequency, validate_gain


from training.session.schema import TrainingSessionCreateRequest

class SessionCreationException(Exception):
    pass

async def create_training_session(
    db: AsyncSession,
    user_id: int,
    request: TrainingSessionCreateRequest,
) -> TrainingSession:
    """Validate training settings and create a training session.

    Raises:
        SessionCreationException: If a frequency or gain setting is invalid.
    """

    if not (validate_frequency(request.min_frequency) and validate_frequency(request.max_frequency)):
        raise SessionCreationException("Invalid Frequency Option")
    if request.min_frequency > request.max_frequency:
        raise SessionCreationException("Invalid Frequency Range")
    if not validate_gain(request.gain_level):
        raise SessionCreationException("Invalid Gain Level")
    session = TrainingSession(
        user_id=user_id,
        num_questions=request.num_questions,
        question_type=request.question_type,
        min_frequency=request.min_frequency,
        max_frequency=request.max_frequency,
        gain_level=request.gain_level
    )
    return await repository.create(db, session)
