from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import QuestionType
from models.training_session import TrainingSession
from repositories.training_session import create_training_session as _create_training_session

from domain.training.frequencies import validate_frequency, get_frequency_range
from domain.training.rules import TrainingRule
from domain.training.difficulty import calculate_difficulty
from domain.training.generator import generate_question


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
    if not (validate_frequency(min_frequency) and validate_frequency(max_frequency)):
        raise SessionCreationException("Invalid Frequency Option")
    if gain_level <= 0:
        raise SessionCreationException("Gain Level must be positive")
    new_training_session = TrainingSession(
        user_id=user_id,
        question_type=question_type,
        min_frequency=min_frequency,
        max_frequency=max_frequency,
        gain_level=gain_level
    )
    return await _create_training_session(db, new_training_session)