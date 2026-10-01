from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from training.question import repository
from training.question.model import TrainingQuestion
from training.question.schema import AnswerQuestionRequest
from training.session.model import TrainingSession
from training.domain.info import get_frequency_range
from training.domain.rules import TrainingRule
from training.domain.generator import generate_question
from training.enums import SessionStatus
from training.session import service as session_service

class SessionCompletedException(Exception):
    pass

class QuestionAnsweredException(Exception):
    pass

class QuestionNotFoundException(Exception):
    pass

async def create_training_question(
    db: AsyncSession,
    session: TrainingSession
) -> TrainingQuestion:
    """
    Generate and persist a training question for a session.

    Raises:
        Exception: DB Failure
    """
    if session.session_status == SessionStatus.COMPLETED:
        raise SessionCompletedException()

    rule = TrainingRule(
        frequencies=get_frequency_range(session.min_frequency, session.max_frequency),
        gain_level=session.gain_level,
        question_type=session.question_type
    )
    question = generate_question(rule)

    question = TrainingQuestion(
        training_session_id=session.id,
        target_frequency=question.frequency,
        target_gain=question.gain
    )
    try:
        question = await repository.create(db, question, flush=True)
        await db.commit()
        return question
    except Exception as e:
        await db.rollback()
        raise e


async def get_or_create_question(
    db: AsyncSession, session: TrainingSession,
) -> tuple[TrainingQuestion, bool]:
    """
    Reuse an unanswered question while the caller holds the session lock.

    Raises: SessionCompletedException (if the session is complete)

    """
    question = await repository.get_one(
        db,
        TrainingQuestion.training_session_id == session.id,
        TrainingQuestion.is_answered.is_(False),
        lock=True,
    )
    try:
        await session_service.update_timestamp(db, session)
        if question is not None:
            await db.commit()
            return question, False
        return await create_training_question(db, session), True
    except Exception:
        await db.rollback()
        raise


async def answer_question(
    db: AsyncSession, session: TrainingSession, question_id: int,
    answer: AnswerQuestionRequest,
) -> TrainingQuestion:
    """
    Record an answer while the caller holds the session lock.


    Raises: QuestionNotFoundException, QuestionAnsweredException,
        Some other exception which rolls back DB
    """
    question = await repository.get_one(
        db, TrainingQuestion.training_session_id == session.id,
        TrainingQuestion.id == question_id, lock=True,
    )
    if question is None:
        raise QuestionNotFoundException()
    if question.is_answered:
        raise QuestionAnsweredException()

    try:
        question = await repository.update(
            db, question, flush=True,
            user_frequency=answer.user_frequency,
            user_gain=answer.user_gain, is_answered=True,
            is_correct=(question.target_frequency == answer.user_frequency
                        and question.target_gain == answer.user_gain),
            answered_at=datetime.now(timezone.utc),
        )

        # Check if the session is complete. Mark as complete if so.
        questions = await repository.get_all(
                db, TrainingQuestion.training_session_id == session.id,
        )
        if len(questions) == session.num_questions:
            await session_service.mark_session_complete(db, session)

        await session_service.update_timestamp(db, session)
        await db.commit()
        return question
    except Exception as e:
        await db.rollback()
        raise e
