from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from training.enums import QuestionType, SessionStatus
from training.question import repository
from training.question.model import TrainingQuestion
from training.question.schema import AnswerQuestionRequest
from training.session import service as session_service
from training.session.model import TrainingSession
from training.question.types.base import PlanItem
from training.question.types.registry import get_strategy

class SessionCompletedException(Exception):
    pass


class QuestionAnswerException(Exception):
    pass


class QuestionNotFoundException(Exception):
    pass

class QuestionCreationException(Exception):
    pass


def _get_next_plan_block(session: TrainingSession, question_count: int) -> PlanItem:
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

async def create_question(db: AsyncSession, session: TrainingSession) -> TrainingQuestion:
    if session.session_status == SessionStatus.COMPLETED:
        raise SessionCompletedException()

    questions = await repository.get_all(db, TrainingQuestion.training_session_id == session.id)
    if len(questions) >= session.num_questions:
        raise SessionCompletedException()

    plan_block = _get_next_plan_block(session, len(questions))
    question_type = QuestionType(plan_block["question_type"])
    strategy = get_strategy(question_type)

    question = TrainingQuestion(
        training_session_id=session.id,
        sequence=len(questions) + 1,
        question_type=question_type,
    )

    question_detail = strategy.generate_question(plan_block["settings"])
    strategy.attach_question_detail(question, question_detail)

    try:
        question = await repository.create(db, question, flush=True)
        await db.commit()
        persisted_question = await repository.get_one(
            db, question.question_type, TrainingQuestion.id == question.id
        )
        if persisted_question is None:
            raise QuestionCreationException("Created question could not be reloaded")
        return persisted_question
    except Exception:
        await db.rollback()
        raise

async def get_or_create_question(
    db: AsyncSession, session: TrainingSession,
) -> tuple[TrainingQuestion, bool]:
    question = await repository.get_one(
        db,
        None,
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
        None,
        TrainingQuestion.training_session_id == session.id,
        TrainingQuestion.id == question_id,
        lock=True,
    )
    if question is None:
        raise QuestionNotFoundException()
    if question.is_answered:
        raise QuestionAnswerException("The question is already answered.")
    if answer.question_type != question.question_type.value:
        raise QuestionAnswerException("Answer type does not match question type.")

    try:

        strategy = get_strategy(question.question_type)
        is_correct = await strategy.record_answer(db, question, answer)
        await repository.record_answer(
            db,
            question,
            is_correct=is_correct,
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
    except ValueError as exc:
        await db.rollback()
        raise QuestionAnswerException(str(exc)) from exc
    except Exception:
        await db.rollback()
        raise
