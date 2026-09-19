from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import QuestionType
from models.training_question import TrainingQuestion
from models.training_session import TrainingSession
from repositories.training_session import (
    create_training_session as _create_training_session,
    get_one_training_session
)
from repositories.training_question import create_training_question as _create_training_question

from domain.training.info import validate_frequency, validate_gain, get_frequency_range
from domain.training.rules import TrainingRule
from domain.training.generator import generate_question


class SessionCreationException(Exception):
    pass

class QuestionCreationException(Exception):
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
    if not validate_gain(gain_level):
        raise SessionCreationException("Invalid Gain Level")
    new_training_session = TrainingSession(
        user_id=user_id,
        question_type=question_type,
        min_frequency=min_frequency,
        max_frequency=max_frequency,
        gain_level=gain_level
    )
    return await _create_training_session(db, new_training_session)

async def create_training_question(
    db: AsyncSession,
    t_session: TrainingSession
) -> TrainingQuestion:
    t_rule = TrainingRule(
        frequencies=get_frequency_range(t_session.min_frequency, t_session.max_frequency),
        gain_level=t_session.gain_level,
        question_type=t_session.question_type
    )
    question = generate_question(t_rule)

    training_question = TrainingQuestion(
        training_session_id=t_session.id,
        target_frequency=question.frequency,
        target_gain=question.gain
    )
    return await _create_training_question(db, training_question)
