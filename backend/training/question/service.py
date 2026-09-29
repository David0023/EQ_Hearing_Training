from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from training.question import repository
from training.question.model import TrainingQuestion
from training.question.schema import AnswerQuestionRequest
from training.session.model import TrainingSession
from training.domain.info import get_frequency_range
from training.domain.rules import TrainingRule
from training.domain.generator import generate_question

async def create_training_question(
    db: AsyncSession,
    t_session: TrainingSession
) -> TrainingQuestion:
    """Generate and persist a training question for a session."""
    rule = TrainingRule(
        frequencies=get_frequency_range(t_session.min_frequency, t_session.max_frequency),
        gain_level=t_session.gain_level,
        question_type=t_session.question_type
    )
    question = generate_question(rule)

    question = TrainingQuestion(
        training_session_id=t_session.id,
        target_frequency=question.frequency,
        target_gain=question.gain
    )
    return await repository.create(db, question)


async def get_or_create_question(
    db: AsyncSession, session: TrainingSession,
) -> tuple[TrainingQuestion, bool]:
    """Reuse an unanswered question while the caller holds the session lock."""
    question = await repository.get_one(
        db,
        TrainingQuestion.training_session_id == session.id,
        TrainingQuestion.is_answered.is_(False),
        lock=True,
    )
    if question is not None:
        return question, False
    return await create_training_question(db, session), True


async def answer_question(
    db: AsyncSession, session: TrainingSession, question_id: int,
    answer: AnswerQuestionRequest,
) -> TrainingQuestion:
    """Record an answer while the caller holds the session lock."""
    question = await repository.get_one(
        db, TrainingQuestion.training_session_id == session.id,
        TrainingQuestion.id == question_id, lock=True,
    )
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The question cannot be found")
    if question.is_answered:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This question is already completed")
    return await repository.update(
        db, question, user_frequency=answer.user_frequency,
        user_gain=answer.user_gain, is_answered=True,
        is_correct=(question.target_frequency == answer.user_frequency
                    and question.target_gain == answer.user_gain),
        answered_at=datetime.now(timezone.utc),
    )
