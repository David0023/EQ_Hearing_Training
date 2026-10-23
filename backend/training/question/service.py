from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from training.domain.info import STANDARD_GAIN_OPTIONS, get_frequency_range
from training.domain.generator import generate_question
from training.enums import QuestionType, SessionStatus
from training.question import repository
from training.question.model import TrainingQuestion
from training.question.models.simple_blind import SimpleBlindQuestion
from training.question.schema import AnswerQuestionRequest
from training.question.types.simple_blind.rule import SimpleBlindRule
from training.session import service as session_service
from training.session.model import TrainingSession


class SessionCompletedException(Exception):
    pass


class QuestionAnswerException(Exception):
    pass


class QuestionNotFoundException(Exception):
    pass


def _get_next_plan_block(session: TrainingSession, question_count: int) -> dict:
    plan = session.config.get("question_plan", [])
    if not isinstance(plan, list):
        raise ValueError("Session question_plan must be a list")
    consumed = 0
    for block in plan:
        count = int(block["count"])
        if question_count < consumed + count:
            return block
        consumed += count
    raise SessionCompletedException()


def _build_rule(block: dict) -> SimpleBlindRule:
    question_type = QuestionType(block["question_type"])
    if question_type is not QuestionType.SIMPLE_BLIND:
        raise ValueError(f"Unsupported question type: {question_type.value}")

    settings = block["settings"]
    frequencies = get_frequency_range(settings["min_frequency"], settings["max_frequency"])
    gain_options = [
        gain for gain in STANDARD_GAIN_OPTIONS
        if settings["min_gain"] <= gain <= settings["max_gain"]
    ]
    gains = [-gain for gain in gain_options] + [0.0] + gain_options
    return SimpleBlindRule(frequencies=frequencies, gains=gains)


async def create_question(db: AsyncSession, session: TrainingSession) -> TrainingQuestion:
    if session.session_status == SessionStatus.COMPLETED:
        raise SessionCompletedException()

    questions = await repository.get_all(db, TrainingQuestion.training_session_id == session.id)
    if len(questions) >= session.num_questions:
        raise SessionCompletedException()
    plan_block = _get_next_plan_block(session, len(questions))
    generated = generate_question(_build_rule(plan_block))
    question = TrainingQuestion(
        training_session_id=session.id,
        sequence=len(questions) + 1,
        question_type=generated.question_type,
        simple_blind=SimpleBlindQuestion(
            target_frequency=generated.target_frequency,
            target_gain=generated.target_gain,
        ),
    )
    try:
        question = await repository.create(db, question, flush=True)
        await db.commit()
        return await repository.get_one(db, TrainingQuestion.id == question.id)
    except Exception:
        await db.rollback()
        raise


async def get_or_create_question(
    db: AsyncSession, session: TrainingSession,
) -> tuple[TrainingQuestion, bool]:
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
        return await create_question(db, session), True
    except Exception:
        await db.rollback()
        raise


async def answer_question(
    db: AsyncSession,
    session: TrainingSession,
    question_id: int,
    answer: AnswerQuestionRequest,
) -> tuple[bool, TrainingQuestion]:
    question = await repository.get_one(
        db,
        TrainingQuestion.training_session_id == session.id,
        TrainingQuestion.id == question_id,
        lock=True,
    )
    if question is None:
        raise QuestionNotFoundException()
    if question.is_answered:
        raise QuestionAnswerException("The question is already answered.")
    if question.question_type is not QuestionType.SIMPLE_BLIND or question.simple_blind is None:
        raise QuestionAnswerException("This question type cannot be answered yet.")

    try:
        detail = question.simple_blind
        question = await repository.record_answer(
            db,
            question,
            user_frequency=answer.user_frequency,
            user_gain=answer.user_gain,
            is_correct=(
                detail.target_frequency == answer.user_frequency
                and detail.target_gain == answer.user_gain
            ),
            answered_at=datetime.now(timezone.utc),
        )
        questions = await repository.get_all(
            db, TrainingQuestion.training_session_id == session.id
        )
        session_complete = len(questions) == session.num_questions and all(
            item.is_answered for item in questions
        )
        if session_complete:
            await session_service.mark_session_complete(db, session)
        await session_service.update_timestamp(db, session)
        await db.commit()
        return session_complete, question
    except Exception:
        await db.rollback()
        raise
